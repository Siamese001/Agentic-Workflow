"""Shared SelectedRoleFactSet (SRFS) runtime helpers for apps_rg section lanes.

Loads persisted SRFS JSON and derives section slices, validation, ``selected_fact_plan``-shaped
artifacts, and deterministic ``allowed_fact_ids`` (including metric derivatives) in the same
namespace as ``claim_ledger.source_fact_ids`` (``candidate_fact_id`` / ``fact_id``).

This module does not thread CLI or dispatch; callers use it from section lanes and integration
wrappers (e.g. ``exec_summary_srfs_integration``).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

# X2 gate ids that enforce claim_ledger / output source_fact_ids ⊆ SRFS slice (W4).
SRFS_SLICE_SOURCE_FACT_GATE_BY_SECTION: dict[str, str] = {
    "headline": "x2_headline_source_fact_ids_within_srfs_slice",
    "executive_summary": "x2_executive_summary_source_fact_ids_within_srfs_slice",
    "unify_bullets": "x2_unify_bullets_source_fact_ids_within_srfs_slice",
    "unify_narrative": "x2_unify_narrative_source_fact_ids_within_srfs_slice",
    "ibm_bullets": "x2_ibm_bullets_source_fact_ids_within_srfs_slice",
    "ibm_narrative": "x2_ibm_narrative_source_fact_ids_within_srfs_slice",
    "competencies": "x2_competencies_source_fact_ids_within_srfs_slice",
}

_REQUIRED_TOP: tuple[str, ...] = (
    "selection_id",
    "selected_facts_by_section",
    "blocked_facts",
    "facts_requiring_human_confirmation",
    "unsupported_jd_needs",
)

_SECTION_KEYS_FROZEN: frozenset[str] = frozenset(SECTION_KEYS)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def metric_derivative_fact_id(candidate_fact_id: str, metric_raw: str) -> str:
    """Metric-bound derivative ID; must stay aligned with executive_summary SRFS and base-resume metrics."""
    return f"{candidate_fact_id}_metric_{sha16(metric_raw)[:8]}"


def _metric_raw_from_slice(slice_row: dict[str, Any]) -> str:
    raw_metrics = slice_row.get("metric_values") or []
    if not isinstance(raw_metrics, list) or not raw_metrics:
        return ""
    parts = [str(x) for x in raw_metrics if str(x).strip()]
    return "|".join(parts)


def slice_row_to_plan_fact(
    slice_row: dict[str, Any],
    *,
    section_id: str = "executive_summary",
) -> dict[str, Any]:
    """Map a SRFS JSON row to a plan ``fact`` dict.

    HIGH confidence always allowed. MEDIUM allowed only when registry-backed
    ``verification_status`` is ``eligible_medium_with_source_trace`` (commercial seam).
    """
    cid = str(slice_row.get("candidate_fact_id") or "").strip()
    if not cid:
        raise ValueError(f"SRFS {section_id} slice row missing candidate_fact_id")
    conf = str(slice_row.get("confidence") or "").strip().upper()
    vstat = str(slice_row.get("verification_status") or "").strip()
    if conf == "HIGH":
        pass
    elif conf == "MEDIUM" and vstat == "eligible_medium_with_source_trace":
        trace = slice_row.get("source_trace_archive_relpaths") or []
        if not trace:
            raise ValueError(
                f"SRFS {section_id} fact {cid} is claim-eligible MEDIUM but missing source_trace_archive_relpaths"
            )
    else:
        raise ValueError(
            f"SRFS {section_id} fact {cid} has confidence {conf!r} verification={vstat!r}; "
            "only HIGH or claim-eligible MEDIUM with source trace may supply proof"
        )
    claim = str(slice_row.get("claim_text") or "").strip()
    mr = _metric_raw_from_slice(slice_row)
    row: dict[str, Any] = {
        "fact_id": cid,
        "claim_text": claim,
        "candidate_fact_id": cid,
        "srfs_verification_status": vstat or slice_row.get("verification_status"),
        "confidence": conf,
        "claim_eligible_medium": bool(slice_row.get("claim_eligible_medium")),
        "source_trace_archive_relpaths": list(slice_row.get("source_trace_archive_relpaths") or ()),
        "metric_values": tuple(slice_row.get("metric_values") or ()),
        "company_lane": slice_row.get("company_lane"),
        "role_families_supported": slice_row.get("role_families_supported") or [],
    }
    row["metric_raw"] = mr
    row["has_metric"] = bool(mr)
    tech = slice_row.get("technologies")
    row["technologies"] = list(tech) if isinstance(tech, list) else []
    row["domain"] = str(slice_row.get("domain") or "").strip()
    se = slice_row.get("source_employment")
    row["source_employment"] = str(se).strip() if se else ""
    return row


def build_allowed_fact_ids_for_plan_facts(
    facts: list[dict[str, Any]],
) -> tuple[list[str], set[str]]:
    """Return ordered allowed IDs: base ``fact_id`` plus metric derivatives when ``metric_raw`` is set."""
    ordered: list[str] = []
    seen: set[str] = set()

    def _push(fid: str) -> None:
        if fid not in seen:
            seen.add(fid)
            ordered.append(fid)

    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        if not fid:
            continue
        _push(fid)
        mr = fact.get("metric_raw")
        if mr:
            mid = metric_derivative_fact_id(fid, str(mr))
            _push(mid)
    allowed = set(ordered)
    return ordered, allowed


def load_selected_role_fact_set(path: str | Path) -> dict[str, Any]:
    """Load and validate top-level SRFS document keys from JSON (path must exist)."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"SelectedRoleFactSet path not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("SelectedRoleFactSet JSON must deserialize to an object")
    missing = [k for k in _REQUIRED_TOP if k not in data]
    if missing:
        raise ValueError(f"SelectedRoleFactSet JSON missing keys: {missing}")
    return data


