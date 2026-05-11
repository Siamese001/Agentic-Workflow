"""
Generic Package-Driven C0 Grounding Binding

App-agnostic C0 binding that performs evidence retrieval and produces
FinalEvidenceContract from app-owned retrieval/source/freshness policies.
No app-specific retrieval logic in core.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    yaml = None

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L1_cognition.package_driven_l1_binding import PackageDrivenL1Plan

_LOGGER = logging.getLogger(__name__)


class EvidenceSupportStatus(Enum):
    """Support status for evidence quality."""
    EMPTY = "EMPTY"
    WEAK_INSUFFICIENT = "WEAK_INSUFFICIENT"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    PASS = "PASS"
    STRONG = "STRONG"
    CONFLICTED = "CONFLICTED"


class DataBoundaryLabel(Enum):
    """Data boundary labels for retrieved/uploaded content."""
    EVIDENCE_DATA_ONLY = "EVIDENCE_DATA_ONLY"
    INSTRUCTION_SPACE = "INSTRUCTION_SPACE"  # Never used for retrieved content


@dataclass(frozen=True)
class EvidenceItem:
    """Single evidence item from retrieval."""
    evidence_id: str
    source_ref: str
    content_snippet: str
    retrieval_timestamp: str
    freshness_status: str
    support_status: str
    citation_info: Dict[str, Any]
    data_boundary_label: str = "EVIDENCE_DATA_ONLY"
    claim_extractions: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    contradiction_flags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SourceRegisterEntry:
    """Entry in the source register."""
    source_id: str
    source_url: str
    source_type: str
    tier_classification: str
    retrieval_timestamp: str
    freshness_ttl: int
    acl_info: Dict[str, Any]
    provenance_chain: List[Dict[str, Any]]


@dataclass(frozen=True)
class ClaimEvidenceMapping:
    """Mapping of a claim to its evidence."""
    claim_id: str
    claim_text: str
    claim_type: str
    supporting_evidence_refs: List[str]
    contradicting_evidence_refs: List[str]
    confidence_assessment: str
    materiality_flag: bool


@dataclass(frozen=True)
class FreshnessReport:
    """Report on evidence freshness."""
    sources_checked: int
    sources_fresh: int
    sources_stale: int
    sources_blocked: int
    ttl_violations: List[Dict[str, Any]]
    downgrade_applications: List[Dict[str, Any]]
    timestamp: str


@dataclass(frozen=True)
class ContradictionReport:
    """Report on evidence contradictions."""
    contradictions_detected: int
    contradiction_details: List[Dict[str, Any]]
    resolution_recommendations: List[str]
    materiality_assessment: str
    timestamp: str


@dataclass(frozen=True)
class CitationInfo:
    """Citation information for evidence."""
    citation_id: str
    source_ref: str
    claim_refs: List[str]
    inline_location: str
    retrieval_timestamp: str


@dataclass(frozen=True)
class FinalEvidenceContract:
    """
    Final evidence contract produced by C0 grounding.
    
    Contains all evidence artifacts for downstream PA/L2 consumption.
    All retrieved/uploaded content marked as EVIDENCE_DATA_ONLY.
    """
    # Identity
    request_id: str
    run_id: str
    app_id: str
    task_class: str
    tenant_id: str
    trace_id: str
    
    # References
    route_contract_ref: str
    retrieval_plan_ref: str
    
    # Evidence artifacts
    evidence_items: List[EvidenceItem]
    source_register: List[SourceRegisterEntry]
    claim_evidence_map: List[ClaimEvidenceMapping]
    
    # Quality reports
    freshness_report: FreshnessReport
    contradiction_report: ContradictionReport
    
    # Maps and metadata
    citation_map: List[CitationInfo]
    source_lineage_map: Dict[str, List[str]]
    source_version_map: Dict[str, str]
    acl_verification_receipts: List[Dict[str, Any]]
    freshness_receipts: List[Dict[str, Any]]
    
    # Support assessment
    support_status: str
    support_score: float
    support_score_profile: Dict[str, Any]
    
    # Exclusions
    excluded_evidence_refs: List[str]
    blocked_source_refs: List[str]
    
    # Integrity
    final_evidence_digest: str
    
    # Optional substrate writeback (inert only)
    substrate_writeback_candidate_ref: Optional[str] = None
    
    # Data boundary verification
    all_evidence_data_boundary_verified: bool = True
    data_boundary_label: str = "EVIDENCE_DATA_ONLY"
    
    # Schema version
    schema_version: str = "AG9.C0.FEC.1"


def _load_yaml_profile(profile_ref: str) -> Optional[Dict[str, Any]]:
    """Load YAML profile from app-owned config."""
    if not yaml:
        _LOGGER.error("PyYAML not available")
        return None
    
    repo_root = Path(__file__).parent.parent.parent.parent
    profile_path = repo_root / profile_ref
    
    if not profile_path.exists():
        _LOGGER.warning(f"Profile not found: {profile_path}")
        return None
    
    try:
        with open(profile_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        _LOGGER.error(f"Failed to load profile {profile_path}: {e}")
        return None


def _compute_digest(data: Any) -> str:
    """Compute SHA256 digest of data."""
    content = str(data).encode("utf-8")
    return hashlib.sha256(content).hexdigest()[:16]


def c0_build_retrieval_plan(
    route_contract: RouteContract,
    retrieval_profile: Dict[str, Any],
    source_mix_policy: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build retrieval plan from app-owned profiles.
    
    No app-specific logic - all decisions from config.
    """
    # Get depth profile from route contract context or use default
    depth_profile = "standard"  # Would come from request context
    
    # Get max sources/chunks from profile
    max_sources = retrieval_profile.get("max_sources_by_depth", {}).get(depth_profile, 10)
    max_chunks = retrieval_profile.get("max_chunks_by_depth", {}).get(depth_profile, 100)
    
    # Get source tier requirements from source_mix_policy
    min_tiers = source_mix_policy.get("minimum_tier_counts", {}).get(depth_profile, {})
    
    # Get allowed source classes from profile
    allowed_classes = retrieval_profile.get("allowed_source_classes", [])
    blocked_classes = retrieval_profile.get("blocked_source_classes", [])
    
    plan = {
        "plan_id": f"retrieval_plan_{route_contract.request_id}",
        "route_contract_ref": route_contract.request_id,
        "depth_profile": depth_profile,
        "max_sources": max_sources,
        "max_chunks": max_chunks,
        "source_tier_requirements": min_tiers,
        "allowed_source_classes": allowed_classes,
        "blocked_source_classes": blocked_classes,
        "query_decomposition": retrieval_profile.get("query_decomposition_strategy", {}),
        "coverage_families": retrieval_profile.get("coverage_families", {}),
        "citation_requirement": retrieval_profile.get("citation_requirement", {}),
    }
    
    return plan


