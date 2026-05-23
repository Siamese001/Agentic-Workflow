"""Ledger-aware X2 source_fact_id validation against the active section proof pool."""
from __future__ import annotations

from typing import Any, Iterable

from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    _is_forbidden_proof_source_fact_id,
    source_fact_base_id,
)
from apps_rg.runtime.sections.selected_role_fact_set import is_srfs_disallowed_proof_id

VALID_PROOF_SOURCES = frozenset({PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH})


def proof_source_from_metadata(metadata: dict[str, Any] | None) -> str:
    from apps_rg.runtime.product_evidence_authority import (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        proof_source_from_product_metadata,
    )

    if metadata is None:
        return PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    meta = metadata if isinstance(metadata, dict) else {}
    if not meta:
        return PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    ea = meta.get("evidence_authority")
    if isinstance(ea, dict) and str(ea.get("authority") or "").strip():
        resolved = proof_source_from_product_metadata(meta)
        if resolved:
            return resolved
    pt = str(meta.get("proof_pool_type") or "")
    if pt in ("augmented_skills_graph", PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH):
        return PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    if pt == "selected_role_fact_set":
        return PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    if pt:
        raise ValueError(
            f"proof_pool_type {pt!r} is not product authority; "
            f"expected evidence_authority={EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}"
        )
    raise ValueError(
        "missing evidence_authority; product requires augmented_skills_graph + ledger"
    )


def is_id_in_active_proof_pool(
    fid: str,
    allowed_fact_ids: set[str],
    alias_map: dict[str, str] | None = None,
) -> bool:
    s = str(fid).strip()
    if not s:
        return False
    base = source_fact_base_id(s.split("_metric_", 1)[0])
    if s in allowed_fact_ids or base in allowed_fact_ids:
        return True
    amap = alias_map or {}
    ledger = amap.get(base) or amap.get(s)
    if ledger and (ledger in allowed_fact_ids or source_fact_base_id(ledger) in allowed_fact_ids):
        return True
    reverse = {v: k for k, v in amap.items()}
    surface = reverse.get(base) or reverse.get(s)
    if surface and (surface in allowed_fact_ids or source_fact_base_id(surface) in allowed_fact_ids):
        return True
    return False


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
    meta = proof_pool_metadata or {}
    pool_digest = (
        proof_pool_digest
        or str(meta.get("canonical_evidence_set_digest") or "")
        or str(meta.get("proof_pool_digest") or "")
    )
    alias_map = dict(meta.get("id_alias_map") or {})
    if not alias_map:
        canon = meta.get("canonical_section_evidence_set")
        if isinstance(canon, dict):
            alias_map = dict(canon.get("id_alias_map") or {})

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
        if not is_id_in_active_proof_pool(s, allowed_fact_ids, alias_map=alias_map):
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
        "canonical_evidence_set_digest": pool_digest,
        "id_alias_map": alias_map,
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
    """X2 gate envelope for ledger-primary active proof pool (single gate id per section)."""
    from apps_rg.runtime.product_evidence_authority import is_product_evidence_authority_active

    ok, receipt, fail = validate_active_proof_pool_source_fact_ids(
        section=section_id,
        collected_ids=collected_ids,
        allowed_fact_ids=allowed_fact_ids,
        proof_pool_metadata=proof_pool_metadata,
        proof_pool_ref=proof_pool_ref,
        proof_pool_digest=proof_pool_digest,
        validator_name="evaluate_proof_pool_source_fact_gate",
    )
    product = is_product_evidence_authority_active(proof_pool_metadata)
    pt = str((proof_pool_metadata or {}).get("proof_pool_type") or "")
    srfs_used = (not product) and pt == "selected_role_fact_set"
    env = {
        **receipt,
        "x2_srfs_gate_status": "NOT_APPLICABLE" if product else ok,
        "out_of_slice_fact_ids": receipt.get("unsupported_source_fact_ids") or [],
        "srfs_allowed_fact_ids_count": len(allowed_fact_ids),
        "selected_role_fact_set_used": srfs_used,
        "broad_skills_ledger_used": False,
        "broad_skills_ledger_used_as_authority": False,
        "base_resume_fallback_used": False,
        "srfs_section_id": section_id,
    }
    return ok, env, fail


def proof_pool_x2_gate_id(
    section_id: str,
    *,
    proof_pool_metadata: dict[str, Any] | None = None,
    srfs_slice_gate_active: bool = False,
) -> str:
    """Canonical X2 membership gate id (W3: ``*_within_srfs_slice`` retired)."""
    _ = (proof_pool_metadata, srfs_slice_gate_active)
    return f"x2_{section_id}_active_proof_pool_source_fact_ids"


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
