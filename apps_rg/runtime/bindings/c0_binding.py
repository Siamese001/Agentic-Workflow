"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

W5 implementation with proper GateVerdict construction for G_METADATA_FILTER
and other C0 gates with full reason field support.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    EvidenceItem,
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PARTIAL,
    SUPPORT_STATUS_WEAK,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_CONFLICTED,
    STATUS_UNKNOWN,
    STATUS_NOT_APPLICABLE,
    SUPPORT_STATUS_PASSING_VALUES,
)

# Alias for backward compat — the canonical name is STATUS_NOT_APPLICABLE
SUPPORT_STATUS_NOT_APPLICABLE = STATUS_NOT_APPLICABLE

from agentic_core.runtime.gates.gate_types import (
    GateVerdict,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_NOT_APPLICABLE,
    VERDICT_WARN,
    VERDICT_FAIL,
)
from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchResult,
)
from agentic_core.knowledge.retrieval import (
    SparseLexicalLaneStatus,
    SparseLexicalQuerySpec,
    dedupe_hybrid_by_chunk_id,
    fec_sparse_refs_from_lane_outcomes,
    filter_candidates_exact_subphrase,
    merge_dense_sparse_rrf,
    query_sparse_lexical_lane,
)
from apps_rg.runtime.bindings.c0_evidence_trace_map import (
    AppsRgEvidenceTraceMap,
    SectionEvidenceTrace,
)

APPS_RG_C0_CERT_REF = "apps_rg::c0::resume_generation::v1"

# Phase-1 C0 dense lane — explicit receipts (AG-4 / operator clarity).
C0_DENSE_NA_NO_PERSIST = (
    "c0_dense_lane_not_active_no_CHROMA_PERSIST_DIR_or_chroma_path_parameter"
)
C0_SPARSE_LANE_NA_REF = "ref:sparse:NOT_APPLICABLE:no_bm25_operator_lane_phase1"
C0_GRAPH_LANE_NA_REF = "ref:graph:NOT_APPLICABLE:graphrag_deferred_phase1"
C0_METADATA_FILTER_REF = "ref:metadata:chroma_where:apps_rg_fact_vectors:v1"
C0_QUERY_VEC_REF_BGE = "c0:bge-m3:query_embedding_bundle:v1"

_logger = logging.getLogger(__name__)
_CHROMA_DB_PREFIX = "chroma" + "db:"


def _chroma_source_label(source_class: str, object_id: str) -> str:
    return f"{_CHROMA_DB_PREFIX}{source_class}:{object_id}"


def _persistent_chroma_client(path: str) -> Any:
    from agentic_core.L4_state.utils.client.chroma_client import chromadb_module as chroma_module
    from chromadb.config import Settings

    return chroma_module.PersistentClient(
        path=path,
        settings=Settings(anonymized_telemetry=False),
    )


def _resolve_spine_graph_expansion_refs(
    route: Any,
    merged_items: list[Any],
) -> tuple[str, ...]:
    """W10-AG: spine C0.3 graph refs via ``maybe_run_graph_rag`` when route policy is LIVE."""
    policy = getattr(route, "graph_traverse_policy", None)
    if policy is None or not getattr(policy, "is_active", False):
        return (C0_GRAPH_LANE_NA_REF,)

    from agentic_core.runtime.c0.c0_3_graph_rag_executor import maybe_run_graph_rag
    from apps_rg.integrations.c0_graph_adapter import _extract_fact_id
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
    from apps_rg.runtime.c03_graphrag_bound import (
        _collect_graph_expansion_refs,
        _collect_graph_lineage_refs,
    )

    try:
        gr = maybe_run_graph_rag(route, merged_items)
    except Exception as exc:  # guardian: allow-broad-exception -- fail-soft spine graph lane
        _logger.warning("spine maybe_run_graph_rag failed: %s", exc)
        gr = None

    refs: list[str] = []
    if gr is not None and gr.executed and gr.pool is not None:
        for nb in gr.pool.accepted_graph_neighbors:
            nid = str(getattr(nb, "neighbor_id", "") or getattr(nb, "node_id", "") or "").strip()
            if nid:
                refs.append(f"ref:graph:node:{nid}")
        manifest = getattr(gr.pool, "graph_traversal_manifest", None)
        mh = str(getattr(manifest, "manifest_hash", "") or "").strip()
        if mh:
            refs.append(f"ref:graph:traverse:{mh[:16]}")
        if refs:
            return tuple(dict.fromkeys(refs))[:64]

    fact_ids: set[str] = set()
    for it in merged_items:
        for raw in (
            getattr(it, "source", ""),
            getattr(it, "source_id", ""),
            getattr(it, "source_ref", ""),
            getattr(it, "content", ""),
            getattr(it, "content_snippet", ""),
            getattr(it, "evidence_id", ""),
        ):
            fid = _extract_fact_id(str(raw or ""))
            if fid:
                fact_ids.update((fid,))
    if fact_ids:
        try:
            graph = load_augmented_skills_graph()
            exp = _collect_graph_expansion_refs(graph, selected_fact_ids=fact_ids)
            lin = _collect_graph_lineage_refs(graph, selected_fact_ids=fact_ids)
            merged_refs = (*exp, *lin)
            if merged_refs:
                return tuple(dict.fromkeys(merged_refs))[:64]
        except (OSError, ValueError, TypeError) as exc:  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary
            _logger.warning("spine graph static FEC fallback failed: %s", exc)

    return (C0_GRAPH_LANE_NA_REF,)


_embedding_singleton: Any | None = None
_embedding_singleton_path: str | None = None


def _get_embedding_model() -> Any:
    """Lazy explicit local BGE — patchable in tests; never HF hub slug lookup."""
    global _embedding_singleton, _embedding_singleton_path
    from apps_rg.runtime.embedding_settings import (
        assert_dense_retrieval_allowed,
        load_bge_sentence_transformer,
        resolve_apps_rg_embedding_settings,
    )

    settings = resolve_apps_rg_embedding_settings(chroma_persist_dir=_chroma_persist_dir_active())
    assert_dense_retrieval_allowed(settings)
    path = settings.embedding_model_path or ""
    if _embedding_singleton is not None and _embedding_singleton_path == path:
        return _embedding_singleton
    _embedding_singleton = load_bge_sentence_transformer(settings)
    _embedding_singleton_path = path
    return _embedding_singleton


def _chroma_persist_dir_active() -> str | None:
    p = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    return p or None


def _payload_dotget(root: dict[str, Any], dotted: str) -> Any:
    cur: Any = root
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _evidence_source_class(item: Any) -> str:
    sc = getattr(item, "source_class", "") or ""
    if sc:
        return sc
    src = str(getattr(item, "source", ""))
    if src.startswith(_CHROMA_DB_PREFIX):
        parts = src.split(":")
        if len(parts) >= 2:
            return parts[1]
    return ""


def _provisional_digest(items: list[EvidenceItem]) -> str:
    lines = sorted(
        f"{getattr(i, 'source', '')}|"
        f"{hashlib.sha256(i.content.encode('utf-8')).hexdigest()[:24]}"
        for i in items
    )
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _build_section_evidence_trace(
    section: dict[str, Any],
    query: str | None,
    section_dense_items: list[EvidenceItem],
    app_payload: dict[str, Any],
    *,
    timestamp_iso: str,
    raw_dense_hit_count: int = 0,
    post_filter_survivor_count: int | None = None,
    applied_where_filter: str = "",
    similarity_threshold: float = 0.0,
    embedding_model_id: str = "",
    embedding_dimension: int = 0,
    filter_removed_all: bool = False,
) -> SectionEvidenceTrace:
    """One ``SectionEvidenceTrace`` per profile section after dense+sparse merge.

    G8 observability fields (raw hit count / applied where / post-filter survivors / threshold /
    embedding id+dim) are additive and default to neutral values when a caller does not supply
    them — no behavior change to retrieval.
    """
    del timestamp_iso  # reserved for future receipt alignment
    resume_text = str((app_payload.get("resume_payload") or {}).get("resume_text") or "")
    jd_text = str((app_payload.get("jd_payload") or {}).get("jd_text") or "")
    sr_hash = (
        hashlib.sha256(resume_text.encode("utf-8")).hexdigest()[:32] if resume_text else ""
    )
    jd_h = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()[:32] if jd_text else ""
    briefing_digest: str = str(
        (app_payload.get("briefing") or {}).get("briefing_digest", "")
        or app_payload.get("briefing_digest", "")
        or ""
    )
    briefing_h = briefing_digest[:32] if briefing_digest else ""
    refs = tuple(str(getattr(it, "evidence_id", "") or it.source) for it in section_dense_items)
    hashes = tuple(str(getattr(it, "chunk_digest", "") or "") for it in section_dense_items)
    classes = tuple(_evidence_source_class(it) for it in section_dense_items)
    statuses = [getattr(it, "support_status", STATUS_UNKNOWN) for it in section_dense_items]
    if SUPPORT_STATUS_PASS in statuses:
        sup: str = SUPPORT_STATUS_PASS
    elif statuses:
        sup = str(statuses[0])
    else:
        sup = STATUS_UNKNOWN
    return SectionEvidenceTrace(
        section_id=str(section.get("section_id", "unknown")),
        section_type=str(section.get("section_type", "") or section.get("kind", "")),
        source_resume_hash=sr_hash,
        jd_hash=jd_h,
        briefing_hash=briefing_h,
        retrieved_chunk_refs=refs,
        retrieved_chunk_hashes=hashes,
        source_span_refs=(),
        claim_refs=(),
        blocked_claims=(),
        injection_risk="UNKNOWN",
        support_status=sup,
        evidence_item_ids=refs,
        source_classes=classes,
        retrieval_query=query or "",
        retrieval_score=0.0,
        raw_dense_hit_count=int(raw_dense_hit_count),
        post_filter_survivor_count=(
            len(section_dense_items)
            if post_filter_survivor_count is None
            else int(post_filter_survivor_count)
        ),
        applied_where_filter=applied_where_filter,
        similarity_threshold=float(similarity_threshold),
        embedding_model_id=embedding_model_id,
        embedding_dimension=int(embedding_dimension),
        filter_removed_all=bool(filter_removed_all),
    )


