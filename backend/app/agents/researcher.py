"""Researcher agent — Week 1.

Takes a client brief, plans 3-5 sub-topics to investigate, runs web searches,
synthesizes findings into markdown notes saved to disk.

Built with the raw Google Gemini SDK (google-genai). No LangGraph yet — that
comes in week 3. Demonstrates the standard tool-use loop:
  model emits function_call → we execute → return function_response → repeat
  until the model returns plain text.

Usage:
    uv run python -m backend.app.agents.researcher "Your client brief here"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from backend.app.tools import notes_writer, web_search


# Load .env from project root
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

console = Console()

# Gemini 2.5 Flash for the Researcher — cheap, fast, plenty good for synthesis.
# Pro is reserved for Strategist + Critic in later weeks.
MODEL = "gemini-2.5-flash"
MAX_ITERATIONS = 20  # safety cap — most briefs finish in 8-12 iterations

# Free tier on Gemini Flash is 5 RPM. Until Tier 1 promotion happens, we pace
# at 1 call every 15s = 4 RPM, safely under. Set to 0 once on Tier 1.
INTER_CALL_DELAY_SEC = 15
RETRY_ON_429_MAX = 3

SYSTEM_PROMPT = """You are the Researcher at an AI consulting agency. Your job is to take a client brief and produce structured, well-sourced research notes that a Copywriter and Strategist can build on.

Process:
1. Read the brief carefully. Identify 3-5 specific sub-topics that need investigation.
2. For each sub-topic, call web_search with focused queries. Don't run more than 3 searches per sub-topic — be efficient.
3. After each sub-topic, call save_note with the findings. One note per sub-topic, not one giant note.
4. When all sub-topics are covered, return a plain-text summary listing the notes you wrote and one paragraph synthesizing the overall findings.

Quality bar:
- Every factual claim must be backed by a source URL.
- Prefer recent sources (2024-2026) for market data.
- If sources contradict each other, note the disagreement.
- Don't invent numbers. If you can't find a stat, say so.

