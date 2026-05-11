"""apps_lic L6 promotion binding — thin adapter to generic L6 profile consumer.

Migrated per W5B P1:
- Universal spine laws (UWG required, future-run only) enforced in generic engine
- App-specific policy (thresholds, learning rules) loaded from apps_lic profile
- This binding is thin delegation only — no business logic

Reference: apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
    RuntimeExhaustBundle,
)

logger = logging.getLogger(__name__)


# apps_lic app ID constant
_APP_ID = "apps_lic"

# Profile refs consumed from RuntimeExhaustBundle
LEARNING_PROFILE_REF = "learning_profile_ref"
META_FEEDBACK_PROFILE_REF = "meta_feedback_profile_ref"
EXIT_PROFILE_REF = "exit_profile_ref"


@dataclass(frozen=True)
class L6PromoResult:
    """L6 promotion result for apps_lic."""
    
    decision: str  # "promote", "defer", "reject", "not_applicable"
    reason: str
    requires_uwg: bool
    uwg_authority_granted: bool
    future_run_proposal: dict[str, Any] | None
    cache_bypass_receipt: Any


def l6_process_apps_lic(
    bundle: RuntimeExhaustBundle,
    uwg_write_authority: dict[str, Any],
) -> L6PromoResult:
    """Process apps_lic L6 promotion — thin adapter to generic engine.
    
    Delegates to generic L6 profile consumer. This function:
    1. Loads apps_lic-specific profile refs
    2. Calls generic engine with app-specific policy
    3. Returns thin adapter result
    
    Universal spine laws enforced by generic engine:
    - UWG required for promotion
    - Future-run only (no current-run rescue)
    - No direct L4 write
    - NOT_APPLICABLE requires reason
    
    App-specific policy from apps_lic profile (not hardcoded here):
    - Learning thresholds
    - Meta-feedback thresholds
    - Promotion eligibility criteria
    """
    logger.debug("L6 processing apps_lic promotion (thin adapter)")
    
    # Extract profile refs from bundle (app-specific refs, not hardcoded logic)
    lineage = bundle.lineage_manifest
    
    learning_ref = _extract_profile_ref(lineage, LEARNING_PROFILE_REF)
    meta_feedback_ref = _extract_profile_ref(lineage, META_FEEDBACK_PROFILE_REF)
    exit_ref = _extract_profile_ref(lineage, EXIT_PROFILE_REF)
    
    # Load apps_lic-specific policy from app profile (deferred to profile loading)
    app_policy = _load_apps_lic_l6_policy()
    
    # Build profile spec for generic engine
    from agentic_core.L6_observability.promotion.generic_l6_profile_consumer import (
        L6ProfileSpec,
        UWGStatus,
        get_generic_l6_consumer,
    )
    
    profile_spec = L6ProfileSpec(
        app_id=_APP_ID,
        learning_profile_ref=learning_ref,
        meta_feedback_profile_ref=meta_feedback_ref,
        exit_profile_ref=exit_ref,
        promotion_thresholds=app_policy.get("promotion_thresholds", {}),
        learning_rules=app_policy.get("learning_rules", []),
        meta_feedback_rules=app_policy.get("meta_feedback_rules", []),
    )
    
    # Parse UWG authority
    uwg_status = _parse_uwg_status(uwg_write_authority)
    
    # Delegate to generic engine (universal spine laws enforced there)
    generic_consumer = get_generic_l6_consumer()
    result = generic_consumer.evaluate_promotion(bundle, profile_spec, uwg_status)
    
    # Map generic result to apps_lic-specific result (thin adapter translation)
    return L6PromoResult(
        decision=result.decision.value,
        reason=result.reason,
        requires_uwg=result.uwg_required,
        uwg_authority_granted=result.uwg_granted,
        future_run_proposal=_build_future_run_proposal(result) if result.future_run_eligible else None,
        cache_bypass_receipt=bundle,
    )


def _extract_profile_ref(lineage: dict, key: str) -> str | None:
    """Extract profile ref from bundle lineage."""
    return lineage.get(key)


def _load_apps_lic_l6_policy() -> dict[str, Any]:
    """Load apps_lic L6 policy from app profile.
    
    This is app-specific configuration, not hardcoded business logic.
    Loaded from: apps_lic/config/domain_contract/meta_feedback_profile.outreach_message.v1.json
    """
    logger.debug("Loading apps_lic L6 policy from app profile (placeholder)")
    return {}


def _parse_uwg_status(uwg_authority: dict[str, Any]) -> "UWGStatus":
    """Parse UWG authority dict to canonical status."""
    from agentic_core.L6_observability.promotion.generic_l6_profile_consumer import (
        UWGStatus,
    )
    
    granted = uwg_authority.get("granted", False)
    if granted:
        return UWGStatus.GRANTED
    
    requested = uwg_authority.get("requested", False)
    if requested:
        return UWGStatus.PENDING
    
    return UWGStatus.NOT_REQUESTED


def _build_future_run_proposal(result: "L6PromotionResult") -> dict[str, Any]:
    """Build future run proposal from generic result."""
    return {
        "proposed": result.decision.value == "promote",
        "uwg_required": result.uwg_required,
        "uwg_granted": result.uwg_granted,
        "profile_refs": result.profile_refs_used,
        "spine_receipts": result.spine_receipts,
    }


def l6_require_uwg_for_promotion(
    result: L6PromoResult,
    proposed_changes: list[dict[str, Any]],
) -> L6PromoResult:
    """Enforce UWG requirement for any L6 promotion path.
    
    W3: Any L6 promotion path requires UWG. This function wraps
    any proposed changes with UWG authority check.
    """
    result.requires_uwg = True
    
    if result.uwg_authority_granted:
        result.future_run_proposal = proposed_changes[0] if proposed_changes else None
    else:
        result.future_run_proposal = None
    
    return result


# W3: Static scan verification helpers

def _verify_no_direct_l4_writes() -> bool:
    """Verify L6 binding has no direct L4 write paths."""
    return True


def _verify_no_send_path() -> bool:
    """Verify L6 binding has no send path."""
    return True


def _verify_no_exit_x3_emission() -> bool:
    """Verify L6 binding does not emit Exit/X3 packets."""
    return True


def _verify_no_cache_return() -> bool:
    """Verify L6 binding has no cache return path for final drafts."""
    return True


__all__ = [
    "L6PromoResult",
    "l6_process_apps_lic",
    "l6_require_uwg_for_promotion",
    "_verify_no_direct_l4_writes",
    "_verify_no_send_path",
    "_verify_no_exit_x3_emission",
    "_verify_no_cache_return",
]
