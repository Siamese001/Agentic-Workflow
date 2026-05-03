"""PDF / text reference-doc ingest adapter (plan §P3.1).

Extracts text from ``.pdf``, ``.txt``, or ``.md`` files and chunks them
via :mod:`apps_shared.chunking` (plan §P3.2). Used by the
``--reference-doc`` CLI flag to calibrate retrieval against a known
exemplar (e.g., the Blend360 SVP Agentic Transformation PDF).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

_log = logging.getLogger("apps_research.pdf_ingest")


@dataclass(frozen=True)
class Chunk:
    """A single chunked excerpt with provenance."""

    chunk_id: str
    file_path: str
    text: str
    chunk_index: int


def _read_pdf_text(path: Path) -> str:
    try:
        import pypdf  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "pypdf not installed. Install via: pip install pypdf"
        ) from exc
    reader = pypdf.PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # guardian: allow-broad-exception -- pypdf page extraction raises heterogeneous; log and skip per page
            _log.warning("[pdf_ingest] page extract failed in %s: %s", path.name, exc)
    return "\n\n".join(pages)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def ingest(path: Path, chunk_tokens: int = 512, overlap_tokens: int = 50) -> list[Chunk]:
    """Read ``path``, extract text, return a list of :class:`Chunk`.

    Args:
        path: the reference-doc path (.pdf / .txt / .md).
        chunk_tokens: target chunk size (default 512 per plan P3.2).
        overlap_tokens: adjacent-chunk overlap (default 50 per plan P3.2).

    Returns:
        List of :class:`Chunk`, empty if the file is unreadable.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if the extension is unsupported.
        RuntimeError: if ``.pdf`` requested and ``pypdf`` is not installed.
    """
    if not path.exists():
        raise FileNotFoundError(f"reference-doc not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        raw = _read_pdf_text(path)
    elif suffix in {".txt", ".md"}:
        raw = _read_text(path)
    else:
        raise ValueError(f"unsupported reference-doc extension: {suffix}")

    from apps_shared.chunking import chunk_text

    pieces = chunk_text(raw, chunk_tokens=chunk_tokens, overlap_tokens=overlap_tokens)
    return [
        Chunk(
            chunk_id=f"{path.name}::c{i:04d}",
            file_path=str(path),
            text=piece,
            chunk_index=i,
        )
        for i, piece in enumerate(pieces)
    ]
