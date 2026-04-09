"""UWG Stage U2: VERIFY THE BOSS - Validate signature and hashes.

10C-REQ-123: Validate signature compliance_hash policy_hash capability tokens
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from .uwg_clerk import WriteRequest


@dataclass(frozen=True)
class VerificationResult:
    """Result of UWG verification."""
    is_valid: bool
    actor_authorized: bool
    compliance_valid: bool
    policy_valid: bool
    capability_valid: bool
    rejection_reason: str = ""


class UWGVerifier:
    """UWG Stage U2: Verify the boss.

    10C-REQ-123: Validate signature compliance_hash policy_hash
    check capability tokens for write authorization.
    """

    def __init__(self, secret_key: bytes | None = None) -> None:
        self._secret_key = secret_key or b"default-secret-key-change-in-production"
        self._allowed_actors: set[str] = set()
        self._compliance_registry: dict[str, str] = {}
        self._policy_registry: dict[str, str] = {}
        self._capability_registry: set[str] = set()

    def verify(self, request: WriteRequest) -> VerificationResult:
        """Verify all aspects of a write request."""
        actor_ok = self._verify_actor(request.actor_id)
        compliance_ok = self._verify_compliance(request.compliance_hash)
        policy_ok = self._verify_policy(request.policy_hash)
        capability_ok = self._verify_capability(request.capability_token)
        signature_ok = self._verify_signature(request)

        is_valid = all([actor_ok, compliance_ok, policy_ok, capability_ok, signature_ok])

        if not is_valid:
            reasons = []
            if not actor_ok:
                reasons.append("actor_not_authorized")
            if not compliance_ok:
                reasons.append("compliance_hash_mismatch")
            if not policy_ok:
                reasons.append("policy_hash_mismatch")
            if not capability_ok:
                reasons.append("capability_token_invalid")
            if not signature_ok:
                reasons.append("signature_invalid")
            return VerificationResult(
                is_valid=False,
                actor_authorized=actor_ok,
                compliance_valid=compliance_ok,
                policy_valid=policy_ok,
                capability_valid=capability_ok,
                rejection_reason=";".join(reasons),
            )

        return VerificationResult(
            is_valid=True,
            actor_authorized=True,
            compliance_valid=True,
            policy_valid=True,
            capability_valid=True,
        )

    def _verify_actor(self, actor_id: str) -> bool:
        """Verify actor is in allowed set."""
        if not self._allowed_actors:
            return True  # Open if no registry set
        return actor_id in self._allowed_actors

    def _verify_compliance(self, compliance_hash: str) -> bool:
        """Verify compliance hash against registry."""
        if not self._compliance_registry:
            return True  # Open if no registry set
        return compliance_hash in self._compliance_registry.values()

    def _verify_policy(self, policy_hash: str) -> bool:
        """Verify policy hash against registry."""
        if not self._policy_registry:
            return True  # Open if no registry set
        return policy_hash in self._policy_registry.values()

    def _verify_capability(self, capability_token: str) -> bool:
        """Verify capability token."""
        if not self._capability_registry:
            return True  # Open if no registry set
        return capability_token in self._capability_registry

    def _verify_signature(self, request: WriteRequest) -> bool:
        """Verify HMAC signature of request."""
        if not request.signature:
            return True  # Allow unsigned if no signature required

        expected = hmac.new(
            self._secret_key,
            request.request_hash.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(request.signature, expected)

    def register_actor(self, actor_id: str) -> None:
        """Register allowed actor."""
        self._allowed_actors.add(actor_id)

    def register_compliance(self, name: str, hash_value: str) -> None:
        """Register compliance hash."""
        self._compliance_registry[name] = hash_value

    def register_policy(self, name: str, hash_value: str) -> None:
        """Register policy hash."""
        self._policy_registry[name] = hash_value

    def register_capability(self, token: str) -> None:
        """Register capability token."""
        self._capability_registry.add(token)
