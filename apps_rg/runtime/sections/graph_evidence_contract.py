"""Graph-native evidence contract helpers for apps_rg section lanes.

This module owns generic proof-pool mechanics shared by graph evidence lanes:
metric derivative IDs, selected evidence plan normalization, active proof-pool
reporting, and claim-ledger source ID collection. It deliberately does not load
or resolve SelectedRoleFactSet/SRFS artifacts.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from apps_rg.runtime.graph_era_aliases import emit_graph_era_aliases

SECTION_KEYS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def metric_derivative_fact_id(candidate_fact_id: str, metric_raw: str) -> str:
    """Metric-bound derivative ID for section proof-pool allowlists."""
    return f"{candidate_fact_id}_metric_{sha16(metric_raw)[:8]}"


def _metric_raw_from_row(row: dict[str, Any]) -> str:
    raw_metrics = row.get("metric_values") or []
    if not isinstance(raw_metrics, list) or not raw_metrics:
        return ""
    return "|".join(str(x) for x in raw_metrics if str(x).strip())


def slice_row_to_plan_fact(
    slice_row: dict[str, Any],
    *,
    section_id: str = "executive_summary",
) -> dict[str, Any]:
    """Map a graph/candidate evidence row to a selected evidence plan fact."""
    _ = section_id
    cid = str(
        slice_row.get("candidate_fact_id")
        or slice_row.get("fact_id")
        or slice_row.get("role_episode_bundle_id")
        or ""
    ).strip()
    if not cid:
        raise ValueError("selected graph evidence row missing candidate_fact_id/fact_id")
    conf = str(slice_row.get("confidence") or slice_row.get("support_level") or "HIGH").strip().upper()
    vstat = str(
        slice_row.get("verification_status")
        or slice_row.get("approval_status")
        or slice_row.get("support_level")
        or "approved_by_graph_presence"
    ).strip()
    mr = _metric_raw_from_row(slice_row)
    technologies = slice_row.get("technologies")
    if not isinstance(technologies, list):
        technologies = []
    row: dict[str, Any] = {
        "fact_id": cid,
        "claim_text": str(slice_row.get("claim_text") or "").strip(),
        "candidate_fact_id": cid,
        "verification_status": vstat,
        "confidence": conf,
        "claim_eligible_medium": bool(slice_row.get("claim_eligible_medium")),
        "source_trace_archive_relpaths": list(slice_row.get("source_trace_archive_relpaths") or ()),
        "metric_values": tuple(slice_row.get("metric_values") or ()),
        "company_lane": slice_row.get("company_lane"),
        "role_families_supported": slice_row.get("role_families_supported") or [],
        "metric_raw": mr,
        "has_metric": bool(mr),
        "technologies": technologies,
        "domain": str(slice_row.get("domain") or slice_row.get("domain_family") or "").strip(),
        "source_employment": str(slice_row.get("source_employment") or "").strip(),
    }
    for key in (
        "role_episode_bundle_id",
        "employer",
        "employer_node_id",
        "graph_skill_node_ids",
        "metric_outcome_ids",
        "selected_metric_ids",
        "allowed_graph_evidence_ids",
        "linked_identity_fact_ids",
        "graph_evidence_type",
    ):
        if key in slice_row:
            row[key] = slice_row[key]
    return row


def build_allowed_fact_ids_for_plan_facts(
    facts: list[dict[str, Any]],
) -> tuple[list[str], set[str]]:
    """Return ordered allowed IDs: base fact IDs plus metric derivatives."""
    ordered: list[str] = []
    seen: set[str] = set()

    def _push(fid: str) -> None:
        if fid and fid not in seen:
            seen.add(fid)
            ordered.append(fid)

    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        _push(fid)
        for gid in fact.get("allowed_graph_evidence_ids") or []:
            _push(str(gid).strip())
        mr = fact.get("metric_raw")
        if mr and fid:
            _push(metric_derivative_fact_id(fid, str(mr)))
    return ordered, set(ordered)


def selection_method_for_section(section_id: str) -> str:
    return f"selected_graph_evidence_plan_{section_id}"


def selected_graph_evidence_plan_from_payload(source: dict[str, Any] | None) -> dict[str, Any]:
    """Extract the selected graph-evidence plan from a runtime payload or proof-pool metadata."""
    if not isinstance(source, dict):
        return {}
    plan = source.get("selected_graph_evidence_plan")
    if isinstance(plan, dict) and plan:
        return plan
    pp_meta = source.get("proof_pool_metadata")
    if isinstance(pp_meta, dict):
        nested = pp_meta.get("selected_graph_evidence_plan")
        if isinstance(nested, dict) and nested:
            return nested
    return {}


def require_selected_graph_evidence_plan(
    source: dict[str, Any] | None,
    *,
    section_id: str,
) -> dict[str, Any]:
    plan = selected_graph_evidence_plan_from_payload(source)
    if not plan:
        raise ValueError(
            f"{section_id}: graph packet is mandatory; missing selected_graph_evidence_plan"
        )
    return plan


def require_section_packet(
    source: dict[str, Any] | None,
    *,
    section_id: str,
    packet_key: str,
) -> dict[str, Any]:
    """Require an attached section packet either top-level or nested in proof_pool_metadata."""
    if not isinstance(source, dict):
        raise ValueError(f"{section_id}: graph packet is mandatory; missing {packet_key}")
    packet = source.get(packet_key)
    if not isinstance(packet, dict) or not packet:
        pp_meta = source.get("proof_pool_metadata")
        if isinstance(pp_meta, dict):
            nested = pp_meta.get(packet_key)
            if isinstance(nested, dict) and nested:
                packet = nested
    if not isinstance(packet, dict) or not packet:
        raise ValueError(f"{section_id}: graph packet is mandatory; missing {packet_key}")
    return packet


def build_selected_graph_evidence_plan(
    *,
    section_id: str,
    selection_method: str,
    facts: list[dict[str, Any]],
    required_fact_ids: list[str] | None = None,
    **extra_fields: Any,
) -> dict[str, Any]:
    """Build a selected graph-evidence plan with optional section-specific metadata."""
    plan: dict[str, Any] = {
        "section_id": section_id,
        "selection_method": selection_method,
        "facts": facts,
    }
    if required_fact_ids is not None:
        plan["required_fact_ids"] = list(required_fact_ids)
    if extra_fields:
        plan.update(extra_fields)
    return plan


def build_graph_evidence_runtime_payload(
    *,
    run_id_prefix: str,
    section_id: str,
    prompt_id: str,
    repo_root: Path,
    base_json_path: Path,
    base_hash: str,
    selected_graph_evidence_plan: dict[str, Any],
    allowed_graph_evidence_ids: Iterable[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    writable_context_scope: str,
    extra_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a graph-era runtime payload and backfill fact-era aliases for compatibility."""
    payload: dict[str, Any] = {
        "run_id": datetime.now(timezone.utc).strftime(f"{run_id_prefix}_%Y%m%d_%H%M%S"),
        "section_id": section_id,
        "prompt_id": prompt_id,
        "base_resume_json_ref": str(base_json_path.relative_to(repo_root))
        if base_json_path.is_relative_to(repo_root)
        else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_graph_evidence_plan": selected_graph_evidence_plan,
        "allowed_graph_evidence_ids": list(allowed_graph_evidence_ids),
        "writable_context_scope": writable_context_scope,
        "full_resume_writable": False,
    }
    if extra_fields:
        payload.update(extra_fields)
    emit_graph_era_aliases(payload)
    return payload


