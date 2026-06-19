"""L0 route evidence — deterministic digest + HMAC (W3)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Mapping

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
        "planning_capsule_ref": str((plan.policy_refs or {}).get("l1_planning_capsule_ref", "")),
        "planning_prior_set_ref": str((plan.policy_refs or {}).get("l1_planning_prior_set_ref", "")),
        "completion_criteria": dict((plan.output_expectation or {}).get("completion_criteria") or {}),
        "ambiguity_register_id": str((plan.ambiguity_register or {}).get("register_id", "")),
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_route_digest(digest: str, *, secret: bytes) -> str:
    """HMAC-SHA256 over route digest (REQ-L0-HMAC-SIGNED-001)."""

    if not secret:
        return ""
    return hmac.new(secret, digest.encode("utf-8"), hashlib.sha256).hexdigest()


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
    if not sig:
        return route

    from dataclasses import replace

    reason_codes = tuple(route.reason_codes or ())
    planning_reason_codes = []
    planning_capsule_ref = str((plan.policy_refs or {}).get("l1_planning_capsule_ref", "") or "")
    planning_prior_set_ref = str((plan.policy_refs or {}).get("l1_planning_prior_set_ref", "") or "")
    ambiguity_register_id = str((plan.ambiguity_register or {}).get("register_id", "") or "")
    if planning_capsule_ref:
        planning_reason_codes.append(f"l1_planning_capsule_ref={planning_capsule_ref}")
    if planning_prior_set_ref:
        planning_reason_codes.append(f"l1_planning_prior_set_ref={planning_prior_set_ref}")
    if ambiguity_register_id:
        planning_reason_codes.append(f"l1_ambiguity_register_id={ambiguity_register_id}")

    return replace(
        route,
        route_digest=digest,
        hmac_sig=sig,
        signature=sig,
        reason_codes=reason_codes + tuple(planning_reason_codes),
    )
