# Day 1 — Researcher agent shipped

**Posted:** 2026-05-26 · LinkedIn

---

Day 1 of building an AI consulting agency.

The idea: a virtual agency where every employee is an AI agent. A user submits a brief, the agents self-organize — CEO delegates, specialists execute, QA reviews — and you get a real deliverable (PDF report, deck, image).

Shipped today: the Researcher agent.

How it works:
→ Reads a client brief
→ Plans 3-5 sub-topics to investigate
→ Searches the web (Tavily)
→ Writes cited markdown notes to disk

One real run today: "Market entry analysis for a B2B HR-tech SaaS targeting 10-50 person companies in Tilburg/Eindhoven."

Result: 5 research notes with cited sources, including specifics like the Dutch HR software market valued at €14B in 2025 with 8.59% CAGR projected through 2033.

Cost: $0.007. Less than a cent.

The engineering decisions I'm most proud of after a few hours of work:

→ Two-tier model routing prep — Researcher uses Gemini 2.5 Flash (cheap, fast), reasoning agents will use Gemini 2.5 Pro later. Same pattern as Anthropic's Haiku/Sonnet.

→ Retry handling for free-tier rate limits (5 RPM) and 503 overloads with exponential backoff.

→ "Honest" prompt: the agent admits when it can't find data instead of inventing numbers. One of today's notes literally says "Obtaining precise statistics... proved challenging" — exactly the kind of behavior I want.

→ Built the tool-use loop without a framework first. LangGraph comes in week 3 — only when I've felt the pain the framework solves.

6-week plan, building in public, applying for AI engineering roles in Tilburg/Brabant when it ships.

Repo: github.com/stevensitosava/ai-agency

Follow along if you're into agent design, evals, or hiring people who ship.

#AIAgents #BuildInPublic #SoftwareEngineering #Tilburg #Gemini

---

## Image suggestion (attach to the post)

The terminal output from today's full run is the strongest visual — shows the agent's iteration count, notes written, tokens, and the $0.007 cost number in a clean Rich-formatted panel. Take a screenshot of:

```
┌─────────── Done ────────────┐
│ Iterations: 20              │
│ Notes written: 4            │
│ Tokens: 86150 in / 1867 out │
│ Estimated cost: $0.00702    │
└─────────────────────────────┘
```

Or a screenshot of one of the generated research notes — the one at `data/notes/.../dutch-hr-tech-market-size-trends.md` shows real cited sources, which is the most credibility-building visual.

---

## Posting checklist

- [ ] Open https://linkedin.com/post (or your LinkedIn home, click "Start a post")
- [ ] Paste the post body (lines marked with → render fine on LinkedIn — they accept all Unicode)
- [ ] Attach the terminal screenshot OR a screenshot of the cited research note
- [ ] Hit post Tuesday-Thursday 8-10 AM NL time for max engagement
- [ ] After 24h: comment on your own post with a follow-up like "Day 2 update coming Friday — Copywriter agent + the first PDF"
- [ ] Set a reminder for the Day 7 / Week 1 wrap post
