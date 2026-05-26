"""Structural tests for the LangGraph orchestrator — no API calls."""

from __future__ import annotations

import pytest

from backend.app.graph import (
    _thread_id,
    build_graph,
    decide_after_critic,
)
from backend.app.state import AgencyState, empty_state


# ---- graph topology ----

def test_graph_compiles_without_checkpointer() -> None:
    g = build_graph()
    nodes = set(g.get_graph().nodes) - {"__start__", "__end__"}
    assert nodes == {"research", "copywrite", "critique", "bump_revisions", "finalize"}


def test_graph_compiles_with_checkpointer() -> None:
    # Checkpointer path imported in the function — just verify it doesn't blow up
    from backend.app.graph import get_checkpointer
    cp = get_checkpointer()
    g = build_graph(checkpointer=cp)
    assert g is not None


# ---- conditional edge logic (the supervisor decision) ----

def test_decide_approve_goes_to_finalize() -> None:
    state = empty_state("brief", "project")
    state["verdict"] = "APPROVE"
    state["revisions"] = 0
    assert decide_after_critic(state) == "finalize"


def test_decide_revise_with_budget_loops_back() -> None:
    state = empty_state("brief", "project", max_revisions=3)
    state["verdict"] = "REVISE"
    state["revisions"] = 0
    assert decide_after_critic(state) == "copywrite"


def test_decide_revise_at_cap_force_finalize() -> None:
    # When the NEXT revision would exceed the cap, ship as-is
    state = empty_state("brief", "project", max_revisions=3)
    state["verdict"] = "REVISE"
    state["revisions"] = 2  # next would be 3, which hits the cap
    assert decide_after_critic(state) == "finalize"


@pytest.mark.parametrize("revisions,expected", [
    (0, "copywrite"),
    (1, "copywrite"),
    (2, "finalize"),  # next would be 3 = cap
    (3, "finalize"),
])
def test_decide_revise_revision_counter(revisions: int, expected: str) -> None:
    state = empty_state("brief", "project", max_revisions=3)
    state["verdict"] = "REVISE"
    state["revisions"] = revisions
    assert decide_after_critic(state) == expected


# ---- thread id helpers ----

@pytest.mark.parametrize("project,expected", [
    ("Simple Project", "simple-project"),
    ("Project with !@# chars", "project-with-chars"),
    ("ALREADY-LOWER", "already-lower"),
    ("   trim   spaces   ", "trim-spaces"),
])
def test_thread_id_normalises(project: str, expected: str) -> None:
    assert _thread_id(project) == expected


def test_thread_id_truncated() -> None:
    long_project = "a" * 200
    tid = _thread_id(long_project)
    assert len(tid) == 80


def test_thread_id_empty_fallback() -> None:
    assert _thread_id("") == "untitled"
    assert _thread_id("###") == "untitled"


# ---- state helpers ----

def test_empty_state_has_required_keys() -> None:
    state = empty_state("brief text", "Project X")
    assert state["brief"] == "brief text"
    assert state["project"] == "Project X"
    assert state["max_revisions"] == 3
    assert state["revisions"] == 0
    assert state["total_cost"] == 0.0
    assert state["approved"] is False
    assert state["history"] == []


def test_empty_state_custom_max_revisions() -> None:
    state = empty_state("b", "p", max_revisions=5)
    assert state["max_revisions"] == 5
