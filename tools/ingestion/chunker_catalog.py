"""Chunker catalog seed for ADR-063.

The catalog gives ingest entry points one source-kind lookup instead of
ad-hoc chunker selection. The implementations here are deterministic,
stdlib-only seeds that establish the registry, markdown lineage, thin Python
symbol recovery, pytest-node extraction, and trace-window grouping contracts.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Chunk:
    """A catalog-produced chunk plus metadata used by manifests/hydration."""

    chunk_id: str
    text: str
    source_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Chunker(Protocol):
    """Protocol implemented by source-specific chunkers."""

    name: str

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        """Return deterministic chunks for the source text."""


def _stable_chunk_id(chunker_name: str, source_path: str, ordinal: int, text: str) -> str:
    digest = hashlib.sha256(
        f"{chunker_name}\n{source_path}\n{ordinal}\n{text}".encode("utf-8")
    ).hexdigest()[:16]
    return f"{chunker_name.split('/')[0]}:{digest}"


def _line_slice(lines: list[str], node: ast.AST) -> str:
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", getattr(node, "lineno", 1))
    return "\n".join(lines[start:end]).rstrip()


def _parent_id(source_path: str, lineage: list[str]) -> str | None:
    if not source_path and not lineage:
        return None
    if not lineage:
        return source_path or None
    slug = "/".join(re.sub(r"[^a-z0-9]+", "-", item.lower()).strip("-") for item in lineage[:2])
    return f"{source_path}#{slug}" if source_path else slug


class PlainTextChunker:
    """Fallback chunker for unknown source kinds."""

    name = "plain_text/v1"

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        stripped = text.strip()
        if not stripped:
            return []
        return [
            Chunk(
                chunk_id=_stable_chunk_id(self.name, source_path, 0, stripped),
                text=stripped,
                source_kind=source_kind,
                metadata={
                    "chunker_name": self.name,
                    "chunk_kind": "primary",
                    "parent_id": source_path or None,
                    "source_path": source_path,
                },
            )
        ]


class MarkdownHeaderChunker:
    """Split markdown on H1-H3/H4 boundaries and stamp header lineage."""

    name = "markdown_header/v1"
    _header_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        lines = text.splitlines()
        chunks: list[Chunk] = []
        lineage: list[str] = []
        section_lines: list[str] = []
        section_start = 1

        def flush(end_line: int) -> None:
            body = "\n".join(section_lines).strip()
            if not body:
                return
            chunk_lineage = list(lineage[:4])
            ordinal = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=_stable_chunk_id(self.name, source_path, ordinal, body),
                    text=body,
                    source_kind=source_kind,
                    metadata={
                        "chunker_name": self.name,
                        "chunk_kind": "primary",
                        "header_lineage": chunk_lineage,
                        "parent_id": _parent_id(source_path, chunk_lineage),
                        "source_path": source_path,
                        "start_line": section_start,
                        "end_line": end_line,
                    },
                )
            )

        for line_no, line in enumerate(lines, start=1):
            match = self._header_re.match(line)
            if match:
                flush(line_no - 1)
                level = min(len(match.group(1)), 4)
                title = match.group(2).strip()
                lineage = lineage[: level - 1] + [title]
                section_lines = [line]
                section_start = line_no
                continue
            section_lines.append(line)

        flush(len(lines))
        return chunks


class AstThinChunker:
    """Python AST chunker that also emits thin chunks for sparse symbols."""

    name = "ast_thin/v1"

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return PlainTextChunker().chunk(text, source_kind=source_kind, source_path=source_path)

        lines = text.splitlines()
        chunks: list[Chunk] = []
        for node in tree.body:
            chunk_text = ""
            chunk_kind = "primary"
            symbol_name = ""
            symbol_type = type(node).__name__

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbol_name = node.name
                chunk_text = _line_slice(lines, node)
                if not node.args.args and not ast.get_docstring(node):
                    chunk_kind = "thin"
            elif isinstance(node, ast.ClassDef):
                symbol_name = node.name
                chunk_text = _line_slice(lines, node)
                has_method = any(isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) for child in node.body)
                if not has_method:
                    chunk_kind = "thin"
            elif isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                caps_names = [name for name in names if name.isupper()]
                if caps_names:
                    symbol_name = ",".join(caps_names)
                    chunk_text = _line_slice(lines, node)
                    chunk_kind = "thin"

            if not chunk_text.strip():
                continue
            ordinal = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=_stable_chunk_id(self.name, source_path, ordinal, chunk_text),
                    text=chunk_text,
                    source_kind=source_kind,
                    metadata={
                        "chunker_name": self.name,
                        "chunk_kind": chunk_kind,
                        "parent_id": source_path or None,
                        "source_path": source_path,
                        "symbol_name": symbol_name,
                        "symbol_type": symbol_type,
                        "start_line": getattr(node, "lineno", None),
                        "end_line": getattr(node, "end_lineno", None),
                    },
                )
            )
        return chunks


class PytestNodeChunker(AstThinChunker):
    """Chunk one pytest collection node per test function/class."""

    name = "pytest_node/v1"

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return PlainTextChunker().chunk(text, source_kind=source_kind, source_path=source_path)

        lines = text.splitlines()
        chunks: list[Chunk] = []
        for node in ast.walk(tree):
            is_test_func = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            is_test_class = isinstance(node, ast.ClassDef) and node.name.startswith("Test")
            if not (is_test_func or is_test_class):
                continue
            body = _line_slice(lines, node)
            ordinal = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=_stable_chunk_id(self.name, source_path, ordinal, body),
                    text=body,
                    source_kind=source_kind,
                    metadata={
                        "chunker_name": self.name,
                        "chunk_kind": "primary",
                        "parent_id": source_path or None,
                        "source_path": source_path,
                        "symbol_name": node.name,
                        "symbol_type": type(node).__name__,
                        "start_line": getattr(node, "lineno", None),
                        "end_line": getattr(node, "end_lineno", None),
                    },
                )
            )
        return chunks


class CausalWindowChunker:
    """Group JSONL trace rows into trace-level causal windows."""

    name = "causal_window/v1"

    def chunk(self, text: str, *, source_kind: str, source_path: str = "") -> list[Chunk]:
        traces: dict[str, list[dict[str, Any]]] = {}
        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{source_path or '<trace-jsonl>'}:{line_no}: invalid JSON") from exc
            trace_id = str(row.get("trace_id") or row.get("traceId") or "unknown")
            traces.setdefault(trace_id, []).append(row)

        chunks: list[Chunk] = []
        for trace_id, rows in sorted(traces.items()):
            body = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
            ordinal = len(chunks)
            agent_classes = sorted({str(row.get("agent_class")) for row in rows if row.get("agent_class")})
            chunks.append(
                Chunk(
                    chunk_id=_stable_chunk_id(self.name, source_path, ordinal, body),
                    text=body,
                    source_kind=source_kind,
                    metadata={
                        "chunker_name": self.name,
                        "chunk_kind": "aggregate",
                        "parent_id": f"{source_path}#{trace_id}" if source_path else trace_id,
                        "source_path": source_path,
                        "trace_id": trace_id,
                        "agent_class": agent_classes[0] if len(agent_classes) == 1 else None,
                        "span_count": len(rows),
                    },
                )
            )
        return chunks


class ChunkerCatalog:
    """Source-kind to chunker registry."""

    def __init__(self, fallback: Chunker | None = None) -> None:
        self._fallback = fallback or PlainTextChunker()
        self._chunkers: dict[str, Chunker] = {}

    def register_chunker(self, source_kind: str, chunker: type[Chunker] | Chunker) -> None:
        if not source_kind:
            raise ValueError("source_kind must be non-empty")
        instance = chunker() if isinstance(chunker, type) else chunker
        self._chunkers[source_kind] = instance

    def resolve(self, source_kind: str) -> Chunker:
        if os.getenv("CHUNKER_CATALOG_DISABLE") == "1":
            return self._fallback
        return self._chunkers.get(source_kind, self._fallback)

    def chunk(self, source_kind: str, text: str, *, source_path: str = "") -> list[Chunk]:
        return self.resolve(source_kind).chunk(text, source_kind=source_kind, source_path=source_path)


DEFAULT_CATALOG = ChunkerCatalog()
DEFAULT_CATALOG.register_chunker("code/python", AstThinChunker)
DEFAULT_CATALOG.register_chunker("docs/markdown", MarkdownHeaderChunker)
DEFAULT_CATALOG.register_chunker("docs/rules-and-plans", MarkdownHeaderChunker)
DEFAULT_CATALOG.register_chunker("tests/python", PytestNodeChunker)
DEFAULT_CATALOG.register_chunker("traces/jsonl", CausalWindowChunker)
DEFAULT_CATALOG.register_chunker("incidents-rca/markdown", MarkdownHeaderChunker)


def resolve(source_kind: str) -> Chunker:
    """Resolve a chunker from the default catalog."""

    return DEFAULT_CATALOG.resolve(source_kind)


def chunk_text(source_kind: str, text: str, *, source_path: str = "") -> list[Chunk]:
    """Chunk text through the default catalog."""

    return DEFAULT_CATALOG.chunk(source_kind, text, source_path=source_path)


__all__ = [
    "AstThinChunker",
    "CausalWindowChunker",
    "Chunk",
    "ChunkerCatalog",
    "DEFAULT_CATALOG",
    "MarkdownHeaderChunker",
    "PlainTextChunker",
    "PytestNodeChunker",
    "chunk_text",
    "resolve",
]