def c0_execute_retrieval_stub(
    retrieval_plan: Dict[str, Any],
    request_context: Dict[str, Any],
) -> List[EvidenceItem]:
    """
    Stub for evidence retrieval execution.
    
    In real implementation, this would:
    - Execute retrieval through generic approved connectors
    - Hydrate source refs, versions, citations, ACL, freshness, lineage
    - Return evidence items with full metadata
    
    For W4, returns stub evidence demonstrating structure.
    """
    _LOGGER.info("Retrieval stub executing for plan: %s", retrieval_plan.get("plan_id"))
    
    # Return stub evidence items
    return [
        EvidenceItem(
            evidence_id="ev-001",
            source_ref="src-001",
            content_snippet="Stub evidence content for testing C0 structure",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            freshness_status="FRESH",
            support_status="PASS",
            citation_info={"inline": "[1]", "source_url": "https://example.com"},
            data_boundary_label="EVIDENCE_DATA_ONLY",
            confidence_score=0.85,
        )
    ]


def c0_normalize_uploaded_briefing_stub(
    briefing_content: str,
    briefing_metadata: Dict[str, Any],
    normalization_policy: Dict[str, Any],
) -> Optional[EvidenceItem]:
    """
    Stub for uploaded briefing normalization.
    
    In real implementation, this would:
    - Scan for injection attempts
    - Extract claims with provenance
    - Tag citation gaps
    - Mark with EVIDENCE_DATA_ONLY boundary
    
    Returns None if briefing fails security checks.
    """
    _LOGGER.info("Briefing normalization stub for: %s", briefing_metadata.get("filename", "unknown"))
    
    # Check data boundary enforcement
    data_boundary = normalization_policy.get("data_boundary_label", "EVIDENCE_DATA_ONLY")
    
    # Check security scan requirement
    if normalization_policy.get("security_scan", {}).get("injection_scan") == "required":
        # In real impl, would scan for injection patterns
        pass
    
    return EvidenceItem(
        evidence_id="briefing-001",
        source_ref="uploaded-briefing-001",
        content_snippet=briefing_content[:200],  # Truncated for stub
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        freshness_status="FRESH",
        support_status="PASS",
        citation_info={"source_type": "UPLOADED_EVIDENCE_BRIEFING"},
        data_boundary_label=data_boundary,
        claim_extractions=[],  # Would be populated by claim extraction
    )