def get_section_fact_slice(srfs: dict[str, Any], section_id: str) -> list[dict[str, Any]]:
    """Return normalized list of dict rows for ``section_id``.

    Accepts legacy list::

        selected_facts_by_section.<section_id>: [...]

    or nested::

        selected_facts_by_section.<section_id>: {{ "facts": [...] }}

    Non-dict rows are skipped. Unknown ``section_id`` is rejected.
    """
    if section_id not in _SECTION_KEYS_FROZEN:
        raise ValueError(f"unknown section_id: {section_id!r}")
    sbs = srfs.get("selected_facts_by_section")
    if not isinstance(sbs, dict):
        return []
    raw = sbs.get(section_id)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        facts = raw.get("facts")
        if facts is None:
            return []
        if not isinstance(facts, list):
            raise ValueError(
                f"selected_facts_by_section.{section_id}.facts must be a list when using nested shape"
            )
        return [x for x in facts if isinstance(x, dict)]
    raise ValueError(
        f"selected_facts_by_section.{section_id} must be a list or an object with a 'facts' array"
    )


def validate_section_slice_required(srfs: dict[str, Any], section_id: str) -> None:
    """Fail closed when the section slice is missing, empty, unknown, or has invalid rows (required SRFS mode)."""
    if section_id not in _SECTION_KEYS_FROZEN:
        raise ValueError(f"unknown section_id: {section_id!r}")
    sbs = srfs.get("selected_facts_by_section")
    if not isinstance(sbs, dict) or section_id not in sbs:
        raise ValueError(f"SRFS missing required section slice: {section_id!r}")
    slice_rows = get_section_fact_slice(srfs, section_id)
    if not slice_rows:
        raise ValueError(f"SRFS section slice is empty: {section_id!r}")
    for i, row in enumerate(slice_rows):
        if not isinstance(row, dict):
            raise ValueError(f"SRFS slice row {i} must be an object (section={section_id})")
        cid = str(row.get("candidate_fact_id") or "").strip()
        if not cid:
            raise ValueError(
                f"SRFS slice row {i} missing candidate_fact_id (section={section_id})"
            )


def _selection_method_for(section_id: str) -> str:
    if section_id == "executive_summary":
        return "selected_role_fact_set_executive_summary"
    return f"selected_role_fact_set_{section_id}"


def _no_high_facts_error(section_id: str) -> ValueError:
    if section_id == "executive_summary":
        return ValueError(
            "SelectedRoleFactSet has no executive_summary HIGH facts; "
            "cannot compile role-adaptive executive_summary proof pool."
        )
    return ValueError(
        f"SelectedRoleFactSet has no {section_id} HIGH facts; cannot compile proof pool."
    )


