"""Identity verifier protocol and default implementations for E3 ingress gate.

Closes gap G-04: E3 identity was presence-only. This module provides a
pluggable ``IdentityVerifier`` protocol so the gate can verify bearer tokens,
JWTs, or OAuth claims at ingress — and produce a ``VerifiedIdentity`` whose
``tenant_id`` / ``scopes`` drive ``caller_scope_baseline`` derivation.

Layer authority: L5 (policy plane) — verify only, no durable writes.

Default shipped implementations:
    * :class:`NoopIdentityVerifier` — presence-only (back-compat; tests only).
    * :class:`SharedSecretIdentityVerifier` — HMAC bearer token; production-ready
      for internal service-to-service calls.

A JWT implementation is intentionally left as an injection point; callers that
need OAuth/JWT provide their own ``IdentityVerifier`` matching this protocol.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerifiedIdentity:
    """Result of a successful identity verification.

    Fields are derived from verified claims only — never from raw envelope
    user-controlled input.
    """

    caller_id: str
    tenant_id: str
    scopes: tuple[str, ...] = field(default_factory=tuple)
    verified_at_utc: float = field(default_factory=time.time)

    def fingerprint(self) -> str:
        """Deterministic short hash of the verified triple (caller, tenant, scopes)."""

        payload = f"{self.caller_id}|{self.tenant_id}|{','.join(sorted(self.scopes))}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


class IdentityVerificationError(Exception):
    """Raised by a verifier when the presented credential cannot be trusted.

    The ingress gate converts this into an ``E3_IDENTITY_UNTRUSTED`` rejection.
    """


@runtime_checkable
class IdentityVerifier(Protocol):
    """Protocol for identity verification at ingress.

    Implementations MUST be pure read-side: no durable writes, no network I/O
    that can block for more than a small bounded timeout.
    """

    def verify(self, caller_identity: str, envelope: dict) -> VerifiedIdentity:
        """Verify ``caller_identity`` (plus any auxiliary envelope claims).

        Raises :class:`IdentityVerificationError` on any failure.
        """

        ...


class NoopIdentityVerifier:
    """Presence-only verifier. Back-compat shim; not for production.

    Logs a WARNING every 1000 verifications so unconfigured deployments are
    visible in L6 logs.
    """

    def __init__(self) -> None:
        self._count = 0

    def verify(self, caller_identity: str, envelope: dict) -> VerifiedIdentity:
        if not caller_identity or not isinstance(caller_identity, str):
            raise IdentityVerificationError("caller_identity is missing or not a string.")

        self._count += 1
        if self._count == 1 or self._count % 1000 == 0:
            logger.warning(
                "[NoopIdentityVerifier] No real identity verification configured "
                "(count=%d). Use SharedSecretIdentityVerifier or a JWT verifier in prod.",
                self._count,
            )

        tenant_id = str(envelope.get("tenant_id") or "default")
        return VerifiedIdentity(caller_id=caller_identity, tenant_id=tenant_id)


class SharedSecretIdentityVerifier:
    """HMAC-SHA256 bearer-token verifier for internal service-to-service calls.

    Envelope contract::

        {
            "caller_identity": "svc-underwriting",
            "auth_token": "<hex-hmac>",
            "auth_timestamp": <unix-epoch-seconds>,
            "tenant_id": "tenant-42",
            ...
        }

    The presented token MUST equal ``HMAC(shared_secret, f"{caller_identity}|{auth_timestamp}")``
    and ``auth_timestamp`` MUST be within ``clock_skew_seconds`` of server time.
    """

    def __init__(
        self,
        shared_secret: bytes,
        *,
        clock_skew_seconds: int = 300,
        allowed_callers: set[str] | None = None,
    ) -> None:
        if not isinstance(shared_secret, (bytes, bytearray)) or len(shared_secret) < 16:
            raise ValueError("shared_secret must be at least 16 bytes of entropy.")
        self._secret = bytes(shared_secret)
        self._clock_skew = int(clock_skew_seconds)
        self._allowed = allowed_callers

    def verify(self, caller_identity: str, envelope: dict) -> VerifiedIdentity:
        if not caller_identity:
            raise IdentityVerificationError("caller_identity is missing.")
        if self._allowed is not None and caller_identity not in self._allowed:
            raise IdentityVerificationError(f"caller_identity {caller_identity!r} not in allowlist.")

        token = envelope.get("auth_token")
        ts = envelope.get("auth_timestamp")
        if not isinstance(token, str) or not token:
            raise IdentityVerificationError("auth_token missing.")
        if not isinstance(ts, (int, float)):
            raise IdentityVerificationError("auth_timestamp missing or not numeric.")

        now = time.time()
        if abs(now - float(ts)) > self._clock_skew:
            raise IdentityVerificationError(
                f"auth_timestamp outside clock skew window (skew={self._clock_skew}s)."
            )

        expected = hmac.new(
            self._secret,
            f"{caller_identity}|{int(ts)}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, token):
            raise IdentityVerificationError("auth_token does not match expected HMAC.")

        tenant_id = str(envelope.get("tenant_id") or caller_identity)
        scopes_raw = envelope.get("scopes") or ()
        if isinstance(scopes_raw, str):
            scopes: tuple[str, ...] = tuple(s.strip() for s in scopes_raw.split(",") if s.strip())
        elif isinstance(scopes_raw, (list, tuple)):
            scopes = tuple(str(s) for s in scopes_raw)
        else:
            scopes = ()

        return VerifiedIdentity(caller_id=caller_identity, tenant_id=tenant_id, scopes=scopes)


__all__ = [
    "IdentityVerificationError",
    "IdentityVerifier",
    "NoopIdentityVerifier",
    "SharedSecretIdentityVerifier",
    "VerifiedIdentity",
]
