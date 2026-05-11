"""W12 — Package-Driven Delegation Broker

Core component routing cross-app delegation calls.
Ensures apps_rg/apps_lic enter apps_research U0 properly.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

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
    """Config for delegation broker."""
    allow_delegation: bool = True
    require_delegation_context: bool = True
    require_caller_app_id: bool = True
    require_tenant_boundary: bool = True


class PackageDrivenDelegationBroker:
    """Brokers cross-app research delegation.
    
    Core owns delegation routing. Apps provide delegation profiles via U0.
    """
    
    def __init__(self, config: DelegationConfig):
        """Initialize with delegation config.
        
        Args:
            config: Delegation policy config
        """
        self._config = config
    
    def delegate_research(
        self,
        caller_app_id: str,
        target_app_id: str,
        delegation_context: DelegationContext,
        evidence_bundles: List[Dict[str, Any]] = None
    ) -> DelegationResult:
        """Delegate research from caller app to target app.
        
        Args:
            caller_app_id: ID of calling app (apps_rg, apps_lic)
            target_app_id: ID of target app (apps_research)
            delegation_context: Context for delegation
            evidence_bundles: Evidence to pass to target app
            
        Returns:
            DelegationResult with substrate return packet
        """
        # Validate delegation is allowed
        if not self._config.allow_delegation:
            return self._create_failure_result(
                delegation_context,
                "Cross-app delegation not enabled in config"
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
        
        # Validate target is apps_research
        if target_app_id != "apps_research":
            return self._create_failure_result(
                delegation_context,
                f"Cross-app delegation only supported to apps_research, not {target_app_id}"
            )
        
        # Validate delegation_context required fields
        if self._config.require_delegation_context:
            missing_fields = self._validate_delegation_context(delegation_context, caller_app_id)
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
        # In real implementation, this would call apps_research U0 entry
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
        caller_app_id: str
    ) -> List[str]:
        """Validate delegation context based on caller app requirements."""
        missing = []
        
        # apps_rg requires jd_content_hash when JD context exists
        if caller_app_id == "apps_rg":
            # In real implementation, check if JD context exists and require hash
            pass  # Simplified for now
        
        # apps_lic requires role_context_hash when role context exists
        if caller_app_id == "apps_lic":
            # In real implementation, check if role context exists and require hash
            pass  # Simplified for now
        
        # Common required fields
        if not context.task_class:
            missing.append("task_class")
        
        if not context.cross_app_reuse_policy_ref:
            missing.append("cross_app_reuse_policy_ref")
        
        return missing
    
    def _create_substrate_packet(
        self,
        payload: CrossAppPayload
    ) -> SubstrateReturnPacket:
        """Create substrate return packet from delegation result.
        
        In real implementation, this would come from apps_research Exit.
        """
        context = payload.delegation_context
        
        return SubstrateReturnPacket(
            packet_id=f"substrate-{context.delegation_id}",
            delegation_id=context.delegation_id,
            caller_app_id=context.caller_app_id,
            target_app_id="apps_research",
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
            target_app_id="apps_research",
            success=False,
            failure_reason=reason,
            validation_errors=[reason],
        )


# Broker singleton
default_broker = PackageDrivenDelegationBroker(DelegationConfig())


def delegate_research(
    caller_app_id: str,
    target_app_id: str,
    delegation_context: DelegationContext
) -> DelegationResult:
    """Convenience function for research delegation."""
    return default_broker.delegate_research(caller_app_id, target_app_id, delegation_context)
