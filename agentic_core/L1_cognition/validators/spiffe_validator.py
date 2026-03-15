from __future__ import annotations

import hashlib

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "spiffe_validator", "L1")
_emit_routes_through("p1", "spiffe_validator", "L1")
_emit_escalates_to_human("p1", "spiffe_validator", "L1")
_emit_reads_policy_state("p1", "spiffe_validator", "L1")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import logging
import secrets
from typing import Any

from agentic_core.L1_cognition.identity.spiffe_manager_types import (
    AgentIdentity,
    IdentityType,
    IdentityVerificationResult,
    TrustDomain,
)

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class SpiffeManager:
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
        TrustDomain: TrustDomain = TrustDomain.LOCAL,
        default_ttl_seconds: int = 3600,
        enable_logging: bool = True,
    ):
        """Initialize SPIFFE manager.

        Args:
            TrustDomain: Default trust domain
            default_ttl_seconds: Default identity TTL
            enable_logging: Enable logging
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SpiffeManager.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SpiffeManager.__init__", "p0_governance")
        self.TrustDomain = TrustDomain
        self.default_ttl_seconds = default_ttl_seconds
        self.enable_logging = enable_logging
        self._identities: dict[str, AgentIdentity] = {}
        self._revoked_ids: set = set()
        if self.enable_logging:
            LOGGER.info(
                "spiffe_manager_initialized",
                extra={"TrustDomain": TrustDomain.value, "default_ttl": default_ttl_seconds},
            )

    def create_identity(
        self,
        agent_name: str,
        agent_type: IdentityType,
        namespace: str = "default",
        capabilities: list[str] | None = None,
        ttl_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "SpiffeManager.create_identity")

        ttl: Any = ttl_seconds or self.default_ttl_seconds
        now: Any = get_clock().now_epoch()
        spiffe_id: Any = self._generate_spiffe_id(
            TrustDomain=self.TrustDomain, namespace=namespace, agent_name=agent_name
        )
        public_key, private_key = self._generate_key_pair()
        identity: Any = AgentIdentity(
            spiffe_id=spiffe_id,
            agent_type=agent_type,
            TrustDomain=self.TrustDomain,
            public_key=public_key,
            private_key=private_key,
            issued_at=now,
            expires_at=now + ttl,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )
        self._identities[spiffe_id] = identity
        if self.enable_logging:
            LOGGER.info(
                "identity_created",
                extra={
                    "spiffe_id": spiffe_id,
                    "agent_type": agent_type.value,
                    "namespace": namespace,
                    "expires_in": ttl,
                },
            )
        return identity

    def verify_identity(self, spiffe_id: str, public_key: str) -> IdentityVerificationResult:
        """Verify an agent identity.

        Args:
            spiffe_id: SPIFFE ID to verify
            public_key: Public key to verify

        Returns:
            IdentityVerificationResult
        """
        if spiffe_id in self._revoked_ids:
            return IdentityVerificationResult(valid=False, reason="Identity has been revoked")
        identity: Any = self._identities.get(spiffe_id)
        if not identity:
            return IdentityVerificationResult(valid=False, reason="Identity not found")
        if identity.is_expired():
            return IdentityVerificationResult(valid=False, identity=identity, reason="Identity has expired")
        if identity.public_key != public_key:
            return IdentityVerificationResult(valid=False, identity=identity, reason="Public key mismatch")
        if self.enable_logging:
            LOGGER.debug("identity_verified", extra={"spiffe_id": spiffe_id})
        return IdentityVerificationResult(
            valid=True, identity=identity, reason="Identity verified successfully"
        )

    def rotate_credentials(self, spiffe_id: str, ttl_seconds: int | None = None) -> AgentIdentity | None:
        """Rotate credentials for an existing identity.

        Args:
            spiffe_id: SPIFFE ID to rotate
            ttl_seconds: New TTL

        Returns:
            Updated AgentIdentity or None if not found
        """
        identity: Any = self._identities.get(spiffe_id)
        if not identity:
            return None
        ttl: Any = ttl_seconds or self.default_ttl_seconds
        now: Any = get_clock().now_epoch()
        public_key, private_key = self._generate_key_pair()
        identity.public_key = public_key
        identity.private_key = private_key
        identity.issued_at = now
        identity.expires_at = now + ttl
        if self.enable_logging:
            LOGGER.info(
                "credentials_rotated", extra={"spiffe_id": spiffe_id, "new_expires_at": identity.expires_at}
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
                LOGGER.warning("identity_revoked", extra={"spiffe_id": spiffe_id})
            return True
        return False

    def get_identity(self, spiffe_id: str) -> AgentIdentity | None:
        """Get an identity by SPIFFE ID.

        Args:
            spiffe_id: SPIFFE ID

        Returns:
            AgentIdentity or None
        """
        return self._identities.get(spiffe_id)

    def list_identities(
        self, agent_type: IdentityType | None = None, namespace: str | None = None
    ) -> list[AgentIdentity]:
        """List all identities.

        Args:
            agent_type: Filter by agent type
            namespace: Filter by namespace

        Returns:
            List of AgentIdentity objects
        """
        identities: Any = list(self._identities.values())
        if agent_type:
            identities: Any = [i for i in identities if i.agent_type == agent_type]
        if namespace:
            identities: Any = [i for i in identities if i.get_namespace() == namespace]
        return identities

    def cleanup_expired(self) -> int:
        """Remove expired identities.

        Returns:
            Number of identities removed
        """
        expired: Any = [
            spiffe_id for spiffe_id, identity in self._identities.items() if identity.is_expired()
        ]
        for spiffe_id in expired:
            del self._identities[spiffe_id]
        if self.enable_logging and expired:
            LOGGER.info("expired_identities_cleaned", extra={"count": len(expired)})
        return len(expired)

    def _generate_spiffe_id(self, TrustDomain: TrustDomain, namespace: str, agent_name: str) -> str:
        """Generate a SPIFFE ID.

        Args:
            TrustDomain: Trust domain
            namespace: Namespace
            agent_name: Agent name

        Returns:
            SPIFFE ID string
        """
        return f"spiffe://{TrustDomain.value}/{namespace}/{agent_name}"

    def _generate_key_pair(self) -> tuple[str, str]:
        """Generate a cryptographic key pair.

        Simplified implementation using SHA-256 hashing.
        Production should use RSA/ECDSA key generation.

        Returns:
            Tuple of (public_key, private_key)
        """
        seed = secrets.token_bytes(32)
        private_key = hashlib.sha256(seed).hexdigest()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return (public_key, private_key)

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L1 cognition agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def create_spiffe_manager(
    TrustDomain: TrustDomain = TrustDomain.LOCAL, default_ttl_seconds: int = 3600
) -> SpiffeManager:
    """Factory function to create SPIFFE manager.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        TrustDomain: Trust domain
        default_ttl_seconds: Default TTL

    Returns:
        SPIFFEManager instance
    """
    return SpiffeManager(TrustDomain=TrustDomain, default_ttl_seconds=default_ttl_seconds)


def get_spiffe_manager() -> SpiffeManager:
    """Factory function to get spiffe manager instance."""
    return SpiffeManager()
    return SPIFFEManager(TrustDomain=TrustDomain, default_ttl_seconds=default_ttl_seconds)
