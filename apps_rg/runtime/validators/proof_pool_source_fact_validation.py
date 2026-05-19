"""Ledger-aware X2 source_fact_id validation against the active section proof pool."""
from __future__ import annotations

from typing import Any, Iterable

from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    PROOF_SOURCE_BASE_RESUME_FALLBACK,
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    PROOF_SOURCE_SRFS,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    _is_forbidden_proof_source_fact_id,
    source_fact_base_id,
)
from apps_rg.runtime.sections.selected_role_fact_set import is_srfs_disallowed_proof_id

VALID_PROOF_SOURCES = frozenset(
    {
        PROOF_SOURCE_SRFS,
        PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        PROOF_SOURCE_BROAD_SKILLS_LEDGER,
        PROOF_SOURCE_BASE_RESUME_FALLBACK,
    }
)


def proof_source_from_metadata(metadata: dict[str, Any] | None) -> str:
    pt = str((metadata or {}).get("proof_pool_type") or "")
    if pt == "selected_role_fact_set":
        return PROOF_SOURCE_SRFS
    if pt in ("augmented_skills_graph", "augmented_skills_graph_c03_graphrag"):
        return PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    if pt == "broad_skills_ledger":
        return PROOF_SOURCE_BROAD_SKILLS_LEDGER
    if pt == "base_resume_fallback":
        return PROOF_SOURCE_BASE_RESUME_FALLBACK
    return PROOF_SOURCE_BASE_RESUME_FALLBACK


def is_id_in_active_proof_pool(fid: str, allowed_fact_ids: set[str]) -> bool:
    s = str(fid).strip()
    if not s:
        return False
    base = source_fact_base_id(s.split("_metric_", 1)[0])
    return s in allowed_fact_ids or base in allowed_fact_ids


def validate_active_proof_pool_source_fact_ids(
    *,
    section: str,
    collected_ids: Iterable[str],
    allowed_fact_ids: set[str],
    proof_pool_metadata: dict[str, Any] | None = None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
    validator_name: str = "validate_active_proof_pool_source_fact_ids",
) -> tuple[bool, dict[str, Any], str | None]:
    """Validate claim-support IDs against the active pool; reject JD/briefing and unknown IDs."""
    proof_source = proof_source_from_metadata(proof_pool_metadata)
    if proof_pool_ref:
        pool_ref = proof_pool_ref
    elif proof_pool_metadata:
        pool_ref = str(
            proof_pool_metadata.get("broad_skills_ledger_ref")
            or proof_pool_metadata.get("srfs_path")
            or proof_pool_metadata.get("proof_pool_ref")
            or ""
        )
    else:
        pool_ref = ""
    pool_digest = proof_pool_digest or str((proof_pool_metadata or {}).get("proof_pool_digest") or "")

    seen: set[str] = set()
    checked: list[str] = []
    unsupported: list[str] = []
    rejected_non_proof: list[str] = []
    jd_or_briefing: list[str] = []

    for raw in collected_ids:
        s = str(raw).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        checked.append(s)
        if is_srfs_disallowed_proof_id(s):
            rejected_non_proof.append(s)
            su = s.upper().replace(" ", "_")
            if su in ("BRIEFING_ONLY",) or "briefing" in s.lower():
                jd_or_briefing.append(s)
            else:
                jd_or_briefing.append(s)
            continue
        bad, reason = _is_forbidden_proof_source_fact_id(s)
        if bad:
            rejected_non_proof.append(s)
            if "briefing" in reason:
                jd_or_briefing.append(s)
            else:
                jd_or_briefing.append(s)
            continue
        if not is_id_in_active_proof_pool(s, allowed_fact_ids):
            unsupported.append(s)

    ok = not unsupported and not rejected_non_proof and bool(checked or allowed_fact_ids)
    status = "PASS" if ok else "FAIL"
    decisive: str | None = None
    if rejected_non_proof:
        decisive = "non_proof_source_fact_ids:" + ",".join(sorted(set(rejected_non_proof))[:24])
    elif unsupported:
        decisive = "unsupported_source_fact_ids:" + ",".join(sorted(set(unsupported))[:24])
    elif not checked:
        decisive = "no_source_fact_ids_collected"

    meta = proof_pool_metadata or {}
    skills_status = str(meta.get("skills_authority_status") or meta.get("skills_source_authority_status") or "")
    skills_src = str(meta.get("skills_authority_source_type") or meta.get("skills_source_type") or "")
    claim_src = str(meta.get("claim_evidence_source_type") or "")
    broad_skills_skills_auth = meta.get("legacy_broad_skills_ledger_skills_authority")
    if broad_skills_skills_auth is True or meta.get("broad_skills_ledger_skills_authority") is True:
        skills_status = "FAIL"
    if skills_src == "broad_skills_ledger":
        skills_status = "FAIL"

    receipt: dict[str, Any] = {
        "section": section,
        "proof_source": proof_source,
        "proof_pool_ref": pool_ref,
        "proof_pool_digest": pool_digest,
        "claim_evidence_source_type": claim_src or None,
        "claim_evidence_source_ref": meta.get("claim_evidence_source_ref"),
        "skills_authority_source_type": skills_src or None,
        "skills_authority_status": skills_status or "UNKNOWN",
        "skills_authority_graph_ref": meta.get("skills_authority_graph_ref") or meta.get("graph_ref"),
        "legacy_broad_skills_ledger_skills_authority": bool(broad_skills_skills_auth),
        "broad_skills_ledger_claim_evidence_only": meta.get("broad_skills_ledger_claim_evidence_only"),
        "allowed_source_fact_ids_count": len(allowed_fact_ids),
        "source_fact_ids_checked": checked,
        "unsupported_source_fact_ids": sorted(set(unsupported)),
        "rejected_non_proof_source_ids": sorted(set(rejected_non_proof)),
        "jd_or_briefing_ids_rejected": sorted(set(jd_or_briefing)),
        "x2_source_fact_pool_status": status,
        "decisive_reason": decisive,
        "validator_name": validator_name,
    }
    if skills_status in ("BLOCKED", "UNKNOWN", "FAIL", ""):
        receipt["skills_authority_x2_boundary"] = "NOT_PASS"
    elif skills_status == "PASS":
        receipt["skills_authority_x2_boundary"] = "PASS"
    else:
        receipt["skills_authority_x2_boundary"] = "UNKNOWN"
    return ok, receipt, decisive


