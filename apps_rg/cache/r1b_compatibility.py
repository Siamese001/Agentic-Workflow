"""R1B candidate admissibility — metadata + child chunks before reuse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.cache.r1b_constants import (
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
    NON_ADMISSIBLE_RUNTIME_STATUSES,
    SECTION_CHUNK_TYPES,
    X3_FINISH_ALLOWED,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk


@dataclass(frozen=True)
class CompatibilityVerdict:
    admissible: bool
    reason: str
    checks: dict[str, bool]


def _has_digest(val: str) -> bool:
    return bool(str(val or "").strip())


def assess_intent_record_admissibility(
    record: HistoricalIntentRecord,
    *,
    chunks: list[HistoricalOutputChunk],
    runtime_generation_status: str = "",
) -> CompatibilityVerdict:
    checks: dict[str, bool] = {}
    x3 = str(record.x3_disposition or "").strip().upper()
    checks["x3_allows_finish"] = x3 in X3_FINISH_ALLOWED
    checks["proof_eligible"] = bool(record.proof_eligible)
    checks["not_mock_runtime"] = str(runtime_generation_status or "").strip() not in NON_ADMISSIBLE_RUNTIME_STATUSES
    checks["jd_digest_present"] = _has_digest(record.jd_digest)
    checks["base_resume_digest_present"] = _has_digest(record.base_resume_digest)
    checks["prompt_profile_hash_present"] = _has_digest(record.prompt_profile_hash)
    checks["gate_profile_hash_present"] = _has_digest(record.gate_profile_hash)
    checks["intent_vector_ref_present"] = _has_digest(record.request_intent_vector_ref)
    checks["final_resume_chunk_present"] = any(c.chunk_type == CHUNK_TYPE_FINAL_RESUME for c in chunks)
    checks["section_proof_summary_present"] = any(
        c.chunk_type == CHUNK_TYPE_SECTION_PROOF for c in chunks
    )
    section_types = {c.chunk_type for c in chunks if c.chunk_type in SECTION_CHUNK_TYPES}
    checks["at_least_one_section_output"] = len(section_types) >= 1
    checks["chunks_parent_linked"] = all(
        c.parent_intent_record_id == record.record_id and not c.to_dict().get("independent_cache_identity", True)
        for c in chunks
    )

    failed = [k for k, v in checks.items() if not v]
    if failed:
        return CompatibilityVerdict(
            admissible=False,
            reason="; ".join(failed),
            checks=checks,
        )
    return CompatibilityVerdict(admissible=True, reason="", checks=checks)


def assess_candidate_for_reuse(
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    *,
    query_digest: str,
    query_prompt_hash: str = "",
    query_gate_hash: str = "",
    runtime_generation_status: str = "",
) -> CompatibilityVerdict:
    """Compatibility for retrieval — includes profile/digest alignment when query hashes supplied."""
    base = assess_intent_record_admissibility(
        record,
        chunks=chunks,
        runtime_generation_status=runtime_generation_status,
    )
    if not base.admissible:
        return base

    checks = dict(base.checks)
    if query_prompt_hash:
        checks["prompt_profile_hash_match"] = record.prompt_profile_hash == query_prompt_hash
    else:
        checks["prompt_profile_hash_match"] = True
    if query_gate_hash:
        checks["gate_profile_hash_match"] = record.gate_profile_hash == query_gate_hash
    else:
        checks["gate_profile_hash_match"] = True

    failed = [k for k, v in checks.items() if not v]
    if failed:
        return CompatibilityVerdict(
            admissible=False,
            reason="; ".join(failed),
            checks=checks,
        )
    return CompatibilityVerdict(admissible=True, reason="", checks=checks)


def compatibility_report_row(
    *,
    candidate_record_id: str,
    verdict: CompatibilityVerdict,
    similarity: float,
) -> dict[str, Any]:
    return {
        "candidate_record_id": candidate_record_id,
        "similarity": similarity,
        "admissible": verdict.admissible,
        "reason": verdict.reason,
        "checks": verdict.checks,
    }


__all__ = [
    "CompatibilityVerdict",
    "assess_candidate_for_reuse",
    "assess_intent_record_admissibility",
    "compatibility_report_row",
]
