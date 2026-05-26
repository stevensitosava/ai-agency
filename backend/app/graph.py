"""LangGraph orchestrator — Week 3.

Replaces the manual loop in `pipeline.py` with a proper StateGraph.

Graph shape:

    START
      |
      v
    research
      |
      v
    copywrite <-----+
      |             |
      v             |
    critique       (feedback)
      |             |
      +--> REVISE --+   (max_revisions cap)
      |
      v
    finalize
      |
      v
     END

Checkpointing:
- SqliteSaver writes every state transition to data/db/checkpoints.sqlite.
- Each run uses a thread_id (project slug) so an interrupted run can be
  resumed by calling the graph again with the same thread_id.

Two-tier model routing:
- Researcher: Gemini 2.5 Flash (cheap iteration over searches)
- Copywriter: Flash by default; Pro available via env override
- Critic: Gemini 2.5 Pro (judgment quality matters)
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Literal

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.panel import Panel

from backend.app.agents import copywriter, critic, researcher
from backend.app.state import AgencyState
from backend.app.tools import report_writer


console = Console()

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DB = ROOT / "data" / "db" / "checkpoints.sqlite"


# ---------- Nodes ----------

def node_research(state: AgencyState) -> AgencyState:
    """Run the Researcher tool-use loop. Produces cited notes on disk."""
    console.rule("[bold cyan]Researcher")
    result = researcher.run_researcher(
        state["brief"],
        project_name=state["project"],
    )
    delta = {
        "notes_paths": result["notes"],
        "research_input_tokens": result["input_tokens"],
        "research_output_tokens": result["output_tokens"],
        "research_cost": result["cost_usd"],
        "total_cost": state.get("total_cost", 0.0) + result["cost_usd"],
        "history": state.get("history", []) + [{
            "node": "research",
            "cost": result["cost_usd"],
            "notes": len(result["notes"]),
        }],
    }
    return delta  # type: ignore[return-value]


def node_copywrite(state: AgencyState) -> AgencyState:
    """Draft (or revise) the proposal based on notes + optional Critic feedback."""
    revisions = state.get("revisions", 0)
    label = "Copywriter — REVISION" if revisions > 0 else "Copywriter — DRAFT 1"
    console.rule(f"[bold magenta]{label}")

    result = copywriter.run_copywriter(
        state["project"],
        brief=state.get("brief", ""),
        revision_feedback=state.get("feedback", "") if revisions > 0 else "",
        previous_draft=state.get("draft", "") if revisions > 0 else "",
    )
    # Save intermediate draft to disk
    suffix = f"draft-{revisions + 1}"
    report_writer.save_deliverable(state["project"], result.draft, suffix=suffix)

    delta = {
        "draft": result.draft,
        "write_cost": state.get("write_cost", 0.0) + result.cost_usd,
        "total_cost": state.get("total_cost", 0.0) + result.cost_usd,
        "history": state.get("history", []) + [{
            "node": "copywrite",
            "revision": revisions,
            "cost": result.cost_usd,
        }],
    }
    return delta  # type: ignore[return-value]


def node_critique(state: AgencyState) -> AgencyState:
    """Run the Critic and capture its structured verdict."""
    console.rule("[bold red]Critic")
    verdict = critic.run_critic(state["draft"])
    delta = {
        "verdict": verdict.verdict,
        "feedback": verdict.feedback,
        "rubric_scores": verdict.rubric_scores,
        "critic_cost": state.get("critic_cost", 0.0) + verdict.cost_usd,
        "total_cost": state.get("total_cost", 0.0) + verdict.cost_usd,
        "history": state.get("history", []) + [{
            "node": "critique",
            "verdict": verdict.verdict,
            "cost": verdict.cost_usd,
        }],
    }
    return delta  # type: ignore[return-value]


def node_finalize(state: AgencyState) -> AgencyState:
    """Save the final deliverable and stamp approval status."""
    console.rule("[bold green]Finalize")
    approved = state.get("verdict") == "APPROVE"
    suffix = "final-approved" if approved else "final-max-revisions"
    path = report_writer.save_deliverable(
        state["project"], state["draft"], suffix=suffix
    )
    console.print(f"  saved: {path}")
    return {
        "final_path": path,
        "approved": approved,
    }  # type: ignore[return-value]


# ---------- Conditional edge ----------

def decide_after_critic(state: AgencyState) -> Literal["copywrite", "finalize"]:
    """The supervisor decision. Implements the bounded revision loop."""
    if state.get("verdict") == "APPROVE":
        return "finalize"
    if state.get("revisions", 0) + 1 >= state.get("max_revisions", 3):
        # Bumping revisions one more time would exceed the cap — ship as-is.
        return "finalize"
    return "copywrite"


def node_bump_revisions(state: AgencyState) -> AgencyState:
    """Tiny passthrough that increments the revision counter before re-drafting."""
    return {"revisions": state.get("revisions", 0) + 1}  # type: ignore[return-value]


# ---------- Graph builder ----------

def build_graph(checkpointer=None):
    """Build and compile the agency StateGraph."""
    g = StateGraph(AgencyState)
    g.add_node("research", node_research)
    g.add_node("copywrite", node_copywrite)
    g.add_node("critique", node_critique)
    g.add_node("bump_revisions", node_bump_revisions)
    g.add_node("finalize", node_finalize)

    g.add_edge(START, "research")
    g.add_edge("research", "copywrite")
    g.add_edge("copywrite", "critique")

    # Critic decides: approve -> finalize, or send back for revision (capped)
    g.add_conditional_edges(
        "critique",
        decide_after_critic,
        {
            "copywrite": "bump_revisions",
            "finalize": "finalize",
        },
    )
    g.add_edge("bump_revisions", "copywrite")
    g.add_edge("finalize", END)

    return g.compile(checkpointer=checkpointer)


def get_checkpointer() -> SqliteSaver:
    """Create the SqliteSaver, ensuring the db file's parent dir exists."""
    CHECKPOINT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
    return SqliteSaver(conn)


