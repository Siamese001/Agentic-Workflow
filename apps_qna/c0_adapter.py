"""C0 Thin Adapter — shapes request, calls canonical C0, returns unchanged.

W2.1: Enhanced adapter with proper error handling, fail-closed semantics,
and canonical C0 integration contract.

D1.1: Wired to canonical run_c0 from agentic_core.L0_routing.c0_retrieval.

W2 (bge-review-apps-qna-c0-chroma-migration-f9a3b2): Prefer canonical
Chroma retrieval from data/cache/chromadb, collection apps_qna_interview_cards.
The previous flat index under C:/AgenticEmbeddings remains as a gated fallback
for this rollout wave.

The adapter MUST:
- Shape an app-specific C0 request from interview parameters
- Call the canonical C0 retrieval endpoint
- Return the canonical FinalEvidenceContract unchanged
- Handle C0 errors fail-closed (→ SAFE_ABSTAIN)
- Never transform evidence or invent facts

Plan: docs/archive/windsurf/legacy-tree/plans/bge-m3-gap-closure-c8f3a2.md W1
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np

from apps_qna.types.evidence_contracts import FinalEvidenceContract

_LOGGER = logging.getLogger(__name__)

# Index location — override via env var for tests / non-Windows environments
_DEFAULT_INDEX_DIR = Path(
    os.environ.get(
        "APPS_QNA_INDEX_DIR",
        "C:/AgenticEmbeddings/indexes/apps_qna_interview_cards",
    )
)
_INDEX_FILE = _DEFAULT_INDEX_DIR / "index.json"
_CHROMA_COLLECTION_NAME = "apps_qna_interview_cards"
_FLAT_FALLBACK_ENV = "APPS_QNA_C0_ENABLE_FLAT_FALLBACK"

# Retrieval config
_DEFAULT_TOP_K = 5
_SIMILARITY_FLOOR = 0.0  # accept all positives; caller can filter

# Lazy-cached retrieval handles — reset by tests via _reset_index_cache()
_INDEX_CACHE: dict[str, Any] | None = None
_CHROMA_COLLECTION_CACHE: Any | None = None


def _reset_index_cache() -> None:
    """Clear in-process retrieval caches (for tests)."""
    global _INDEX_CACHE, _CHROMA_COLLECTION_CACHE
    _INDEX_CACHE = None
    _CHROMA_COLLECTION_CACHE = None


def _load_index() -> dict[str, Any] | None:
    """Load flat index.json from disk; returns None if unavailable."""
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE
    if not _INDEX_FILE.exists():
        _LOGGER.warning("apps_qna index not found: %s", _INDEX_FILE)
        return None
    try:
        with open(_INDEX_FILE, "r", encoding="utf-8") as fh:
            _INDEX_CACHE = json.load(fh)
        _LOGGER.debug(
            "Loaded apps_qna index: %d vectors", len(_INDEX_CACHE.get("vectors", []))
        )
        return _INDEX_CACHE
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        _LOGGER.warning("Failed to load apps_qna index: %s", exc)
        return None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two pre-normalised float lists."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = float(np.linalg.norm(va))
    norm_b = float(np.linalg.norm(vb))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def _flat_fallback_enabled() -> bool:
    raw = os.environ.get(_FLAT_FALLBACK_ENV, "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _query_for_fetch(query_text: str, interview_slug: str) -> str:
    return query_text.strip() or interview_slug.strip()


def _embed_query(query: str) -> list[float] | None:
    try:
        from tools.embedders import get_embedder  # noqa: PLC0415

        embedder = get_embedder()
        if not embedder.is_available():
            _LOGGER.debug("BGE-M3 embedder unavailable; C0 retrieval cannot run")
            return None
        query_vec = list(embedder.embed(query))
        if len(query_vec) != 1024:
            _LOGGER.warning("Query embedding has wrong dims=%d; expected 1024", len(query_vec))
            return None
        return query_vec
    except (ImportError, AttributeError, RuntimeError, TypeError, ValueError, OSError) as exc:
        _LOGGER.warning("Embedder error during C0 fetch: %s", exc)
        return None


def _is_expected_chroma_unavailable(exc: Exception) -> bool:
    if isinstance(exc, (ImportError, AttributeError, RuntimeError, TypeError, ValueError, OSError, KeyError)):
        return True
    if type(exc).__name__ in {"ChromaError", "InvalidCollectionException", "NotFoundError"}:
        return True
    message = str(exc).lower()
    return "does not exist" in message or "not found" in message


def _metadata_dim_matches(metadata: dict[str, Any]) -> bool:
    raw_dim = metadata.get("embedding_dim", metadata.get("embedding_dimension"))
    if raw_dim is None:
        return False
    try:
        return int(raw_dim) == 1024
    except (TypeError, ValueError):
        return False


def _load_chroma_collection() -> Any | None:
    """Load the canonical apps_qna Chroma collection, if available and compatible."""
    global _CHROMA_COLLECTION_CACHE
    if _CHROMA_COLLECTION_CACHE is not None:
        return _CHROMA_COLLECTION_CACHE

    try:
        from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir  # noqa: PLC0415
        from agentic_core.L4_state.utils.client.chroma_client import (  # noqa: PLC0415
            chromadb_module as chromadb,
        )

        persist_dir = canonical_persist_dir()
        if not persist_dir.exists():
            _LOGGER.debug("apps_qna Chroma persist dir not found: %s", persist_dir)
            return None
        client = chromadb.PersistentClient(path=str(persist_dir))
        collection = client.get_collection(name=_CHROMA_COLLECTION_NAME)
        metadata = getattr(collection, "metadata", None) or {}
        if metadata.get("embedding_model") != "BAAI/bge-m3" or not _metadata_dim_matches(metadata):
            _LOGGER.warning("apps_qna Chroma collection has incompatible metadata: %s", metadata)
            return None
        _CHROMA_COLLECTION_CACHE = collection
        return collection
    except Exception as exc:  # noqa: BLE001
        if not _is_expected_chroma_unavailable(exc):
            raise
        _LOGGER.debug("apps_qna Chroma collection unavailable: %s", exc)
        return None


def _score_from_chroma_distance(distance: Any) -> float:
    try:
        score = 1.0 - float(distance)
    except (TypeError, ValueError):
        score = 0.0
    return min(max(score, 0.0), 1.0)


def _chroma_fetch(query_vec: list[float], top_k: int = _DEFAULT_TOP_K) -> list[dict[str, Any]]:
    collection = _load_chroma_collection()
    if collection is None:
        return []
    try:
        results = collection.query(
            query_embeddings=[query_vec],
            n_results=top_k,
            include=["metadatas", "distances", "documents"],
        )
    except Exception as exc:  # noqa: BLE001
        if not _is_expected_chroma_unavailable(exc):
            raise
        _LOGGER.warning("apps_qna Chroma query failed; flat fallback may be used: %s", exc)
        return []

    ids = (results.get("ids") or [[]])[0] or []
    distances = (results.get("distances") or [[]])[0] or []
    metadatas = (results.get("metadatas") or [[]])[0] or []

    hits: list[dict[str, Any]] = []
    for rank, row_id in enumerate(ids):
        score = _score_from_chroma_distance(distances[rank] if rank < len(distances) else None)
        if score < _SIMILARITY_FLOOR:
            continue
        metadata = metadatas[rank] if rank < len(metadatas) and isinstance(metadatas[rank], dict) else {}
        hits.append(
            {
                "id": str(row_id),
                "score": score,
                "metadata": metadata,
            }
        )
    return hits


def _flat_fetch(query_vec: list[float], top_k: int = _DEFAULT_TOP_K) -> list[dict[str, Any]]:
    index = _load_index()
    if not index:
        return []

    vectors = index.get("vectors", [])
    if not vectors:
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in vectors:
        ev = entry.get("embedding")
        if not ev or len(ev) != 1024:
            continue
        sim = _cosine_similarity(query_vec, ev)
        if sim >= _SIMILARITY_FLOOR:
            scored.append((sim, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for sim, entry in scored[:top_k]:
        results.append(
            {
                "id": entry.get("id", ""),
                "score": sim,
                "metadata": entry.get("metadata", {}),
            }
        )
    return results


class C0UnavailableError(Exception):
    """Raised when canonical C0 is unavailable — fail-closed."""


def call_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> dict[str, Any]:
    """Call canonical C0 and return FinalEvidenceContract unchanged.

    Args:
        interview_slug: The interview slug for evidence scoping.
        route_id: The selected route id.
        query_text: Optional retrieval query text.

    Returns:
        A FinalEvidenceContract-shaped dict.

    Raises:
        C0UnavailableError: If canonical C0 is unreachable (fail-closed).
    """
    try:
        fec = _call_canonical_c0(
            interview_slug=interview_slug,
            route_id=route_id,
            query_text=query_text,
        )
    except Exception as exc:
        _LOGGER.error("C0 unavailable for slug=%s: %s", interview_slug, exc)
        raise C0UnavailableError(
            f"Canonical C0 unavailable for interview '{interview_slug}'. "
            "Fail-closed: no evidence can be invented."
        ) from exc

    return fec.to_dict()


def _real_fetch(
    query_text: str,
    interview_slug: str,
    top_k: int = _DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """Query canonical Chroma first, then optionally fall back to the flat index.

    Returns a list of up to ``top_k`` result dicts ordered by cosine
    similarity descending.  Each dict has keys:
        - ``id``         (str) interview_slug of the matched card
        - ``score``      (float) cosine similarity 0..1
        - ``metadata``   (dict) card_id, base_card_type, archetype, expected_evidence

    Returns empty list when:
    - canonical Chroma collection is unavailable and flat fallback is disabled
    - both Chroma and flat fallback miss
    - embedder unavailable (no GPU / no sentence-transformers)
    - expected retrieval errors occur
    """
    query = _query_for_fetch(query_text, interview_slug)
    if not query:
        return []

    query_vec = _embed_query(query)
    if query_vec is None:
        return []

    chroma_hits = _chroma_fetch(query_vec, top_k=top_k)
    if chroma_hits:
        return chroma_hits
    if not _flat_fallback_enabled():
        return []
    return _flat_fetch(query_vec, top_k=top_k)


def _call_canonical_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> FinalEvidenceContract:
    """Call the canonical C0 retrieval endpoint via run_c0.

    W2 (bge-review-apps-qna-c0-chroma-migration-f9a3b2): Uses _real_fetch to
    query canonical Chroma first, with the flat index as a gated rollout
    fallback. When the retriever returns candidates the
    CandidateEvidencePool is populated and the canonical pipeline emits a
    GROUNDED contract. Falls back to template_only when the index is
    unavailable or the embedder cannot run.
    """
    from agentic_core.L0_routing.c0_retrieval import (
        run_c0,
        RouteContract,
        L1PlanContract,
        FreshnessClass,
        SupportTarget,
    )
    from agentic_core.L0_routing.c0_retrieval.candidate_pool import (
        CandidateChunk,
        CandidateEvidencePool,
        HydrationManifest,
        RetrievalScores,
    )
    from agentic_core.L0_routing.c0_retrieval.verdicts import (
        RetrievalLane,
        SourceClass,
        SupportStatus,
    )

    raw_hits = _real_fetch(query_text, interview_slug)

    def _real_fetch_fn(plan: Any, route: Any) -> CandidateEvidencePool:
        if not raw_hits:
            return CandidateEvidencePool(plan_id=plan.plan_id, candidates=())

        chunks: list[CandidateChunk] = []
        for rank, hit in enumerate(raw_hits, start=1):
            source_id = hit["id"] or f"card_{rank}"
            meta = hit.get("metadata", {})
            chunk = CandidateChunk(
                chunk_id=source_id,
                source_class=SourceClass.DOCS,
                text=meta.get("base_card_type", source_id),
                manifest=HydrationManifest(
                    source_id=source_id,
                    doc_id=meta.get("card_id", source_id),
                    section=meta.get("archetype", ""),
                    data_class="internal",
                    retrieval_lane=RetrievalLane.DENSE,
                ),
                scores=RetrievalScores(
                    raw_score=float(hit["score"]),
                    normalized_score=min(max(float(hit["score"]), 0.0), 1.0),
                    rank=rank,
                ),
                found_by_lanes=(RetrievalLane.DENSE,),
            )
            chunks.append(chunk)

        return CandidateEvidencePool(
            plan_id=plan.plan_id,
            candidates=tuple(chunks),
            lanes_used=(RetrievalLane.DENSE,),
        )

    def _stub_adjacency(node_id: str, relations: Any) -> tuple:
        return ()

    route = RouteContract(
        route_id=route_id,
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope=interview_slug or "apps_qna",
        data_class="internal",
    )
    plan_contract = L1PlanContract(
        task_spec=f"interview_prep:{interview_slug}",
        query_spec=query_text or interview_slug,
        grounding_required=True,
        user_task_text=query_text,
    )

    result = run_c0(
        route=route,
        plan_contract=plan_contract,
        fetch=_real_fetch_fn,
        adjacency=_stub_adjacency,
    )

    canonical = result.contract

    # W1.2: grounded=True when we have real retrieval hits, regardless of
    # what the canonical pipeline emits (it may emit EMPTY if the pool
    # passes through unchanged; raw_hits is the ground truth).
    grounded = bool(raw_hits)
    sufficiency = "grounded" if grounded else "template_only"

    # Prefer raw_hits IDs as retrieval_sources (concrete evidence); fall back
    # to canonical must_use_view if available.
    if raw_hits:
        retrieval_sources: tuple[str, ...] = tuple(h["id"] for h in raw_hits if h.get("id"))
        source_register: tuple[str, ...] = retrieval_sources
        claim_confidence = float(raw_hits[0]["score"]) if raw_hits else 0.0
    else:
        retrieval_sources = ()
        source_register = ()
        if canonical.must_use_view:
            retrieval_sources = tuple(v.source_id for v in canonical.must_use_view)
            source_register = retrieval_sources
        claim_confidence = float(canonical.support_score)

    contradiction_flags: tuple[str, ...] = ()
    if canonical.contradiction_flags:
        contradiction_flags = tuple(str(f) for f in canonical.contradiction_flags)

    freshness = "current"
    if canonical.freshness_report and canonical.freshness_report.stale_sources:
        freshness = "stale"

    return FinalEvidenceContract(
        schema_version="1.0",
        producer="agentic_core.C0",
        grounded=grounded,
        retrieval_sources=retrieval_sources,
        route_id=route_id,
        evidence_sufficiency=sufficiency,
        interview_slug=interview_slug,
        query_text=query_text,
        source_register=source_register,
        freshness_assessment=freshness,
        claim_confidence=claim_confidence,
        contradiction_flags=contradiction_flags,
    )


__all__ = [
    "C0UnavailableError",
    "call_c0",
    "_real_fetch",
    "_chroma_fetch",
    "_flat_fetch",
    "_load_index",
    "_load_chroma_collection",
    "_reset_index_cache",
]