def evaluate_proof_pool_source_fact_gate(
    *,
    section_id: str,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
    proof_pool_metadata: dict[str, Any] | None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
) -> tuple[bool, dict[str, Any], str | None]:
    """X2 gate envelope compatible with SRFS slice gates + ledger-primary receipt fields."""
    ok, receipt, fail = validate_active_proof_pool_source_fact_ids(
        section=section_id,
        collected_ids=collected_ids,
        allowed_fact_ids=allowed_fact_ids,
        proof_pool_metadata=proof_pool_metadata,
        proof_pool_ref=proof_pool_ref,
        proof_pool_digest=proof_pool_digest,
        validator_name="evaluate_proof_pool_source_fact_gate",
    )
    env = {
        **receipt,
        "x2_srfs_gate_status": ok,
        "out_of_slice_fact_ids": receipt.get("unsupported_source_fact_ids") or [],
        "srfs_allowed_fact_ids_count": len(allowed_fact_ids),
        "selected_role_fact_set_used": proof_source_from_metadata(proof_pool_metadata) == PROOF_SOURCE_SRFS,
        "broad_skills_ledger_used": proof_source_from_metadata(proof_pool_metadata)
        == PROOF_SOURCE_BROAD_SKILLS_LEDGER,
        "base_resume_fallback_used": proof_source_from_metadata(proof_pool_metadata)
        == PROOF_SOURCE_BASE_RESUME_FALLBACK,
        "srfs_section_id": section_id,
    }
    return ok, env, fail


def proof_pool_x2_gate_id(
    section_id: str,
    *,
    proof_pool_metadata: dict[str, Any] | None,
    srfs_slice_gate_active: bool = False,
) -> str:
    """Legacy SRFS gate id for unit tests; active-pool id for ledger-primary runtime."""
    pt = str((proof_pool_metadata or {}).get("proof_pool_type") or "")
    legacy = f"x2_{section_id}_source_fact_ids_within_srfs_slice"
    active = f"x2_{section_id}_active_proof_pool_source_fact_ids"
    if pt == "selected_role_fact_set":
        return legacy
    if srfs_slice_gate_active and pt not in (PROOF_SOURCE_BROAD_SKILLS_LEDGER, PROOF_SOURCE_BASE_RESUME_FALLBACK):
        return legacy
    return active


def write_x2_source_fact_pool_receipt(artifacts_dir: Any, receipt: dict[str, Any]) -> str:
    from pathlib import Path

    from apps_rg.runtime.sections.lane_artifact_io import write_json

    path = Path(artifacts_dir) / "x2_source_fact_pool_receipt.json"
    write_json(path, receipt)
    return str(path)


def scope_ids_membership_only(
    source_ids: set[str],
    *,
    allowed_fact_ids: set[str],
    forbidden_prefixes: tuple[str, ...] = (),
) -> tuple[bool, list[str], list[str], list[str]]:
    """Membership-based fact scope (no legacy bul_* prefix requirement)."""
    illegal_prefix: list[str] = []
    forbidden_hits: list[str] = []
    not_in_pool: list[str] = []
    for sid in source_ids:
        s = str(sid)
        if any(s.startswith(p) for p in forbidden_prefixes):
            forbidden_hits.append(s)
        if is_srfs_disallowed_proof_id(s) or _is_forbidden_proof_source_fact_id(s)[0]:
            forbidden_hits.append(s)
            continue
        if not is_id_in_active_proof_pool(s, allowed_fact_ids):
            not_in_pool.append(s)
    ok = bool(source_ids) and not illegal_prefix and not forbidden_hits and not not_in_pool
    return ok, illegal_prefix, forbidden_hits, not_in_pool


__all__ = [
    "VALID_PROOF_SOURCES",
    "evaluate_proof_pool_source_fact_gate",
    "is_id_in_active_proof_pool",
    "proof_pool_x2_gate_id",
    "proof_source_from_metadata",
    "scope_ids_membership_only",
    "validate_active_proof_pool_source_fact_ids",
    "write_x2_source_fact_pool_receipt",
]
