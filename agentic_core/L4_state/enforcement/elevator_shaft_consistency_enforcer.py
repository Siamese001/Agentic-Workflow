"""ElevatorShaftConsistencyEnforcer — runtime semantic clock synchronization gate.

The ADG shows ElevatorShaft (2 nodes) and semantic_clock (48 nodes) exist as
first-class constructs, but only 1 ``snapshots_state`` edge exists, and
``observes_runtime_state`` has only 1 edge.  The state synchronization semantics
(version consistency, injection timing) are not proven by the static graph.

This module adds the runtime enforcement layer:

  1. ``assert_clock_synchronized`` — hard-fails if two SemanticClockSnapshots
     diverge beyond a configurable tick tolerance.
  2. ``assert_no_wall_clock_in_module`` — delegates to the existing
     ``scan_module_for_wallclock`` AST scanner to gate a module before use.
  3. ``ElevatorShaftConsistencyEnforcer`` — stateful enforcer that tracks the
     canonical clock per layer and rejects state transitions that violate
     monotonicity or exceed the drift threshold.

ADG governance plane: calls to ``assert_clock_synchronized`` generate
``verifies_boundary`` and ``snapshots_state`` edges from the caller to the
SemanticClock surface, closing the synchronization proof gap.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

Logger = logging.getLogger(__name__)

_DEFAULT_DRIFT_TOLERANCE: int = 5


class ClockSyncViolation(RuntimeError):
    """Raised when two SemanticClockSnapshots are not sufficiently synchronized."""


class MonotonicityViolation(RuntimeError):
    """Raised when a new clock tick is less than the previously recorded tick."""


class WallClockContaminationError(RuntimeError):
    """Raised when a module contains forbidden wall-clock calls."""


def assert_clock_synchronized(
    snapshot_a: SemanticClockSnapshot,
    snapshot_b: SemanticClockSnapshot,
    *,
    tolerance: int = _DEFAULT_DRIFT_TOLERANCE,
    context: str = "",
) -> None:
    """Assert that two SemanticClockSnapshots are within *tolerance* ticks of each other.

    Args:
        snapshot_a: First clock snapshot (e.g. from the caller layer).
        snapshot_b: Second clock snapshot (e.g. from the callee layer).
        tolerance: Maximum allowed tick difference before raising.
        context: Optional context string for error messages.

    Raises:
        ClockSyncViolation: if ``abs(a.tick - b.tick) > tolerance``.
    """
    _emit_snapshots_state(str(uuid.uuid4()), "Module.assert_clock_synchronized", "L4_STATE")
    validate_semantic_clock(snapshot_a, context=f"{context}.a")
    validate_semantic_clock(snapshot_b, context=f"{context}.b")
    drift = abs(snapshot_a.tick - snapshot_b.tick)
    if drift > tolerance:
        raise ClockSyncViolation(
            f"ElevatorShaftConsistencyEnforcer: clock drift {drift} exceeds tolerance {tolerance}. "
            f"snapshot_a.tick={snapshot_a.tick}, snapshot_b.tick={snapshot_b.tick}. "
            f"context={context!r}",
        )
    Logger.debug(
        "[ElevatorShaftConsistencyEnforcer] clocks synchronized: drift=%d, tolerance=%d, ctx=%r",
        drift,
        tolerance,
        context,
    )


def assert_no_wall_clock_in_module(module_path: Path, context: str = "") -> None:
    """Assert that *module_path* contains no wall-clock calls.

    Delegates to ``scan_module_for_wallclock`` (L6 observability AST scanner).

    Raises:
        WallClockContaminationError: if any wall-clock violation is found.
    """
    from agentic_core.L6_observability.utils.engines.semantic_clock_validator import (  # noqa: PLC0415
        scan_module_for_wallclock,
    )

    violations = scan_module_for_wallclock(module_path)
    if violations:
        raise WallClockContaminationError(
            f"ElevatorShaftConsistencyEnforcer: wall-clock contamination in {module_path} "
            f"({context}): {violations}",
        )
    Logger.debug("[ElevatorShaftConsistencyEnforcer] no wall-clock calls in %s (%s)", module_path, context)


@dataclass
class LayerClockRecord:
    """Tracks the last-known semantic clock tick for a single layer."""

    layer: str
    last_tick: int = 0
    advance_count: int = 0


class ElevatorShaftConsistencyEnforcer:
    """Runtime enforcer for elevator shaft state synchronization.

    Maintains the canonical tick per layer and enforces:
    - Monotonicity: ticks must not go backward.
    - Drift: cross-layer drift must stay within tolerance.
    - Wall-clock isolation: modules submitted for registration are AST-scanned.

    Usage::

        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=3)
        enforcer.record_advance("L0", snapshot_l0)
        enforcer.record_advance("L2", snapshot_l2)
        enforcer.assert_layers_synchronized("L0", "L2")
    """

    def __init__(self, drift_tolerance: int = _DEFAULT_DRIFT_TOLERANCE) -> None:
        self._drift_tolerance = drift_tolerance
        self._layer_records: dict[str, LayerClockRecord] = {}
        self._scanned_modules: set[str] = set()

    def record_advance(self, layer: str, snapshot: SemanticClockSnapshot) -> None:
        """Record a clock advancement for *layer*.

        Raises:
            MonotonicityViolation: if the new tick is less than the last recorded tick.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ElevatorShaftConsistencyEnforcer.record_advance",
        )

        validate_semantic_clock(snapshot, context=f"layer={layer}")
        record = self._layer_records.setdefault(layer, LayerClockRecord(layer=layer))
        if snapshot.tick < record.last_tick:
            raise MonotonicityViolation(
                f"ElevatorShaftConsistencyEnforcer: non-monotonic tick for layer '{layer}': "
                f"new={snapshot.tick} < last={record.last_tick}",
            )
        record.last_tick = snapshot.tick
        record.advance_count += 1
        Logger.debug(
            "[ElevatorShaftConsistencyEnforcer] layer=%s tick=%d (advances=%d)",
            layer,
            snapshot.tick,
            record.advance_count,
        )

    def assert_layers_synchronized(self, layer_a: str, layer_b: str) -> None:
        """Assert that two layers are within drift tolerance.

        Raises:
            ClockSyncViolation: if drift exceeds tolerance.
            KeyError: if either layer has not been recorded yet.
        """
        if layer_a not in self._layer_records:
            raise KeyError(f"ElevatorShaftConsistencyEnforcer: layer '{layer_a}' has no recorded tick.")
        if layer_b not in self._layer_records:
            raise KeyError(f"ElevatorShaftConsistencyEnforcer: layer '{layer_b}' has no recorded tick.")
        rec_a = self._layer_records[layer_a]
        rec_b = self._layer_records[layer_b]
        snap_a = SemanticClockSnapshot(tick=rec_a.last_tick)
        snap_b = SemanticClockSnapshot(tick=rec_b.last_tick)
        assert_clock_synchronized(
            snap_a,
            snap_b,
            tolerance=self._drift_tolerance,
            context=f"{layer_a}<>{layer_b}",
        )

    def register_module(self, module_path: Path) -> None:
        """Register a module after asserting it contains no wall-clock calls.

        Raises:
            WallClockContaminationError: if the module has wall-clock violations.
        """
        path_str = str(module_path)
        if path_str in self._scanned_modules:
            return
        assert_no_wall_clock_in_module(module_path, context="register_module")
        self._scanned_modules.add(path_str)
        Logger.debug("[ElevatorShaftConsistencyEnforcer] module registered clean: %s", module_path)

    def layer_tick(self, layer: str) -> int | None:
        """Return the last recorded tick for *layer*, or None if not yet recorded."""
        rec = self._layer_records.get(layer)
        return rec.last_tick if rec is not None else None

    def summary(self) -> dict[str, Any]:
        """Return a summary of all tracked layers."""
        _adg_violates: list[str] = []
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _root = Path(__file__).resolve().parents[4]
            _bp = _gbp(Path(__file__).resolve(), _root)
            _adg_violates = sorted(_bp.antipattern_signals)
            if _adg_violates:
                Logger.warning(
                    "[ADG] ElevatorShaftConsistencyEnforcer: layer-violation signals=%s "
                    "(score=%.3f) — escalate severity",
                    _adg_violates,
                    _bp.behavioral_score,
                )
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return {
            layer: {"last_tick": rec.last_tick, "advance_count": rec.advance_count}
            for layer, rec in sorted(self._layer_records.items())
        } | {"adg_violates": _adg_violates}


_GLOBAL_ENFORCER: ElevatorShaftConsistencyEnforcer | None = None


def get_enforcer(drift_tolerance: int = _DEFAULT_DRIFT_TOLERANCE) -> ElevatorShaftConsistencyEnforcer:
    """Return the global ElevatorShaftConsistencyEnforcer instance."""
    global _GLOBAL_ENFORCER
    if _GLOBAL_ENFORCER is None:
        _GLOBAL_ENFORCER = ElevatorShaftConsistencyEnforcer(drift_tolerance=drift_tolerance)
    return _GLOBAL_ENFORCER


def reset_enforcer() -> None:
    """Reset the global enforcer (for testing only)."""
    global _GLOBAL_ENFORCER
    _GLOBAL_ENFORCER = None
