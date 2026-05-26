import Link from "next/link";

export const metadata = {
  title: "Engineering notes · AI Agency",
  description:
    "Decisions I'd defend in an interview: why raw Python before LangGraph, two-tier model routing, structured JSON over regex, what the eval suite found.",
};

export default function NotesPage() {
  return (
    <article className="max-w-3xl mx-auto px-6 py-12">
      <div className="font-mono text-xs uppercase tracking-[0.2em] text-accent mb-6">
        ● Engineering notes
      </div>
      <h1 className="font-serif text-4xl lg:text-5xl leading-tight tracking-tight text-ink mb-6 max-w-2xl">
        Five decisions I&rsquo;d defend in an interview.
      </h1>
      <p className="text-ash text-lg leading-relaxed mb-16 max-w-2xl">
        The architecture decisions that actually mattered while building this.
        Each one comes from running into a wall, choosing a path, and learning
        whether the path was right. No buzzwords.
      </p>

      <Note
        num="01"
        title="Raw Python first, framework second"
        body={
          <>
            <p>
              Week 1–2 was a plain Python loop. <code>brief → Researcher
              → Copywriter → Critic → maybe revise → done</code>. No
              LangGraph, no LangChain, no abstraction. The agents were three
              functions, the loop was a <code>for revision in range(N)</code>{" "}
              block.
            </p>
            <p>
              That code{" "}
              <Link href="/runs/brabant-fintech-pricing">
                produced a Critic-APPROVED consulting proposal
              </Link>{" "}
              for $0.03 in week 2. Working. Tested. Done.
            </p>
            <p>
              I only rewrote it as a LangGraph <code>StateGraph</code> in week 3
              when three concrete things justified the complexity:
            </p>
            <ol>
              <li>
                <strong>Checkpointing.</strong> Every state transition
                persists to <code>data/db/checkpoints.sqlite</code>. An
                interrupted run resumes from the last node, no re-running the
                expensive Researcher.
              </li>
              <li>
                <strong>State as data.</strong> Every node returns a partial
                state dict. No hidden globals. Testable without API calls — see
                the 17 graph tests in <code>tests/test_graph.py</code>.
              </li>
              <li>
                <strong>Conditional routing as a pure function.</strong>{" "}
                <code>decide_after_critic(state)</code> is one function deciding
                APPROVE → finalize, REVISE → re-draft, cap-reached → ship.
                Provably terminates.
              </li>
            </ol>
            <p>
              The reverse order — &ldquo;reach for the framework first&rdquo; —
              is the common junior mistake. Most LangGraph repos on GitHub
              would&rsquo;ve been clearer as plain Python loops.
            </p>
          </>
        }
      />

      <Note
        num="02"
        title="Two-tier model routing"
        body={
          <>
            <p>
              The Researcher runs <strong>Gemini 2.5 Flash</strong> — it&rsquo;s
              looping over web searches, synthesis is cheap. The Critic runs{" "}
              <strong>Gemini 2.5 Pro</strong> — judgment quality matters, and
              the Critic only runs 1–4 times per brief total.
            </p>
            <p>
              This is the same pattern as Anthropic&rsquo;s Haiku-for-extraction
              + Sonnet-for-reasoning. The savings compound: ~7,000 tokens of
              Researcher loop on Flash costs $0.005; the same tokens on Pro
              would cost $0.10. The Critic uses ~3,000 tokens once, costs
              $0.005. End-to-end: $0.03 per brief.
            </p>
            <p>
              The Copywriter sits in the middle — defaults to Flash for first
              drafts, accepts <code>--model gemini-2.5-pro</code> when quality
              matters more than speed (e.g. the high-stakes revision pass).
            </p>
          </>
        }
      />

      <Note
        num="03"
        title="Structured JSON output, not regex-parsing prose"
        body={
          <>
            <p>
              The Critic returns its verdict via Gemini&rsquo;s{" "}
              <code>responseMimeType: &quot;application/json&quot;</code>{" "}
              configuration. The model is constrained at generation time to
              produce a single valid JSON object matching a known shape:
            </p>
            <pre>{`{
  "verdict": "APPROVE" or "REVISE",
  "feedback": "<numbered list or empty>",
  "rubric_scores": {
    "structure": "PASS" or "FAIL",
    "citations": "PASS" or "FAIL",
    ...four more...
  }
}`}</pre>
            <p>
              No regex over markdown. No &ldquo;please respond in this
              format&rdquo; in the prompt and hope. The supervisor function
              reads <code>state[&quot;verdict&quot;]</code> directly and routes
              accordingly.
            </p>
            <p>
              This is the boring-but-load-bearing detail in agent systems. Most
              implementations parse free-form text and break the first time the
              model says &ldquo;Sure! Here&rsquo;s my verdict:&rdquo; before the
              JSON. <code>responseMimeType</code> eliminates that whole class of
              bug.
            </p>
          </>
        }
      />

      <Note
        num="04"
        title="The eval suite found a real gap"
        body={
          <>
            <p>
              The whole point of building an{" "}
              <Link href="/evaluation">eval suite</Link> is to learn something
              uncomfortable about your own system. Mine taught me this: the
              Critic&rsquo;s six-point rubric doesn&rsquo;t catch the
              difference that matters most.
            </p>
            <p>
              When I ran the same brief through (a) the full agency pipeline
              and (b) a solo Gemini 2.5 Pro one-shot baseline, an independent
              grader gave both a 6/6 PASS. Identical structural integrity.
            </p>
            <p>
              But: the agency cited <strong>11 distinct URLs</strong>. The
              baseline cited <strong>2</strong>. On other briefs the baseline
              cited <strong>zero</strong> and still passed the citation
              criterion, because the rubric checks structure
              (&ldquo;numbered, in source list&rdquo;), not existence
              (&ldquo;the URL loads and contains the claim&rdquo;).
            </p>
            <p>
              That&rsquo;s a real finding. The agency&rsquo;s value isn&rsquo;t
              that it scores higher on a flawed rubric — it&rsquo;s that it
              grounds claims in actual web sources. The fix for the rubric is
              future work: load each cited URL, verify it responds 200, check
              the claim appears in the page text.
            </p>
          </>
        }
      />

      <Note
        num="05"
        title="What I&rsquo;d build differently in week 7"
        body={
          <>
            <ol>
              <li>
                <strong>Source verification step.</strong> Block the
                Critic&rsquo;s APPROVE verdict until every cited URL returns
                200 and the corresponding claim text matches the page contents
                via a fuzzy match. This raises the floor on hallucination.
              </li>
              <li>
                <strong>Per-claim grounding tracker.</strong> Extract every
                numeric claim ($X bn, Y%, Z employees) and validate against
                the source list. Right now nothing checks if &ldquo;€14B Dutch
                HR market&rdquo; matches the cited source&rsquo;s actual
                number.
              </li>
              <li>
                <strong>Async pipeline.</strong> The Researcher runs
                searches sequentially with a 15s free-tier delay. On Tier 1,
                running searches in parallel cuts wall time by ~3×. Easy win
                once quota allows.
              </li>
              <li>
                <strong>Plug in a Strategist agent.</strong> Right now the
                Copywriter does both findings synthesis and recommendation
                generation. Splitting these into two specialized roles would
                make the eval comparison sharper (and is how a real consulting
                firm divides the work).
              </li>
              <li>
                <strong>Submit-a-brief form.</strong> The dashboard currently
                browses past runs. The next interaction layer is letting a
                visitor type a brief and watch the agents work in real time
                via SSE. Needs a long-lived Python backend, which Vercel
                serverless functions can&rsquo;t host. A small Fly.io or
                Railway deploy fixes that.
              </li>
            </ol>
          </>
        }
      />

      <hr className="border-t border-rule my-16" />

      <section className="mb-16">
        <div className="font-mono text-xs uppercase tracking-[0.2em] text-accent mb-4">
          Reach out
        </div>
        <h2 className="font-serif text-3xl text-ink mb-4">
          I&rsquo;m looking for AI engineering roles in Tilburg / Brabant.
        </h2>
        <p className="text-ash text-lg leading-relaxed mb-6 max-w-2xl">
          If you&rsquo;re hiring for someone who can take an agent system from
          empty repo to shipped portfolio in six weeks while keeping the
          engineering decisions defensible — let&rsquo;s talk.
        </p>
        <div className="flex flex-wrap gap-3">
          <a
            href="mailto:srssdesing@gmail.com?subject=AI%20Agency%20—%20chat%3F"
            className="bg-ink text-cream px-5 py-3 text-sm font-medium hover:bg-accent transition-colors inline-flex items-center gap-2"
          >
            Email
            <span className="font-mono">→</span>
          </a>
          <a
            href="https://stevensawarin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-rule text-ink px-5 py-3 text-sm font-medium hover:border-ink transition-colors inline-flex items-center gap-2"
          >
            stevensawarin.com
            <span className="font-mono">↗</span>
          </a>
          <a
            href="https://github.com/stevensitosava"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-rule text-ink px-5 py-3 text-sm font-medium hover:border-ink transition-colors inline-flex items-center gap-2"
          >
            GitHub
            <span className="font-mono">↗</span>
          </a>
        </div>
      </section>
    </article>
  );
}

function Note({
  num,
  title,
  body,
}: {
  num: string;
  title: string;
  body: React.ReactNode;
}) {
  return (
    <section className="mb-16">
      <div className="flex items-baseline gap-4 mb-6">
        <div className="font-serif text-3xl text-accent leading-none shrink-0">
          {num}
        </div>
        <h2 className="font-serif text-2xl lg:text-3xl text-ink leading-tight tracking-tight">
          {title}
        </h2>
      </div>
      <div className="prose-doc ml-0 lg:ml-12">{body}</div>
    </section>
  );
}
