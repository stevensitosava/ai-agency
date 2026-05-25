# AI Agency

A virtual consulting agency staffed entirely by AI agents. A user submits a brief; the agency self-organizes — CEO delegates, specialists execute, QA reviews — and delivers downloadable artifacts (PDF reports, PPTX decks, images).

Portfolio project demonstrating production-grade multi-agent orchestration: LangGraph supervisor pattern, two-tier model routing (Haiku + Sonnet), checkpointing, eval suite, observability.

**Status:** Week 1 / 6 — Researcher agent in progress
**Author:** Steven Sawarin · Tilburg, NL
**Stack:** Python 3.11+ · Google Gemini (Flash + Pro) · Tavily · SQLite → Postgres · LangGraph (week 3+) · Next.js (week 4+)

---

## Quick start

```bash
# 1. Install deps (uv handles venv + install in one step)
uv sync

# 2. Copy env, fill in keys
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and TAVILY_API_KEY

# 3. Run the Researcher agent on a sample brief
uv run python -m backend.app.agents.researcher "Market analysis to launch a fitness app in the Netherlands"
```

Notes get saved to `data/notes/`.

---

## 6-week compressed roadmap

| Week | Goal | Ship | Public artifact |
|---|---|---|---|
| **1** | Single-agent foundation | Researcher (web search → notes), raw Anthropic SDK, CLI | GitHub repo + README |
| **2** | Multi-agent loop | Add Copywriter + Critic. PDF deliverable. Three-agent loop with max-3-revisions. | Blog post: "Building a multi-agent loop without LangGraph" |
| **3** | LangGraph refactor | Supervisor pattern, checkpointing, two-tier model routing (Haiku + Sonnet) | Blog post: "Why I rewrote it in LangGraph" |
| **4** | UI + deployment | Next.js dashboard, live message stream, Vercel deploy | Live URL + LinkedIn post #1 |
| **5** | Evaluation rigor | 15 Dutch-context test briefs vs solo Claude. Cost/quality data. | Blog post: "Evaluating a multi-agent system" |
| **6** | Polish + launch | Observability dashboard, cost tracker, demo video, README architecture doc. **Start applying.** | LinkedIn launch post + demo video |

---

## Architecture (final state)

```
                Next.js dashboard (week 4+)
                       │
                       ▼
                FastAPI / WebSockets
                       │
                       ▼
        LangGraph supervisor (CEO agent)
       /        |        |          \
Researcher  Copywriter  Strategist  Critic
       \        |        |          /
        Shared workspace (Postgres + pgvector)
                       │
                  LangSmith traces
```

**Week 1 is much simpler** — single Researcher + SQLite + CLI. The full architecture lands in week 3-4.

---

## Folder layout

```
ai-agency/
├── pyproject.toml         # uv-managed deps
├── .env.example           # template (copy to .env)
├── README.md
├── backend/
│   └── app/
│       ├── agents/        # one file per agent
│       │   └── researcher.py
│       └── tools/         # tool implementations
│           ├── web_search.py
│           └── notes_writer.py
└── data/
    ├── notes/             # agent-generated notes (gitignored)
    └── deliverables/      # final outputs (gitignored)
```

---

## Cost notes

- **Google Gemini** (against $300 trial credits):
  - 2.5 Flash ~$0.075/M input, $0.30/M output — used for Researcher (cheap, fast)
  - 2.5 Pro ~$1.25/M input, $5/M output — used for Strategist + Critic + Copywriter (reasoning)
  - Typical brief end-to-end with two-tier routing: ~$0.05-$0.20
- **Tavily** — free tier covers 1,000 searches/month. Plenty for development + eval suite.
- **Vercel** — free tier for the UI (weeks 4+).
- **Postgres** — local SQLite first, then local Postgres or Supabase free tier.

Budget for the whole 6 weeks: **~$5-$15** out of the $300 Google credits. Plenty of headroom for the eval suite.

The two-tier routing story (Flash for Researcher, Pro for reasoning agents) is one of the headline talking points for interviews — same architecture as Anthropic's Haiku/Sonnet pattern.

---

## Test brief library (build out in week 5)

Dutch-context briefs that signal Tilburg/Brabant relevance:

1. "Market analysis to launch a fitness app in the Netherlands"
2. "Competitive analysis for a Tilburg-area SaaS HR tool targeting SMBs"
3. "Pricing strategy for a B2B fintech entering Brabant manufacturing"
4. "Brand positioning for a Dutch sustainable e-commerce launch"
5. "Customer acquisition plan for a Tilburg restaurant chain expanding to Eindhoven"
6. *(+9 more)*

---

## Why this project

Mirrors what NL companies (CM.com, Vantage AI, Say Hai, Subduxion) sell in 2026. Built to demonstrate end-to-end senior engineering: agent design, cost-aware routing, evaluation, deployment, UX.

The interesting engineering decisions documented as I make them, posted publicly weekly. Build in public.