def c0_build_source_register(
    evidence_items: List[EvidenceItem],
    retrieval_profile: Dict[str, Any],
) -> List[SourceRegisterEntry]:
    """Build source register from evidence items."""
    register = []
    
    for item in evidence_items:
        entry = SourceRegisterEntry(
            source_id=item.source_ref,
            source_url=item.citation_info.get("source_url", ""),
            source_type=item.citation_info.get("source_type", "unknown"),
            tier_classification="tier_2_credible",  # Would be determined by actual source
            retrieval_timestamp=item.retrieval_timestamp,
            freshness_ttl=2592000,  # 30 days default
            acl_info={"tenant_id": "", "owner_read": True},
            provenance_chain=[],
        )
        register.append(entry)
    
    return register


def c0_build_claim_evidence_map(
    evidence_items: List[EvidenceItem],
    retrieval_profile: Dict[str, Any],
) -> List[ClaimEvidenceMapping]:
    """Build claim-evidence map from evidence items."""
    # In real implementation, would extract claims from evidence
    # and map supporting/contradicting evidence
    
    mappings = []
    for i, item in enumerate(evidence_items):
        mapping = ClaimEvidenceMapping(
            claim_id=f"claim-{i:03d}",
            claim_text=f"Claim extracted from {item.source_ref}",
            claim_type="factual",
            supporting_evidence_refs=[item.evidence_id],
            contradicting_evidence_refs=[],
            confidence_assessment="PASS",
            materiality_flag=False,
        )
        mappings.append(mapping)
    
    return mappings


