from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeVar

_T = TypeVar("_T")

LOW_NORMATIVE_COVERAGE = "LOW_NORMATIVE_COVERAGE"

_TIER_RERANK_DISCOUNT: dict[str, float] = {
    "T1_vendor": 1.00,
    "T2_standard": 1.00,
    "T3_guidance": 0.85,
    "T4_repo_canonical": 0.50,
    "T4_implementation_evidence": 0.00,
}


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
        except (TypeError, ValueError):
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
            except (TypeError, ValueError):
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


def filter_normative_sources(
    results: list[_T],
    allowed_collections: tuple[str, ...] = ("ext_authority",),
    allowed_tiers: tuple[str, ...] = (
        "T1_vendor",
        "T2_standard",
        "T3_guidance",
        "T4_repo_canonical",
    ),
) -> tuple[list[_T], list[_T]]:
    """Partition results into (accepted, rejected) based on normative allowlist.

    A chunk is accepted if ALL of the following hold:
      1. metadata["source_collection"] is in ``allowed_collections``
      2. metadata["authority_tier"] is in ``allowed_tiers``
      3. metadata["invalid_for_normative_use"] is explicitly ``False``

    Missing provenance metadata fails closed (chunk is rejected).
    If ``accepted`` is empty the caller MUST NOT fall back to ``rejected``
    chunks for normative use; surface ``LOW_NORMATIVE_COVERAGE`` instead.

    Returns:
        Tuple of (accepted, rejected) lists preserving input order within each.
    """
    accepted: list[_T] = []
    rejected: list[_T] = []
    for r in results:
        meta = getattr(r, "metadata", {}) or {}
        source_col = meta.get("source_collection", "")
        tier = meta.get("authority_tier", "")
        invalid = meta.get("invalid_for_normative_use", True)  # fail-closed: missing = reject
        if source_col in allowed_collections and tier in allowed_tiers and invalid is False:
            accepted.append(r)
        else:
            rejected.append(r)
    return accepted, rejected


def make_citation_anchor_from_chunk(chunk: Any) -> "CitationAnchor":
    """Build a CitationAnchor using chunk metadata as the provenance source.

    Reads ``metadata["source_collection"]`` directly from the chunk rather than
    from the routing-level ``EvidenceBundle.collection``, so per-chunk provenance
    is self-describing and independent of routing correctness.
    """
    meta = getattr(chunk, "metadata", {}) or {}
    return CitationAnchor(
        chunk_id=str(getattr(chunk, "chunk_id", "") or ""),
        collection=str(meta.get("source_collection") or meta.get("source", "unknown")),
        canonical_digest=str(meta.get("canonical_digest", "")),
        file_path=str(meta.get("file_path", "")),
        layer=str(meta.get("layer", "")),
        provenance_confidence=float(meta.get("authority_level", 0.0)),
    )


def apply_authority_rerank(
    results: list[_T],
    authority_bonus: float = 0.15,
    tier_aware: bool = False,
) -> list[_T]:
    """Boost combined_score by authority_level metadata and re-sort.

    Works with any result type that has a ``metadata`` dict and a ``combined_score``
    attribute (e.g. ``HybridSearchResult``).  Results missing ``authority_level``
    receive no bonus (safe fallback — no KeyError).

    Args:
        results: List of search result objects with ``.metadata`` and ``.combined_score``.
        authority_bonus: Maximum score bonus when authority_level == 1.0.  Default 0.15.
        tier_aware: When True, multiplies the bonus by ``_TIER_RERANK_DISCOUNT[authority_tier]``
            so that arch_docs (T4_implementation_evidence) receive zero bonus and lower tiers
            receive proportionally reduced bonuses.  Default False preserves existing behaviour.

    Returns:
        New list sorted by boosted combined_score descending.
    """
    from dataclasses import replace as _replace

    boosted: list[Any] = []
    for r in results:
        meta = getattr(r, "metadata", {}) or {}
        level = meta.get("authority_level")
        if level is not None:
            try:
                bonus = authority_bonus * float(level)
            except (TypeError, ValueError):
                bonus = 0.0
        else:
            bonus = 0.0
        if tier_aware and bonus > 0.0:
            tier = meta.get("authority_tier", "")
            bonus = bonus * _TIER_RERANK_DISCOUNT.get(tier, 0.0)
        if bonus > 0.0:
            try:
                r = _replace(r, combined_score=r.combined_score + bonus)
            except (
                TypeError,
                AttributeError,
            ):  # guardian: allow-silent-swallow -- score replacement: non-fatal, original score kept
                pass
        boosted.append(r)
    boosted.sort(key=lambda x: getattr(x, "combined_score", 0.0), reverse=True)
    return boosted  # type: ignore[return-value]


def doc_family_dedup(results: list[_T], max_per_family: int = 3) -> list[_T]:
    """Keep at most ``max_per_family`` results per doc_family metadata value.

    Preserves order within each family (highest-scored first if results are
    pre-sorted).  Results missing ``doc_family`` are placed in a ``"_unknown"``
    bucket and are *not* deduplicated against each other.

    Args:
        results: List of search result objects with ``.metadata``.
        max_per_family: Maximum chunks to keep per doc_family.  Default 3.

    Returns:
        Filtered list with per-family cap applied.
    """
    family_counts: dict[str, int] = {}
    filtered: list[_T] = []
    for r in results:
        meta = getattr(r, "metadata", {}) or {}
        family = str(meta.get("doc_family") or "_unknown")
        count = family_counts.get(family, 0)
        if family == "_unknown" or count < max_per_family:
            filtered.append(r)
            family_counts[family] = count + 1
    return filtered


def collapse_group_dedup(results: list[_T], max_per_group: int = 2) -> list[_T]:
    """Keep at most ``max_per_group`` results per collapse_group metadata value.

    Preserves insertion order (highest-scored first if results are pre-sorted).
    Results missing ``collapse_group`` are placed in a ``"_ungrouped"`` bucket
    and always pass through — no cap is applied to them.

    This is finer-grained than ``doc_family_dedup``: multiple sources can share
    ``doc_family="reference"`` while belonging to distinct collapse_groups
    (e.g. ``"langgraph"``, ``"autogen"``, ``"openai_agents_raw_github"``), so
    each framework is capped independently.

    Args:
        results: List of search result objects with ``.metadata``.
        max_per_group: Maximum chunks to keep per collapse_group.  Default 2.

    Returns:
        Filtered list with per-group cap applied.
    """
    group_counts: dict[str, int] = {}
    filtered: list[_T] = []
    for r in results:
        meta = getattr(r, "metadata", {}) or {}
        group = str(meta.get("collapse_group") or "_ungrouped")
        count = group_counts.get(group, 0)
        if group == "_ungrouped" or count < max_per_group:
            filtered.append(r)
            group_counts[group] = count + 1
    return filtered
