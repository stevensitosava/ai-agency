"""Notes writer tool — persist research findings to disk.

Writes markdown files to data/notes/{project_slug}/{topic_slug}.md so the
agent has a durable record and subsequent agents can read its output.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


NOTES_DIR = Path(__file__).resolve().parents[3] / "data" / "notes"


def _slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def save_note(project: str, topic: str, content: str, sources: list[str] | None = None) -> str:
    """Persist a research note to disk. Returns the path written."""
    project_slug = _slugify(project)
    topic_slug = _slugify(topic)
    target_dir = NOTES_DIR / project_slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{topic_slug}.md"

    header = (
        f"# {topic}\n\n"
        f"**Project:** {project}\n"
        f"**Written:** {datetime.now(timezone.utc).isoformat()}\n\n"
    )
    if sources:
        header += "**Sources:**\n" + "\n".join(f"- {s}" for s in sources) + "\n\n---\n\n"
    else:
        header += "---\n\n"

    target.write_text(header + content, encoding="utf-8")
    return str(target)


# Function declaration for Gemini tool-use API
FUNCTION_DECLARATION = {
    "name": "save_note",
    "description": (
        "Save a research note to disk under data/notes/{project}/{topic}.md. "
        "Use this AFTER you've gathered enough information about a sub-topic — "
        "one note per sub-topic, not one giant note for everything."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The sub-topic this note covers (becomes the file name).",
            },
            "content": {
                "type": "string",
                "description": (
                    "Markdown-formatted notes. Use headings, bullet points, "
                    "and inline citations like [1], [2] referring to the sources list."
                ),
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of URLs that back up the claims in this note.",
            },
        },
        "required": ["topic", "content"],
    },
}
