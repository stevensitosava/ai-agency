"""Eval orchestrator.

For each brief in briefs.yaml:
  1. Run the agency pipeline (LangGraph: Researcher -> Copywriter <-> Critic)
  2. Run the baseline (solo Gemini 2.5 Pro, one-shot)
  3. Independent grader scores both with the same rubric
  4. Save raw outputs + verdicts to eval/results/{brief_id}/

Then aggregate.py turns those files into a summary report.

Usage:
    uv run python -m eval.run_evaluation                    # all briefs
    uv run python -m eval.run_evaluation --ids brief1,brief2  # specific
    uv run python -m eval.run_evaluation --skip-agency        # baseline only
    uv run python -m eval.run_evaluation --skip-baseline      # agency only
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from backend.app.tools import report_writer
from eval import baseline, grader


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "eval" / "results"
BRIEFS_FILE = ROOT / "eval" / "briefs.yaml"

console = Console()


def load_briefs(ids: list[str] | None = None) -> list[dict]:
    with open(BRIEFS_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    briefs = data["briefs"]
    if ids:
        briefs = [b for b in briefs if b["id"] in ids]
    return briefs


def run_agency_for_brief(brief: dict) -> dict:
    """Run the agency pipeline and return the final draft + cost."""
    # We import lazily to avoid spinning up the graph when we just want baselines.
    from backend.app.graph import run_graph

    project = brief["id"]
    started = time.monotonic()
    state = run_graph(
        brief=brief["brief"],
        project=project,
        max_revisions=3,
    )
    duration = time.monotonic() - started
    return {
        "draft": state.get("draft", ""),
        "cost_usd": state.get("total_cost", 0.0),
        "duration_seconds": duration,
        "revisions": state.get("revisions", 0),
        "approved_by_critic": state.get("approved", False),
        "notes_count": len(state.get("notes_paths", [])),
    }


def run_one_brief(
    brief: dict, *, skip_agency: bool, skip_baseline: bool
) -> dict:
    """Execute both pipelines + grader for a single brief, save results."""
    bid = brief["id"]
    target_dir = RESULTS_DIR / bid
    target_dir.mkdir(parents=True, exist_ok=True)

    out: dict = {"brief": brief}

    # Agency pipeline
    if not skip_agency:
        console.rule(f"[bold cyan]Agency · {bid}")
        agency = run_agency_for_brief(brief)
        (target_dir / "agency.md").write_text(agency["draft"], encoding="utf-8")
        out["agency"] = {
            "cost_usd": agency["cost_usd"],
            "duration_seconds": agency["duration_seconds"],
            "revisions": agency["revisions"],
            "approved_by_critic": agency["approved_by_critic"],
            "notes_count": agency["notes_count"],
        }

    # Baseline solo Gemini
    if not skip_baseline:
        console.rule(f"[bold yellow]Baseline · {bid}")
        b = baseline.run_baseline(brief["brief"])
        (target_dir / "baseline.md").write_text(b.output, encoding="utf-8")
        out["baseline"] = {
            "cost_usd": b.cost_usd,
            "duration_seconds": b.duration_seconds,
            "input_tokens": b.input_tokens,
            "output_tokens": b.output_tokens,
        }

    # Grade each output that exists
    console.rule(f"[bold magenta]Grading · {bid}")
    for source in ("agency", "baseline"):
        path = target_dir / f"{source}.md"
        if not path.exists():
            continue
        draft = path.read_text(encoding="utf-8")
        console.print(f"  grading [yellow]{source}[/yellow] draft...")
        g = grader.grade(draft)
        (target_dir / f"{source}-grade.json").write_text(
            json.dumps(asdict(g), indent=2), encoding="utf-8"
        )
        out[source]["grade"] = {
            "pass_count": g.pass_count,
            "overall_quality": g.overall_quality,
            "one_line_assessment": g.one_line_assessment,
            "rubric_scores": g.rubric_scores,
            "grader_cost_usd": g.cost_usd,
        }
        console.print(
            f"    {source}: [bold]{g.pass_count}/6 PASS[/bold] · quality {g.overall_quality}/10 · ${g.cost_usd:.5f}"
        )

    (target_dir / "summary.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(prog="run_evaluation")
    parser.add_argument(
        "--ids", help="Comma-separated list of brief IDs to run (default: all)"
    )
    parser.add_argument("--skip-agency", action="store_true", dest="skip_agency")
    parser.add_argument("--skip-baseline", action="store_true", dest="skip_baseline")
    args = parser.parse_args()

    ids = [s.strip() for s in args.ids.split(",")] if args.ids else None
    briefs = load_briefs(ids)
    if not briefs:
        console.print("[red]No briefs to run[/red]")
        sys.exit(1)

    console.print(f"[bold]Running eval on {len(briefs)} brief(s)[/bold]")
    results = []
    for i, brief in enumerate(briefs, 1):
        console.rule(f"[bold]({i}/{len(briefs)}) {brief['id']}")
        try:
            results.append(run_one_brief(
                brief,
                skip_agency=args.skip_agency,
                skip_baseline=args.skip_baseline,
            ))
        except Exception as e:
            console.print(f"[red]Failed {brief['id']}: {type(e).__name__}: {e}[/red]")
            results.append({"brief": brief, "error": str(e)})

    # Quick summary table
    table = Table(title="Eval results", show_header=True)
    table.add_column("brief id", overflow="fold")
    table.add_column("agency", justify="center")
    table.add_column("baseline", justify="center")
    table.add_column("agency $", justify="right")
    table.add_column("base $", justify="right")
    for r in results:
        if "error" in r:
            table.add_row(r["brief"]["id"], "[red]ERR[/red]", "", "", "")
            continue
        ag = r.get("agency", {}).get("grade", {})
        bl = r.get("baseline", {}).get("grade", {})
        table.add_row(
            r["brief"]["id"],
            f"{ag.get('pass_count', '-')}/6  q{ag.get('overall_quality', '-')}",
            f"{bl.get('pass_count', '-')}/6  q{bl.get('overall_quality', '-')}",
            f"${r.get('agency', {}).get('cost_usd', 0):.4f}",
            f"${r.get('baseline', {}).get('cost_usd', 0):.4f}",
        )
    console.print(table)


if __name__ == "__main__":
    main()
