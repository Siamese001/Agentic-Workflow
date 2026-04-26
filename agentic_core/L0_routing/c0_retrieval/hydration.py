"""C0.2A SOURCE HYDRATION / SPAN NORMALIZATION.

Spec: C0 Context Engine.md lines 338-373. Quality flags + chunk-boundary
risk classifier. Pure-data, no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .candidate_pool import CandidateChunk, CandidateEvidencePool


class ChunkBoundaryRisk(str, Enum):
    """Spec line 367 — chunk_boundary_risk: low/medium/high."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class QualityFlags:
    """Spec lines 361-367 — quality flags per hydrated chunk."""

    span_resolves: bool
    source_version_current: bool
    acl_clear: bool
    parent_context_available: bool
    citation_anchor_stable: bool
    chunk_boundary_risk: ChunkBoundaryRisk = ChunkBoundaryRisk.LOW

    def all_green(self) -> bool:
        """True iff every flag is in its safe state."""
        return (
            self.span_resolves
            and self.source_version_current
            and self.acl_clear
            and self.parent_context_available
            and self.citation_anchor_stable
            and self.chunk_boundary_risk == ChunkBoundaryRisk.LOW
        )


@dataclass(frozen=True)
class HydratedChunk:
    """A CandidateChunk + computed quality flags + canonicalized identity."""

    candidate: CandidateChunk
    canonical_source_path: str
    section_hierarchy: tuple[str, ...]
    chunk_version: str
    citation_anchor_candidates: tuple[str, ...]
    quality: QualityFlags

    def __post_init__(self) -> None:
        if not self.canonical_source_path.strip():
            raise ValueError("canonical_source_path required")
        if not self.chunk_version.strip():
            raise ValueError("chunk_version required")


@dataclass(frozen=True)
class HydratedEvidencePool:
    """Spec line 370 — output of C0.2A."""

    plan_id: str
    hydrated: tuple[HydratedChunk, ...]
    hydration_failures: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("HydratedEvidencePool.plan_id required")

    def all_green_chunks(self) -> tuple[HydratedChunk, ...]:
        return tuple(h for h in self.hydrated if h.quality.all_green())


def _classify_boundary_risk(text: str) -> ChunkBoundaryRisk:
    """Heuristic — does the text look like it ends mid-thought?"""
    if not text:
        return ChunkBoundaryRisk.HIGH
    last = text.rstrip()[-1:] if text.rstrip() else ""
    if last in (".", "!", "?", ";", ":", ")", "]", "}", '"', "'"):
        return ChunkBoundaryRisk.LOW
    if last in (",", "-"):
        return ChunkBoundaryRisk.MEDIUM
    return ChunkBoundaryRisk.HIGH


def _derive_quality(c: CandidateChunk, *, tenant: str) -> QualityFlags:
    m = c.manifest
    return QualityFlags(
        span_resolves=m.line_range != (0, 0) or m.section != "" or m.row_key != "",
        source_version_current=m.version != "" or m.commit != "" or m.snapshot != "",
        acl_clear=(m.tenant == tenant or not tenant) and m.data_class != "blocked",
        parent_context_available=bool(m.parent_chunk_id) or bool(m.section),
        citation_anchor_stable=bool(m.line_range != (0, 0) or m.section or m.row_key),
        chunk_boundary_risk=_classify_boundary_risk(c.text),
    )


def normalize_pool(
    pool: CandidateEvidencePool,
    *,
    tenant: str,
) -> HydratedEvidencePool:
    """Run hydration + quality classification across the pool.

    Failed hydrations (e.g., empty source path) become entries in
    `hydration_failures` rather than being silently dropped.
    """
    hydrated: list[HydratedChunk] = []
    failures: list[str] = []
    for c in pool.candidates:
        m = c.manifest
        canonical = m.file_path or m.url or m.doc_id or m.table_id or m.trace_id
        if not canonical:
            failures.append(
                f"chunk {c.chunk_id!r}: cannot compute canonical_source_path",
            )
            continue
        section_hier = tuple(s for s in (m.section, m.heading) if s)
        version = m.version or m.commit or m.snapshot or "unknown"
        anchor_candidates: list[str] = []
        if m.line_range != (0, 0):
            anchor_candidates.append(f"line:{m.line_range[0]}-{m.line_range[1]}")
        if m.section:
            anchor_candidates.append(f"section:{m.section}")
        if m.row_key:
            anchor_candidates.append(f"row:{m.row_key}")
        if m.timestamp:
            anchor_candidates.append(f"ts:{m.timestamp}")
        try:
            hydrated.append(
                HydratedChunk(
                    candidate=c,
                    canonical_source_path=canonical,
                    section_hierarchy=section_hier,
                    chunk_version=version,
                    citation_anchor_candidates=tuple(anchor_candidates),
                    quality=_derive_quality(c, tenant=tenant),
                )
            )
        except ValueError as exc:
            failures.append(f"chunk {c.chunk_id!r}: {exc}")
    return HydratedEvidencePool(
        plan_id=pool.plan_id,
        hydrated=tuple(hydrated),
        hydration_failures=tuple(failures),
    )


__all__ = [
    "ChunkBoundaryRisk",
    "HydratedChunk",
    "HydratedEvidencePool",
    "QualityFlags",
    "normalize_pool",
]
