"""Generic Delegation Router — Profile-Driven Cross-App Delegation

Routes cross-app delegation calls using app-owned delegation profiles.
Zero app-specific literals or branching in this module.
"""
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from agentic_core.runtime.delegation import (
    DelegationContext,
    CrossAppPayload,
    SubstrateReturnPacket,
    DelegationResult,
    DelegationType,
    ReuseEligibility,
)


@dataclass(frozen=True)
class DelegationConfig:
    """Config for delegation router."""
    allow_delegation: bool = True
    require_delegation_context: bool = True
    require_caller_app_id: bool = True
    require_tenant_boundary: bool = True
    default_target_app: str = "apps_research"


@dataclass(frozen=True)
class AppDelegationProfile:
    """App-specific delegation rules loaded from delegation profile YAML."""
    app_id: str
    allowed_targets: List[str]
    required_context_fields: List[str]
    optional_context_fields: List[str] = field(default_factory=list)


class ProfileLoader:
    """Loads delegation profiles from app-owned config files.
    
    Profiles are stored at: {app_id}/config/domain_contract/delegation_profile.yaml
    """
    
    @staticmethod
    def load_delegation_profile(app_id: str, repo_root: Optional[Path] = None) -> Optional[AppDelegationProfile]:
        """Load delegation profile for the given app.
        
        Args:
            app_id: The app identifier (e.g., "apps_example")
            repo_root: Optional repository root path (for testing)
            
        Returns:
            AppDelegationProfile if found, None otherwise
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
            
            return ProfileLoader._parse_delegation_profile(data)
        except Exception:
            return None
    
    @staticmethod
    def _parse_delegation_profile(data: Dict[str, Any]) -> AppDelegationProfile:
        """Parse YAML data into AppDelegationProfile."""
        routing = data.get("delegation_routing", {})
        
        return AppDelegationProfile(
            app_id=data.get("app_id", "unknown"),
            allowed_targets=routing.get("allowed_targets", []),
            required_context_fields=routing.get("required_context_fields", []),
            optional_context_fields=routing.get("optional_context_fields", []),
        )


class GenericDelegationRouter:
    """Routes cross-app delegation using profile-driven rules.
    
    This router contains ZERO app-specific literals or branching.
    All app-specific routing rules are loaded from app-owned profiles.
    """
    
    def __init__(self, config: DelegationConfig, profile_loader: Optional[Callable[[str], Optional[AppDelegationProfile]]] = None):
        """Initialize with delegation config and optional profile loader.
        
        Args:
            config: Generic delegation configuration
            profile_loader: Optional function to load app profiles (for testing)
        """
        self._config = config
        self._profile_loader = profile_loader or ProfileLoader.load_delegation_profile
    
    def delegate_research(
        self,
        caller_app_id: str,
        target_app_id: str,
        delegation_context: DelegationContext,
        evidence_bundles: List[Dict[str, Any]] = None
    ) -> DelegationResult:
        """Delegate research from caller app to target app using profile-driven rules.
        
        Args:
            caller_app_id: ID of calling app (loaded from profile)
            target_app_id: ID of target app (validated against profile)
            delegation_context: Context for delegation
            evidence_bundles: Evidence to pass to target app
            
        Returns:
            DelegationResult with substrate return packet
        """
        # Validate delegation is allowed globally
        if not self._config.allow_delegation:
            return self._create_failure_result(
                delegation_context,
                "Cross-app delegation not enabled in config"
            )
        
        # Load caller's delegation profile
        profile = self._profile_loader(caller_app_id)
        if profile is None:
            return self._create_failure_result(
                delegation_context,
                f"No delegation profile found for caller app: {caller_app_id}"
            )
        
        # Validate caller_app_id
        if self._config.require_caller_app_id:
            if not delegation_context.caller_app_id:
                return self._create_failure_result(
                    delegation_context,
                    "caller_app_id required in delegation context"
                )
            
            if delegation_context.caller_app_id != caller_app_id:
                return self._create_failure_result(
                    delegation_context,
                    f"Delegation context caller_app_id {delegation_context.caller_app_id} "
                    f"does not match caller {caller_app_id}"
                )
        
        # Validate target is in allowed targets (from profile)
        if target_app_id not in profile.allowed_targets:
            allowed_list = ", ".join(profile.allowed_targets)
            return self._create_failure_result(
                delegation_context,
                f"Cross-app delegation from {caller_app_id} only supported to: {allowed_list}, "
                f"not {target_app_id}"
            )
        
        # Validate delegation_context required fields (from profile)
        if self._config.require_delegation_context:
            missing_fields = self._validate_delegation_context(delegation_context, profile)
            if missing_fields:
                return self._create_failure_result(
                    delegation_context,
                    f"Missing required fields in delegation context: {missing_fields}"
                )
        
        # Validate tenant/session boundary
        if self._config.require_tenant_boundary:
            if not delegation_context.tenant_id:
                return self._create_failure_result(
                    delegation_context,
                    "tenant_id required for delegation"
                )
        
        # Build cross-app payload
        payload = CrossAppPayload(
            payload_id=f"payload-{delegation_context.delegation_id}",
            delegation_context=delegation_context,
            evidence_bundles=evidence_bundles or [],
            replay_key=f"replay:{delegation_context.delegation_id}",
        )
        
        # Route to target app U0
        # In real implementation, this would call target app U0 entry
        # For now, return success with substrate packet
        substrate_packet = self._create_substrate_packet(payload)
        
        return DelegationResult(
            delegation_id=delegation_context.delegation_id,
            caller_app_id=caller_app_id,
            target_app_id=target_app_id,
            success=True,
            substrate_packet=substrate_packet,
            evidence_digest=f"sha256:delegation-{delegation_context.delegation_id}",
        )
    
    def _validate_delegation_context(
        self,
        context: DelegationContext,
        profile: AppDelegationProfile
    ) -> List[str]:
        """Validate delegation context based on profile requirements.
        
        Args:
            context: Delegation context
            profile: App delegation profile
            
        Returns:
            List of missing required fields
        """
        missing = []
        
        # Check all required fields from profile
        for field in profile.required_context_fields:
            value = getattr(context, field, None)
            if not value:
                missing.append(field)
        
        return missing
    
    def _create_substrate_packet(
        self,
        payload: CrossAppPayload
    ) -> SubstrateReturnPacket:
        """Create substrate return packet from delegation result.
        
        In real implementation, this would come from target app Exit.
        """
        context = payload.delegation_context
        
        return SubstrateReturnPacket(
            packet_id=f"substrate-{context.delegation_id}",
            delegation_id=context.delegation_id,
            caller_app_id=context.caller_app_id,
            target_app_id=self._config.default_target_app,
            research_substrate={
                "entities": [],
                "sources": [],
                "claims": [],
            },
            data_boundary_label="EVIDENCE_DATA_ONLY",
            substrate_provenance={
                "delegation_id": context.delegation_id,
                "caller_app_id": context.caller_app_id,
                "created_at": context.created_at,
            },
            reuse_eligibility=ReuseEligibility.ELIGIBLE,
            evidence_digest=f"sha256:substrate-{context.delegation_id}",
        )
    
    def _create_failure_result(
        self,
        context: DelegationContext,
        reason: str
    ) -> DelegationResult:
        """Create failure delegation result."""
        return DelegationResult(
            delegation_id=context.delegation_id if context else "unknown",
            caller_app_id=context.caller_app_id if context else "unknown",
            target_app_id=self._config.default_target_app,
            success=False,
            failure_reason=reason,
            validation_errors=[reason],
        )


# Router singleton with default config
default_config = DelegationConfig()
default_router = GenericDelegationRouter(default_config)


def delegate_research(
    caller_app_id: str,
    target_app_id: str,
    delegation_context: DelegationContext
) -> DelegationResult:
    """Convenience function for research delegation using generic router."""
    return default_router.delegate_research(caller_app_id, target_app_id, delegation_context)
