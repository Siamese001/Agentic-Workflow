"""L5 Exit Kill-Switch primitive (ADR-042).

In-memory store + hit resolver. Every activate / hit / release emits an
audit-ledger row conforming to
``config/schemas/kill_switch_audit.schema.json``.

This module is intentionally small and process-local. A durable audit-
ledger writer is a separate follow-up.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Literal, Mapping

Event = Literal["activate", "hit", "release"]


@dataclass(frozen=True)
class KillSwitchActivation:
    """A single active kill-switch entry."""

    activation_id: str
    scope: str
    reason: str
    operator: str
    activated_at_utc: str
    ttl_seconds: int | None = None
    on_hit: Literal["deny_reroute", "escalate"] = "deny_reroute"
    released_at_utc: str | None = None


@dataclass(frozen=True)
class KillSwitchHit:
    """Result of testing a request context against active kill-switches."""

    hit: bool
    activation_id: str | None = None
    scope: str | None = None
    reason: str | None = None
    on_hit: Literal["deny_reroute", "escalate"] = "deny_reroute"


AuditSink = Callable[[Mapping[str, object]], None]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _matches_scope(scope_expr: str, context: Mapping[str, str | None]) -> bool:
    """Evaluate a scope expression against a request context.

    Scope grammar (ADR-042 §2.1):
      fleet
      tenant:<tenant_id>
      route:<route_class>
      tool:<tool_name>
      agent:<agent_class>
      cost_class:<class_name>
    """
    if scope_expr == "fleet":
        return True
    if ":" not in scope_expr:
        return False
    kind, value = scope_expr.split(":", 1)
    kind = kind.strip()
    value = value.strip()
    if kind == "tenant":
        return context.get("tenant") == value
    if kind == "route":
        return context.get("route_class") == value
    if kind == "tool":
        tools = context.get("tools")
        if isinstance(tools, str):
            return value in tools.split(",")
        return False
    if kind == "agent":
        return context.get("agent_class") == value
    if kind == "cost_class":
        return context.get("cost_class") == value
    return False


class KillSwitchStore:
    """Process-local store of active kill-switches."""

    def __init__(self, audit_sink: AuditSink | None = None) -> None:
        self._lock = threading.Lock()
        self._active: dict[str, KillSwitchActivation] = {}
        self._audit_sink = audit_sink

    def _emit(self, payload: Mapping[str, object]) -> None:
        if self._audit_sink is None:
            return
        try:
            self._audit_sink(payload)
        except (
            OSError,
            ValueError,
        ):  # guardian: allow-silent-swallow -- audit-sink failures never block runtime kill-switch decisions; observability is best-effort here
            pass

    def activate(
        self,
        *,
        scope: str,
        reason: str,
        operator: str,
        ttl_seconds: int | None = None,
        on_hit: Literal["deny_reroute", "escalate"] = "deny_reroute",
        policy_snapshot: str | None = None,
    ) -> KillSwitchActivation:
        if not scope or not reason or not operator:
            raise ValueError("scope, reason, operator are required non-empty strings")
        entry = KillSwitchActivation(
            activation_id=f"ks-{uuid.uuid4().hex}",
            scope=scope,
            reason=reason,
            operator=operator,
            activated_at_utc=_utcnow(),
            ttl_seconds=ttl_seconds,
            on_hit=on_hit,
        )
        with self._lock:
            self._active[entry.activation_id] = entry
        self._emit(
            {
                "schema_version": 1,
                "event": "activate",
                "scope": entry.scope,
                "reason": entry.reason,
                "operator": entry.operator,
                "ttl_seconds": entry.ttl_seconds,
                "activated_at": entry.activated_at_utc,
                "released_at": None,
                "hit_request_id": None,
                "hit_trace_id": None,
                "policy_snapshot": policy_snapshot,
                "activation_ref": entry.activation_id,
            }
        )
        return entry

    def release(
        self,
        activation_id: str,
        *,
        operator: str = "system",
        policy_snapshot: str | None = None,
    ) -> KillSwitchActivation | None:
        with self._lock:
            entry = self._active.pop(activation_id, None)
        if entry is None:
            return None
        released = KillSwitchActivation(
            activation_id=entry.activation_id,
            scope=entry.scope,
            reason=entry.reason,
            operator=entry.operator,
            activated_at_utc=entry.activated_at_utc,
            ttl_seconds=entry.ttl_seconds,
            on_hit=entry.on_hit,
            released_at_utc=_utcnow(),
        )
        self._emit(
            {
                "schema_version": 1,
                "event": "release",
                "scope": released.scope,
                "reason": released.reason,
                "operator": operator,
                "ttl_seconds": released.ttl_seconds,
                "activated_at": released.activated_at_utc,
                "released_at": released.released_at_utc,
                "hit_request_id": None,
                "hit_trace_id": None,
                "policy_snapshot": policy_snapshot,
                "activation_ref": released.activation_id,
            }
        )
        return released

    def hit(
        self,
        context: Mapping[str, str | None],
        *,
        request_id: str | None = None,
        trace_id: str | None = None,
        policy_snapshot: str | None = None,
    ) -> KillSwitchHit:
        """Return the first matching activation (if any) and emit a hit row."""
        with self._lock:
            snapshot = tuple(self._active.values())
        for entry in snapshot:
            if _matches_scope(entry.scope, context):
                self._emit(
                    {
                        "schema_version": 1,
                        "event": "hit",
                        "scope": entry.scope,
                        "reason": entry.reason,
                        "operator": entry.operator,
                        "ttl_seconds": entry.ttl_seconds,
                        "activated_at": entry.activated_at_utc,
                        "released_at": None,
                        "hit_request_id": request_id,
                        "hit_trace_id": trace_id,
                        "policy_snapshot": policy_snapshot,
                        "activation_ref": entry.activation_id,
                    }
                )
                return KillSwitchHit(
                    hit=True,
                    activation_id=entry.activation_id,
                    scope=entry.scope,
                    reason=entry.reason,
                    on_hit=entry.on_hit,
                )
        return KillSwitchHit(hit=False)

    def active_activations(self) -> tuple[KillSwitchActivation, ...]:
        with self._lock:
            return tuple(self._active.values())


__all__ = [
    "AuditSink",
    "Event",
    "KillSwitchActivation",
    "KillSwitchHit",
    "KillSwitchStore",
]
