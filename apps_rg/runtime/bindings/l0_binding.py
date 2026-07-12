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
    "CANONICAL_L0_ROUTE_IDS",
    "_MANAGED_ROUTE_TEST_FLAG",
    "RouteProfileNotFoundError",
    "RouteProfileSchemaError",
    "l0_route_apps_rg",
    "reset_route_profiles_cache",
]

# W9 / L3 harness — env var name for managed-workflow test activation (stable symbol)
_MANAGED_ROUTE_TEST_FLAG = "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"
_MANAGED_ROUTE_PRODUCTION_FLAG = "APPS_RG_ENABLE_MANAGED_WORKFLOW_L0"

CANONICAL_L0_ROUTE_IDS: frozenset[str] = frozenset(
    {
        "R1A_EXACT_CACHE",
        "R1B_SEMANTIC_CACHE",
        "R5_FALLBACK",
        "R3_SIMPLE_GROUNDED_READ",
        "R4_SINGLE_ACTION",
        "R3R4_MANAGED_WORKFLOW",
    }
)
_TERMINAL_ROUTE_IDS = frozenset({"R1A_EXACT_CACHE", "R1B_SEMANTIC_CACHE", "R5_FALLBACK"})
_ROUTE_SELECTION_ORDER: dict[str, int] = {
    "R1A_EXACT_CACHE": 10,
    "R1B_SEMANTIC_CACHE": 20,
    "R5_FALLBACK": 30,
    "R3_SIMPLE_GROUNDED_READ": 40,
    "R4_SINGLE_ACTION": 50,
    "R3R4_MANAGED_WORKFLOW": 60,
}

APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-w3"
# Module-level spine labels mirror the default grounded managed profile (SSOT: route_profiles.yaml).
APPS_RG_ROUTE_FAMILY: str = "R3R4_MANAGED_WORKFLOW"
APPS_RG_ROUTE_ID: str = "R3R4_MANAGED_WORKFLOW"
APPS_RG_CACHE_ELIGIBILITY: str = "profile_driven"
APPS_RG_HITL_POSTURE: str = "advisory"
APPS_RG_FALLBACK_ROUTE_ID: str = "R5_FALLBACK"

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
    raw = yaml.full_load(path.read_bytes().decode("utf-8"))
    if not isinstance(raw, list) or not raw:
        raise RouteProfileSchemaError("route_profiles.yaml must be a non-empty YAML list")
    for idx, row in enumerate(raw):
        _validate_profile_row(row, idx)
    _PROFILE_CACHE = raw
    return _PROFILE_CACHE


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _is_test_posture() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST") or _truthy_env("APPS_RG_L0_TEST_POSTURE"))


def _validate_profile_row(row: Any, idx: int) -> None:
    if not isinstance(row, dict) or "spine" not in row:
        raise RouteProfileSchemaError(f"profile row {idx} must be a dict with 'spine'")
    for key in (
        "route_profile_id",
        "app_id",
        "task_class",
        "status",
        "production_enabled",
        "test_only",
        "required_activation_flags",
    ):
        if key not in row:
            raise RouteProfileSchemaError(f"profile row {idx} missing required key {key!r}")
    if not isinstance(row["production_enabled"], bool):
        raise RouteProfileSchemaError(f"profile row {idx} production_enabled must be bool")
    if not isinstance(row["test_only"], bool):
        raise RouteProfileSchemaError(f"profile row {idx} test_only must be bool")
    flags = row["required_activation_flags"]
    if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
        raise RouteProfileSchemaError(
            f"profile row {idx} required_activation_flags must be a list[str]"
        )
    spine = row["spine"]
    if not isinstance(spine, dict):
        raise RouteProfileSchemaError(f"profile row {idx} spine must be a mapping")
    for key in ("canonical_route_id", "app_route_id", "route_family", "execution_form", "l3_required"):
        if key not in spine:
            raise RouteProfileSchemaError(f"profile row {idx} spine missing {key!r}")
    canonical_route_id = str(spine.get("canonical_route_id") or "")
    route_family = str(spine.get("route_family") or "")
    if canonical_route_id not in CANONICAL_L0_ROUTE_IDS:
        raise RouteProfileSchemaError(
            f"profile row {idx} canonical_route_id {canonical_route_id!r} is not canonical"
        )
    if route_family not in CANONICAL_L0_ROUTE_IDS:
        raise RouteProfileSchemaError(
            f"profile row {idx} route_family {route_family!r} is not canonical"
        )
    legacy_route_id = str(spine.get("route_id") or "")
    if legacy_route_id and legacy_route_id != canonical_route_id:
        raise RouteProfileSchemaError(
            f"profile row {idx} route_id must not contradict canonical_route_id"
        )
    if not str(spine.get("app_route_id") or ""):
        raise RouteProfileSchemaError(f"profile row {idx} app_route_id must be non-empty")
    if canonical_route_id in _TERMINAL_ROUTE_IDS and bool(spine.get("l3_required")):
        raise RouteProfileSchemaError(f"profile row {idx} terminal routes cannot require L3")


