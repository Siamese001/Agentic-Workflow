"""C0.2 EVIDENCE FETCH — candidate evidence pool.

Spec: C0 Context Engine.md lines 261-335. Backend-agnostic data structures;
actual fetch lives in adapters (out of scope for base wave).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .verdicts import RetrievalLane, SourceClass


@dataclass(frozen=True)
class RetrievalScores:
    """Per-lane raw + normalized scores for one chunk hit."""

    raw_score: float = 0.0
    normalized_score: float = 0.0  # 0..1
    rank: int = 0  # 1-indexed within its lane

    def __post_init__(self) -> None:
        if not 0.0 <= self.normalized_score <= 1.0:
            raise ValueError("normalized_score must be in [0,1]")
        if self.rank < 0:
            raise ValueError("rank must be >= 0")


@dataclass(frozen=True)
class HydrationManifest:
    """Spec lines 310-318 — per-chunk attached metadata."""

    source_id: str
    file_path: str = ""
    url: str = ""
    doc_id: str = ""
    trace_id: str = ""
    table_id: str = ""
    section: str = ""
    heading: str = ""
    line_range: tuple[int, int] = (0, 0)
    row_key: str = ""
    timestamp: str = ""
    version: str = ""
    commit: str = ""
    snapshot: str = ""
    tenant: str = ""
    region: str = ""
    data_class: str = "internal"
    retrieval_lane: RetrievalLane = RetrievalLane.DENSE
    parent_chunk_id: str = ""
    child_chunk_ids: tuple[str, ...] = ()
    sibling_chunk_ids: tuple[str, ...] = ()
    extras: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("HydrationManifest.source_id required")
        a, b = self.line_range
        if a < 0 or b < 0 or b < a:
            raise ValueError(f"invalid line_range {self.line_range}")


@dataclass(frozen=True)
class CandidateChunk:
    """One unit of candidate evidence — pre-verification."""

    chunk_id: str
    source_class: SourceClass
    text: str
    manifest: HydrationManifest
    scores: RetrievalScores = field(default_factory=RetrievalScores)
    found_by_lanes: tuple[RetrievalLane, ...] = ()

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("CandidateChunk.chunk_id required")
        if self.text == "":
            raise ValueError("CandidateChunk.text must not be empty")
        if not self.found_by_lanes:
            # Lane provenance is mandatory (spec C0.I3).
            raise ValueError(
                f"CandidateChunk {self.chunk_id!r} missing lane provenance "
                f"(C0.I3 — every retrieved item preserves retrieval_lane)",
            )


@dataclass(frozen=True)
class CandidateEvidencePool:
    """Spec lines 320-324 — unverified candidate pool."""

    plan_id: str
    candidates: tuple[CandidateChunk, ...]
    lanes_used: tuple[RetrievalLane, ...] = ()
    fetch_latency_ms: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    fetch_errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("CandidateEvidencePool.plan_id required")
        if self.fetch_latency_ms < 0:
            raise ValueError("fetch_latency_ms must be >= 0")
        # Soft sanity: every candidate's lanes must be in lanes_used (if set).
        if self.lanes_used:
            allowed = set(self.lanes_used)
            for c in self.candidates:
                missing = set(c.found_by_lanes) - allowed
                if missing:
                    raise ValueError(
                        f"candidate {c.chunk_id!r} cites lanes {missing} "
                        f"not in pool.lanes_used={set(self.lanes_used)}",
                    )

    def by_source(self, sc: SourceClass) -> tuple[CandidateChunk, ...]:
        return tuple(c for c in self.candidates if c.source_class == sc)

    def by_lane(self, lane: RetrievalLane) -> tuple[CandidateChunk, ...]:
        return tuple(c for c in self.candidates if lane in c.found_by_lanes)


__all__ = [
    "CandidateChunk",
    "CandidateEvidencePool",
    "HydrationManifest",
    "RetrievalScores",
]
