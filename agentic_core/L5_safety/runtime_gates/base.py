"""Runtime Gate Mesh — base protocol and registry.

Each of the 29 gates implements ``RuntimeGate`` and registers itself in
``GATE_REGISTRY`` via the ``@register_gate`` decorator.

The orchestrator enforces ordering separately; gates do not call each other.
"""

from __future__ import annotations

from typing import Callable, ClassVar, Protocol, runtime_checkable

from agentic_core.L5_safety.runtime_gates.types import (
    Disposition,
    GateContext,
    GateDecision,
)


@runtime_checkable
class RuntimeGate(Protocol):
    """Protocol every runtime gate satisfies."""

    GATE_ID: ClassVar[str]  # "G01" … "G29"
    PRIMARY_LAYER: ClassVar[
        str
    ]  # "U0" | "L1" | "L0" | "C0" | "L2" | "L3" | "L5" | "L6" | "Exit" | "UWG" | "PA"

    def evaluate(self, ctx: GateContext) -> GateDecision: ...


GATE_REGISTRY: dict[str, RuntimeGate] = {}


def register_gate(cls):
    """Class decorator that registers a gate class instance under its GATE_ID."""
    if not hasattr(cls, "GATE_ID") or not cls.GATE_ID:
        raise ValueError(f"{cls.__name__} must declare GATE_ID")
    instance = cls()
    GATE_REGISTRY[cls.GATE_ID] = instance
    return cls


def deny(gate_id: str, *reason_codes: str, **metadata) -> GateDecision:
    """Construct a DENY decision with ``stop_condition_violated=True``."""
    return GateDecision(
        gate_id=gate_id,
        disposition=Disposition.DENY,
        reason_codes=list(reason_codes),
        metadata=metadata,
        stop_condition_violated=True,
    )


def allow(gate_id: str, *reason_codes: str, alias: str = "", **metadata) -> GateDecision:
    """Construct an ALLOW decision."""
    return GateDecision(
        gate_id=gate_id,
        disposition=Disposition.ALLOW,
        alias=alias,
        reason_codes=list(reason_codes),
        metadata=metadata,
    )


def escalate(gate_id: str, *reason_codes: str, **metadata) -> GateDecision:
    """Construct an ESCALATE_HITL decision."""
    return GateDecision(
        gate_id=gate_id,
        disposition=Disposition.ESCALATE_HITL,
        reason_codes=list(reason_codes),
        metadata=metadata,
    )


__all__ = [
    "RuntimeGate",
    "GATE_REGISTRY",
    "register_gate",
    "deny",
    "allow",
    "escalate",
]
