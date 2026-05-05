"""Re-engagement Policy Evaluator for apps_lic — L5 Safety.

Wave 3, Phase 2 of apps-lic-infra-prerequisites-unblock-p2p3

This module evaluates HITL policy rules against touch context to determine
when human review is required for re-engagement touches.

App: apps_lic
Layer: L5 Safety (agentic_core/L5_safety/evaluators/)

Dependencies:
    - HITL Policy Schema (agentic_core/L5_safety/policy/apps_lic_reengagement.py)
    - Touch State (agentic_core/L4_state/uwg/touch_state_writer.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

from agentic_core.L5_safety.policy.apps_lic_reengagement import (
    HITLTrigger,
    HITLReviewType,
    HITLUrgency,
    HITLPolicyRule,
    ReengagementHITLPolicy,
    HITLReviewRequest,
    HITLPolicyRegistry,
)


# -----------------------------------------------------------------------------
# Evaluation Request / Result
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PolicyEvalRequest:
    """Request to evaluate HITL policy for a touch.
    
    Fields
    ------
    touch_id : str
        Touch being evaluated
    recipient_hash : str
        Hashed recipient identifier
    campaign_id : str
        Parent campaign
    touch_sequence : int
        Position in sequence (1-indexed)
    recipient_tier : str
        Recipient seniority: "executive"|"senior"|"mid"|"junior"
    trigger_signal : Optional[str]
        What triggered this touch
    trigger_confidence : float
        Confidence in trigger (0.0-1.0)
    prior_replies : list[dict]
        History of prior replies in sequence
    tone_calibration_passed : bool
        Whether tone calibration succeeded
    content_risk_score : float
        Content risk assessment (0.0-1.0)
    manual_review_flag : bool
        Explicit flag from ops
    """
    
    touch_id: str
    recipient_hash: str
    campaign_id: str
    touch_sequence: int
    recipient_tier: str = "mid"
    trigger_signal: Optional[str] = None
    trigger_confidence: float = 0.0
    prior_replies: list[dict] = field(default_factory=list)
    tone_calibration_passed: bool = True
    content_risk_score: float = 0.0
    manual_review_flag: bool = False


@dataclass(frozen=True)
class PolicyEvalResult:
    """Result of HITL policy evaluation.
    
    Fields
    ------
    touch_id : str
        Touch that was evaluated
    requires_hitl : bool
        Whether HITL review is required
    triggered_rules : list[str]
        Which rules triggered (if any)
    review_type : HITLReviewType
        Type of review required
    urgency : HITLUrgency
        Review urgency
    review_request : Optional[HITLReviewRequest]
        Populated if HITL required
    risk_factors : list[str]
        All risk factors identified
    evaluated_at : str
        ISO timestamp
    """
    
    touch_id: str
    requires_hitl: bool
    triggered_rules: list[str] = field(default_factory=list)
    review_type: HITLReviewType = HITLReviewType.POST_SEND
    urgency: HITLUrgency = HITLUrgency.LOW
    review_request: Optional[HITLReviewRequest] = None
    risk_factors: list[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# -----------------------------------------------------------------------------
# Risk Factor Detector
# -----------------------------------------------------------------------------

class RiskFactorDetector:
    """Detects risk factors in touch context for policy evaluation.
    
    This class maps raw context fields to HITL triggers, providing
    the bridge between touch data and policy rules.
    """
    
    # Sensitive signal types that require extra care
    SENSITIVE_SIGNALS = {
        "layoff",
        "restructuring",
        "acquisition_target",
        "merger",
        "downsizing",
        "bankruptcy",
        "leadership_change",
        "investigation",
    }
    
    def __init__(self, request: PolicyEvalRequest):
        self._request = request
    
    def detect_all(self) -> dict[HITLTrigger, dict[str, Any]]:
        """Detect all risk factors present in context.
        
        Returns
        -------
        dict[HITLTrigger, dict]
            Mapping of detected triggers to their context data
        """
        factors = {}
        
        # Sequence-based triggers
        if self._request.touch_sequence == 1:
            factors[HITLTrigger.FIRST_TOUCH] = {"sequence": 1}
        elif self._request.touch_sequence > 1:
            factors[HITLTrigger.REENGAGEMENT_SEQUENCE] = {"sequence": self._request.touch_sequence}
        
        if self._request.touch_sequence >= 3:
            factors[HITLTrigger.HIGH_SEQUENCE_NUMBER] = {"sequence": self._request.touch_sequence}
        
        # Signal-based triggers
        if self._request.trigger_confidence >= 0.8:
            factors[HITLTrigger.HIGH_CONFIDENCE_SIGNAL] = {
                "confidence": self._request.trigger_confidence,
            }
        
        if self._request.trigger_signal in self.SENSITIVE_SIGNALS:
            factors[HITLTrigger.SIGNAL_TYPE_SENSITIVE] = {
                "signal": self._request.trigger_signal,
            }
        
        # Context-based triggers
        if self._request.recipient_tier == "executive":
            factors[HITLTrigger.EXECUTIVE_RECIPIENT] = {
                "tier": self._request.recipient_tier,
            }
        
        # Prior reply analysis
        negative_replies = [
            r for r in self._request.prior_replies
            if r.get("classification") == "negative"
        ]
        if negative_replies:
            factors[HITLTrigger.PRIOR_NEGATIVE_REPLY] = {
                "count": len(negative_replies),
                "last_at": negative_replies[-1].get("received_at"),
            }
        
        opt_out_indicators = [
            r for r in self._request.prior_replies
            if r.get("opt_out_indicated", False)
        ]
        if opt_out_indicators:
            factors[HITLTrigger.PRIOR_OPT_OUT_ATTEMPT] = {
                "count": len(opt_out_indicators),
            }
        
        # Content-based triggers
        if not self._request.tone_calibration_passed:
            factors[HITLTrigger.TONE_CALIBRATION_FAIL] = {}
        
        if self._request.content_risk_score > 0.7:
            factors[HITLTrigger.HIGH_RISK_CONTENT] = {
                "risk_score": self._request.content_risk_score,
            }
        
        # Manual flag
        if self._request.manual_review_flag:
            factors[HITLTrigger.MANUAL_REVIEW_FLAG] = {}
        
        # Compound risk detection
        risk_count = len([
            f for f in factors.keys()
            if f not in (
                HITLTrigger.HIGH_CONFIDENCE_SIGNAL,
                HITLTrigger.FIRST_TOUCH,
            )
        ])
        if risk_count >= 2:
            factors[HITLTrigger.COMPOUND_RISK] = {
                "risk_factor_count": risk_count,
                "base_factors": list(factors.keys()),
            }
        
        return factors
    
    def get_risk_factor_list(self) -> list[str]:
        """Get list of risk factor names as strings."""
        factors = self.detect_all()
        return [f.value for f in factors.keys()]


# -----------------------------------------------------------------------------
# Policy Evaluator
# -----------------------------------------------------------------------------

class ReengagementPolicyEvaluator:
    """Evaluator for apps_lic re-engagement HITL policy.
    
    This class implements the policy evaluation logic, matching