Stop when you've covered all sub-topics. Don't keep researching forever — the Copywriter needs to start their work."""


def _parse_retry_delay(err: genai_errors.ClientError, fallback: int = 60) -> int:
    """Extract retry_delay seconds from a Gemini 429 error, fall back to fallback."""
    msg = str(err)
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", msg, re.IGNORECASE)
    if m:
        return int(float(m.group(1))) + 2  # tiny buffer
    return fallback


def _call_with_retry(client: genai.Client, contents: list, config, *, model: str = MODEL) -> Any:
    """Call generate_content with automatic retry on 429 (rate limit) and 503 (overload)."""
    for attempt in range(1, RETRY_ON_429_MAX + 2):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except genai_errors.ClientError as e:
            if e.code == 429 and attempt <= RETRY_ON_429_MAX:
                wait = _parse_retry_delay(e)
                console.print(f"[yellow]  429 rate-limited. Waiting {wait}s (attempt {attempt}/{RETRY_ON_429_MAX})...[/yellow]")
                time.sleep(wait)
                continue
            raise
        except genai_errors.ServerError as e:
            # 503 "model overloaded" — exponential backoff
            if e.code == 503 and attempt <= RETRY_ON_429_MAX:
                wait = min(20 * (2 ** (attempt - 1)), 90)  # 20s, 40s, 80s (capped 90)
                console.print(f"[yellow]  503 overloaded. Backing off {wait}s (attempt {attempt}/{RETRY_ON_429_MAX})...[/yellow]")
                time.sleep(wait)
                continue
            raise


def run_researcher(
    brief: str,
    project_name: str | None = None,
    *,
    model: str = MODEL,
    max_iter: int = MAX_ITERATIONS,
    pace_seconds: int = INTER_CALL_DELAY_SEC,
) -> dict[str, Any]:
    """Run the Researcher loop on a brief. Returns a summary dict."""
    client = genai.Client(api_key=os.environ["GOOGLE_AI_STUDIO_KEY"])

    project = project_name or brief[:60]

    console.print(Panel.fit(
        f"[bold]Brief:[/bold] {brief}\n[bold]Project:[/bold] {project}\n[bold]Model:[/bold] {model}",
        title="Researcher · Week 1",
        border_style="cyan",
    ))

    # Tool config — both function declarations under one Tool
    tools = [types.Tool(function_declarations=[
        web_search.FUNCTION_DECLARATION,
        notes_writer.FUNCTION_DECLARATION,
    ])]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        temperature=0.3,
    )

    # Conversation history — Gemini uses `contents` (list of Content)
    contents: list[Any] = [
        types.Content(role="user", parts=[types.Part(text=brief)])
    ]

    notes_written: list[str] = []
    total_in_tokens = 0
    total_out_tokens = 0
    iteration = 0

    for iteration in range(1, max_iter + 1):
        # Pace ourselves to respect free-tier 5 RPM (--no-pace once on Tier 1).
        if iteration > 1 and pace_seconds > 0:
            console.print(f"[dim]  (pacing {pace_seconds}s for free-tier RPM)[/dim]")
            time.sleep(pace_seconds)

        resp = _call_with_retry(client, contents, config, model=model)

        if resp.usage_metadata:
            total_in_tokens += resp.usage_metadata.prompt_token_count or 0
            total_out_tokens += resp.usage_metadata.candidates_token_count or 0

        candidate = resp.candidates[0]
        contents.append(candidate.content)

        # Collect function calls + text from this turn
        function_calls = []
        for part in candidate.content.parts or []:
            if part.text and part.text.strip():
                console.print(Markdown(part.text))
            if part.function_call:
                function_calls.append(part.function_call)

        # No function calls → model is done
        if not function_calls:
            break

        # Execute every function call, collect responses
        function_response_parts = []
        for fc in function_calls:
            args = dict(fc.args) if fc.args else {}
            console.print(f"[dim]-> calling[/dim] [yellow]{fc.name}[/yellow]({_truncate(args)})")
            try:
                if fc.name == "web_search":
                    result: Any = web_search.web_search(**args)
                elif fc.name == "save_note":
                    # Inject the project name (we control it, not the model)
                    path = notes_writer.save_note(project=project, **args)
                    notes_written.append(path)
                    result = {"saved_to": path}
                    console.print(f"[green]  [OK] saved {Path(path).name}[/green]")
                else:
                    result = {"error": f"unknown tool {fc.name}"}
            except Exception as e:  # tool failures are reported, loop continues
                result = {"error": f"{type(e).__name__}: {e}"}
                console.print(f"[red]  [FAIL] {e}[/red]")

            function_response_parts.append(types.Part.from_function_response(
                name=fc.name,
                response={"result": result},
            ))

        # Send all function responses back in one user turn
        contents.append(types.Content(role="user", parts=function_response_parts))
    else:
        console.print(f"[red]Hit max iterations ({MAX_ITERATIONS}) — stopping.[/red]")

    # Cost estimate — Gemini 2.5 Flash: $0.075/M input + $0.30/M output (May 2026)
    cost_in = total_in_tokens * 0.075 / 1_000_000
    cost_out = total_out_tokens * 0.30 / 1_000_000
    total_cost = cost_in + cost_out

    console.print(Panel.fit(
        f"[bold]Iterations:[/bold] {iteration}\n"
        f"[bold]Notes written:[/bold] {len(notes_written)}\n"
        f"[bold]Tokens:[/bold] {total_in_tokens} in / {total_out_tokens} out\n"
        f"[bold]Estimated cost:[/bold] ${total_cost:.5f}",
        title="Done",
        border_style="green",
    ))

    return {
        "iterations": iteration,
        "notes": notes_written,
        "input_tokens": total_in_tokens,
        "output_tokens": total_out_tokens,
        "cost_usd": total_cost,
    }


def _truncate(obj: Any, n: int = 80) -> str:
    s = str(obj)
    return s[:n] + "..." if len(s) > n else s


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="researcher",
        description="Run the Researcher agent on a client brief.",
    )
    parser.add_argument("brief", nargs="+", help="The client brief (quoted or as plain words)")
    parser.add_argument("--project", "-p", help="Project name (defaults to first 60 chars of brief)")
    parser.add_argument("--model", default=MODEL, help=f"Gemini model (default: {MODEL})")
    parser.add_argument(
        "--max-iter", type=int, default=MAX_ITERATIONS, dest="max_iter",
        help=f"Max tool-use iterations (default: {MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--no-pace", action="store_true",
        help="Disable free-tier RPM pacing (use after Tier 1 promotion)",
    )
    args = parser.parse_args()

    brief = " ".join(args.brief)
    run_researcher(
        brief,
        project_name=args.project,
        model=args.model,
        max_iter=args.max_iter,
        pace_seconds=0 if args.no_pace else INTER_CALL_DELAY_SEC,
    )


if __name__ == "__main__":
    main()
