"""CLI prerequisite probe for apps_rg historical research briefing checks."""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.prerequisites.briefing_validator import (
    BriefingValidationResult,
    check_briefing_prerequisite,
)

_logger = logging.getLogger(__name__)


def check_apps_rg_cli_prerequisites(**kwargs: Any) -> dict[str, Any] | None:
    """Validate apps_rg prerequisites without reaching back into core L0 gates."""
    target_company = str(kwargs.get("target_company", "") or "")
    target_role = str(kwargs.get("target_role", "") or "")
    policy_hash = str(kwargs.get("policy_hash", "") or "")
    trace_id = str(kwargs.get("trace_id", "") or "")
    confidence = float(kwargs.get("confidence", 1.0) or 1.0)
    briefing = kwargs.get("briefing")

    check = check_briefing_prerequisite(
        briefing,
        target_company=target_company,
        target_role=target_role,
    )

    if check.is_valid:
        return {
            "selected_route": "R3",
            "confidence": confidence,
            "reason_codes": ("d3_briefing_valid",),
            "freshness_class": "bounded",
            "cache_policy": "no_cache",
            "execution_form": "single_grounded_step",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    if check.requires_apps_research:
        _logger.info(
            "apps_rg prerequisite: routing to apps_research first "
            "(reason=%s, company=%s)",
            check.result.value,
            target_company,
        )
        return {
            "selected_route": "R3R4_MANAGED",
            "confidence": confidence,
            "reason_codes": ("d3_research_required",),
            "freshness_class": "bounded",
            "cache_policy": "no_cache",
            "execution_form": "managed_workflow",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    if check.result in {
        BriefingValidationResult.POLICY_MISMATCH,
        BriefingValidationResult.BLUEPRINT_MISMATCH,
        BriefingValidationResult.SCOPE_MISMATCH,
    }:
        _logger.warning(
            "apps_rg prerequisite: briefing incompatible (result=%s, reason=%s)",
            check.result.value,
            check.reason,
        )
        return {
            "selected_route": "R5",
            "confidence": 0.0,
            "reason_codes": ("r5_clarification_needed",),
            "freshness_class": "stale_ok",
            "cache_policy": "no_cache",
            "execution_form": "terminal_return",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }

    return None
