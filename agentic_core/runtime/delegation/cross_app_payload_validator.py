"""W12 — Cross-App Payload Validator

Validates cross-app payloads for compliance with delegation policy.
"""
from typing import Any, Dict, List
from dataclasses import dataclass

from agentic_core.runtime.delegation import (
    CrossAppPayload,
    DelegationContext,
    ReuseEligibility,
    CrossAppReuseValidation,
)


@dataclass(frozen=True)
class ValidationPolicy:
    """Policy for payload validation."""
    require_jd_hash_for_apps_rg: bool = True
    require_role_context_hash_for_apps_lic: bool = True
    max_substrate_age_hours: int = 168  # 7 days
    require_tenant_match: bool = True
    require_session_boundary: bool = True


class CrossAppPayloadValidator:
    """Validates cross-app payloads for policy compliance.
    
    Core owns validation logic. Apps provide validation policy config.
    """
    
    def __init__(self, policy: ValidationPolicy):
        """Initialize with validation policy."""
        self._policy = policy
    
    def validate_payload(
        self,
        payload: CrossAppPayload
    ) -> List[str]:
        """Validate cross-app payload.
        
        Args:
            payload: Cross-app payload to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        context = payload.delegation_context
        
        # Validate caller_app_id
        if not context.caller_app_id:
            errors.append("caller_app_id required")
        
        # Validate based on caller app type
        if context.caller_app_id == "apps_rg":
            errors.extend(self._validate_apps_rg_payload(context))
        
        if context.caller_app_id == "apps_lic":
            errors.extend(self._validate_apps_lic_payload(context))
        
        # Validate tenant boundary
        if self._policy.require_tenant_match:
            if not context.tenant_id:
                errors.append("tenant_id required for tenant boundary enforcement")
        
        # Validate session boundary
        if self._policy.require_session_boundary:
            if not context.session_id:
                errors.append("session_id required for session boundary")
        
        # Validate task class
        if context.task_class != "research_substrate":
            errors.append(f"Unsupported task_class: {context.task_class}")
        
        # Validate delegation type
        if context.delegation_type.name not in ["RESEARCH_SUBSTRATE", "UPLOADED_BRIEFING"]:
            errors.append(f"Unsupported delegation type: {context.delegation_type}")
        
        return errors
    
    def _validate_apps_rg_payload(
        self,
        context: DelegationContext
    ) -> List[str]:
        """Validate apps_rg specific requirements."""
        errors = []
        
        # apps_rg requires jd_content_hash when JD context exists
        if self._policy.require_jd_hash_for_apps_rg:
            # In real implementation, detect if JD context exists
            # For now, check if hash is present (simplified)
            if not context.jd_content_hash:
                errors.append(
                    "apps_rg delegation requires jd_content_hash when JD context present"
                )
        
        return errors
    
    def _validate_apps_lic_payload(
        self,
        context: DelegationContext
    ) -> List[str]:
        """Validate apps_lic specific requirements."""
        errors = []
        
        # apps_lic requires role_context_hash when role context exists
        if self._policy.require_role_context_hash_for_apps_lic:
            # In real implementation, detect if role context exists
            # For now, check if hash is present (simplified)
            if not context.role_context_hash:
                errors.append(
                    "apps_lic delegation requires role_context_hash when role context present"
                )
        
        return errors
    
    def validate_reuse(
        self,
        substrate: Dict[str, Any],
        requesting_app_id: str,
        requesting_context: Dict[str, Any]
    ) -> CrossAppReuseValidation:
        """Validate if substrate can be reused by requesting app.
        
        Args:
            substrate: Existing research substrate
            requesting_app_id: App requesting reuse
            requesting_context: Context for reuse request
            
        Returns:
            CrossAppReuseValidation with eligibility
        """
        substrate_id = substrate.get("substrate_id", "unknown")
        substrate_tenant = substrate.get("tenant_id", "")
        substrate_jd_hash = substrate.get("jd_content_hash", "")
        substrate_role_hash = substrate.get("role_context_hash", "")
        substrate_age_hours = substrate.get("age_hours", 0)
        
        request_tenant = requesting_context.get("tenant_id", "")
        request_jd_hash = requesting_context.get("jd_content_hash", "")
        request_role_hash = requesting_context.get("role_context_hash", "")
        
        # Check tenant mismatch
        if substrate_tenant != request_tenant:
            return CrossAppReuseValidation(
                substrate_id=substrate_id,
                requesting_app_id=requesting_app_id,
                eligible=False,
                eligibility=ReuseEligibility.TENANT_MISMATCH,
                tenant_mismatch=True,
            )
        
        # Check JD hash mismatch (for apps_rg)
        if requesting_app_id == "apps_rg":
            if substrate_jd_hash and substrate_jd_hash != request_jd_hash:
                return CrossAppReuseValidation(
                    substrate_id=substrate_id,
                    requesting_app_id=requesting_app_id,
                    eligible=False,
                    eligibility=ReuseEligibility.JD_HASH_MISMATCH,
                    jd_hash_mismatch=True,
                )
        
        # Check role context mismatch (for apps_lic)
        if requesting_app_id == "apps_lic":
            if substrate_role_hash and substrate_role_hash != request_role_hash:
                return CrossAppReuseValidation(
                    substrate_id=substrate_id,
                    requesting_app_id=requesting_app_id,
                    eligible=False,
                    eligibility=ReuseEligibility.ROLE_CONTEXT_MISMATCH,
                    role_context_mismatch=True,
                )
        
        # Check staleness
        if substrate_age_hours > self._policy.max_substrate_age_hours:
            return CrossAppReuseValidation(
                substrate_id=substrate_id,
                requesting_app_id=requesting_app_id,
                eligible=False,
                eligibility=ReuseEligibility.STALE,
                staleness_hours=substrate_age_hours,
            )
        
        # All checks passed
        return CrossAppReuseValidation(
            substrate_id=substrate_id,
            requesting_app_id=requesting_app_id,
            eligible=True,
            eligibility=ReuseEligibility.ELIGIBLE,
        )
    
    def validate_not_terminal_cache(
        self,
        output_payload: Dict[str, Any]
    ) -> bool:
        """Validate that output is not being cached as terminal answer.
        
        Args:
            output_payload: Output to validate
            
        Returns:
            True if valid (not terminal cache), False if prohibited
        """
        output_type = output_payload.get("output_type", "")
        
        # Prohibited terminal cache types
        prohibited_types = {
            "apps_rg_final_resume_bullets_terminal_cache",
            "apps_rg_final_resume_sections_terminal_cache",
            "apps_lic_final_outreach_copy_terminal_cache",
            "apps_lic_campaign_copy_terminal_cache",
            "customized_user_specific_final_narrative_terminal_cache",
        }
        
        if output_type in prohibited_types:
            return False
        
        # Check for data boundary label
        data_boundary = output_payload.get("data_boundary_label", "")
        if data_boundary == "EVIDENCE_DATA_ONLY":
            return True  # Evidence data is fine
        
        return True


default_validator = CrossAppPayloadValidator(ValidationPolicy())
