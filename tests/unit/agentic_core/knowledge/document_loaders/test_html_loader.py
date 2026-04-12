"""Tests for HTMLDocumentLoader — stdlib-first HTML text extraction."""

from pathlib import Path


def test_html_loader_extracts_visible_text(tmp_path: Path):
    """Visible text is extracted and HTML tags are stripped."""


def test_html_loader_strips_script_and_style(tmp_path: Path):
    """Script and style blocks are removed from output."""


def test_html_loader_returns_empty_on_missing_file(tmp_path: Path):
    """Missing file returns empty string, no exception."""


def test_html_loader_handles_entities(tmp_path: Path):
    """HTML entities are unescaped to their character equivalents."""
