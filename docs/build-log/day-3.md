# Day 3 — LangGraph refactor lands

**Date:** 2026-05-26 (continued)

---

Day 3 of building the AI consulting agency. Today: rewrote the orchestration layer to use LangGraph's `StateGraph`.

Why now, not Day 1?

Week 1-2 was a plain Python loop. Brief → Researcher → Copywriter → Critic → maybe revise → done. Worked perfectly. The Critic produced a real APPROVE verdict yesterday on a Brabant fintech proposal for $0.03 total. So why touch it?

Three concrete things LangGraph adds that the loop didn't have:

1. **Checkpointing.** The agency now persists every state transition to `data/db/checkpoints.sqlite` via `SqliteSaver`. An interrupted run resumes from the last node — no re-running the Researcher (which costs the most). Try it: kill the process mid-Copywriter, then `--resume` to pick up where you left off.

2. **State as data.** Every node returns a partial `AgencyState` delta. No hidden globals, no function-call gymnastics. The supervisor decision is one pure function:

   ```python
   def decide_after_critic(state) -> Literal["copywrite", "finalize"]:
       if state["verdict"] == "APPROVE":
           return "finalize"
       if state["revisions"] + 1 >= state["max_revisions"]:
           return "finalize"  # cap reached
       return "copywrite"
   ```

   This function is tested 6 different ways in `tests/test_graph.py`. Provably terminates.

3. **The graph is the documentation.** `g.get_graph().draw_mermaid()` exports the actual orchestration as a Mermaid diagram. The README embeds it. No drift between docs and code.

What didn't change: the agents themselves. `researcher.py`, `copywriter.py`, and `critic.py` are still framework-free Python functions that take state in and return state out. LangGraph wraps them, doesn't replace them.

Tests: 30/30 passing in 0.04s.

Repo: github.com/stevensitosava/ai-agency

Next: Next.js dashboard (Week 4) — give the agent loop a visible heartbeat.