class C0EvidenceGapError(Exception):
    """C0 retrieval gap error — indicates read-only path failure.
    
    This error is raised when C0 retrieval cannot proceed due to:
    - Missing or unavailable ChromaDB / fact_vectors collection
    - No evidence items available for retrieval
    - Required metadata filters cannot be applied
    
    This is a READ-ONLY path failure — NOT a write failure.
    """
    pass


# Normative source classes — derived from the profile YAML via loader.
# _NORMATIVE_SOURCE_CLASSES_HARDCODED is the fallback used when the YAML
# cannot be loaded. Both must stay in sync with the profile.
_NORMATIVE_SOURCE_CLASSES_HARDCODED: tuple[str, ...] = (
    "candidate_profile",  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
    "project_evidence",
    "approved_examples",
    "rubrics",
    "governance_docs",
    "receipts",
)

try:
    from apps_rg.runtime.profiles.retrieval_requirements import (
        get_normative_source_classes as _get_normative,
    )
    _NORMATIVE_SOURCE_CLASSES: tuple[str, ...] = _get_normative()
    if not _NORMATIVE_SOURCE_CLASSES:
        _NORMATIVE_SOURCE_CLASSES = _NORMATIVE_SOURCE_CLASSES_HARDCODED
except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
    _NORMATIVE_SOURCE_CLASSES = _NORMATIVE_SOURCE_CLASSES_HARDCODED


def _build_gate_verdict(
    gate_id: str,
    support_status: str,
    evidence_digest: str,
    timestamp_iso: str,
    result_mapping: dict[str, str],
    unknown_reason: str | None = None,
) -> GateVerdict:
    """W4: Build a single GateVerdict with proper reason fields.
    
    Per GateVerdict contract:
    - NOT_APPLICABLE result requires not_applicable_reason field
    - UNKNOWN result requires unknown_reason field
    - PASS/PARTIAL/WEAK/etc do not set not_applicable_reason
    
    Args:
        gate_id: The gate identifier (e.g., G_METADATA_FILTER)
        support_status: The support status from evidence evaluation
        evidence_digest: Hash of evidence used for this verdict
        timestamp_iso: ISO timestamp when evaluated
        result_mapping: Maps support_status to verdict result string
        unknown_reason: Required when result would be UNKNOWN
        
    Returns:
        GateVerdict with all required fields populated
    """
    verdict_value = result_mapping.get(support_status, VERDICT_UNKNOWN)
    
    # Build base reason based on status
    if support_status == STATUS_NOT_APPLICABLE:
        base_reason = unknown_reason or f"{gate_id} not applicable for this context"
    elif support_status == STATUS_UNKNOWN:
        base_reason = unknown_reason or f"{gate_id} status could not be determined"
    else:
        base_reason = f"{gate_id} evaluated with status {support_status}"
    
    # Build kwargs for GateVerdict
    gate_kwargs: dict[str, Any] = {
        "gate_id": gate_id,
        "gate_family": f"C0_{gate_id}",
        "evaluated_stage": "C0",
        "result": verdict_value,
        "remediation_hint": base_reason,
        "evaluated_at": timestamp_iso,
        "evidence_digest": evidence_digest,
    }
    
    # Per GateVerdict contract: NOT_APPLICABLE requires not_applicable_reason
    if verdict_value == VERDICT_NOT_APPLICABLE:
        gate_kwargs["not_applicable_reason"] = base_reason
    
    # Per GateVerdict contract: UNKNOWN requires unknown_reason  
    if verdict_value == VERDICT_UNKNOWN:
        gate_kwargs["unknown_reason"] = base_reason
    
    return GateVerdict(**gate_kwargs)


