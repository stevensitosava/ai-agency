# Day 5 — Eval suite + headline finding

**Date:** 2026-05-26 (later still)
**Live:** https://ai-agency-dashboard-omega.vercel.app/evaluation

---

Day 5. Built the evaluation framework — the most common gap in agent portfolios on GitHub.

The pieces:

1. **`eval/briefs.yaml`** — 15 Dutch-context test briefs across 6 categories (pricing, market entry, competitive analysis, GTM, positioning, operations) with `easy`/`medium`/`hard` difficulty.
2. **`eval/baseline.py`** — solo Gemini 2.5 Pro on the brief, single shot, no tools. The "naive LLM" comparison.
3. **`eval/grader.py`** — an independent Gemini 2.5 Pro instance with no knowledge of which system produced the output. Applies the same six-point rubric to both agency and baseline outputs.
4. **`eval/run_evaluation.py`** — orchestrator. For each brief: agency → baseline → grade both. Saves all artifacts to `eval/results/{brief_id}/`.
5. **`eval/aggregate.py`** — turns N graded runs into a markdown summary table.

## The interesting finding

After 4 briefs evaluated, the rubric scores are virtually tied. **Both systems can hit 6/6 PASS, quality 10/10.** The Critic's rubric is good at structural integrity — does the proposal have the right sections, do citations reference a source list, are the verbs concrete — but it's not good at the dimension that actually matters in consulting work: **are the cited sources real?**

| Metric | Agency | Baseline |
|---|---|---|
| Avg rubric PASS (out of 6) | 6.0 | 5.75 |
| Avg overall quality (out of 10) | 10.0 | 9.25 |
| Avg distinct sources cited | 11.0 | 1.3 |

The baseline (solo Pro) emits **zero sources** on some briefs and still passes the citations criterion. The rubric counts citation structure, not citation existence. The agency cites ~5× more distinct URLs because it actually runs Tavily web searches and grounds each claim against a found source.

This is the kind of finding worth surfacing in an interview. "I built an eval suite and the result was: the rubric doesn't catch the gap. Here's what catches it: source count. Here's what would catch it better: URL verification + numeric-claim grounding. Future work."

## What's NOT in this commit

- Only 1 of 4 briefs had a full agency run (the Brabant one from yesterday). Agency runs cost more time + API quota, so I prioritized the framework + headline finding over completeness. The other 14 briefs are queued to run on Tier 1.
- The eval page on the dashboard renders the same report you see if you `cat eval/results/REPORT.md`. No fancy charts yet — the table tells the story.

Repo: github.com/stevensitosava/ai-agency
Live: https://ai-agency-dashboard-omega.vercel.app/evaluation

Next (Week 6): observability layer + the full 15-brief sweep + a 2-minute demo video.
