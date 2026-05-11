"""Cross-App Delegation Runtime — Package-Driven Research Substrate Sharing

W12 Implementation: apps_rg/apps_lic delegate research to apps_research.

Hard Rules:
1. Delegation goes through U0 with proper caller_app_id
2. apps_research returns substrate (evidence data only)
3. Downstream apps treat substrate as evidence, not instruction
4. Tenant/session/context boundaries enforced
5. Final customized outputs never cached as terminal answers
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto


class DelegationType(Enum):
    """Types of cross-app delegation."""
    RESEARCH_SUBSTRATE = auto()
    UPLOADED_BRIEFING = auto()
    SOURCE_REGISTER = auto()


class ReuseEligibility(Enum):
    """Eligibility of substrate for reuse."""
    ELIGIBLE = auto()
    TENANT_MISMATCH = auto()
    CONTEXT_MISMATCH = auto()
    STALE = auto()
    JD_HASH_MISMATCH = auto()
    ROLE_CONTEXT_MISMATCH = auto()
    PROHIBITED_TERMINAL_CACHE = auto()


@dataclass(frozen=True)
class DelegationContext:
    """Context for cross-app delegation.
    
    Immutable context capturing delegation intent.
    """
    delegation_id: str
    caller_app_id: str  # apps_rg or apps_lic
    target_app_id: str  # apps_research
    
    # Task specification
    task_class: str  # research_substrate
    delegation_type: DelegationType
    
    # Content references
    jd_content_hash: str = ""  # Required for apps_rg when JD present
    role_context_hash: str = ""  # Required for apps_lic when role context present
    
    # Tenant/session boundaries
    tenant_id: str = ""
    session_id: str = ""
    
    # Policy compliance
    cross_app_reuse_policy_ref: str = ""
    uploaded_briefing_policy_ref: str = ""
    
    # Provenance
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_digest: str = ""


@dataclass(frozen=True)
class CrossAppPayload:
    """Payload for cross-app delegation.
    
    Passed from caller app to target app U0.
    """
    payload_id: str
    delegation_context: DelegationContext
    
    # U0 package overrides for delegated call
    runtime_package_overrides: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence from caller (uploaded briefings, etc.)
    evidence_bundles: List[Dict[str, Any]] = field(default_factory=list)
    
    # Policy hashes
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: List[str] = field(default_factory=list)
    
    # Replay key for idempotency
    replay_key: str = ""


@dataclass(frozen=True)
class SubstrateReturnPacket:
    """Return packet from apps_research to caller.
    
    Contains research substrate as evidence data only.
    Never instruction authority.
    """
    packet_id: str
    delegation_id: str
    caller_app_id: str
    target_app_id: str = "apps_research"
    
    # Research substrate (evidence data)
    research_substrate: Dict[str, Any] = field(default_factory=dict)
    entity_aliases: List[Dict[str, Any]] = field(default_factory=list)
    source_register: List[Dict[str, Any]] = field(default_factory=list)
    claim_evidence_map: List[Dict[str, Any]] = field(default_factory=list)
    
    # Data boundary label (always EVIDENCE_DATA_ONLY)
    data_boundary_label: str = "EVIDENCE_DATA_ONLY"
    
    # Provenance
    substrate_provenance: Dict[str, Any] = field(default_factory=dict)
    freshness_ttl_hours: int = 168  # 7 days default
    
    # Reuse eligibility
    reuse_eligibility: ReuseEligibility = ReuseEligibility.ELIGIBLE
    reuse_block_reasons: List[str] = field(default_factory=list)
    
    # Evidence digest
    evidence_digest: str = ""
    
    def is_evidence_only(self) -> bool:
        """Verify this packet is evidence data only."""
        return self.data_boundary_label == "EVIDENCE_DATA_ONLY"
    
    def is_reusable(self) -> bool:
        """Check if substrate is eligible for reuse."""
        return self.reuse_eligibility == ReuseEligibility.ELIGIBLE


@dataclass(frozen=True)
class DelegationResult:
    """Complete result of cross-app delegation."""
    delegation_id: str
    caller_app_id: str
    target_app_id: str
    
    # Success/failure
    success: bool
    substrate_packet: Optional[SubstrateReturnPacket] = None
    
    # Failure details
    failure_reason: str = ""
    validation_errors: List[str] = field(default_factory=list)
    
    # Evidence
    evidence_digest: str = ""


@dataclass(frozen=True)
class BriefingNormalizationResult:
    """Result of uploaded briefing normalization."""
    briefing_id: str
    normalized: bool
    
    # Normalization outputs
    research_substrate_ref: str = ""
    provenance_check_passed: bool = False
    acl_check_passed: bool = False
    injection_scan_passed: bool = False
    citation_gaps_tagged: List[str] = field(default_factory=list)
    
    # Data boundary
    data_boundary_label: str = "EVIDENCE_DATA_ONLY"
    
    # Errors
    errors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CrossAppReuseValidation:
    """Validation of cross-app substrate reuse."""
    substrate_id: str
    requesting_app_id: str
    
    eligible: bool = False
    eligibility: ReuseEligibility = ReuseEligibility.ELIGIBLE
    
    # Mismatch details
    tenant_mismatch: bool = False
    jd_hash_mismatch: bool = False
    role_context_mismatch: bool = False
    staleness_hours: int = 0
    
    # Validation timestamp
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


__all__ = [
    "DelegationType",
    "ReuseEligibility",
    "DelegationContext",
    "CrossAppPayload",
    "SubstrateReturnPacket",
    "DelegationResult",
    "BriefingNormalizationResult",
    "CrossAppReuseValidation",
]
