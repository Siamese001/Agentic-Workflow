"""L0 route evidence — deterministic digest + HMAC (W3)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Mapping, Sequence

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract

__all__ = [
    "RouteSigningSecretMissingError",
    "compute_route_digest",
    "resolve_route_hmac_secret",
    "serialize_l0_route_artifact",
    "sign_route_digest",
    "stamp_route_evidence",
]


class RouteSigningSecretMissingError(RuntimeError):
    """L0 route signing secret is required outside explicit test/dev posture."""


def resolve_route_hmac_secret() -> bytes:
    """Resolve HMAC secret for route signing (test-friendly default under pytest)."""

    raw = os.environ.get("APPS_RG_ROUTE_HMAC_SECRET", "").strip()
    if raw:
        return raw.encode("utf-8")
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return b"apps_rg_route_hmac_test_secret_v1"
    return b""


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
    """Deterministic digest over routing decision fields (REQ-L0-DETERMINISTIC-DIGEST-001)."""

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
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_route_digest(digest: str, *, secret: bytes) -> str:
    """HMAC-SHA256 over route digest (REQ-L0-HMAC-SIGNED-001)."""

    if not secret:
        return ""
    return hmac.new(secret, digest.encode("utf-8"), hashlib.sha256).hexdigest()


def _sha256_json_prefix(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _l1_capsule_consumption_refs(plan: L1PlanContract) -> tuple[str, ...]:
    task_spec = dict(plan.task_spec or {})
    support_expectation = dict(plan.support_expectation or {})
    capsule_ref = str(task_spec.get("apps_rg_planning_capsule_ref") or "").strip()
    capsule = task_spec.get("apps_rg_planning_capsule")
    if not capsule_ref and isinstance(capsule, Mapping):
        capsule_ref = str(capsule.get("capsule_digest") or "").strip()
    if not capsule_ref:
        return ()
    route_features: Any = {}
    completion_count = 0
    work_unit_count = 0
    if isinstance(capsule, Mapping):
        route_features = capsule.get("route_feature_hints") or {}
        completion = capsule.get("completion_criteria")
        work_units = capsule.get("work_units")
        completion_count = len(completion) if isinstance(completion, Sequence) else 0
        work_unit_count = len(work_units) if isinstance(work_units, Sequence) else 0
    evidence_ref = str(support_expectation.get("apps_rg_evidence_plan_ref") or "").strip()
    refs = [
        f"l1_capsule_digest:{capsule_ref[:24]}",
        f"l1_route_features:{_sha256_json_prefix(route_features)}",
        f"l1_completion_criteria:{completion_count}",
        f"l1_work_units:{work_unit_count}",
        f"l1_work_shape:{plan.work_shape or 'unknown'}",
        f"l1_task_shape:{plan.task_shape or 'unknown'}",
    ]
    if evidence_ref:
        refs.append(f"l1_evidence_plan_ref:{evidence_ref[:24]}")
    return tuple(refs)


def _explicit_unsigned_test_posture() -> bool:
    posture = os.environ.get("APPS_RG_ROUTE_SIGNING_POSTURE", "").strip().lower()
    return posture in {"unsigned_test", "explicit_unsigned_test", "test_unsigned"}


def _route_reason_value(route: RouteContract, prefix: str) -> str:
    needle = f"{prefix}="
    for code in route.reason_codes or ():
        if code.startswith(needle):
            return code[len(needle):]
    return ""


def _snapshot_value(route: RouteContract, prefix: str) -> str:
    needle = f"{prefix}:"
    for ref in route.snapshot_refs or ():
        if ref.startswith(needle):
            return ref[len(needle):]
    return ""


def serialize_l0_route_artifact(route: RouteContract) -> dict[str, Any]:
    """Canonical JSON-ready L0 RouteContract/[RET] artifact."""

    gate_receipts = [
        {
            "gate_id": r.gate_id,
            "verdict": r.verdict,
            "score": r.score,
            "facts_present": r.facts_present,
            "adapter_kind": r.adapter_kind,
            "reason": r.reason,
        }
        for r in route.route_gate_receipts
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
            x
            for x in _route_reason_value(route, "blocking_gate_ids").split("|")
            if x
        ),
        "route_block_reason": _route_reason_value(route, "route_block_reason"),
        "route_gate_receipts": gate_receipts,
        "cache_lookup_receipts": {
            "r1a": route.r1a_lookup_receipt_ref or route.cache_lookup_r1a_receipt,
            "r1b": route.r1b_lookup_receipt_ref or route.cache_lookup_r1b_receipt,
            "r5": route.r5_fallback_receipt_ref or route.cache_lookup_r5_receipt,
        },
        "terminal": {
            "is_terminal": route.route_id in {"R1A_EXACT_CACHE", "R1B_SEMANTIC_CACHE", "R5_FALLBACK"},
            "route_branch": route.route_id,
            "terminal_reason": _route_reason_value(route, "terminal_reason"),
            "cache_receipt_ref": terminal_receipt,
            "fallback_receipt_ref": route.r5_fallback_receipt_ref or route.cache_lookup_r5_receipt,
        },
        "allowed_next_stage": tuple(sorted(route.allowed_next_stage)),
        "replay_key": route.replay_key,
        "policy_hash": _snapshot_value(route, "policy_hash"),
        "blueprint_hash": _snapshot_value(route, "blueprint_hash"),
        "registry_digest_set": tuple(
            x
            for x in _snapshot_value(route, "registry_digest_set").split("|")
            if x
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
    """Return RouteContract with route_digest + hmac_sig (+ signature mirror)."""

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
    sig = sign_route_digest(digest, secret=secret)
    if sig:
        signing_posture = "signed"
    elif _explicit_unsigned_test_posture():
        signing_posture = "unsigned_test"
    else:
        raise RouteSigningSecretMissingError(
            "APPS_RG_ROUTE_HMAC_SECRET is required for L0 route signing outside "
            "pytest or APPS_RG_ROUTE_SIGNING_POSTURE=unsigned_test."
        )
    l1_refs = _l1_capsule_consumption_refs(plan)

    from dataclasses import replace

    updates: dict[str, Any] = {
        "route_digest": digest,
        "reason_codes": tuple(route.reason_codes or ())
        + (f"route_signing_posture={signing_posture}",)
        + l1_refs,
    }
    if sig:
        updates["hmac_sig"] = sig
        updates["signature"] = sig
    return replace(route, **updates)
