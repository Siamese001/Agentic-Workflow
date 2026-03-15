"""HTML Document Loader — stdlib-first HTML text extraction for RAG ingestion."""

from __future__ import annotations

import html
import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

log = logging.getLogger(__name__)


class _TagStripper(HTMLParser):
    """Minimal stdlib HTMLParser that extracts visible text content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._pieces: list[str] = []
        self._skip_depth: int = 0
        self._skip_tags: frozenset[str] = frozenset({"script", "style", "head"})

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._pieces.append(data)

    def get_text(self) -> str:
        return " ".join(self._pieces)


_RE_SCRIPT_STYLE = re.compile("<\\s*(script|style)[^>]*>.*?</\\s*\\1\\s*>", re.DOTALL | re.IGNORECASE)
_RE_TAGS = re.compile("<[^>]+>")
_RE_WHITESPACE = re.compile("\\s+")


def _try_load_text(file_path: Path) -> str | None:
    """
    Attempt HTML text extraction via multiple strategies.

    Returns:
        Extracted visible text on success, or None on any failure.
    """
    try:
        raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("HTML read failed for %s: %s", file_path, exc)
        return None
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text: str = soup.get_text(separator=" ", strip=True)
        return _RE_WHITESPACE.sub(" ", text).strip()
    except ImportError:
        pass
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("bs4 extraction failed, falling back to stdlib: %s", exc)
    try:
        stripper = _TagStripper()
        stripper.feed(raw)
        text = stripper.get_text()
        text = html.unescape(text)
        text = _RE_WHITESPACE.sub(" ", text).strip()
        return text
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("Stdlib HTML extraction failed for %s: %s", file_path, exc)
    try:
        text = _RE_SCRIPT_STYLE.sub("", raw)
        text = _RE_TAGS.sub(" ", text)
        text = html.unescape(text)
        text = _RE_WHITESPACE.sub(" ", text).strip()
        return text
    # guardian: allow-silent-swallow
    except Exception:
        return None


class HTMLDocumentLoader:
    """ImportError-safe HTML loader. Uses BeautifulSoup if available, stdlib otherwise."""

    @staticmethod
    def load_file(file_path: Path) -> str:
        """
        Extract visible text from an HTML file.

        Args:
            file_path: Path to the HTML file.

        Returns:
            Visible text content with tags stripped, or "" on any failure.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HTMLDocumentLoader.load_file")

        text = _try_load_text(file_path)
        return text if text is not None else ""

    @staticmethod
    def load_path(path: Path) -> str:
        """Alias for load_file (API parity with other loaders)."""
        return HTMLDocumentLoader.load_file(path)


__all__ = ["HTMLDocumentLoader"]
