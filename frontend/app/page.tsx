import Link from "next/link";
import { listRuns } from "../lib/runs";

export default function Home() {
  const runs = listRuns();

  return (
    <div>
      {/* HERO */}
      <section className="border-b border-rule">
        <div className="max-w-5xl mx-auto px-6 py-20 lg:py-28">
          <div className="font-mono text-xs uppercase tracking-[0.2em] text-accent mb-6">
            ● Multi-agent consulting system
          </div>
          <h1 className="font-serif text-5xl lg:text-7xl leading-[1.05] tracking-tight text-ink max-w-3xl">
            A virtual consulting agency
            <br />
            <em className="not-italic text-accent font-normal italic">
              staffed by AI agents.
            </em>
          </h1>
          <p className="text-ash text-lg leading-relaxed max-w-2xl mt-8">
            A user submits a brief. The agents self-organize — Researcher
            gathers cited evidence, Copywriter drafts the proposal, Critic
            reviews it against a six-point rubric and bounces it back for
            revision if it doesn&rsquo;t pass. The loop terminates with a
            client-grade deliverable in under three cents of API cost.
          </p>
          <div className="flex flex-wrap gap-3 mt-10">
            <Link
              href="/runs"
              className="bg-ink text-cream px-5 py-3 text-sm font-medium hover:bg-accent transition-colors inline-flex items-center gap-2"
            >
              See sample runs
              <span className="font-mono">→</span>
            </Link>
            <a
              href="https://github.com/stevensitosava/ai-agency"
              target="_blank"
              rel="noopener noreferrer"
              className="border border-rule text-ink px-5 py-3 text-sm font-medium hover:border-ink transition-colors inline-flex items-center gap-2"
            >
              Read the code
              <span className="font-mono">↗</span>
            </a>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-b border-rule">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="font-mono text-xs uppercase tracking-[0.16em] text-mute mb-4">
            How it works
          </div>
          <h2 className="font-serif text-3xl lg:text-4xl leading-tight tracking-tight text-ink max-w-2xl mb-12">
            Four nodes, one bounded loop.
          </h2>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-8">
            {[
              {
                num: "01",
                title: "Researcher",
                body:
                  "Plans 3–5 sub-topics, runs Tavily web searches, writes cited markdown notes to disk. Uses Gemini 2.5 Flash. Tool-use loop with rate-limit retry.",
              },
              {
                num: "02",
                title: "Copywriter",
                body:
                  "Loads the notes, drafts a six-section proposal (Exec Summary, Context, Findings, Recommendations, Next Steps, Sources). Cites every factual claim.",
              },
              {
                num: "03",
                title: "Critic",
                body:
                  "Reviews against six rubric points: structure, citations, specificity, synthesis, honesty, voice. Returns structured JSON — APPROVE or REVISE with specific feedback.",
              },
              {
                num: "04",
                title: "Supervisor",
                body:
                  "Conditional edge in the LangGraph. APPROVE → ship. REVISE with budget → loop back. Cap reached → ship as-is. Provably terminates.",
              },
            ].map((step) => (
              <div key={step.num} className="flex gap-5">
                <div className="font-serif text-4xl text-accent leading-none shrink-0">
                  {step.num}
                </div>
                <div>
                  <h3 className="font-serif text-xl text-ink mb-2">
                    {step.title}
                  </h3>
                  <p className="text-ash leading-relaxed text-[15px]">
                    {step.body}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED RUN */}
      {runs.length > 0 && (
        <section className="border-b border-rule">
          <div className="max-w-5xl mx-auto px-6 py-16">
            <div className="font-mono text-xs uppercase tracking-[0.16em] text-mute mb-4">
              Featured run
            </div>
            <h2 className="font-serif text-3xl lg:text-4xl leading-tight tracking-tight text-ink max-w-2xl mb-2">
              Real output, real cost.
            </h2>
            <p className="text-ash mb-10 max-w-2xl">
              These are unedited agent deliverables saved during pipeline runs.
              Every claim is cited; every revision is logged.
            </p>
            <Link
              href={`/runs/${runs[0].slug}`}
              className="block border border-rule hover:border-ink transition-colors p-8 bg-cream"
            >
              <div className="flex items-start justify-between gap-6 mb-4">
                <div>
                  <div className="font-mono text-xs uppercase tracking-[0.14em] text-mute mb-2">
                    {runs[0].niche}
                  </div>
                  <h3 className="font-serif text-2xl text-ink leading-tight">
                    {runs[0].brief}
                  </h3>
                </div>
                <span className="bg-accent-soft text-accent font-mono text-[10px] uppercase tracking-[0.15em] px-2 py-1 rounded-full shrink-0">
                  ● {runs[0].status}
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-6 pt-6 border-t border-rule">
                <Stat label="Date" value={runs[0].date} />
                <Stat label="Notes" value={`${runs[0].notes}`} />
                <Stat label="Revisions" value={`${runs[0].revisions}`} />
                <Stat label="Cost" value={runs[0].cost} accent />
              </div>
            </Link>
          </div>
        </section>
      )}

      {/* STACK */}
      <section>
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="font-mono text-xs uppercase tracking-[0.16em] text-mute mb-4">
            Stack
          </div>
          <h2 className="font-serif text-3xl lg:text-4xl leading-tight tracking-tight text-ink max-w-2xl mb-10">
            Production-shaped, week by week.
          </h2>
          <div className="grid md:grid-cols-3 gap-y-10 gap-x-12">
            <StackItem
              num="W1–2"
              title="Plain Python loop"
              body="google-genai SDK, Tavily, pytest. No framework until complexity earned it."
            />
            <StackItem
              num="W3"
              title="LangGraph + SQLite"
              body="StateGraph with 5 nodes, conditional edge, SqliteSaver checkpointing. Resumable runs."
            />
            <StackItem
              num="W4"
              title="Next.js dashboard"
              body="This site. App Router, server components, restrained design system, deployed to Vercel."
            />
            <StackItem
              num="W5"
              title="Eval suite"
              body="15 Dutch-context briefs vs solo-Gemini baseline. Cost / quality / latency numbers."
            />
            <StackItem
              num="W6"
              title="Observability"
              body="Per-agent cost dashboard, LangSmith traces, demo video, README architecture."
            />
            <StackItem
              num="Now"
              title="Open to roles"
              body={
                <>
                  Tilburg / Brabant AI engineering. See{" "}
                  <Link href="/notes" className="text-accent underline">
                    engineering notes
                  </Link>{" "}
                  for the decisions worth defending.
                </>
              }
            />
          </div>
        </div>
      </section>

      {/* HIRE CTA */}
      <section className="bg-ink text-cream">
        <div className="max-w-5xl mx-auto px-6 py-20">
          <div className="font-mono text-xs uppercase tracking-[0.2em] text-[#E89456] mb-6">
            ● Hiring signal
          </div>
          <h2 className="font-serif text-3xl lg:text-5xl leading-tight tracking-tight mb-6 max-w-3xl">
            Six weeks. Eleven commits.
            <br />
            <em className="text-[#E89456] not-italic font-normal italic">
              One shipped portfolio piece.
            </em>
          </h2>
          <p className="text-[rgba(250,247,241,0.75)] text-lg leading-relaxed max-w-2xl mb-10">
            If you&rsquo;re hiring AI engineers in Tilburg or Brabant and want
            someone who can take a multi-agent system from empty repo to
            shipped product while keeping every architecture decision
            defensible — let&rsquo;s talk.
          </p>
          <div className="flex flex-wrap gap-3">
            <a
              href="mailto:srssdesing@gmail.com?subject=AI%20Agency%20—%20chat%3F"
              className="bg-cream text-ink px-6 py-3.5 text-sm font-medium hover:bg-[#E89456] hover:text-cream transition-colors inline-flex items-center gap-2"
            >
              Email Steven
              <span className="font-mono">→</span>
            </a>
            <a
              href="https://stevensawarin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="border border-[rgba(250,247,241,0.25)] text-cream px-6 py-3.5 text-sm font-medium hover:bg-[rgba(250,247,241,0.08)] transition-colors inline-flex items-center gap-2"
            >
              stevensawarin.com
              <span className="font-mono">↗</span>
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div>
      <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-mute mb-1">
        {label}
      </div>
      <div
        className={`font-serif text-xl ${accent ? "text-accent" : "text-ink"}`}
      >
        {value}
      </div>
    </div>
  );
}

function StackItem({
  num,
  title,
  body,
}: {
  num: string;
  title: string;
  body: React.ReactNode;
}) {
  return (
    <div>
      <div className="font-mono text-xs text-accent tracking-[0.1em] mb-2">
        {num}
      </div>
      <h3 className="font-serif text-lg text-ink mb-2">{title}</h3>
      <p className="text-ash text-[14.5px] leading-relaxed">{body}</p>
    </div>
  );
}
