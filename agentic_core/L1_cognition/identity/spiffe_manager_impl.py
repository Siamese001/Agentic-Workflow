"""Implementation for spiffe_manager."""

import logging
import time
import hashlib
import secrets
from typing import Any, Dict, List, Optional

# Assuming these types are defined elsewhere
# from .spiffe_manager_types import AgentIdentity, IdentityType, IdentityVerificationResult, TrustDomain
class TrustDomain:
    LOCAL = "local"
    # Add other trust domains if necessary

class IdentityType:
    AGENT = "agent"
    # Add other identity types if necessary

class IdentityVerificationResult:
    def __init__(self, valid: bool, reason: str = "", identity: Optional['AgentIdentity'] = None):
        self.valid = valid
        self.reason = reason
        self.identity = identity

class AgentIdentity:
    def __init__(self,
                 spiffe_id: str,
                 agent_type: IdentityType,
                 trust_domain: TrustDomain,
                 public_key: str,
                 private_key: str,
                 issued_at: float,
                 expires_at: float,
                 capabilities: List[str],
                 metadata: Dict[str, Any]):
        self.spiffe_id = spiffe_id
        self.agent_type = agent_type
        self.trust_domain = trust_domain
        self.public_key = public_key
        self.private_key = private_key
        self.issued_at = issued_at
        self.expires_at = expires_at
        self.capabilities = capabilities
        self.metadata = metadata

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def get_namespace(self) -> str:
        parts = self.spiffe_id.split('/')
        if len(parts) > 3:
            return parts[3]
        return 'default'


LOGGER = logging.getLogger(__name__)



class SPIFFEManager:
    """Manager for SPIFFE-based agent identities. """

    def __init__(self,
                 trust_domain: TrustDomain = TrustDomain.LOCAL,
                 default_ttl_seconds: int = 3600,
                 enable_logging: bool = True):
        """Initialize SPIFFE manager. """
        self.trust_domain = trust_domain
        self.default_ttl_seconds = default_ttl_seconds
        self.enable_logging = enable_logging
        self._identities: Dict[str, AgentIdentity] = {}
        self._revoked_ids: set = set()
        if self.enable_logging:
            LOGGER.info('spiffe_manager_initialized',
                        extra={'trust_domain': trust_domain.value if hasattr(trust_domain, 'value') else trust_domain,
                               'default_ttl': default_ttl_seconds})

    def create_identity(self,
                        agent_name: str,
                        agent_type: IdentityType,
                        namespace: str = 'default',
                        capabilities: Optional[List[str]] = None,
                        ttl_seconds: Optional[int] = None,
                        metadata: Optional[Dict[str,
                                                Any]] = None) -> AgentIdentity:
        """Create a new agent identity. """
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        spiffe_id = self._generate_spiffe_id(trust_domain=self.trust_domain,
                                             namespace=namespace,
                                             agent_name=agent_name)
        public_key, private_key = self._generate_key_pair()
        identity = AgentIdentity(spiffe_id=spiffe_id,
                                 agent_type=agent_type,
                                 trust_domain=self.trust_domain,
                                 public_key=public_key,
                                 private_key=private_key,
                                 issued_at=now,
                                 expires_at=now + ttl,
                                 capabilities=capabilities or [],
                                 metadata=metadata or {})
        self._identities[spiffe_id] = identity
        if self.enable_logging:
            LOGGER.info('identity_created',
                        EXTRA={'spiffe_id': spiffe_id,
                               'agent_type': agent_type.value if hasattr(agent_type, 'value') else agent_type,
                               'namespace': namespace,
                               'expires_in': ttl})
        return identity

    def verify_identity(self, spiffe_id: str, public_key: str) -> IdentityVerificationResult:
        """Verify an agent identity. """
        if spiffe_id in self._revoked_ids:
            return IdentityVerificationResult(valid=False, reason='Identity has been revoked')
        identity = self._identities.get(spiffe_id)
        if not identity:
            return IdentityVerificationResult(valid=False, reason='Identity not found')
        if identity.is_expired():
            return IdentityVerificationResult(valid=False,
                                              identity=identity,
                                              reason='Identity has expired')
        if identity.public_key != public_key:
            return IdentityVerificationResult(valid=False,
                                              identity=identity,
                                              reason='Public key mismatch')
        if self.enable_logging:
            LOGGER.debug('identity_verified', extra={'spiffe_id': spiffe_id})
        return IdentityVerificationResult(valid=True,
                                          identity=identity,
                                          reason='Identity verified successfully')

    def rotate_credentials(self,
                           spiffe_id: str,
                           ttl_seconds: Optional[int] = None) -> Optional[AgentIdentity]:
        """Rotate credentials for an existing identity. """
        identity = self._identities.get(spiffe_id)
        if not identity:
            return None
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        public_key, private_key = self._generate_key_pair()
        identity.public_key = public_key
        identity.private_key = private_key
        identity.issued_at = now
        identity.expires_at = now + ttl
        if self.enable_logging:
            LOGGER.info('credentials_rotated',
                        EXTRA={'spiffe_id': spiffe_id,
                               'new_expires_at': identity.expires_at})
        return identity

    def revoke_identity(self, spiffe_id: str) -> bool:
        """Revoke an agent identity. """
        if spiffe_id in self._identities:
            self._revoked_ids.add(spiffe_id)
            if self.enable_logging:
                LOGGER.warning('identity_revoked', extra={
                               'spiffe_id': spiffe_id})
            return True
        return False

    def get_identity(self, spiffe_id: str) -> Optional[AgentIdentity]:
        """Get an identity by SPIFFE ID. """
        return self._identities.get(spiffe_id)

    def list_identities(self,
                        agent_type: Optional[IdentityType] = None,
                        namespace: Optional[str] = None) -> List[AgentIdentity]:
        """List all identities. """
        identities = list(self._identities.values())
        if agent_type:
            identities = [i for i in identities if i.agent_type == agent_type]
        if namespace:
            identities = [i for i in identities if i.get_namespace()
                          == namespace]
        return identities

    def cleanup_expired(self) -> int:
        """Remove expired identities. """
        expired_ids = [spiffe_id for spiffe_id,
                   identity in self._identities.items() if identity.is_expired()]
        for spiffe_id in expired_ids:
            del self._identities[spiffe_id]
        if self.enable_logging and expired_ids:
            LOGGER.info('expired_identities_cleaned',
                        extra={'count': len(expired_ids)})
        return len(expired_ids)

    def _generate_spiffe_id(self,
                            trust_domain: TrustDomain,
                            namespace: str,
                            agent_name: str) -> str:
        """Generate a SPIFFE ID. """
        return f'spiffe://{trust_domain.value if hasattr(trust_domain, "value") else trust_domain}/{namespace}/{agent_name}'

    def _generate_key_pair(self) -> tuple[str, str]:
        """Generate a cryptographic key pair. """
        seed = secrets.token_bytes(32)
        private_key = hashlib.sha256(seed).hexdigest()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return (public_key, private_key)


def create_spiffe_manager(trust_domain: TrustDomain = TrustDomain.LOCAL,
                          default_ttl_seconds: int = 3600) -> SPIFFEManager:
    """Factory function to create SPIFFE manager. """
    return SPIFFEManager(trust_domain=trust_domain, default_ttl_seconds=default_ttl_seconds)