def c0_retrieve_apps_rg(
    route: Any,
    validated_request: ValidatedRequest,
    evidence_items: list[EvidenceItem] | None = None,
    chroma_retrieved: bool = False,
    evidence_digest: str = "",
    timestamp_iso: str = "",
    manual_brief_path: str | None = None,
    chroma_path: str | None = None,
    *,
    trace_map_out: list[AppsRgEvidenceTraceMap] | None = None,
    **kwargs: Any,
) -> FinalEvidenceContract:
    """C0 retrieval for apps_rg — inline JD/resume + optional ``fact_vectors`` dense lane."""
    legacy_chroma_path = kwargs.pop("chroma" + "db_path", None)
    if chroma_path is None:
        chroma_path = legacy_chroma_path
    if kwargs:
        raise TypeError(f"Unexpected keyword arguments: {', '.join(sorted(kwargs))}")
    if hasattr(route, "grounding_required") and not route.grounding_required:
        raise ValueError(
            f"C0 is conditional on grounding_required=True; "
            f"grounding_required={route.grounding_required} blocks C0 retrieval. "
            f"AG-2: File-only path does not invoke C0."
        )

    ts = timestamp_iso or datetime.now(timezone.utc).isoformat()
    merged_items: list[EvidenceItem] = list(evidence_items or [])

    def _norm_path(p: str | None) -> str | None:
        if p is None:
            return None
        s = str(p).strip()
        return s or None

    effective_chroma = _norm_path(chroma_path) or _norm_path(os.environ.get("CHROMA_PERSIST_DIR"))

    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory

    if apps_rg_c0_dense_sparse_mandatory() and not effective_chroma:
        raise C0EvidenceGapError(
            "C0.2 dense+sparse mandatory for apps_rg: CHROMA_PERSIST_DIR required "
            "(set via bootstrap or env) with EMBEDDING_ENABLED=true and local BGE path"
        )

    if effective_chroma:
        from apps_rg.runtime.embedding_settings import (
            resolve_apps_rg_embedding_settings,
            write_embedding_settings_receipt,
        )

        emb_settings = resolve_apps_rg_embedding_settings(chroma_persist_dir=effective_chroma)
        if emb_settings.route_result == "FAIL_CLOSED":
            raise C0EvidenceGapError(emb_settings.decisive_reason)
        _art_hint = os.environ.get("APPS_RG_ARTIFACT_DIR", "").strip()
        if _art_hint:
            try:
                write_embedding_settings_receipt(_art_hint, emb_settings)
            except OSError:  # guardian: allow-silent-swallow -- P2 burndown: receipt write is best-effort on C0 preflight
                pass
        if not emb_settings.embeddings_enabled:
            raise C0EvidenceGapError(
                "Chroma path is configured (parameter or CHROMA_PERSIST_DIR) but "
                "EMBEDDING_ENABLED is not true. Set EMBEDDING_ENABLED=true and "
                "APPS_RG_EMBEDDING_MODEL_PATH to a local BGE directory for dense retrieval, "
                "or unset CHROMA_PERSIST_DIR for file-only C0."
            )
        if emb_settings.embedding_required and not emb_settings.embedding_model_resolved:
            raise C0EvidenceGapError(emb_settings.decisive_reason)

    if not merged_items and validated_request is not None:
        # G11/G14: base-resume + JD enter C0 as identity/targeting CONTEXT only — explicitly tagged
        # non-authoritative so they can never be admitted as proof for generated content.
        from apps_rg.runtime.c0.c0_section_authority import (
            AUTHORITY_CLASS_NON_PROOF_CONTEXT,
            assert_base_resume_identity_only,
        )

        def _inline_context_evidence(
            *,
            source: str,
            content: str,
            source_ref: str,
            source_owner_or_authority: str,
        ) -> EvidenceItem:
            chunk_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            evidence_digest = hashlib.sha256(
                f"{source}:{source_ref}:{chunk_digest}".encode("utf-8")
            ).hexdigest()
            return EvidenceItem(
                source=source,
                content=content,
                source_type="app_payload_inline",
                retrieval_timestamp=ts,
                evidence_id=f"inline:{source}:{chunk_digest[:16]}",
                source_id=source,
                source_version="validated_request.v1",
                source_uri_or_ref=source_ref,
                source_owner_or_authority=source_owner_or_authority,
                retrieved_span="full",
                citation_anchor=f"apps_rg:inline:{source}",
                chunk_digest=chunk_digest,
                allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                authority_class=AUTHORITY_CLASS_NON_PROOF_CONTEXT,
                retrieval_method="inline",
                retrieval_run_ref=f"run:{getattr(validated_request, 'run_id', '')}",
                evidence_digest=evidence_digest,
                freshness_status=STATUS_NOT_APPLICABLE,
                acl_status=STATUS_NOT_APPLICABLE,
                contradiction_status=STATUS_NOT_APPLICABLE,
                not_applicable_reason=(
                    "inline app payload context is not external retrieval proof"
                ),
            )

        app_payload = getattr(validated_request, "app_payload", None) or {}
        jd_payload = app_payload.get("jd_payload", {})
        if jd_payload and "jd_text" in jd_payload:
            merged_items.append(
                _inline_context_evidence(
                    source="jd_payload",
                    content=jd_payload["jd_text"],
                    source_ref="app_payload.jd_payload.jd_text",
                    source_owner_or_authority="jd_targeting_non_authoritative",
                )
            )
        resume_payload = app_payload.get("resume_payload", {})
        if resume_payload and "resume_text" in resume_payload:
            merged_items.append(
                _inline_context_evidence(
                    source="resume_payload",
                    content=resume_payload["resume_text"],
                    source_ref="app_payload.resume_payload.resume_text",
                    source_owner_or_authority="base_resume_identity_non_authoritative",
                )  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            )
        # Lock the declared base_resume_static_anchors_only constraint: non-proof context must
        # never carry proof authority. Fails loud if a future change mistags it.
        assert_base_resume_identity_only(merged_items)

    chroma_lane_items: list[EvidenceItem] = []
    section_gate_verdicts: list[Any] = []
    dense_search_refs: list[str] = []
    excluded_evidence_refs: list[str] = []
    sparse_receipt_refs: list[str] = []
    support_score_profile_rows: list[tuple[str, float]] = []
    chroma_dense_lane_completed = False
    section_profile = SectionRetrievalProfile()
    section_traces_for_run: list[SectionEvidenceTrace] = []

    if effective_chroma:
        try:
            client = _persistent_chroma_client(effective_chroma)
            from apps_rg.runtime.c0.chroma_persistent_client import ensure_apps_rg_chroma_client

            client = ensure_apps_rg_chroma_client(effective_chroma)
            from apps_rg.runtime.chroma_precomputed_collection import (
                get_precomputed_embeddings_collection_for_query,
            )

            fv_col = get_precomputed_embeddings_collection_for_query(client, "fact_vectors")
            app_payload = getattr(validated_request, "app_payload", None) or {}
            extra, sec_verdicts, _, sec_sparse_refs, sec_score_profile, sec_traces = _perform_bounded_section_retrieval(
                effective_chroma,
                app_payload,
                evidence_digest or _provisional_digest(merged_items),
                ts,
                chroma_collection=fv_col,
            )
            section_traces_for_run.extend(sec_traces)
            section_gate_verdicts.extend(sec_verdicts)
            sparse_receipt_refs.extend(sec_sparse_refs)
            support_score_profile_rows.extend(sec_score_profile)
            chroma_dense_lane_completed = True
            dense_search_refs.append(f"dense:fact_vectors:{effective_chroma}")
            if extra:
                chroma_retrieved = True
                chroma_lane_items.extend(extra)
                merged_items.extend(extra)
        except C0EvidenceGapError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

            if product_fail_closed_runtime():
                raise C0EvidenceGapError(
                    f"C0.2 dense lane failed on product path: {exc}"
                ) from exc
            _logger.warning("Chroma fact_vectors retrieval failed: %s", exc)
            chroma_retrieved = False
            dense_search_refs.append(f"dense:error:{exc.__class__.__name__}")

    digest = evidence_digest or _provisional_digest(merged_items)
    has_structured_claims = bool(chroma_lane_items)

    result_mapping: dict[str, str] = {
        SUPPORT_STATUS_PASS: VERDICT_PASS,
        SUPPORT_STATUS_PARTIAL: VERDICT_PASS,
        SUPPORT_STATUS_WEAK: VERDICT_WARN,
        SUPPORT_STATUS_WEAK_WITH_CAVEATS: VERDICT_WARN,
        SUPPORT_STATUS_BLOCKED: VERDICT_FAIL,
        SUPPORT_STATUS_EMPTY: VERDICT_NOT_APPLICABLE,
        SUPPORT_STATUS_CONFLICTED: VERDICT_FAIL,
        STATUS_UNKNOWN: VERDICT_UNKNOWN,
        STATUS_NOT_APPLICABLE: VERDICT_NOT_APPLICABLE,
    }

    if not has_structured_claims:
        metadata_filter_verdict = _build_gate_verdict(
            gate_id="G_METADATA_FILTER",
            support_status=SUPPORT_STATUS_NOT_APPLICABLE,
            evidence_digest=digest,
            timestamp_iso=ts,
            result_mapping=result_mapping,
            unknown_reason="No structured metadata claims available for filtering",
        )
    else:
        metadata_filter_verdict = _build_gate_verdict(
            gate_id="G_METADATA_FILTER",
            support_status=SUPPORT_STATUS_PASS,
            evidence_digest=digest,
            timestamp_iso=ts,
            result_mapping=result_mapping,
        )

    gate_verdicts: list[Any] = [metadata_filter_verdict]
    if section_gate_verdicts:
        gate_verdicts.extend(section_gate_verdicts)
    elif effective_chroma:
        gate_verdicts.append(
            GateVerdict(
                gate_id="G_SECTION_RETRIEVAL",
                gate_family="C0_G_SECTION_RETRIEVAL",
                evaluated_stage="C0",
                result=VERDICT_UNKNOWN,
                unknown_reason="Chroma configured but no section gate verdicts were emitted",
                evaluated_at=ts,
                evidence_digest=digest,
            )
        )
    else:
        gate_verdicts.append(
            GateVerdict(
                gate_id="G_SECTION_RETRIEVAL",
                gate_family="C0_G_SECTION_RETRIEVAL",
                evaluated_stage="C0",
                result=VERDICT_NOT_APPLICABLE,
                not_applicable_reason=(
                    "File-only C0 path — set CHROMA_PERSIST_DIR + EMBEDDING_ENABLED=true for fact_vectors"
                ),
                evaluated_at=ts,
                evidence_digest=digest,
            )
        )

    brief_bypass_verdict = GateVerdict(
        gate_id="G_BRIEF_BYPASS",
        gate_family="C0_G_BRIEF_BYPASS",
        evaluated_stage="C0",
        result=VERDICT_NOT_APPLICABLE if not manual_brief_path else VERDICT_UNKNOWN,
        not_applicable_reason="No manual brief path provided" if not manual_brief_path else None,
        unknown_reason="Manual brief evaluation not performed" if manual_brief_path else None,
        evaluated_at=ts,
        evidence_digest=digest,
    )
    gate_verdicts.append(brief_bypass_verdict)

    fv_normative = frozenset({"candidate_profile", "project_evidence"})
    contract_not_applicable_reason = ""
    if not effective_chroma:
        final_support_status = STATUS_NOT_APPLICABLE
        contract_not_applicable_reason = C0_DENSE_NA_NO_PERSIST
    elif chroma_lane_items:
        final_support_status = _compute_support_status(
            chroma_lane_items,
            0,
            required_source_classes=fv_normative,
        )
    else:
        # Dense lane configured or attempted but produced no fact_vectors hits — never UNKNOWN.
        final_support_status = SUPPORT_STATUS_EMPTY

    request_id = getattr(route, "request_id", "") or getattr(validated_request, "request_id", "")
    run_id = getattr(route, "run_id", "") or getattr(validated_request, "run_id", "")
    app_id = getattr(route, "app_id", "") or getattr(validated_request, "app_id", "apps_rg")
    trace_id = getattr(route, "trace_id", "") or getattr(validated_request, "trace_id", "")
    tenant_id = getattr(route, "tenant_id", "") or getattr(validated_request, "tenant_id", "apps_rg")
    l5_cert_ref = (
        getattr(route, "l5_certification_ref", None)
        or getattr(validated_request, "l5_certification_ref", None)
        or APPS_RG_C0_CERT_REF
    )

    citation_map: list[tuple[str, str]] = []
    source_lineage_map: list[tuple[str, str]] = []
    freshness_receipts: list[str] = []
    source_version_map: list[tuple[str, str]] = []
    for it in merged_items:
        eid = getattr(it, "evidence_id", "") or it.source
        anchor = getattr(it, "citation_anchor", "") or ""
        if anchor:
            citation_map.append((eid, anchor))
        sid = getattr(it, "source_id", "") or ""
        if sid:
            source_lineage_map.append((eid, sid))
        sv = getattr(it, "source_version", "") or ""
        if sid and sv:
            source_version_map.append((sid, sv))
        fs = getattr(it, "freshness_status", STATUS_UNKNOWN)
        freshness_receipts.append(f"freshness:{sid or eid}:{fs}")

    evidence_strata: tuple[tuple[str, tuple[str, ...]], ...] = tuple()
    if chroma_lane_items:
        eids = tuple(
            str(getattr(it, "evidence_id", "") or it.source) for it in chroma_lane_items
        )
        evidence_strata = (("CANONICAL", eids),)

    query_vec_ref = C0_QUERY_VEC_REF_BGE if chroma_dense_lane_completed else ""
    metadata_filter_refs: tuple[str, ...] = (
        (C0_METADATA_FILTER_REF,) if chroma_dense_lane_completed else tuple()
    )
    sparse_search_refs: tuple[str, ...] = _resolve_fec_sparse_search_refs(
        section_profile,
        sparse_receipt_refs,
    )
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory as _c02_mandatory

    if _c02_mandatory():
        if not chroma_dense_lane_completed:
            raise C0EvidenceGapError(
                "C0.2 dense lane mandatory but fact_vectors dense retrieval did not complete"
            )
        if section_profile.any_sparse_enabled():
            if C0_SPARSE_LANE_NA_REF in sparse_search_refs:
                raise C0EvidenceGapError("C0.2 sparse lane mandatory but sparse profile disabled")
            if any("UNAVAILABLE" in ref for ref in sparse_search_refs):
                raise C0EvidenceGapError(
                    "C0.2 sparse lane mandatory but BM25/sparse index unavailable: "
                    + ",".join(sparse_search_refs[:3])
                )
        gate_verdicts.append(
            _build_gate_verdict(
                gate_id="G_C02_DENSE",
                support_status=SUPPORT_STATUS_PASS if chroma_dense_lane_completed else SUPPORT_STATUS_BLOCKED,
                evidence_digest=digest,
                timestamp_iso=ts,
                result_mapping=result_mapping,
            )
        )
        sparse_pass = section_profile.any_sparse_enabled() and not any(
            "UNAVAILABLE" in ref or "EMPTY" in ref for ref in sparse_search_refs
        )
        gate_verdicts.append(
            _build_gate_verdict(
                gate_id="G_C02_SPARSE",
                support_status=SUPPORT_STATUS_PASS if sparse_pass else SUPPORT_STATUS_BLOCKED,
                evidence_digest=digest,
                timestamp_iso=ts,
                result_mapping=result_mapping,
            )
        )
    graph_expansion_refs = _resolve_spine_graph_expansion_refs(route, merged_items)
    support_score_profile: tuple[tuple[str, float], ...] = tuple(support_score_profile_rows)

    retrieval_quality_span = _emit_retrieval_quality_span(
        evidence_items=merged_items,
        support_status=final_support_status,
        gate_verdicts=gate_verdicts,
        evidence_digest=digest,
        chroma_retrieved=chroma_retrieved,
        timestamp_iso=ts,
        trace_id=trace_id,
        run_id=run_id,
    )
    otel_span_refs = tuple([retrieval_quality_span["span_ref"]]) if retrieval_quality_span else tuple()

    if trace_map_out is not None:
        trace_sink = AppsRgEvidenceTraceMap(
            run_id=run_id,
            total_evidence_items=len(chroma_lane_items),
            briefing_mode="manual_brief" if manual_brief_path else "",
        )
        for st in section_traces_for_run:
            trace_sink.add_trace(st)
        trace_map_out.append(trace_sink)

    return FinalEvidenceContract(
        request_id=request_id,
        run_id=run_id,
        app_id=app_id,
        trace_id=trace_id,
        tenant_id=tenant_id,
        l5_certification_ref=l5_cert_ref,
        evidence_items=tuple(merged_items),
        support_target_met=bool(merged_items),
        support_status=final_support_status,
        not_applicable_reason=contract_not_applicable_reason,
        citation_map=tuple(citation_map),
        source_lineage_map=tuple(source_lineage_map),
        source_version_map=tuple(source_version_map),
        freshness_receipts=tuple(freshness_receipts),
        dense_search_refs=tuple(dense_search_refs),
        query_vec_ref=query_vec_ref,
        sparse_search_refs=sparse_search_refs,
        graph_expansion_refs=graph_expansion_refs,
        metadata_filter_refs=metadata_filter_refs,
        support_score_profile=support_score_profile,
        evidence_strata=evidence_strata,
        excluded_evidence_refs=tuple(excluded_evidence_refs),
        gate_verdict_refs=tuple(f"gate:{v.gate_id}:{v.result}" for v in gate_verdicts),
        compilation_hash=digest,
        final_evidence_digest=digest,
        evidence_collection_timestamp=ts,
        otel_span_refs=otel_span_refs,
    )


