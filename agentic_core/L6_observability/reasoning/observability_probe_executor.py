"""ObservabilityProbeExecutorAgent — Canonical parameterized observability agent.

Consolidates: TrackObservabilityCostAgent, CoordinateObservabilityOperationsAgent,
              StrategicObservationAgent, DeadlockDetectorAgent, DebateSynthesisAgent,
              RuntimeTelemetryAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class ObservabilityProbeExecutorAgent(SovereignBaseAgent):
    """Parameterized observability probe agent.

    Usage:
        probe = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
    """

    project_root: Any = field(default=None)
    probe_type: str = "generic"
    _results: dict = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()

    # guardian: allow-type-erasure
    def execute(self, context: dict | None = None) -> dict:
        """Dispatch to probe-specific execution."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ObservabilityProbeExecutorAgent.execute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "ObservabilityProbeExecutorAgent.execute", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "ObservabilityProbeExecutorAgent.execute"
        )

        ctx = context or {}
        handler = self._get_handler()
        if handler:
            self._results = handler(ctx)
        return self._results

    def _get_handler(self):
        handlers = {
            "cost_tracker": self._probe_cost,
            "coordinator": self._probe_coordination,
            "strategic": self._probe_strategic,
            "deadlock": self._probe_deadlock,
            "debate": self._probe_debate,
            "runtime_telemetry": self._probe_telemetry,
        }
        return handlers.get(self.probe_type)

    # guardian: allow-type-erasure
    def _probe_cost(self, ctx: dict) -> dict:
        return {"probe": "cost_tracker", "metrics": ctx.get("cost_metrics", {})}

    # guardian: allow-type-erasure
    def _probe_coordination(self, ctx: dict) -> dict:
        return {"probe": "coordinator", "operations": ctx.get("operations", [])}

    # guardian: allow-type-erasure
    def _probe_strategic(self, ctx: dict) -> dict:
        return {"probe": "strategic", "observations": ctx.get("observations", [])}

    # guardian: allow-type-erasure
    def _probe_deadlock(self, ctx: dict) -> dict:
        return {"probe": "deadlock", "cycles": ctx.get("dependency_cycles", [])}

    # guardian: allow-type-erasure
    def _probe_debate(self, ctx: dict) -> dict:
        return {"probe": "debate", "synthesis": ctx.get("debate_results", {})}

    # guardian: allow-type-erasure
    def _probe_telemetry(self, ctx: dict) -> dict:
        return {"probe": "runtime_telemetry", "benchmarks": ctx.get("benchmarks", {})}

    # guardian: allow-type-erasure
    def scan_violations(self, target_territory: str | None = None) -> dict:
        """Contract-aligned surface for EXECUTION_PLAN phase 4.5.

        Delegates to execute() with debate probe context.
        """
        ctx: dict[str, Any] = {}
        if target_territory is not None:
            ctx["target_territory"] = target_territory
        result = self.execute(ctx)
        return {"violations": result.get("synthesis", {}).get("violations", [])}

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        return super().heal_repository(**kwargs)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "skipped",
            "details": f"ObservabilityProbeExecutor({self.probe_type})",
            "artifacts": [],
            "errors": [],
        }
