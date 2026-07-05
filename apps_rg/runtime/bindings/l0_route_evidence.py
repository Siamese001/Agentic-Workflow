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
    "compute_route_digest",
    "resolve_route_hmac_secret",
    "sign_route_digest",
    "stamp_route_evidence",
]


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
        "replay_key": plan.replay_key,
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
    )
    sig = sign_route_digest(digest, secret=resolve_route_hmac_secret())
    l1_refs = _l1_capsule_consumption_refs(plan)

    from dataclasses import replace

    updates: dict[str, Any] = {
        "route_digest": digest,
        "reason_codes": tuple(route.reason_codes or ()) + l1_refs,
    }
    if sig:
        updates["hmac_sig"] = sig
        updates["signature"] = sig
    return replace(route, **updates)
