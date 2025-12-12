"""SPIFFE Identity Manager for Agent Authentication.

Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Manages cryptographically-verified agent identities using SPIFFE principles.

SPIFFE (Secure Production Identity Framework For Everyone) provides:
- Cryptographic identity for workloads
- Automatic credential rotation
- Platform-agnostic identity verification
"""

import hashlib
import secrets
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IdentityType(Enum):
    """Types of agent identities."""
    ORCHESTRATOR = "orchestrator"
    COGNITIVE_AGENT = "cognitive_agent"
    ACTION_AGENT = "action_agent"
    TOOL_AGENT = "tool_agent"
    HUMAN_OPERATOR = "human_operator"


class TrustDomain(Enum):
    """Trust domains for identity verification."""
    LOCAL = "local"
    CLUSTER = "cluster"
    FEDERATED = "federated"


@dataclass
class AgentIdentity:
    """Cryptographically-verified agent identity.
    
    Based on SPIFFE ID format: spiffe://trust-domain/path
    """
    spiffe_id: str
    agent_type: IdentityType
    trust_domain: TrustDomain
    public_key: str
    private_key: str
    issued_at: float
    expires_at: float
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if identity has expired.
        
        Returns:
            True if expired
        """
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if identity is valid.
        
        Returns:
            True if valid (not expired and has required fields)
        """
        return (
            not self.is_expired()
            and self.spiffe_id
            and self.public_key
            and self.private_key
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes private key).
        
        Returns:
            Dictionary representation
        """
        return {
            "spiffe_id": self.spiffe_id,
            "agent_type": self.agent_type.value,
            "trust_domain": self.trust_domain.value,
            "public_key": self.public_key,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }
    
    def get_namespace(self) -> str:
        """Extract namespace from SPIFFE ID.
        
        Returns:
            Namespace portion of SPIFFE ID
        """
        # Format: spiffe://trust-domain/namespace/agent-name
        parts = self.spiffe_id.split("/")
        if len(parts) >= 4:
            return parts[3]
        return "default"
    
    def get_agent_name(self) -> str:
        """Extract agent name from SPIFFE ID.
        
        Returns:
            Agent name portion of SPIFFE ID
        """
        # Format: spiffe://trust-domain/namespace/agent-name
        parts = self.spiffe_id.split("/")
        if len(parts) >= 5:
            return parts[4]
        return "unknown"


@dataclass
class IdentityVerificationResult:
    """Result of identity verification."""
    valid: bool
    identity: Optional[AgentIdentity] = None
    reason: str = ""
    verified_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "valid": self.valid,
            "identity": self.identity.to_dict() if self.identity else None,
            "reason": self.reason,
            "verified_at": self.verified_at,
        }


class SPIFFEManager:
    """Manager for SPIFFE-based agent identities.
    
    Provides:
    - Identity generation with cryptographic keys
    - Identity verification
    - Automatic credential rotation
    - Trust domain management
    
    Simplified implementation for Phase 3.
    Production systems should use full SPIFFE/SPIRE infrastructure.
    """
    
    def __init__(
        self,
        trust_domain: TrustDomain = TrustDomain.LOCAL,
        default_ttl_seconds: int = 3600,
        enable_logging: bool = True,
    ):
        """Initialize SPIFFE manager.
        
        Args:
            trust_domain: Default trust domain
            default_ttl_seconds: Default identity TTL
            enable_logging: Enable logging
        """
        self.trust_domain = trust_domain
        self.default_ttl_seconds = default_ttl_seconds
        self.enable_logging = enable_logging
        
        self._identities: Dict[str, AgentIdentity] = {}
        self._revoked_ids: set = set()
        
        if self.enable_logging:
            logger.info(
                "spiffe_manager_initialized",
                extra={
                    "trust_domain": trust_domain.value,
                    "default_ttl": default_ttl_seconds,
                }
            )
    
    def create_identity(
        self,
        agent_name: str,
        agent_type: IdentityType,
        namespace: str = "default",
        capabilities: Optional[List[str]] = None,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentIdentity:
        """Create a new agent identity.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent
            namespace: Namespace for the agent
            capabilities: List of capabilities
            ttl_seconds: Time-to-live in seconds
            metadata: Additional metadata
            
        Returns:
            AgentIdentity with cryptographic credentials
        """
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        
        # Generate SPIFFE ID
        spiffe_id = self._generate_spiffe_id(
            trust_domain=self.trust_domain,
            namespace=namespace,
            agent_name=agent_name,
        )
        
        # Generate cryptographic keys (simplified)
        public_key, private_key = self._generate_key_pair()
        
        identity = AgentIdentity(
            spiffe_id=spiffe_id,
            agent_type=agent_type,
            trust_domain=self.trust_domain,
            public_key=public_key,
            private_key=private_key,
            issued_at=now,
            expires_at=now + ttl,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )
        
        # Store identity
        self._identities[spiffe_id] = identity
        
        if self.enable_logging:
            logger.info(
                "identity_created",
                extra={
                    "spiffe_id": spiffe_id,
                    "agent_type": agent_type.value,
                    "namespace": namespace,
                    "expires_in": ttl,
                }
            )
        
        return identity
    
    def verify_identity(
        self,
        spiffe_id: str,
        public_key: str,
    ) -> IdentityVerificationResult:
        """Verify an agent identity.
        
        Args:
            spiffe_id: SPIFFE ID to verify
            public_key: Public key to verify
            
        Returns:
            IdentityVerificationResult
        """
        # Check if revoked
        if spiffe_id in self._revoked_ids:
            return IdentityVerificationResult(
                valid=False,
                reason="Identity has been revoked",
            )
        
        # Check if exists
        identity = self._identities.get(spiffe_id)
        if not identity:
            return IdentityVerificationResult(
                valid=False,
                reason="Identity not found",
            )
        
        # Check if expired
        if identity.is_expired():
            return IdentityVerificationResult(
                valid=False,
                identity=identity,
                reason="Identity has expired",
            )
        
        # Verify public key
        if identity.public_key != public_key:
            return IdentityVerificationResult(
                valid=False,
                identity=identity,
                reason="Public key mismatch",
            )
        
        if self.enable_logging:
            logger.debug(
                "identity_verified",
                extra={"spiffe_id": spiffe_id}
            )
        
        return IdentityVerificationResult(
            valid=True,
            identity=identity,
            reason="Identity verified successfully",
        )
    
    def rotate_credentials(
        self,
        spiffe_id: str,
        ttl_seconds: Optional[int] = None,
    ) -> Optional[AgentIdentity]:
        """Rotate credentials for an existing identity.
        
        Args:
            spiffe_id: SPIFFE ID to rotate
            ttl_seconds: New TTL
            
        Returns:
            Updated AgentIdentity or None if not found
        """
        identity = self._identities.get(spiffe_id)
        if not identity:
            return None
        
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        
        # Generate new keys
        public_key, private_key = self._generate_key_pair()
        
        # Update identity
        identity.public_key = public_key
        identity.private_key = private_key
        identity.issued_at = now
        identity.expires_at = now + ttl
        
        if self.enable_logging:
            logger.info(
                "credentials_rotated",
                extra={
                    "spiffe_id": spiffe_id,
                    "new_expires_at": identity.expires_at,
                }
            )
        
        return identity
    
    def revoke_identity(self, spiffe_id: str) -> bool:
        """Revoke an agent identity.
        
        Args:
            spiffe_id: SPIFFE ID to revoke
            
        Returns:
            True if revoked successfully
        """
        if spiffe_id in self._identities:
            self._revoked_ids.add(spiffe_id)
            
            if self.enable_logging:
                logger.warning(
                    "identity_revoked",
                    extra={"spiffe_id": spiffe_id}
                )
            
            return True
        
        return False
    
    def get_identity(self, spiffe_id: str) -> Optional[AgentIdentity]:
        """Get an identity by SPIFFE ID.
        
        Args:
            spiffe_id: SPIFFE ID
            
        Returns:
            AgentIdentity or None
        """
        return self._identities.get(spiffe_id)
    
    def list_identities(
        self,
        agent_type: Optional[IdentityType] = None,
        namespace: Optional[str] = None,
    ) -> List[AgentIdentity]:
        """List all identities.
        
        Args:
            agent_type: Filter by agent type
            namespace: Filter by namespace
            
        Returns:
            List of AgentIdentity objects
        """
        identities = list(self._identities.values())
        
        if agent_type:
            identities = [i for i in identities if i.agent_type == agent_type]
        
        if namespace:
            identities = [i for i in identities if i.get_namespace() == namespace]
        
        return identities
    
    def cleanup_expired(self) -> int:
        """Remove expired identities.
        
        Returns:
            Number of identities removed
        """
        expired = [
            spiffe_id for spiffe_id, identity in self._identities.items()
            if identity.is_expired()
        ]
        
        for spiffe_id in expired:
            del self._identities[spiffe_id]
        
        if self.enable_logging and expired:
            logger.info(
                "expired_identities_cleaned",
                extra={"count": len(expired)}
            )
        
        return len(expired)
    
    def _generate_spiffe_id(
        self,
        trust_domain: TrustDomain,
        namespace: str,
        agent_name: str,
    ) -> str:
        """Generate a SPIFFE ID.
        
        Args:
            trust_domain: Trust domain
            namespace: Namespace
            agent_name: Agent name
            
        Returns:
            SPIFFE ID string
        """
        # Format: spiffe://trust-domain/namespace/agent-name
        return f"spiffe://{trust_domain.value}/{namespace}/{agent_name}"
    
    def _generate_key_pair(self) -> tuple[str, str]:
        """Generate a cryptographic key pair.
        
        Simplified implementation using SHA-256 hashing.
        Production should use RSA/ECDSA key generation.
        
        Returns:
            Tuple of (public_key, private_key)
        """
        # Generate random seed
        seed = secrets.token_bytes(32)
        
        # Generate private key (hash of seed)
        private_key = hashlib.sha256(seed).hexdigest()
        
        # Generate public key (hash of private key)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        return public_key, private_key


def create_spiffe_manager(
    trust_domain: TrustDomain = TrustDomain.LOCAL,
    default_ttl_seconds: int = 3600,
) -> SPIFFEManager:
    """Factory function to create SPIFFE manager.
    
    Args:
        trust_domain: Trust domain
        default_ttl_seconds: Default TTL
        
    Returns:
        SPIFFEManager instance
    """
    return SPIFFEManager(
        trust_domain=trust_domain,
        default_ttl_seconds=default_ttl_seconds,
    )
