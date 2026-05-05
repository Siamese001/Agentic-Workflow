"""HITL Policy Schema for apps_lic Re-engagement — L5 Safety.

Wave 3, Phase 1 of apps-lic-infra-prerequisites-unblock-p2p3

This module defines the HITL (Human-in-the-Loop) policy schema for
multi-touch re-engagement, specifying when human review is required.

App: apps_lic
Layer: L5 Safety (agentic_core/L5_safety/policy/)

Dependencies:
    - L5 Policy Framework (agentic_core/L5_safety/policy/framework.py)
    - apps_lic touch state (apps_lic/state/touch_state_registration.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# -----------------------------------------------------------------------------
# HITL Decision Types
# -----------------------------------------------------------------------------

class HITLTrigger(str, Enum):
    """Triggers that can initiate HITL review."""
    
    # Sequence-based triggers
    FIRST_TOUCH = "first_touch"                    # First outreach to recipient
    REENGAGEMENT_SEQUENCE = "reengagement_sequence"  # Nth touch in sequence (N>1)
    HIGH_SEQUENCE_NUMBER = "high_sequence_number"  # Touch 3+ in sequence
    
    # Signal-based triggers
    HIGH_CONFIDENCE_SIGNAL = "high_confidence_signal"  # Signal confidence > threshold
    SIGNAL_TYPE_SENSITIVE = "signal_type_sensitive"    # Sensitive trigger (e.g., layoff)
    SIGNAL_CONFLICT = "signal_conflict"                  # Conflicting signals
    
    # Context-based triggers
    EXECUTIVE_RECIPIENT = "executive_recipient"    # C-level or VP target
    PRIOR_NEGATIVE_REPLY = "prior_negative_reply"  # Previously got negative response
    PRIOR_OPT_OUT_ATTEMPT = "prior_opt_out_attempt"  # Prior opt-out indication
    
    # Content-based triggers
    TONE_CALIBRATION_FAIL = "tone_calibration_fail"  # Archetype mismatch
    HIGH_RISK_CONTENT = "high_risk_content"      # Content flagged as high-risk
    
    # Aggregate triggers
    COMPOUND_RISK = "compound_risk"              # Multiple low-risk factors combined
    MANUAL_REVIEW_FLAG = "manual_review_flag"    # Explicit flag from ops


class HITLReviewType(str, Enum):
    """Types of HITL review required."""
    
    PRE_SEND = "pre_send"            # Review before message sent
    POST_SEND = "post_send"          # Review after message sent (audit)
    REAL_TIME = "real_time"          # Real-time approval required
    BATCH_REVIEW = "batch_review"    # Can be reviewed in batch


class HITLResolution(str, Enum):
    """Possible resolutions of HITL review."""
    
    APPROVED = "approved"            # Approved as-is
    APPROVED_WITH_EDITS = "approved_with_edits"  # Approved with modifications
    REJECTED = "rejected"            # Rejected, do not send
    DEFERRED = "deferred"            # Defer to later review
    ESCALATED = "escalated"          # Escalate to higher authority


class HITLUrgency(str, Enum):
    """Urgency levels for HITL review."""
    
    CRITICAL = "critical"            # Review within 1 hour
    HIGH = "high"                    # Review within 4 hours
    NORMAL = "normal"                # Review within 24 hours
    LOW = "low"                      # Review within 72 hours


# -----------------------------------------------------------------------------
# HITL Policy Schema
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class HITLPolicyRule:
    """Single HITL policy rule.
    
    Fields
    ------
    rule_id : str
        Unique rule identifier
    trigger : HITLTrigger
        What condition triggers this rule
    review_type : HITLReviewType
        What type of review is required
    urgency : HITLUrgency
        How quickly review must happen
    conditions : dict
        Additional conditions for rule matching
    rationale : str
        Why this rule exists
    enabled : bool
        Whether rule is currently active
    """
    
    rule_id: str
    trigger: HITLTrigger
    review_type: HITLReviewType
    urgency: HITLUrgency
    conditions: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    enabled: bool = True


@dataclass(frozen=True)
class ReengagementHITLPolicy:
    """Complete HITL policy for apps_lic re-engagement.
    
    This policy specifies when human review is required for
