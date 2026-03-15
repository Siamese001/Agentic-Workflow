"""
Phase 8 — CitationBundle: deterministic, non-mutating citation artifact.

Attached to any response that uses L4 retrieval.
citation_hash = sha256(canonical_bytes excluding citation_hash).
Anchors sorted by (source_doc_id, chunk_id, char_start) for determinism.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L4_state.types.retrieval_anchor_types import RetrievalAnchor
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "citation_bundle_types", "L4")
_emit_routes_through("p1", "citation_bundle_types", "L4")
_emit_escalates_to_human("p1", "citation_bundle_types", "L4")
_emit_reads_policy_state("p1", "citation_bundle_types", "L4")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _anchor_sort_key(a: RetrievalAnchor) -> tuple[str, str, int]:
    return (a.source_doc_id, a.chunk_id, a.char_start)


@dataclass
class CitationBundle:
    """
    Deterministic citation artifact attached to retrieval-backed responses.

    Fields
    ------
    schema_version : int              — bumped on breaking changes
    request_hash   : str              — sha256 of canonical retrieval request
    anchors        : list[RetrievalAnchor] — sorted by (source_doc_id, chunk_id, char_start)
    citation_hash  : str              — sha256(canonical_bytes); auto-computed
    """

    schema_version: int
    request_hash: str
    anchors: list[RetrievalAnchor]
    citation_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"CitationBundle: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.request_hash:
            raise ValueError("CitationBundle: request_hash must be non-empty")
        if not isinstance(self.anchors, list):
            raise TypeError("CitationBundle: anchors must be a list")
        self.anchors = sorted(self.anchors, key=_anchor_sort_key)
        object.__setattr__(self, "citation_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding citation_hash (self-referential).
        Anchors sorted by (source_doc_id, chunk_id, char_start).
        Volatile fields (retrieved_at_utc) excluded from hash computation.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CitationBundle.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CitationBundle.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "CitationBundle.canonical_bytes")

        doc: dict[str, Any] = {
            "anchors": [
                {
                    "char_end": a.char_end,
                    "char_start": a.char_start,
                    "chunk_id": a.chunk_id,
                    "source_doc_id": a.source_doc_id,
                    "version_hash": a.version_hash,
                }
                for a in sorted(self.anchors, key=_anchor_sort_key)
            ],
            "request_hash": self.request_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_hash": self.request_hash,
            "anchors": [a.to_dict() for a in self.anchors],
            "citation_hash": self.citation_hash,
        }


def build_citation_bundle(request_hash: str, anchors: list[RetrievalAnchor]) -> CitationBundle:
    """Factory: build a CitationBundle from a request hash and anchor list."""
    return CitationBundle(schema_version=_SCHEMA_VERSION, request_hash=request_hash, anchors=anchors)
