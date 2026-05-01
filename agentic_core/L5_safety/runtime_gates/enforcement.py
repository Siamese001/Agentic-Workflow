"""Runtime-gate enforcement bridge for production layers.

Provides the stable API that L0/L1/L2/L3/L5 composition roots call when
they want runtime gates evaluated at a layer boundary. Wraps
``runtime_gates.dispatch.run_layer`` with explicit halt semantics, a
rollout-mode switch, and a layer-entry decorator.

Modes (env ``RUNTIME_GATES_ENFORCEMENT_MODE``):
- ``strict`` — raise ``RuntimeGateHaltError`` on halt; production safety.
- ``soft``   — log halt as warning, return ``MeshResult``; for graceful rollouts.
- ``audit``  — always log result, never raise; default during onboarding.
- ``off``    — no-op, return empty MeshResult; for emergency disable.

Per-layer disable: ``RUNTIME_GATES_DISABLED_LAYERS=L0,L3`` skips those layers.
"""

from __future__ import annotations

import functools
import logging
import os
from collections.abc import Callable
from enum import Enum
from typing import Any

from agentic_core.L5_safety.runtime_gates.dispatch import run_layer
from agentic_core.L5_safety.runtime_gates.orchestrator import MeshResult
from agentic_core.L5_safety.runtime_gates.types import GateContext

logger = logging.getLogger(__name__)


class EnforcementMode(str, Enum):
    """Bounded enforcement modes."""

    STRICT = "strict"
    SOFT = "soft"
    AUDIT = "audit"
    OFF = "off"


_DEFAULT_MODE = EnforcementMode.AUDIT
_MODE_ENV = "RUNTIME_GATES_ENFORCEMENT_MODE"
_DISABLED_LAYERS_ENV = "RUNTIME_GATES_DISABLED_LAYERS"


class RuntimeGateHaltError(RuntimeError):
    """Raised in strict mode when the gate mesh halts.

    Carries the full ``MeshResult`` so callers can introspect the halting
    decision, reason codes, and the partial decision log.
    """

    def __init__(self, layer: str, result: MeshResult) -> None:
        self.layer = layer
        self.result = result
        last = result.decisions[-1] if result.decisions else None
        gate_id = result.halted_at or (last.gate_id if last else "unknown")
        codes = list(last.reason_codes) if last else []
        super().__init__(
            f"runtime gate halt: layer={layer!r} gate={gate_id} reason={result.halt_reason!r} codes={codes}"
        )


def _resolve_mode(explicit: EnforcementMode | str | None = None) -> EnforcementMode:
    """Mode resolution: explicit arg > env var > default."""
    if explicit is not None:
        if isinstance(explicit, EnforcementMode):
            return explicit
        try:
            return EnforcementMode(str(explicit).lower())
        except ValueError as exc:
            raise ValueError(
                f"unknown enforcement mode {explicit!r}; valid: {[m.value for m in EnforcementMode]}"
            ) from exc
    raw = os.environ.get(_MODE_ENV, "")
    if not raw:
        return _DEFAULT_MODE
    try:
        return EnforcementMode(raw.lower())
    except ValueError:
        logger.warning(
            "runtime-gates enforcement: unknown mode %r in %s; falling back to %s",
            raw,
            _MODE_ENV,
            _DEFAULT_MODE.value,
        )
        return _DEFAULT_MODE


def _layer_is_disabled(layer: str) -> bool:
    """Per-layer disable via ``RUNTIME_GATES_DISABLED_LAYERS``."""
    raw = os.environ.get(_DISABLED_LAYERS_ENV, "")
    if not raw:
        return False
    disabled = {x.strip() for x in raw.split(",") if x.strip()}
    return layer in disabled


def enforce_layer(
    layer: str,
    ctx: GateContext,
    *,
    mode: EnforcementMode | str | None = None,
) -> MeshResult:
    """Invoke runtime gates for a layer with mode-aware halt semantics.

    Args:
        layer: One of the ``LAYER_*`` constants from
            ``runtime_gates.dispatch``.
        ctx: The shared ``GateContext`` populated by the calling layer.
        mode: Override the env-driven default for this call. Optional.

    Returns:
        ``MeshResult`` from ``run_layer``. In ``off`` mode the result is
        always passing with no decisions.

    Raises:
        ``RuntimeGateHaltError`` only in ``strict`` mode on a halting result.
    """
    resolved_mode = _resolve_mode(mode)
    if resolved_mode is EnforcementMode.OFF or _layer_is_disabled(layer):
        return MeshResult()

    result = run_layer(layer, ctx)

    # Always log a structured line for observability.
    if result.passed:
        logger.info(
            "runtime-gates enforcement: layer=%s mode=%s result=passed gates=%d",
            layer,
            resolved_mode.value,
            len(result.decisions),
        )
    else:
        last = result.decisions[-1] if result.decisions else None
        codes = list(last.reason_codes) if last else []
        logger.warning(
            "runtime-gates enforcement: layer=%s mode=%s result=halted gate=%s reason=%s codes=%s",
            layer,
            resolved_mode.value,
            result.halted_at,
            result.halt_reason,
            codes,
        )
        if resolved_mode is EnforcementMode.STRICT:
            raise RuntimeGateHaltError(layer, result)

    return result


def enforces_layer(
    layer: str,
    *,
    ctx_arg: str = "ctx",
    ctx_builder: Callable[..., GateContext] | None = None,
    mode: EnforcementMode | str | None = None,
) -> Callable:
    """Decorator wrapping a layer-entry function with gate enforcement.

    Args:
        layer: Layer constant (e.g. ``LAYER_L0``).
        ctx_arg: Name of the keyword argument carrying the
            ``GateContext`` when ``ctx_builder`` is not supplied.
        ctx_builder: Optional callable ``(*args, **kwargs) -> GateContext``
            invoked to construct a fresh context if the function does not
            receive one directly.
        mode: Force enforcement mode for this call site (overrides env).

    Behavior:
        - In ``strict`` mode, the decorated function never executes if the
          gate mesh halts; the ``RuntimeGateHaltError`` propagates.
        - In ``soft`` / ``audit`` modes, the function executes regardless;
          the wrapper attaches the ``MeshResult`` to the return value as
          ``__runtime_gate_result__`` when the return is a mutable object.
    """

    def _decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def _wrapper(*args: Any, **kwargs: Any):
            ctx: GateContext
            if ctx_builder is not None:
                ctx = ctx_builder(*args, **kwargs)
            else:
                supplied = kwargs.get(ctx_arg)
                if supplied is None:
                    raise TypeError(
                        f"@enforces_layer({layer!r}): "
                        f"no GateContext found at kwarg {ctx_arg!r} "
                        f"and no ctx_builder supplied"
                    )
                ctx = supplied
            result = enforce_layer(layer, ctx, mode=mode)
            output = fn(*args, **kwargs)
            try:
                # Attach for callers that want to introspect.
                output.__runtime_gate_result__ = result  # type: ignore[attr-defined]
            except (AttributeError, TypeError):  # guardian: allow-silent-swallow -- output attribute annotation: non-fatal; output returned regardless
                pass
            return output

        _wrapper.__runtime_gate_layer__ = layer  # type: ignore[attr-defined]
        return _wrapper

    return _decorator


__all__ = [
    "EnforcementMode",
    "RuntimeGateHaltError",
    "enforce_layer",
    "enforces_layer",
]
