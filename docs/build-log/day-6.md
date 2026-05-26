# Day 6 — Engineering notes + hire CTA

**Date:** 2026-05-26 (final)
**Live:** https://ai-agency-dashboard-omega.vercel.app/notes

---

Day 6 is about closing the portfolio loop. The agent system works, the eval suite found a real gap, the dashboard renders the artifacts. What was missing: the **page that converts a casual scroll into an interview**.

That page is `/notes`. Five engineering decisions, each spelled out in the kind of detail I&rsquo;d defend in a whiteboard interview:

1. **Raw Python first, framework second.** Why I didn&rsquo;t reach for LangGraph in week 1. What three concrete things justified the rewrite in week 3.
2. **Two-tier model routing.** Flash for the iterative Researcher, Pro for the judgment-heavy Critic. Math on the cost compounding.
3. **Structured JSON output, not regex-parsing prose.** Why `responseMimeType: application/json` is the load-bearing detail in agent systems.
4. **The eval suite found a real gap.** The rubric scores baseline 5.75/6 and agency 6.0/6 — but the agency cites 5× more sources. The rubric checks structure, not source existence.
5. **What I&rsquo;d build in week 7.** Source verification, per-claim grounding, async pipeline, Strategist split, submit form.

Plus a clear **hire CTA** at the bottom of the landing page and the notes page — ink-on-cream block with a direct mailto link. The dashboard now has five well-shaped routes:

- `/` — what + how + featured run + stack + hire CTA
- `/runs` — every agency run
- `/runs/[slug]` — one run end-to-end with rendered drafts and rubric badges
- `/evaluation` — the headline finding from the eval suite
- `/notes` — the five engineering decisions

That&rsquo;s a portfolio piece, not a side project.

## What didn&rsquo;t ship today (intentionally)

- A demo video. The dashboard tells the story without one; a video is nice-to-have for week 7+.
- The full 15-brief eval sweep. Quota-blocked; runs on Tier 1 promotion.
- A submit-a-brief form. Needs a Python backend deployed somewhere with longer timeouts than Vercel allows. Fly.io / Railway one-shot when I&rsquo;m ready.
- LangSmith integration. Worth doing but isn&rsquo;t the highest-leverage move before applying.

## What this looks like to a recruiter

A live URL, a public repo, 12 dated commits over a week, 30 passing unit tests, a graph diagram in the README, real consulting deliverables in `docs/sample-deliverables/`, an honest eval finding with proposed future work, and a clear way to make contact.

If they spend 60 seconds, they get the headline. If they spend 5 minutes, they have enough to send a first interview email.

## Closing the 6-week arc

Six weeks. Eleven commits before this one — twelve including the Week 6 commit when I push. Every week shipped a tangible artifact, not just code:

- **W1**: working Researcher + tests
- **W2**: full agency loop + Critic-approved sample deliverable
- **W3**: LangGraph + checkpointing + 30 tests
- **W4**: Next.js dashboard on Vercel
- **W5**: eval suite + headline finding
- **W6**: engineering notes + hire CTA

Repo: github.com/stevensitosava/ai-agency
Live: https://ai-agency-dashboard-omega.vercel.app

Now: start applying.