def _condition_value(plan: L1PlanContract, key: str) -> Any:
    if key == "generation_mode":
        return (plan.task_spec or {}).get("generation_mode", "")
    if "." not in key:
        return getattr(plan, key, None)
    root, *parts = key.split(".")
    value: Any
    if root == "task_spec":
        value = plan.task_spec or {}
    elif root == "query_spec":
        value = plan.query_spec or {}
    elif root == "support_expectation":
        value = plan.support_expectation or {}
    elif root == "output_expectation":
        value = plan.output_expectation or {}
    elif root == "policy_refs":
        value = plan.policy_refs or {}
    elif root == "route_hints":
        return None
    else:
        value = getattr(plan, root, None)
    for part in parts:
        if isinstance(value, Mapping):
            value = value.get(part)
        else:
            return None
    return value


def _conditions_match(conditions: Mapping[str, Any], plan: L1PlanContract) -> bool:
    if not conditions:
        return False
    for key, expected in conditions.items():
        if _condition_value(plan, str(key)) != expected:
            return False
    return True


def _profile_active(row: dict[str, Any]) -> bool:
    flags = [str(flag) for flag in (row.get("required_activation_flags") or ())]
    if any(_truthy_env(flag) for flag in flags):
        return True
    if bool(row.get("test_only", False)):
        return _is_test_posture()
    return bool(row.get("production_enabled", False))


def _route_order(row: dict[str, Any]) -> tuple[int, int, str]:
    spine = row["spine"]
    canonical_route_id = str(spine["canonical_route_id"])
    return (
        _ROUTE_SELECTION_ORDER[canonical_route_id],
        int(row.get("selection_order", 0) or 0),
        str(row.get("route_profile_id", "")),
    )


def _select_profile(plan: L1PlanContract) -> dict[str, Any]:
    rows = _load_profiles()
    active_rows = [row for row in rows if _profile_active(row)]
    explicit_matches = [
        row
        for row in active_rows
        if isinstance(row.get("conditions"), dict)
        and row.get("conditions")
        and _conditions_match(row["conditions"], plan)
    ]
    if explicit_matches:
        explicit_matches.sort(key=_route_order)
        best_order = _route_order(explicit_matches[0])[:2]
        tied = [row for row in explicit_matches if _route_order(row)[:2] == best_order]
        if len(tied) > 1:
            names = ", ".join(str(row.get("route_profile_id", "")) for row in tied)
            raise RouteProfileSchemaError(f"ambiguous active route profile matches: {names}")
        return explicit_matches[0]
    default_rows = [
        row
        for row in active_rows
        if not row.get("conditions")
    ]
    if len(default_rows) == 1:
        return default_rows[0]
    if len(default_rows) > 1:
        names = ", ".join(str(row.get("route_profile_id", "")) for row in default_rows)
        raise RouteProfileSchemaError(f"ambiguous default route profiles: {names}")
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
                verdict="NOT_APPLICABLE",
                score=0.0,
                facts_present=False,
                reason="budget profile not enforced",
            )
        )

    return tuple(receipts)


def _required_gate_ids(plan: L1PlanContract, row: dict[str, Any]) -> frozenset[str]:
    budget = row.get("budget_constraints") if isinstance(row.get("budget_constraints"), dict) else {}
    required: set[str] = set()
    if plan.grounding_required:
        required.add("G07_GROUNDING_READINESS")
    if bool(row.get("personalization_default", False)):
        required.add("G08_PERSONALIZATION")
    if bool(budget.get("enforced", False)):
        required.update({"G10_BUDGET", "G20_ROUTE_BUDGET"})
    return frozenset(required)


