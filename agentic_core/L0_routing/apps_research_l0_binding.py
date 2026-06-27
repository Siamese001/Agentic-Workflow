"""L0 routing binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

L0 is the THIRD stage. Its job is to:
1. Consume L1PlanContract projections (task_spec / support_expectation / output_expectation).
2. Emit a typed RouteContract with route_id, flags, cache eligibility, reason codes.

apps_research always routes to R3_SIMPLE_GROUNDED_READ:
  grounding_required=True, model_generation_required=True,
  write_authority_present=False, action_required=False.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_research import integrations as _integrations

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_L0_CERT_REF: str = "l0-apps-research-company-brief-ag9"

# apps_research canonical route: grounded read-only synthesis
_ROUTE_ID: str = "R3_SIMPLE_GROUNDED_READ"
_ROUTE_FAMILY: str = "evidence_grounded_generation"
_EXECUTION_FORM: str = "single_step"

# Cache eligibility — apps_research uses R1A exact (topic+depth hash match)
# but NOT R1B (semantic) or R4 (action) caches.
_CACHE_ELIGIBILITY: dict[str, bool] = {
    "r1a_exact": True,
    "r1b_semantic": False,
    "r3_grounded": True,
    "r4_action": False,
}

# Allowed model: Qwen 32B AWQ on local vLLM
_ALLOWED_MODELS: tuple[str, ...] = (QWEN_LOCAL_MODEL_ID,)


def l0_route_apps_research(l1_plan: L1PlanContract) -> RouteContract:
    """Emit RouteContract for apps_research company_brief task.

    Reads exclusively from L1PlanContract projections. Never re-reads
    the raw ingress payload or environment state.

    Returns a fully-typed RouteContract. Raises ValueError on bad input.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_research: expected L1PlanContract, got {type(l1_plan)}"
        )

    task_spec = l1_plan.task_spec or {}
    support_expectation = l1_plan.support_expectation or {}

    # apps_research is always R3 — verify L1 plan is consistent
    if not l1_plan.grounding_required:
        _LOGGER.warning(
            "l0_route_apps_research: L1 plan has grounding_required=False "
            "but apps_research route requires grounding. Overriding to True."
        )
    if not l1_plan.model_generation_required:
        _LOGGER.warning(
            "l0_route_apps_research: L1 plan has model_generation_required=False "
            "but apps_research route requires model generation. Overriding to True."
        )

    reason_codes: list[str] = [
        f"route={_ROUTE_ID}",
        f"task_class={l1_plan.app_id}.company_brief",
        "grounding=required",
        "write_authority=absent",
        "cache=r1a_eligible",
    ]

    if support_expectation.get("provenance_required"):
        reason_codes.append("provenance=required")

    routing_ts = datetime.now(timezone.utc).isoformat()

    _LOGGER.debug(
        "L0 apps_research route: %s family=%s execution=%s",
        _ROUTE_ID,
        _ROUTE_FAMILY,
        _EXECUTION_FORM,
    )

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id="apps_research",
        trace_id=l1_plan.trace_id,
        route_id=_ROUTE_ID,
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id=l1_plan.tenant_id,
        sandbox_required=False,
        egress_policy_ref="",
        allowed_tools=(),
        allowed_models=_ALLOWED_MODELS,
        allowed_networks=(),
        allowed_file_roots=("artifacts/",),
        route_family=_ROUTE_FAMILY,
        execution_form=_EXECUTION_FORM,
        cache_eligibility=_CACHE_ELIGIBILITY,
        action_required=False,
        reason_codes=tuple(reason_codes),
        routing_timestamp=routing_ts,
        schema_version="AG9.L0.1",
        posture=POSTURE_READ_ONLY,
        l5_certification_ref=APPS_RESEARCH_L0_CERT_REF,
    )


__all__ = [
    "APPS_RESEARCH_L0_CERT_REF",
    "l0_route_apps_research",
]
