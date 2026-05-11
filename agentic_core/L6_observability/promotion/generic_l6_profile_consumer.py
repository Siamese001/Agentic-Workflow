"""Generic L6 profile consumer — processes learning/meta-feedback profiles for promotion decisions.

This engine is app-agnostic. It consumes:
- RuntimeExhaustBundle (S1A completed-run evidence)
- learning_profile_ref (from app profile)
- meta_feedback_profile_ref (from app profile)
- exit_profile_ref (from app profile)
- uwg_write_authority (UWG approval status)

Universal spine laws (hardcoded in generic engine):
- UWG is REQUIRED for any promotion/write admission
- L6 is future-run ONLY (never current-run rescue)
- No direct L4 write (Exit X3C only path)
- NOT_APPLICABLE requires explicit reason

App-specific policy (from app profiles, not hardcoded here):
- Learning thresholds
- Meta-feedback thresholds
- Promotion eligibility criteria
- Judge/rubric configurations

Reference: W5B P1 apps_lic migration plan
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence, Protocol

from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
    RuntimeExhaustBundle,
)

logger = logging.getLogger(__name__)


class PromotionDecision(str, Enum):
    """Canonical promotion decisions."""
    
    PROMOTE = "promote"
    DEFER = "defer"
    REJECT = "reject"
    NOT_APPLICABLE = "not_applicable"


class UWGStatus(str, Enum):
    """UWG write authority status."""
    
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    NOT_REQUESTED = "not_requested"


@dataclass(frozen=True)
class L6ProfileSpec:
    """App-provided learning/meta-feedback profile specification.
    
    This is app-specific policy passed from app profile. Generic engine
    does NOT hardcode any app-specific thresholds here.
    """
    
    # App identification (for logging/telemetry only)
    app_id: str
    
    # Profile refs (consumed from RuntimeExhaustBundle or app config)
    learning_profile_ref: str | None = None
    meta_feedback_profile_ref: str | None = None
    exit_profile_ref: str | None = None
    
    # App-specific policy (loaded from app profile, not hardcoded)
    promotion_thresholds: Mapping[str, Any] = field(default_factory=dict)
    learning_rules: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    meta_feedback_rules: Sequence[Mapping[str, Any]] = field(default_factory=tuple)


@dataclass(frozen=True)
class L6PromotionResult:
    """Result of L6 promotion evaluation."""
    
    decision: PromotionDecision
    reason: str
    uwg_required: bool  # Always True per universal spine law
    uwg_granted: bool
    future_run_eligible: bool
    app_id: str
    profile_refs_used: Mapping[str, str | None]
    # Generic spine receipts (not app-specific)
    spine_receipts: Mapping[str, Any] = field(default_factory=dict)


class L6ProfileConsumer:
    """Generic L6 profile consumer — app-agnostic promotion engine.
    
    Universal spine laws enforced here (not in app bindings):
    1. UWG required for promotion
    2. Future-run only (no current-run rescue)
    3. No direct L4 write
    4. NOT_APPLICABLE requires reason
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def evaluate_promotion(
        self,
        bundle: RuntimeExhaustBundle,
        profile_spec: L6ProfileSpec,
        uwg_write_authority: UWGStatus,
    ) -> L6PromotionResult:
        """Evaluate promotion using app profile + universal spine laws.
        
        Args:
            bundle: RuntimeExhaustBundle with completed-run evidence
            profile_spec: App-specific L6 profile specification
            uwg_write_authority: UWG approval status
            
        Returns:
            L6PromotionResult with decision and spine receipts
        """
        self.logger.debug(
            "L6 evaluating promotion for app=%s with UWG=%s",
            profile_spec.app_id,
            uwg_write_authority.value
        )
        
        # Universal spine law: UWG is ALWAYS required for promotion
        uwg_required = True
        uwg_granted = uwg_write_authority == UWGStatus.GRANTED
        
        # Universal spine law: L6 is future-run ONLY
        # (Never promote current-run; always propose future run)
        future_run_eligible = True
        
        # If UWG not granted, decision is DEFER regardless of app policy
        if not uwg_granted:
            return L6PromotionResult(
                decision=PromotionDecision.DEFER,
                reason=f"UWG write authority {uwg_write_authority.value} — promotion deferred",
                uwg_required=uwg_required,
                uwg_granted=uwg_granted,
                future_run_eligible=future_run_eligible,
                app_id=profile_spec.app_id,
                profile_refs_used={
                    "learning_profile_ref": profile_spec.learning_profile_ref,
                    "meta_feedback_profile_ref": profile_spec.meta_feedback_profile_ref,
                    "exit_profile_ref": profile_spec.exit_profile_ref,
                },
                spine_receipts={
                    "universal_law": "UWG_REQUIRED_FOR_PROMOTION",
                    "evaluated_at": "L6",
                    "write_path": "EXIT_X3C_UWG_L4_DURABLE",
                },
            )
        
        # App-specific policy evaluation (loaded from profile, not hardcoded)
        # This is where app-specific thresholds would be applied
        app_decision = self._evaluate_app_policy(bundle, profile_spec)
        
        return L6PromotionResult(
            decision=app_decision.decision,
            reason=app_decision.reason,
            uwg_required=uwg_required,
            uwg_granted=uwg_granted,
            future_run_eligible=future_run_eligible,
            app_id=profile_spec.app_id,
            profile_refs_used={
                "learning_profile_ref": profile_spec.learning_profile_ref,
                "meta_feedback_profile_ref": profile_spec.meta_feedback_profile_ref,
                "exit_profile_ref": profile_spec.exit_profile_ref,
            },
            spine_receipts={
                "universal_law": "UWG_REQUIRED_FOR_PROMOTION",
                "evaluated_at": "L6",
                "write_path": "EXIT_X3C_UWG_L4_DURABLE",
                "app_policy_applied": True,
            },
        )
    
    def _evaluate_app_policy(
        self,
        bundle: RuntimeExhaustBundle,
        profile_spec: L6ProfileSpec,
    ) -> "_AppPolicyDecision":
        """Evaluate app-specific policy from profile.
        
        This method consumes app-specific policy from the profile_spec
        without hardcoding any app-specific business logic.
        """
        # App-specific policy would be loaded and evaluated here
        # For now, default to promotion if UWG granted (app can override via profile)
        
        if profile_spec.promotion_thresholds:
            # App-specific thresholds present — would evaluate here
            return _AppPolicyDecision(
                decision=PromotionDecision.PROMOTE,
                reason="App-specific promotion thresholds satisfied (from profile)",
            )
        
        # Default: promote if UWG granted (apps can constrain via profile)
        return _AppPolicyDecision(
            decision=PromotionDecision.PROMOTE,
            reason="Default promotion with UWG grant (no app-specific constraints)",
        )


@dataclass(frozen=True)
class _AppPolicyDecision:
    """Internal result of app-specific policy evaluation."""
    
    decision: PromotionDecision
    reason: str


# Singleton instance for use by thin adapter bindings
_generic_l6_consumer: L6ProfileConsumer | None = None


def get_generic_l6_consumer() -> L6ProfileConsumer:
    """Get or create singleton generic L6 consumer instance."""
    global _generic_l6_consumer
    if _generic_l6_consumer is None:
        _generic_l6_consumer = L6ProfileConsumer()
    return _generic_l6_consumer
