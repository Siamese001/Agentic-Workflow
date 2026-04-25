"""
Scoped per-run credential mint — W2-P2.2 (gap plan b7c4e2 G3).

Implements the Anthropic Claude-Code-on-the-Web pattern:

    "Sensitive credentials (such as git credentials or signing keys) are
    never inside the sandbox with Claude Code. ... Inside the sandbox, the
    git client authenticates to this service with a custom-built scoped
    credential. The proxy verifies this credential ..."

This module defines:

* ``ScopedCredential`` — an opaque, short-lived token bound to a single
  step lineage + audience (service name) + expiry.
* ``CredentialMint`` — issues / verifies / revokes ``ScopedCredential``
  instances. HMAC-based, in-memory; no secrets in the sandbox process.
* ``ScopedCredentialStore`` — trivial registry used by tests and by the
  W2 egress proxy (future wiring) to verify tokens at egress time.

Secrets (the mint's HMAC key) live in the mint instance which is created
**outside** the L2 sandbox context and only token *material* is handed to
the sandbox. Rotating the mint invalidates all outstanding tokens.

Guardian note: no broad exceptions; no subprocess; no filesystem writes.
"""

from __future__ import annotations

import hmac
import os
import secrets
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

__all__ = [
    "ScopedCredential",
    "CredentialMint",
    "InvalidCredential",
    "CredentialExpired",
    "CredentialRevoked",
]


class InvalidCredential(Exception):
    """Raised when a presented credential fails signature verification."""


class CredentialExpired(Exception):
    """Raised when a presented credential is past its expiry."""


class CredentialRevoked(Exception):
    """Raised when a presented credential was revoked."""


@dataclass(frozen=True, slots=True)
class ScopedCredential:
    """Short-lived credential scoped to (step_id, audience).

    ``token`` is what crosses the sandbox boundary. The signature binds the
    scope tuple to the mint's secret so forgery requires the mint's key.
    """

    step_id: str
    audience: str
    issued_at: float
    expires_at: float
    nonce: str
    signature: str

    @property
    def token(self) -> str:
        """Flat string form safe to pass through subprocess env / headers."""
        return (
            f"{self.step_id}.{self.audience}.{int(self.issued_at)}."
            f"{int(self.expires_at)}.{self.nonce}.{self.signature}"
        )

    def to_header_value(self) -> str:
        """Return a ``Bearer``-style header value."""
        return f"Bearer {self.token}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "audience": self.audience,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
            # signature deliberately omitted from to_dict to discourage logging
        }


@dataclass
class _MintState:
    revoked_nonces: set[str] = field(default_factory=set)


class CredentialMint:
    """HMAC-based scoped-credential issuer. Lives outside the sandbox."""

    def __init__(self, *, secret: bytes | None = None, default_ttl_s: float = 300.0) -> None:
        if secret is None:
            secret = os.urandom(32)
        if len(secret) < 16:
            raise ValueError("mint secret must be at least 16 bytes")
        self._secret = secret
        self._default_ttl_s = default_ttl_s
        self._state = _MintState()

    def issue(
        self,
        *,
        step_id: str,
        audience: str,
        ttl_s: float | None = None,
    ) -> ScopedCredential:
        """Mint a fresh credential for ``(step_id, audience)``."""
        if not step_id or not audience:
            raise ValueError("step_id and audience are required")
        ttl = float(ttl_s if ttl_s is not None else self._default_ttl_s)
        if ttl <= 0:
            raise ValueError("ttl_s must be positive")
        now = time.time()
        nonce = secrets.token_hex(16)
        issued_at = now
        expires_at = now + ttl
        sig = self._sign(step_id, audience, issued_at, expires_at, nonce)
        return ScopedCredential(
            step_id=step_id,
            audience=audience,
            issued_at=issued_at,
            expires_at=expires_at,
            nonce=nonce,
            signature=sig,
        )

    def verify(
        self,
        credential: ScopedCredential,
        *,
        expected_audience: str | None = None,
    ) -> None:
        """Validate signature, expiry, and revocation. Raises on failure."""
        if credential.nonce in self._state.revoked_nonces:
            raise CredentialRevoked(credential.nonce)
        now = time.time()
        if now > credential.expires_at:
            raise CredentialExpired(f"expired at {credential.expires_at}, now {now}")
        if expected_audience is not None and credential.audience != expected_audience:
            raise InvalidCredential(
                f"audience mismatch: got {credential.audience!r}, expected {expected_audience!r}"
            )
        expected_sig = self._sign(
            credential.step_id,
            credential.audience,
            credential.issued_at,
            credential.expires_at,
            credential.nonce,
        )
        if not hmac.compare_digest(expected_sig, credential.signature):
            raise InvalidCredential("signature mismatch")

    def revoke(self, credential: ScopedCredential) -> None:
        """Revoke by nonce. Subsequent ``verify`` calls raise ``CredentialRevoked``."""
        self._state.revoked_nonces.add(credential.nonce)

    def rotate_secret(self) -> None:
        """Replace the mint's secret. Invalidates every outstanding credential."""
        self._secret = os.urandom(32)
        self._state = _MintState()

    def _sign(
        self,
        step_id: str,
        audience: str,
        issued_at: float,
        expires_at: float,
        nonce: str,
    ) -> str:
        payload = f"{step_id}|{audience}|{int(issued_at)}|{int(expires_at)}|{nonce}".encode("utf-8")
        return hmac.new(self._secret, payload, sha256).hexdigest()[:32]
