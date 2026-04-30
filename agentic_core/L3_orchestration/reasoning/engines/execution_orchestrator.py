"""Execution orchestrator shim with deterministic state handling.

W5 P5.3 (2026-04-30, plan adg-three-bucket-unified-c4f8e2): added
``populate_blast_radius_cache`` pilot — the first L2/L3 consumer of the
P3.3 graph-layer surface per ADR-079. Feature-flagged OFF by default
(``L2_PILOT_BLAST_RADIUS_ENABLED``) so the pilot cannot regress current
runtime behavior. See ADR-079 for the L2 agent graph-layer integration
contract (latency budget, fallback rules, layer-gravity invariant).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration: this orchestrator shim does not read
# analytical views directly. When the P5.3 pilot is enabled it delegates to
# ``tools.adg.core.service.ADGService.get_blast_radius`` which itself is
# inventory-mode (reads the mv_* projection, not proof_view). So this file
# stays ``inventory`` — consistent with ADR-079's layer-gravity rule that L2
# consumers are permitted downward read-only consumption.
__adg_consumer_mode__ = "inventory"

import logging
import os
from copy import deepcopy
from dataclasses import dataclass, field
from time import time
from typing import Any

logger = logging.getLogger(__name__)

# Feature flag env var (default OFF). When "1", the pilot path is active.
# Rollback: unset the env var or set to anything other than "1".
_PILOT_FLAG_ENV: str = "L2_PILOT_BLAST_RADIUS_ENABLED"


def _coerce_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict or None")
    return dict(payload)


def _pilot_enabled() -> bool:
    """Return True iff the W5 P5.3 blast-radius pilot is active.

    Resolved at call time (not at import time) so tests can flip the env var
    per-case via ``monkeypatch.setenv`` without reloading the module.
    """
    return os.environ.get(_PILOT_FLAG_ENV, "0") == "1"


@dataclass
class ExecutionOrchestrator:
    """Small placeholder object used by import-and-contract tests.

    The implementation stays intentionally compact but provides deterministic
    merge semantics, immutable snapshots, and a bounded run history that is
    useful when these shims are exercised outside the test suite.
    """

    state: dict[str, Any] = field(default_factory=dict)
    max_history: int = 50
    run_count: int = 0
    _history: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = _coerce_payload(payload)
        self.run_count += 1
        if normalized:
            self.state.update(normalized)
        self.state["run_count"] = self.run_count
        snapshot = self.snapshot()
        self._history.append({"timestamp": time(), "state": snapshot})
        if len(self._history) > max(1, int(self.max_history)):
            self._history = self._history[-int(self.max_history) :]
        return snapshot

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.state)

    def history(self) -> list[dict[str, Any]]:
        return deepcopy(self._history)

    def reset(self) -> None:
        self.state.clear()
        self.run_count = 0
        self._history.clear()

    # ------------------------------------------------------------------
    # W5 P5.3 pilot — blast-radius-aware cache populate (feature-flagged)
    # ------------------------------------------------------------------
    def populate_blast_radius_cache(
        self,
        target_node_id: str,
        *,
        hops: int = 2,
        service: Any = None,
    ) -> dict[str, Any]:
        """Populate an internal blast-radius cache entry for ``target_node_id``.

        This is the W5 P5.3 pilot consumer of the P3.3 graph-layer surface,
        conforming to ADR-079's L2 agent integration contract.

        Behavior:
            * Feature-flagged via env var ``L2_PILOT_BLAST_RADIUS_ENABLED=1``.
              When OFF (default): returns an empty dict without touching ADG
              — preserves pre-P5.3 runtime behavior exactly.
            * When ON: queries
              ``tools.adg.core.service.ADGService.get_blast_radius`` (the
              P3.3-exposed MV surface) with ``hops`` transitive depth.
              Result is cached under
              ``self.state["blast_radius_cache"][target_node_id]``.
            * Any exception from the ADG path is logged and returns an
              empty dict — the L2/L3 caller MUST stay live on ADG failure.

        Args:
            target_node_id: ADG node id (e.g. ``"ADG::Symbol::pkg.mod.func"``
                            or an integer-string id).
            hops: Transitive depth. Default 2 matches the MCP tool default.
            service: Optional pre-built ``ADGService`` (tests inject here).
                     When None, a service is constructed lazily inside the
                     guarded try/except.

        Returns:
            The cached blast-radius dict on success, or ``{}`` on any of:
            feature-flag OFF, service construction failure, query failure.
        """
        if not _pilot_enabled():
            # Explicit no-op — the pilot default is OFF so current runtime
            # behavior is unchanged.
            return {}

        cache: dict[str, Any] = self.state.setdefault("blast_radius_cache", {})

        try:
            if service is None:
                # Lazy import: avoids paying the ADGService import cost in
                # every runtime that doesn't enable the pilot.
                from tools.adg.core.service import ADGService  # noqa: PLC0415
                service = ADGService()
            response = service.get_blast_radius(target_node_id, hops=hops)
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            # ADR-079: any ADG failure must not leak to the caller. Log,
            # degrade to empty dict, return.
            logger.warning(
                "P5.3 blast-radius pilot: ADG query failed for %s (hops=%d): %s",
                target_node_id, hops, exc,
            )
            return {}

        # ``response`` is an ``ADGResponse`` dataclass; callers likely only
        # care about its ``.data`` payload plus provenance. Normalize to a
        # plain dict so the cache entry has no import dependency.
        payload: dict[str, Any] = {
            "node_id": target_node_id,
            "hops": hops,
            "data": getattr(response, "data", response),
            "backend_used": getattr(response, "backend_used", "unknown"),
        }
        cache[target_node_id] = payload
        return payload


def validate_execution_orchestrator() -> bool:
    probe = ExecutionOrchestrator()
    result = probe.run({"status": "ok"})
    return result.get("status") == "ok" and len(probe.history()) == 1


__all__ = ["ExecutionOrchestrator", "validate_execution_orchestrator"]
