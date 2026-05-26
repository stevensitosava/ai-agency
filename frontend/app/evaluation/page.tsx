import fs from "node:fs";
import path from "node:path";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const metadata = {
  title: "Evaluation · AI Agency",
  description:
    "Agency pipeline vs solo Gemini 2.5 Pro baseline, scored against the same six-point rubric by an independent grader.",
};

function loadReport(): string {
  const p = path.resolve(process.cwd(), "lib", "data", "eval-report.md");
  return fs.readFileSync(p, "utf-8");
}

export default function EvaluationPage() {
  const report = loadReport();

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="font-mono text-xs uppercase tracking-[0.2em] text-accent mb-6">
        ● Evaluation
      </div>
      <h1 className="font-serif text-4xl lg:text-5xl leading-tight tracking-tight text-ink mb-6 max-w-2xl">
        Does the agency actually do anything?
      </h1>
      <p className="text-ash text-lg leading-relaxed max-w-2xl mb-12">
        Rubric-based comparison against solo Gemini 2.5 Pro on the same brief.
        Both outputs scored by an independent grader using the same six-point
        rubric the Critic uses internally. Methodology and per-brief scores
        below.
      </p>

      {/* Key finding card */}
      <div className="border border-rule bg-paper p-6 mb-12">
        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute mb-3">
          Headline finding
        </div>
        <p className="text-ink text-lg leading-relaxed font-serif">
          Rubric scores alone don&rsquo;t capture the gap. Both systems can hit
          6/6 on structural checks, but the agency cites ~5× more distinct
          sources because it actually runs web searches. The baseline&rsquo;s
          citations are plausible-looking but unverified — and sometimes the
          baseline emits zero sources while still passing the citation
          criterion.
        </p>
      </div>

      {/* Rendered report */}
      <div className="prose-doc">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
      </div>

      {/* What's next */}
      <div className="mt-12 p-6 border border-rule bg-cream">
        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-mute mb-3">
          Open questions for Week 6
        </div>
        <ul className="text-ash leading-relaxed text-[15px] space-y-2 list-disc ml-5">
          <li>
            <strong className="text-ink">Source authenticity check.</strong>{" "}
            Add an automated step that loads each cited URL and verifies it
            responds 200 + the claim appears in the page text.
          </li>
          <li>
            <strong className="text-ink">Hallucination tracker.</strong>{" "}
            Extract every numeric claim ($X bn, Y%, Z employees) and ask the
            grader to flag any that aren&rsquo;t in the source pages.
          </li>
          <li>
            <strong className="text-ink">Domain difficulty calibration.</strong>{" "}
            Run all 15 briefs (currently 4 evaluated) and segment results by
            category and difficulty.
          </li>
          <li>
            <strong className="text-ink">Cost normalization.</strong> The agency
            costs more per brief. Quality-per-dollar comparison once Tier 1 is
            promoted and we can run the full sweep.
          </li>
        </ul>
      </div>
    </div>
  );
}
