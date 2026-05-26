// Data layer for "agency runs" — reads sample deliverables from the repo at build time.
//
// In Week 5+ this will be a real database / API call, but for now the agency's
// historical output lives as files committed to docs/sample-deliverables/.

import fs from "node:fs";
import path from "node:path";

export type RubricScores = {
  structure: "PASS" | "FAIL";
  citations: "PASS" | "FAIL";
  specificity: "PASS" | "FAIL";
  synthesis: "PASS" | "FAIL";
  honesty: "PASS" | "FAIL";
  voice: "PASS" | "FAIL";
};

export type Verdict = {
  verdict: "APPROVE" | "REVISE";
  feedback: string | string[];
  rubric_scores: RubricScores;
};

export type RunMeta = {
  slug: string;
  brief: string;
  niche: string;
  date: string;
  cost: string;
  status: "approved" | "revised" | "draft";
  revisions: number;
  notes: number;
};

export type Run = RunMeta & {
  draftFirst: string;
  verdictFirst: Verdict;
  draftFinal: string;
  verdictFinal: Verdict;
};

// Sample-deliverables are bundled into the Next.js app at frontend/lib/data/
// so the build context is self-contained (no relative paths outside frontend/).
// The canonical source is docs/sample-deliverables/ in the repo root.
function deliverablesDir(): string {
  return path.resolve(process.cwd(), "lib", "data");
}

function read(file: string): string {
  return fs.readFileSync(path.join(deliverablesDir(), file), "utf-8");
}

function readJson<T>(file: string): T {
  return JSON.parse(read(file)) as T;
}

// Hand-curated run index. New runs added here when they're committed.
const RUN_INDEX: RunMeta[] = [
  {
    slug: "design-agency-retainer",
    brief:
      "Sales motion redesign for a Tilburg-area design agency shifting from project work to retainer",
    niche: "Design Agency · Operations",
    date: "2026-05-26",
    cost: "$0.02",
    status: "approved",
    revisions: 0,
    notes: 4,
  },
  {
    slug: "brabant-fintech-pricing",
    brief:
      "Pricing strategy for a Dutch B2B fintech entering Brabant manufacturing",
    niche: "B2B Fintech · Manufacturing",
    date: "2026-05-26",
    cost: "$0.03",
    status: "approved",
    revisions: 1,
    notes: 4,
  },
];

export function listRuns(): RunMeta[] {
  return RUN_INDEX;
}

export function getRun(slug: string): Run | null {
  const meta = RUN_INDEX.find((r) => r.slug === slug);
  if (!meta) return null;

  // File mapping — matches the actual files committed to docs/sample-deliverables/
  const fileMap: Record<string, { d1: string; v1: string; df: string; vf: string }> = {
    "brabant-fintech-pricing": {
      d1: "pricing-strategy-brabant-fintech.md",
      v1: "pricing-strategy-brabant-fintech-critic-verdict.json",
      df: "pricing-strategy-brabant-fintech-FINAL.md",
      vf: "pricing-strategy-brabant-fintech-critic-verdict-FINAL.json",
    },
    "design-agency-retainer": {
      // First-draft approved — no revision needed, so draft1 == final
      d1: "design-agency-retainer-FINAL.md",
      v1: "design-agency-retainer-critic-verdict-FINAL.json",
      df: "design-agency-retainer-FINAL.md",
      vf: "design-agency-retainer-critic-verdict-FINAL.json",
    },
  };
  const files = fileMap[slug];
  if (!files) return null;

  return {
    ...meta,
    draftFirst: read(files.d1),
    verdictFirst: readJson<Verdict>(files.v1),
    draftFinal: read(files.df),
    verdictFinal: readJson<Verdict>(files.vf),
  };
}
