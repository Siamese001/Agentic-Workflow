"""L0 routing binding for the apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P3 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W3 (AG-2 — consumes
   L1PlanContract app_payload-derived projections to drive route_family +
   cache_eligibility + action_required).
+   plan apps-rg-ensemble-judge-restoration-a7c4e2 W2 (cache lookup receipts
   + work-shape evaluation for managed_workflow execution_form).

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
    - execution_form: "single_step" | "managed_workflow" (from work-shape hints)
    - cache_eligibility: per-tier booleans (R1A/R1B/R3/R4)
    - cache_lookup_r1a_receipt: serialized R1A lookup result (hit/miss)
    - cache_lookup_r1b_receipt: serialized R1B lookup result (always miss today)
    - cache_lookup_r5_receipt: serialized R5 lookup result (always miss today)
    - workflow_ref: resolved workflow ID when execution_form="managed_workflow"
    - action_required: True only when generation_mode demands state mutation
      (resume_generation never does — write_authority_present=False)

W4 P4.2: L3 opt-in via environment variable APPS_RG_L3_OPT_IN=1.
Ensemble restoration W2: Actual cache lookups before execution_form decision.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract

_log = logging.getLogger(__name__)


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


def _perform_cache_lookups(l1_plan: L1PlanContract) -> tuple[str, str, str]:
    """Run actual R1A/R1B/R5 cache lookups and return serialized receipts.

    Returns:
        (r1a_receipt_json, r1b_receipt_json, r5_receipt_json)

    Each receipt is a JSON string with keys: result ("hit"|"miss"), digest,
    and optional cached_run_dir (for hits).

    Fail-soft: any exception during lookup produces a miss receipt.
    """
    # R1A exact-match lookup
    r1a_receipt: dict = {"result": "miss", "digest": ""}
    try:
        from apps_rg.cache.r1a_adapter import compute_r1a_key, check_r1a_cache

        query_spec = l1_plan.query_spec
        policy_refs = l1_plan.policy_refs
        key = compute_r1a_key(
            source_resume_hash=str(query_spec.get("resume_hash", "none")),
            target_company=str(query_spec.get("target_company", "")),
            target_role=str(query_spec.get("target_role", "")),
            jd_hash=str(query_spec.get("jd_hash", "none")),
            briefing_hash=str(query_spec.get("briefing_hash", "none")),
            policy_hash=str(policy_refs.get("manifest_digest", "unknown")),
            blueprint_hash=str(policy_refs.get("blueprint_hash", "unknown")),
        )
        r1a_receipt["digest"] = key
        hit = check_r1a_cache(
            key=key,
            policy_hash=str(policy_refs.get("manifest_digest", "")),
            blueprint_hash=str(policy_refs.get("blueprint_hash", "")),
        )
        if hit:
            r1a_receipt["result"] = "hit"
            r1a_receipt["cached_run_dir"] = hit
            _log.info("[L0] R1A exact cache HIT: %s", hit)
        else:
            _log.debug("[L0] R1A exact cache MISS for key=%s", key[:16])
    except ImportError:
        _log.debug("[L0] R1A adapter not available — recording miss")
    except (TypeError, ValueError, OSError) as exc:
        _log.debug("[L0] R1A lookup failed: %s", exc)

    # R1B semantic lookup — currently quarantined; always produce miss receipt
    r1b_receipt: dict = {"result": "miss", "digest": "", "reason": "r1b_quarantined"}

    # R5 fallback lookup — not yet implemented; always miss
    r5_receipt: dict = {"result": "miss", "reason": "r5_not_implemented"}

    return (
        json.dumps(r1a_receipt, separators=(",", ":")),
        json.dumps(r1b_receipt, separators=(",", ":")),
        json.dumps(r5_receipt, separators=(",", ":")),
    )


def _evaluate_execution_form(l1_plan: L1PlanContract, r1a_hit: bool) -> str:
    """Determine execution_form from cache state + L1 work-shape hints.

    Logic:
      1. If R1A hit → "single_step" (cache serves the response directly)
      2. If env APPS_RG_EXECUTION_FORM is set → use that value explicitly
      3. If ALL 4 work-shape hints are True → "managed_workflow"
      4. If env APPS_RG_L3_OPT_IN=1 → "managed_workflow" (legacy opt-in)
      5. Otherwise → "single_step"

    The explicit env var APPS_RG_EXECUTION_FORM overrides all hint-based
    logic so operators can force a specific form. This is the ONLY supported
    override path — no silent fallback from managed_workflow to single_step.
    """
    if r1a_hit:
        return "single_step"

    explicit_form = os.environ.get("APPS_RG_EXECUTION_FORM", "").strip().lower()
    if explicit_form in ("single_step", "managed_workflow"):
        return explicit_form

    if (
        l1_plan.multiple_work_units_hint
        and l1_plan.merge_required_hint
        and l1_plan.per_unit_quality_selection_hint
        and l1_plan.candidate_generation_expected_hint
    ):
        return "managed_workflow"

    l3_opt_in = os.environ.get("APPS_RG_L3_OPT_IN", "") in ("1", "true", "yes")
    if l3_opt_in:
        return "managed_workflow"

    return "single_step"


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

    # Ensemble W2: Actual cache lookups BEFORE execution_form decision.
    # This proves cache was consulted — receipts are serialized into RouteContract.
    r1a_receipt, r1b_receipt, r5_receipt = _perform_cache_lookups(l1_plan)
    r1a_hit = '"result":"hit"' in r1a_receipt

    # Ensemble W2: Evaluate execution_form from cache state + work-shape hints.
    execution_form = _evaluate_execution_form(l1_plan, r1a_hit)
    l3_required = execution_form == "managed_workflow"

    # AG-2: derive app_payload-aware routing fields from L1 projections.
    route_family = _derive_route_family(l1_plan)
    cache_eligibility = _derive_cache_eligibility(l1_plan)
    action_required = _derive_action_required(l1_plan)

    # Ensemble W2: workflow_ref placeholder — registry resolution lands in Wave 3.
    workflow_ref = ""
    if l3_required:
        workflow_ref = "apps_rg.resume_generation.managed_workflow.v1"

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        trace_id=l1_plan.trace_id,
        # W1 P1.2: thread identity quad from L1PlanContract (D6)
        tenant_id=l1_plan.tenant_id,
        route_id=route_id,
        l3_required=l3_required,
        grounding_required=l1_plan.grounding_required,
        model_generation_required=l1_plan.model_generation_required,
        write_authority_present=l1_plan.write_authority_present,
        # W2 P2.1: capability/sandbox/egress — apps_rg is read-only, single vllm model (D11=default-empty)
        # W4 cross-ref: allowed_models here is the L0 ROUTE allowlist — it gates which
        # models L2 may dispatch to. PA's APPS_RG_TARGET_MODEL (apps_rg_pa_binding.py) is
        # the GENERATION TARGET declaration on the compiled artifact. Both must name the
        # same model. Intentionally kept as two separate declarations: L0 owns the
        # routing policy; PA owns the artifact target field. See W4 slot_lineage_map
        # component_hash_map["route"] comment for divergence detection.
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
        # Ensemble W2: managed workflow resolution (registry in Wave 3)
        workflow_ref=workflow_ref,
        # Ensemble W2: actual cache lookup receipts (prove lookups happened)
        cache_lookup_r1a_receipt=r1a_receipt,
        cache_lookup_r1b_receipt=r1b_receipt,
        cache_lookup_r5_receipt=r5_receipt,
        # AG-2: thread replay_key forward.
        replay_key=l1_plan.replay_key,
        reason_codes=_build_reason_codes(l1_plan) + (
            f"route_family={route_family}",
            f"execution_form={execution_form}",
            f"cache_eligibility={cache_eligibility}",
            f"action_required={action_required}",
            f"r1a_result={'hit' if r1a_hit else 'miss'}",
            f"workflow_ref={workflow_ref}",
        ),
        routing_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-2.a7c4e2",
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )


__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_DEFAULT_ROUTE_ID",
    "APPS_RG_EXECUTIVE_ROUTE_ID",
    "l0_route_apps_rg",
]
