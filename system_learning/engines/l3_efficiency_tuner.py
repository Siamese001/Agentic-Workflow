"""L3 Efficiency Tuner — analyzes orchestration timing to identify bottlenecks.

Consumes telemetry events emitted by L3 orchestration (handshake duration,
arbitration time, dedup counts, territory processing time) and produces
advisory efficiency reports for the meta-learning pipeline.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "l3_efficiency_tuner", "p0_governance")
_emit_reads_policy_state("p0", "l3_efficiency_tuner", "policy_binding")
_emit_snapshots_state("p0", "l3_efficiency_tuner", "state_snapshot")
emit_replay_key("p0", "l3_efficiency_tuner")
emit_determinism_digest("p0", "l3_efficiency_tuner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)
_SLOW_TERRITORY_THRESHOLD_MS = 30000
_SLOW_AGENT_THRESHOLD_MS = 10000


@dataclass(frozen=True, slots=True)
class EfficiencyBottleneck:
    """A single identified bottleneck in orchestration timing."""

    component: str
    metric_name: str
    observed_value_ms: float
    threshold_ms: float
    territory: str
    recommendation: str

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EfficiencyBottleneck.canonical_bytes")

        data = {
            "component": self.component,
            "metric_name": self.metric_name,
            "observed_value_ms": self.observed_value_ms,
            "threshold_ms": self.threshold_ms,
            "territory": self.territory,
            "recommendation": self.recommendation,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True)
class EfficiencyReport:
    """Advisory report of orchestration efficiency analysis."""

    snapshot_id: str
    bottlenecks: tuple[EfficiencyBottleneck, ...]
    total_territories: int
    total_agents_executed: int
    avg_territory_time_ms: float

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EfficiencyReport.canonical_bytes")

        data = {
            "snapshot_id": self.snapshot_id,
            "bottlenecks": [json.loads(b.canonical_bytes().decode("utf-8")) for b in self.bottlenecks],
            "total_territories": self.total_territories,
            "total_agents_executed": self.total_agents_executed,
            "avg_territory_time_ms": self.avg_territory_time_ms,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class L3EfficiencyTuner:
    """Analyzes L3 orchestration telemetry for bottlenecks.

    Parameters
    ----------
    slow_territory_threshold_ms : float
        Threshold for flagging slow territory processing.
    slow_agent_threshold_ms : float
        Threshold for flagging slow individual agents.
    """

    def __init__(
        self,
        slow_territory_threshold_ms: float = _SLOW_TERRITORY_THRESHOLD_MS,
        slow_agent_threshold_ms: float = _SLOW_AGENT_THRESHOLD_MS,
    ) -> None:
        self._slow_territory_ms = slow_territory_threshold_ms
        self._slow_agent_ms = slow_agent_threshold_ms

    def analyze(
        self,
        *,
        snapshot_id: str,
        territory_timings: dict[str, float],
        agent_timings: dict[str, dict[str, float]],
    ) -> EfficiencyReport:
        """Analyze orchestration timings and produce an efficiency report.

        Parameters
        ----------
        snapshot_id : str
            Pipeline snapshot identifier.
        territory_timings : dict[str, float]
            Mapping of territory name to total processing time in ms.
        agent_timings : dict[str, dict[str, float]]
            Mapping of territory → {agent_name: time_ms}.

        Returns
        -------
        EfficiencyReport
            Advisory report with identified bottlenecks.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L3EfficiencyTuner.analyze")

        bottlenecks: list[EfficiencyBottleneck] = []
        total_agents = 0
        for territory, time_ms in sorted(territory_timings.items()):
            if time_ms > self._slow_territory_ms:
                bottlenecks.append(
                    EfficiencyBottleneck(
                        component="L3_orchestration",
                        metric_name="territory_processing_time",
                        observed_value_ms=time_ms,
                        threshold_ms=self._slow_territory_ms,
                        territory=territory,
                        recommendation=f"Territory '{territory}' took {time_ms:.0f}ms (threshold: {self._slow_territory_ms:.0f}ms). Consider parallelizing or reducing agent count.",
                    )
                )
        for territory, agents in sorted(agent_timings.items()):
            for agent_name, time_ms in sorted(agents.items()):
                total_agents += 1
                if time_ms > self._slow_agent_ms:
                    bottlenecks.append(
                        EfficiencyBottleneck(
                            component=agent_name,
                            metric_name="agent_execution_time",
                            observed_value_ms=time_ms,
                            threshold_ms=self._slow_agent_ms,
                            territory=territory,
                            recommendation=f"Agent '{agent_name}' in '{territory}' took {time_ms:.0f}ms (threshold: {self._slow_agent_ms:.0f}ms). Consider caching or optimizing scan scope.",
                        )
                    )
        total_territories = len(territory_timings)
        times = list(territory_timings.values())
        avg_time = sum(times) / len(times) if times else 0.0
        return EfficiencyReport(
            snapshot_id=snapshot_id,
            bottlenecks=tuple(bottlenecks),
            total_territories=total_territories,
            total_agents_executed=total_agents,
            avg_territory_time_ms=round(avg_time, 2),
        )


def extract_timings_from_runtime_state(
    state: dict[str, Any],
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """Extract territory and agent timings from runtime state.

    Looks for ``territory_timings`` and ``agent_execution_log`` keys
    in the runtime state dict.

    Returns
    -------
    tuple[dict[str, float], dict[str, dict[str, float]]]
        ``(territory_timings, agent_timings)`` — both may be empty.
    """
    territory_timings: dict[str, float] = {}
    agent_timings: dict[str, dict[str, float]] = {}
    exec_log = state.get("agent_execution_log", [])
    for entry in exec_log:
        if not isinstance(entry, dict):
            continue
        territory = entry.get("territory", "__unknown__")
        agent = entry.get("agent", "unknown")
        duration_ms = entry.get("duration_ms", 0.0)
        try:
            duration_ms = float(duration_ms)
        except (TypeError, ValueError):
            duration_ms = 0.0
        if territory not in territory_timings:
            territory_timings[territory] = 0.0
        territory_timings[territory] += duration_ms
        if territory not in agent_timings:
            agent_timings[territory] = {}
        agent_timings[territory][agent] = duration_ms
    return (territory_timings, agent_timings)


__all__ = [
    "L3EfficiencyTuner",
    "EfficiencyReport",
    "EfficiencyBottleneck",
    "extract_timings_from_runtime_state",
]
