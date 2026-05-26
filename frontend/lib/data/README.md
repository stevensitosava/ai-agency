# Sample Deliverables

Real output produced by the agency on real briefs. Unedited agent output saved directly from pipeline runs.

## Brabant fintech pricing strategy — full revision cycle ✅ APPROVED

A complete end-to-end run of the agency on a Dutch B2B fintech brief, including the Critic's revision loop closing successfully on revision 1.

| File | What it is |
|---|---|
| [`pricing-strategy-brabant-fintech.md`](pricing-strategy-brabant-fintech.md) | First Copywriter draft from the research notes |
| [`pricing-strategy-brabant-fintech-critic-verdict.json`](pricing-strategy-brabant-fintech-critic-verdict.json) | Critic's verdict on draft 1: **REVISE** (5/6 PASS, FAIL on citations) |
| [`pricing-strategy-brabant-fintech-FINAL.md`](pricing-strategy-brabant-fintech-FINAL.md) | Revised draft after Copywriter addressed the citation feedback |
| [`pricing-strategy-brabant-fintech-critic-verdict-FINAL.json`](pricing-strategy-brabant-fintech-critic-verdict-FINAL.json) | Critic's verdict on revision: **APPROVE** (6/6 PASS, empty feedback) |

### The narrative arc

1. **Researcher** → 4 cited research notes (Brabant manufacturing, competitive landscape, pricing models, value-based pricing)
2. **Copywriter** → produces draft 1
3. **Critic** → REVISE: "Executive Summary and Context lack citations. Citation numbers in Findings don't match the source they reference."
4. **Copywriter** (revision) → produces draft 2 addressing both points
5. **Critic** (round 2) → APPROVE. All six rubric criteria PASS.

### Total cost: ~$0.03

| Phase | Model | Cost |
|---|---|---|
| Researcher (4 notes) | Gemini 2.5 Flash | ~$0.007 |
| Copywriter draft 1 | Gemini 2.5 Flash | ~$0.005 |
| Critic verdict 1 | Gemini 2.5 Pro | $0.00375 |
| Copywriter draft 2 (revision) | Gemini 2.5 Pro | $0.01385 |
| Critic verdict 2 | Gemini 2.5 Pro | $0.00253 |
| **Total** | | **~$0.03** |

A real consulting proposal with cited claims, concrete recommendations, validated by an independent quality gate — for under 3 cents.

### What the Critic actually caught (verdict round 1)

> *"Factual claims in the Executive Summary and Context sections lack citations. Every claim about market size, regional characteristics, or industry challenges must be sourced."*

> *"There are numerous incorrect citations in the Findings section. The cited source number often does not match the content of the claim... All citations must be reviewed and corrected to point to the appropriate source for the specific claim being made."*

Specific. Actionable. Pointed to exact sections. This is the differentiator vs. generic "improve the writing" LLM feedback.

### How to regenerate

```bash
uv run python -m backend.app.pipeline "Pricing strategy for a Dutch B2B fintech entering Brabant manufacturing"
```

On Tier 1 (no free-tier daily caps), this runs end-to-end in ~30 seconds. On free tier with pacing, ~6-8 minutes.
