"""Types for the Reflexion pattern.

Reflexion builds verbal self-critique into a memory buffer and uses it
to iteratively revise responses until a convergence gate is satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class ReflexionCritique:
    """Verbal critique produced by the Evaluator LLM call."""

    iteration: int
    response: str
    critique: str
    score: float
    passed: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReflexionMemory:
    """Accumulates critique history across iterations for the Revisor."""

    task: str
    critiques: list[ReflexionCritique] = field(default_factory=list)

    def add(self, critique: ReflexionCritique) -> None:
        self.critiques.append(critique)

    def summary(self) -> str:
        """Return a condensed summary of prior critiques for the Revisor prompt."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflexionMemory.summary")

        if not self.critiques:
            return ""
        lines = [f"Iteration {c.iteration}: score={c.score:.2f} — {c.critique[:120]}" for c in self.critiques]
        return "\n".join(lines)

    def best_response(self) -> str | None:
        """Return the response with the highest score seen so far."""
        if not self.critiques:
            return None
        return max(self.critiques, key=lambda c: c.score).response
