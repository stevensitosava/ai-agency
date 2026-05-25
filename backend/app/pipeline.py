"""Pipeline orchestrator — Week 2.

Runs the full agency loop on a single brief:

    brief -> Researcher -> notes
                  |
                  v
              Copywriter -> draft -> Critic
                  ^                     |
                  |                     |
                  +---- REVISE? --------+
                            |
                        (max 3 passes)
                            v
                       final report

Usage:
    uv run python -m backend.app.pipeline "Your client brief here"
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.app.agents import copywriter, critic, researcher
from backend.app.tools import report_writer


load_dotenv()  # load .env from cwd or project root
console = Console()

MAX_REVISIONS = 3


@dataclass
class PipelineResult:
    project: str
    final_report_path: str
    approved: bool
    revisions_used: int
    total_cost_usd: float


def run_pipeline(
    brief: str,
    *,
    project_name: str | None = None,
    research_model: str = researcher.MODEL,
    write_model: str = copywriter.DEFAULT_MODEL,
    critic_model: str = critic.DEFAULT_MODEL,
    max_revisions: int = MAX_REVISIONS,
    pace_seconds: int = researcher.INTER_CALL_DELAY_SEC,
) -> PipelineResult:
    project = project_name or brief[:60]
    total_cost = 0.0

    # Phase 1 — Research
    console.rule("[bold cyan]Phase 1 — Researcher")
    research = researcher.run_researcher(
        brief,
        project_name=project,
        model=research_model,
        pace_seconds=pace_seconds,
    )
    total_cost += research["cost_usd"]

    # Phase 2 — Draft + Critic loop
    console.rule("[bold magenta]Phase 2 — Copywriter + Critic loop")
    draft_text = ""
    verdict = None
    revisions = 0

    for revision in range(max_revisions + 1):  # +1 for the initial draft
        suffix = f"draft-{revision + 1}"
        if revision == 0:
            draft_result = copywriter.run_copywriter(
                project, brief=brief, model=write_model,
            )
        else:
            assert verdict is not None
            draft_result = copywriter.run_copywriter(
                project,
                brief=brief,
                revision_feedback=verdict.feedback,
                previous_draft=draft_text,
                model=write_model,
            )
        draft_text = draft_result.draft
        total_cost += draft_result.cost_usd
        report_writer.save_deliverable(project, draft_text, suffix=suffix)

        verdict = critic.run_critic(draft_text, model=critic_model)
        total_cost += verdict.cost_usd

        if verdict.verdict == "APPROVE":
            break
        revisions = revision + 1

    approved = verdict is not None and verdict.verdict == "APPROVE"
    final_suffix = "final-approved" if approved else "final-max-revisions"
    final_path = report_writer.save_deliverable(project, draft_text, suffix=final_suffix)

    # Summary
    table = Table(title="Pipeline summary", show_header=False, border_style="green")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Project", project)
    table.add_row("Approved", "[green]YES[/green]" if approved else "[yellow]NO (hit max revisions)[/yellow]")
    table.add_row("Revisions used", str(revisions))
    table.add_row("Notes written", str(len(research["notes"])))
    table.add_row("Total cost", f"${total_cost:.5f}")
    table.add_row("Final report", final_path)
    console.print(table)

    return PipelineResult(
        project=project,
        final_report_path=final_path,
        approved=approved,
        revisions_used=revisions,
        total_cost_usd=total_cost,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Run the full AI Agency pipeline: Researcher -> Copywriter -> Critic loop.",
    )
    parser.add_argument("brief", nargs="+", help="The client brief")
    parser.add_argument("--project", "-p", help="Project name (defaults to first 60 chars of brief)")
    parser.add_argument("--research-model", default=researcher.MODEL)
    parser.add_argument("--write-model", default=copywriter.DEFAULT_MODEL)
    parser.add_argument("--critic-model", default=critic.DEFAULT_MODEL)
    parser.add_argument("--max-revisions", type=int, default=MAX_REVISIONS, dest="max_revisions")
    parser.add_argument("--no-pace", action="store_true", help="Disable free-tier RPM pacing")
    args = parser.parse_args()

    if not os.environ.get("GOOGLE_AI_STUDIO_KEY"):
        console.print("[red]GOOGLE_AI_STUDIO_KEY not set in .env[/red]")
        raise SystemExit(1)

    brief = " ".join(args.brief)
    run_pipeline(
        brief,
        project_name=args.project,
        research_model=args.research_model,
        write_model=args.write_model,
        critic_model=args.critic_model,
        max_revisions=args.max_revisions,
        pace_seconds=0 if args.no_pace else researcher.INTER_CALL_DELAY_SEC,
    )


if __name__ == "__main__":
    main()