def plan_fact_to_employment_bullet_row(plan_fact: dict[str, Any]) -> dict[str, Any]:
    """Map selected evidence plan facts to the section bullet-row shape."""
    fid = str(plan_fact.get("fact_id") or "").strip()
    mr = str(plan_fact.get("metric_raw") or "").strip()
    technologies = plan_fact.get("technologies")
    if not isinstance(technologies, list):
        technologies = []
    source_emp = str(plan_fact.get("source_employment") or plan_fact.get("employer") or "Graph Evidence").strip()
    return {
        "fact_id": fid,
        "claim_text": str(plan_fact.get("claim_text") or ""),
        "source_employment": source_emp,
        "has_metric": bool(mr),
        "metric_raw": mr,
        "domain": str(plan_fact.get("domain") or ""),
        "technologies": technologies,
    }


def graph_only_proof_pool_metadata(
    *,
    section_id: str,
    candidate_fact_pool_count: int,
    allowed_fact_ids_count: int,
    graph_ref: str,
    legacy_ledger_ref: str = "",
) -> dict[str, Any]:
    n = int(allowed_fact_ids_count)
    out: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "selected_role_fact_set_used": False,
        "base_resume_claim_authority": False,
        "graph_only_claim_authority": True,
        "graph_evidence_plan_used": True,
        "section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": n,
        "fallback_used": False,
        "fallback_reason": "",
        "c03_graphrag_bound_required": True,
    }
    if legacy_ledger_ref:
        out["claim_evidence_substrate_ref"] = legacy_ledger_ref
        out["legacy_skills_ledger_ref"] = legacy_ledger_ref
        out["legacy_skills_ledger_role"] = "deprecated_reference"
    if graph_ref:
        out["graph_ref"] = graph_ref
    return out


def _ledger_root_fact_ids_union(claim_ledger: list[Any] | None) -> set[str]:
    ids: set[str] = set()
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            ids.add(str(fid).split("_metric_")[0])
    return ids


