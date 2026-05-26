import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getRun, listRuns, type RubricScores, type Verdict } from "../../../lib/runs";

export async function generateStaticParams() {
  return listRuns().map((r) => ({ slug: r.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const run = getRun(slug);
  if (!run) return { title: "Run · AI Agency" };
  return { title: `${run.brief} · AI Agency` };
}

export default async function RunDetail({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const run = getRun(slug);
  if (!run) notFound();

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* breadcrumb */}
      <Link
        href="/runs"
        className="font-mono text-xs text-mute hover:text-ink transition-colors inline-flex items-center gap-1.5"
      >
        ← all runs
      </Link>

      {/* header */}
      <div className="mt-6 pb-10 border-b border-rule">
        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-accent mb-3">
          ● {run.niche} · {run.date}
        </div>
        <h1 className="font-serif text-3xl lg:text-4xl leading-tight tracking-tight text-ink">
          {run.brief}
        </h1>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-8">
          <Stat label="Final status" value={run.status} accent />
          <Stat label="Notes gathered" value={`${run.notes}`} />
          <Stat label="Revisions" value={`${run.revisions}`} />
          <Stat label="Total cost" value={run.cost} accent />
        </div>
      </div>

      {/* The narrative — chronological */}
      <Step
        index="01"
        label="Researcher"
        title="Gathered evidence"
        description={`Ran ${run.notes} focused web searches via Tavily, wrote one cited markdown note per sub-topic.`}
      />

      <Step
        index="02"
        label="Copywriter — Draft 1"
        title="First draft"
        description="Loaded the research notes, drafted a structured proposal across six required sections."
      />
      <DraftViewer markdown={run.draftFirst} />

      <Step
        index="03"
        label="Critic — Verdict 1"
        title="First review"
        description="Reviewed against the six-point rubric. Each criterion graded PASS / FAIL."
      />
      <VerdictPanel verdict={run.verdictFirst} />

      <Step
        index="04"
        label="Copywriter — Revision"
        title="Revised draft"
        description="Re-drafted addressing each numbered item from the Critic&rsquo;s feedback."
      />
      <DraftViewer markdown={run.draftFinal} />

      <Step
        index="05"
        label="Critic — Final verdict"
        title="Final review"
        description="Re-reviewed the revision against the same rubric."
      />
      <VerdictPanel verdict={run.verdictFinal} />

      <div className="mt-16 p-6 border border-rule bg-paper">
        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute mb-2">
          Reproduce
        </div>
        <pre className="font-mono text-[13px] text-ink overflow-x-auto">
          <code>
            uv run python -m backend.app.pipeline \
            <br />
            &nbsp;&nbsp;{`"${run.brief}"`}
          </code>
        </pre>
        <p className="text-ash text-sm mt-3 leading-relaxed">
          On Tier 1 (paid billing linked), this runs end-to-end in ~30 seconds.
          On the free tier with rate-limit pacing, ~6 minutes.
        </p>
      </div>
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

function Step({
  index,
  label,
  title,
  description,
}: {
  index: string;
  label: string;
  title: string;
  description: string;
}) {
  return (
    <div className="mt-14 mb-4">
      <div className="flex items-baseline gap-4">
        <div className="font-serif text-3xl text-accent leading-none">
          {index}
        </div>
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute">
            {label}
          </div>
          <h2 className="font-serif text-2xl text-ink leading-tight mt-1">
            {title}
          </h2>
        </div>
      </div>
      <p
        className="text-ash mt-3 ml-12 leading-relaxed"
        dangerouslySetInnerHTML={{ __html: description }}
      />
    </div>
  );
}

function DraftViewer({ markdown }: { markdown: string }) {
  return (
    <div className="border border-rule bg-cream mt-2">
      <div className="bg-paper border-b border-rule px-4 py-2 flex items-center gap-3">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#D8D2C2]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#D8D2C2]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#D8D2C2]" />
        </div>
        <span className="font-mono text-[11px] text-mute">
          proposal.md
        </span>
      </div>
      <div className="px-8 py-7 prose-doc max-h-[640px] overflow-y-auto">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
}

function VerdictPanel({ verdict }: { verdict: Verdict }) {
  const isApprove = verdict.verdict === "APPROVE";
  const feedback = Array.isArray(verdict.feedback)
    ? verdict.feedback
    : verdict.feedback
    ? [verdict.feedback]
    : [];

  return (
    <div className="border border-rule bg-paper mt-2 p-6">
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-rule">
        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute">
          Structured JSON verdict
        </div>
        <span
          className={`font-mono text-xs px-2.5 py-1 rounded-full ${
            isApprove
              ? "bg-pass/10 text-pass"
              : "bg-fail/10 text-fail"
          }`}
          style={{
            backgroundColor: isApprove
              ? "rgba(31, 122, 76, 0.12)"
              : "rgba(178, 58, 44, 0.12)",
            color: isApprove ? "var(--pass)" : "var(--fail)",
          }}
        >
          ● {verdict.verdict}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        {Object.entries(verdict.rubric_scores).map(([k, v]) => (
          <div
            key={k}
            className="flex items-center justify-between p-2.5 bg-cream border border-rule"
          >
            <span className="text-sm text-ink capitalize">{k}</span>
            <RubricBadge value={v as "PASS" | "FAIL"} />
          </div>
        ))}
      </div>

      {feedback.length > 0 && (
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute mb-3">
            Feedback
          </div>
          <ol className="space-y-2 list-decimal ml-5 text-ash text-[14.5px] leading-relaxed">
            {feedback.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ol>
        </div>
      )}
      {feedback.length === 0 && isApprove && (
        <p className="text-ash text-[14.5px] italic">
          No feedback — passes all six criteria.
        </p>
      )}
    </div>
  );
}

function RubricBadge({ value }: { value: "PASS" | "FAIL" }) {
  const pass = value === "PASS";
  return (
    <span
      className="font-mono text-[10px] uppercase tracking-[0.12em] px-2 py-0.5 rounded-full"
      style={{
        backgroundColor: pass
          ? "rgba(31, 122, 76, 0.15)"
          : "rgba(178, 58, 44, 0.15)",
        color: pass ? "var(--pass)" : "var(--fail)",
      }}
    >
      {value}
    </span>
  );
}

// Help eslint know we use the imported types
export type _Unused = RubricScores;
