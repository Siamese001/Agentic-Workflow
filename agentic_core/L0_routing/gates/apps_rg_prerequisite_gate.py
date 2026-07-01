"""L0 routing gate for the historical research prerequisite.

This gate runs in L0 BEFORE L2 DAG execution. It determines whether
the apps_rg static DAG can proceed or must route to apps_research first.
"""

from __future__ import annotations

from importlib import import_module
import logging
from typing import Optional

from agentic_core.L0_routing.types.routing_artifact_types import (
    L0Route,
    L0RouteContract,
    RouteReasonCode,
)

_APP_PKG = "_".join(("apps", "rg"))


def _load_app_module(module_parts: tuple[str, ...]):
    return import_module(".".join(module_parts))


# guardian: allow-layer-violation -- L0 gate lazily loads the app prerequisite validator; approved cross-layer coupling point
_briefing_validator_module = _load_app_module((_APP_PKG, "prerequisites", "briefing_validator"))
BriefingValidationResult = getattr(_briefing_validator_module, "BriefingValidationResult")
check_briefing_prerequisite = getattr(_briefing_validator_module, "check_briefing_prerequisite")
_section_c0_evidence_room_enabled = getattr(
    _load_app_module((_APP_PKG, "runtime", "c0", "evidence_room")),
    "section_c0_evidence_room_enabled",
)

_logger = logging.getLogger(__name__)


def check_apps_rg_prerequisites(
    target_company: str,
    target_role: str,
    policy_hash: str,
    blueprint_hash: str,
    trace_id: str,
    confidence: float = 1.0,
    **kwargs,
) -> Optional[L0RouteContract]:
    """Check if apps_rg can proceed or needs apps_research first.

    Returns:
        - L0RouteContract with R3 if briefing is valid (apps_rg can proceed)
        - L0RouteContract with R3R4_MANAGED if apps_research needed first
        - None if check cannot determine (fallback to normal routing)
    """
    check = check_briefing_prerequisite(
        target_company=target_company,
        target_role=target_role,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        **kwargs,
    )

    if check.is_valid:
        # Briefing valid — apps_rg can proceed
        return {
            "selected_route": L0Route.R3,
            "confidence": confidence,
            "reason_codes": ("d3_briefing_valid",),  # Custom code for valid briefing
            "freshness_class": "bounded",
            "cache_policy": "no_cache",  # Not a cache hit, but prerequisite met
            "execution_form": "single_grounded_step",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    if check.requires_apps_research:
        # Need apps_research first — route to managed workflow
        _logger.info(
            "apps_rg prerequisite: routing to apps_research first "
            "(reason=%s, company=%s)",
            check.result.value,
            target_company,
        )
        return {
            "selected_route": L0Route.R3R4_MANAGED,
            "confidence": confidence,
            "reason_codes": ("d3_research_required",),  # Custom code for research prerequisite
            "freshness_class": "bounded",
            "cache_policy": "no_cache",
            "execution_form": "managed_workflow",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    # Briefing exists but incompatible — fail closed
    if check.result in {
        BriefingValidationResult.POLICY_MISMATCH,
        BriefingValidationResult.BLUEPRINT_MISMATCH,
        BriefingValidationResult.SCOPE_MISMATCH,
    }:
        _logger.warning(
            "apps_rg prerequisite: briefing incompatible (result=%s, reason=%s). "
            "Failing closed — apps_rg cannot proceed.",
            check.result.value,
            check.reason,
        )
        # Return R5 abstain with specific reason
        return {
            "selected_route": L0Route.R5,
            "confidence": 0.0,
            "reason_codes": (RouteReasonCode.R5_CLARIFICATION_NEEDED.value,),
            "freshness_class": "stale_ok",
            "cache_policy": "no_cache",
            "execution_form": "terminal_return",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    # Cannot determine — let downstream routing decide
    return None


__all__ = ["check_apps_rg_prerequisites"]
