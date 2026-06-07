"""RuntimeGateEngine — Fused runtime gate execution authority.

The single entrypoint for all runtime gate evaluation. Apps register their
gate packs (definitions + callables); the engine executes gates in order,
aggregates verdicts into GateBundles, and normalizes JudgeVerdicts.

W5 vocabulary (boundary remediation f8e3c1): ``GateVerdict`` objects produced
here are **00C / GateMesh** live proceed-or-stop evidence feeding write-admission
and runtime bundles. They are **not** ``apps_rg.runtime.bindings.exit_binding.ExitGateVerdict``
and they do **not** subsume Exit's single X3 disposition (X3 remains Exit-owned
after X1/X2 aggregation).

Spec reference: docs/archive/windsurf/legacy-tree/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0.P4)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from agentic_core.L5_safety.runtime_gates.contracts import Result

from agentic_core.runtime_gates.definitions import (
    GateDefinition,
    GateEnforcement,
    GatePlacement,
    GateVerdict,
    JudgeVerdict,
)
from agentic_core.runtime_gates.gate_bundle import GateBundle


# Gate callable type: (artifact, context) -> GateVerdict
GateCallable = Callable[[Any, dict[str, Any]], GateVerdict]


@dataclass(frozen=True)
class GatePack:
    """A registered set of gates from an application.

    Fields:
        app_id: The application (e.g., "apps_rg")
        definitions: Mapping of gate_id -> GateDefinition
        callables: Mapping of gate_id -> GateCallable
    """

    app_id: str
    definitions: dict[str, GateDefinition] = field(default_factory=dict)
    callables: dict[str, GateCallable] = field(default_factory=dict)


class RuntimeGateEngine:
    """Fused runtime gate execution engine.

    Single point of execution for all runtime gates. Apps register gate packs;
    the engine evaluates gates in placement order, aggregates verdicts, and
    produces GateBundles for WriteAdmissionGuard.
    """

    def __init__(self):
        """Initialize the engine with empty registry."""
        self._gate_packs: dict[str, GatePack] = {}
        self._all_definitions: dict[str, GateDefinition] = {}

    def register_gate_pack(
        self,
        app_id: str,
        definitions: list[GateDefinition],
        callables: dict[str, GateCallable],
    ) -> None:
        """Register a gate pack from an application.

        Args:
            app_id: The application (e.g., "apps_rg")
            definitions: List of GateDefinitions for this app's gates
            callables: Mapping of gate_id -> callable that produces GateVerdict
        """
        defs_map = {d.gate_id: d for d in definitions}
        pack = GatePack(
            app_id=app_id,
            definitions=defs_map,
            callables=callables,
        )
        self._gate_packs[app_id] = pack
        self._all_definitions.update(defs_map)

    def evaluate(
        self,
        app_id: str,
        placement: GatePlacement,
        artifact: Any,
        context: dict[str, Any],
    ) -> GateBundle:
        """Evaluate all gates for a given placement.

        Args:
            app_id: The application whose gates to evaluate
            placement: The lifecycle placement (PER_CAND, POST_ENS, etc.)
            artifact: The candidate artifact being evaluated
            context: Runtime context (run_context, config, etc.)

        Returns:
            GateBundle with aggregated verdicts
        """
        pack = self._gate_packs.get(app_id)
        if pack is None:
            # No gate pack registered — return empty bundle (fail-closed default)
            return GateBundle(
                app_id=app_id,
                placement=placement,
                verdicts=(),
                overall_result=Result.UNKNOWN,
                evaluator_ref=f"RuntimeGateEngine:{app_id}",
            )

        # Find gates for this placement
        placement_gates = [
            (gate_id, pack.definitions[gate_id])
            for gate_id, defn in pack.definitions.items()
            if defn.placement == placement
        ]

        # Sort by dependencies (simple topological sort)
        sorted_gates = self._sort_by_dependencies(placement_gates, pack.definitions)

        # Execute gates in order
        verdicts: list[GateVerdict] = []
        start_time = time.time()

        for gate_id, gate_def in sorted_gates:
            callable_fn = pack.callables.get(gate_id)
            if callable_fn is None:
                # Missing callable — fail this gate
                verdicts.append(GateVerdict(
                    gate_id=gate_id,
                    result=Result.UNKNOWN,
                    reason=f"Callable not found for gate {gate_id}",
                    reason_codes=("missing_callable",),
                ))
                continue

            # Execute gate
            gate_start = time.time()
            try:
                verdict = callable_fn(artifact, context)
                # Ensure latency is set
                if verdict.latency_ms == 0.0:
                    verdict = GateVerdict(
                        gate_id=verdict.gate_id,
                        result=verdict.result,
                        reason=verdict.reason,
                        reason_codes=verdict.reason_codes,
                        evidence_refs=verdict.evidence_refs,
                        timestamp_utc=verdict.timestamp_utc or datetime.now(timezone.utc).isoformat(),
                        latency_ms=(time.time() - gate_start) * 1000,
                        deterministic_digest=verdict.deterministic_digest,
                    )
            except Exception as e:  # guardian: allow-broad-exception -- P1 ADG burndown
                # Gate threw exception — treat as UNKNOWN (fail-closed)
                verdict = GateVerdict(
                    gate_id=gate_id,
                    result=Result.UNKNOWN,
                    reason=f"Gate {gate_id} raised: {type(e).__name__}: {e}",
                    reason_codes=("gate_exception", type(e).__name__),
                    latency_ms=(time.time() - gate_start) * 1000,
                )
            verdicts.append(verdict)

        total_latency_ms = (time.time() - start_time) * 1000

        # Create bundle
        bundle = GateBundle.from_verdicts(
            app_id=app_id,
            placement=placement,
            verdicts=verdicts,
            evaluator_ref=f"RuntimeGateEngine:{app_id}:{placement.value}",
        )
        # Override latency with measured total
        return GateBundle(
            app_id=bundle.app_id,
            placement=bundle.placement,
            verdicts=bundle.verdicts,
            overall_result=bundle.overall_result,
            evidence_refs=bundle.evidence_refs,
            evaluator_ref=bundle.evaluator_ref,
            latency_ms_total=total_latency_ms,
        )

    def normalize_judge_verdict(self, judge_verdict: JudgeVerdict) -> GateVerdict:
        """Normalize a JudgeVerdict into a GateVerdict.

        This is the bridge between online judges (narrative_judge_scorer)
        and the runtime gate system. The RuntimeGateEngine uses this when
        a judge produces a verdict that needs to be aggregated into a GateBundle.
        """
        return judge_verdict.to_gate_verdict()

    def get_gate_definitions(self) -> dict[str, GateDefinition]:
        """Get all registered gate definitions."""
        return self._all_definitions.copy()

    def _sort_by_dependencies(
        self,
        gates: list[tuple[str, GateDefinition]],
        all_definitions: dict[str, GateDefinition],
    ) -> list[tuple[str, GateDefinition]]:
        """Simple topological sort by dependencies."""
        # Build dependency graph
        gate_ids = {g[0] for g in gates}
        deps: dict[str, set[str]] = {}

        for gate_id, gate_def in gates:
            # Only include dependencies that are in this placement
            deps[gate_id] = {d for d in gate_def.dependencies if d in gate_ids}

        # Kahn's algorithm
        result: list[tuple[str, GateDefinition]] = []
        no_deps = [g for g in gates if not deps[g[0]]]

        while no_deps:
            gate = no_deps.pop(0)
            result.append(gate)

            # Remove this gate from other gates' dependencies
            for gate_id, gate_def in gates:
                if gate[0] in deps.get(gate_id, set()):
                    deps[gate_id].remove(gate[0])
                    if not deps[gate_id] and gate_id not in {g[0] for g in result}:
                        # Find the gate_def for this gate_id
                        for g in gates:
                            if g[0] == gate_id:
                                no_deps.append(g)
                                break

        # If there are remaining gates, there's a cycle — add them anyway
        remaining = [g for g in gates if g[0] not in {r[0] for r in result}]
        result.extend(remaining)

        return result


__all__ = [
    "RuntimeGateEngine",
    "GatePack",
    "GateCallable",
]
