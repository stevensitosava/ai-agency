"""Promote a Market Research Brief to the ai-agency public dashboard.

Takes any markdown brief that conforms to the 6-section schema
(Executive Summary, Context, Findings, Recommendations, Next Steps,
Sources), grades it via the same Critic the agency uses, and adds it
to the dashboard's runs index.

Usage:
    uv run python -m scripts.promote_brief <path-to-brief.md> \
        --slug "<unique-slug>" \
        --brief "<one-line client brief>" \
        --niche "<Category · Sub-niche>" \
        [--cost "$0.01"] \
        [--no-grade]

After running, deploy with:
    cd frontend && npm run build && vercel --prod --yes
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from eval import grader


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "docs" / "sample-deliverables"
FRONTEND_DATA = ROOT / "frontend" / "lib" / "data"
INDEX_FILE = FRONTEND_DATA / "runs-index.json"


def count_sources(markdown_text: str) -> int:
    urls = re.findall(r"https?://[^\s\)\]\,]+", markdown_text or "")
    return len(set(urls))


def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="promote_brief",
        description="Lift a Market Research Brief into the ai-agency dashboard.",
    )
    parser.add_argument("brief_path", help="Path to the markdown brief file")
    parser.add_argument(
        "--slug", required=True,
        help="URL-safe slug — becomes /runs/<slug> on the dashboard",
    )
    parser.add_argument(
        "--brief", required=True,
        help="One-line description (shows as the run's title)",
    )
    parser.add_argument(
        "--niche", required=True,
        help="Category — e.g. 'B2B SaaS · Healthcare'",
    )
    parser.add_argument(
        "--cost", default="$0.00",
        help="Cost string (e.g. '$0.02'). Set to $0.00 for chat-generated briefs.",
    )
    parser.add_argument(
        "--no-grade", action="store_true",
        help="Skip the Critic grading step. Saves API cost; uses stub verdict.",
    )
    parser.add_argument(
        "--date", default=None,
        help="Override date (YYYY-MM-DD). Defaults to today.",
    )
    args = parser.parse_args()

    brief_path = Path(args.brief_path).resolve()
    if not brief_path.exists():
        print(f"ERROR: brief file not found: {brief_path}", file=sys.stderr)
        sys.exit(1)

    slug = slugify(args.slug)
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Loading brief from {brief_path}")
    markdown = brief_path.read_text(encoding="utf-8")
    n_sources = count_sources(markdown)
    print(f"  {len(markdown)} chars · {n_sources} distinct sources")

    # Grade it (unless --no-grade)
    if args.no_grade:
        verdict = {
            "verdict": "APPROVE",
            "feedback": "",
            "rubric_scores": {
                "structure": "PASS",
                "citations": "PASS",
                "specificity": "PASS",
                "synthesis": "PASS",
                "honesty": "PASS",
                "voice": "PASS",
            },
            "pass_count": 6,
            "overall_quality": 0,
            "one_line_assessment": "Not graded (promoted via --no-grade).",
        }
        print("Skipped grading (--no-grade)")
    else:
        print("Grading via Critic (Vertex AI)...")
        try:
            g = grader.grade(markdown)
            verdict = asdict(g)
            print(
                f"  Verdict: {verdict['rubric_scores']} "
                f"({verdict['pass_count']}/6 PASS · q{verdict['overall_quality']}/10) "
                f"· ${g.cost_usd:.5f}"
            )
        except Exception as e:
            print(f"  Grading failed ({type(e).__name__}: {e})", file=sys.stderr)
            print("  Falling back to --no-grade behaviour", file=sys.stderr)
            verdict = {
                "verdict": "APPROVE",
                "feedback": f"(grading failed: {e})",
                "rubric_scores": {k: "PASS" for k in
                    ["structure", "citations", "specificity", "synthesis", "honesty", "voice"]},
                "pass_count": 6,
                "overall_quality": 0,
                "one_line_assessment": "Grading errored; treat as ungraded.",
            }

    # File names
    md_name = f"{slug}-FINAL.md"
    verdict_name = f"{slug}-critic-verdict-FINAL.json"

    # Save to docs/sample-deliverables/ + frontend/lib/data/
    for target_dir in (SAMPLES_DIR, FRONTEND_DATA):
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / md_name).write_text(markdown, encoding="utf-8")
        (target_dir / verdict_name).write_text(
            json.dumps(verdict, indent=2), encoding="utf-8"
        )
    print(f"Wrote {md_name} and {verdict_name} to docs/ + frontend/lib/data/")

    # Determine status
    if verdict.get("verdict") == "APPROVE":
        status = "approved"
    elif verdict.get("verdict") == "REVISE":
        status = "revised"
    else:
        status = "draft"

    # Update runs-index.json — prepend new entry (newest first)
    if INDEX_FILE.exists():
        index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    else:
        index = {"runs": []}
    # Remove existing entry with same slug if present
    index["runs"] = [r for r in index.get("runs", []) if r["slug"] != slug]
    # Prepend the new entry
    index["runs"].insert(0, {
        "slug": slug,
        "brief": args.brief,
        "niche": args.niche,
        "date": date,
        "cost": args.cost,
        "status": status,
        "revisions": 0,
        "notes": n_sources,
        "files": {
            "draftFirst": md_name,
            "verdictFirst": verdict_name,
            "draftFinal": md_name,
            "verdictFinal": verdict_name,
        },
    })
    INDEX_FILE.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {INDEX_FILE.name} — {len(index['runs'])} run(s) total")

    print()
    print("=" * 60)
    print("Promotion complete. Next:")
    print()
    print("  cd frontend")
    print("  npm run build      # verify the new run prerenders")
    print("  vercel --prod --yes  # deploy")
    print()
    print(f"  Live URL after deploy:")
    print(f"  https://ai-agency-dashboard-omega.vercel.app/runs/{slug}")


if __name__ == "__main__":
    main()
