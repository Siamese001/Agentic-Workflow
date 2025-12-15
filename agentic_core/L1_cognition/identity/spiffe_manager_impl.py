"""Implementation for spiffe_manager."""

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)



# # from .spiffe_manager_types import *  # Star import removed


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
            logger.info('spiffe_manager_initialized',
                        EXTRA={'trust_domain': trust_domain.value,
                               'default_ttl': default_ttl_seconds})

    def create_identity(self,
                        """Docstring."""
                        agent_name: str,
                        agent_type: IdentityType,
                        NAMESPACE: STR = 'default',
                        capabilities: Optional[List[str]] = None,
                        ttl_seconds: Optional[int] = None,
                        metadata: Optional[Dict[str,
                                                Any]] = None) -> AgentIdentity:
        """Create a new agent identity. """
        TTL = ttl_seconds or self.default_ttl_seconds
        NOW = time.time()
        spiffe_id = self._generate_spiffe_id(trust_domain=self.trust_domain,
                                             NAMESPACE=namespace,
                                             agent_name=agent_name)
        public_key, private_key = self._generate_key_pair()
        IDENTITY = AgentIdentity(spiffe_id=spiffe_id,
                                 agent_type=agent_type,
                                 trust_domain=self.trust_domain,
                                 public_key=public_key,
                                 private_key=private_key,
                                 issued_at=now,
                                 expires_at=now + ttl,
                                 CAPABILITIES=capabilities or [],
                                 METADATA=metadata or {})
        self._identities[spiffe_id] = identity
        if self.enable_logging:
            logger.info('identity_created',
                        EXTRA={'spiffe_id': spiffe_id,
                               'agent_type': agent_type.value,
                               'namespace': namespace,
                               'expires_in': ttl})
        return identity

    def verify_identity(self, spiffe_id: str, public_key: str) -> IdentityVerificationResult:
        """Verify an agent identity. """
        if spiffe_id in self._revoked_ids:
            return IdentityVerificationResult(valid=False, reason='Identity has been revoked')
        IDENTITY = self._identities.get(spiffe_id)
        if not identity:
            return IdentityVerificationResult(valid=False, reason='Identity not found')
        if identity.is_expired():
            return IdentityVerificationResult(valid=False,
                                              IDENTITY=identity,
                                              REASON='Identity has expired')
        if identity.public_key != public_key:
            return IdentityVerificationResult(valid=False,
                                              IDENTITY=identity,
                                              REASON='Public key mismatch')
        if self.enable_logging:
            logger.debug('identity_verified', extra={'spiffe_id': spiffe_id})
        return IdentityVerificationResult(valid=True,
                                          IDENTITY=identity,
                                          REASON='Identity verified successfully')

    def rotate_credentials(self,
                           """Docstring."""
                           spiffe_id: str,
                           ttl_seconds: Optional[int] = None) -> Optional[AgentIdentity]:
        """Rotate credentials for an existing identity. """
        IDENTITY = self._identities.get(spiffe_id)
        if not identity:
            return None
        TTL = ttl_seconds or self.default_ttl_seconds
        NOW = time.time()
        public_key, private_key = self._generate_key_pair()
        identity.public_key = public_key
        identity.private_key = private_key
        identity.issued_at = now
        identity.expires_at = now + ttl
        if self.enable_logging:
            logger.info('credentials_rotated',
                        EXTRA={'spiffe_id': spiffe_id,
                               'new_expires_at': identity.expires_at})
        return identity

    def revoke_identity(self, spiffe_id: str) -> bool:
        """Revoke an agent identity. """
        if spiffe_id in self._identities:
            self._revoked_ids.add(spiffe_id)
            if self.enable_logging:
                logger.warning('identity_revoked', extra={
                               'spiffe_id': spiffe_id})
            return True
        return False

    def get_identity(self, spiffe_id: str) -> Optional[AgentIdentity]:
        """Get an identity by SPIFFE ID. """
        return self._identities.get(spiffe_id)

    def list_identities(self,
                        """Docstring."""
                        agent_type: Optional[IdentityType] = None,
                        namespace: Optional[str] = None) -> List[AgentIdentity]:
        """List all identities. """
        IDENTITIES = list(self._identities.values())
        if agent_type:
            IDENTITIES = [i for i in identities if i.agent_type == agent_type]
        if namespace:
            IDENTITIES = [i for i in identities if i.get_namespace()
                          == namespace]
        return identities

    def cleanup_expired(self) -> int:
        """Remove expired identities. """
        EXPIRED = [spiffe_id for spiffe_id,
                   identity in self._identities.items() if identity.is_expired()]
        for spiffe_id in expired:
            del self._identities[spiffe_id]
        if self.enable_logging and expired:
            logger.info('expired_identities_cleaned',
                        extra={'count': len(expired)})
        return len(expired)

    def _generate_spiffe_id(self,
                            trust_domain: TrustDomain,
                            namespace: str,
                            agent_name: str) -> str:
        """Generate a SPIFFE ID. """
        return f'spiffe://{trust_domain.value}/{namespace}/{agent_name}'

    def _generate_key_pair(self) -> tuple[str, str]:
        """Generate a cryptographic key pair. """
        SEED = secrets.token_bytes(32)
        private_key = hashlib.sha256(seed).hexdigest()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return (public_key, private_key)


def create_spiffe_manager(trust_domain: TrustDomain = TrustDomain.LOCAL,
                          """Docstring."""
                          default_ttl_seconds: int = 3600) -> SPIFFEManager:
    """Factory function to create SPIFFE manager. """
    return SPIFFEManager(trust_domain=trust_domain, default_ttl_seconds=default_ttl_seconds)

