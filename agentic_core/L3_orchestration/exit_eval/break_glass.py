"""Break-glass emergency override — X3E disposition.

Hardening addendum H3 contract:

- Only an identity holding ``break_glass`` capability token may invoke.
- Invocation requires a written justification and an expiry (<= 60 min).
- Break-glass CANNOT bypass X1A (policy), X1C hard sub-gates
  (sandbox/mutation auth), or UWG verification (U1-U3). It MAY bypass
  X1B/X1D/X1E/X1F/X1G.
- Every invocation creates an immutable audit row AND routes through
  X3E — never silently reuses X3D.
- Break-glass runs may not commit to customer-facing L4 stores without a
  second-operator ratification (enforced at the UWG boundary, not here).
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


class BreakGlassError(RuntimeError):
    """Raised when break-glass preconditions are not met."""


BYPASS_ALLOWED_GATES = frozenset({"X1B", "X1D", "X1E", "X1F", "X1G"})
BYPASS_FORBIDDEN_GATES = frozenset({"X1A", "X1C"})
MAX_EXPIRY_SECONDS = 60 * 60  # 1 hour hard cap per H3.2


@dataclass(frozen=True)
class BreakGlassToken:
    """A break-glass capability token.

    Production tokens come from the repo's auth plane. A token's
    ``capabilities`` MUST include ``"break_glass"`` for this module to
    accept it.
    """

    identity: str
    capabilities: frozenset[str]
    issued_at: float
    expires_at: float

    def is_valid(self, *, now: float) -> bool:
        return "break_glass" in self.capabilities and self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class BreakGlassInvocation:
    """Result of a successful break-glass authorization."""

    audit_id: str
    identity: str
    justification: str
    bypassed_gates: tuple[str, ...]
    invoked_at: float
    expires_at: float


@dataclass(frozen=True)
class BreakGlassAuditRow:
    """Immutable audit record per H3 invariant."""

    audit_id: str
    identity: str
    justification: str
    bypassed_gates: tuple[str, ...]
    invoked_at: float
    expires_at: float
    run_id: str = ""
    extras: dict[str, object] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "audit_id": self.audit_id,
                "identity": self.identity,
                "justification": self.justification,
                "bypassed_gates": list(self.bypassed_gates),
                "invoked_at": self.invoked_at,
                "expires_at": self.expires_at,
                "run_id": self.run_id,
                **self.extras,
            },
            sort_keys=True,
        )


class BreakGlassAuthority:
    """Authorization + audit for X3E invocations.

    Usage:

        authority = BreakGlassAuthority(audit_sink=jsonl_audit_sink(path))
        inv = authority.invoke(
            token=tok,
            justification="production outage, refund processing down",
            bypassed_gates=("X1F",),
            run_id=run_id,
            expiry_seconds=900,
        )
    """

    def __init__(
        self,
        audit_sink: Callable[[BreakGlassAuditRow], None],
        *,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._audit_sink = audit_sink
        self._now = now or time.time

    def invoke(
        self,
        *,
        token: BreakGlassToken,
        justification: str,
        bypassed_gates: tuple[str, ...],
        run_id: str,
        expiry_seconds: int,
    ) -> BreakGlassInvocation:
        now = self._now()
        if not token.is_valid(now=now):
            raise BreakGlassError("break-glass token missing capability or expired")
        if not justification.strip():
            raise BreakGlassError("break-glass requires non-empty justification")
        if expiry_seconds <= 0 or expiry_seconds > MAX_EXPIRY_SECONDS:
            raise BreakGlassError(f"break-glass expiry must be in (0, {MAX_EXPIRY_SECONDS}] seconds")

        bypass_set = frozenset(bypassed_gates)
        forbidden = bypass_set & BYPASS_FORBIDDEN_GATES
        if forbidden:
            raise BreakGlassError(
                f"break-glass cannot bypass gates {sorted(forbidden)}: "
                "X1A and X1C hard sub-gates must hold under emergency (H3.1)"
            )
        unknown = bypass_set - BYPASS_ALLOWED_GATES
        if unknown:
            raise BreakGlassError(f"break-glass received unknown gate names: {sorted(unknown)}")

        audit_id = f"bg-{secrets.token_hex(8)}"
        expires_at = now + expiry_seconds
        row = BreakGlassAuditRow(
            audit_id=audit_id,
            identity=token.identity,
            justification=justification.strip(),
            bypassed_gates=tuple(sorted(bypass_set)),
            invoked_at=now,
            expires_at=expires_at,
            run_id=run_id,
        )
        # Audit write MUST succeed or invocation fails closed — we refuse
        # to issue a break-glass that lacks a persistent audit trail.
        try:
            self._audit_sink(row)
        except (OSError, RuntimeError) as exc:
            raise BreakGlassError(f"break-glass audit sink failed, invocation refused: {exc}") from exc

        return BreakGlassInvocation(
            audit_id=audit_id,
            identity=token.identity,
            justification=row.justification,
            bypassed_gates=row.bypassed_gates,
            invoked_at=now,
            expires_at=expires_at,
        )


def jsonl_audit_sink(path: str | Path) -> Callable[[BreakGlassAuditRow], None]:
    """File-backed immutable-append sink for break-glass audit rows."""
    target = Path(path)

    def _write(row: BreakGlassAuditRow) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(row.to_json())
            fh.write("\n")

    return _write


__all__ = [
    "BYPASS_ALLOWED_GATES",
    "BYPASS_FORBIDDEN_GATES",
    "BreakGlassAuditRow",
    "BreakGlassAuthority",
    "BreakGlassError",
    "BreakGlassInvocation",
    "BreakGlassToken",
    "MAX_EXPIRY_SECONDS",
    "jsonl_audit_sink",
]
