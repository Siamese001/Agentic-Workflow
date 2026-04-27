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


# --- v4 Capability-Token schema additions (G6) ---------------------------------
class PermissionLadderEntry(str, Enum):
    """`capability_token.schema.md` §2 — graduated permission rungs."""

    READ = "read"
    SUGGEST = "suggest"
    MUTATE = "mutate"
    EXTERNAL = "external"


class GrantMode(str, Enum):
    """`capability_token.schema.md` §1 — connector / tool authorization."""

    ONE_TIME = "one_time"
    PERMANENT = "permanent"
    SESSIONED = "sessioned"


class LifecycleState(str, Enum):
    """`capability_token.schema.md` §6 — token lifecycle state machine."""

    ISSUED = "ISSUED"
    IN_USE = "IN_USE"
    EXPIRED = "EXPIRED"
    CONSUMED = "CONSUMED"
    REVOKED = "REVOKED"
    STEP_UP_PENDING = "STEP_UP_PENDING"


# --- Guardrail family taxonomy (G9) --------------------------------------------
class GuardrailFamilyId(str, Enum):
    """`guardrail_families.md` §1 — 18 named families F-01..F-18."""

    F01_MODERATION = "F-01"
    F02_SECRET_KEYS = "F-02"
    F03_CONTAINS_PII = "F-03"
    F04_JAILBREAK = "F-04"
    F05_PROMPT_INJECTION = "F-05"
    F06_NSFW = "F-06"
    F07_URL_FILTER = "F-07"
    F08_HALLUCINATION = "F-08"
    F09_OFF_TOPIC = "F-09"
    F10_COMPETITORS = "F-10"
    F11_KEYWORD_FILTER = "F-11"
    F12_CUSTOM_PROMPT_CHECK = "F-12"
    F13_SENSITIVE_DATA = "F-13"
    F14_GUARD_MODEL_REVIEW = "F-14"
    F15_HANDOFF_VALIDITY = "F-15"
    F16_CONTEXT_BLEED = "F-16"
    F17_SUPPLY_CHAIN_DIGEST = "F-17"
    F18_THREAT_INTEL_SIGNATURE = "F-18"


class GuardrailStage(str, Enum):
    """`guardrail_families.md` — stage taxonomy."""

    INGRESS = "INGRESS"
    EGRESS = "EGRESS"
    HANDOFF = "HANDOFF"
    CONTEXT = "CONTEXT"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"


class GuardrailBank(str, Enum):
    """`guardrail_families.md` §2 — bank assignment."""

    CLIENT_UNIVERSAL = "CLIENT_UNIVERSAL"
    AGENT_DOMAIN = "AGENT_DOMAIN"
    EGRESS_INSPECTION = "EGRESS_INSPECTION"


class EvaluatorKind(str, Enum):
    """`guardrail_families.md` §4 — evaluator kind."""

    REGEX = "REGEX"
    CLASSIFIER = "CLASSIFIER"
    LLM_JUDGE = "LLM_JUDGE"
    GUARD_MODEL = "GUARD_MODEL"
    DIGEST_MATCH = "DIGEST_MATCH"


# --- Risk-tier control matrix bands (G10) --------------------------------------
class AuditDetailLevel(str, Enum):
    """`risk_tier_bands.md` §3 — audit log detail by band."""

    SUMMARY = "summary"
    FULL = "full"
    FULL_STRUCTURED = "full+structured"


class RetentionBand(str, Enum):
    """`risk_tier_bands.md` §3 + `calibration_assurance_planes.md` §4.3 — retention by band."""

    SHORT = "short"
    STANDARD = "standard"
    EXTENDED_FORENSIC = "extended+forensic"


class SandboxIsolationTier(str, Enum):
    """`risk_tier_bands.md` §3 — sandbox isolation by band."""

    PROCESS = "process"
    PROCESS_FS = "process+fs"
    PROCESS_FS_NET = "process+fs+net"


class ConnectorAllowlistWidth(str, Enum):
    """`risk_tier_bands.md` §3 — connector allowlist width."""

    DEFAULT = "default"
    NARROWED = "narrowed"
    STRICT = "strict"


class CalibrationCadence(str, Enum):
    """`risk_tier_bands.md` §3 — calibration cadence."""

    WEEKLY = "weekly"
    DAILY = "daily"
    CONTINUOUS = "continuous"


# --- Egress kind taxonomy (G5) -------------------------------------------------
class EgressKind(str, Enum):
    """`00A.5` egress lane taxonomy."""

    MODEL = "MODEL"
    TOOL = "TOOL"
    CONNECTOR = "CONNECTOR"
    NETWORK = "NETWORK"


# --- Static drift kind taxonomy (G7) -------------------------------------------
class StaticDriftKind(str, Enum):
    """`00A.7` static drift taxonomy."""

    ARCHITECTURE = "ARCHITECTURE"
    POLICY = "POLICY"
    REGISTRY = "REGISTRY"
    PROMPT = "PROMPT"
    CONNECTOR_CONFIG = "CONNECTOR_CONFIG"
    ROUTE_WORKFLOW = "ROUTE_WORKFLOW"
    HIDDEN_EGRESS = "HIDDEN_EGRESS"
    DIRECT_WRITE_PATH = "DIRECT_WRITE_PATH"
    BYPASS_WRAPPER = "BYPASS_WRAPPER"
    GOLDEN_SNAPSHOT = "GOLDEN_SNAPSHOT"


# --- Snapshot match status (G1) ------------------------------------------------
class MatchStatus(str, Enum):
    """`00A.8` snapshot verification match status."""

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    DEGRADED = "DEGRADED"
    REPLAY_APPROVED = "REPLAY_APPROVED"


# --- Promotion plane (G11) -----------------------------------------------------
class PromotionPlane(str, Enum):
    """`calibration_assurance_planes.md` — out-of-band plane source."""

    CALIBRATION = "CALIBRATION"
    ASSURANCE = "ASSURANCE"
    AUDIT_FORENSIC = "AUDIT_FORENSIC"


__all__ = [
    "AuditDetailLevel",
    "BoundaryClassification",
    "CalibrationCadence",
    "ConnectorAllowlistWidth",
    "DecisionVerdict",
    "EgressKind",
    "EvaluatorKind",
    "GovernanceMode",
    "GrantMode",
    "GuardrailBank",
    "GuardrailFamilyId",
    "GuardrailStage",
    "LifecycleState",
    "MatchStatus",
    "NextLane",
    "OriginLabel",
    "PacketKind",
    "PermissionLadderEntry",
    "PromotionPlane",
    "ReasonCode",
    "RetentionBand",
    "ReviewDepth",
    "RiskTierBandV5",
    "SandboxIsolationTier",
    "SideEffectClass",
    "StandardsTag",
    "StaticDriftKind",
    "TriageFlag",
]
