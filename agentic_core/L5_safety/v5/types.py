"""v5 governance enums.

Each enum maps directly to a numbered section of
``docs/reference/00_L5_Policy_Plane/Governance & Safety v5.md``.

All values are deterministic strings so canonical JSON serialization is
stable across hosts. v5 introduces CRITICAL (missing in v4's
``RiskTierBand`` literal in ``agentic_core.interfaces.principal_chain_types``).
"""

from __future__ import annotations

from enum import Enum


class PacketKind(str, Enum):
    """Spec G0 INPUT PACKET TYPES (lines 24–31)."""

    REQUEST_ENVELOPE = "request_envelope"
    L1_PLAN_CONTRACT = "l1_plan_contract"
    L0_ROUTE_CONTRACT = "l0_route_contract"
    L3_STEP_CONTRACT = "l3_step_contract"
    L2_EXECUTION_REQUEST = "l2_execution_request"
    HITL_REENTRY_PACKET = "hitl_reentry_packet"
    EXIT_DISPOSITION_REQUEST = "exit_disposition_request"


class SideEffectClass(str, Enum):
    """Spec G0 declared side_effect_class (line 37)."""

    NONE = "NONE"
    READ = "READ"
    MODEL_CALL = "MODEL_CALL"
    TOOL_CALL = "TOOL_CALL"
    NETWORK = "NETWORK"
    MEMORY = "MEMORY"
    WRITE_PROPOSAL = "WRITE_PROPOSAL"
    EXTERNAL_COMMIT = "EXTERNAL_COMMIT"


class GovernanceMode(str, Enum):
    """Spec G1 MODE SELECTION (lines 61–66)."""

    STATIC_CHECK = "STATIC_CHECK"
    RUNTIME_CHECK = "RUNTIME_CHECK"
    HUMAN_REENTRY = "HUMAN_REENTRY"
    COMMIT_REVIEW = "COMMIT_REVIEW"
    INCIDENT_REVIEW = "INCIDENT_REVIEW"


class RiskTierBandV5(str, Enum):
    """Spec G1 RISK TIER BAND ASSIGNMENT (lines 68–72).

    v5 adds CRITICAL on top of v4's LOW/MODERATE/HIGH literal.
    """

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewDepth(str, Enum):
    """Spec G1 review_depth (line 85)."""

    FAST_PATH = "FAST_PATH"
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    LOCKDOWN = "LOCKDOWN"


class TriageFlag(str, Enum):
    """Spec G1 triage_flags (line 86)."""

    INJECTION_SUSPECTED = "injection_suspected"
    SCOPE_MISMATCH = "scope_mismatch"
    IDENTITY_GAP = "identity_gap"
    REGISTRY_GAP = "registry_gap"
    SIDE_EFFECT_MISMATCH = "side_effect_mismatch"
    HARD_CONSTRAINT_CANDIDATE = "hard_constraint_candidate"


class NextLane(str, Enum):
    """Spec G1 next_lane (line 87)."""

    STATIC_LANE = "STATIC_LANE"
    RUNTIME_LANE = "RUNTIME_LANE"
    BOTH_LANES = "BOTH_LANES"
    DECISION_RAIL_REJECT = "DECISION_RAIL_REJECT"


class OriginLabel(str, Enum):
    """Spec G2a ORIGIN LABELS (lines 168–177).

    Authority order (highest first): system_policy > governance_policy >
    registry_config > developer_admin > retrieved/tool_output/human_review >
    user_turn > prior_artifact.
    """

    SYSTEM_POLICY = "system_policy"
    GOVERNANCE_POLICY = "governance_policy"
    REGISTRY_CONFIG = "registry_config"
    DEVELOPER_ADMIN = "developer_admin"
    USER_TURN = "user_turn"
    RETRIEVED = "retrieved"
    TOOL_OUTPUT = "tool_output"
    HUMAN_REVIEW = "human_review"
    PRIOR_ARTIFACT = "prior_artifact"


class BoundaryClassification(str, Enum):
    """Spec G2a boundary_classification (line 188)."""

    TRUSTED_INSTRUCTION = "trusted_instruction"
    UNTRUSTED_DATA = "untrusted_data"
    QUARANTINED = "quarantined"
    STRIPPED = "stripped"
    REJECTED = "rejected"


class DecisionVerdict(str, Enum):
    """Spec Decision Rail terminal verdicts (lines 611–636)."""

    REJECT = "REJECT"
    REMEDIATE = "REMEDIATE"
    ESCALATE = "ESCALATE"
    CERTIFY = "CERTIFY"


class ReasonCode(str, Enum):
    """Spec GovernanceResult.reason_codes (lines 663–681)."""

    POLICY_VIOLATION = "policy_violation"
    HARD_CONSTRAINT_BREACH = "hard_constraint_breach"
    MISSING_AUTHORITY = "missing_authority"
    REGISTRY_MISMATCH = "registry_mismatch"
    ROUTE_MISMATCH = "route_mismatch"
    INJECTION_DETECTED = "injection_detected"
    CONTEXT_BLEED = "context_bleed"
    CROSS_TENANT_RISK = "cross_tenant_risk"
    DATA_SENSITIVITY_RISK = "data_sensitivity_risk"
    EVIDENCE_WEAK = "evidence_weak"
    GROUNDEDNESS_REQUIRED = "groundedness_required"
    HITL_REQUIRED = "HITL_required"
    SANDBOX_INSUFFICIENT = "sandbox_insufficient"
    REPLAY_INCOMPLETE = "replay_incomplete"
    PROVIDER_MISMATCH = "provider_mismatch"
    TOOL_SCHEMA_MISMATCH = "tool_schema_mismatch"
    CONNECTOR_SCOPE_MISMATCH = "connector_scope_mismatch"
    BUDGET_EXCEEDED = "budget_exceeded"
    DRIFT_DETECTED = "drift_detected"


class StandardsTag(str, Enum):
    """Spec G2 standards_fingerprint (line 108) + GovernanceResult (lines 686–692)."""

    NIST_AI_RMF = "NIST_AI_RMF"
    ISO_42001 = "ISO_42001"
    COSAI_BASELINES = "CoSAI_baselines"
    SOC2_CONTROLS = "SOC2_controls"
    SECTOR_OVERLAY = "sector_overlay"
    INTERNAL_OVERLAY = "internal_overlay"


__all__ = [
    "BoundaryClassification",
    "DecisionVerdict",
    "GovernanceMode",
    "NextLane",
    "OriginLabel",
    "PacketKind",
    "ReasonCode",
    "ReviewDepth",
    "RiskTierBandV5",
    "SideEffectClass",
    "StandardsTag",
    "TriageFlag",
]