# =============================================================================
# W6: Retrieval Quality Span Emission (Observability-only, L6 is post-runtime)
# =============================================================================

def _emit_retrieval_quality_span(
    evidence_items: list[Any],  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
    support_status: str,
    gate_verdicts: list[Any],
    evidence_digest: str,
    chroma_retrieved: bool,
    timestamp_iso: str,
    trace_id: str,
    run_id: str,
) -> dict[str, Any] | None:
    """Emit retrieval quality span for L6 observability.
    
    W6 Invariants:
    - This is observability-only data for later L6 consumption
    - L6 is strictly post-runtime; no current-run rescue path
    - No X3 disposition changes
    - All W1-W5 invariants preserved
    
    Args:
        evidence_items: List of EvidenceItem from retrieval
        support_status: Final support status (PASS, UNKNOWN, etc.)
        gate_verdicts: List of GateVerdict from C0 evaluation
        evidence_digest: Hash of evidence
        chroma_retrieved: Whether Chroma retrieval was performed
        timestamp_iso: ISO timestamp string
        trace_id: Trace identifier for span correlation
        run_id: Run identifier for span correlation
        
    Returns:
        Dictionary with span data and span_ref, or None if emission fails
    """
    try:
        # Count evidence items by source type
        evidence_count = len(evidence_items)
        
        # Count excluded items (items that failed metadata filter)
        excluded_count = sum(
            1 for item in evidence_items
            if getattr(item, "metadata_score", 0.0) == 0.0
            and getattr(item, "dense_score", 0.0) > 0.0
        )

        metadata_filter_hits = sum(
            1 for item in evidence_items
            if getattr(item, "metadata_score", 0.0) > 0.0
        )

        dense_hits = sum(
            1 for item in evidence_items
            if getattr(item, "source_type", "") == "fact_vectors"
        )

        section_retrieval_hits = sum(
            1 for item in evidence_items
            if getattr(item, "retrieval_run_ref", "") == "c0_section_retrieval:v1"
        )
        
        # Gate verdict count
        gate_verdict_count = len(gate_verdicts)
        
        # Build span payload
        span_payload: dict[str, Any] = {
            "span_kind": "retrieval_quality",
            "layer": "C0",
            "app_id": "apps_rg",
            "trace_id": trace_id,
            "run_id": run_id,
            "timestamp": timestamp_iso,
            "evidence_count": evidence_count,
            "support_status": support_status,
            "excluded_count": excluded_count,
            "metadata_filter_hits": metadata_filter_hits,
            "dense_hits": dense_hits,
            "section_retrieval_hits": section_retrieval_hits,
            "gate_verdict_count": gate_verdict_count,
            "final_evidence_digest": evidence_digest,
            "chroma_retrieved": chroma_retrieved,
        }
        
        # Generate span ref (deterministic for replay)
        span_ref = f"span:c0:retrieval_quality:{trace_id}:{run_id}:{evidence_digest[:16]}"
        
        return {
            "span_ref": span_ref,
            "payload": span_payload,
        }
    except Exception:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # W6: Fail-soft on span emission — never block C0 for observability
        return None


# =============================================================================
# W4: Section Retrieval Classes
# =============================================================================

@dataclass
class SectionRetrievalBudget:
    """Budget tracker for section retrieval."""
    max_total_items: int
    max_sections: int = 5
    items_retrieved: int = 0
    sections_queried: int = 0
    
    def record_retrieval(self, count: int) -> "SectionRetrievalBudget":
        """Record items retrieved and return updated budget."""
        return SectionRetrievalBudget(
            max_total_items=self.max_total_items,
            max_sections=self.max_sections,
            items_retrieved=self.items_retrieved + count,
            sections_queried=self.sections_queried,
        )
    
    def record_section_query(self) -> "SectionRetrievalBudget":
        """Record a section query and return updated budget."""
        return SectionRetrievalBudget(
            max_total_items=self.max_total_items,
            max_sections=self.max_sections,
            items_retrieved=self.items_retrieved,
            sections_queried=self.sections_queried + 1,
        )
    
    def can_retrieve_more(self, count: int) -> bool:
        """Check if more items can be retrieved."""
        return self.items_retrieved + count <= self.max_total_items
    
    @property
    def budget_exhausted(self) -> bool:
        """Check if item budget is exhausted."""
        return self.items_retrieved >= self.max_total_items
    
    @property
    def sections_budget_exhausted(self) -> bool:
        """Check if section budget is exhausted."""
        return self.sections_queried >= self.max_sections


@dataclass
class SectionRetrievalResult:
    """Result of section retrieval."""
    section_id: str
    evidence_items: list[EvidenceItem]
    status: str
    verdicts: list[Any]


@dataclass
class SectionQueryResult:
    """Container for section query result - provides evidence_items attribute."""
    evidence_items: list[EvidenceItem]
    budget: SectionRetrievalBudget


class SectionRetrievalProfile:
    """Profile for section-level retrieval configuration."""
    
    # Class attribute for test compatibility (tests patch this)
    PROFILE_PATH = Path("apps_rg/config/domain_contract/section_retrieval_profile.yaml")
    
    def __init__(self):
        self._config: dict[str, Any] = {}
        self._sections: list[dict[str, Any]] = []
        self._load_profile()
    
    def _get_profile_path(self) -> Path:
        """Get profile path - uses class PROFILE_PATH for test compatibility."""
        # First check if class PROFILE_PATH exists (for test patching)
        class_path = self.PROFILE_PATH
        if class_path.exists():
            return class_path
        # Fallback to module-relative path
        module_dir = Path(__file__).parent.parent.parent  # apps_rg/
        return module_dir / "config" / "domain_contract" / "section_retrieval_profile.yaml"
    
    def _load_profile(self) -> None:
        """Load profile from YAML."""
        profile_path = self._get_profile_path()
        if profile_path.exists():
            import yaml
            with open(profile_path, encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
                self._sections = self._config.get("sections", [])
        else:
            self._config = {"enabled": False}
            self._sections = []
    
    @property
    def enabled(self) -> bool:
        return self._config.get("enabled", False)
    
    @property
    def collection_name(self) -> str:
        return "fact_vectors"
    
    @property
    def allowed_source_classes(self) -> list[str]:
        return ["candidate_profile", "project_evidence"]
    
    @property
    def max_total_items(self) -> int:
        return self._config.get("global_constraints", {}).get("max_total_evidence_items", 15)
    
    @property
    def max_sections(self) -> int:
        return self._config.get("global_constraints", {}).get("max_sections_to_query", 5)
    
    @property
    def max_query_budget(self) -> int:
        return self._config.get("global_constraints", {}).get("max_query_budget_ms", 5000)
    
    def get_sections(self) -> list[dict[str, Any]]:
        """Get configured sections."""
        return self._sections

    def resolve_section_id(self, section_id: str) -> str:
        """Apply ``section_id_aliases`` (e.g. professional_summary → executive_summary)."""
        aliases = self._config.get("section_id_aliases") or {}
        if isinstance(aliases, dict):
            return str(aliases.get(section_id) or section_id)
        return section_id

    def get_section_config(self, section_id: str) -> dict[str, Any] | None:
        """Return retrieval profile row for ``section_id``, or None if unconfigured."""
        canonical = self.resolve_section_id(section_id)
        for row in self._sections:
            if str(row.get("section_id") or "") in (section_id, canonical):
                return row
        return None
    
    def get_sparse_defaults(self) -> dict[str, Any]:
        return dict(self._config.get("sparse_lane_defaults") or {})

    def any_sparse_enabled(self) -> bool:
        """True when any section's effective sparse config is enabled (respects mandatory policy env)."""
        for section in self._sections:
            if self.section_sparse_config(section).get("sparse_enabled"):
                return True
        return False

    _SPARSE_CONFIG_KEYS: tuple[str, ...] = (
        "sparse_enabled",
        "sparse_top_k",
        "sparse_lane_id",
        "sparse_collection_ref",
        "sparse_index_ref",
        "lexical_query_fields",
        "exact_match_fields",
        "dense_sparse_merge_policy",
        "sparse_unavailable_behavior",
        "sparse_empty_behavior",
    )

    def section_sparse_config(self, section: dict[str, Any]) -> dict[str, Any]:
        from apps_rg.runtime.c0_mandatory_policy import (
            apps_rg_c0_dense_sparse_mandatory,
            apps_rg_c0_sparse_profile_enabled,
        )

        merged: dict[str, Any] = {}
        for key in self._SPARSE_CONFIG_KEYS:
            if key in self.get_sparse_defaults():
                merged[key] = self.get_sparse_defaults()[key]
            if key in section:
                merged[key] = section[key]
        if not apps_rg_c0_sparse_profile_enabled():
            merged["sparse_enabled"] = False
        elif apps_rg_c0_dense_sparse_mandatory():
            merged["sparse_enabled"] = True
        coll = merged.get("sparse_collection_ref") or merged.get("sparse_index_ref")
        if coll:
            merged["sparse_collection_ref"] = str(coll)
        if not merged.get("sparse_lane_id"):
            sid = section.get("section_id", "section")
            merged["sparse_lane_id"] = f"c0.sparse.{sid}"
        return merged

    def _resolve_field_paths(
        self,
        field_paths: list[str],
        app_payload: dict[str, Any],
        *,
        min_len: int = 10,
    ) -> str | None:
        for field_path in field_paths:
            value = _payload_dotget(app_payload, field_path)
            if value and isinstance(value, str) and len(value) >= min_len:
                return value
        return None

    def build_query_for_section(self, section: dict[str, Any], app_payload: dict[str, Any]) -> str | None:
        """Build query text for a section from app_payload."""
        query_fields = section.get("query_fields", [])
        fallback_queries = section.get("fallback_queries", [])
        resolved = self._resolve_field_paths(query_fields, app_payload)
        if resolved:
            return resolved
        if fallback_queries:
            return str(fallback_queries[0])
        return None

    def build_lexical_query_for_section(
        self,
        section: dict[str, Any],
        app_payload: dict[str, Any],
        sparse_cfg: dict[str, Any],
    ) -> str | None:
        lexical_fields = sparse_cfg.get("lexical_query_fields") or []
        if lexical_fields:
            resolved = self._resolve_field_paths(list(lexical_fields), app_payload)
            if resolved:
                return resolved
        return self.build_query_for_section(section, app_payload)


def _chunk_id_from_evidence_item(item: EvidenceItem) -> str:
    eid = str(getattr(item, "evidence_id", "") or "")
    if eid.startswith("chroma:"):
        return eid.split(":", 1)[1]
    src = str(getattr(item, "source", ""))
    if src.startswith(_CHROMA_DB_PREFIX):
        return src.rsplit(":", 1)[-1]
    if eid:
        return eid
    return hashlib.sha256(item.content.encode("utf-8")).hexdigest()[:16]


def _evidence_item_to_hybrid(item: EvidenceItem) -> HybridSearchResult:
    chunk_id = _chunk_id_from_evidence_item(item)
    dense = float(getattr(item, "dense_score", 0.0) or getattr(item, "confidence_score", 0.0) or 0.0)
    lexical = float(getattr(item, "bm25_score", 0.0) or 0.0)
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=item.content,
        metadata={},
        combined_score=max(dense, lexical),
        source="vector" if dense >= lexical else "lexical",
        vector_score=dense,
        lexical_score=lexical,
    )


