"""L0 route evidence — deterministic digest, L1 readiness gate, and HMAC."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Mapping, Sequence

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.route_gate_receipt import RouteGateReceipt

__all__ = [
    "L1PlanNotReadyError",
    "RouteSigningSecretMissingError",
    "compute_route_digest",
    "resolve_route_hmac_secret",
    "serialize_l0_route_artifact",
    "sign_route_digest",
    "stamp_route_evidence",
]


class RouteSigningSecretMissingError(RuntimeError):
    """L0 route signing secret is required outside explicit test/dev posture."""


class L1PlanNotReadyError(RuntimeError):
    """L0-owned fail-closed signal for a verified but blocked L1 plan."""

    def __init__(self, receipt: RouteGateReceipt) -> None:
        self.receipt = receipt
        super().__init__(
            f"G_L1_PLAN_READY blocked routing: verdict={receipt.verdict} reason={receipt.reason}"
        )


def resolve_route_hmac_secret() -> bytes:
    raw = os.environ.get("APPS_RG_ROUTE_HMAC_SECRET", "").strip()
    if raw:
        return raw.encode("utf-8")
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return b"apps_rg_route_hmac_test_secret_v1"
    return b""


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _verified_l1_binding(plan: L1PlanContract) -> dict[str, Any]:
    from apps_rg.runtime.bindings.l1_planning_capsule import (
        extract_verified_planning_capsule,
    )

    capsule, verification = extract_verified_planning_capsule(plan, required=False)
    if not capsule:
        return {}
    profile_refs = capsule.get("planning_prior_refs") or ()
    profile = profile_refs[0] if profile_refs and isinstance(profile_refs[0], Mapping) else {}
    return {
        "capsule_digest": str(capsule.get("capsule_digest") or ""),
        "planning_profile_ref": str(profile.get("ref") or ""),
        "planning_profile_digest": str(profile.get("digest") or ""),
        "planning_status": str(capsule.get("planning_status") or ""),
        "validation_receipt_id": str(plan.validation_receipt_id or ""),
        "route_feature_digest": _sha256_json(capsule.get("route_feature_hints") or {}),
        "work_units_digest": _sha256_json(capsule.get("work_units") or []),
        "completion_criteria_digest": _sha256_json(
            capsule.get("completion_criteria") or []
        ),
        "evidence_plan_digest": _sha256_json(capsule.get("evidence_plan") or []),
        "verification_digest": _sha256_json(verification),
    }


def _l1_plan_ready_receipt(plan: L1PlanContract) -> RouteGateReceipt:
    binding = _verified_l1_binding(plan)
    if not binding:
        return RouteGateReceipt(
            gate_id="G_L1_PLAN_READY",
            verdict="UNKNOWN",
            score=0.0,
            facts_present=False,
            reason=(
                "legacy L1PlanContract has no apps_rg planning capsule; "
                "canonical apps_rg L1 callers must provide one"
            ),
        )
    status = binding["planning_status"]
    if status == "READY":
        return RouteGateReceipt(
            gate_id="G_L1_PLAN_READY",
            verdict="PASS",
            score=1.0,
            facts_present=True,
            reason="verified L1 capsule is READY and bound to planning profile bytes",
        )
    if status == "BLOCKED":
        return RouteGateReceipt(
            gate_id="G_L1_PLAN_READY",
            verdict="FAIL",
            score=0.0,
            facts_present=True,
            reason="verified L1 capsule has blocking ambiguity and requires HITL or repair",
        )
    return RouteGateReceipt(
        gate_id="G_L1_PLAN_READY",
        verdict="UNKNOWN",
        score=0.0,
        facts_present=True,
        reason=f"verified L1 capsule has unsupported planning_status={status!r}",
    )


def compute_route_digest(
    *,
    plan: L1PlanContract,
    route_id: str,
    route_family: str,
    execution_form: str,
    l3_required: bool,
    route_profile_ref: str,
    cache_eligibility: Mapping[str, bool],
    replay_key: str = "",
) -> str:
    """Digest route authority plus the exact verified L1 plan it consumed."""

    data: dict[str, Any] = {
        "app_id": plan.app_id,
        "request_id": plan.request_id,
        "route_id": route_id,
        "route_family": route_family,
        "execution_form": execution_form,
        "l3_required": l3_required,
        "grounding_required": plan.grounding_required,
        "apps_research_call_required": plan.apps_research_call_required,
        "model_generation_required": plan.model_generation_required,
        "route_profile_ref": route_profile_ref,
        "cache_eligibility": dict(sorted(cache_eligibility.items())),
        "replay_key": replay_key or plan.replay_key,
        "validation_receipt_id": getattr(plan, "validation_receipt_id", ""),
        "l1_plan_binding": _verified_l1_binding(plan),
    }
    canonical = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_route_digest(digest: str, *, secret: bytes) -> str:
    if not secret:
        return ""
    return hmac.new(secret, digest.encode("utf-8"), hashlib.sha256).hexdigest()


def _l1_capsule_consumption_refs(plan: L1PlanContract) -> tuple[str, ...]:
    binding = _verified_l1_binding(plan)
    if not binding:
        return ()
    capsule_digest = binding["capsule_digest"]
    return (
        f"l1_capsule_digest:{capsule_digest[:24]}",
        f"l1_profile_digest:{binding['planning_profile_digest'][:24]}",
        f"l1_route_features:{binding['route_feature_digest'][:16]}",
        f"l1_work_units:{binding['work_units_digest'][:16]}",
        f"l1_completion_criteria:{binding['completion_criteria_digest'][:16]}",
        f"l1_evidence_plan_ref:{binding['evidence_plan_digest'][:16]}",
        f"l1_planning_status:{binding['planning_status']}",
        f"l1_work_shape:{plan.work_shape or 'unknown'}",
        f"l1_task_shape:{plan.task_shape or 'unknown'}",
    )


def _explicit_unsigned_test_posture() -> bool:
    posture = os.environ.get("APPS_RG_ROUTE_SIGNING_POSTURE", "").strip().lower()
    return posture in {"unsigned_test", "explicit_unsigned_test", "test_unsigned"}


def _route_reason_value(route: RouteContract, prefix: str) -> str:
    needle = f"{prefix}="
    for code in route.reason_codes or ():
        if code.startswith(needle):
            return code[len(needle) :]
    return ""


def _snapshot_value(route: RouteContract, prefix: str) -> str:
    needle = f"{prefix}:"
    for ref in route.snapshot_refs or ():
        if ref.startswith(needle):
            return ref[len(needle) :]
    return ""


def serialize_l0_route_artifact(route: RouteContract) -> dict[str, Any]:
    """Canonical JSON-ready L0 RouteContract artifact."""

    gate_receipts = [
        {
            "gate_id": receipt.gate_id,
            "verdict": receipt.verdict,
            "score": receipt.score,
            "facts_present": receipt.facts_present,
            "adapter_kind": receipt.adapter_kind,
            "reason": receipt.reason,
        }
        for receipt in route.route_gate_receipts
    ]
    terminal_receipt = (
        route.r1a_lookup_receipt_ref
        or route.r1b_lookup_receipt_ref
        or route.r5_fallback_receipt_ref
        or route.cache_lookup_r1a_receipt
        or route.cache_lookup_r1b_receipt
        or route.cache_lookup_r5_receipt
    )
    return {
        "request_id": route.request_id,
        "run_id": route.run_id,
        "trace_id": route.trace_id,
        "trace_root": route.trace_id,
        "app_id": route.app_id,
        "route_id": route.route_id,
        "canonical_route_id": route.route_id,
        "app_route_id": _route_reason_value(route, "app_route_id"),
        "route_family": route.route_family,
        "execution_form": route.execution_form,
        "route_profile_ref": route.route_profile_ref,
        "route_policy_ref": route.route_policy_ref,
        "route_digest": route.route_digest,
        "signature": {
            "posture": _route_reason_value(route, "route_signing_posture")
            or ("signed" if route.hmac_sig or route.signature else "unsigned"),
            "hmac_sig": route.hmac_sig or route.signature,
        },
        "route_gate_status": _route_reason_value(route, "route_gate_status"),
        "blocking_gate_ids": tuple(
            item
            for item in _route_reason_value(route, "blocking_gate_ids").split("|")
            if item
        ),
        "route_block_reason": _route_reason_value(route, "route_block_reason"),
        "route_gate_receipts": gate_receipts,
        "cache_lookup_receipts": {
            "r1a": route.r1a_lookup_receipt_ref or route.cache_lookup_r1a_receipt,
            "r1b": route.r1b_lookup_receipt_ref or route.cache_lookup_r1b_receipt,
            "r5": route.r5_fallback_receipt_ref or route.cache_lookup_r5_receipt,
        },
        "terminal": {
            "is_terminal": route.route_id
            in {"R1A_EXACT_CACHE", "R1B_SEMANTIC_CACHE", "R5_FALLBACK"},
            "route_branch": route.route_id,
            "terminal_reason": _route_reason_value(route, "terminal_reason"),
            "cache_receipt_ref": terminal_receipt,
            "fallback_receipt_ref": route.r5_fallback_receipt_ref
            or route.cache_lookup_r5_receipt,
        },
        "allowed_next_stage": tuple(sorted(route.allowed_next_stage)),
        "replay_key": route.replay_key,
        "policy_hash": _snapshot_value(route, "policy_hash"),
        "blueprint_hash": _snapshot_value(route, "blueprint_hash"),
        "registry_digest_set": tuple(
            item
            for item in _snapshot_value(route, "registry_digest_set").split("|")
            if item
        ),
        "snapshot_refs": tuple(route.snapshot_refs),
    }


def stamp_route_evidence(
    route: RouteContract,
    *,
    plan: L1PlanContract,
    route_id: str,
    route_family: str,
    execution_form: str,
    l3_required: bool,
    route_profile_ref: str,
    cache_eligibility: Mapping[str, bool],
) -> RouteContract:
    """Gate plan readiness, then bind and sign the route to the verified L1 capsule."""

    readiness = _l1_plan_ready_receipt(plan)
    if readiness.verdict == "FAIL":
        raise L1PlanNotReadyError(readiness)

    digest = compute_route_digest(
        plan=plan,
        route_id=route_id,
        route_family=route_family,
        execution_form=execution_form,
        l3_required=l3_required,
        route_profile_ref=route_profile_ref,
        cache_eligibility=cache_eligibility,
        replay_key=route.replay_key,
    )
    secret = resolve_route_hmac_secret()
    signature = sign_route_digest(digest, secret=secret)
    if signature:
        signing_posture = "signed"
    elif _explicit_unsigned_test_posture():
        signing_posture = "unsigned_test"
    else:
        raise RouteSigningSecretMissingError(
            "APPS_RG_ROUTE_HMAC_SECRET is required for L0 route signing outside "
            "pytest or APPS_RG_ROUTE_SIGNING_POSTURE=unsigned_test."
        )

    binding = _verified_l1_binding(plan)
    existing_receipts = tuple(
        receipt
        for receipt in route.route_gate_receipts
        if receipt.gate_id != readiness.gate_id
    )
    readiness_ref = readiness.to_runtime_gate_ref()
    existing_refs = tuple(
        ref for ref in route.route_gate_refs if not str(ref).startswith("G_L1_PLAN_READY")
    )
    snapshot_refs = tuple(route.snapshot_refs or ())
    if binding:
        snapshot_refs += (
            f"l1_capsule_digest:{binding['capsule_digest']}",
            f"l1_planning_profile_digest:{binding['planning_profile_digest']}",
            f"l1_plan_binding_digest:{_sha256_json(binding)}",
        )

    from dataclasses import replace

    updates: dict[str, Any] = {
        "route_digest": digest,
        "route_gate_receipts": existing_receipts + (readiness,),
        "route_gate_refs": existing_refs + (readiness_ref,),
        "snapshot_refs": snapshot_refs,
        "reason_codes": tuple(route.reason_codes or ())
        + (f"route_signing_posture={signing_posture}",)
        + (f"l1_plan_ready={readiness.verdict}",)
        + _l1_capsule_consumption_refs(plan),
    }
    if signature:
        updates["hmac_sig"] = signature
        updates["signature"] = signature
    return replace(route, **updates)
