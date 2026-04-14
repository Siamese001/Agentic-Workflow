from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CitationAnchor:
    chunk_id: str
    collection: str
    canonical_digest: str
    file_path: str
    layer: str
    provenance_confidence: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "chunk_id", str(self.chunk_id or ""))
        object.__setattr__(self, "collection", str(self.collection or ""))
        object.__setattr__(self, "canonical_digest", str(self.canonical_digest or ""))
        object.__setattr__(self, "file_path", str(self.file_path or ""))
        object.__setattr__(self, "layer", str(self.layer or ""))
        try:
            confidence = float(self.provenance_confidence)
        except Exception:
            confidence = 0.0
        object.__setattr__(self, "provenance_confidence", max(0.0, min(1.0, confidence)))


@dataclass(frozen=True)
class ContradictionFlag:
    id_a: str
    id_b: str
    reason: str
    score_a: float
    score_b: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "id_a", str(self.id_a or ""))
        object.__setattr__(self, "id_b", str(self.id_b or ""))
        object.__setattr__(self, "reason", str(self.reason or ""))
        for attr in ("score_a", "score_b"):
            try:
                value = float(getattr(self, attr))
            except Exception:
                value = 0.0
            object.__setattr__(self, attr, value)


@dataclass
class EvidenceBundle:
    query: str
    collection: str
    ranked_chunks: list[Any]
    citation_anchors: dict[str, CitationAnchor]
    contradiction_flags: list[ContradictionFlag]
    exact_match_winners: list[str]
    expanded_chunk_ids: list[str]
    shaping_stats: dict[str, Any] = field(default_factory=dict)
    retrieval_coverage: Any | None = None

    def __post_init__(self) -> None:
        self.query = str(self.query or "")
        self.collection = str(self.collection or "")
        self.ranked_chunks = list(self.ranked_chunks or [])
        self.citation_anchors = dict(self.citation_anchors or {})
        self.contradiction_flags = list(self.contradiction_flags or [])
        self.exact_match_winners = [
            str(item) for item in (self.exact_match_winners or []) if item is not None
        ]
        self.expanded_chunk_ids = [str(item) for item in (self.expanded_chunk_ids or []) if item is not None]
        self.shaping_stats = dict(self.shaping_stats or {})

    @property
    def ranked_chunk_ids(self) -> list[str]:
        ids: list[str] = []
        for chunk in self.ranked_chunks:
            chunk_id = getattr(chunk, "chunk_id", None)
            if chunk_id is not None:
                ids.append(str(chunk_id))
        return ids

    def dedup_ratio(self) -> float:
        input_count = max(1, int(self.shaping_stats.get("input_count", len(self.ranked_chunks)) or 1))
        after_dedup = int(self.shaping_stats.get("after_dedup", len(self.ranked_chunks)) or 0)
        return max(0.0, min(1.0, 1.0 - (after_dedup / input_count)))
