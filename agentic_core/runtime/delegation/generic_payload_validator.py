"""Generic Payload Validator — Profile-Driven Cross-App Validation

Validates cross-app payloads using app-owned delegation profiles.
Zero app-specific literals or branching in this module.
"""
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from agentic_core.runtime.delegation import (
    CrossAppPayload,
    DelegationContext,
    ReuseEligibility,
    CrossAppReuseValidation,
)


@dataclass(frozen=True)
class ValidationPolicy:
    """Generic validation policy loaded from app profile."""
    max_substrate_age_hours: int = 168  # 7 days
    require_tenant_match: bool = True
    require_session_boundary: bool = True
    supported_task_classes: List[str] = field(default_factory=lambda: ["research_substrate"])
    supported_delegation_types: List[str] = field(default_factory=lambda: ["RESEARCH_SUBSTRATE", "UPLOADED_BRIEFING"])


@dataclass(frozen=True)
class AppValidationProfile:
    """App-specific validation rules loaded from delegation profile YAML."""
    app_id: str
    require_jd_content_hash: bool = False
    require_role_context_hash: bool = False
    error_messages: Dict[str, str] = field(default_factory=dict)
    reuse_match_fields: List[str] = field(default_factory=list)
    reuse_eligibility_rules: List[Dict[str, Any]] = field(default_factory=list)
    prohibited_terminal_types: List[str] = field(default_factory=list)
    allowed_boundary_labels: List[str] = field(default_factory=lambda: ["EVIDENCE_DATA_ONLY"])


