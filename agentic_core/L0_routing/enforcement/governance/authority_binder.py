"""C0 G2: WHO'S ASKING? - Authority context binding.

10C-REQ-111: Attach identity and credentials to request authority context
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Identity:
    """Immutable identity."""

    actor_id: str
    role: str
    tenant_id: str = "default"

    def to_hash(self) -> str:
        """Hash of identity."""
        raw = f"{self.actor_id}:{self.role}:{self.tenant_id}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Credentials:
    """Credentials for authentication."""

    token: str = ""
    signature: str = ""
    expiry: float = 0.0
    scopes: list[str] = field(default_factory=list)


@dataclass
class AuthorityContext:
    """Authority context attached to request.

    10C-REQ-111: Contains identity, credentials, and policy bindings.
    """

    identity: Identity
    credentials: Credentials
    policy_hash: str = ""
    compliance_hash: str = ""
    capability_tokens: list[str] = field(default_factory=list)
    bound_at: float = 0.0

    def is_authenticated(self) -> bool:
        """Check if context has valid authentication."""
        return bool(self.identity.actor_id and self.credentials.token)

    def has_scope(self, scope: str) -> bool:
        """Check if context has specific scope."""
        return scope in self.credentials.scopes

    def to_audit_record(self) -> dict[str, Any]:
        """Convert to audit-safe record (no sensitive data)."""
        return {
            "identity_hash": self.identity.to_hash(),
            "role": self.identity.role,
            "tenant_id": self.identity.tenant_id,
            "policy_hash": self.policy_hash,
            "scopes": self.credentials.scopes,
            "bound_at": self.bound_at,
        }


class AuthorityBinder:
    """C0 G2: Authority context binder.

    10C-REQ-111: Bind authority context to request with identity
    credentials and policy compliance.
    """

    def __init__(self) -> None:
        self._identity_registry: dict[str, Identity] = {}
        self._policy_registry: dict[str, str] = {}
        self._compliance_registry: dict[str, str] = {}

    def bind(
        self,
        actor_id: str,
        credentials: Credentials,
        policy_hash: str = "",
        compliance_hash: str = "",
    ) -> AuthorityContext:
        """Bind authority context."""
        identity = self._identity_registry.get(actor_id, Identity(actor_id=actor_id, role="unknown"))

        return AuthorityContext(
            identity=identity,
            credentials=credentials,
            policy_hash=policy_hash or self._get_default_policy(),
            compliance_hash=compliance_hash or self._get_default_compliance(),
            bound_at=0.0,  # Would use determinism surface clock
        )

    def _get_default_policy(self) -> str:
        """Get default policy hash."""
        return self._policy_registry.get("default", "")

    def _get_default_compliance(self) -> str:
        """Get default compliance hash."""
        return self._compliance_registry.get("default", "")

    def register_identity(self, identity: Identity) -> None:
        """Register an identity."""
        self._identity_registry[identity.actor_id] = identity

    def register_policy(self, name: str, hash_val: str) -> None:
        """Register a policy hash."""
        self._policy_registry[name] = hash_val

    def verify_binding(self, context: AuthorityContext) -> bool:
        """Verify a bound authority context."""
        # Check identity exists
        if context.identity.actor_id not in self._identity_registry:
            return False

        # Check policy exists
        if context.policy_hash not in self._policy_registry.values():
            return False

        return True
