import Link from "next/link";
import { listRuns } from "../../lib/runs";

export const metadata = {
  title: "Runs · AI Agency",
};

export default function RunsPage() {
  const runs = listRuns();

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-[0.2em] text-accent mb-6">
        ● Sample deliverables
      </div>
      <h1 className="font-serif text-4xl lg:text-5xl leading-tight tracking-tight text-ink mb-6 max-w-2xl">
        Every run, end-to-end.
      </h1>
      <p className="text-ash text-lg leading-relaxed max-w-2xl mb-12">
        Unedited agent output saved directly from pipeline runs. Each entry
        shows the initial draft, the Critic&rsquo;s first verdict, every
        revision, and the final approved proposal.
      </p>

      <div className="divide-y divide-rule border-y border-rule">
        {runs.map((run) => (
          <Link
            key={run.slug}
            href={`/runs/${run.slug}`}
            className="group block py-6 hover:bg-paper -mx-6 px-6 transition-colors"
          >
            <div className="flex items-start justify-between gap-6">
              <div className="min-w-0">
                <div className="font-mono text-[11px] uppercase tracking-[0.14em] text-mute mb-2">
                  {run.niche} · {run.date}
                </div>
                <h2 className="font-serif text-xl lg:text-2xl text-ink leading-tight group-hover:text-accent transition-colors">
                  {run.brief}
                </h2>
                <div className="flex flex-wrap gap-x-5 gap-y-1 mt-3 text-sm text-ash">
                  <span>
                    <span className="text-mute">notes</span> {run.notes}
                  </span>
                  <span>
                    <span className="text-mute">revisions</span> {run.revisions}
                  </span>
                  <span>
                    <span className="text-mute">cost</span>{" "}
                    <span className="text-accent">{run.cost}</span>
                  </span>
                </div>
              </div>
              <div className="shrink-0 flex flex-col items-end gap-2">
                <span className="bg-accent-soft text-accent font-mono text-[10px] uppercase tracking-[0.15em] px-2 py-1 rounded-full">
                  ● {run.status}
                </span>
                <span className="font-mono text-mute text-sm group-hover:text-accent transition-colors">
                  →
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {runs.length === 1 && (
        <p className="text-mute text-sm mt-10 max-w-2xl">
          More runs land here as the agency processes new briefs. Each one
          gets full transparency — initial draft, Critic verdict, revisions,
          and final approved deliverable, all committed to the repo.
        </p>
      )}
    </div>
  );
}
