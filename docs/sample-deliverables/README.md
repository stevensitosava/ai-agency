# Sample Deliverables

Real output produced by the agency on real briefs. These are not curated cherry-picks — they're verbatim agent output saved during pipeline runs.

## How to read these

Each file is the **draft proposal** that came out of the Copywriter agent after the Researcher had gathered notes. The Critic step (which approves or sends back for revision) was not run on these particular drafts due to free-tier quota timing — but the drafts themselves are unedited agent output.

| File | Brief |
|---|---|
| [`pricing-strategy-brabant-fintech.md`](pricing-strategy-brabant-fintech.md) | "Pricing strategy for a Dutch B2B fintech entering Brabant manufacturing" |

## What "good" looks like

The Critic's six-point rubric:
1. **Structure** — Executive Summary, Context, Findings, Recommendations, Next Steps, Sources (all present)
2. **Citations** — every factual claim backed by a numbered source
3. **Specificity** — Recommendations use concrete verbs (Implement, Offer, Develop), Next Steps use action verbs (Draft, Develop, Schedule, Build) — no "explore" or "investigate"
4. **Synthesis** — notes are reshaped into a narrative, not dumped verbatim
5. **Honesty** — explicit when data is missing (e.g. "This is an inference from the research note stating 'not explicitly detailed'")
6. **Voice** — third-person agency voice, no first-person

The Brabant fintech deliverable passes all six on a read-through.

## How they were generated

```bash
uv run python -m backend.app.pipeline "Pricing strategy for a Dutch B2B fintech entering Brabant manufacturing"
```

Total cost: under $0.05 per deliverable (Gemini 2.5 Flash for Researcher + Copywriter, Pro for Critic when quota permits).

Time end-to-end: 3-6 minutes on free-tier pacing; ~30 seconds on Tier 1.
