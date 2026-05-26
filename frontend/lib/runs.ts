// Data layer for "agency runs" — reads from a JSON index + markdown/JSON files
// committed to frontend/lib/data/.
//
// The index lives at lib/data/runs-index.json so scripts (notably the
// promote_brief.py promoter that lifts a Market Research Brief from RUBRIC
// into the dashboard) can append new runs without touching this file.

import fs from "node:fs";
import path from "node:path";
import indexJson from "./data/runs-index.json";

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

export type RunFiles = {
  draftFirst: string;
  verdictFirst: string;
  draftFinal: string;
  verdictFinal: string;
};

export type RunIndexEntry = RunMeta & { files: RunFiles };

export type Run = RunMeta & {
  draftFirst: string;
  verdictFirst: Verdict;
  draftFinal: string;
  verdictFinal: Verdict;
};

const RUN_INDEX: RunIndexEntry[] = (indexJson as { runs: RunIndexEntry[] }).runs;

function deliverablesDir(): string {
  return path.resolve(process.cwd(), "lib", "data");
}

function read(file: string): string {
  return fs.readFileSync(path.join(deliverablesDir(), file), "utf-8");
}

function readJson<T>(file: string): T {
  return JSON.parse(read(file)) as T;
}

export function listRuns(): RunMeta[] {
  // Strip files field for the public list
  return RUN_INDEX.map(({ files: _files, ...meta }) => meta);
}

export function getRun(slug: string): Run | null {
  const entry = RUN_INDEX.find((r) => r.slug === slug);
  if (!entry) return null;
  const { files, ...meta } = entry;
  return {
    ...meta,
    draftFirst: read(files.draftFirst),
    verdictFirst: readJson<Verdict>(files.verdictFirst),
    draftFinal: read(files.draftFinal),
    verdictFinal: readJson<Verdict>(files.verdictFinal),
  };
}
