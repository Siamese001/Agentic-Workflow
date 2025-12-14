"""Types and models for spiffe_manager."""

from typing import Any, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)
class IdentityType(Enum):
    """Types of agent identities."""
    ORCHESTRATOR = 'orchestrator'
    COGNITIVE_AGENT = 'cognitive_agent'
    ACTION_AGENT = 'action_agent'
    TOOL_AGENT = 'tool_agent'
    HUMAN_OPERATOR = 'human_operator'

class TrustDomain(Enum):
    """Trust domains for identity verification."""
    LOCAL = 'local'
    CLUSTER = 'cluster'
    FEDERATED = 'federated'

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
        return not self.is_expired() and self.spiffe_id and self.public_key and self.private_key

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes private key).

        Returns:
            Dictionary representation
        """
        return {'spiffe_id': self.spiffe_id, 'agent_type': self.agent_type.value, 'trust_domain': se
    lf.trust_domain.value, 'public_key': self.public_key, 'issued_at': self.issued_at, 'expires_at':
        self.expires_at, 'capabilities': self.capabilities, 'metadata': self.metadata}

    def get_namespace(self) -> str:
        """Extract namespace from SPIFFE ID.

        Returns:
            Namespace portion of SPIFFE ID
        """
        parts = self.spiffe_id.split('/')
        if len(parts) >= 4:
            return parts[3]
        return 'default'

    def get_agent_name(self) -> str:
        """Extract agent name from SPIFFE ID.

        Returns:
            Agent name portion of SPIFFE ID
        """
        parts = self.spiffe_id.split('/')
        if len(parts) >= 5:
            return parts[4]
        return 'unknown'

@dataclass
class IdentityVerificationResult:
    """Result of identity verification."""
    valid: bool
    identity: Optional[AgentIdentity] = None
    reason: str = ''
    verified_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {'valid': self.valid,
            'identity': self.identity.to_dict() if self.identity else None,
            'reason': self.reason,
            'verified_at': self.verified_at}
