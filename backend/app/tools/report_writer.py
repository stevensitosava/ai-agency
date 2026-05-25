"""Report writer — load notes from disk, save deliverables.

Pure I/O — no LLM calls. Used by the Copywriter (saves drafts) and the
pipeline orchestrator (saves the final approved deliverable).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


DELIVERABLES_DIR = Path(__file__).resolve().parents[3] / "data" / "deliverables"
NOTES_DIR = Path(__file__).resolve().parents[3] / "data" / "notes"


def _slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def load_notes(project: str) -> str:
    """Concatenate all markdown notes for a project into one string."""
    slug = _slugify(project)
    note_dir = NOTES_DIR / slug
    if not note_dir.exists():
        return ""
    parts: list[str] = []
    for path in sorted(note_dir.glob("*.md")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def save_deliverable(
    project: str,
    content: str,
    *,
    suffix: str = "",
    extension: str = "md",
) -> str:
    """Persist a deliverable to disk under data/deliverables/{project_slug}/.

    `suffix` is appended to the filename — useful for draft-1, draft-2, final.
    Returns the path written.
    """
    slug = _slugify(project)
    target_dir = DELIVERABLES_DIR / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name_parts = ["report", stamp]
    if suffix:
        name_parts.append(_slugify(suffix))
    name = "-".join(name_parts) + f".{extension}"
    target = target_dir / name
    target.write_text(content, encoding="utf-8")
    return str(target)
