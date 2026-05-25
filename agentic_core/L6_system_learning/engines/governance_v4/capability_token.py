"""L5 Governance v4 — Capability Token Minter + Sandbox Envelope Minter.

Per Governance v4 G2/Decision Rail, every CERTIFY decision binds a
``capability_token`` carrying a scoped, TTL-bounded grant plus a
``sandbox_envelope``. This module mints both deterministically.

Reference
---------
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` —
G-06, G-07, G-09, G-19, ``capability_token.schema.md``.

KPI surface (publish via UnifiedKPIBoard)
-----------------------------------------
- ``CAPABILITY_TOKEN_TTL_VIOLATIONS`` (count, EQ 0)
- ``CAPABILITY_TOKEN_SCOPE_VIOLATIONS`` (count, EQ 0)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PrincipalChain:
    """Identity chain bound to every capability token (v4 G-04)."""

    invoking_user: str
    agent_id: str
    parent_agent_id: str | None
    delegation_depth: int
    scope: str


@dataclass(frozen=True)
class CapabilityToken:
    """Scoped, TTL-bounded execution grant.

    Fields encode the v4 Decision Rail "bind capability_token" payload.
    """

    token_id: str
    scope: str
    ttl_seconds: float
    issued_at_epoch: float
    single_use: bool
    principal_chain: PrincipalChain
    connector_allowlist: tuple[str, ...]
    plan_digest: str
    permission_ladder: tuple[str, ...]
    standards_fingerprint: str

    @property
    def expires_at_epoch(self) -> float:
        return self.issued_at_epoch + self.ttl_seconds


@dataclass(frozen=True)
class SandboxEnvelope:
    """Companion to capability token — scopes the execution sandbox (v4 G-19)."""

    envelope_id: str
    token_id: str
    fs_writable_paths: tuple[str, ...]
    network_allowlist: tuple[str, ...]
    cpu_seconds_max: float
    memory_bytes_max: int
    egress_inspection_required: bool


def _stable_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class CapabilityTokenMinter:
    """Mint capability tokens after CERTIFY.

    The minter does NOT enforce TTL/scope at use-time — that's the
    responsibility of upstream callers and the runtime. The minter tracks
    *self-reported violations* via :meth:`mark_ttl_violation` and
    :meth:`mark_scope_violation` and publishes the corresponding KPIs.
    """

    DEFAULT_TTL_SECONDS: float = 600.0  # 10 minutes
    MAX_TTL_SECONDS: float = 4 * 3600.0  # 4 hours hard ceiling

    def __init__(self) -> None:
        self._ttl_violations: int = 0
        self._scope_violations: int = 0

    def mint(
        self,
        *,
        scope: str,
        principal_chain: PrincipalChain,
        connector_allowlist: Sequence[str],
        plan_digest: str,
        permission_ladder: Sequence[str],
        standards_fingerprint: str,
        ttl_seconds: float | None = None,
        single_use: bool = True,
        issued_at_epoch: float | None = None,
    ) -> CapabilityToken:
        """Construct a content-addressed capability token.

        Raises ``ValueError`` if ``ttl_seconds`` exceeds :attr:`MAX_TTL_SECONDS`
        or ``scope`` is empty.
        """
        if not scope:
            raise ValueError("scope must be non-empty")
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS
        if ttl <= 0 or ttl > self.MAX_TTL_SECONDS:
            raise ValueError(
                f"ttl_seconds={ttl} out of range (0, {self.MAX_TTL_SECONDS}]"
            )
        ts = issued_at_epoch if issued_at_epoch is not None else time.time()
        payload = {
            "scope": scope,
            "ttl_seconds": ttl,
            "issued_at_epoch": ts,
            "single_use": single_use,
            "principal_chain": {
                "invoking_user": principal_chain.invoking_user,
                "agent_id": principal_chain.agent_id,
                "parent_agent_id": principal_chain.parent_agent_id,
                "delegation_depth": principal_chain.delegation_depth,
                "scope": principal_chain.scope,
            },
            "connector_allowlist": sorted(connector_allowlist),
            "plan_digest": plan_digest,
            "permission_ladder": list(permission_ladder),
            "standards_fingerprint": standards_fingerprint,
        }
        token_id = _stable_hash(payload)
        return CapabilityToken(
            token_id=token_id,
            scope=scope,
            ttl_seconds=ttl,
            issued_at_epoch=ts,
            single_use=single_use,
            principal_chain=principal_chain,
            connector_allowlist=tuple(sorted(connector_allowlist)),
            plan_digest=plan_digest,
            permission_ladder=tuple(permission_ladder),
            standards_fingerprint=standards_fingerprint,
        )

    def mark_ttl_violation(self) -> None:
        """Record one expired-token use."""
        self._ttl_violations += 1

    def mark_scope_violation(self) -> None:
        """Record one out-of-scope token use."""
        self._scope_violations += 1

    @property
    def violation_counts(self) -> tuple[int, int]:
        """Return ``(ttl_violations, scope_violations)``."""
        return (self._ttl_violations, self._scope_violations)

    def reset_violation_counts(self) -> None:
        self._ttl_violations = 0
        self._scope_violations = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from agentic_core.L6_system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ts = time.time()
            board.record(V7KPISample(
                name=V7KPIName.CAPABILITY_TOKEN_TTL_VIOLATIONS,
                value=float(self._ttl_violations),
                timestamp=ts, source="capability_token_minter",
                metadata={"count": self._ttl_violations},
            ))
            board.record(V7KPISample(
                name=V7KPIName.CAPABILITY_TOKEN_SCOPE_VIOLATIONS,
                value=float(self._scope_violations),
                timestamp=ts, source="capability_token_minter",
                metadata={"count": self._scope_violations},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break minting
            logger.warning("v7_kpi_capability_token_violations_failed: %s", exc)


class SandboxEnvelopeMinter:
    """Mint a sandbox envelope alongside a capability token."""

    def mint(
        self,
        *,
        token: CapabilityToken,
        fs_writable_paths: Sequence[str] = (),
        network_allowlist: Sequence[str] = (),
        cpu_seconds_max: float = 60.0,
        memory_bytes_max: int = 512 * 1024 * 1024,
        egress_inspection_required: bool = True,
    ) -> SandboxEnvelope:
        payload = {
            "token_id": token.token_id,
            "fs_writable_paths": sorted(fs_writable_paths),
            "network_allowlist": sorted(network_allowlist),
            "cpu_seconds_max": cpu_seconds_max,
            "memory_bytes_max": memory_bytes_max,
            "egress_inspection_required": egress_inspection_required,
        }
        envelope_id = _stable_hash(payload)
        return SandboxEnvelope(
            envelope_id=envelope_id,
            token_id=token.token_id,
            fs_writable_paths=tuple(sorted(fs_writable_paths)),
            network_allowlist=tuple(sorted(network_allowlist)),
            cpu_seconds_max=cpu_seconds_max,
            memory_bytes_max=memory_bytes_max,
            egress_inspection_required=egress_inspection_required,
        )


__all__ = [
    "PrincipalChain",
    "CapabilityToken",
    "SandboxEnvelope",
    "CapabilityTokenMinter",
    "SandboxEnvelopeMinter",
]
