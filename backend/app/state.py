"""Shared state schema for the LangGraph orchestrator.

A single TypedDict that flows through every node. Each node returns a partial
dict (a state delta) that LangGraph merges into the running state.
"""

from __future__ import annotations

from typing import TypedDict


class AgencyState(TypedDict, total=False):
    # Inputs
    brief: str
    project: str
    max_revisions: int

    # Researcher output
    notes_paths: list[str]
    research_input_tokens: int
    research_output_tokens: int
    research_cost: float

    # Copywriter state — current draft + revision count
    draft: str
    revisions: int  # 0 = initial draft, 1+ = revision passes
    write_cost: float

    # Critic state — latest verdict
    verdict: str  # "APPROVE" | "REVISE"
    feedback: str
    rubric_scores: dict[str, str]
    critic_cost: float

    # Finalization
    final_path: str
    approved: bool

    # Cumulative tracking
    total_cost: float
    history: list[dict]  # one entry per node invocation


def empty_state(brief: str, project: str, max_revisions: int = 3) -> AgencyState:
    """Build the initial state for a fresh pipeline run."""
    return AgencyState(
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
