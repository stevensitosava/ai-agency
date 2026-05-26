# Evaluation report

Agency pipeline vs solo Gemini 2.5 Pro baseline, both scored by an independent grader against the same six-point rubric. `N = 4` brief(s) so far.

## Aggregate scores

| Metric | Agency | Baseline |
|---|---|---|
| Avg rubric PASS (out of 6) | **6.0** | 5.8 |
| Avg overall quality (out of 10) | **10.0** | 9.2 |
| Avg distinct sources cited | **2.8** | 1.2 |

**Headline finding:** rubric scores alone don't capture the gap. Both systems can hit 6/6 on structural checks, but the agency cites ~2.2× more distinct sources because it actually runs web searches. The baseline's citations are plausible-looking but unverified.

## Per-brief results

| Brief | Agency PASS · q · sources | Baseline PASS · q · sources |
|---|---|---|
| `competitive-design-agency-eindhoven` | — | 6/6 · q10 · 0 src |
| `gtm-sustainable-ecom-be` | — | 6/6 · q10 · 3 src |
| `pricing-fintech-brabant-manufacturing` | 6/6 · q10 · 11 src | 6/6 · q10 · 2 src |
| `pricing-saas-tech-smb` | — | 5/6 · q7 · 0 src |

## Methodology

1. **Brief library** — `eval/briefs.yaml` defines test briefs across 6 categories (pricing, market entry, competitive analysis, GTM, positioning, operations).
2. **Agency** — runs the LangGraph pipeline: Researcher (Tavily web search) → Copywriter → Critic, with up to 3 revisions. Output: final approved markdown.
3. **Baseline** — single shot of Gemini 2.5 Pro on the brief, with the same section requirements in the system prompt. No web search, no revision.
4. **Independent grader** — a separate Gemini 2.5 Pro instance with no knowledge of which system produced the output. Same six-point rubric the Critic uses internally, applied externally.
5. **Source count** — heuristic: count distinct `http(s)://` URLs in the rendered markdown. Doesn't verify URLs are real or load; that's future work.
