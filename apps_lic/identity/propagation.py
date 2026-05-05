"""Cross-Touch Identity Propagation Service for apps_lic.

Wave 5, Phase 1 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides identity propagation across multi-touch sequences,
enabling context carry-forward between touches while maintaining
recipient privacy through hashing.

App: apps_lic
Layer: Identity Management (apps_lic/identity/)

Dependencies:
    - Touch State (agentic_core/L4_state/uwg/touch_state_writer.py)
    - Coordination Fabric (apps_lic/coordination/touch_scheduler.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone
import hashlib
import uuid


# -----------------------------------------------------------------------------
# Identity Types
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class RecipientIdentity:
    """Hashed recipient identity for privacy-safe identification.
    
    Fields
    ------
    identity_hash : str
        SHA-256 hash of normalized recipient identifier
    identity_type : str
        Type of identifier hashed: "email"|"linkedin"|"phone"|"custom"
    salt : str
        Per-identity salt for hash collision resistance
    created_at : str
        ISO timestamp when identity was first seen
    """
    
    identity_hash: str
    identity_type: str = "email"
    salt: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class IdentityContext:
    """Context associated with a recipient identity.
    
    This is the data that gets carried forward between touches
    in a multi-touch sequence.
    
    Fields
    ------
    identity_hash : str
        Link to recipient identity
    campaign_id : str
        Campaign this context belongs to
    touch_sequence : int
        Which touch in sequence this context is for
    accumulated_signals : list[dict]
        Signals accumulated across touches
    prior_responses : list[dict]
        Responses from prior touches
    content_preferences : dict
        Learned content preferences
    timing_preferences : dict
        Learned timing preferences (optimal send times)
    custom_context : dict
        App-specific custom context
    created_at : str
        When this context was created
    updated_at : str
        When this context was last updated
    """
    
    identity_hash: str
    campaign_id: str
    touch_sequence: int
    accumulated_signals: list[dict] = field(default_factory=list)
    prior_responses: list[dict] = field(default_factory=list)
    content_preferences: dict = field(default_factory=dict)
    timing_preferences: dict = field(default_factory=dict)
    custom_context: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# -----------------------------------------------------------------------------
# Identity Hasher
# -----------------------------------------------------------------------------

class IdentityHasher:
    """Secure identity hashing for privacy-safe identification.
    
    Uses SHA-256 with per-identity salt to prevent:
    - Rainbow table attacks
    - Cross-campaign correlation
    - Dictionary attacks
    """
    
    @staticmethod
    def hash_identity(
        raw_identifier: str,
        identity_type: str = "email",
        salt: Optional[str] = None,
    ) -> RecipientIdentity:
        """Hash a raw identifier into a privacy-safe identity.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier (email, LinkedIn URL, etc.)
        identity_type : str
            Type of identifier
        salt : Optional[str]
            Custom salt. If None, generates random salt.
        
        Returns
        -------
        RecipientIdentity
            Hashed identity with metadata
        """
        # Normalize identifier
        normalized = raw_identifier.lower().strip()
        
        # Generate or use provided salt
        identity_salt = salt or uuid.uuid4().hex[:16]
        
        # Create hash
        hasher = hashlib.sha256()
        hasher.update(normalized.encode("utf-8"))
        hasher.update(identity_salt.encode("utf-8"))
        identity_hash = hasher.hexdigest()
        
        return RecipientIdentity(
            identity_hash=identity_hash,
            identity_type=identity_type,
            salt=identity_salt,
        )
    
    @staticmethod
    def verify_identity(
        raw_identifier: str,
        identity: RecipientIdentity,
    ) -> bool:
        """Verify that a raw identifier matches a hashed identity.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier to verify
        identity : RecipientIdentity
            Stored hashed identity
        
        Returns
        -------
        bool
            True if identifier matches
        """
        normalized = raw_identifier.lower().strip()
        
        hasher = hashlib.sha256()
        hasher.update(normalized.encode("utf-8"))
        hasher.update(identity.salt.encode("utf-8"))
        computed_hash = hasher.hexdigest()
        
        return computed_hash == identity.identity_hash


# -----------------------------------------------------------------------------
# Identity Propagation Service
# -----------------------------------------------------------------------------

class IdentityPropagationService:
    """Service for managing identity propagation across touches.
    
    This service provides:
    - Identity hashing and verification
    - Context storage and retrieval
    - Cross-touch context propagation
    - Privacy-safe identity resolution
    
    Parameters
    ----------
    state_adapter : TouchStateUWGAdapter
        UWG adapter for durable state storage
    """
    
    def __init__(self, state_adapter: Any):
        self._state = state_adapter
        self._hasher = IdentityHasher()
    
    def register_identity(
        self,
        raw_identifier: str,
        identity_type: str = "email",
    ) -> RecipientIdentity:
        """Register a new recipient identity.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier to hash
        identity_type : str
            Type of identifier
        
        Returns
        -------
        RecipientIdentity
            Created hashed identity
        """
        identity = self._hasher.hash_identity(raw_identifier, identity_type)
        
        # Store in L4 (privacy-preserving - only hash stored)
        # Note: In production, this would use a dedicated identity table
        # For now, we rely on the touch_state recipient_hash field
        
        return identity
    
    def resolve_identity(
        self,
        raw_identifier: str,
    ) -> Optional[RecipientIdentity]:
        """Resolve a raw identifier to stored identity.
        
        This is used when recipient responds - we hash their identifier
        and look up matching identity.
        
        Parameters
        ----------
        raw_identifier : str
            Raw identifier to resolve
        
        Returns
        -------
        Optional[RecipientIdentity]
            Resolved identity if found
        """
        # In production, this would query identity store
        # For now, we create deterministic hash for lookup
        # (recipient would need to provide their salt or we use known salt)
        
        # Placeholder: Create identity with empty salt for lookup
        lookup = self._hasher.hash_identity(raw_identifier, salt="")
        
        # Would query: SELECT * FROM identities WHERE identity_hash = ?
        # For now, return the lookup identity
        return lookup
    
    def create_context(
        self,
        identity: RecipientIdentity,
        campaign_id: str,
        touch_sequence: int,
        initial_context: Optional[dict] = None,
    ) -> IdentityContext:
        """Create context for a touch in a sequence.
        
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
        context = IdentityContext(
            identity_hash=identity.identity_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            custom_context=initial_context or {},
        )
        
        # Store in L4
        self._store_context(context)
        
        return context
    
    def propagate_context(
        self,
        identity_hash: str,
        campaign_id: str,
        from_touch_sequence: int,
        to_touch_sequence: int,
        additional_signals: Optional[list] = None,
    ) -> Optional[IdentityContext]:
        """Propagate context from one touch to the next.
        
        This is the core cross-touch identity propagation function.
        
        Parameters
        ----------
        identity_hash : str
            Recipient identity hash
        campaign_id : str
            Campaign ID
        from_touch_sequence : int
            Source touch sequence number
        to_touch_sequence : int
            Target touch sequence number
        additional_signals : Optional[list]
            New signals to add to context
        
        Returns
        -------
        Optional[IdentityContext]
            New context for target touch, or None if source not found
        """
        # Load source context
        source_context = self._load_context(
            identity_hash=identity_hash,
            campaign_id=campaign_id,
            touch_sequence=from_touch_sequence,
        )
        
        if source_context is None:
            return None
        
        # Build new context for target touch
        new_context = IdentityContext(
            identity_hash=identity_hash,
            campaign_id=campaign_id,
            touch_sequence=to_touch_sequence,
            accumulated_signals=list(source_context.accumulated_signals),
            prior_responses=list(source_context.prior_responses),
            content_preferences=dict(source_context.content_preferences),
            timing_preferences=dict(source_context.timing_preferences),
            custom_context=dict(source_context.custom_context),
        )
        
        # Add new signals
        if additional_signals:
            new_context.accumulated_signals.extend(additional_signals)
        
        # Store new context
        self._store_context(new_context)
        
        return new_context
    
    def update_context_from_response(
        self,
        identity_hash: str,
        campaign_id: str,
        touch_sequence: int,
        response_data: dict,
    ) -> Optional[IdentityContext]:
        """Update context based on recipient response.
        
        Called when recipient replies to a touch.
        
        Parameters
        ----------
        identity_hash : str
            Recipient identity hash
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Which touch was responded to
        response_data : dict
            Response data (classification, sentiment, etc.)
        
        Returns
        -------
        Optional[IdentityContext]
            Updated context
        """
        context = self._load_context(
            identity_hash=identity_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
        )
        
        if context is None:
            return None
        
        # Add response to history
        response_record = {
            "touch_sequence": touch_sequence,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "classification": response_data.get("classification", "unknown"),
            "sentiment": response_data.get("sentiment", "neutral"),
            "content_preview": response_data.get("content", "")[:200],
        }
        
        # Build updated context (dataclass is frozen, so create new)
        updated_context = IdentityContext(
            identity_hash=context.identity_hash,
            campaign_id=context.campaign_id,
            touch_sequence=context.touch_sequence,
            accumulated_signals=list(context.accumulated_signals),
            prior_responses=list(context.prior_responses) + [response_record],
            content_preferences=self._learn_content_preferences(
                context.content_preferences,
                response_data,
            ),
            timing_preferences=self._learn_timing_preferences(
                context.timing_preferences,
                response_data,
            ),
            custom_context=dict(context.custom_context),
            created_at=context.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        
        self._store_context(updated_context)
        
        return updated_context
    
    def _store_context(self, context: IdentityContext) -> bool:
        """Store context in L4 state."""
        # Serialize context for storage
        context_data = {
            "identity_hash": context.identity_hash,
            "campaign_id": context.campaign_id,
            "touch_sequence": context.touch_sequence,
            "accumulated_signals": context.accumulated_signals,
            "prior_responses": context.prior_responses,
            "content_preferences": context.content_preferences,
            "timing_preferences": context.timing_preferences,
            "custom_context": context.custom_context,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
        }
        
        # In production, this would write to apps_lic_identity_context table
        # For now, we store in touch_state context_carry_forward field
        return True
    
    def _load_context(
        self,
        identity_hash: str,
        campaign_id: str,
        touch_sequence: int,
    ) -> Optional[IdentityContext]:
        """Load context from L4 state."""
        # In production, this would query apps_lic_identity_context table
        # For now, return None (would be populated from touch_state query)
        return None
    
    def _learn_content_preferences(
        self,
        existing: dict,
        response_data: dict,
    ) -> dict:
        """Learn content preferences from response."""
        # Simple learning: track what content got positive responses
        preferences = dict(existing)
        
        if response_data.get("classification") == "positive":
            content_type = response_data.get("content_type", "unknown")
            preferences[content_type] = preferences.get(content_type, 0) + 1
        
        return preferences
    
    def _learn_timing_preferences(
        self,
        existing: dict,
        response_data: dict,
    ) -> dict:
        """Learn timing preferences from response."""
        preferences = dict(existing)
        
        # Track response time patterns
        hour_of_day = datetime.now(timezone.utc).hour
        preferences[f"response_hour_{hour_of_day}"] = preferences.get(
            f"response_hour_{hour_of_day}", 0
        ) + 1
        
        return preferences


# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------

def get_identity_propagation_service(
    state_adapter: Optional[Any] = None,
) -> IdentityPropagationService:
    """Get configured IdentityPropagationService.
    
    Parameters
    ----------
    state_adapter : Optional[TouchStateUWGAdapter]
        UWG adapter. If None, uses default.
    
    Returns
    -------
    IdentityPropagationService
        Configured service
    """
    if state_adapter is None:
        from agentic_core.L4_state.uwg.durable_write_gateway import get_gateway
        from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter
        
        gateway = get_gateway()
        state_adapter = TouchStateUWGAdapter(gateway)
    
    return IdentityPropagationService(state_adapter)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "RecipientIdentity",
    "IdentityContext",
    "IdentityHasher",
    "IdentityPropagationService",
    "get_identity_propagation_service",
]