touches in a multi-touch sequence.
    
    Fields
    ------
    policy_id : str
        Policy identifier (always "apps_lic.reengagement")
    version : str
        Policy version (semver)
    enabled : bool
        Whether policy is active
    rules : list[HITLPolicyRule]
        Policy rules in priority order
    default_urgency : HITLUrgency
        Default urgency if no rule matches
    compound_risk_threshold : int
        How many low-risk factors trigger compound review
    """
    
    policy_id: str = "apps_lic.reengagement"
    version: str = "1.0.0"
    enabled: bool = True
    rules: list[HITLPolicyRule] = field(default_factory=list)
    default_urgency: HITLUrgency = HITLUrgency.NORMAL
    compound_risk_threshold: int = 2
    
    def __post_init__(self):
        if not self.rules:
            # Auto-populate with default rules if empty
            object.__setattr__(self, 'rules', self._default_rules())
    
    @staticmethod
    def _default_rules() -> list[HITLPolicyRule]:
        """Generate default policy rules for apps_lic re-engagement."""
        return [
            # Critical: High sequence number + executive
            HITLPolicyRule(
                rule_id="R001",
                trigger=HITLTrigger.HIGH_SEQUENCE_NUMBER,
                review_type=HITLReviewType.PRE_SEND,
                urgency=HITLUrgency.HIGH,
                conditions={"min_sequence": 3, "recipient_tier": "executive"},
                rationale="Third+ touch to executives requires review to avoid fatigue",
            ),
            # Critical: Prior negative reply
            HITLPolicyRule(
                rule_id="R002",
                trigger=HITLTrigger.PRIOR_NEGATIVE_REPLY,
                review_type=HITLReviewType.PRE_SEND,
                urgency=HITLUrgency.CRITICAL,
                conditions={},
                rationale="Re-engaging after negative reply is high-risk",
            ),
            # High: Sensitive signal type
            HITLPolicyRule(
                rule_id="R003",
                trigger=HITLTrigger.SIGNAL_TYPE_SENSITIVE,
                review_type=HITLReviewType.PRE_SEND,
                urgency=HITLUrgency.HIGH,
                conditions={"sensitive_signals": ["layoff", "restructuring", "acquisition_target"]},
                rationale="Sensitive business signals require careful handling",
            ),
            # High: First touch to executive
            HITLPolicyRule(
                rule_id="R004",
                trigger=HITLTrigger.EXECUTIVE_RECIPIENT,
                review_type=HITLReviewType.PRE_SEND,
                urgency=HITLUrgency.HIGH,
                conditions={"touch_sequence": 1},
                rationale="First touch to executives requires approval",
            ),
            # Normal: Reengagement sequence
            HITLPolicyRule(
                rule_id="R005",
                trigger=HITLTrigger.REENGAGEMENT_SEQUENCE,
                review_type=HITLReviewType.BATCH_REVIEW,
                urgency=HITLUrgency.NORMAL,
                conditions={"min_sequence": 2, "max_sequence": 3},
                rationale="Standard batch review for sequence touches",
            ),
            # Low: High confidence signal (informational)
            HITLPolicyRule(
                rule_id="R006",
                trigger=HITLTrigger.HIGH_CONFIDENCE_SIGNAL,
                review_type=HITLReviewType.POST_SEND,
                urgency=HITLUrgency.LOW,
                conditions={"min_confidence": 0.9},
                rationale="High-confidence signals get post-send audit only",
            ),
        ]
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize policy to dictionary."""
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "enabled": self.enabled,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "trigger": r.trigger.value,
                    "review_type": r.review_type.value,
                    "urgency": r.urgency.value,
                    "conditions": r.conditions,
                    "rationale": r.rationale,
                    "enabled": r.enabled,
                }
                for r in self.rules
            ],
            "default_urgency": self.default_urgency.value,
            "compound_risk_threshold": self.compound_risk_threshold,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReengagementHITLPolicy:
        """Deserialize policy from dictionary."""
        rules = [
            HITLPolicyRule(
                rule_id=r["rule_id"],
                trigger=HITLTrigger(r["trigger"]),
                review_type=HITLReviewType(r["review_type"]),
                urgency=HITLUrgency(r["urgency"]),
                conditions=r.get("conditions", {}),
                rationale=r.get("rationale", ""),
                enabled=r.get("enabled", True),
            )
            for r in data.get("rules", [])
        ]
        
        return cls(
            policy_id=data.get("policy_id", "apps_lic.reengagement"),
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            rules=rules,
            default_urgency=HITLUrgency(data.get("default_urgency", "normal")),
            compound_risk_threshold=data.get("compound_risk_threshold", 2),
        )


# -----------------------------------------------------------------------------
# HITL Review Request / Result
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class HITLReviewRequest:
    """Request for HITL review.
    
    Fields
    ------
    review_id : str
        Unique review identifier
    touch_id : str
        Touch requiring review
    recipient_hash : str
        Hashed recipient identifier
    campaign_id : str
        Parent campaign
    triggered_rules : list[str]
        Which policy rules triggered this review
    review_type : HITLReviewType
        Type of review required
    urgency : HITLUrgency
        Review urgency
    context : dict
        Full context for reviewer
    created_at : str
        ISO timestamp when review created
    """
    
    review_id: str
    touch_id: str
    recipient_hash: str
    campaign_id: str
    triggered_rules: list[str]
    review_type: HITLReviewType
    urgency: HITLUrgency
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat())


@dataclass(frozen=True)
class HITLReviewResult:
    """Result of HITL review.
    
    Fields
    ------
    review_id : str
        Review that was resolved
    touch_id : str
        Touch that was reviewed
    resolution : HITLResolution
        Outcome of review
    resolved_by : str
        Who resolved the review
    resolved_at : str
        ISO timestamp when resolved
    notes : str
        Reviewer notes
    modifications : dict
        Any modifications made to content
    """
    
    review_id: str
    touch_id: str
    resolution: HITLResolution
    resolved_by: str
    resolved_at: str
    notes: str = ""
    modifications: dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# Policy Registry
# -----------------------------------------------------------------------------

class HITLPolicyRegistry:
    """Registry for HITL policies.
    
    Provides lookup and caching of HITL policies by app/purpose.
    """
    
    _policies: dict[str, ReengagementHITLPolicy] = {}
    
    @classmethod
    def register(cls, policy: ReengagementHITLPolicy) -> None:
        """Register a policy."""
        cls._policies[policy.policy_id] = policy
    
    @classmethod
    def get(cls, policy_id: str) -> Optional[ReengagementHITLPolicy]:
        """Get a registered policy."""
        return cls._policies.get(policy_id)
    
    @classmethod
    def get_or_default(cls, policy_id: str) -> ReengagementHITLPolicy:
        """Get policy or return default for apps_lic."""
        policy = cls.get(policy_id)
        if policy is None and policy_id == "apps_lic.reengagement":
            policy = ReengagementHITLPolicy()
            cls.register(policy)
        return policy or ReengagementHITLPolicy()


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "HITLTrigger",
    "HITLReviewType",
    "HITLResolution",
    "HITLUrgency",
    "HITLPolicyRule",
    "ReengagementHITLPolicy",
    "HITLReviewRequest",
    "HITLReviewResult",
    "HITLPolicyRegistry",
]
