"""R1B lookup — HistoricalIntentRecord vectors first; chunks are never primary keys."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.cache.r1b_compatibility import CompatibilityVerdict, assess_candidate_for_reuse, compatibility_report_row
from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    R1B_CHUNK_REUSE_AUTHORITY,
    R1B_NOT_C0_FACT_VECTORS,
    R1B_REUSE_AUTHORITY_SCOPE,
    R1B_SECTION_REUSE_AUTHORITY,
    r1b_reuse_authority_policy,
)
from apps_rg.cache.r1b_intent_vector import (
    cosine_similarity,
    intent_text_from_request,
    normalized_intent_digest,
    pseudo_vector_from_digest,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root


@dataclass
class R1BLookupHit:
    record: HistoricalIntentRecord
    chunks: list[HistoricalOutputChunk]
    similarity: float
    verdict: CompatibilityVerdict


def lookup_r1b_role_target_run(
    raw_request: dict[str, Any],
    *,
    store: R1BSemanticCacheStore | None = None,
    similarity_threshold: float = 0.88,
    query_prompt_hash: str = "",
    query_gate_hash: str = "",
) -> R1BLookupHit | None:
    """Search intent records by vector similarity; validate child chunks before hit."""
    st = store or R1BSemanticCacheStore(default_store_root())
    intent_text = intent_text_from_request(raw_request)
    query_digest = normalized_intent_digest(intent_text)
    from apps_rg.cache.r1b_bge_embedding import resolve_query_vector

    query_vec, _kind = resolve_query_vector(intent_text, query_digest)

    best: R1BLookupHit | None = None
    for rid in st.list_intent_record_ids():
        record = st.load_intent(rid)
        if record is None or not record.cache_admissible:
            continue
        if record.cache_grain != CACHE_GRAIN_ROLE_TARGET_RUN:
            continue
        rec_vec = st.load_intent_vector(record)
        sim = cosine_similarity(query_vec, rec_vec)
        if sim < similarity_threshold:
            continue
        chunks = st.load_chunks(record.record_id)
        verdict = assess_candidate_for_reuse(
            record,
            chunks,
            query_digest=query_digest,
            query_prompt_hash=query_prompt_hash,
            query_gate_hash=query_gate_hash,
        )
        if not verdict.admissible:
            continue
        if best is None or sim > best.similarity:
            best = R1BLookupHit(record=record, chunks=chunks, similarity=sim, verdict=verdict)
    return best


def lookup_r1b_with_compatibility_report(
    raw_request: dict[str, Any],
    *,
    store: R1BSemanticCacheStore | None = None,
    similarity_threshold: float = 0.88,
    query_prompt_hash: str = "",
    query_gate_hash: str = "",
) -> tuple[R1BLookupHit | None, list[dict[str, Any]]]:
    """Return hit (if any) plus per-candidate compatibility rows for proof fixtures."""
    st = store or R1BSemanticCacheStore(default_store_root())
    intent_text = intent_text_from_request(raw_request)
    query_digest = normalized_intent_digest(intent_text)
    from apps_rg.cache.r1b_bge_embedding import resolve_query_vector

    query_vec, _kind = resolve_query_vector(intent_text, query_digest)
    report: list[dict[str, Any]] = []
    best: R1BLookupHit | None = None

    for rid in st.list_intent_record_ids():
        record = st.load_intent(rid)
        if record is None:
            continue
        if record.cache_grain != CACHE_GRAIN_ROLE_TARGET_RUN:
            continue
        rec_vec = st.load_intent_vector(record)
        sim = cosine_similarity(query_vec, rec_vec)
        chunks = st.load_chunks(record.record_id)
        verdict = assess_candidate_for_reuse(
            record,
            chunks,
            query_digest=query_digest,
            query_prompt_hash=query_prompt_hash,
            query_gate_hash=query_gate_hash,
        )
        report.append(compatibility_report_row(candidate_record_id=rid, verdict=verdict, similarity=sim))
        if not record.cache_admissible or not verdict.admissible or sim < similarity_threshold:
            continue
        if best is None or sim > best.similarity:
            best = R1BLookupHit(record=record, chunks=chunks, similarity=sim, verdict=verdict)

    return best, report


def filter_chunks_by_section(
    chunks: list[HistoricalOutputChunk],
    *,
    section_id: str,
    chunk_type: str | None = None,
) -> list[HistoricalOutputChunk]:
    """P5 — section drawer filter for governed Chroma / file store reads."""
    sid = str(section_id or "").strip()
    want_type = chunk_type or (f"{sid}_output" if sid else "")
    out: list[HistoricalOutputChunk] = []
    for ch in chunks:
        if sid and ch.section_id != sid:
            continue
        if want_type and ch.chunk_type != want_type:
            continue
        out.append(ch)
    return out


def lookup_section_output_chunk(
    hit: R1BLookupHit,
    section_id: str,
) -> HistoricalOutputChunk | None:
    """Best section display chunk for reuse preflight (P5)."""
    rows = filter_chunks_by_section(
        hit.chunks,
        section_id=section_id,
        chunk_type=f"{section_id}_output",
    )
    for ch in rows:
        if len(str(ch.chunk_text or "").strip()) >= 8:
            return ch
    return rows[0] if rows else None


def hit_to_probe_dict(hit: R1BLookupHit) -> dict[str, Any]:
    return {
        "cached": True,
        "route_id": "R1B_SEMANTIC_CACHE",
        "cache_grain": CACHE_GRAIN_ROLE_TARGET_RUN,
        "lookup_anchor": "HistoricalIntentRecord.request_intent_vector",
        "parent_intent_record_id": hit.record.record_id,
        "similarity": hit.similarity,
        "similarity_score": hit.similarity,
        "child_chunk_count": len(hit.chunks),
        "independent_chunk_identities": False,
        "not_c0_fact_vectors": True,
        "r1b_vs_c0": R1B_NOT_C0_FACT_VECTORS,
        "reuse_scope": R1B_REUSE_AUTHORITY_SCOPE,
        "reuse_authority_policy": r1b_reuse_authority_policy(),
        "section_level_semantic_reuse_authority": R1B_SECTION_REUSE_AUTHORITY,
        "section_level_lane_skip_authorized": False,
        "child_chunk_reuse_authority": R1B_CHUNK_REUSE_AUTHORITY,
        "source_run_id": hit.record.source_run_id,
        "x3_disposition": hit.record.x3_disposition,
        "compatibility_checks": hit.verdict.checks,
    }


__all__ = [
    "R1BLookupHit",
    "filter_chunks_by_section",
    "hit_to_probe_dict",
    "lookup_r1b_role_target_run",
    "lookup_r1b_with_compatibility_report",
    "lookup_section_output_chunk",
]