def _blocking_gate_ids(
    plan: L1PlanContract,
    row: dict[str, Any],
    receipts: tuple[RouteGateReceipt, ...],
) -> tuple[str, ...]:
    required = _required_gate_ids(plan, row)
    return tuple(
        receipt.gate_id
        for receipt in receipts
        if receipt.gate_id in required and receipt.verdict in {"FAIL", "UNKNOWN"}
    )


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_refs(row: dict[str, Any]) -> tuple[str, ...]:
    repo_root = _repo_root()
    policy_path = repo_root / _ROUTE_PROFILE_RELPATH
    registry_path = repo_root / "apps_rg" / "config" / "route_registry.yaml"
    policy_hash = _sha256_json(row)
    blueprint_hash = _file_sha256(policy_path)
    registry_digests = [
        f"route_profiles={blueprint_hash}",
        f"route_registry={_file_sha256(registry_path)}",
    ]
    return (
        f"policy_hash:{policy_hash}",
        f"blueprint_hash:{blueprint_hash}",
        f"registry_digest_set:{'|'.join(registry_digests)}",
    )


def _stable_replay_key(plan: L1PlanContract, *, route_id: str, route_profile_ref: str) -> str:
    if plan.replay_key:
        return plan.replay_key
    payload = {
        "request_id": plan.request_id,
        "run_id": plan.run_id,
        "trace_id": plan.trace_id,
        "app_id": plan.app_id,
        "route_id": route_id,
        "route_profile_ref": route_profile_ref,
    }
    return f"l0replay:{_sha256_json(payload)[:24]}"


