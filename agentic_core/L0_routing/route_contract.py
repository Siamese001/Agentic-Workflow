"""L0 Route Contract Producer — AG-RGGOV-W6 Core Contract

L0 consumes L1PlanContract and emits RouteContract.

Responsibilities:
- Consume L1PlanContract
- Make routing decision based on grounding_required, model_generation_required
- Emit RouteContract with selected execution path

Hard Constraints:
- Core owns all routing decisions
- apps_rg does not route
- Contract dataclass is defined in runtime/contracts/, imported here
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract

_logger = logging.getLogger(__name__)
_L5_CERT_REF_FAIL_CLOSED = os.getenv("L5_CERT_REF_FAIL_CLOSED", "0") == "1"


def _check_l5_cert_ref_l0(ref: str) -> None:
    """Fail-soft L5 cert ref verify at L0 entry per AG-W0-3=A_consume_entry."""
    try:
        from agentic_core.L5_safety.contracts.registry import verify_certification_ref
        valid = verify_certification_ref(ref)
    except Exception as exc:  # guardian: allow-log-and-swallow -- L5 registry must not crash L0 routing; treat as unverified  # guardian: allow-broad-exception -- P1 ADG burndown
        _logger.warning("L5CertRefViolation stage=L0_entry registry_error=%s", exc)
        return
    if not valid:
        msg = "L5CertRefViolation stage=L0_entry ref=%r — missing or invalid l5_certification_ref"
        if _L5_CERT_REF_FAIL_CLOSED:
            raise ValueError(msg % (ref,))
        _logger.warning(msg, ref)


class L0Router:
    """L0 routing layer for apps_rg tasks.

    Consumes L1PlanContract and emits RouteContract with execution path.
    """

    def route(self, plan: L1PlanContract) -> RouteContract:
        """Generate RouteContract from L1PlanContract.

        Args:
            plan: L1 planning output with execution prerequisites

        Returns:
            RouteContract with selected route and execution path
        """
        # L0 entry: verify upstream (L1 plan) l5_certification_ref (AG-W0-3)
        _check_l5_cert_ref_l0(getattr(plan, "l5_certification_ref", ""))

        # Determine route based on plan requirements
        route_id, l3_required = self._select_route(plan)

        reason_codes = self._build_reason_codes(plan)

        return RouteContract(
            request_id=plan.request_id,
            run_id=plan.run_id,
            app_id=plan.app_id,
            trace_id=plan.trace_id,
            route_id=route_id,
            l3_required=l3_required,
            grounding_required=plan.grounding_required,
            model_generation_required=plan.model_generation_required,
            write_authority_present=plan.write_authority_present,
            reason_codes=reason_codes,
            routing_timestamp=datetime.now(timezone.utc).isoformat(),
            schema_version="W6.0",
            l5_certification_ref=getattr(plan, "l5_certification_ref", ""),
        )

    def _select_route(self, plan: L1PlanContract) -> tuple[str, bool]:
        """Select route based on plan requirements."""
        if plan.write_authority_present:
            return "R5_MANAGED_WORKFLOW", True  # L3 required for write authority
        elif plan.model_generation_required:
            return "R3_SIMPLE_GROUNDED_READ", False  # Standard read route
        else:
            return "R1_CACHE_ONLY", False  # Cache fallback

    def _build_reason_codes(self, plan: L1PlanContract) -> tuple[str, ...]:
        """Build routing reason codes from plan."""
        codes: list[str] = []
        if plan.grounding_required:
            codes.append("grounding_required=true")
        else:
            codes.append("grounding_required=false")

        if plan.model_generation_required:
            codes.append("model_generation_required=true")
        else:
            codes.append("model_generation_required=false")

        if plan.write_authority_present:
            codes.append("write_authority_present=true")
        else:
            codes.append("write_authority_present=false")

        if plan.l3_required if hasattr(plan, 'l3_required') else False:
            codes.append("L3_required=true")
        else:
            codes.append("L3_required=false")

        return tuple(codes)
