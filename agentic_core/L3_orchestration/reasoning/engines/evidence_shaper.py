"""C0 Evidence Shaping — Phase 2/3/4 post-retrieval pipeline.

Pipeline (runs after dense+sparse fusion):
  1. Dedup by canonical_digest (keep highest combined_score winner)
  2. Preserve exact-match winners from sparse leg
  3. Hydrate full metadata from ChromaDB for winning chunk IDs
  4. Expand parent/child context via chunk_index proximity (file_path + chunk_index ± 1)
  5. Retain contradictory candidates with a flag instead of silently dropping
  6. Emit citation-ready CitationAnchor per result
  7. HeuristicReranker — signal-based rerank (no model)
  8. Return EvidenceBundle — backward-compatible, richer payload

Metadata affordance map (from Phase 1 audit):
  code_chunks      canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✗  name ✓  entity_type ✓
  symbols          canonical_digest ✓  file_path ~  layer ✓  chunk_index ✗  symbol_name ✓  adg_name ✓
  arch_docs        canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✓  doc_type ✓
  tests_guardrails canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✓  doc_type ✓
  runtime_evidence canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✗  evidence_type ✓
  process_docs     canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✓  doc_type ✓
  ext_knowledge    canonical_digest ✓  source_url ✓  layer ✓  chunk_index ✗  document_title ✓
  incidents_rca    canonical_digest ✓  file_path ✓  layer ✓  chunk_index ✓  doc_type ✓
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult

_log = logging.getLogger(__name__)

# Collections that have chunk_index — enables sibling expansion
_CHUNK_INDEX_COLLECTIONS = frozenset({"arch_docs", "tests_guardrails", "process_docs", "incidents_rca"})

# Max siblings to fetch per winning chunk (bounded expansion)
_MAX_SIBLINGS = 1  # fetch at most 1 chunk before + 1 chunk after

# Similarity threshold for near-duplicate detection (digest-based = exact, cosine-based = near)
_NEAR_DUP_DIGEST_KEY = "canonical_digest"

# Exact-match signal patterns (mirrors hybrid_search_engine._detect_query_signal)
_SNAKE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_CAMEL_RE = re.compile(r"\b[A-Z][a-zA-Z0-9]+[A-Z][a-zA-Z0-9]*\b|\b[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*\b")
_PATH_RE = re.compile(r"\b(?:[a-zA-Z_][a-zA-Z0-9_]*\.){2,}[a-zA-Z_][a-zA-Z0-9_]*\b")
_QUOTED_RE = re.compile(r'"[^"]+"|\'[^\']+\'')


# ---------------------------------------------------------------------------
# Output contract types
# ---------------------------------------------------------------------------


@dataclass
class CitationAnchor:
    """Citation-ready provenance anchor for a single retrieved chunk."""

    chunk_id: str
    collection: str
    canonical_digest: str = ""
    file_path: str = ""
    layer: str = ""
    source_url: str = ""  # ext_knowledge only
    entity_name: str = ""  # code_chunks: name; symbols: symbol_name/adg_name
    section: str = ""  # arch_docs/process_docs/incidents_rca: chunk_index + doc_type
    doc_type: str = ""
    provenance_confidence: float = 1.0  # 0.0–1.0 based on metadata completeness

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "collection": self.collection,
            "canonical_digest": self.canonical_digest,
            "file_path": self.file_path or self.source_url,
            "layer": self.layer,
            "entity_name": self.entity_name,
            "section": self.section,
            "doc_type": self.doc_type,
            "provenance_confidence": round(self.provenance_confidence, 3),
        }


@dataclass
class ContradictionFlag:
    """Two results that may contradict each other."""

    id_a: str
    id_b: str
    reason: str
    score_a: float
    score_b: float


@dataclass
class EvidenceBundle:
    """Richer post-shaping retrieval payload (Phase 4 output contract).

    Downstream code that previously consumed list[HybridSearchResult] can still
    access .ranked_chunks for backward compatibility.
    """

    query: str
    collection: str
    ranked_chunks: list[Any]  # list[HybridSearchResult] ordered by rerank
    citation_anchors: dict[str, CitationAnchor]  # chunk_id -> anchor
    contradiction_flags: list[ContradictionFlag]
    exact_match_winners: list[str]  # chunk_ids that won via sparse leg
    expanded_chunk_ids: list[str]  # chunk_ids added by sibling expansion
    shaping_stats: dict[str, Any] = field(default_factory=dict)

    def provenance_summary(self) -> dict[str, Any]:
        """Compact provenance report for the bundle."""
        anchors = list(self.citation_anchors.values())
        complete = sum(1 for a in anchors if a.provenance_confidence >= 0.8)
        return {
            "total_chunks": len(self.ranked_chunks),
            "exact_match_count": len(self.exact_match_winners),
            "expanded_count": len(self.expanded_chunk_ids),
            "contradiction_count": len(self.contradiction_flags),
            "anchors_complete": complete,
            "anchors_total": len(anchors),
            "collections_covered": list({a.collection for a in anchors}),
        }


# ---------------------------------------------------------------------------
# Citation anchor builder
# ---------------------------------------------------------------------------


def _build_anchor(chunk_id: str, collection: str, meta: dict[str, Any]) -> CitationAnchor:
    digest = str(meta.get("canonical_digest", ""))
    file_path = str(meta.get("file_path", ""))
    layer = str(meta.get("layer", ""))
    source_url = str(meta.get("source_url", ""))
    doc_type = str(meta.get("doc_type", "") or meta.get("artifact_type", ""))
    chunk_idx = str(meta.get("chunk_index", ""))

    # entity_name: prefer specific symbol fields, fall back to name/title
    entity_name = (
        meta.get("name")
        or meta.get("symbol_name")
        or meta.get("adg_name")
        or meta.get("document_title")
        or ""
    )
    entity_name = str(entity_name)

    section = f"{doc_type}:{chunk_idx}" if chunk_idx else doc_type

    # provenance_confidence: 1.0 if all key fields present, degrade by 0.15 per missing field
    key_fields = [digest, file_path or source_url, layer]
    missing = sum(1 for f in key_fields if not f)
    confidence = max(0.0, 1.0 - missing * 0.15)

    return CitationAnchor(
        chunk_id=chunk_id,
        collection=collection,
        canonical_digest=digest,
        file_path=file_path,
        layer=layer,
        source_url=source_url,
        entity_name=entity_name,
        section=section,
        doc_type=doc_type,
        provenance_confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def _dedup_by_digest(results: list[Any]) -> list[Any]:
    """Keep one result per canonical_digest (highest combined_score wins).

    Falls back to chunk_id identity if digest is absent.
    """
    seen: dict[str, Any] = {}
    for r in results:
        key = r.metadata.get(_NEAR_DUP_DIGEST_KEY) or r.chunk_id
        existing = seen.get(key)
        if existing is None or r.combined_score > existing.combined_score:
            seen[key] = r
    return list(seen.values())


# ---------------------------------------------------------------------------
# Contradiction detection
# ---------------------------------------------------------------------------


def _detect_contradictions(results: list[Any]) -> list[ContradictionFlag]:
    """Flag pairs that share a file_path but have conflicting layer or doc_type signals.

    Conservative: only flag when both have non-empty layer AND they differ AND
    the combined_score of both is above a minimum threshold (not just noise).
    """
    flags: list[ContradictionFlag] = []
    MIN_SCORE = 0.15
    by_file: dict[str, list[Any]] = {}
    for r in results:
        fp = r.metadata.get("file_path", "")
        if fp:
            by_file.setdefault(fp, []).append(r)

    for fp, group in by_file.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if a.combined_score < MIN_SCORE or b.combined_score < MIN_SCORE:
                    continue
                layer_a = a.metadata.get("layer", "")
                layer_b = b.metadata.get("layer", "")
                if layer_a and layer_b and layer_a != layer_b:
                    flags.append(
                        ContradictionFlag(
                            id_a=a.chunk_id,
                            id_b=b.chunk_id,
                            reason=f"same file_path={fp!r} conflicting layers: {layer_a!r} vs {layer_b!r}",
                            score_a=a.combined_score,
                            score_b=b.combined_score,
                        )
                    )
    return flags


# ---------------------------------------------------------------------------
# Sibling (parent/child) expansion
# ---------------------------------------------------------------------------


def _expand_siblings(
    results: list[Any],
    collection_name: str,
    chroma_client: Any,
    existing_ids: set[str],
) -> list[Any]:
    """Fetch chunk_index ± 1 siblings for results from chunk_index-capable collections.

    Returns only newly fetched chunks not already in results.
    Bounded: at most _MAX_SIBLINGS before + after per winning chunk.
    Graceful: if collection lacks chunk_index, returns empty list.
    """
    if collection_name not in _CHUNK_INDEX_COLLECTIONS:
        return []
    if chroma_client is None:
        return []

    try:
        col = chroma_client.get_collection(collection_name)
    except (ValueError, AttributeError) as e:
        _log.debug("expand_siblings: cannot get collection %s: %s", collection_name, e)
        return []

    new_chunks: list[Any] = []
    seen_new: set[str] = set()

    for r in results:
        idx_str = r.metadata.get("chunk_index")
        fp = r.metadata.get("file_path", "")
        if not idx_str or not fp:
            continue
        try:
            idx = int(idx_str)
        except (ValueError, TypeError):
            continue

        for delta in range(-_MAX_SIBLINGS, _MAX_SIBLINGS + 1):
            if delta == 0:
                continue
            target_idx = idx + delta
            if target_idx < 1:
                continue
            try:
                hits = col.get(
                    where={
                        "$and": [
                            {"file_path": {"$eq": fp}},
                            {"chunk_index": {"$eq": str(target_idx)}},
                        ]
                    },
                    include=["documents", "metadatas"],
                    limit=1,
                )
                for cid, doc, meta in zip(
                    hits.get("ids", []),
                    hits.get("documents", []),
                    hits.get("metadatas", []),
                ):
                    if cid in existing_ids or cid in seen_new:
                        continue
                    seen_new.add(cid)
                    # Import here to avoid circular at module load
                    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
                        HybridSearchResult,
                    )

                    sibling = HybridSearchResult(
                        chunk_id=cid,
                        content=doc or "",
                        metadata=meta or {},
                        source="sibling_expansion",
                        vector_score=r.vector_score * 0.7,  # discounted
                        lexical_score=0.0,
                        combined_score=r.combined_score * 0.6,
                    )
                    new_chunks.append(sibling)
            except (ValueError, AttributeError, KeyError) as e:
                _log.debug("sibling fetch failed idx=%d fp=%s: %s", target_idx, fp, e)

    return new_chunks


# ---------------------------------------------------------------------------
# Heuristic Reranker (Phase 3)
# ---------------------------------------------------------------------------


def _query_has_exact_signal(query: str) -> bool:
    return bool(
        _QUOTED_RE.search(query)
        or _SNAKE_RE.search(query)
        or _CAMEL_RE.search(query)
        or _PATH_RE.search(query)
    )


def _heuristic_score(
    result: Any,
    query: str,
    exact_signal: bool,
    exact_match_ids: set[str],
) -> float:
    """Compute a rerank score using only existing signals — no model.

    Signal breakdown:
      dense_score        — semantic recall quality
      sparse_score       — exact-match quality
      exact_match_bonus  — chunk won via sparse leg
      identifier_bonus   — metadata entity_name matches query token
      provenance_bonus   — metadata completeness
      sibling_penalty    — expanded siblings score lower by default
    """
    vs = result.vector_score
    ls = result.lexical_score
    meta = result.metadata

    # Dynamic weights mirror hybrid_search_engine._compute_weights
    if exact_signal:
        vw, lw = 0.35, 0.65
    else:
        vw, lw = 0.80, 0.20

    base = vw * vs + lw * ls

    # Exact-match winner bonus
    exact_bonus = 0.20 if result.chunk_id in exact_match_ids else 0.0

    # Identifier hit: entity_name or symbol_name substring match
    entity = (meta.get("name") or meta.get("symbol_name") or meta.get("adg_name") or "").lower()
    query_lower = query.lower()
    identifier_bonus = 0.10 if entity and entity in query_lower else 0.0

    # Provenance: canonical_digest present = +0.05
    prov_bonus = 0.05 if meta.get("canonical_digest") else 0.0

    # Sibling penalty — expanded chunks score below direct hits
    sibling_penalty = 0.15 if result.source == "sibling_expansion" else 0.0

    score = base + exact_bonus + identifier_bonus + prov_bonus - sibling_penalty
    return max(0.0, score)


# ---------------------------------------------------------------------------
# EvidenceShaper — main entry point
# ---------------------------------------------------------------------------


class EvidenceShaper:
    """Post-retrieval evidence shaping pipeline (C0 layer).

    Usage:
        shaper = EvidenceShaper()
        bundle = shaper.shape(query, results, collection_name, chroma_client)
    """

    def shape(
        self,
        query: str,
        results: list[Any],
        collection_name: str = "code_chunks",
        chroma_client: Any = None,
    ) -> "EvidenceBundle":
        """Run the full shaping pipeline and return an EvidenceBundle.

        Args:
            query: Original query text
            results: Fused list[HybridSearchResult] from hybrid engine
            collection_name: Collection that was searched
            chroma_client: ChromaDB client for sibling expansion (optional)

        Returns:
            EvidenceBundle with shaped, reranked, annotated results
        """
        stats: dict[str, Any] = {"input_count": len(results)}

        # 1. Dedup by canonical_digest
        deduped = _dedup_by_digest(results)
        stats["after_dedup"] = len(deduped)

        # 2. Identify exact-match winners (from sparse leg)
        exact_ids: set[str] = {r.chunk_id for r in deduped if r.source in ("lexical", "both")}
        stats["exact_match_count"] = len(exact_ids)

        # 3. Contradiction detection (before expansion, on core results)
        contradiction_flags = _detect_contradictions(deduped)
        stats["contradiction_count"] = len(contradiction_flags)

        # 4. Sibling expansion
        existing_ids = {r.chunk_id for r in deduped}
        siblings = _expand_siblings(
            deduped[:10],  # expand only top-10 to stay bounded
            collection_name,
            chroma_client,
            existing_ids,
        )
        expanded_ids = [s.chunk_id for s in siblings]
        stats["expanded_count"] = len(siblings)
        combined = deduped + siblings

        # 5. Heuristic rerank
        exact_signal = _query_has_exact_signal(query)
        scored = sorted(
            combined,
            key=lambda r: _heuristic_score(r, query, exact_signal, exact_ids),
            reverse=True,
        )
        stats["output_count"] = len(scored)

        # 6. Build citation anchors from metadata
        anchors: dict[str, CitationAnchor] = {}
        for r in scored:
            anchors[r.chunk_id] = _build_anchor(r.chunk_id, collection_name, r.metadata)

        _log.debug(
            "EvidenceShaper: col=%s in=%d dedup=%d exact=%d expand=%d out=%d contradictions=%d",
            collection_name,
            stats["input_count"],
            stats["after_dedup"],
            stats["exact_match_count"],
            stats["expanded_count"],
            stats["output_count"],
            stats["contradiction_count"],
        )

        return EvidenceBundle(
            query=query,
            collection=collection_name,
            ranked_chunks=scored,
            citation_anchors=anchors,
            contradiction_flags=contradiction_flags,
            exact_match_winners=list(exact_ids),
            expanded_chunk_ids=expanded_ids,
            shaping_stats=stats,
        )