def build_section_fact_plan(srfs: dict[str, Any], section_id: str) -> dict[str, Any]:
    """Build ``selected_fact_plan``-shaped dict: HIGH rows only, same selection_method as legacy exec for that lane."""
    validate_section_slice_required(srfs, section_id)
    slice_rows = get_section_fact_slice(srfs, section_id)
    plan_facts: list[dict[str, Any]] = []
    for r in slice_rows:
        plan_facts.append(slice_row_to_plan_fact(r, section_id=section_id))
    if not plan_facts:
        raise _no_high_facts_error(section_id)
    return {
        "section_id": section_id,
        "selection_method": _selection_method_for(section_id),
        "facts": plan_facts,
        "required_fact_ids": [str(f["fact_id"]) for f in plan_facts],
    }


def build_allowed_fact_ids_for_section(srfs: dict[str, Any], section_id: str) -> tuple[list[str], set[str]]:
    """``validate_section_slice_required`` + plan facts + metric-expanded allowed set (order preserved)."""
    plan = build_section_fact_plan(srfs, section_id)
    return build_allowed_fact_ids_for_plan_facts(list(plan.get("facts") or []))


def build_srfs_integration_envelope(
    srfs_document: dict[str, Any],
    *,
    executive_summary_plan_facts: list[dict[str, Any]],
    artifact_path_resolved: str,
) -> dict[str, Any]:
    """Executive-summary integration envelope (artifact ref + blocked/confirmation IDs). Unchanged contract."""
    blocked = srfs_document.get("blocked_facts") or []
    conf_q = srfs_document.get("facts_requiring_human_confirmation") or []
    ujd = srfs_document.get("unsupported_jd_needs") or []

    blocked_ids = sorted(
        {str(x.get("candidate_fact_id") or "").strip() for x in blocked if isinstance(x, dict)}
    )
    blocked_ids = [x for x in blocked_ids if x]

    conf_ids: list[str] = []
    for item in conf_q:
        if not isinstance(item, dict):
            continue
        nested = item.get("fact") or {}
        if isinstance(nested, dict):
            cid = str(nested.get("candidate_fact_id") or "").strip()
            if cid:
                conf_ids.append(cid)
    conf_ids = sorted(set(conf_ids))

    exec_fact_ids = [str(f["fact_id"]) for f in executive_summary_plan_facts]

    return {
        "artifact_path_resolved": artifact_path_resolved,
        "selection_id": str(srfs_document.get("selection_id") or ""),
        "executive_summary_selected_fact_ids": exec_fact_ids,
        "blocked_facts_count": len(blocked_ids),
        "facts_requiring_human_confirmation_count": len(conf_ids),
        "unsupported_jd_needs_count": len(ujd if isinstance(ujd, list) else []),
        "blocked_candidate_fact_ids": blocked_ids,
        "confirmation_required_candidate_fact_ids": conf_ids,
        "confidence_policy_excerpt": str(srfs_document.get("confidence_policy") or "")[:500],
        "candidate_not_canonical_assertion": srfs_document.get("candidate_not_canonical_assertion"),
        "no_jd_fact_minting_assertion": srfs_document.get("no_jd_fact_minting_assertion"),
    }