def _receipt_ref(plan: L1PlanContract, *keys: str) -> str:
    task_spec = dict(plan.task_spec or {})
    for key in keys:
        value = str(task_spec.get(key) or "").strip()
        if value:
            return value
    return ""


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

    route_id = str(spine.get("canonical_route_id", ""))
    app_route_id = str(spine.get("app_route_id", ""))
    route_family = str(spine.get("route_family", ""))
    execution_form = str(spine.get("execution_form", ""))
    l3_required = bool(spine.get("l3_required", False))
    terminal_route = route_id in _TERMINAL_ROUTE_IDS

    managed = row.get("managed_workflow") if isinstance(row.get("managed_workflow"), dict) else {}
    workflow_ref = str(managed.get("workflow_ref", "") or "")
    workflow_manifest_ref = str(managed.get("workflow_manifest_ref", "") or "")
    workflow_registry_ref = str(managed.get("workflow_registry_ref", "") or "")

    test_mode = os.environ.get("APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED", "").strip() in ("1", "true", "yes")
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
    replay_key = _stable_replay_key(plan, route_id=route_id, route_profile_ref=route_profile_ref)

    personalization_required = bool(row.get("personalization_default", False))
    if route_id == "R1A_EXACT_CACHE":
        cache_eligibility = {
            "r1a_exact": True,
            "r1b_semantic": False,
            "r3_grounded": False,
            "r4_action": False,
        }
    elif route_id == "R1B_SEMANTIC_CACHE":
        cache_eligibility = {
            "r1a_exact": False,
            "r1b_semantic": True,
            "r3_grounded": False,
            "r4_action": False,
        }
    elif route_id == "R5_FALLBACK":
        cache_eligibility = {
            "r1a_exact": False,
            "r1b_semantic": False,
            "r3_grounded": False,
            "r4_action": False,
        }
    elif personalization_required:
        cache_eligibility = {
            "r1a_exact": False,
            "r1b_semantic": False,
            "r3_grounded": bool(plan.grounding_required),
            "r4_action": route_id == "R4_SINGLE_ACTION",
        }
    else:
        cache_eligibility = {
            "r1a_exact": True,
            "r1b_semantic": True,
            "r3_grounded": bool(plan.grounding_required),
            "r4_action": route_id == "R4_SINGLE_ACTION",
        }

    receipts = _evaluate_route_gates(plan, row)
    blocking_gate_ids = _blocking_gate_ids(plan, row, receipts)
    gate_strings = tuple(r.to_runtime_gate_ref() for r in receipts)

    allowed: frozenset[str] = frozenset()
    if (
        execution_form.upper() == "MANAGED_WORKFLOW"
        and l3_required
        and not terminal_route
        and not blocking_gate_ids
    ):
        allowed = frozenset({"L3"})

    graph_policy = _graph_policy_from_row(row)
    if terminal_route or not plan.grounding_required:
        graph_policy = None

    ts = datetime.now(timezone.utc).isoformat()
    policy_path = str(_ROUTE_PROFILE_RELPATH).replace("\\", "/")
    hitl_posture = str(row.get("hitl_posture") or "none")
    hitl_gate_ref = str(row.get("hitl_required_gate_ref") or "")
    route_gate_status = "BLOCKED" if blocking_gate_ids else "PASS"
    block_reason = ""
    if blocking_gate_ids:
        block_reason = "required_gate_not_pass"

    r1a_receipt = _receipt_ref(plan, "r1a_receipt_ref", "exact_cache_receipt_ref", "cache_receipt_ref")
    r1b_receipt = _receipt_ref(plan, "r1b_receipt_ref", "semantic_cache_receipt_ref", "cache_receipt_ref")
    r5_receipt = _receipt_ref(plan, "r5_fallback_receipt_ref", "fallback_receipt_ref")
    terminal_reason = ""
    if route_id == "R1A_EXACT_CACHE":
        terminal_reason = "exact_cache_hit"
    elif route_id == "R1B_SEMANTIC_CACHE":
        terminal_reason = "semantic_cache_hit"
    elif route_id == "R5_FALLBACK":
        terminal_reason = "fallback_or_abstain"

    reason_codes = (
        f"execution_form={execution_form}",
        f"canonical_route_id={route_id}",
        f"app_route_id={app_route_id}",
        f"route_gate_status={route_gate_status}",
        f"hitl_posture={hitl_posture}",
    )
    if hitl_gate_ref:
        reason_codes += (f"hitl_required_gate_ref={hitl_gate_ref}",)
    if blocking_gate_ids:
        reason_codes += (
            f"blocking_gate_ids={'|'.join(blocking_gate_ids)}",
            f"route_block_reason={block_reason}",
        )
    if terminal_reason:
        reason_codes += (f"terminal_reason={terminal_reason}",)

    route = RouteContract(
        request_id=plan.request_id,
        run_id=plan.run_id,
        app_id=plan.app_id,
        trace_id=plan.trace_id,
        route_id=route_id,
        l3_required=l3_required,
        grounding_required=plan.grounding_required,
        apps_research_call_required=plan.apps_research_call_required,
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
        cache_lookup_r1a_receipt=r1a_receipt if route_id == "R1A_EXACT_CACHE" else "",
        cache_lookup_r1b_receipt=r1b_receipt if route_id == "R1B_SEMANTIC_CACHE" else "",
        cache_lookup_r5_receipt=r5_receipt if route_id == "R5_FALLBACK" else "",
        r1a_lookup_receipt_ref=r1a_receipt if route_id == "R1A_EXACT_CACHE" else "",
        r1b_lookup_receipt_ref=r1b_receipt if route_id == "R1B_SEMANTIC_CACHE" else "",
        r5_fallback_receipt_ref=r5_receipt if route_id == "R5_FALLBACK" else "",
        route_gate_refs=gate_strings,
        route_gate_receipts=receipts,
        allowed_next_stage=allowed,
        provider_model_requirement_ref=provider_ref,
        personalization_required=personalization_required,
        work_shape=work_shape,
        task_shape=task_shape,
        route_profile_ref=route_profile_ref,
        route_policy_ref=f"{policy_path}#{route_profile_ref}",
        reason_codes=reason_codes,
        routing_timestamp=ts,
        replay_key=replay_key,
        snapshot_refs=_snapshot_refs(row),
        l5_certification_ref=plan.l5_certification_ref,
        graph_traverse_policy=graph_policy,
    )

    from apps_rg.runtime.bindings.l0_l3_otel_spans import emit_l0_route_span
    from apps_rg.runtime.bindings.l0_route_evidence import stamp_route_evidence

    stamped = stamp_route_evidence(
        route,
        plan=plan,
        route_id=route_id,
        route_family=route_family,
        execution_form=execution_form,
        l3_required=l3_required,
        route_profile_ref=route_profile_ref,
        cache_eligibility=cache_eligibility,
    )
    span = emit_l0_route_span(stamped)
    if span and span.get("span_ref"):
        from dataclasses import replace

        stamped = replace(
            stamped,
            otel_span_refs=tuple(stamped.otel_span_refs) + (str(span["span_ref"]),),
        )
    return stamped
