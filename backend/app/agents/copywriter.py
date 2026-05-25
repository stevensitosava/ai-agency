"""Copywriter agent — Week 2.

Takes the Researcher's notes from `data/notes/{project_slug}/` and produces a
structured proposal draft in markdown. Single LLM call (no tool use) —
Gemini 2.5 Flash is enough for first drafts; Pro can be opted in via --model.

Usage from CLI:
    uv run python -m backend.app.agents.copywriter "Project name"
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel

from backend.app.tools import report_writer


ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
console = Console()

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are the Copywriter at an AI consulting agency. You take research notes produced by the Researcher and turn them into a structured client-ready proposal draft.

Required sections (in this exact order):

# Executive Summary
2-3 sentences. The most important findings + the core recommendation. No preamble.

# Context
1-2 short paragraphs. Frame the client's situation as captured in the brief.

# Findings
A series of headed subsections (### Heading) — one per research note. Cite every factual claim with bracketed numbers [1], [2] referring to a flat sources list at the end. Don't dump the note verbatim — synthesize, prune, sharpen.

# Recommendations
A numbered list of 3-5 concrete, actionable recommendations. Each item: one bold lead sentence, then 1-2 sentences of justification grounded in the findings.

# Next Steps
3-4 bullet points. Specific, owner-assignable actions. No vague verbs like "explore" or "investigate" — use "draft", "decide", "schedule", "build".

# Sources
A flat numbered list. Every URL referenced in the Findings section, deduplicated.

Style rules:
- Plain markdown. No HTML.
- No "I" or "we" — write in the agency voice (third-person, neutral, confident).
- No marketing fluff — every sentence either states a fact, a decision, or an action.
- If the notes contradict each other, surface the disagreement in Findings.
- If a number isn't in the notes, don't invent one. Say "not yet quantified" or similar.

If the user's message includes a "REVISION REQUEST" block, treat it as authoritative feedback from the Critic and address each point in your revision."""


@dataclass
class CopywriterResult:
    draft: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


def run_copywriter(
    project: str,
    *,
    brief: str = "",
    revision_feedback: str = "",
    previous_draft: str = "",
    model: str = DEFAULT_MODEL,
) -> CopywriterResult:
    """Generate (or revise) a proposal draft from the Researcher's notes."""
    client = genai.Client(api_key=os.environ["GOOGLE_AI_STUDIO_KEY"])

    notes = report_writer.load_notes(project)
    if not notes:
        raise RuntimeError(
            f"No notes found at data/notes/{report_writer._slugify(project)}/. "
            "Run the Researcher first."
        )

    user_msg_parts = [
        f"Project: {project}",
        f"Original brief: {brief}" if brief else "",
        "",
        "RESEARCH NOTES (from the Researcher):",
        notes,
    ]
    if previous_draft and revision_feedback:
        user_msg_parts.extend([
            "",
            "PREVIOUS DRAFT:",
            previous_draft,
            "",
            "REVISION REQUEST (from the Critic):",
            revision_feedback,
            "",
            "Produce a revised draft that addresses every point.",
        ])
    user_msg = "\n".join(p for p in user_msg_parts if p is not None)

    console.print(Panel.fit(
        f"[bold]Project:[/bold] {project}\n"
        f"[bold]Mode:[/bold] {'REVISION' if revision_feedback else 'INITIAL DRAFT'}\n"
        f"[bold]Notes loaded:[/bold] {len(notes)} chars\n"
        f"[bold]Model:[/bold] {model}",
        title="Copywriter",
        border_style="magenta",
    ))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.4,
    )

    resp = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=[types.Part(text=user_msg)])],
        config=config,
    )

    draft = resp.candidates[0].content.parts[0].text or ""
    in_toks = resp.usage_metadata.prompt_token_count or 0
    out_toks = resp.usage_metadata.candidates_token_count or 0

    # Pricing: Flash $0.075/M input + $0.30/M output; Pro $1.25/M + $5/M
    if "pro" in model.lower():
        cost = in_toks * 1.25 / 1_000_000 + out_toks * 5 / 1_000_000
    else:
        cost = in_toks * 0.075 / 1_000_000 + out_toks * 0.30 / 1_000_000

    console.print(f"[green]  [OK] draft generated · {in_toks} in / {out_toks} out · ${cost:.5f}[/green]")

    return CopywriterResult(
        draft=draft,
        input_tokens=in_toks,
        output_tokens=out_toks,
        cost_usd=cost,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="copywriter")
    parser.add_argument("project", help="Project name (matches notes folder)")
    parser.add_argument("--brief", default="", help="Original brief, for context")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    result = run_copywriter(args.project, brief=args.brief, model=args.model)
    path = report_writer.save_deliverable(args.project, result.draft, suffix="draft-1")
    console.print(f"[cyan]Saved draft to: {path}[/cyan]")


if __name__ == "__main__":
    main()