def _thread_id(project: str) -> str:
    """Stable thread id per project — letters, digits, dashes only."""
    return re.sub(r"[^a-z0-9-]+", "-", project.lower()).strip("-")[:80] or "untitled"


def run_graph(
    brief: str,
    project: str,
    *,
    max_revisions: int = 3,
    resume: bool = False,
) -> AgencyState:
    """Run the graph end-to-end with checkpointing.

    Pass `resume=True` to continue an interrupted thread (uses the same
    thread_id derived from the project name).
    """
    checkpointer = get_checkpointer()
    graph = build_graph(checkpointer=checkpointer)

    thread_id = _thread_id(project)
    config = {"configurable": {"thread_id": thread_id}}

    if resume:
        console.print(Panel.fit(
            f"Resuming thread [bold]{thread_id}[/bold]",
            border_style="yellow",
        ))
        final = graph.invoke(None, config=config)  # None = pick up from checkpoint
    else:
        initial = AgencyState(
            brief=brief,
            project=project,
            max_revisions=max_revisions,
            notes_paths=[],
            research_input_tokens=0,
            research_output_tokens=0,
            research_cost=0.0,
            draft="",
            revisions=0,
            write_cost=0.0,
            verdict="",
            feedback="",
            rubric_scores={},
            critic_cost=0.0,
            final_path="",
            approved=False,
            total_cost=0.0,
            history=[],
        )
        final = graph.invoke(initial, config=config)

    console.print(Panel.fit(
        f"[bold]Project:[/bold] {project}\n"
        f"[bold]Thread:[/bold] {thread_id}\n"
        f"[bold]Approved:[/bold] {'[green]YES[/green]' if final.get('approved') else '[yellow]NO[/yellow]'}\n"
        f"[bold]Revisions used:[/bold] {final.get('revisions', 0)}\n"
        f"[bold]Notes written:[/bold] {len(final.get('notes_paths', []))}\n"
        f"[bold]Total cost:[/bold] ${final.get('total_cost', 0):.5f}\n"
        f"[bold]Final report:[/bold] {final.get('final_path', '')}",
        title="Pipeline summary",
        border_style="green",
    ))
    return final