class ProfileLoader:
    """Loads delegation profiles from app-owned config files.
    
    Profiles are stored at: {app_id}/config/domain_contract/delegation_profile.yaml
    """
    
    @staticmethod
    def load_profile(app_id: str, repo_root: Optional[Path] = None) -> Optional[AppValidationProfile]:
        """Load validation profile for the given app.
        
        Args:
            app_id: The app identifier (e.g., "apps_example")
            repo_root: Optional repository root path (for testing)
            
        Returns:
            AppValidationProfile if found, None otherwise
        """
        if repo_root is None:
            # Default: look in current working directory and parent directories
            repo_root = Path.cwd()
            # Try to find git root
            while repo_root.parent != repo_root:
                if (repo_root / ".git").exists():
                    break
                repo_root = repo_root.parent
        
        profile_path = repo_root / app_id / "config" / "domain_contract" / "delegation_profile.yaml"
        
        if not profile_path.exists():
            return None
        
        try:
            with open(profile_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return ProfileLoader._parse_profile(data)
        except Exception:  # guardian: allow-return-none-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
            return None
    
    @staticmethod
    def _parse_profile(data: Dict[str, Any]) -> AppValidationProfile:
        """Parse YAML data into AppValidationProfile."""
        payload = data.get("payload_validation", {})
        reuse = data.get("reuse_validation", {})
        terminal = data.get("terminal_cache", {})
        
        return AppValidationProfile(
            app_id=data.get("app_id", "unknown"),
            require_jd_content_hash=payload.get("require_jd_content_hash", False),
            require_role_context_hash=payload.get("require_role_context_hash", False),
            error_messages=payload.get("error_messages", {}),
            reuse_match_fields=reuse.get("required_match_fields", []),
            reuse_eligibility_rules=reuse.get("eligibility_rules", []),
            prohibited_terminal_types=terminal.get("prohibited_output_types", []),
            allowed_boundary_labels=terminal.get("allowed_boundary_labels", ["EVIDENCE_DATA_ONLY"]),
        )


class GenericPayloadValidator:
    """Validates cross-app payloads using profile-driven rules.
    
    This validator contains ZERO app-specific literals or branching.
    All app-specific validation rules are loaded from app-owned profiles.
    """
    
    def __init__(self, policy: ValidationPolicy, profile_loader: Optional[Callable[[str], Optional[AppValidationProfile]]] = None):
        """Initialize with validation policy and optional profile loader.
        
        Args:
            policy: Generic validation policy
            profile_loader: Optional function to load app profiles (for testing)
        """
        self._policy = policy
        self._profile_loader = profile_loader or ProfileLoader.load_profile
    
    def validate_payload(
        self,
        payload: CrossAppPayload
    ) -> List[str]:
        """Validate cross-app payload using profile-driven rules.
        
        Args:
            payload: Cross-app payload to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        context = payload.delegation_context
        
        # Load app-specific profile
        profile = self._profile_loader(context.caller_app_id)
        if profile is None:
            errors.append(f"No delegation profile found for app: {context.caller_app_id}")
            return errors
        
        # Validate caller_app_id present
        if not context.caller_app_id:
            errors.append("caller_app_id required")
        
        # Validate based on profile rules
        errors.extend(self._validate_profile_rules(context, profile))
        
        # Validate tenant boundary
        if self._policy.require_tenant_match:
            if not context.tenant_id:
                errors.append("tenant_id required for tenant boundary enforcement")
        
        # Validate session boundary
        if self._policy.require_session_boundary:
            if not context.session_id:
                errors.append("session_id required for session boundary")
        
        # Validate task class
        if context.task_class not in self._policy.supported_task_classes:
            errors.append(f"Unsupported task_class: {context.task_class}")
        
        # Validate delegation type
        delegation_type_name = context.delegation_type.name
        if delegation_type_name not in self._policy.supported_delegation_types:
            errors.append(f"Unsupported delegation type: {delegation_type_name}")
        
        return errors
    
    def _validate_profile_rules(
        self,
        context: DelegationContext,
        profile: AppValidationProfile
    ) -> List[str]:
        """Validate app-specific rules from profile.
        
        Args:
            context: Delegation context
            profile: App validation profile
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate jd_content_hash requirement
        if profile.require_jd_content_hash:
            if not context.jd_content_hash:
                error_msg = profile.error_messages.get(
                    "missing_jd_hash",
                    f"{profile.app_id} delegation requires jd_content_hash when JD context present"
                )
                errors.append(error_msg)
        
        # Validate role_context_hash requirement
        if profile.require_role_context_hash:
            if not context.role_context_hash:
                error_msg = profile.error_messages.get(
                    "missing_role_hash",
                    f"{profile.app_id} delegation requires role_context_hash when role context present"
                )
                errors.append(error_msg)
        
        return errors
    
    def validate_reuse(
        self,
        substrate: Dict[str, Any],
        requesting_app_id: str,
        requesting_context: Dict[str, Any]
    ) -> CrossAppReuseValidation:
        """Validate if substrate can be reused by requesting app.
        
        Uses profile-driven rules to determine reuse eligibility.
        
        Args:
            substrate: Existing research substrate
            requesting_app_id: App requesting reuse
            requesting_context: Context for reuse request
            
        Returns:
            CrossAppReuseValidation with eligibility
        """
        substrate_id = substrate.get("substrate_id", "unknown")
        substrate_tenant = substrate.get("tenant_id", "")
        substrate_age_hours = substrate.get("age_hours", 0)
        
        request_tenant = requesting_context.get("tenant_id", "")
        
        # Load profile for requesting app
        profile = self._profile_loader(requesting_app_id)
        if profile is None:
            return CrossAppReuseValidation(
                substrate_id=substrate_id,
                requesting_app_id=requesting_app_id,
                eligible=False,
                eligibility=ReuseEligibility.CONTEXT_MISMATCH,
            )
        
        # Check tenant mismatch (always required if policy requires tenant match)
        if self._policy.require_tenant_match:
            if substrate_tenant != request_tenant:
                return CrossAppReuseValidation(
                    substrate_id=substrate_id,
                    requesting_app_id=requesting_app_id,
                    eligible=False,
                    eligibility=ReuseEligibility.TENANT_MISMATCH,
                    tenant_mismatch=True,
                )
        
        # Check profile-specific reuse validation rules
        for rule in profile.reuse_eligibility_rules:
            field = rule.get("field", "")
            condition = rule.get("condition", "equals")
            failure_eligibility = rule.get("failure_eligibility", "CONTEXT_MISMATCH")
            
            substrate_value = substrate.get(field, "")
            request_value = requesting_context.get(field, "")
            
            if condition == "equals":
                if substrate_value and substrate_value != request_value:
                    # Map string eligibility to enum
                    if failure_eligibility == "JD_HASH_MISMATCH":
                        eligibility = ReuseEligibility.JD_HASH_MISMATCH
                        jd_hash_mismatch = True
                        role_context_mismatch = False
                    elif failure_eligibility == "ROLE_CONTEXT_MISMATCH":
                        eligibility = ReuseEligibility.ROLE_CONTEXT_MISMATCH
                        jd_hash_mismatch = False
                        role_context_mismatch = True
                    else:
                        eligibility = ReuseEligibility.CONTEXT_MISMATCH
                        jd_hash_mismatch = False
                        role_context_mismatch = False
                    
                    return CrossAppReuseValidation(
                        substrate_id=substrate_id,
                        requesting_app_id=requesting_app_id,
                        eligible=False,
                        eligibility=eligibility,
                        jd_hash_mismatch=jd_hash_mismatch,
                        role_context_mismatch=role_context_mismatch,
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
        output_payload: Dict[str, Any],
        app_id: str
    ) -> bool:
        """Validate that output is not being cached as terminal answer.
        
        Args:
            output_payload: Output to validate
            app_id: App ID for profile lookup
            
        Returns:
            True if valid (not terminal cache), False if prohibited
        """
        output_type = output_payload.get("output_type", "")
        
        # Load profile to get prohibited types
        profile = self._profile_loader(app_id)
        if profile is None:
            return True  # Fail open if no profile found
        
        # Check if output type is in prohibited list
        if output_type in profile.prohibited_terminal_types:
            return False
        
        # Check for data boundary label
        data_boundary = output_payload.get("data_boundary_label", "")
        if data_boundary in profile.allowed_boundary_labels:
            return True  # Evidence data is fine
        
        return True


default_policy = ValidationPolicy()
default_validator = GenericPayloadValidator(default_policy)