def selected_fact_plan_from_srfs(plan_facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Executive_summary plan envelope from already-built HIGH facts (used by exec integration wrapper)."""
    return {
        "section_id": "executive_summary",
        "selection_method": "selected_role_fact_set_executive_summary",
        "facts": plan_facts,
        "required_fact_ids": [str(f["fact_id"]) for f in plan_facts],
    }


def selection_method_for_section(section_id: str) -> str:
    """Public alias for SRFS selection_method strings on ``selected_fact_plan``."""
    return _selection_method_for(section_id)


def plan_fact_to_employment_bullet_row(plan_fact: dict[str, Any]) -> dict[str, Any]:
    """Map SRFS plan ``fact`` dict to employment bullet row shape used by headline/competencies/unify/IBM lanes."""
    fid = str(plan_fact.get("fact_id") or "").strip()
    mr = str(plan_fact.get("metric_raw") or "").strip()
    technologies = plan_fact.get("technologies")
    if not isinstance(technologies, list):
        technologies = []
    se = plan_fact.get("source_employment")
    source_emp = str(se).strip() if se else "SelectedRoleFactSet"
    return {
        "fact_id": fid,
        "claim_text": str(plan_fact.get("claim_text") or ""),
        "source_employment": source_emp,
        "has_metric": bool(mr),
        "metric_raw": mr,
        "domain": str(plan_fact.get("domain") or ""),
        "technologies": technologies,
    }


def base_proof_pool_metadata(
    *,
    section_id: str,
    candidate_fact_pool_count: int,
    allowed_fact_ids_count: int,
    fallback_reason: str = "no_selected_role_fact_set_supplied",
) -> dict[str, Any]:
    return {
        "proof_pool_type": "base_resume_fallback",
        "selected_role_fact_set_used": False,
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": int(allowed_fact_ids_count),
        "srfs_allowed_fact_ids_count": 0,
        "fallback_used": True,
        "fallback_reason": str(fallback_reason),
        "full_resume_srfs_supported": False,
    }


def srfs_proof_pool_metadata(
    *,
    section_id: str,
    candidate_fact_pool_count: int,
    allowed_fact_ids_count: int,
) -> dict[str, Any]:
    n = int(allowed_fact_ids_count)
    return {
        "proof_pool_type": "selected_role_fact_set",
        "selected_role_fact_set_used": True,
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": n,
        "srfs_allowed_fact_ids_count": n,
        "fallback_used": False,
        "fallback_reason": "",
        "full_resume_srfs_supported": False,
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
    return {
        "proof_pool_type": "augmented_skills_graph",
        "selected_role_fact_set_used": False,
        "broad_skills_ledger_used": False,
        "base_resume_claim_authority": False,
        "graph_only_claim_authority": True,
        "broad_skills_ledger_ref": legacy_ledger_ref or None,
        "candidate_fact_ledger_ref": legacy_ledger_ref or None,
        "legacy_skills_ledger_ref": legacy_ledger_ref or None,
        "legacy_skills_ledger_role": "deprecated_reference",
        "broad_skills_ledger_claim_evidence_only": False,
        "broad_skills_ledger_skills_authority": False,
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": n,
        "srfs_allowed_fact_ids_count": n,
        "fallback_used": False,
        "fallback_reason": "",
        "full_resume_srfs_supported": False,
        "c03_graphrag_bound_required": True,
    }


def broad_skills_ledger_proof_pool_metadata(
    *,
    section_id: str,
    candidate_fact_pool_count: int,
    allowed_fact_ids_count: int,
    ledger_ref: str,
) -> dict[str, Any]:
    n = int(allowed_fact_ids_count)
    return {
        "proof_pool_type": "broad_skills_ledger",
        "selected_role_fact_set_used": False,
        "broad_skills_ledger_used": True,
        "broad_skills_ledger_ref": str(ledger_ref),
        "candidate_fact_ledger_ref": str(ledger_ref),
        "broad_skills_ledger_claim_evidence_only": True,
        "broad_skills_ledger_skills_authority": False,
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": n,
        "srfs_allowed_fact_ids_count": 0,
        "fallback_used": False,
        "fallback_reason": "",
        "full_resume_srfs_supported": False,
    }


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
    *,
    srfs_active: bool,
) -> bool | None:
    """Aligns with headline-style required_fact_ids vs claim_ledger union (metric roots)."""
    if not srfs_active:
        return None
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


def normalized_srfs_section_reporting_fields(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> dict[str, Any]:
    """W6: flat SRFS audit fields for section_metric_receipt / consumers."""
    pp = dict(runtime_payload.get("proof_pool_metadata") or {})
    srfs_active = bool(pp.get("selected_role_fact_set_used")) or str(pp.get("proof_pool_type") or "") == (
        "selected_role_fact_set"
    )
    gate_id = SRFS_SLICE_SOURCE_FACT_GATE_BY_SECTION.get(section_id)
    x2_srfs_gate_status = "NOT_APPLICABLE"
    out_of_slice: list[str] = []
    srfs_allowed_from_gate: int | None = None

    if srfs_active and gate_id:
        gate = next((g for g in x2_gates if g.get("gate_id") == gate_id), None)
        if gate is None:
            x2_srfs_gate_status = "UNKNOWN"
        elif gate.get("pass"):
            x2_srfs_gate_status = "PASS"
        else:
            x2_srfs_gate_status = "FAIL"
        if gate is not None:
            ov = gate.get("observed_value")
            if isinstance(ov, dict):
                oos = ov.get("out_of_slice_fact_ids")
                if isinstance(oos, list):
                    out_of_slice = [str(x) for x in oos]
                sac = ov.get("srfs_allowed_fact_ids_count")
                if isinstance(sac, int):
                    srfs_allowed_from_gate = sac
    elif srfs_active:
        x2_srfs_gate_status = "UNKNOWN"

    if not srfs_active:
        out_of_slice = []

    req_ids = (selected_fact_plan or {}).get("required_fact_ids") if isinstance(selected_fact_plan, dict) else None
    req_count = len(req_ids or []) if isinstance(req_ids, list) else 0

    pool_type = str(pp.get("proof_pool_type") or ("selected_role_fact_set" if srfs_active else "base_resume_fallback"))
    meta_allowed = int(pp.get("allowed_fact_ids_count") or 0)
    meta_srfs_allowed = int(pp.get("srfs_allowed_fact_ids_count") or 0)
    if srfs_allowed_from_gate is not None:
        meta_srfs_allowed = srfs_allowed_from_gate

    return {
        "proof_pool_type": pool_type,
        "selected_role_fact_set_used": bool(srfs_active),
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(pp.get("candidate_fact_pool_count") or 0),
        "allowed_fact_ids_count": meta_allowed,
        "required_fact_ids_count": req_count,
        "claim_ledger_union_matches_required_fact_ids": compute_claim_ledger_union_matches_required_fact_ids(
            selected_fact_plan if isinstance(selected_fact_plan, dict) else None,
            claim_ledger,
            srfs_active=srfs_active,
        ),
        "out_of_slice_fact_ids": list(out_of_slice),
        "fallback_used": bool(pp.get("fallback_used", not srfs_active)),
        "fallback_reason": str(pp.get("fallback_reason") or ""),
        "x2_srfs_gate_status": x2_srfs_gate_status,
        "srfs_allowed_fact_ids_count": meta_srfs_allowed if srfs_active else 0,
        "full_resume_srfs_supported": False,
    }


def merge_normalized_srfs_reporting_into_dict(
    receipt: dict[str, Any],
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> None:
    """Mutates ``receipt`` with :func:`normalized_srfs_section_reporting_fields` (W6)."""
    receipt.update(
        normalized_srfs_section_reporting_fields(
            section_id=section_id,
            runtime_payload=runtime_payload,
            x2_gates=x2_gates,
            selected_fact_plan=selected_fact_plan,
            claim_ledger=claim_ledger,
        )
    )


def resolve_srfs_section_proof_bundle(
    srfs_path: str | Path,
    section_id: str,
) -> tuple[dict[str, Any], list[str], set[str], dict[str, Any]]:
    """Load SRFS JSON, validate slice, return (selected_fact_plan, ordered_allowed, allowed_set, proof_pool_metadata)."""
    doc = load_selected_role_fact_set(srfs_path)
    plan = build_section_fact_plan(doc, section_id)
    facts = list(plan.get("facts") or [])
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    meta = srfs_proof_pool_metadata(
        section_id=section_id,
        candidate_fact_pool_count=len(facts),
        allowed_fact_ids_count=len(allowed),
    )
    return plan, ordered, allowed, meta


def stub_source_fact_ids_for_allowed(allowed_sorted: list[str], *, max_ids: int = 6) -> list[str]:
    """Deterministic subset of allowed IDs for offline contract stubs (prefer non-metric tokens)."""
    bases: list[str] = []
    for x in allowed_sorted:
        if "_metric_" in x:
            continue
        if x not in bases:
            bases.append(x)
        if len(bases) >= max_ids:
            break
    if bases:
        return bases
    return list(allowed_sorted)[:max_ids]


def is_srfs_disallowed_proof_id(fid: str) -> bool:
    """JD/briefing/target/companion-shaped proof tokens and empty IDs are never SRFS-proofable."""
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
    """All claim_ledger proof tokens (full strings, including metric derivatives)."""
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
    """Unify / IBM bullets: bullet wrappers plus claim_ledger."""
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
    """Competencies: category source_fact_ids, term-level ids, and claim_ledger."""
    ids = collect_source_fact_ids_from_claim_ledger(claim_ledger)
    for cat in competencies or []:
        if not isinstance(cat, dict):
            continue
        for fid in cat.get("source_fact_ids") or []:
            ids.append(str(fid))
        for t in cat.get("terms") or []:
            if isinstance(t, dict):
                if t.get("source_fact_id") is not None:
                    ids.append(str(t["source_fact_id"]))
                for x in t.get("source_fact_ids") or []:
                    ids.append(str(x))
    return ids


def collect_source_fact_ids_for_section(
    section_id: str,
    *,
    claim_ledger: Iterable[Any] | None = None,
    parsed_output: dict[str, Any] | None = None,
    competencies: Iterable[Any] | None = None,
) -> list[str]:
    """Dispatch collection for W4 SRFS slice gates."""
    if section_id in ("unify_bullets", "ibm_bullets"):
        return collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
    if section_id == "competencies":
        return collect_source_fact_ids_from_competencies_struct(competencies, claim_ledger)
    return collect_source_fact_ids_from_claim_ledger(claim_ledger)


def validate_source_fact_ids_within_srfs_slice(
    *,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, list[str]]:
    """Every emitted id must appear exactly in ``allowed_fact_ids`` (includes metric hash tokens)."""
    bad: list[str] = []
    seen: set[str] = set()
    for raw in collected_ids:
        s = str(raw).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        if is_srfs_disallowed_proof_id(s):
            bad.append(s)
            continue
        if s not in allowed_fact_ids:
            bad.append(s)
    return (len(bad) == 0, sorted(set(bad)))


def evaluate_srfs_slice_source_fact_gate(
    *,
    section_id: str,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, dict[str, Any], str | None]:
    """Build X2 gate pass/fail plus W4 metadata envelope (``observed_value``)."""
    ok, oos = validate_source_fact_ids_within_srfs_slice(
        collected_ids=collected_ids,
        allowed_fact_ids=allowed_fact_ids,
    )
    env: dict[str, Any] = {
        "x2_srfs_gate_status": ok,
        "out_of_slice_fact_ids": oos,
        "srfs_allowed_fact_ids_count": len(allowed_fact_ids),
        "selected_role_fact_set_used": True,
        "srfs_section_id": section_id,
    }
    fail = None if ok else "source_fact_ids outside SRFS slice: " + ", ".join(oos[:48])
    return ok, env, fail


__all__ = [
    "SRFS_SLICE_SOURCE_FACT_GATE_BY_SECTION",
    "SECTION_KEYS",
    "build_allowed_fact_ids_for_plan_facts",
    "build_allowed_fact_ids_for_section",
    "build_section_fact_plan",
    "build_srfs_integration_envelope",
    "get_section_fact_slice",
    "load_selected_role_fact_set",
    "metric_derivative_fact_id",
    "selected_fact_plan_from_srfs",
    "selection_method_for_section",
    "plan_fact_to_employment_bullet_row",
    "base_proof_pool_metadata",
    "broad_skills_ledger_proof_pool_metadata",
    "graph_only_proof_pool_metadata",
    "compute_claim_ledger_union_matches_required_fact_ids",
    "merge_normalized_srfs_reporting_into_dict",
    "normalized_srfs_section_reporting_fields",
    "srfs_proof_pool_metadata",
    "resolve_srfs_section_proof_bundle",
    "stub_source_fact_ids_for_allowed",
    "sha16",
    "slice_row_to_plan_fact",
    "validate_section_slice_required",
    "is_srfs_disallowed_proof_id",
    "collect_source_fact_ids_from_claim_ledger",
    "collect_source_fact_ids_from_bullets_and_ledger",
    "collect_source_fact_ids_from_competencies_struct",
    "collect_source_fact_ids_for_section",
    "validate_source_fact_ids_within_srfs_slice",
    "evaluate_srfs_slice_source_fact_gate",
]