detected risk factors against policy rules to determine if HITL
review is required.
    
    Parameters
    ----------
    policy : Optional[ReengagementHITLPolicy]
        Policy to evaluate against. Uses default if None.
    """
    
    def __init__(
        self,
        policy: Optional[ReengagementHITLPolicy] = None,
    ):
        self._policy = policy or HITLPolicyRegistry.get_or_default("apps_lic.reengagement")
    
    def evaluate(self, request: PolicyEvalRequest) -> PolicyEvalResult:
        """Evaluate HITL policy for a touch.
        
        Parameters
        ----------
        request : PolicyEvalRequest
            Evaluation request
        
        Returns
        -------
        PolicyEvalResult
            Evaluation result with HITL determination
        """
        # Detect risk factors
        detector = RiskFactorDetector(request)
        risk_factors = detector.detect_all()
        risk_factor_list = detector.get_risk_factor_list()
        
        # Match against policy rules
        triggered_rules = []
        highest_urgency = self._policy.default_urgency
        final_review_type = HITLReviewType.POST_SEND
        
        for rule in self._policy.rules:
            if not rule.enabled:
                continue
            
            # Check if rule trigger matches detected factors
            if rule.trigger in risk_factors:
                # Check additional conditions
                if self._check_conditions(rule, request, risk_factors[rule.trigger]):
                    triggered_rules.append(rule.rule_id)
                    
                    # Upgrade urgency if higher
                    if self._urgency_rank(rule.urgency) > self._urgency_rank(highest_urgency):
                        highest_urgency = rule.urgency
                    
                    # Upgrade review type if more strict
                    if self._review_type_rank(rule.review_type) > self._review_type_rank(final_review_type):
                        final_review_type = rule.review_type
        
        # Check compound risk threshold
        if len(risk_factors) >= self._policy.compound_risk_threshold:
            compound_rule = self._get_compound_rule()
            if compound_rule and compound_rule.rule_id not in triggered_rules:
                triggered_rules.append(compound_rule.rule_id)
        
        # Build result
        requires_hitl = len(triggered_rules) > 0
        
        review_request = None
        if requires_hitl:
            review_request = HITLReviewRequest(
                review_id=f"hitl-{request.touch_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                touch_id=request.touch_id,
                recipient_hash=request.recipient_hash,
                campaign_id=request.campaign_id,
                triggered_rules=triggered_rules,
                review_type=final_review_type,
                urgency=highest_urgency,
                context={
                    "recipient_tier": request.recipient_tier,
                    "touch_sequence": request.touch_sequence,
                    "trigger_signal": request.trigger_signal,
                    "trigger_confidence": request.trigger_confidence,
                    "prior_replies": request.prior_replies,
                    "tone_calibration_passed": request.tone_calibration_passed,
                    "content_risk_score": request.content_risk_score,
                    "risk_factors": risk_factor_list,
                },
            )
        
        return PolicyEvalResult(
            touch_id=request.touch_id,
            requires_hitl=requires_hitl,
            triggered_rules=triggered_rules,
            review_type=final_review_type,
            urgency=highest_urgency,
            review_request=review_request,
            risk_factors=risk_factor_list,
        )
    
    def _check_conditions(
        self,
        rule: HITLPolicyRule,
        request: PolicyEvalRequest,
        factor_context: dict[str, Any],
    ) -> bool:
        """Check if rule conditions match request context."""
        conditions = rule.conditions
        
        # Check sequence conditions
        if "min_sequence" in conditions:
            if request.touch_sequence < conditions["min_sequence"]:
                return False
        
        if "max_sequence" in conditions:
            if request.touch_sequence > conditions["max_sequence"]:
                return False
        
        if "touch_sequence" in conditions:
            if request.touch_sequence != conditions["touch_sequence"]:
                return False
        
        # Check recipient tier
        if "recipient_tier" in conditions:
            if request.recipient_tier != conditions["recipient_tier"]:
                return False
        
        # Check confidence
        if "min_confidence" in conditions:
            if request.trigger_confidence < conditions["min_confidence"]:
                return False
        
        # Check signal type
        if "sensitive_signals" in conditions:
            if request.trigger_signal not in conditions["sensitive_signals"]:
                return False
        
        return True
    
    def _urgency_rank(self, urgency: HITLUrgency) -> int:
        """Rank urgency for comparison (higher = more urgent)."""
        ranks = {
            HITLUrgency.LOW: 1,
            HITLUrgency.NORMAL: 2,
            HITLUrgency.HIGH: 3,
            HITLUrgency.CRITICAL: 4,
        }
        return ranks.get(urgency, 0)
    
    def _review_type_rank(self, review_type: HITLReviewType) -> int:
        """Rank review type for comparison (higher = more strict)."""
        ranks = {
            HITLReviewType.POST_SEND: 1,
            HITLReviewType.BATCH_REVIEW: 2,
            HITLReviewType.PRE_SEND: 3,
            HITLReviewType.REAL_TIME: 4,
        }
        return ranks.get(review_type, 0)
    
    def _get_compound_rule(self) -> Optional[HITLPolicyRule]:
        """Find compound risk rule in policy."""
        for rule in self._policy.rules:
            if rule.trigger == HITLTrigger.COMPOUND_RISK and rule.enabled:
                return rule
        return None


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------

def evaluate_touch_for_hitl(
    touch_id: str,
    recipient_hash: str,
    campaign_id: str,
    touch_sequence: int,
    **kwargs,
) -> PolicyEvalResult:
    """One-shot evaluation of a touch for HITL requirements.
    
    Parameters
    ----------
    touch_id : str
        Touch identifier
    recipient_hash : str
        Hashed recipient
    campaign_id : str
        Campaign ID
    touch_sequence : int
        Position in sequence
    **kwargs
        Additional PolicyEvalRequest fields
    
    Returns
    -------
    PolicyEvalResult
        Evaluation result
    
    Example
    -------
    >>> result = evaluate_touch_for_hitl(
    ...     touch_id="touch-123",
    ...     recipient_hash="hash-abc",
    ...     campaign_id="campaign-456",
    ...     touch_sequence=3,
    ...     recipient_tier="executive",
    ...     trigger_confidence=0.85,
    ... )
    >>> if result.requires_hitl:
    ...     print(f"HITL required: {result.triggered_rules}")
    """
    request = PolicyEvalRequest(
        touch_id=touch_id,
        recipient_hash=recipient_hash,
        campaign_id=campaign_id,
        touch_sequence=touch_sequence,
        **kwargs,
    )
    
    evaluator = ReengagementPolicyEvaluator()
    return evaluator.evaluate(request)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "PolicyEvalRequest",
    "PolicyEvalResult",
    "RiskFactorDetector",
    "ReengagementPolicyEvaluator",
    "evaluate_touch_for_hitl",
]