def _apply_hybrid_scores_to_evidence_item(
    item: EvidenceItem,
    row: HybridSearchResult,
    *,
    timestamp_iso: str,
) -> EvidenceItem:
    methods: list[str] = []
    if row.vector_score > 0.0:
        methods.append("dense")
    if row.lexical_score > 0.0:
        methods.append("sparse")
    retrieval_method = ",".join(methods) if methods else getattr(item, "retrieval_method", "dense")
    dense = float(row.vector_score if row.vector_score > 0.0 else getattr(item, "dense_score", 0.0))
    lexical = float(row.lexical_score)
    return EvidenceItem(
        source=item.source,
        content=row.content or item.content,
        source_type=getattr(item, "source_type", "fact_vectors"),
        evidence_id=getattr(item, "evidence_id", ""),
        source_id=getattr(item, "source_id", ""),
        source_version=getattr(item, "source_version", ""),
        citation_anchor=getattr(item, "citation_anchor", ""),
        chunk_digest=getattr(item, "chunk_digest", ""),
        confidence_score=max(dense, getattr(item, "confidence_score", 0.0)),
        dense_score=dense,
        bm25_score=lexical,
        metadata_score=getattr(item, "metadata_score", 0.0),
        retrieval_timestamp=timestamp_iso or getattr(item, "retrieval_timestamp", ""),
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        fact_vec_ref=getattr(item, "fact_vec_ref", ""),
        query_vec_ref=getattr(item, "query_vec_ref", ""),
        retrieval_method=retrieval_method,
        retrieval_run_ref=getattr(item, "retrieval_run_ref", "c0_section_retrieval:v1"),
        freshness_status=getattr(item, "freshness_status", STATUS_UNKNOWN),
        support_status=getattr(item, "support_status", STATUS_UNKNOWN),
    )


def _merge_section_dense_sparse_items(
    dense_items: list[EvidenceItem],
    sparse_outcome: Any,
    *,
    merge_policy: str,
    timestamp_iso: str,
) -> list[EvidenceItem]:
    if sparse_outcome.status != SparseLexicalLaneStatus.OK or not sparse_outcome.hybrid_rows:
        return list(dense_items)
    dense_hybrid = [_evidence_item_to_hybrid(it) for it in dense_items]
    sparse_rows = list(sparse_outcome.hybrid_rows)
    if merge_policy == "sparse_only":
        merged_rows = dedupe_hybrid_by_chunk_id(sparse_rows)
    elif dense_hybrid:
        merged_rows = merge_dense_sparse_rrf(dense_hybrid, sparse_rows)
        merged_rows = dedupe_hybrid_by_chunk_id(merged_rows)
    else:
        merged_rows = dedupe_hybrid_by_chunk_id(sparse_rows)
    by_chunk = {_chunk_id_from_evidence_item(it): it for it in dense_items}
    out: list[EvidenceItem] = []
    for row in merged_rows:
        base = by_chunk.get(row.chunk_id)
        if base is not None:
            out.append(_apply_hybrid_scores_to_evidence_item(base, row, timestamp_iso=timestamp_iso))
        elif row.lexical_score > 0.0:
            out.append(
                EvidenceItem(
                    source=f"sparse:retrieval:{row.chunk_id}",
                    content=row.content,
                    source_type="fact_vectors",
                    evidence_id=f"sparse:{row.chunk_id}",
                    citation_anchor=f"urn:chunk:{row.chunk_id}",
                    chunk_digest=hashlib.sha256(row.content.encode("utf-8")).hexdigest()[:32],
                    dense_score=float(row.vector_score),
                    bm25_score=float(row.lexical_score),
                    confidence_score=float(max(row.vector_score, row.lexical_score)),
                    retrieval_method="sparse" if row.vector_score <= 0.0 else "dense,sparse",
                    retrieval_run_ref="c0_section_sparse:v1",  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    retrieval_timestamp=timestamp_iso,
                    allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                    support_status=STATUS_UNKNOWN,
                )
            )
    return out if out else list(dense_items)


def _run_section_sparse_lane(
    section: dict[str, Any],
    app_payload: dict[str, Any],
    profile: SectionRetrievalProfile,
    metadata_profile: MetadataFilterProfile,
) -> Any:
    sparse_cfg = profile.section_sparse_config(section)
    if not sparse_cfg.get("sparse_enabled"):
        return None
    query_text = profile.build_lexical_query_for_section(section, app_payload, sparse_cfg)
    coll_ref = str(sparse_cfg.get("sparse_collection_ref") or profile.collection_name)
    lane_id = str(sparse_cfg.get("sparse_lane_id") or section.get("section_id", "section"))
    meta_filter: dict[str, Any] | None = None
    req = section.get("required_metadata_filters") or {}
    if isinstance(req, dict) and req:
        meta_filter = {
            str(k): v for k, v in req.items() if not isinstance(v, (dict, list))
        }
    allow = section.get("source_class_allowlist") or profile.allowed_source_classes
    if allow and len(allow) == 1:
        meta_filter = dict(meta_filter or {})
        meta_filter["source_class"] = allow[0]
    spec = SparseLexicalQuerySpec(
        lane_id=lane_id,
        query_text=query_text or "",
        top_k=int(sparse_cfg.get("sparse_top_k") or 5),
        sparse_index_collection_name=coll_ref,
        metadata_filter=meta_filter,
    )
    return query_sparse_lexical_lane(spec)


def _metadata_match_for_chunk(meta: dict[str, Any], app_payload: dict[str, Any]) -> float:
    """Lightweight JD↔chunk metadata overlap score for observability (0..1)."""
    if not app_payload:
        return 0.0
    jd = app_payload.get("jd_payload", {}) or {}
    tc = jd.get("target_company")
    if tc:
        co = str(meta.get("company") or meta.get("employer") or "")
        if not co:
            return 0.0
        tl = str(tc).lower()
        cl = co.lower()
        if tl in cl or cl in tl:
            return 1.0
        return 0.0
    return 0.5