def compute_claim_ledger_union_matches_required_fact_ids(
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> bool | None:
    if not isinstance(selected_fact_plan, dict):
        return None
    req = {
        str(x).split("_metric_")[0]
        for x in (selected_fact_plan.get("required_fact_ids") or [])
        if str(x).strip()
    }
    ledger = _ledger_root_fact_ids_union(claim_ledger)
    if not req:
        return False
    return req == ledger


def _out_of_pool_from_active_gate(active_gate: dict[str, Any] | None) -> list[str]:
    if active_gate is None:
        return []
    ov = active_gate.get("observed_value")
    if not isinstance(ov, dict):
        return []
    oos = ov.get("out_of_slice_fact_ids") or ov.get("out_of_pool_fact_ids")
    if not isinstance(oos, list):
        return []
    return [str(x) for x in oos]


def normalized_graph_evidence_reporting_fields(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> dict[str, Any]:
    """Flat active graph evidence fields for section_metric_receipt."""
    from apps_rg.runtime.product_evidence_authority import product_authority_reporting_fields

    pp = dict(runtime_payload.get("proof_pool_metadata") or {})
    req_ids = (selected_fact_plan or {}).get("required_fact_ids") if isinstance(selected_fact_plan, dict) else None
    req_count = len(req_ids or []) if isinstance(req_ids, list) else 0
    out = product_authority_reporting_fields(
        section_id=section_id,
        proof_pool_metadata=pp,
        allowed_fact_ids_count=int(pp.get("allowed_fact_ids_count") or 0),
        required_fact_ids_count=req_count,
    )
    out["claim_ledger_union_matches_required_fact_ids"] = compute_claim_ledger_union_matches_required_fact_ids(
        selected_fact_plan if isinstance(selected_fact_plan, dict) else None,
        claim_ledger,
    )
    active_gate_id = f"x2_{section_id}_active_proof_pool_source_fact_ids"
    active_gate = next((g for g in x2_gates if g.get("gate_id") == active_gate_id), None)
    if active_gate is not None:
        out["x2_active_proof_pool_gate_status"] = "PASS" if active_gate.get("pass") else "FAIL"
        out["out_of_pool_fact_ids"] = _out_of_pool_from_active_gate(active_gate)
    if bool(pp.get("fallback_used")):
        out["fallback_used"] = True
        out["fallback_reason"] = str(pp.get("fallback_reason") or "")
    return out


def merge_graph_evidence_reporting_into_dict(
    receipt: dict[str, Any],
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> None:
    receipt.update(
        normalized_graph_evidence_reporting_fields(
            section_id=section_id,
            runtime_payload=runtime_payload,
            x2_gates=x2_gates,
            selected_fact_plan=selected_fact_plan,
            claim_ledger=claim_ledger,
        )
    )
    from apps_rg.runtime.bindings.section_lane_c0_metrics import (
        merge_c0_metrics_into_section_metric_receipt,
    )

    merge_c0_metrics_into_section_metric_receipt(receipt, runtime_payload)
    art = runtime_payload.get("artifact_dir")
    if art:
        from apps_rg.runtime.evidence.canonical_evidence_digest_chain import (
            DIGEST_CHAIN_ARTIFACT,
            build_canonical_evidence_digest_chain,
            emit_canonical_evidence_digest_chain,
        )

        ad = Path(str(art))
        if (ad / "x2_gate_outputs.json").is_file():
            if not (ad / DIGEST_CHAIN_ARTIFACT).is_file():
                emit_canonical_evidence_digest_chain(ad, section_id=section_id)
            chain = build_canonical_evidence_digest_chain(ad, section_id=section_id)
            receipt["canonical_evidence_set_digest"] = chain.get("c05_canonical_evidence_digest")
            receipt["fec_allowed_fact_ids_digest"] = chain.get("c06_final_evidence_contract_digest")
            receipt["c07_runtime_bound_evidence_digest"] = chain.get("c07_runtime_bound_evidence_digest")
            receipt["pa_c0_slot_digest"] = chain.get("pa_c0_slot_digest")
            receipt["provider_request_allowed_ids_digest"] = chain.get(
                "provider_request_allowed_ids_digest"
            )
            receipt["claim_ledger_source_fact_ids_digest"] = chain.get(
                "claim_ledger_source_fact_ids_digest"
            )
            receipt["x2_active_pool_digest"] = chain.get("x2_active_pool_digest")
            receipt["section_receipt_digest"] = chain.get("section_receipt_digest")
            receipt["canonical_evidence_digest_chain_ref"] = DIGEST_CHAIN_ARTIFACT
            receipt["canonical_evidence_invariants_pass"] = (chain.get("invariants") or {}).get(
                "all_pass"
            )


def is_disallowed_proof_id(fid: str) -> bool:
    """JD/briefing/target/companion-shaped proof tokens and empty IDs are never proofable."""
    from apps_rg.runtime.section_proof.section_input_usage_ledger import (
        _is_forbidden_proof_source_fact_id,
    )

    s = str(fid).strip()
    if not s:
        return False
    su = s.upper().replace(" ", "_")
    if su in ("JD_ONLY", "BRIEFING_ONLY", "TARGET_ONLY", "JOB_DESCRIPTION_ONLY"):
        return True
    bad, _ = _is_forbidden_proof_source_fact_id(s)
    return bad


def collect_source_fact_ids_from_claim_ledger(claim_ledger: Iterable[Any] | None) -> list[str]:
    ids: list[str] = []
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            ids.append(str(fid))
        if row.get("source_fact_id") is not None:
            ids.append(str(row["source_fact_id"]))
    return ids


def collect_source_fact_ids_from_bullets_and_ledger(
    parsed_output: dict[str, Any] | None,
    claim_ledger: Iterable[Any] | None,
) -> list[str]:
    ids: list[str] = []
    for bullet in (parsed_output or {}).get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        for fid in bullet.get("source_fact_ids") or []:
            ids.append(str(fid))
    ids.extend(collect_source_fact_ids_from_claim_ledger(claim_ledger))
    return ids


def collect_source_fact_ids_from_competencies_struct(
    competencies: Iterable[Any] | None,
    claim_ledger: Iterable[Any] | None,
) -> list[str]:
    ids = collect_source_fact_ids_from_claim_ledger(claim_ledger)
    for cat in competencies or []:
        if not isinstance(cat, dict):
            continue
        for fid in cat.get("source_fact_ids") or []:
            ids.append(str(fid))
        for term in cat.get("terms") or []:
            if isinstance(term, dict):
                if term.get("source_fact_id") is not None:
                    ids.append(str(term["source_fact_id"]))
                for x in term.get("source_fact_ids") or []:
                    ids.append(str(x))
    return ids


def collect_source_fact_ids_for_section(
    section_id: str,
    *,
    claim_ledger: Iterable[Any] | None = None,
    parsed_output: dict[str, Any] | None = None,
    competencies: Iterable[Any] | None = None,
) -> list[str]:
    if section_id in ("unify_bullets", "ibm_bullets"):
        return collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
    if section_id == "competencies":
        return collect_source_fact_ids_from_competencies_struct(competencies, claim_ledger)
    return collect_source_fact_ids_from_claim_ledger(claim_ledger)


def validate_source_fact_ids_within_active_pool(
    *,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, list[str]]:
    bad: list[str] = []
    seen: set[str] = set()
    for raw in collected_ids:
        s = str(raw).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        if is_disallowed_proof_id(s) or s not in allowed_fact_ids:
            bad.append(s)
    return (len(bad) == 0, sorted(set(bad)))


def evaluate_active_pool_source_fact_gate(
    *,
    section_id: str,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, dict[str, Any], str | None]:
    ok, out_of_pool = validate_source_fact_ids_within_active_pool(
        collected_ids=collected_ids,
        allowed_fact_ids=allowed_fact_ids,
    )
    env: dict[str, Any] = {
        "x2_active_pool_gate_status": ok,
        "out_of_pool_fact_ids": out_of_pool,
        "allowed_fact_ids_count": len(allowed_fact_ids),
        "graph_evidence_plan_used": True,
        "section_id": section_id,
    }
    fail = None if ok else "source_fact_ids outside active proof pool: " + ", ".join(out_of_pool[:48])
    return ok, env, fail


__all__ = [
    "SECTION_KEYS",
    "build_allowed_fact_ids_for_plan_facts",
    "build_graph_evidence_runtime_payload",
    "build_selected_graph_evidence_plan",
    "collect_source_fact_ids_for_section",
    "collect_source_fact_ids_from_bullets_and_ledger",
    "collect_source_fact_ids_from_claim_ledger",
    "collect_source_fact_ids_from_competencies_struct",
    "compute_claim_ledger_union_matches_required_fact_ids",
    "evaluate_active_pool_source_fact_gate",
    "graph_only_proof_pool_metadata",
    "is_disallowed_proof_id",
    "merge_graph_evidence_reporting_into_dict",
    "metric_derivative_fact_id",
    "normalized_graph_evidence_reporting_fields",
    "plan_fact_to_employment_bullet_row",
    "require_section_packet",
    "require_selected_graph_evidence_plan",
    "selection_method_for_section",
    "selected_graph_evidence_plan_from_payload",
    "sha16",
    "slice_row_to_plan_fact",
    "validate_source_fact_ids_within_active_pool",
]
