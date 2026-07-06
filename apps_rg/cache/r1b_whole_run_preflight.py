"""W9 — whole-run R1B preflight (HistoricalIntentRecord lookup before generation)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    C0_FACT_VECTORS_COLLECTION,
    R1B_CHUNK_REUSE_AUTHORITY,
    R1B_NOT_C0_FACT_VECTORS,
    R1B_REUSE_AUTHORITY_SCOPE,
    R1B_SECTION_REUSE_AUTHORITY,
    r1b_reuse_authority_policy,
)
from apps_rg.cache.r1b_retrieval import R1BLookupHit, hit_to_probe_dict, lookup_r1b_role_target_run
from apps_rg.cache.r1b_retrieval import lookup_r1b_with_compatibility_report
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root

# Canonical whole-run cache preflight order (R1A handled in apps_rg/__main__.py).
PREFLIGHT_ORDER: tuple[str, ...] = (
    "R1A_EXACT_CACHE",
    "R1B_SEMANTIC_ROLE_TARGET_RUN",
    "NORMAL_GENERATION",
)

ROUTE_R1B = "R1B_SEMANTIC_CACHE"
PACKET_TYPE = "apps_rg.R1BCacheReturnPacket"


@dataclass
class WholeRunR1BPreflightResult:
    outcome: str  # r1b_hit | r1b_miss | r1b_inadmissible_only
    r1b_hit: bool
    lookup_anchor: str
    cache_grain: str
    probe: dict[str, Any] | None = None
    terminal_packet: dict[str, Any] | None = None
    child_chunk_inspection: dict[str, Any] | None = None
    compatibility_report: list[dict[str, Any]] = field(default_factory=list)
    generation_required: bool = True
    c0_fact_vectors_consulted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "r1b_hit": self.r1b_hit,
            "lookup_anchor": self.lookup_anchor,
            "cache_grain": self.cache_grain,
            "preflight_order": list(PREFLIGHT_ORDER),
            "probe": self.probe,
            "terminal_packet": self.terminal_packet,
            "child_chunk_inspection": self.child_chunk_inspection,
            "compatibility_report": self.compatibility_report,
            "generation_required": self.generation_required,
            "c0_fact_vectors_consulted": self.c0_fact_vectors_consulted,
            "not_c0_fact_vectors": True,
            "r1b_vs_c0": R1B_NOT_C0_FACT_VECTORS,
            "c0_collection_excluded": C0_FACT_VECTORS_COLLECTION,
            "reuse_scope": R1B_REUSE_AUTHORITY_SCOPE,
            "reuse_authority_policy": r1b_reuse_authority_policy(),
            "section_level_loose_reuse": False,
            "section_level_semantic_reuse_authority": R1B_SECTION_REUSE_AUTHORITY,
            "section_level_lane_skip_authorized": False,
            "child_chunk_reuse_authority": R1B_CHUNK_REUSE_AUTHORITY,
            "exit_bypassed": False,
        }


def _child_chunk_inspection_receipt(hit: R1BLookupHit) -> dict[str, Any]:
    """Prove chunks were loaded for compatibility only — not independent lookup keys."""
    inspected: list[dict[str, Any]] = []
    for ch in hit.chunks:
        inspected.append(
            {
                "chunk_id": ch.chunk_id,
                "chunk_type": ch.chunk_type,
                "section_id": ch.section_id,
                "parent_intent_record_id": ch.parent_intent_record_id,
                "independent_cache_identity": ch.to_dict().get("independent_cache_identity", False),
                "used_as_lookup_key": False,
                "reuse_authority": R1B_CHUNK_REUSE_AUTHORITY,
                "section_level_lane_skip_authorized": False,
            }
        )
    return {
        "parent_intent_record_id": hit.record.record_id,
        "chunks_inspected_count": len(inspected),
        "chunks_inspected": inspected,
        "independent_chunk_lookup_performed": False,
        "lookup_anchor": "HistoricalIntentRecord.request_intent_vector",
        "reuse_authority_policy": r1b_reuse_authority_policy(),
        "section_level_lane_skip_authorized": False,
        "child_chunk_reuse_authority": R1B_CHUNK_REUSE_AUTHORITY,
    }


def build_r1b_cache_return_packet(
    hit: R1BLookupHit,
    *,
    raw_request: dict[str, Any],
    prompt_profile_hash: str = "",
    gate_profile_hash: str = "",
) -> dict[str, Any]:
    """Terminal cache-return packet for Exit review (apps_rg-local; no L2 execution)."""
    probe = hit_to_probe_dict(hit)
    return {
        "packet_type": PACKET_TYPE,
        "route_id": ROUTE_R1B,
        "cache_grain": CACHE_GRAIN_ROLE_TARGET_RUN,
        "request_id": str(raw_request.get("request_id") or hit.record.source_run_id),
        "run_id": hit.record.source_run_id,
        "parent_intent_record_id": hit.record.record_id,
        "lookup_anchor": probe["lookup_anchor"],
        "similarity": hit.similarity,
        "reason_codes": [
            "r1b_semantic_hit",
            "role_target_run_grain",
            "compatibility_passed",
            "w8_post_exit_admissible_record",
        ],
        "prompt_profile_hash": prompt_profile_hash or hit.record.prompt_profile_hash,
        "gate_profile_hash": gate_profile_hash or hit.record.gate_profile_hash,
        "x3_disposition": hit.record.x3_disposition,
        "proof_eligible": hit.record.proof_eligible,
        "exit_review_required": True,
        "no_l2_execution_assertion": True,
        "no_generation_pipeline": True,
        "exit_bypassed": False,
        "not_c0_fact_vectors": True,
        "c0_collection_excluded": C0_FACT_VECTORS_COLLECTION,
        "reuse_scope": R1B_REUSE_AUTHORITY_SCOPE,
        "reuse_authority_policy": r1b_reuse_authority_policy(),
        "section_level_semantic_reuse_authority": R1B_SECTION_REUSE_AUTHORITY,
        "section_level_lane_skip_authorized": False,
        "child_chunk_reuse_authority": R1B_CHUNK_REUSE_AUTHORITY,
        "child_chunk_count": len(hit.chunks),
        "compatibility_checks": hit.verdict.checks,
    }


def execute_whole_run_r1b_preflight(
    *,
    raw_request: dict[str, Any],
    runs_dir: str | Path | None = None,
    similarity_threshold: float | None = None,
    prompt_profile_hash: str = "",
    gate_profile_hash: str = "",
) -> WholeRunR1BPreflightResult:
    """R1B whole-run lookup: intent vectors only; miss/inadmissible → generation fallthrough."""
    from apps_rg.cache.r1b_adapter import _get_similarity_threshold
    from apps_rg.cache.r1b_derived_index import lookup_r1b_via_derived_index

    root = Path(runs_dir) if runs_dir else default_store_root()
    threshold = float(similarity_threshold if similarity_threshold is not None else _get_similarity_threshold())
    ph = str(prompt_profile_hash or raw_request.get("prompt_profile_hash") or "")
    gh = str(gate_profile_hash or raw_request.get("gate_profile_hash") or "")

    hit, report = lookup_r1b_via_derived_index(
        raw_request,
        projection_root=root,
        similarity_threshold=threshold,
        query_prompt_hash=ph,
        query_gate_hash=gh,
    )

    if hit is None:
        projection_unavailable = any(
            "derived_index_unavailable" in (row.get("reason_codes") or [])
            for row in report
        )
        inadmissible_only = any(
            row.get("similarity", 0) >= threshold and not row.get("admissible")
            for row in report
        )
        return WholeRunR1BPreflightResult(
            outcome=(
                "r1b_read_projection_unavailable"
                if projection_unavailable
                else "r1b_inadmissible_only" if inadmissible_only else "r1b_miss"
            ),
            r1b_hit=False,
            lookup_anchor="HistoricalIntentRecord.request_intent_vector",
            cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
            compatibility_report=report,
            generation_required=True,
            c0_fact_vectors_consulted=False,
        )

    probe = hit_to_probe_dict(hit)
    terminal = build_r1b_cache_return_packet(
        hit,
        raw_request=raw_request,
        prompt_profile_hash=ph,
        gate_profile_hash=gh,
    )
    inspection = _child_chunk_inspection_receipt(hit)
    return WholeRunR1BPreflightResult(
        outcome="r1b_hit",
        r1b_hit=True,
        lookup_anchor=probe["lookup_anchor"],
        cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
        probe=probe,
        terminal_packet=terminal,
        child_chunk_inspection=inspection,
        compatibility_report=report,
        generation_required=False,
        c0_fact_vectors_consulted=False,
    )


def write_r1b_preflight_receipt(path: Path, result: WholeRunR1BPreflightResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_r1b_whole_run_preflight(
    *,
    raw_request: dict[str, Any],
    runs_dir: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any] | None:
    """Adapter-facing whole-run R1B check; returns probe dict on hit else None."""
    result = execute_whole_run_r1b_preflight(
        raw_request=raw_request,
        runs_dir=runs_dir,
        similarity_threshold=kwargs.get("similarity_threshold"),
        prompt_profile_hash=str(kwargs.get("prompt_profile_hash") or ""),
        gate_profile_hash=str(kwargs.get("gate_profile_hash") or ""),
    )
    if not result.r1b_hit or result.probe is None:
        return None
    merged = dict(result.probe)
    merged["terminal_packet"] = result.terminal_packet
    merged["child_chunk_inspection"] = result.child_chunk_inspection
    merged["preflight_order"] = list(PREFLIGHT_ORDER)
    return merged


__all__ = [
    "PACKET_TYPE",
    "PREFLIGHT_ORDER",
    "ROUTE_R1B",
    "WholeRunR1BPreflightResult",
    "build_r1b_cache_return_packet",
    "check_r1b_whole_run_preflight",
    "execute_whole_run_r1b_preflight",
    "write_r1b_preflight_receipt",
]