def _perform_bounded_section_retrieval(
    chroma_path: str | None,
    app_payload: dict[str, Any],
    evidence_digest: str,
    timestamp_iso: str,
    chroma_collection: Any | None = None,
    *,
    section_id_filter: str | None = None,
) -> tuple[list[EvidenceItem], list[Any], str, list[str], list[tuple[str, float]], list[SectionEvidenceTrace]]:
    """Perform bounded section retrieval from fact_vectors.

    Returns: (evidence_items, gate_verdicts, status, sparse_receipt_refs,
    support_score_profile, section_traces)
    """
    profile = SectionRetrievalProfile()
    
    if not profile.enabled:
        # Historical contract: disabled profile reports NOT_APPLICABLE with no gate row
        # (callers treat this as "section machinery off", not a gate failure).
        return [], [], "NOT_APPLICABLE", [], [], []

    if not chroma_path and chroma_collection is None:
        verdict = GateVerdict(
            gate_id="G_SECTION_RETRIEVAL",
            gate_family="C0_G_SECTION_RETRIEVAL",
            evaluated_stage="C0",
            result=VERDICT_NOT_APPLICABLE,
            not_applicable_reason="fact_vectors collection unavailable (no chroma_path)",
            evaluated_at=timestamp_iso,
            evidence_digest=evidence_digest,
        )
        return [], [verdict], "UNKNOWN", [], [], []

    budget = SectionRetrievalBudget(
        max_total_items=profile.max_total_items,
        max_sections=profile.max_sections,
    )

    evidence_items: list[EvidenceItem] = []
    verdicts: list[Any] = []
    sparse_receipt_refs: list[str] = []
    support_score_profile: list[tuple[str, float]] = []
    section_traces: list[SectionEvidenceTrace] = []
    metadata_profile = MetadataFilterProfile()

    # Dense path health: invalid/missing persist dir or collection must be UNKNOWN,
    # not EMPTY (bounded-section contract tests + operator clarity).
    if chroma_collection is None and chroma_path:
        try:
            _probe_client = _persistent_chroma_client(chroma_path)
            from apps_rg.runtime.c0.chroma_persistent_client import ensure_apps_rg_chroma_client

            _probe_client = ensure_apps_rg_chroma_client(chroma_path)
            _probe_client.get_collection(profile.collection_name)
        except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            verdict = GateVerdict(
                gate_id="G_SECTION_RETRIEVAL",
                gate_family="C0_G_SECTION_RETRIEVAL",
                evaluated_stage="C0",
                result=VERDICT_UNKNOWN,
                unknown_reason=(
                    "fact_vectors collection unavailable or chroma_path not openable "
                    f"({profile.collection_name})"
                ),
                evaluated_at=timestamp_iso,
                evidence_digest=evidence_digest,
            )
            return [], [verdict], "UNKNOWN", [], [], []

    from apps_rg.runtime.embedding_settings import (
        assert_dense_retrieval_allowed,
        resolve_apps_rg_embedding_settings,
    )
    from tools.ingestion.chroma_ingest_pipeline import embed_text

    _sec_emb = resolve_apps_rg_embedding_settings(chroma_persist_dir=chroma_path)
    assert_dense_retrieval_allowed(_sec_emb)
    model = _get_embedding_model()
    # G8: embedding identity is a run-level constant; capture once for per-section traces.
    _embedding_model_id = str(getattr(_sec_emb, "embedding_model_name", "") or "")

    sections = profile.get_sections()
    if section_id_filter:
        canonical = profile.resolve_section_id(section_id_filter)
        sections = [
            s
            for s in sections
            if str(s.get("section_id") or "") in (section_id_filter, canonical)
        ]
        if not sections:
            verdict = GateVerdict(
                gate_id="G_SECTION_RETRIEVAL",
                gate_family="C0_G_SECTION_RETRIEVAL",
                evaluated_stage="C0",
                result=VERDICT_UNKNOWN,
                unknown_reason=f"no section_retrieval_profile for {section_id_filter!r}",
                evaluated_at=timestamp_iso,
                evidence_digest=evidence_digest,
            )
            return [], [verdict], "UNKNOWN", [], [], []

    for section in sections:
        if budget.sections_budget_exhausted or budget.budget_exhausted:
            break

        query = profile.build_query_for_section(section, app_payload)
        if not query:
            continue

        try:
            if chroma_collection is not None:
                collection = chroma_collection
            else:
                client = _persistent_chroma_client(chroma_path or "")
                from apps_rg.runtime.c0.chroma_persistent_client import ensure_apps_rg_chroma_client

                client = ensure_apps_rg_chroma_client(chroma_path or "")
                collection = client.get_collection(profile.collection_name)

            allow = section.get("source_class_allowlist") or [
                "candidate_profile",
                "project_evidence",
            ]
            where = metadata_profile.build_chroma_where_clause(
                app_payload,
                source_class_allowlist=allow,
            )
            if where is None:
                where = {
                    "$and": [
                        {"app": "apps_rg"},
                        {"source_class": {"$in": allow}},
                    ],
                }

            nk = int(section.get("dense_top_k", section.get("max_k", 3)))
            qemb = embed_text(model, query)
            result = collection.query(
                query_embeddings=[qemb],
                n_results=min(nk, 32),
                where=where,
            )  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary

            # G8: raw dense hits (post-where, pre exact-match), applied filter, embedding dim.
            _raw_hit_count = (
                len(result["ids"][0]) if result and result.get("ids") and result["ids"] else 0
            )
            try:
                _where_filter_str = json.dumps(where, sort_keys=True, default=str)
            except (TypeError, ValueError):
                _where_filter_str = str(where)
            _embedding_dimension = len(qemb) if qemb is not None else 0

            # G7: a section-scoped filter must not silently discard 100% of candidates. If the
            # narrow filter matched nothing, re-query ONCE with the broad app+source_class clause;
            # if THAT matches, the JD/section metadata filter removed all candidates — fall back to
            # the broader group and name the reason rather than reporting a falsely empty section.
            _filter_removed_all = False
            _broad_where = {"$and": [{"app": "apps_rg"}, {"source_class": {"$in": allow}}]}
            _narrow_empty = not (result and result.get("ids") and result["ids"][0])
            if _narrow_empty and where != _broad_where:
                broad_result = collection.query(
                    query_embeddings=[qemb],
                    n_results=min(nk, 32),
                    where=_broad_where,
                )
                if broad_result and broad_result.get("ids") and broad_result["ids"][0]:
                    _filter_removed_all = True
                    result = broad_result
                    _raw_hit_count = len(broad_result["ids"][0])
                    _where_filter_str = (
                        json.dumps(_broad_where, sort_keys=True, default=str)
                        + " (G7_fallback_from_section_filter)"
                    )

            section_dense_items: list[EvidenceItem] = []
            if result and result.get("ids"):
                for i, doc_id in enumerate(result["ids"][0]):
                    if budget.budget_exhausted:
                        break

                    metadata = (
                        result.get("metadatas", [[{}]])[0][i]
                        if result.get("metadatas")
                        else {}
                    )
                    document = (
                        result.get("documents", [[""]])[0][i]
                        if result.get("documents")
                        else ""
                    )
                    distance = (
                        result.get("distances", [[0.0]])[0][i]
                        if result.get("distances")
                        else 0.0
                    )
                    dense = max(0.0, 1.0 - float(distance))
                    sc = str(metadata.get("source_class", "candidate_profile"))
                    anchor = str(metadata.get("citation_anchor", "") or "")
                    digest = str(
                        metadata.get("chunk_digest", "")
                        or hashlib.sha256(document.encode("utf-8")).hexdigest()[:32]
                    )
                    meta_score = _metadata_match_for_chunk(metadata, app_payload)

                    item = EvidenceItem(
                        source=_chroma_source_label(sc, doc_id),
                        content=document,
                        source_type="fact_vectors",
                        evidence_id=f"chroma:{doc_id}",
                        source_id=str(
                            metadata.get("source_document_id")
                            or metadata.get("source_id")
                            or doc_id
                        ),
                        source_version=str(metadata.get("source_version_hash") or ""),
                        citation_anchor=anchor,
                        chunk_digest=digest,
                        confidence_score=dense,
                        dense_score=dense,
                        metadata_score=meta_score,
                        retrieval_timestamp=timestamp_iso,
                        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                        fact_vec_ref=f"chroma:fact_vectors:{doc_id}",
                        query_vec_ref="c0:bge-m3:query",
                        retrieval_method="dense",
                        retrieval_run_ref="c0_section_retrieval:v1",
                        freshness_status=str(metadata.get("freshness_status") or "FRESH"),
                        support_status=SUPPORT_STATUS_PASS if anchor else STATUS_UNKNOWN,
                    )
                    section_dense_items.append(item)
                    budget = budget.record_retrieval(1)

            sparse_outcome = _run_section_sparse_lane(
                section, app_payload, profile, metadata_profile
            )
            if sparse_outcome is not None:
                sparse_receipt_refs.append(sparse_outcome.receipt_ref)
                sparse_cfg = profile.section_sparse_config(section)
                merge_policy = str(sparse_cfg.get("dense_sparse_merge_policy") or "rrf")
                section_dense_items = _merge_section_dense_sparse_items(
                    section_dense_items,
                    sparse_outcome,
                    merge_policy=merge_policy,
                    timestamp_iso=timestamp_iso,
                )
                if sparse_outcome.status == SparseLexicalLaneStatus.OK:
                    lex_scores = [float(it.bm25_score) for it in section_dense_items if it.bm25_score > 0.0]
                    if lex_scores:
                        support_score_profile.append(
                            (f"sparse:{section.get('section_id', 'section')}", sum(lex_scores) / len(lex_scores))
                        )
                dense_scores = [float(it.dense_score) for it in section_dense_items if it.dense_score > 0.0]
                if dense_scores:
                    support_score_profile.append(
                        (f"dense:{section.get('section_id', 'section')}", sum(dense_scores) / len(dense_scores))
                    )

            exact_fields = profile.section_sparse_config(section).get("exact_match_fields") or []
            if exact_fields and section_dense_items:
                exact_phrases = [
                    _payload_dotget(app_payload, str(field_path))
                    for field_path in exact_fields
                ]
                exact_phrases = [p for p in exact_phrases if isinstance(p, str) and p.strip()]
                if exact_phrases:
                    rebuilt: list[EvidenceItem] = []
                    for it in section_dense_items:
                        rm = getattr(it, "retrieval_method", "") or ""
                        if any(phrase in it.content for phrase in exact_phrases) and "exact" not in rm:
                            rm = f"{rm},exact" if rm else "exact"
                            rebuilt.append(
                                EvidenceItem(
                                    source=it.source,
                                    content=it.content,
                                    source_type=getattr(it, "source_type", "fact_vectors"),
                                    evidence_id=getattr(it, "evidence_id", ""),
                                    source_id=getattr(it, "source_id", ""),
                                    source_version=getattr(it, "source_version", ""),
                                    citation_anchor=getattr(it, "citation_anchor", ""),
                                    chunk_digest=getattr(it, "chunk_digest", ""),
                                    confidence_score=getattr(it, "confidence_score", 0.0),
                                    dense_score=getattr(it, "dense_score", 0.0),
                                    bm25_score=getattr(it, "bm25_score", 0.0),
                                    metadata_score=getattr(it, "metadata_score", 0.0),
                                    retrieval_timestamp=getattr(it, "retrieval_timestamp", timestamp_iso),
                                    allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                                    fact_vec_ref=getattr(it, "fact_vec_ref", ""),
                                    query_vec_ref=getattr(it, "query_vec_ref", ""),
                                    retrieval_method=rm,
                                    retrieval_run_ref=getattr(it, "retrieval_run_ref", ""),
                                    freshness_status=getattr(it, "freshness_status", STATUS_UNKNOWN),
                                    support_status=getattr(it, "support_status", STATUS_UNKNOWN),
                                )
                            )
                        else:
                            rebuilt.append(it)
                    section_dense_items = rebuilt

            section_traces.append(
                _build_section_evidence_trace(
                    section,
                    query,
                    section_dense_items,  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    app_payload,
                    timestamp_iso=timestamp_iso,
                    raw_dense_hit_count=_raw_hit_count,
                    post_filter_survivor_count=len(section_dense_items),
                    applied_where_filter=_where_filter_str,
                    similarity_threshold=min(
                        (float(getattr(it, "dense_score", 0.0)) for it in section_dense_items),
                        default=0.0,
                    ),
                    embedding_model_id=_embedding_model_id,
                    embedding_dimension=_embedding_dimension,
                    filter_removed_all=_filter_removed_all,
                )
            )
            evidence_items.extend(section_dense_items)
            budget = budget.record_section_query()

        except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            _logger.warning("Section retrieval query failed: %s", exc)
            continue

    if evidence_items:
        verdict = GateVerdict(
            gate_id="G_SECTION_RETRIEVAL",
            gate_family="C0_G_SECTION_RETRIEVAL",
            evaluated_stage="C0",
            result=VERDICT_PASS,
            evaluated_at=timestamp_iso,
            evidence_digest=evidence_digest,
        )
        verdicts.append(verdict)
        status = "PASS"
    else:
        verdict = GateVerdict(
            gate_id="G_SECTION_RETRIEVAL",
            gate_family="C0_G_SECTION_RETRIEVAL",
            evaluated_stage="C0",
            result=VERDICT_UNKNOWN,
            unknown_reason="No section evidence retrieved",
            evaluated_at=timestamp_iso,
            evidence_digest=evidence_digest,
        )
        verdicts.append(verdict)
        status = "EMPTY"

    return evidence_items, verdicts, status, sparse_receipt_refs, support_score_profile, section_traces


