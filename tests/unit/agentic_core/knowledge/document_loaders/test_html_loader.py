"""Tests for HTMLDocumentLoader — stdlib-first HTML text extraction."""

from pathlib import Path

from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def test_html_loader_extracts_visible_text(tmp_path: Path):
    """Visible text is extracted and HTML tags are stripped."""
    html_file = tmp_path / "sample.html"
    html_file.write_text(
        "<html><head><title>T</title></head><body><h1>Hello</h1><p>World</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "Hello" in result
    assert "World" in result
    assert "<" not in result


def test_html_loader_strips_script_and_style(tmp_path: Path):
    """Script and style blocks are removed from output."""
    html_file = tmp_path / "scripted.html"
    html_file.write_text(
        "<html><body><script>var x = 1;</script><style>.a{color:red}</style><p>Visible</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "Visible" in result
    assert "var x" not in result
    assert "color:red" not in result


def test_html_loader_returns_empty_on_missing_file(tmp_path: Path):
    """Missing file returns empty string, no exception."""
    result = HTMLDocumentLoader.load_file(tmp_path / "nonexistent.html")
    assert result == ""


def test_html_loader_handles_entities(tmp_path: Path):
    """HTML entities are unescaped to their character equivalents."""
    html_file = tmp_path / "entities.html"
    html_file.write_text(
        "<html><body><p>&amp; hello &quot;world&quot;</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "& hello" in result
    assert '"world"' in result
    assert "&amp;" not in result
    assert "&quot;" not in result
