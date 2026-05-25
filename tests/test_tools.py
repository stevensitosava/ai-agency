"""Unit tests for tools — no API access required."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.tools import notes_writer, web_search


# ---- slugify ----

@pytest.mark.parametrize("text,expected", [
    ("Hello World", "hello-world"),
    ("Trim   Spaces", "trim-spaces"),
    ("Strip-Special! Chars?", "strip-special-chars"),
    ("Already-kebab", "already-kebab"),
    ("  leading and trailing  ", "leading-and-trailing"),
    ("", "untitled"),
    ("###", "untitled"),
])
def test_slugify_basic(text: str, expected: str) -> None:
    assert notes_writer._slugify(text) == expected


def test_slugify_truncates_to_max_len() -> None:
    long = "a" * 200
    assert len(notes_writer._slugify(long, max_len=60)) == 60


def test_slugify_lowercases_unicode_alnum() -> None:
    # Word chars include accented letters; punctuation stripped
    assert notes_writer._slugify("Café in Tilburg!") == "café-in-tilburg"


# ---- save_note ----

def test_save_note_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(notes_writer, "NOTES_DIR", tmp_path)
    path_str = notes_writer.save_note(
        project="Test Project",
        topic="Test Topic",
        content="hello world",
        sources=["https://example.com"],
    )
    path = Path(path_str)
    assert path.exists()
    assert path.parent.name == "test-project"
    assert path.name == "test-topic.md"
    body = path.read_text(encoding="utf-8")
    assert "# Test Topic" in body
    assert "**Project:** Test Project" in body
    assert "- https://example.com" in body
    assert "hello world" in body


def test_save_note_without_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(notes_writer, "NOTES_DIR", tmp_path)
    notes_writer.save_note(project="p", topic="t", content="body")
    # Should still write without sources section
    body = (tmp_path / "p" / "t.md").read_text(encoding="utf-8")
    assert "**Sources:**" not in body
    assert "body" in body


# ---- tool schemas ----

def test_web_search_function_declaration_shape() -> None:
    decl = web_search.FUNCTION_DECLARATION
    assert decl["name"] == "web_search"
    assert "query" in decl["parameters"]["properties"]
    assert decl["parameters"]["required"] == ["query"]


def test_notes_writer_function_declaration_shape() -> None:
    decl = notes_writer.FUNCTION_DECLARATION
    assert decl["name"] == "save_note"
    props = decl["parameters"]["properties"]
    assert "topic" in props
    assert "content" in props
    # project is injected by the orchestrator, not the model — must NOT be required
    assert "project" not in decl["parameters"]["required"]
    assert "topic" in decl["parameters"]["required"]
    assert "content" in decl["parameters"]["required"]
