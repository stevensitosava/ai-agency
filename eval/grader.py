"""Independent grader — applies the Critic's six-point rubric externally.

The grader is a SEPARATE Gemini 2.5 Pro instance with no knowledge of which
system produced the output. It scores agency output and baseline output the
SAME way, eliminating selection bias.

Why an independent grader (not just the Critic):
- The Critic is part of the agency pipeline — it's already approved/rejected
  the agency output. Using it to grade the baseline too would be fine but
  feels like the agency grading its rival. Cleaner to use a fresh judge.
- The grader uses the identical rubric, so scores are comparable.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Same Vertex AI endpoint as baseline.py — see that file for the rationale.
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
            "VERTEX_API_KEY not set in .env. See eval/baseline.py for setup."
        )
    return VERTEX_KEY


GRADER_SYSTEM_PROMPT = """You are an independent quality grader for consulting proposals. You will be shown a proposal draft and you must score it against this six-point rubric:

1. Structure — has all required sections: Executive Summary, Context, Findings, Recommendations, Next Steps, Sources
2. Citations — every factual claim is backed by a numbered source that matches the source list; sources don't appear invented
3. Specificity — Recommendations and Next Steps use concrete verbs (Implement, Build, Schedule, Decide). Penalize fluff like "explore" or "investigate"
4. Synthesis — findings are reshaped into a coherent narrative, not dumped verbatim from raw research
5. Honesty — admits explicitly when data is missing or uncertain instead of inventing numbers
6. Voice — third-person agency voice; no first-person "I" or "we" in the body

For each criterion, output PASS or FAIL. Also produce a single 0-10 overall_quality score reflecting how client-ready the proposal feels.

You MUST respond with one JSON object (no markdown, no prose):

{
  "rubric_scores": {
    "structure": "PASS" or "FAIL",
    "citations": "PASS" or "FAIL",
    "specificity": "PASS" or "FAIL",
    "synthesis": "PASS" or "FAIL",
    "honesty": "PASS" or "FAIL",
    "voice": "PASS" or "FAIL"
  },
  "pass_count": <integer 0-6>,
  "overall_quality": <integer 0-10>,
  "one_line_assessment": "<one sentence, max 25 words>"
}"""


@dataclass
class Grade:
    rubric_scores: dict[str, str]
    pass_count: int
    overall_quality: int
    one_line_assessment: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


def grade(draft: str) -> Grade:
    """Run the grader against a draft and return structured scores."""
    body = {
        "contents": [{"role": "user", "parts": [{"text": draft}]}],
        "systemInstruction": {"parts": [{"text": GRADER_SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.1,  # deterministic
            "responseMimeType": "application/json",
        },
    }
    req = urllib.request.Request(
        f"{URL}?key={_ensure_key()}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())

    raw = resp["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(raw)

    usage = resp.get("usageMetadata", {})
    in_toks = usage.get("promptTokenCount", 0)
    out_toks = usage.get("candidatesTokenCount", 0)
    cost = in_toks * 1.25 / 1_000_000 + out_toks * 5 / 1_000_000

    return Grade(
        rubric_scores=parsed["rubric_scores"],
        pass_count=parsed["pass_count"],
        overall_quality=parsed["overall_quality"],
        one_line_assessment=parsed["one_line_assessment"],
        input_tokens=in_toks,
        output_tokens=out_toks,
        cost_usd=cost,
    )
