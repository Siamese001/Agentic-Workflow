"""
Phase A: Parent-Child Expander — concrete implementation.

Reconstructs parent section context from child chunk matches using an
in-memory registry of chunk manifests and parent-child links.

C0 RULE: Informational only. Does not authorize execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.retrieval.completeness import GroundedDocument, IParentChildExpander
from agentic_core.evaluation.retrieval.interfaces import Document
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True)
class ChunkEntry:
    """Minimal chunk metadata for parent-child expansion."""

    chunk_id: str
    parent_section_id: str
    sibling_ids: tuple[str, ...]
    content: str
    heading_path: tuple[str, ...]
    source_doc_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "parent_section_id": self.parent_section_id,
            "sibling_ids": list(self.sibling_ids),
            "content": self.content,
            "heading_path": list(self.heading_path),
            "source_doc_id": self.source_doc_id,
        }


@dataclass
class ParentChildRegistry:
    """In-memory registry mapping chunk_id -> ChunkEntry and parent content.

    Populated at index build time from the ChunkManifestRegistry (L4D).
    Read-only at retrieval time.
    """

    _chunks: dict[str, ChunkEntry] = field(default_factory=dict)
    _parent_content: dict[str, str] = field(default_factory=dict)

    def register_chunk(self, entry: ChunkEntry, parent_content: str = "") -> None:
        """Register a chunk entry and its parent section content."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParentChildRegistry.register_chunk")

        self._chunks[entry.chunk_id] = entry
        if entry.parent_section_id and parent_content:
            self._parent_content[entry.parent_section_id] = parent_content

    def get_chunk(self, chunk_id: str) -> ChunkEntry | None:
        return self._chunks.get(chunk_id)

    def get_parent_content(self, parent_section_id: str) -> str:
        return self._parent_content.get(parent_section_id, "")

    def chunk_count(self) -> int:
        return len(self._chunks)

    def parent_count(self) -> int:
        return len(self._parent_content)


class ParentChildExpander(IParentChildExpander):
    """Expands a child chunk to its parent section and neighbor siblings.

    Uses a ParentChildRegistry populated from the ChunkManifestRegistry (L4D).
    Falls back to returning the child document unchanged if no registry entry
    is found — always succeeds, never raises.

    C0 RULE: Read-only, informational expansion only.
    """

    def __init__(self, registry: ParentChildRegistry) -> None:
        self._registry = registry

    def expand(self, child: Document, neighbor_window: int = 1) -> GroundedDocument:
        """Expand child chunk to include parent section and sibling context."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParentChildExpander.expand")

        entry = self._registry.get_chunk(child.doc_id)
        if entry is None:
            return GroundedDocument(
                doc_id=child.doc_id,
                content=child.content,
                score=child.score,
                metadata=dict(child.metadata),
                parent_section_id="",
                parent_content="",
                sibling_ids=[],
                heading_path=[],
                expanded=False,
            )
        parent_content = self._registry.get_parent_content(entry.parent_section_id)
        neighbor_ids = self._resolve_neighbors(entry, neighbor_window)
        return GroundedDocument(
            doc_id=child.doc_id,
            content=child.content,
            score=child.score,
            metadata=dict(child.metadata),
            parent_section_id=entry.parent_section_id,
            parent_content=parent_content,
            sibling_ids=neighbor_ids,
            heading_path=list(entry.heading_path),
            expanded=True,
        )

    def get_parent_section_id(self, chunk_id: str) -> str | None:
        entry = self._registry.get_chunk(chunk_id)
        if entry is None:
            return None
        return entry.parent_section_id or None

    def get_heading_path(self, chunk_id: str) -> list[str]:
        entry = self._registry.get_chunk(chunk_id)
        if entry is None:
            return []
        return list(entry.heading_path)

    def _resolve_neighbors(self, entry: ChunkEntry, window: int) -> list[str]:
        """Return neighbor chunk IDs within the sibling list, bounded by window."""
        siblings = list(entry.sibling_ids)
        if not siblings:
            return []
        try:
            idx = siblings.index(entry.chunk_id)
        except ValueError:
            return siblings[:window]
        lo = max(0, idx - window)
        hi = min(len(siblings), idx + window + 1)
        return [s for s in siblings[lo:hi] if s != entry.chunk_id]


__all__ = ["ChunkEntry", "ParentChildRegistry", "ParentChildExpander"]
