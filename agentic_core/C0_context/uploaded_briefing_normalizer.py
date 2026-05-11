"""W12 — Uploaded Briefing Normalizer (C0)

Normalizes uploaded briefings into research substrate.
Runs provenance check, ACL check, injection scan.
"""
from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agentic_core.runtime.delegation import BriefingNormalizationResult


@dataclass(frozen=True)
class BriefingValidationPolicy:
    """Policy for briefing validation."""
    require_provenance_check: bool = True
    require_acl_check: bool = True
    require_injection_scan: bool = True
    require_citation_check: bool = True
    max_briefing_size_mb: int = 10


class UploadedBriefingNormalizer:
    """Normalizes uploaded briefings into research substrate.
    
    Core owns normalization logic. Apps provide validation policy config.
    """
    
    def __init__(self, policy: BriefingValidationPolicy):
        """Initialize with validation policy."""
        self._policy = policy
    
    def normalize_briefing(
        self,
        briefing_id: str,
        briefing_content: Dict[str, Any],
        source_app_id: str
    ) -> BriefingNormalizationResult:
        """Normalize uploaded briefing into research substrate.
        
        Args:
            briefing_id: Unique briefing identifier
            briefing_content: Briefing content to normalize
            source_app_id: App that uploaded the briefing (apps_rg/apps_lic)
            
        Returns:
            BriefingNormalizationResult with normalization outcome
        """
        errors = []
        
        # Step 1: Provenance check
        provenance_passed = True
        if self._policy.require_provenance_check:
            provenance_passed = self._check_provenance(briefing_content)
            if not provenance_passed:
                errors.append("Provenance check failed")
        
        # Step 2: ACL check
        acl_passed = True
        if self._policy.require_acl_check:
            acl_passed = self._check_acl(briefing_content)
            if not acl_passed:
                errors.append("ACL check failed")
        
        # Step 3: Injection scan
        injection_passed = True
        if self._policy.require_injection_scan:
            injection_passed = self._scan_for_injection(briefing_content)
            if not injection_passed:
                errors.append("Injection scan failed - potential prompt injection detected")
        
        # Step 4: Citation gap check
        citation_gaps = []
        if self._policy.require_citation_check:
            citation_gaps = self._check_citation_gaps(briefing_content)
        
        # Determine normalization success
        normalized = provenance_passed and acl_passed and injection_passed
        
        return BriefingNormalizationResult(
            briefing_id=briefing_id,
            normalized=normalized,
            research_substrate_ref=f"substrate://{briefing_id}" if normalized else "",
            provenance_check_passed=provenance_passed,
            acl_check_passed=acl_passed,
            injection_scan_passed=injection_passed,
            citation_gaps_tagged=citation_gaps,
            data_boundary_label="EVIDENCE_DATA_ONLY",
            errors=errors,
        )
    
    def _check_provenance(self, briefing_content: Dict[str, Any]) -> bool:
        """Check briefing provenance."""
        # Verify briefing has source attribution
        sources = briefing_content.get("sources", [])
        
        if not sources:
            return False
        
        # Verify each source has required fields
        for source in sources:
            if not source.get("url") and not source.get("document_id"):
                return False
        
        return True
    
    def _check_acl(self, briefing_content: Dict[str, Any]) -> bool:
        """Check ACL permissions."""
        # Verify briefing has proper access controls
        acl = briefing_content.get("acl", {})
        
        # Check if public or has explicit permissions
        if acl.get("public", False):
            return True
        
        # Check explicit permissions exist
        permissions = acl.get("permissions", [])
        return len(permissions) > 0
    
    def _scan_for_injection(self, briefing_content: Dict[str, Any]) -> bool:
        """Scan for prompt injection patterns."""
        text = briefing_content.get("text", "")
        
        # Injection patterns to detect
        injection_patterns = [
            "ignore previous instructions",
            "disregard all prior commands",
            "system prompt",
            "you are now",
            "new role",
            "DAN mode",
            "jailbreak",
        ]
        
        text_lower = text.lower()
        
        for pattern in injection_patterns:
            if pattern in text_lower:
                return False  # Injection detected
        
        return True  # No injection detected
    
    def _check_citation_gaps(self, briefing_content: Dict[str, Any]) -> List[str]:
        """Check for citation gaps in briefing."""
        gaps = []
        
        claims = briefing_content.get("claims", [])
        
        for i, claim in enumerate(claims):
            if not claim.get("sources"):
                gaps.append(f"claim_{i}_no_sources")
            elif len(claim.get("sources", [])) < 2:
                gaps.append(f"claim_{i}_insufficient_sources")
        
        return gaps
    
    def validate_as_evidence(
        self,
        briefing_result: BriefingNormalizationResult
    ) -> bool:
        """Validate normalized briefing is suitable as evidence.
        
        Args:
            briefing_result: Normalization result to validate
            
        Returns:
            True if valid as evidence
        """
        if not briefing_result.normalized:
            return False
        
        if not briefing_result.data_boundary_label == "EVIDENCE_DATA_ONLY":
            return False
        
        if not briefing_result.provenance_check_passed:
            return False
        
        if not briefing_result.injection_scan_passed:
            return False
        
        return True


# Default normalizer instance
default_normalizer = UploadedBriefingNormalizer(BriefingValidationPolicy())
