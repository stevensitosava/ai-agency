"""Baseline: solo Gemini 2.5 Pro answers the brief in one shot.

No agents, no web search, no revision loop. This is the "naive LLM" comparison
point — what would happen if you just dropped the brief into a chatbot.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Vertex AI endpoint — bypasses AI Studio free-tier daily caps on text models.
# The AQ. key was created for the same project that holds the $300 trial credits.
# Put `VERTEX_API_KEY=AQ...` in .env (gitignored). See README "Free-tier note".
VERTEX_KEY = os.environ.get("VERTEX_API_KEY", "")
PROJECT = os.environ.get("VERTEX_PROJECT", "gen-lang-client-0359845969")
LOCATION = "us-central1"
MODEL = "gemini-2.5-pro"
URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/"
    f"locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
)


def _ensure_key() -> str:
    if not VERTEX_KEY:
        raise RuntimeError(
            "VERTEX_API_KEY not set in .env. The AQ.-format key bypasses "
            "free-tier daily caps via the Vertex AI endpoint."
        )
    return VERTEX_KEY

BASELINE_SYSTEM_PROMPT = """You are a consulting analyst. Take the client brief below and produce a structured proposal in markdown with these sections in order:

# Executive Summary
2-3 sentences. Most important findings + the core recommendation.

# Context
1-2 short paragraphs framing the client situation.

# Findings
Headed subsections. Cite every factual claim with bracketed numbers [1], [2] referring to a flat sources list at the end. If you don't have specific data, say "not yet quantified" instead of inventing numbers.

# Recommendations
Numbered list of 3-5 concrete, actionable recommendations.

# Next Steps
3-4 specific bullet points. Use verbs like draft, decide, schedule, build.

# Sources
A flat numbered list of URLs. If you don't have real sources, leave this empty rather than inventing them.

Style: third-person agency voice, no "I"/"we", plain markdown."""


@dataclass
class BaselineResult:
    output: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_seconds: float


def run_baseline(brief: str) -> BaselineResult:
    """Run solo Gemini 2.5 Pro on the brief. Returns the markdown + metrics."""
    body = {
        "contents": [{"role": "user", "parts": [{"text": brief}]}],
        "systemInstruction": {"parts": [{"text": BASELINE_SYSTEM_PROMPT}]},
        "generationConfig": {"temperature": 0.3},
    }
    started = time.monotonic()
    req = urllib.request.Request(
        f"{URL}?key={_ensure_key()}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())

    duration = time.monotonic() - started
    output = resp["candidates"][0]["content"]["parts"][0]["text"]
    usage = resp.get("usageMetadata", {})
    in_toks = usage.get("promptTokenCount", 0)
    out_toks = usage.get("candidatesTokenCount", 0)
    # Gemini 2.5 Pro pricing: $1.25/M input, $5/M output
    cost = in_toks * 1.25 / 1_000_000 + out_toks * 5 / 1_000_000

    return BaselineResult(
        output=output,
        input_tokens=in_toks,
        output_tokens=out_toks,
        cost_usd=cost,
        duration_seconds=duration,
    )
