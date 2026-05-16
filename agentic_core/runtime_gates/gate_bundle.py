"""GateBundle — Aggregates GateVerdicts across placements.

Implements GateBundle aggregation and overall result determination.
The RuntimeGateEngine produces a GateBundle after evaluating all gates
for a given placement; the WriteAdmissionGuard uses this to determine
whether to issue a WriteAdmissionReceipt.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0.P2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from agentic_core.L5_safety.runtime_gates.contracts import Result

from agentic_core.runtime_gates.definitions import (
    GateDefinition,
    GateEnforcement,
    GateVerdict,
    JudgeVerdict,
    GatePlacement,
)


@dataclass(frozen=True)
class GateBundle:
    """Aggregated verdicts from a runtime gate evaluation pass.

    Fields:
        app_id: The application being gated (e.g., "apps_rg")
        placement: The lifecycle placement (PRE_LLM, PER_CAND, etc.)
        verdicts: Tuple of individual GateVerdicts
        overall_result: Derived PASS/FAIL/WARN/UNKNOWN
        evidence_refs: Combined evidence references from all verdicts
        evaluator_ref: Reference to the engine/evaluator that produced this bundle
        latency_ms_total: Total wall-clock time for all gate evaluations
    """

    app_id: str
    placement: GatePlacement
    verdicts: tuple[GateVerdict, ...] = field(default_factory=tuple)
    overall_result: Result = Result.UNKNOWN
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    evaluator_ref: str = ""
    latency_ms_total: float = 0.0

    def __post_init__(self) -> None:
        if not self.app_id:
            raise ValueError("app_id is required")
        if isinstance(self.placement, str):
            object.__setattr__(self, "placement", GatePlacement(self.placement))
        if isinstance(self.overall_result, str):
            object.__setattr__(self, "overall_result", Result(self.overall_result))

    @classmethod
    def from_verdicts(
        cls,
        app_id: str,
        placement: GatePlacement,
        verdicts: list[GateVerdict],
        evaluator_ref: str = "",
    ) -> "GateBundle":
        """Create a GateBundle from a list of verdicts, computing overall_result."""
        # Aggregate evidence_refs
        all_evidence = []
        total_latency = 0.0
        for v in verdicts:
            all_evidence.extend(v.evidence_refs)
            total_latency += v.latency_ms

        # Determine overall result
        # Priority: FAIL > UNKNOWN > WARN > NOT_APPLICABLE > PASS
        results = [v.result for v in verdicts]
        overall = Result.PASS  # Default if no verdicts
        if results:
            if Result.FAIL in results:
                overall = Result.FAIL
            elif Result.UNKNOWN in results:
                overall = Result.UNKNOWN
            elif Result.WARN in results:
                overall = Result.WARN
            elif Result.NOT_APPLICABLE in results:
                overall = Result.NOT_APPLICABLE
            elif Result.PASS in results:
                overall = Result.PASS

        return cls(
            app_id=app_id,
            placement=placement,
            verdicts=tuple(verdicts),
            overall_result=overall,
            evidence_refs=tuple(all_evidence),
            evaluator_ref=evaluator_ref,
            latency_ms_total=total_latency,
        )

    def has_critical_failure(self, gate_definitions: dict[str, GateDefinition]) -> bool:
        """Returns True if any non-bypassable gate with FAIL_CLOSED enforcement failed."""
        for verdict in self.verdicts:
            gate_def = gate_definitions.get(verdict.gate_id)
            if gate_def is None:
                # Unknown gate — treat as critical failure (fail-closed)
                return True
            if not gate_def.bypassable and gate_def.enforcement == GateEnforcement.FAIL_CLOSED:
                if verdict.result in (Result.FAIL, Result.UNKNOWN):
                    return True
        return False

    def get_verdict(self, gate_id: str) -> Optional[GateVerdict]:
        """Get a specific gate verdict by gate_id."""
        for v in self.verdicts:
            if v.gate_id == gate_id:
                return v
        return None

    def get_failures(self) -> list[GateVerdict]:
        """Get all verdicts with FAIL or UNKNOWN result."""
        return [v for v in self.verdicts if v.result in (Result.FAIL, Result.UNKNOWN)]

    def get_warnings(self) -> list[GateVerdict]:
        """Get all verdicts with WARN result."""
        return [v for v in self.verdicts if v.result == Result.WARN]


__all__ = ["GateBundle"]