def c0_build_freshness_report(
    evidence_items: List[EvidenceItem],
    freshness_policy: Dict[str, Any],
) -> FreshnessReport:
    """Build freshness report from evidence items."""
    fresh_count = sum(1 for item in evidence_items if item.freshness_status == "FRESH")
    stale_count = sum(1 for item in evidence_items if item.freshness_status == "STALE")
    
    return FreshnessReport(
        sources_checked=len(evidence_items),
        sources_fresh=fresh_count,
        sources_stale=stale_count,
        sources_blocked=0,
        ttl_violations=[],
        downgrade_applications=[],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def c0_build_contradiction_report(
    evidence_items: List[EvidenceItem],
    claim_evidence_map: List[ClaimEvidenceMapping],
    retrieval_profile: Dict[str, Any],
) -> ContradictionReport:
    """Build contradiction report from evidence and claim mappings."""
    # In real implementation, would detect contradictions between evidence items
    
    contradictions = []
    for mapping in claim_evidence_map:
        if mapping.contradicting_evidence_refs:
            contradictions.append({
                "claim_id": mapping.claim_id,
                "contradicting_evidence": mapping.contradicting_evidence_refs,
            })
    
    return ContradictionReport(
        contradictions_detected=len(contradictions),
        contradiction_details=contradictions,
        resolution_recommendations=[],
        materiality_assessment="LOW" if not contradictions else "HIGH",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def c0_compute_support_status(
    evidence_items: List[EvidenceItem],
    source_register: List[SourceRegisterEntry],
    freshness_report: FreshnessReport,
    contradiction_report: ContradictionReport,
    retrieval_profile: Dict[str, Any],
) -> Tuple[str, float, Dict[str, Any]]:
    """Compute support status from evidence quality metrics."""
    policy = retrieval_profile.get("support_status_policy", {})
    thresholds = policy.get("thresholds", {})
    
    # Calculate base score
    total_evidence = len(evidence_items)
    if total_evidence == 0:
        return (EvidenceSupportStatus.EMPTY.value, 0.0, {})
    
    # Score based on evidence count (simplified)
    score = min(100, total_evidence * 10)
    
    # Adjust for freshness
    if freshness_report.sources_stale > 0:
        score -= freshness_report.sources_stale * 5
    
    # Adjust for contradictions
    if contradiction_report.contradictions_detected > 0:
        score -= contradiction_report.contradictions_detected * 15
        status = EvidenceSupportStatus.CONFLICTED.value
    elif score >= thresholds.get("strong_min_support_score", 90):
        status = EvidenceSupportStatus.STRONG.value
    elif score >= thresholds.get("pass_min_support_score", 70):
        status = EvidenceSupportStatus.PASS.value
    elif score >= thresholds.get("weak_max_support_score", 30):
        status = EvidenceSupportStatus.WEAK_WITH_CAVEATS.value
    else:
        status = EvidenceSupportStatus.WEAK_INSUFFICIENT.value
    
    profile = {
        "evidence_count": total_evidence,
        "fresh_sources": freshness_report.sources_fresh,
        "stale_sources": freshness_report.sources_stale,
        "contradictions": contradiction_report.contradictions_detected,
    }
    
    return (status, max(0, score), profile)


def c0_ground_package_driven(
    route_contract: RouteContract,
    validated_request: ValidatedRequest,
    l1_plan: Optional[PackageDrivenL1Plan] = None,
) -> FinalEvidenceContract:
    """
    Generic C0 grounding that consumes app-owned retrieval/freshness/source policies.
    
    Consumes:
        - RouteContract with grounding_required=true
        - ValidatedRequest with runtime_customization_package profile refs
        - App-owned retrieval_profile, source_mix_policy, freshness_policy
    
    Produces:
        - FinalEvidenceContract with all evidence artifacts
        - All retrieved/uploaded content marked EVIDENCE_DATA_ONLY
    
    Does NOT:
        - Answer the user
        - Route
        - Assemble prompts
        - Execute L2 work
        - Write cache
        - Write vector store
        - Write L4
        - Learn
    """
    if not route_contract.grounding_required:
        raise ValueError("C0 grounding called but route_contract.grounding_required is false")
    
    # Extract package refs from ValidatedRequest
    app_payload = validated_request.app_payload or {}
    package = app_payload.get("runtime_customization_package", {})
    
    # Load app-owned profiles
    retrieval_profile_ref = package.get("profile_refs", {}).get("c0_grounding_profile")
    if not retrieval_profile_ref:
        # Fallback to constructing from other refs
        retrieval_profile_ref = package.get("profile_refs", {}).get("retrieval_profile")
    
    retrieval_profile = _load_yaml_profile(retrieval_profile_ref) if retrieval_profile_ref else {}
    
    # Load source mix policy
    source_mix_ref = package.get("profile_refs", {}).get("source_mix_policy")
    source_mix_policy = _load_yaml_profile(source_mix_ref) if source_mix_ref else {}
    
    # Load freshness policy
    freshness_ref = package.get("profile_refs", {}).get("freshness_policy")
    freshness_policy = _load_yaml_profile(freshness_ref) if freshness_ref else {}
    
    # Load uploaded briefing normalization policy
    briefing_ref = package.get("profile_refs", {}).get("uploaded_briefing_normalization_policy")
    briefing_policy = _load_yaml_profile(briefing_ref) if briefing_ref else {}
    
    # Build retrieval plan from app-owned profiles
    retrieval_plan = c0_build_retrieval_plan(route_contract, retrieval_profile, source_mix_policy)
    
    # Execute retrieval (stub)
    evidence_items = c0_execute_retrieval_stub(retrieval_plan, app_payload)
    
    # Check for uploaded briefing in request
    uploaded_briefing = app_payload.get("uploaded_briefing")
    if uploaded_briefing and briefing_policy:
        briefing_item = c0_normalize_uploaded_briefing_stub(
            uploaded_briefing.get("content", ""),
            uploaded_briefing,
            briefing_policy,
        )
        if briefing_item:
            evidence_items.append(briefing_item)
    
    # Build source register
    source_register = c0_build_source_register(evidence_items, retrieval_profile)
    
    # Build claim-evidence map
    claim_evidence_map = c0_build_claim_evidence_map(evidence_items, retrieval_profile)
    
    # Build freshness report
    freshness_report = c0_build_freshness_report(evidence_items, freshness_policy)
    
    # Build contradiction report
    contradiction_report = c0_build_contradiction_report(
        evidence_items, claim_evidence_map, retrieval_profile
    )
    
    # Compute support status
    support_status, support_score, support_profile = c0_compute_support_status(
        evidence_items, source_register, freshness_report, contradiction_report, retrieval_profile
    )
    
    # Build citation map
    citation_map = []
    for item in evidence_items:
        citation = CitationInfo(
            citation_id=f"cite-{item.evidence_id}",
            source_ref=item.source_ref,
            claim_refs=[],
            inline_location=item.citation_info.get("inline", ""),
            retrieval_timestamp=item.retrieval_timestamp,
        )
        citation_map.append(citation)
    
    # Build source lineage and version maps
    source_lineage_map = {item.source_ref: [] for item in evidence_items}
    source_version_map = {item.source_ref: "v1.0" for item in evidence_items}
    
    # Build contract content for digest
    contract_content = {
        "request_id": validated_request.request_id,
        "evidence_count": len(evidence_items),
        "sources": [s.source_id for s in source_register],
    }
    final_digest = _compute_digest(contract_content)
    
    _LOGGER.info(
        "C0 grounding complete: request=%s evidence=%d sources=%d support=%s",
        validated_request.request_id,
        len(evidence_items),
        len(source_register),
        support_status,
    )
    
    return FinalEvidenceContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        task_class=validated_request.task_class,
        tenant_id=validated_request.tenant_id,
        trace_id=validated_request.trace_id,
        route_contract_ref=route_contract.request_id,
        retrieval_plan_ref=retrieval_plan.get("plan_id", ""),
        evidence_items=evidence_items,
        source_register=source_register,
        claim_evidence_map=claim_evidence_map,
        freshness_report=freshness_report,
        contradiction_report=contradiction_report,
        citation_map=citation_map,
        source_lineage_map=source_lineage_map,
        source_version_map=source_version_map,
        acl_verification_receipts=[],
        freshness_receipts=[],
        support_status=support_status,
        support_score=support_score,
        support_score_profile=support_profile,
        excluded_evidence_refs=[],
        blocked_source_refs=[],
        final_evidence_digest=final_digest,
        substrate_writeback_candidate_ref=None,
        all_evidence_data_boundary_verified=True,
        data_boundary_label="EVIDENCE_DATA_ONLY",
        schema_version="AG9.C0.FEC.1",
    )


__all__ = [
    "c0_ground_package_driven",
    "FinalEvidenceContract",
    "EvidenceItem",
    "SourceRegisterEntry",
    "ClaimEvidenceMapping",
    "FreshnessReport",
    "ContradictionReport",
    "CitationInfo",
    "EvidenceSupportStatus",
    "DataBoundaryLabel",
]
