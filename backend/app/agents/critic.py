"""Critic agent — Week 2.

Reviews a Copywriter draft against a fixed quality rubric. Returns a structured
verdict (APPROVE or REVISE + specific feedback). Drives the revision loop.

Uses Gemini 2.5 Pro by default — judgment quality matters more than cost here.

Usage from CLI (for testing in isolation — normally invoked by the pipeline):
    uv run python -m backend.app.agents.critic "Project name" --draft path/to/draft.md
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel


ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
console = Console()

DEFAULT_MODEL = "gemini-2.5-pro"

SYSTEM_PROMPT = """You are the Critic at an AI consulting agency. Your job is to review a Copywriter's draft proposal and decide whether it's ready for client delivery.

Apply this rubric to every draft:

1. **Structure** — has all required sections (Executive Summary, Context, Findings, Recommendations, Next Steps, Sources)?
2. **Citations** — every factual claim in Findings is backed by a numbered source. Sources list at the bottom is complete and deduplicated.
3. **Specificity** — Recommendations are concrete and actionable, not generic ("explore", "investigate" are red flags).
4. **Synthesis** — Findings are synthesized, not dumped verbatim from notes.
5. **Honesty** — invented numbers or unsupported claims = FAIL. Missing data should be explicitly named.
6. **Voice** — agency voice (third-person, neutral, confident). No first-person.

Verdict rules:
- If the draft fails ANY of the six checks above, return verdict "REVISE" with specific feedback.
- If it passes all six, return verdict "APPROVE".
- Feedback should be a numbered list — one item per problem — each pointing to the exact section or claim. No general "improve the writing" comments.

You MUST respond with a single JSON object matching this schema:
{
  "verdict": "APPROVE" or "REVISE",
  "feedback": "numbered list of specific problems, OR empty string if APPROVE",
  "rubric_scores": {
    "structure": "PASS" | "FAIL",
    "citations": "PASS" | "FAIL",
    "specificity": "PASS" | "FAIL",
    "synthesis": "PASS" | "FAIL",
    "honesty": "PASS" | "FAIL",
    "voice": "PASS" | "FAIL"
  }
}

No prose outside the JSON. No markdown fencing. Pure JSON."""


@dataclass
class CriticVerdict:
    verdict: Literal["APPROVE", "REVISE"]
    feedback: str
    rubric_scores: dict[str, str]
    input_tokens: int
    output_tokens: int
    cost_usd: float


def run_critic(draft: str, *, model: str = DEFAULT_MODEL) -> CriticVerdict:
    """Review a draft and return a structured verdict."""
    client = genai.Client(api_key=os.environ["GOOGLE_AI_STUDIO_KEY"])

    console.print(Panel.fit(
        f"[bold]Draft length:[/bold] {len(draft)} chars\n[bold]Model:[/bold] {model}",
        title="Critic",
        border_style="red",
    ))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,  # deterministic judgment
        response_mime_type="application/json",
    )

    resp = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=[types.Part(text=draft)])],
        config=config,
    )

    raw = (resp.candidates[0].content.parts[0].text or "").strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Critic returned malformed JSON: {e}\n---\n{raw}")

    in_toks = resp.usage_metadata.prompt_token_count or 0
    out_toks = resp.usage_metadata.candidates_token_count or 0

    # Pricing: Pro $1.25/M input + $5/M output
    if "pro" in model.lower():
        cost = in_toks * 1.25 / 1_000_000 + out_toks * 5 / 1_000_000
    else:
        cost = in_toks * 0.075 / 1_000_000 + out_toks * 0.30 / 1_000_000

    verdict = parsed.get("verdict", "REVISE")
    color = "green" if verdict == "APPROVE" else "yellow"
    console.print(f"[{color}]  Verdict: {verdict}[/{color}]  ·  ${cost:.5f}")
    if verdict == "REVISE":
        console.print(f"[dim]{parsed.get('feedback', '(no feedback)')[:400]}{'...' if len(parsed.get('feedback', '')) > 400 else ''}[/dim]")

    return CriticVerdict(
        verdict=verdict,
        feedback=parsed.get("feedback", ""),
        rubric_scores=parsed.get("rubric_scores", {}),
        input_tokens=in_toks,
        output_tokens=out_toks,
        cost_usd=cost,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="critic")
    parser.add_argument("--draft", required=True, help="Path to the draft markdown file to review")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    draft_text = Path(args.draft).read_text(encoding="utf-8")
    verdict = run_critic(draft_text, model=args.model)
    console.print(f"\n[bold]rubric_scores:[/bold]")
    for k, v in verdict.rubric_scores.items():
        marker = "[green]+[/green]" if v == "PASS" else "[red]X[/red]"
        console.print(f"  {marker} {k}: {v}")
    if verdict.verdict == "REVISE":
        console.print(f"\n[yellow]feedback:[/yellow]\n{verdict.feedback}")


if __name__ == "__main__":
    main()
