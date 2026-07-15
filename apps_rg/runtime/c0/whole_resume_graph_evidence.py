"""W7 whole-resume C0.3 evidence reconciliation and release authority gate.

The gate is intentionally post-materialization.  It never selects, repairs, or
widens evidence: it reconciles the rendered lane snapshots against the frozen
whole-resume allocation and keeps an absent/unknown W6 human receipt non-PASS.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest
from apps_rg.runtime.c0.resume_graph_allocation import (
    validate_resume_graph_allocation_plan,
)

SCHEMA_VERSION = "whole_resume_graph_evidence_contract_v1"
ARTIFACT_NAME = "whole_resume_graph_evidence_contract.json"
_CLAIM_SECTIONS = frozenset(
    {
        "headline",
        "executive_summary",
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    }
)


def _strings(values: Iterable[Any] | None) -> list[str]:
    return sorted({str(value).strip() for value in values or () if str(value).strip()})


def _safe_repo_path(repo: Path, raw: Any) -> Path | None:
    text = str(raw or "").strip().replace("\\", "/")
    if not text:
        return None
    candidate = (repo / text).resolve() if not Path(text).is_absolute() else Path(text).resolve()
    try:
        candidate.relative_to(repo.resolve())
    except ValueError:
        return None
    return candidate


def _load_json(path: Path | None) -> Any:
    if path is None or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _sha256(path: Path | None) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else ""


def _snapshot_digest(snapshot: Mapping[str, Any]) -> str:
    return str(
        snapshot.get("resume_graph_allocation_plan_digest")
        or (snapshot.get("selected_fact_plan") or {}).get("allocation_plan_digest")
        or (snapshot.get("proof_pool_metadata") or {}).get(
            "resume_graph_allocation_plan_digest"
        )
        or ""
    ).strip()


def _claim_rows(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in snapshot.get("claim_ledger") or []
        if isinstance(row, Mapping) and str(row.get("claim_text") or "").strip()
    ]


def _binding_rows(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in snapshot.get("graph_claim_bindings") or []
        if isinstance(row, Mapping)
    ]


def _official_w6_status(
    *, repo: Path, rollup: Mapping[str, Any]
) -> tuple[str, list[str], dict[str, Any]]:
    authority = rollup.get("resume_graph_w6_release_evidence")
    if not isinstance(authority, Mapping):
        return "UNKNOWN", ["official_w6_release_evidence_missing"], {}
    receipt_path = _safe_repo_path(repo, authority.get("receipt_ref"))
    if receipt_path is None:
        return "UNKNOWN", ["official_w6_receipt_ref_invalid"], {}
    trusted_receipt = str(authority.get("trusted_receipt_sha256") or "").strip()
    trusted_full = str(authority.get("trusted_full_report_sha256") or "").strip()
    try:
        from ops_scripts.ci.check_apps_rg_resume_graph_w6 import validate_artifact

        errors = validate_artifact(
            receipt_path,
            trusted_report_sha256=trusted_receipt,
            trusted_full_report_sha256=trusted_full,
        )
    except Exception as exc:  # fail closed at an external evidence boundary
        errors = [f"official_w6_validation_error:{type(exc).__name__}"]
    status = "PASS" if not errors else "UNKNOWN"
    return status, errors, {
        "receipt_ref": str(authority.get("receipt_ref") or ""),
        "receipt_sha256": _sha256(receipt_path),
        "trusted_receipt_sha256": trusted_receipt,
        "trusted_full_report_sha256": trusted_full,
    }


def build_whole_resume_graph_evidence_contract(
    *,
    repo: Path,
    final_resume_blob: Mapping[str, Any],
    rollup_blob: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a closed, deterministic W7 contract from materialized artifacts."""
    refs_raw = rollup_blob.get("resume_graph_allocation_refs")
    refs = dict(refs_raw) if isinstance(refs_raw, Mapping) else {}
    declared_digest = str(
        rollup_blob.get("resume_graph_allocation_plan_digest") or ""
    ).strip()
    active = bool(declared_digest or refs)
    if not active:
        return {
            "schema_version": SCHEMA_VERSION,
            "active": False,
            "engineering_pass": False,
            "official_w6_status": "UNKNOWN",
            "release_pass": False,
            "unknown_is_pass": False,
            "promotion_eligible": False,
            "failure_codes": ["whole_resume_graph_allocation_not_active"],
            "contract_digest": stable_digest(
                {
                    "schema_version": SCHEMA_VERSION,
                    "active": False,
                    "engineering_pass": False,
                    "official_w6_status": "UNKNOWN",
                    "release_pass": False,
                    "unknown_is_pass": False,
                    "promotion_eligible": False,
                    "failure_codes": ["whole_resume_graph_allocation_not_active"],
                }
            ),
        }

    plan_path = _safe_repo_path(repo, refs.get("allocation_plan"))
    ledger_path = _safe_repo_path(repo, refs.get("usage_ledger"))
    contracts_path = _safe_repo_path(repo, refs.get("section_final_evidence_contracts"))
    plan = _load_json(plan_path)
    ledger = _load_json(ledger_path)
    section_contracts = _load_json(contracts_path)
    failures: list[str] = []
    if not isinstance(plan, Mapping):
        failures.append("allocation_plan_missing_or_invalid")
        plan = {}
    else:
        failures.extend(
            f"allocation_plan:{failure}"
            for failure in validate_resume_graph_allocation_plan(plan)
        )
    if not isinstance(ledger, Mapping):
        failures.append("usage_ledger_missing_or_invalid")
        ledger = {}
    if not isinstance(section_contracts, Mapping):
        failures.append("section_contracts_missing_or_invalid")
        section_contracts = {}

    plan_digest = str(plan.get("allocation_plan_digest") or "").strip()
    if not declared_digest:
        failures.append("rollup_allocation_digest_missing")
    elif declared_digest != plan_digest:
        failures.append("rollup_allocation_digest_mismatch")
    if str(ledger.get("allocation_plan_digest") or "").strip() != plan_digest:
        failures.append("usage_ledger_allocation_digest_mismatch")
    if ledger.get("current_run_only") is not True:
        failures.append("usage_ledger_not_current_run_only")
    if ledger.get("durable_graph_state_mutated") is not False:
        failures.append("durable_graph_state_mutated")

    section_rows: list[dict[str, Any]] = []
    visible_claim_inventory: list[dict[str, str]] = []
    sections = [
        section
        for section in final_resume_blob.get("sections") or []
        if isinstance(section, Mapping)
        and section.get("section_kind") == "generated_lane"
        and str(section.get("section_id") or "") in _CLAIM_SECTIONS
    ]
    observed_ids = {str(section.get("section_id") or "") for section in sections}
    if observed_ids != _CLAIM_SECTIONS:
        failures.append("generated_section_parity_mismatch")

    for section in sorted(sections, key=lambda value: str(value.get("section_id") or "")):
        section_id = str(section.get("section_id") or "")
        snapshot_raw = section.get("l2_output_snapshot")
        snapshot = dict(snapshot_raw) if isinstance(snapshot_raw, Mapping) else {}
        section_failures: list[str] = []
        if snapshot.get("assembly_gap") is True:
            section_failures.append("assembly_gap")
        observed_digest = _snapshot_digest(snapshot)
        if observed_digest != plan_digest:
            section_failures.append("allocation_digest_mismatch")
        contract_raw = section_contracts.get(section_id)
        contract = dict(contract_raw) if isinstance(contract_raw, Mapping) else {}
        if not contract:
            section_failures.append("section_contract_missing")
        else:
            expected_contract_digest = stable_digest(
                {key: value for key, value in contract.items() if key != "contract_digest"}
            )
            if str(contract.get("contract_digest") or "") != expected_contract_digest:
                section_failures.append("section_contract_digest_invalid")
            if str(contract.get("allocation_plan_digest") or "") != plan_digest:
                section_failures.append("section_contract_allocation_digest_mismatch")
            if contract.get("traversal_conservation_pass") is not True:
                section_failures.append("traversal_conservation_nonpass")
            if contract.get("pass") is not True:
                section_failures.append("section_contract_nonpass")

        claims = _claim_rows(snapshot)
        bindings = _binding_rows(snapshot)
        binding_by_hash = {
            str(row.get("visible_claim_hash") or ""): row for row in bindings
        }
        for claim in claims:
            text = str(claim.get("claim_text") or "").strip()
            claim_hash = stable_digest({"text": text})
            visible_claim_inventory.append(
                {"section_id": section_id, "visible_claim_hash": claim_hash}
            )
            binding = binding_by_hash.get(claim_hash)
            if binding is None:
                section_failures.append(f"unbound_visible_claim:{claim_hash[:12]}")
            elif str(binding.get("allocation_plan_digest") or "") != plan_digest:
                section_failures.append(f"binding_digest_mismatch:{claim_hash[:12]}")
        if claims and not bindings:
            section_failures.append("claim_bindings_missing")
        if bindings and snapshot.get("resume_graph_claim_binding_pass") is not True:
            section_failures.append("claim_binding_gate_nonpass")
        section_failures = sorted(set(section_failures))
        failures.extend(f"{section_id}:{code}" for code in section_failures)
        section_rows.append(
            {
                "section_id": section_id,
                "snapshot_digest": str(section.get("section_digest") or ""),
                "allocation_plan_digest": observed_digest,
                "claim_count": len(claims),
                "binding_count": len(bindings),
                "failure_codes": section_failures,
                "pass": not section_failures,
            }
        )

    uniqueness = plan.get("uniqueness_receipt")
    if not isinstance(uniqueness, Mapping) or uniqueness.get("pass") is not True:
        failures.append("global_uniqueness_nonpass")
    conservation = plan.get("candidate_conservation_receipt")
    if not isinstance(conservation, Mapping) or conservation.get("pass") is not True:
        failures.append("candidate_conservation_nonpass")

    official_w6_status, w6_failures, w6_evidence = _official_w6_status(
        repo=repo, rollup=rollup_blob
    )
    failures = sorted(set(failures))
    engineering_pass = not failures
    release_failures = sorted({*failures, *w6_failures})
    release_pass = engineering_pass and official_w6_status == "PASS" and not w6_failures
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "active": True,
        "allocation_plan_digest": plan_digest,
        "artifact_refs": {
            "allocation_plan": str(refs.get("allocation_plan") or ""),
            "usage_ledger": str(refs.get("usage_ledger") or ""),
            "section_final_evidence_contracts": str(
                refs.get("section_final_evidence_contracts") or ""
            ),
        },
        "artifact_sha256": {
            "allocation_plan": _sha256(plan_path),
            "usage_ledger": _sha256(ledger_path),
            "section_final_evidence_contracts": _sha256(contracts_path),
        },
        "section_ids": sorted(observed_ids),
        "section_results": section_rows,
        "visible_claim_count": len(visible_claim_inventory),
        "visible_claim_inventory_digest": stable_digest(visible_claim_inventory),
        "final_snapshot_digest": stable_digest(
            [
                {
                    "section_id": row["section_id"],
                    "snapshot_digest": row["snapshot_digest"],
                }
                for row in section_rows
            ]
        ),
        "engineering_pass": engineering_pass,
        "official_w6_status": official_w6_status,
        "official_w6_evidence": w6_evidence,
        "release_pass": release_pass,
        "unknown_is_pass": False,
        "promotion_eligible": release_pass,
        "failure_codes": failures,
        "release_failure_codes": release_failures,
        "durable_graph_state_mutated": False,
    }
    body["contract_digest"] = stable_digest(body)
    return body


__all__ = [
    "ARTIFACT_NAME",
    "SCHEMA_VERSION",
    "build_whole_resume_graph_evidence_contract",
]
