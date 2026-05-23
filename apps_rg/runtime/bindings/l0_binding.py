"""apps_rg L0 binding — profile-driven RouteContract for resume_generation.

Canonical route profiles: apps_rg/config/domain_contract/route_profiles.yaml
Per plan p3.2_apps-rg-l0-critical-gaps-remediation-a3f8e1.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from agentic_core.runtime.contracts.route_gate_receipt import RouteGateReceipt

__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "_MANAGED_ROUTE_TEST_FLAG",
    "RouteProfileNotFoundError",
    "RouteProfileSchemaError",
    "l0_route_apps_rg",
    "reset_route_profiles_cache",
]

# W9 / L3 harness — env var name for managed-workflow test activation (stable symbol)
_MANAGED_ROUTE_TEST_FLAG = "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"

APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-w3"
# Module-level spine labels mirror the default grounded managed profile (SSOT: route_profiles.yaml).
APPS_RG_ROUTE_FAMILY: str = "R3R4_MANAGED_WORKFLOW"
APPS_RG_ROUTE_ID: str = "R4_MANAGED_DRAFT"
APPS_RG_CACHE_ELIGIBILITY: str = "profile_driven"
APPS_RG_HITL_POSTURE: str = "advisory"
APPS_RG_FALLBACK_ROUTE_ID: str = "R0_PASSTHROUGH"

_ROUTE_PROFILE_RELPATH = Path("apps_rg") / "config" / "domain_contract" / "route_profiles.yaml"

_PROFILE_CACHE: list[dict[str, Any]] | None = None


class RouteProfileNotFoundError(FileNotFoundError):
    """Canonical route profile missing on disk."""


class RouteProfileSchemaError(ValueError):
    """route_profiles.yaml failed structural validation."""


def reset_route_profiles_cache() -> None:
    """Test helper — clears the in-process route profile cache."""
    global _PROFILE_CACHE
    _PROFILE_CACHE = None


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[4]


def _load_profiles() -> list[dict[str, Any]]:
    global _PROFILE_CACHE
    if _PROFILE_CACHE is not None:
        return _PROFILE_CACHE
    path = _repo_root() / _ROUTE_PROFILE_RELPATH
    if not path.is_file():
        raise RouteProfileNotFoundError(f"Canonical route profile missing: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise RouteProfileSchemaError("route_profiles.yaml must be a non-empty YAML list")
    for row in raw:
        if not isinstance(row, dict) or "spine" not in row:
            raise RouteProfileSchemaError("each profile row must be a dict with 'spine'")
    _PROFILE_CACHE = raw
    return _PROFILE_CACHE


def _conditions_match(conditions: Mapping[str, Any], plan: L1PlanContract) -> bool:
    if not conditions:
        return False
    gen = (plan.task_spec or {}).get("generation_mode", "")
    for key, expected in conditions.items():
        if key == "generation_mode":
            if gen != expected:
                return False
        else:
            if getattr(plan, key, None) != expected:
                return False
    return True


def _select_profile(plan: L1PlanContract) -> dict[str, Any]:
    rows = _load_profiles()
    for row in rows:
        cond = row.get("conditions")
        if isinstance(cond, dict) and cond and _conditions_match(cond, plan):
            return row
    for row in rows:
        cond = row.get("conditions")
        if not cond:
            return row
    raise RouteProfileSchemaError("no matching route profile row (missing default catch-all)")


def _graph_policy_from_row(row: dict[str, Any]) -> GraphTraversePolicy | None:
    gt = row.get("graph_traverse")
    if not isinstance(gt, dict):
        return None
    if not gt.get("graph_expansion_allowed"):
        return None
    return GraphTraversePolicy(
        graph_expansion_allowed=bool(gt.get("graph_expansion_allowed", False)),
        max_hops=int(gt.get("max_hops", 0)),
        max_nodes=int(gt.get("max_nodes", 0)),
        max_edges=int(gt.get("max_edges", 0)),
        allowed_relation_types=tuple(str(x) for x in (gt.get("allowed_relation_types") or ())),
        contradiction_scan_enabled=bool(gt.get("contradiction_scan_enabled", False)),
        supersession_scan_enabled=bool(gt.get("supersession_scan_enabled", False)),
        graph_adapter_ref=str(gt.get("graph_adapter_ref", "") or ""),
        live_wiring_deferred=bool(gt.get("live_wiring_deferred", True)),
        wiring_gate=str(gt.get("wiring_gate", "") or ""),
    )


def _evaluate_route_gates(plan: L1PlanContract, row: dict[str, Any]) -> tuple[RouteGateReceipt, ...]:
    """Strict gate receipts — no manufactured PASS on missing facts (p3.2 W3)."""
    receipts: list[RouteGateReceipt] = []
    qs = dict(plan.query_spec or {})
    sup = dict(plan.support_expectation or {})
    budget = row.get("budget_constraints") if isinstance(row.get("budget_constraints"), dict) else {}

    # G07 — grounding prerequisites
    if plan.grounding_required:
        facts = bool(qs.get("jd_hash")) and bool(qs.get("resume_hash"))
        receipts.append(
            RouteGateReceipt(
                gate_id="G07_GROUNDING_READINESS",
                verdict="PASS" if facts else "UNKNOWN",
                score=1.0 if facts else 0.0,
                facts_present=facts,
                reason="jd_hash+resume_hash required for grounding PASS",
            )
        )
    else:
        receipts.append(
            RouteGateReceipt(
                gate_id="G07_GROUNDING_READINESS",
                verdict="NOT_APPLICABLE",
                score=0.0,
                facts_present=True,
                reason="grounding not required",
            )
        )

    personalization = bool(row.get("personalization_default", False))
    if personalization:
        facts = bool(sup)
        receipts.append(
            RouteGateReceipt(
                gate_id="G08_PERSONALIZATION",
                verdict="PASS" if facts else "UNKNOWN",
                score=1.0 if facts else 0.0,
                facts_present=facts,
                reason="support_expectation must be present for personalization policy",
            )
        )
    else:
        receipts.append(
            RouteGateReceipt(
                gate_id="G08_PERSONALIZATION",
                verdict="NOT_APPLICABLE",
                score=0.0,
                facts_present=True,
                reason="personalization not active for this profile",
            )
        )

    enforced = bool(budget.get("enforced", False))
    profile_present = bool(budget.get("profile_present", False))
    if enforced:
        ok = profile_present
        receipts.append(
            RouteGateReceipt(
                gate_id="G10_BUDGET",
                verdict="PASS" if ok else "FAIL",
                score=1.0 if ok else 0.0,
                facts_present=ok,
                reason="budget enforcement requires present profile",
            )
        )
    else:
        receipts.append(
            RouteGateReceipt(
                gate_id="G10_BUDGET",
                verdict="NOT_APPLICABLE",
                score=0.0,
                facts_present=False,
                reason="budget enforcement disabled in route profile",
            )
        )

    # G20 — treat as budget envelope gate (p3.2): PASS only with enforced+bound profile
    if enforced and profile_present:
        receipts.append(
            RouteGateReceipt(
                gate_id="G20_ROUTE_BUDGET",
                verdict="PASS",
                score=1.0,
                facts_present=True,
                reason="budget profile present and enforced",
            )
        )
    elif enforced:
        receipts.append(
            RouteGateReceipt(
                gate_id="G20_ROUTE_BUDGET",
                verdict="UNKNOWN",
                score=0.0,
                facts_present=False,
                reason="enforced without profile_present",
            )
        )
    else:
        receipts.append(
            RouteGateReceipt(
                gate_id="G20_ROUTE_BUDGET",
                verdict="UNKNOWN",
                score=0.0,
                facts_present=False,
                reason="budget profile not enforced — UNKNOWN per p3.2 policy",
            )
        )

    return tuple(receipts)


def l0_route_apps_rg(plan: L1PlanContract) -> RouteContract:
    """Select apps_rg L0 route from L1PlanContract using fail-closed YAML profiles."""
    if not isinstance(plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_rg expects L1PlanContract, got {type(plan).__name__}. "
            "Build a plan via l1_plan_apps_rg(validated_request) first."
        )

    row = _select_profile(plan)
    spine = row["spine"]
    if not isinstance(spine, dict):
        raise RouteProfileSchemaError("spine must be a mapping")

    route_family = str(spine.get("route_family", ""))
    route_id = str(spine.get("route_id", ""))
    execution_form = str(spine.get("execution_form", ""))
    l3_required = bool(spine.get("l3_required", False))

    managed = row.get("managed_workflow") if isinstance(row.get("managed_workflow"), dict) else {}
    workflow_ref = str(managed.get("workflow_ref", "") or "")
    workflow_manifest_ref = str(managed.get("workflow_manifest_ref", "") or "")
    workflow_registry_ref = str(managed.get("workflow_registry_ref", "") or "")

    test_mode = os.environ.get("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "").strip() in ("1", "true", "yes")
    exec_override = os.environ.get("APPS_RG_EXECUTION_FORM", "").strip().lower()
    if exec_override == "managed_workflow":
        execution_form = "MANAGED_WORKFLOW"
        l3_required = True

    if execution_form.upper() == "MANAGED_WORKFLOW" and test_mode:
        manifest_path = (
            _repo_root()
            / "apps_rg"
            / "config"
            / "fixtures"
            / "workflow_manifest.resume_generation.v1.minimal.yaml"
        )
        digest = ""
        rel = ""
        if manifest_path.is_file():
            digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            rel = str(manifest_path.relative_to(_repo_root())).replace("\\", "/")
        registry_resolution_receipt_ref = json.dumps(
            {
                "status": "registered_not_active",
                "resolver": "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED",
                "workflow_manifest_path": rel,
                "manifest_digest": digest,
            },
            separators=(",", ":"),
        )
        if not workflow_ref:
            workflow_ref = "wfm::apps_rg::resume_generation::v1"
        if not workflow_manifest_ref:
            workflow_manifest_ref = workflow_ref
        if not workflow_registry_ref:
            workflow_registry_ref = "apps_rg/config/route_registry.yaml"
    else:
        registry_resolution_receipt_ref = ""

    gen_mode = str((plan.task_spec or {}).get("generation_mode", "") or "")
    work_shape = "full_resume_generation" if plan.merge_required_hint else "narrow_regeneration"
    task_shape = gen_mode or "unknown"
    route_profile_ref = str(row.get("route_profile_id", "") or "")
    provider_ref = str(row.get("provider_model_requirement_ref", "") or "")

    personalization_required = bool(row.get("personalization_default", False))
    if personalization_required:
        cache_eligibility = {
            "r1a_exact": False,
            "r1b_semantic": False,
            "r3_grounded": bool(plan.grounding_required),
            "r4_action": False,
        }
    else:
        cache_eligibility = {
            "r1a_exact": True,
            "r1b_semantic": True,
            "r3_grounded": bool(plan.grounding_required),
            "r4_action": False,
        }

    receipts = _evaluate_route_gates(plan, row)
    gate_strings = tuple(r.to_runtime_gate_ref() for r in receipts)

    allowed: frozenset[str] = frozenset()
    if execution_form.upper() == "MANAGED_WORKFLOW" and l3_required:
        allowed = frozenset({"L3"})

    graph_policy = _graph_policy_from_row(row)
    if not plan.grounding_required:
        graph_policy = None

    ts = datetime.now(timezone.utc).isoformat()
    policy_path = str(_ROUTE_PROFILE_RELPATH).replace("\\", "/")

    route = RouteContract(
        request_id=plan.request_id,
        run_id=plan.run_id,
        app_id=plan.app_id,
        trace_id=plan.trace_id,
        route_id=route_id,
        l3_required=l3_required,
        grounding_required=plan.grounding_required,
        model_generation_required=plan.model_generation_required,
        write_authority_present=plan.write_authority_present,
        tenant_id=plan.tenant_id,
        route_family=route_family,
        execution_form=execution_form,
        cache_eligibility=cache_eligibility,
        action_required=False,
        workflow_ref=workflow_ref,
        workflow_manifest_ref=workflow_manifest_ref,
        workflow_registry_ref=workflow_registry_ref,
        registry_resolution_receipt_ref=registry_resolution_receipt_ref,
        route_gate_refs=gate_strings,
        route_gate_receipts=receipts,
        allowed_next_stage=allowed,
        provider_model_requirement_ref=provider_ref,
        personalization_required=personalization_required,
        work_shape=work_shape,
        task_shape=task_shape,
        route_profile_ref=route_profile_ref,
        route_policy_ref=f"{policy_path}#{route_profile_ref}",
        reason_codes=(f"execution_form={execution_form}",),
        routing_timestamp=ts,
        l5_certification_ref=plan.l5_certification_ref,
        graph_traverse_policy=graph_policy,
    )

    from apps_rg.runtime.bindings.l0_route_evidence import stamp_route_evidence

    return stamp_route_evidence(
        route,
        plan=plan,
        route_id=route_id,
        route_family=route_family,
        execution_form=execution_form,
        l3_required=l3_required,
        route_profile_ref=route_profile_ref,
        cache_eligibility=cache_eligibility,
    )
