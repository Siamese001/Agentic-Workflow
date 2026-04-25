"""Gate-mesh orchestrator.

Dispatches the 29 runtime gates in the spec-defined order and short-circuits
when any gate emits a stop-condition violation or a hard deny disposition.

Spec dispatch order: U0 -> L1 -> L0 -> C0 -> PromptAssembly -> L2 -> L4 -> L3
-> Exit -> UWG -> L6.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.types import (
    Disposition,
    GateContext,
    GateDecision,
)

# Spec-aligned dispatch order (full mesh, all 29 gates).
DISPATCH_ORDER: tuple[str, ...] = (
    # U0 ingress
    "G01",
    "G02",
    # L1 cognition
    "G03",
    # L0 routing + safety
    "G04",
    "G05",
    "G06",
    "G07",
    # C0 retrieval / grounding
    "G08",
    "G09",
    # Prompt assembly
    "G10",
    # L2 execution
    "G11",
    "G12",
    "G13",
    "G14",
    "G15",
    # L4 state / memory
    "G16",
    "G17",
    # L3 orchestration
    "G18",
    "G19",
    "G20",
    # Exit evaluation
    "G21",
    "G22",
    "G23",
    "G24",
    "G26",
    # UWG
    "G27",
    # L6 observability / learning
    "G25",
    "G28",
    "G29",
)

# Dispositions that halt the mesh.
HALT_DISPOSITIONS: frozenset[Disposition] = frozenset(
    {
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.QUARANTINE,
        Disposition.REDACT,
        Disposition.ESCALATE_HITL,
    }
)


@dataclass(slots=True)
class MeshResult:
    """Outcome of a full mesh dispatch."""

    decisions: list[GateDecision] = field(default_factory=list)
    halted_at: str | None = None
    halt_reason: str | None = None

    @property
    def passed(self) -> bool:
        return self.halted_at is None

    @property
    def final_disposition(self) -> Disposition | None:
        return self.decisions[-1].disposition if self.decisions else None


def run_mesh(
    ctx: GateContext,
    *,
    order: tuple[str, ...] = DISPATCH_ORDER,
    halt_on: frozenset[Disposition] = HALT_DISPOSITIONS,
    halt_on_stop_condition: bool = True,
) -> MeshResult:
    """Dispatch every gate in `order`, short-circuiting on halt conditions.

    Args:
        ctx: Shared gate context (caller may mutate between gates if needed).
        order: Gate IDs to invoke, in dispatch order.
        halt_on: Dispositions that halt the mesh immediately.
        halt_on_stop_condition: If True, any decision with
            ``stop_condition_violated=True`` halts the mesh.

    Returns:
        MeshResult with the decisions emitted up to and including the halting
        gate (if any).
    """
    result = MeshResult()
    for gate_id in order:
        decision = evaluate(gate_id, ctx)
        result.decisions.append(decision)
        if halt_on_stop_condition and decision.stop_condition_violated:
            result.halted_at = gate_id
            result.halt_reason = "stop_condition_violated"
            return result
        if decision.disposition in halt_on:
            result.halted_at = gate_id
            result.halt_reason = f"halt_disposition:{decision.disposition.value}"
            return result
    return result


__all__ = ["DISPATCH_ORDER", "HALT_DISPOSITIONS", "MeshResult", "run_mesh"]