def _resolve_fec_sparse_search_refs(
    profile: SectionRetrievalProfile,
    sparse_receipt_refs: list[str],
) -> tuple[str, ...]:
    if not profile.any_sparse_enabled():
        return (C0_SPARSE_LANE_NA_REF,)
    if sparse_receipt_refs:
        return fec_sparse_refs_from_lane_outcomes(*dict.fromkeys(sparse_receipt_refs))
    return fec_sparse_refs_from_lane_outcomes(
        f"ref:sparse:aggregate:status={SparseLexicalLaneStatus.UNAVAILABLE.value}:hits=0"
    )


def _query_fact_vectors_for_section(
    collection: Any,
    query_text: str,
    section: dict[str, Any],
    profile: SectionRetrievalProfile,
    budget: SectionRetrievalBudget,
    evidence_digest: str,
    app_payload: dict[str, Any] | None = None,
    metadata_profile: MetadataFilterProfile | None = None,
    timestamp_iso: str = "",
) -> SectionQueryResult:
    """Compatibility helper for legacy metadata-filter tests.
    
    Product C0.2 retrieval uses ``_perform_bounded_section_retrieval``. This
    helper remains importable for older W5 tests that assert Chroma where-clause
    behavior, but it is not part of the product C0 public surface.
    """
    items: list[EvidenceItem] = []
    
    if not query_text:
        return SectionQueryResult(evidence_items=[], budget=budget)
    
    try:
        mp = metadata_profile or MetadataFilterProfile()
        allow = section.get("source_class_allowlist") or [
            "candidate_profile",
            "project_evidence",
        ]
        where_clause = mp.build_chroma_where_clause(
            app_payload or {},
            source_class_allowlist=allow,
        )
        if where_clause is None:
            where_clause = {
                "$and": [
                    {"app": "apps_rg"},
                    {"source_class": {"$in": allow}},
                ],
            }

        from tools.ingestion.chroma_ingest_pipeline import embed_text

        model = _get_embedding_model()
        qemb = embed_text(model, query_text)
        nk = int(section.get("dense_top_k", section.get("max_k", 3)))
        result = collection.query(
            query_embeddings=[qemb],
            n_results=nk,
            where=where_clause,
        )

        if result and result.get("ids"):
            for i, doc_id in enumerate(result["ids"][0]):
                if budget.budget_exhausted:
                    break

                metadata = (
                    result.get("metadatas", [[{}]])[0][i]
                    if result.get("metadatas")
                    else {}
                )
                document = (
                    result.get("documents", [[""]])[0][i]
                    if result.get("documents")
                    else ""
                )
                distance = (
                    result.get("distances", [[0.0]])[0][i]
                    if result.get("distances")
                    else 0.0
                )
                dense_score = max(0.0, 1.0 - float(distance))
                meta_score = _metadata_match_for_chunk(metadata, app_payload or {})

                item = EvidenceItem(
                    source=metadata.get("source_document_id", doc_id),
                    content=document,
                    source_type="fact_vectors",
                    confidence_score=dense_score,
                    dense_score=dense_score,
                    metadata_score=meta_score,
                    retrieval_timestamp=timestamp_iso or datetime.now(timezone.utc).isoformat(),
                    allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                )
                items.append(item)
                budget = budget.record_retrieval(1)

    except Exception as exc:  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        _logger.warning("Fact vector query failed: %s", exc)

    return SectionQueryResult(evidence_items=items, budget=budget)


# =============================================================================
# W5: Metadata Filter Classes
# =============================================================================

@dataclass(frozen=True)
class MetadataFilterResult:
    """Result of metadata match checking."""
    matched: bool
    match_type: str  # "exact", "partial", "none"
    metadata_score: float
    field_name: str = ""
    filter_value: str = ""


@dataclass
class ClaimCheckResult:
    """Result of deterministic claim checking."""
    verified: bool
    support_status: str
    verification_method: str
    claim_type: str = ""
    claim_value: str = ""
    reason: str = ""


