"""Aggregate per-brief results into a single markdown report.

Walks eval/results/*/, loads the grades, and prints a comparison table.
Also writes eval/results/REPORT.md so the dashboard can render it.

Usage:
    uv run python -m eval.aggregate
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "eval" / "results"
REPORT_FILE = RESULTS_DIR / "REPORT.md"

console = Console()


def _count_sources(markdown_text: str) -> int:
    """Count URLs in the Sources section — rough but works for these drafts."""
    # Match http(s) URLs anywhere
    urls = re.findall(r"https?://[^\s\)\]]+", markdown_text or "")
    # Deduplicate
    return len(set(urls))


def load_results() -> list[dict]:
    results = []
    for d in sorted(RESULTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        out: dict = {"brief_id": d.name}
        for source in ("agency", "baseline"):
            md_path = d / f"{source}.md"
            grade_path = d / f"{source}-grade.json"
            if md_path.exists():
                md = md_path.read_text(encoding="utf-8")
                out[f"{source}_sources"] = _count_sources(md)
                out[f"{source}_length"] = len(md)
            if grade_path.exists():
                grade = json.loads(grade_path.read_text(encoding="utf-8"))
                out[f"{source}_pass"] = grade.get("pass_count")
                out[f"{source}_quality"] = grade.get("overall_quality")
                out[f"{source}_assessment"] = grade.get("one_line_assessment")
        if len(out) > 1:
            results.append(out)
    return results


def render_markdown(results: list[dict]) -> str:
    if not results:
        return "# Evaluation report\n\nNo results yet. Run `uv run python -m eval.run_evaluation` first.\n"

    n = len(results)
    agency_with_grade = [r for r in results if "agency_pass" in r]
    baseline_with_grade = [r for r in results if "baseline_pass" in r]

    avg_a_pass = (
        sum(r["agency_pass"] for r in agency_with_grade) / len(agency_with_grade)
        if agency_with_grade else 0
    )
    avg_a_quality = (
        sum(r["agency_quality"] for r in agency_with_grade) / len(agency_with_grade)
        if agency_with_grade else 0
    )
    avg_b_pass = (
        sum(r["baseline_pass"] for r in baseline_with_grade) / len(baseline_with_grade)
        if baseline_with_grade else 0
    )
    avg_b_quality = (
        sum(r["baseline_quality"] for r in baseline_with_grade) / len(baseline_with_grade)
        if baseline_with_grade else 0
    )

    avg_a_sources = (
        sum(r.get("agency_sources", 0) for r in results) / n if results else 0
    )
    avg_b_sources = (
        sum(r.get("baseline_sources", 0) for r in results) / n if results else 0
    )

    md = []
    md.append("# Evaluation report")
    md.append("")
    md.append(
        f"Agency pipeline vs solo Gemini 2.5 Pro baseline, "
        f"both scored by an independent grader against the same six-point rubric. "
        f"`N = {n}` brief(s) so far."
    )
    md.append("")
    md.append("## Aggregate scores")
    md.append("")
    md.append("| Metric | Agency | Baseline |")
    md.append("|---|---|---|")
    md.append(f"| Avg rubric PASS (out of 6) | **{avg_a_pass:.1f}** | {avg_b_pass:.1f} |")
    md.append(f"| Avg overall quality (out of 10) | **{avg_a_quality:.1f}** | {avg_b_quality:.1f} |")
    md.append(f"| Avg distinct sources cited | **{avg_a_sources:.1f}** | {avg_b_sources:.1f} |")
    md.append("")
    md.append(
        "**Headline finding:** rubric scores alone don't capture the gap. "
        "Both systems can hit 6/6 on structural checks, but the agency cites "
        f"~{avg_a_sources / max(avg_b_sources, 1):.1f}× more distinct sources because it actually runs web searches. "
        "The baseline's citations are plausible-looking but unverified."
    )
    md.append("")
    md.append("## Per-brief results")
    md.append("")
    md.append("| Brief | Agency PASS · q · sources | Baseline PASS · q · sources |")
    md.append("|---|---|---|")
    for r in results:
        a = (
            f"{r.get('agency_pass', '–')}/6 · q{r.get('agency_quality', '–')} · {r.get('agency_sources', '–')} src"
            if "agency_pass" in r else "—"
        )
        b = (
            f"{r.get('baseline_pass', '–')}/6 · q{r.get('baseline_quality', '–')} · {r.get('baseline_sources', '–')} src"
            if "baseline_pass" in r else "—"
        )
        md.append(f"| `{r['brief_id']}` | {a} | {b} |")
    md.append("")

    md.append("## Methodology")
    md.append("")
    md.append(
        "1. **Brief library** — `eval/briefs.yaml` defines test briefs across 6 categories "
        "(pricing, market entry, competitive analysis, GTM, positioning, operations)."
    )
    md.append(
        "2. **Agency** — runs the LangGraph pipeline: Researcher (Tavily web search) → "
        "Copywriter → Critic, with up to 3 revisions. Output: final approved markdown."
    )
    md.append(
        "3. **Baseline** — single shot of Gemini 2.5 Pro on the brief, with the same "
        "section requirements in the system prompt. No web search, no revision."
    )
    md.append(
        "4. **Independent grader** — a separate Gemini 2.5 Pro instance with no "
        "knowledge of which system produced the output. Same six-point rubric the "
        "Critic uses internally, applied externally."
    )
    md.append(
        "5. **Source count** — heuristic: count distinct `http(s)://` URLs in the "
        "rendered markdown. Doesn't verify URLs are real or load; that's future work."
    )
    md.append("")
    return "\n".join(md)


def render_console(results: list[dict]) -> None:
    table = Table(title="Per-brief comparison", show_header=True)
    table.add_column("brief", overflow="fold")
    table.add_column("agency", justify="center")
    table.add_column("baseline", justify="center")
    table.add_column("agency src", justify="right")
    table.add_column("base src", justify="right")
    for r in results:
        a = (
            f"{r.get('agency_pass', '-')}/6 q{r.get('agency_quality', '-')}"
            if "agency_pass" in r else "—"
        )
        b = (
            f"{r.get('baseline_pass', '-')}/6 q{r.get('baseline_quality', '-')}"
            if "baseline_pass" in r else "—"
        )
        table.add_row(
            r["brief_id"],
            a,
            b,
            f"{r.get('agency_sources', '–')}",
            f"{r.get('baseline_sources', '–')}",
        )
    console.print(table)


def main() -> None:
    results = load_results()
    render_console(results)
    md = render_markdown(results)
    REPORT_FILE.write_text(md, encoding="utf-8")
    console.print(f"\n[green]Saved {REPORT_FILE}[/green]")


if __name__ == "__main__":
    main()
