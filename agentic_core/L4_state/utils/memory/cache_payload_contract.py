"""G10 SemanticCachePayload contract — structured emit for R1B.5.

R1B §R1B.5 specifies the semantic-cache payload must carry: prior answer,
cache confidence, dense / BM25 / fused scores, reason codes, hit id,
telemetry, support-manifest flag, freshness class, policy hash. This
module provides the dataclass that enforces the shape.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


_VALID_REASON_CODES: frozenset[str] = frozenset(
    {
        "exact_hit",
        "hybrid_hit",
        "hybrid_reject",
        "support_manifest_reject",
        "scope_mismatch",
        "live_signal_bypass",
        "flow_class_bypass",
        "neighborhood_evicted",
        "ttl_expired",
        "tier_mismatch",
    },
)


@dataclass(frozen=True)
class SemanticCachePayload:
    """Structured R1B cache emit payload."""

    prior_answer: Any
    dense_score: float
    sparse_score: float
    fused_score: float
    hit_id: str
    cache_id: str
    cache_lineage: str  # "L1" | "L2" | "L2_to_L1_writeback"
    cache_tier: str  # "static" | "dynamic"
    reason_codes: tuple[str, ...]
    policy_hash: str
    embedding_model_id: str
    namespace: str
    tenant_id: str
    written_at: float
    ttl_seconds: int
    freshness_class: str  # "hot" | "warm" | "cold"

    evidence_ids: tuple[str, ...] = ()
    grounding_complete: bool = False
    support_manifest_ref: str = ""

    hybrid_threshold: float = 0.0
    similarity_threshold: float = 0.95

    emit_timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        for code in self.reason_codes:
            if code not in _VALID_REASON_CODES:
                raise ValueError(
                    f"SemanticCachePayload: unknown reason_code {code!r}; "
                    f"valid set = {sorted(_VALID_REASON_CODES)}",
                )
        if self.cache_tier not in {"static", "dynamic"}:
            raise ValueError(
                f"SemanticCachePayload: cache_tier must be 'static' or 'dynamic', got {self.cache_tier!r}",
            )
        if self.freshness_class not in {"hot", "warm", "cold"}:
            raise ValueError(
                f"SemanticCachePayload: freshness_class must be "
                f"'hot'|'warm'|'cold', got {self.freshness_class!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict (tuples → lists)."""
        d = asdict(self)
        d["reason_codes"] = list(self.reason_codes)
        d["evidence_ids"] = list(self.evidence_ids)
        return d


def new_hit_id() -> str:
    """Mint a fresh hit_id for a cache emit. Short, opaque, URL-safe."""
    return uuid.uuid4().hex[:16]


def compute_cache_id(context: str, namespace: str) -> str:
    """Stable cache id for lineage tracking. SHA256 short-form of (ctx, ns)."""
    return hashlib.sha256(f"{namespace}\x00{context}".encode()).hexdigest()[:32]


def freshness_class_for_age(age_seconds: float) -> str:
    """Classify entry age into hot/warm/cold tiers."""
    if age_seconds < 3600:
        return "hot"
    if age_seconds < 86400:
        return "warm"
    return "cold"


__all__ = [
    "SemanticCachePayload",
    "compute_cache_id",
    "freshness_class_for_age",
    "new_hit_id",
]
