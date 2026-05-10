"""L0 routing binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P3 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W3 (AG-2 — consumes
   L1PlanContract app_payload-derived projections to drive route_family +
   cache_eligibility + action_required).

L0 is the THIRD stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to consume the L1 plan + its five app_payload-derived
projections, read the apps_rg declarative route profile
(route_profiles.yaml), and emit a typed RouteContract that downstream
C0/PA/L2 stages consume.

AG-2 consumption surface — L0 reads from L1PlanContract:
    - support_expectation.fact_checked_required → grounded route family
    - support_expectation.provenance_required   → grounded route family
    - task_spec.generation_mode                 → route_family taxonomy
    - target_level                              → route_id variant

L0 produces on RouteContract:
    - route_family: e.g. "evidence_grounded_generation"
    - execution_form: "single_step" today; "managed_workflow" future
    - cache_eligibility: per-tier booleans (R1A/R1B/R3/R4)
    - action_required: True only when generation_mode demands state mutation
      (resume_generation never does — write_authority_present=False)

W4 P4.2: L3 opt-in via environment variable APPS_RG_L3_OPT_IN=1.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-app-payload-b3a449"
APPS_RG_DEFAULT_ROUTE_ID: str = "rg.resume_generation.default"
APPS_RG_EXECUTIVE_ROUTE_ID: str = "rg.resume_generation.executive"
_ROUTE_PROFILE_RELPATH: str = "apps_rg/config/domain_contract/route_profiles.yaml"

# AG-2: route_family taxonomy keyed by generation_mode + grounded flag.
# This is the high-level decision; route_id carries the variant detail.
_ROUTE_FAMILY_EVIDENCE_GROUNDED: str = "evidence_grounded_generation"
_ROUTE_FAMILY_UNGROUNDED: str = "ungrounded_generation"
_ROUTE_FAMILY_VALIDATION: str = "validation_only"

_VALIDATION_MODES: frozenset[str] = frozenset({
    "healing_fact_check",
    "healing_unsupported_claim",
})


def _derive_route_family(l1_plan: L1PlanContract) -> str:
    """Pick the route family from L1PlanContract projections.

    Reads task_spec.generation_mode + grounding_required (already derived
    from app_payload by L1).
    """

    generation_mode = str(l1_plan.task_spec.get("generation_mode", ""))
    if generation_mode in _VALIDATION_MODES:
        return _ROUTE_FAMILY_VALIDATION
    if l1_plan.grounding_required:
        return _ROUTE_FAMILY_EVIDENCE_GROUNDED
    return _ROUTE_FAMILY_UNGROUNDED


def _derive_cache_eligibility(l1_plan: L1PlanContract) -> dict[str, bool]:
    """Compute per-cache-tier eligibility from L1 projections.

    AG-2 spec rule: R1B semantic cache eligibility is only marked when
    semantic compatibility evidence can later be proven. For
    resume_generation today: R1A exact-key cache always eligible (the
    payload digest is canonical); R1B semantic deferred (no proof path
    yet); R3 grounded cache eligible iff grounding_required; R4 action
    cache never (no state mutation).
    """

    fact_check_required = bool(
        l1_plan.support_expectation.get("fact_checked_required", False)
    )
    return {
        # exact-key cache — keyed on input payload digest, always safe
        "r1a_exact": True,
        # semantic cache — needs an embedding compat proof; out of scope (AG-2 hard law)
        "r1b_semantic": False,
        # grounded cache — eligible only when L1 demands grounding AND fact-check
        "r3_grounded": bool(l1_plan.grounding_required) and fact_check_required,
        # action cache — apps_rg never mutates state in this scope
        "r4_action": False,
    }


def _derive_action_required(l1_plan: L1PlanContract) -> bool:
    """Action-required follows write_authority_present, which apps_rg never sets."""

    return bool(l1_plan.write_authority_present)


def _read_route_profile_digest(repo_root: Path) -> str:
    """Compute sha256 digest of the route profile bytes."""
    profile_path = repo_root / _ROUTE_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        return hashlib.sha256(profile_path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _build_reason_codes(l1_plan: L1PlanContract) -> tuple[str, ...]:
    """Build human-readable reason codes for the routing decision."""
    codes: list[str] = [
        f"task_class=resume_generation",
        f"route_id={APPS_RG_DEFAULT_ROUTE_ID}",
        "execution_form=single_step",
        f"l3_required=false (managed_workflow path deferred)",
    ]
    if l1_plan.grounding_required:
        codes.append("grounding_required=true (C0 retrieval will fire)")
    if l1_plan.model_generation_required:
        codes.append("model_generation_required=true (L2 LLM call will fire)")
    if not l1_plan.write_authority_present:
        codes.append("write_authority_present=false (no UWG/learning writes)")
    codes.append(
        f"capabilities_count={len(l1_plan.required_capabilities)}: "
        + ",".join(l1_plan.required_capabilities)
    )
    return tuple(codes)


def l0_route_apps_rg(l1_plan: L1PlanContract) -> RouteContract:
    """Emit a RouteContract from an apps_rg L1 plan.

    Args:
        l1_plan: L1PlanContract output of l1_plan_apps_rg.

    Returns:
        RouteContract with route_id, l3_required, and routing flags.

    Raises:
        TypeError: if l1_plan is not an L1PlanContract.
        ValueError: if l1_plan.app_id != 'apps_rg'.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_rg expected L1PlanContract, got {type(l1_plan).__name__}"
        )

    if l1_plan.app_id != "apps_rg":
        raise ValueError(
            f"l0_route_apps_rg expected app_id='apps_rg', got {l1_plan.app_id!r}"
        )

    # Optional digest binding for tampering detection.
    _ = _read_route_profile_digest(_resolve_repo_root())  # captured for parity

    # W2: variant routing based on target_level (DS-3)
    route_id = (
        APPS_RG_EXECUTIVE_ROUTE_ID
        if l1_plan.target_level == "EXECUTIVE"
        else APPS_RG_DEFAULT_ROUTE_ID
    )

    # W4 P4.2: L3 opt-in via env var (binding only; full DAG deferred)
    l3_opt_in = os.environ.get("APPS_RG_L3_OPT_IN", "") in ("1", "true", "yes")

    # AG-2: derive app_payload-aware routing fields from L1 projections.
    route_family = _derive_route_family(l1_plan)
    cache_eligibility = _derive_cache_eligibility(l1_plan)
    action_required = _derive_action_required(l1_plan)
    execution_form = "managed_workflow" if l3_opt_in else "single_step"

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        trace_id=l1_plan.trace_id,
        # W1 P1.2: thread identity quad from L1PlanContract (D6)
        tenant_id=l1_plan.tenant_id,
        route_id=route_id,
        l3_required=l3_opt_in,
        grounding_required=l1_plan.grounding_required,
        model_generation_required=l1_plan.model_generation_required,
        write_authority_present=l1_plan.write_authority_present,
        # W2 P2.1: capability/sandbox/egress — apps_rg is read-only, single vllm model (D11=default-empty)
        sandbox_required=False,
        egress_policy_ref="egress-policy:vllm-only",
        allowed_models=("Qwen/Qwen2.5-32B-Instruct-AWQ",),
        allowed_tools=(),
        allowed_networks=("localhost:8000",),
        allowed_file_roots=("artifacts/apps_rg/",),
        # AG-2 — surface app_payload-derived routing semantics explicitly.
        route_family=route_family,
        execution_form=execution_form,
        cache_eligibility=cache_eligibility,
        action_required=action_required,
        # AG-2: thread replay_key forward.
        replay_key=l1_plan.replay_key,
        reason_codes=_build_reason_codes(l1_plan) + (
            f"route_family={route_family}",
            f"cache_eligibility={cache_eligibility}",
            f"action_required={action_required}",
        ),
        routing_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-2.b3a449",
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )


__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_DEFAULT_ROUTE_ID",
    "APPS_RG_EXECUTIVE_ROUTE_ID",
    "l0_route_apps_rg",
]
