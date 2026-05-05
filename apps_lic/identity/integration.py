"""Identity Integration Wiring for apps_lic — Multi-Touch Spine Integration.

Wave 5, Phase 3 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides the integration layer between identity propagation,
coordination fabric, and touch state, completing the cross-touch
identity propagation infrastructure.

App: apps_lic
Layer: Integration (apps_lic/identity/)

Dependencies:
    - Identity Propagation (apps_lic/identity/propagation.py)
    - Context Carry-Forward (apps_lic/identity/carry_forward.py)
    - Touch Scheduler (apps_lic/coordination/touch_scheduler.py)
    - Touch State Integration (apps_lic/coordination/touch_state_integration.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

from apps_lic.identity.propagation import (
    IdentityPropagationService,
    IdentityContext,
    RecipientIdentity,
)
from apps_lic.identity.carry_forward import (
    ContextCarryForwardBridge,
    CarryForwardRequest,
)


# -----------------------------------------------------------------------------
# Integration Configuration
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class IdentityIntegrationConfig:
    """Configuration for identity integration."""
    
    # Hashing configuration
    default_identity_type: str = "email"
    use_random_salt: bool = True
    
    # Context propagation
    max_signals_per_context: int = 50
    max_response_history: int = 10
    
    # Coordination fabric
    sync_with_scheduler: bool = True
    sync_with_state: bool = True


# -----------------------------------------------------------------------------
# Integration Manager
# -----------------------------------------------------------------------------

class IdentityIntegrationManager:
    """Manager for identity integration across apps_lic components.
    
    This class provides the unified interface for:
    - Identity registration and resolution
    - Context propagation
    - Coordination fabric integration
    - Touch state synchronization
    
    Parameters
    ----------
    identity_service : IdentityPropagationService
        Identity propagation service
    carry_forward_bridge : ContextCarryForwardBridge
        Context carry-forward bridge
    config : IdentityIntegrationConfig
        Integration configuration
    """
    
    def __init__(
        self,
        identity_service: IdentityPropagationService,
        carry_forward_bridge: ContextCarryForwardBridge,
        config: Optional[IdentityIntegrationConfig] = None,
    ):
        self._identity = identity_service
        self._bridge = carry_forward_bridge
        self._config = config or IdentityIntegrationConfig()
    
    # -------------------------------------------------------------------------
    # Identity Management
    # -------------------------------------------------------------------------
    
    def register_recipient(
        self,
        raw_identifier: str,
        identity_type: Optional[str] = None,
    ) -> RecipientIdentity:
        """Register a new recipient.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier (email, LinkedIn URL, etc.)
        identity_type : Optional[str]
            Type of identifier. Uses config default if None.
        
        Returns
        -------
        RecipientIdentity
            Created identity
        """
        return self._identity.register_identity(
            raw_identifier=raw_identifier,
            identity_type=identity_type or self._config.default_identity_type,
        )
    
    def resolve_recipient(
        self,
        raw_identifier: str,
    ) -> Optional[RecipientIdentity]:
        """Resolve raw identifier to identity.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier to resolve
        
        Returns
        -------
        Optional[RecipientIdentity]
            Resolved identity if found
        """
        return self._identity.resolve_identity(raw_identifier)
    
    # -------------------------------------------------------------------------
    # Context Management
    # -------------------------------------------------------------------------
    
    def create_touch_context(
        self,
        identity: RecipientIdentity,
        campaign_id: str,
        touch_sequence: int,
        initial_context: Optional[dict] = None,
    ) -> IdentityContext:
        """Create context for a touch.
        
        Parameters
        ----------
        identity : RecipientIdentity
            Recipient identity
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Position in sequence
        initial_context : Optional[dict]
            Initial context data
        
        Returns
        -------
        IdentityContext
            Created context
        """
        return self._identity.create_context(
            identity=identity,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            initial_context=initial_context,
        )
    
    def propagate_to_next_touch(
        self,
        identity_hash: str,
        campaign_id: str,
        prior_touch_id: str,
        next_touch_id: str,
        prior_sequence: int,
        next_sequence: int,
        new_signals: Optional[list] = None,
    ) -> dict[str, Any]:
        """Propagate context from prior touch to next touch.
        
        This is the main integration method called during sequence
        progression.
        
        Parameters
        ----------
        identity_hash : str
            Recipient identity hash
        campaign_id : str
            Campaign ID
        prior_touch_id : str
            Source touch ID
        next_touch_id : str
            Target touch ID
        prior_sequence : int
            Source sequence number
        next_sequence : int
            Target sequence number
        new_signals : Optional[list]
            New signals to add
        
        Returns
        -------
        dict
            Propagated context
        """
        request = CarryForwardRequest(
            prior_touch_id=prior_touch_id,
            next_touch_id=next_touch_id,
            campaign_id=campaign_id,
            recipient_hash=identity_hash,
            prior_touch_sequence=prior_sequence,
            next_touch_sequence=next_sequence,
            new_signals=new_signals or [],
        )
        
        result = self._bridge.carry_forward(request)
        
        if result.success:
            return result.context_carried
        
        # Failed - return empty context
        return {}
    
    # -------------------------------------------------------------------------
    # Coordination Integration
    # -------------------------------------------------------------------------
    
    def prepare_scheduling_context(
        self,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        prior_context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Prepare context for coordination fabric scheduling.
        
        Parameters
        ----------
        recipient_hash : str
            Recipient identifier
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Sequence position
        prior_context : Optional[dict]
            Prior context data
        
        Returns
        -------
        dict
            Scheduling context
        """
        return self._bridge.prepare_scheduling_context(
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            prior_context=prior_context,
        )
    
    def extract_wake_context(
        self,
        wake_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract context from wake data.
        
        Parameters
        ----------
        wake_data : dict
            Wake data from coordination fabric
        
        Returns
        -------
        dict
            Extracted context
        """
        return self._bridge.extract_context_from_wake(wake_data)
    
    def update_from_send(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        send_metadata: dict[str, Any],
    ) -> bool:
        """Update context after touch is sent.
        
        Parameters
        ----------
        touch_id : str
            Touch ID
        recipient_hash : str
            Recipient identifier
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Sequence number
        send_metadata : dict
            Send metadata
        
        Returns
        -------
        bool
            True if update succeeded
        """
        return self._bridge.update_context_from_send(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            send_metadata=send_metadata,
        )
    
    def update_from_response(
        self,
        identity_hash: str,
        campaign_id: str,
        touch_sequence: int,
        response_data: dict[str, Any],
    ) -> Optional[IdentityContext]:
        """Update context from recipient response.
        
        Parameters
        ----------
        identity_hash : str
            Recipient identity hash
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Which touch was responded to
        response_data : dict
            Response data
        
        Returns
        -------
        Optional[IdentityContext]
            Updated context
        """
        return self._identity.update_context_from_response(
            identity_hash=identity_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            response_data=response_data,
        )


# -----------------------------------------------------------------------------
# Spine Integration
# -----------------------------------------------------------------------------

class IdentitySpineIntegration:
    """Spine integration for identity propagation.
    
    Provides the standard initialization pattern for apps_lic spine.
    """
    
    @staticmethod
    def initialize(
        config: Optional[IdentityIntegrationConfig] = None,
    ) -> dict[str, Any]:
        """Initialize identity integration for apps_lic spine.
        
        This should be called during spine startup, after touch state
        and coordination fabric are initialized.
        
        Parameters
        ----------
        config : Optional[IdentityIntegrationConfig]
            Integration config. Uses defaults if None.
        
        Returns
        -------
        dict[str, Any]
            {
                "status": "success|error",
                "manager": IdentityIntegrationManager|None,
                "error": str|None,
            }
        """
        try:
            from apps_lic.identity.propagation import get_identity_propagation_service
            from apps_lic.identity.carry_forward import ContextCarryForwardBridge
            from agentic_core.L4_state.uwg.durable_write_gateway import get_gateway
            from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter
            
            cfg = config or IdentityIntegrationConfig()
            
            # Create services
            identity_service = get_identity_propagation_service()
            gateway = get_gateway()
            state_adapter = TouchStateUWGAdapter(gateway)
            bridge = ContextCarryForwardBridge(
                identity_service=identity_service,
                state_adapter=state_adapter,
            )
            
            # Create manager
            manager = IdentityIntegrationManager(
                identity_service=identity_service,
                carry_forward_bridge=bridge,
                config=cfg,
            )
            
            return {
                "status": "success",
                "manager": manager,
                "error": None,
            }
        
        except Exception as e:
            return {
                "status": "error",
                "manager": None,
                "error": str(e),
            }
    
    @staticmethod
    def get_manager() -> Optional[IdentityIntegrationManager]:
        """Get the initialized manager (if available).
        
        Returns
        -------
        Optional[IdentityIntegrationManager]
            Manager if initialized, None otherwise
        """
        # In production, this would return a process-global singleton
        # For now, return None (caller should use initialize)
        return None


# -----------------------------------------------------------------------------
# Convenience Entry Point
# -----------------------------------------------------------------------------

def initialize_identity_integration(
    config: Optional[IdentityIntegrationConfig] = None,
) -> Optional[IdentityIntegrationManager]:
    """One-shot initialization of identity integration.
    
    Primary entry point for apps_lic spine initialization.
    
    Parameters
    ----------
    config : Optional[IdentityIntegrationConfig]
        Integration config
    
    Returns
    -------
    Optional[IdentityIntegrationManager]
        Manager if successful, None if failed
    
    Example
    -------
    >>> from apps_lic.identity.integration import initialize_identity_integration
    >>> manager = initialize_identity_integration()
    >>> if manager:
    ...     identity = manager.register_recipient("user@example.com")
    """
    result = IdentitySpineIntegration.initialize(config)
    return result.get("manager")


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "IdentityIntegrationConfig",
    "IdentityIntegrationManager",
    "IdentitySpineIntegration",
    "initialize_identity_integration",
]
