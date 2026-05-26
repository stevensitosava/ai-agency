# Day 4 — Next.js dashboard live on Vercel

**Date:** 2026-05-26 (later)
**Live:** https://ai-agency-dashboard-omega.vercel.app

---

Day 4 of building the AI consulting agency. Today: shipped the Next.js dashboard. Recruiters can now click a link and see real agent output, not just code.

The build is intentionally restrained:

- **Fraunces** for editorial display + **Geist** for body + **JetBrains Mono** for metadata. No Inter, no Helvetica.
- Cream / ink / burnt-amber palette. No purple-to-blue gradient. No glass morphism. No card-in-card.
- Server components throughout — every page is statically prerendered at build time. Zero JavaScript needed to read the deliverables.
- One route per concept: `/` (what + how), `/runs` (everything the agency has done), `/runs/[slug]` (one run end-to-end).

The detail page tells the full narrative of a single brief:

1. Researcher gathers cited evidence
2. Copywriter drafts the proposal
3. Critic reviews — APPROVE or REVISE with specific feedback
4. If REVISE, Copywriter rewrites addressing each numbered item
5. Critic re-reviews and approves

The Critic's verdicts render as a structured panel — six rubric criteria, each as a PASS / FAIL badge. The full revision history is visible in scroll order. Nothing hidden.

The data layer in `lib/runs.ts` is a thin filesystem reader that pulls the markdown + JSON straight from `lib/data/` (copied from the repo's canonical `docs/sample-deliverables/`). Future runs land here automatically by adding one entry to the `RUN_INDEX` array.

What didn't ship today: the "submit a brief" form. That needs a Python backend deployed somewhere that can run the LangGraph for ~30 seconds — Vercel functions cap at 60s, which fits, but the Tier 1 promotion question is still in flight. Saving for Week 5 alongside the eval suite.

Repo: github.com/stevensitosava/ai-agency
Live: https://ai-agency-dashboard-omega.vercel.app

Next: Week 5 — eval suite (15 Dutch-context briefs vs solo-Gemini baseline) + the submission form.
