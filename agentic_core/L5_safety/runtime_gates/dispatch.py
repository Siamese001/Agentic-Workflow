"""Per-layer gate dispatch.

Production code in L0/L1/L2/L3/L5 calls ``run_layer(layer, ctx)`` to invoke
the gates relevant to that layer in spec-defined order. Each call short-
circuits on stop conditions or halt dispositions.

This is the thin API layer; deeper composition-root wiring is intentionally
out of scope (see plan ``runtime-gates-dispatch-wiring-c4e9a2``).
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.orchestrator import (
    HALT_DISPOSITIONS,
    MeshResult,
    run_mesh,
)
from agentic_core.L5_safety.runtime_gates.contracts import GateContext

# Layer name constants.
LAYER_U0 = "U0"
LAYER_L0 = "L0"
LAYER_L1 = "L1"
LAYER_L2 = "L2"
LAYER_L3 = "L3"
LAYER_L4 = "L4"
LAYER_L5 = "L5"
LAYER_L6 = "L6"
LAYER_C0 = "C0"
LAYER_PROMPT = "PromptAssembly"
LAYER_EXIT = "Exit"
LAYER_UWG = "UWG"

# Per-layer gate ordering — drawn from `Evaluation_Runtime_Gates.md` per-gate
# ``PRIMARY_LAYER`` declarations and the spec's per-stage acceptance criteria.
LAYER_GATES: dict[str, tuple[str, ...]] = {
    LAYER_U0: ("G01", "G02"),
    LAYER_L1: ("G03",),
    LAYER_L0: ("G04", "G05", "G06", "G07"),
    LAYER_C0: ("G08", "G09"),
    LAYER_PROMPT: ("G10",),
    LAYER_L2: ("G11", "G12", "G13", "G14", "G15"),
    LAYER_L4: ("G16", "G17"),
    LAYER_L3: ("G18", "G19", "G20"),
    LAYER_EXIT: ("G21", "G22", "G23", "G24", "G26"),
    LAYER_UWG: ("G27",),
    LAYER_L6: ("G25", "G28", "G29"),
    # L5 is the policy/enforcement plane; it consumes results from every layer
    # rather than owning an exclusive gate subset. Provided for completeness.
    LAYER_L5: ("G04", "G05", "G06", "G17"),
}


def gates_for_layer(layer: str) -> tuple[str, ...]:
    """Return the spec-ordered tuple of gate IDs for the given layer."""
    if layer not in LAYER_GATES:
        raise ValueError(f"unknown layer: {layer!r}")
    return LAYER_GATES[layer]


def run_layer(layer: str, ctx: GateContext) -> MeshResult:
    """Invoke all gates registered for ``layer`` and return a MeshResult.

    Short-circuits on stop conditions or halt dispositions, matching
    ``orchestrator.run_mesh`` semantics. Use this from L0/L1/L2/L3/L5 entry
    points to evaluate the layer's gate subset before proceeding.
    """
    order = gates_for_layer(layer)
    return run_mesh(ctx, order=order, halt_on=HALT_DISPOSITIONS)


__all__ = [
    "LAYER_C0",
    "LAYER_EXIT",
    "LAYER_GATES",
    "LAYER_L0",
    "LAYER_L1",
    "LAYER_L2",
    "LAYER_L3",
    "LAYER_L4",
    "LAYER_L5",
    "LAYER_L6",
    "LAYER_PROMPT",
    "LAYER_U0",
    "LAYER_UWG",
    "gates_for_layer",
    "run_layer",
]
