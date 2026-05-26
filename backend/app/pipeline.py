"""Pipeline CLI — Week 3.

Thin wrapper around the LangGraph orchestrator in `backend.app.graph`.

The orchestration logic (nodes, edges, state, conditional routing, max-revision
cap, checkpointing) lives in graph.py. This file just parses CLI args and
hands off.

Usage:
    uv run python -m backend.app.pipeline "Your client brief here"
    uv run python -m backend.app.pipeline --resume "Project name to pick back up"
"""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from rich.console import Console

from backend.app.graph import run_graph


load_dotenv()
console = Console()

DEFAULT_MAX_REVISIONS = 3


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Run the full AI Agency graph: Researcher -> Copywriter <-> Critic -> Finalize.",
    )
    parser.add_argument("brief", nargs="+", help="The client brief (or project name when --resume)")
    parser.add_argument("--project", "-p", help="Project name (defaults to first 60 chars of brief)")
    parser.add_argument(
        "--max-revisions", type=int, default=DEFAULT_MAX_REVISIONS, dest="max_revisions",
        help=f"Critic revision cap (default: {DEFAULT_MAX_REVISIONS})",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume a previously interrupted run from its last checkpoint",
    )
    args = parser.parse_args()

    if not os.environ.get("GOOGLE_AI_STUDIO_KEY"):
        console.print("[red]GOOGLE_AI_STUDIO_KEY not set in .env[/red]")
        raise SystemExit(1)

    brief = " ".join(args.brief)
    project = args.project or brief[:60]

    run_graph(
        brief=brief,
        project=project,
        max_revisions=args.max_revisions,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