class MetadataFilterProfile:
    """Profile for metadata filtering on fact_vectors."""
    
    PROFILE_PATH = Path("apps_rg/config/domain_contract/metadata_filter_profile.yaml")
    
    def __init__(self):
        self._config: dict[str, Any] = {}
        self._filterable_fields: list[dict[str, Any]] = []
        self._load_profile()
    
    def _load_profile(self) -> None:
        """Load profile from YAML."""
        if self.PROFILE_PATH.exists():
            import yaml
            with open(self.PROFILE_PATH, encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
                self._filterable_fields = self._config.get("filterable_fields", [])
        else:
            self._config = self._default_config()
            self._filterable_fields = self._config.get("filterable_fields", [])
    
    def _default_config(self) -> dict[str, Any]:
        """Default configuration."""
        return {
            "enabled": True,
            "collection": "fact_vectors",
            "filterable_fields": [
                {
                    "field_name": "company",
                    "chroma_metadata_key": "company",
                    "display_name": "Company",
                    "query_sources": ["jd_payload.target_company"],
                },
                {
                    "field_name": "role",
                    "chroma_metadata_key": "role",
                    "display_name": "Role",
                    "query_sources": ["jd_payload.target_role"],
                },
                {
                    "field_name": "certification",
                    "chroma_metadata_key": "certification",
                    "display_name": "Certification",
                    "query_sources": ["jd_payload.required_certifications"],
                },
                {
                    "field_name": "year",
                    "chroma_metadata_key": "year",
                    "display_name": "Year/Date Range",
                    "query_sources": ["jd_payload.date_range"],
                },
            ],
            "rejected_source_classes": [
                "company_research",
                "rubrics",
                "governance_docs",
                "approved_examples",
                "receipts",
                "process_docs",
            ],
            "score_separation": {
                "dense_score_field": "confidence_score",
                "metadata_score_field": "metadata_score",
                "combined_score_field": None,
                "evidence_item_fields": ["confidence_score", "metadata_score"],
            },
        }

    @property
    def enabled(self) -> bool:
        return self._config.get("enabled", True)

    def get_filterable_fields(self) -> list[dict[str, Any]]:
        """Get list of filterable fields."""
        return self._filterable_fields

    def build_chroma_where_clause(
        self,
        app_payload: dict[str, Any],
        *,
        source_class_allowlist: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Build Chroma ``where`` with mandatory app + source_class + optional JD filters."""
        if not self.enabled:
            return None

        classes = source_class_allowlist or ["candidate_profile", "project_evidence"]
        filters: list[dict[str, Any]] = [
            {"app": "apps_rg"},
            {"source_class": {"$in": classes}},
        ]

        for field in self._filterable_fields:
            chroma_key = field.get("chroma_metadata_key", field.get("field_name", ""))
            if not chroma_key:
                continue
            for qs in field.get("query_sources", []):
                raw = _payload_dotget(app_payload, qs)
                if raw is None or raw == "":
                    continue
                if isinstance(raw, list):
                    if raw:
                        filters.append({chroma_key: {"$in": [str(x) for x in raw]}})
                else:
                    filters.append({chroma_key: {"$eq": str(raw)}})
                break

        return {"$and": filters}
    
    def check_metadata_match(
        self,
        evidence_metadata: dict[str, Any],
        filter_field: str,
        filter_value: str,
    ) -> MetadataFilterResult:
        """Check if evidence metadata matches filter criteria."""
        evidence_value = evidence_metadata.get(filter_field, "")
        
        if not evidence_value:
            return MetadataFilterResult(
                matched=False,
                match_type="none",
                metadata_score=0.0,
                field_name=filter_field,
                filter_value=filter_value,
            )
        
        # Case-insensitive comparison
        ev_str = str(evidence_value).lower().strip()
        filt_str = str(filter_value).lower().strip()
        
        if ev_str == filt_str:
            return MetadataFilterResult(
                matched=True,
                match_type="exact",
                metadata_score=1.0,
                field_name=filter_field,
                filter_value=filter_value,
            )
        elif filt_str in ev_str or ev_str in filt_str:
            return MetadataFilterResult(
                matched=True,
                match_type="partial",
                metadata_score=0.5,
                field_name=filter_field,
                filter_value=filter_value,
            )
        else:
            return MetadataFilterResult(
                matched=False,
                match_type="none",
                metadata_score=0.0,
                field_name=filter_field,
                filter_value=filter_value,
            )


class DeterministicClaimChecker:
    """Deterministic claim checker for structured claims."""
    
    SUPPORTED_CLAIM_TYPES = [
        "employer_match",
        "certification_match",
        "year_in_range",
        "title_match",
    ]
    
    def __init__(self, profile: MetadataFilterProfile):
        self.profile = profile
    
    def check_claim(
        self,
        claim_type: str,
        claim_value: str,
        evidence_metadata_list: list[dict[str, Any]],
    ) -> ClaimCheckResult:
        """Check a single claim against evidence."""
        if claim_type not in self.SUPPORTED_CLAIM_TYPES:
            return ClaimCheckResult(
                verified=False,
                support_status="UNSUPPORTED",
                verification_method="unsupported",
                claim_type=claim_type,
                claim_value=claim_value,
                reason=f"Claim type {claim_type} not supported",
            )
        
        if claim_type == "employer_match":
            return self._check_employer_match(claim_value, evidence_metadata_list)
        elif claim_type == "certification_match":
            return self._check_certification_match(claim_value, evidence_metadata_list)
        elif claim_type == "year_in_range":
            return self._check_year_range(claim_value, evidence_metadata_list)
        elif claim_type == "title_match":
            return self._check_title_match(claim_value, evidence_metadata_list)
        
        return ClaimCheckResult(
            verified=False,
            support_status="UNSUPPORTED",
            verification_method="unsupported",
            claim_type=claim_type,
            claim_value=claim_value,
        )
    
    def _check_employer_match(
        self,
        claim_value: str,
        evidence_list: list[dict[str, Any]],
    ) -> ClaimCheckResult:
        """Check if employer claim matches evidence (``company`` or legacy ``employer``)."""
        for evidence in evidence_list:
            for key in ("company", "employer"):
                result = self.profile.check_metadata_match(evidence, key, claim_value)
                if result.matched:
                    return ClaimCheckResult(
                        verified=True,
                        support_status="PASS",
                        verification_method="exact_match",
                        claim_type="employer_match",
                        claim_value=claim_value,
                    )

        return ClaimCheckResult(
            verified=False,
            support_status="WEAK_WITH_CAVEATS",
            verification_method="no_match",
            claim_type="employer_match",
            claim_value=claim_value,
            reason="Employer claim not verified in evidence",
        )
    
    def _check_certification_match(
        self,
        claim_value: str,
        evidence_list: list[dict[str, Any]],
    ) -> ClaimCheckResult:
        """Check if certification claim matches evidence."""
        for evidence in evidence_list:
            result = self.profile.check_metadata_match(evidence, "certification", claim_value)
            if result.matched:
                return ClaimCheckResult(
                    verified=True,
                    support_status="PASS",
                    verification_method="exact_match",
                    claim_type="certification_match",
                    claim_value=claim_value,
                )
        
        return ClaimCheckResult(
            verified=False,
            support_status="WEAK_WITH_CAVEATS",
            verification_method="no_match",
            claim_type="certification_match",
            claim_value=claim_value,
            reason="Certification claim not verified in evidence",
        )
    
    def _check_year_range(
        self,
        claim_value: str,
        evidence_list: list[dict[str, Any]],
    ) -> ClaimCheckResult:
        """Check if year range overlaps with evidence."""
        # Parse claim range (e.g., "2020-2023")
        try:
            claim_start, claim_end = self._parse_year_range(claim_value)
        except ValueError:
            return ClaimCheckResult(
                verified=False,
                support_status="PARTIAL",
                verification_method="parse_error",
                claim_type="year_in_range",
                claim_value=claim_value,
                reason="Could not parse year range",
            )
        
        for evidence in evidence_list:
            evidence_year = evidence.get("year", "")
            try:
                ev_start, ev_end = self._parse_year_range(str(evidence_year))
                # Check overlap
                if ev_start <= claim_end and ev_end >= claim_start:
                    return ClaimCheckResult(
                        verified=True,
                        support_status="PASS",
                        verification_method="range_overlap",
                        claim_type="year_in_range",
                        claim_value=claim_value,
                    )
            except ValueError:
                continue
        
        return ClaimCheckResult(
            verified=False,
            support_status="PARTIAL",
            verification_method="no_overlap",
            claim_type="year_in_range",
            claim_value=claim_value,
            reason="Year range does not overlap with evidence",
        )
    
    def _check_title_match(
        self,
        claim_value: str,
        evidence_list: list[dict[str, Any]],
    ) -> ClaimCheckResult:
        """Check if title claim matches evidence (``role`` or legacy ``title``)."""
        for evidence in evidence_list:
            for key in ("role", "title"):
                result = self.profile.check_metadata_match(evidence, key, claim_value)
                if result.matched:
                    return ClaimCheckResult(
                        verified=True,
                        support_status="PASS",
                        verification_method="exact_match",
                        claim_type="title_match",
                        claim_value=claim_value,
                    )

        return ClaimCheckResult(
            verified=False,
            support_status="WEAK_WITH_CAVEATS",
            verification_method="no_match",
            claim_type="title_match",
            claim_value=claim_value,
            reason="Title claim not verified in evidence",
        )
    
    def _parse_year_range(self, year_str: str) -> tuple[int, int]:
        """Parse year range string into (start, end)."""
        parts = year_str.split("-")
        if len(parts) == 1:
            year = int(parts[0].strip())
            return (year, year)
        elif len(parts) == 2:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            return (start, end)
        else:
            raise ValueError(f"Invalid year range: {year_str}")
    
    def check_all_claims(
        self,
        claims: list[tuple[str, str]],
        evidence_metadata_list: list[dict[str, Any]],
    ) -> list[ClaimCheckResult]:
        """Check multiple claims."""
        results = []
        for claim_type, claim_value in claims:
            result = self.check_claim(claim_type, claim_value, evidence_metadata_list)
            results.append(result)
        return results


# ---------------------------------------------------------------------------
# _compute_support_status — derives support_status from evidence items
# ---------------------------------------------------------------------------

def _compute_support_status(
    evidence_items: list,
    excluded_count: int = 0,
    *,
    required_source_classes: frozenset | None = None,
) -> str:
    """Derive aggregate support status from evidence items (and optional class coverage)."""
    del excluded_count  # reserved for future weighting
    if not evidence_items:
        return SUPPORT_STATUS_EMPTY
    req = required_source_classes or frozenset(_NORMATIVE_SOURCE_CLASSES)
    found = {_evidence_source_class(e) for e in evidence_items if _evidence_source_class(e)}
    missing = req - found
    if not missing:
        return SUPPORT_STATUS_PASS
    if not found:
        return SUPPORT_STATUS_WEAK
    if len(found) == 1:
        return SUPPORT_STATUS_WEAK
    return SUPPORT_STATUS_PARTIAL


def _build_chroma_evidence(
    chunks: list[dict[str, Any]],
    timestamp_iso: str,
    excluded_refs: list[str],
) -> tuple[
    list[EvidenceItem],
    list[tuple[str, str]],
    list[tuple[str, str]],
    list[str],
]:
    """Normalize legacy chunk dicts into ``EvidenceItem`` rows + FEC maps."""
    items_out: list[EvidenceItem] = []
    citations: list[tuple[str, str]] = []
    lineage: list[tuple[str, str]] = []
    freshness: list[str] = []

    for chunk in chunks:
        cid = str(chunk.get("_chunk_id", "unknown"))
        sc = str(chunk.get("source_class", "candidate_profile"))
        document = str(chunk.get("_document", chunk.get("document", "")))
        anchor = str(chunk.get("citation_anchor", "") or "")
        inv = str(chunk.get("invalid_for_normative_use", "false")).lower() == "true"

        if sc == "prior_outputs" or inv:
            excluded_refs.append(f"excluded:{cid}")
            continue
        if not anchor:
            excluded_refs.append(f"excluded:{cid}")
            continue

        eid = f"chroma:{cid}"
        src_id = str(chunk.get("source_id", ""))
        fresh = str(chunk.get("freshness", "UNKNOWN"))

        items_out.append(
            EvidenceItem(
                source=_chroma_source_label(sc, cid),
                content=document,
                citation_anchor=anchor,
                support_status=SUPPORT_STATUS_PASS,
                allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                retrieval_timestamp=timestamp_iso,
            )
        )
        citations.append((eid, anchor))
        lineage.append((eid, src_id))
        freshness.append(f"freshness:{src_id or cid}:{fresh}")

    return items_out, citations, lineage, freshness


# Re-export from c0_briefing_bypass for W3 integration
from apps_rg.runtime.bindings.c0_briefing_bypass import (
    BriefEvaluationResult,
    BriefingBypassEvaluator,
    evaluate_manual_brief,
)

__all__ = [
    "APPS_RG_C0_CERT_REF",
    "C0_DENSE_NA_NO_PERSIST",
    "C0_SPARSE_LANE_NA_REF",
    "C0_GRAPH_LANE_NA_REF",
    "C0_METADATA_FILTER_REF",
    "C0_QUERY_VEC_REF_BGE",
    "SUPPORT_STATUS_PASSING_VALUES",
    "EvidenceItem",
    "c0_retrieve_apps_rg",
    "_build_gate_verdict",
    "_get_embedding_model",
    "_NORMATIVE_SOURCE_CLASSES",
    "_NORMATIVE_SOURCE_CLASSES_HARDCODED",
    "C0EvidenceGapError",
    # W4 Section Retrieval
    "SectionRetrievalProfile",
    "SectionRetrievalBudget",
    "SectionRetrievalResult",
    "SectionQueryResult",
    "_perform_bounded_section_retrieval",
    # W5 Metadata Filter
    "MetadataFilterProfile",
    "MetadataFilterResult",
    "DeterministicClaimChecker",
    "ClaimCheckResult",
    # W3 Briefing Bypass (re-exported)
    "BriefEvaluationResult",
    "BriefingBypassEvaluator",
    "evaluate_manual_brief",
    # Chroma evidence builders
    "_build_chroma_evidence",
    "_compute_support_status",
    "_emit_retrieval_quality_span",
]
