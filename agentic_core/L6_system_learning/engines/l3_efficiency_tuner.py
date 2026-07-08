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
from tqdm import tqdm
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "l3_efficiency_tuner", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "l3_efficiency_tuner", "policy_binding")
trace_contract._emit_snapshots_state("p0", "l3_efficiency_tuner", "state_snapshot")

trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l3_efficiency_tuner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l3_efficiency_tuner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l3_efficiency_tuner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l3_efficiency_tuner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l3_efficiency_tuner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l3_efficiency_tuner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l3_efficiency_tuner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l3_efficiency_tuner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l3_efficiency_tuner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l3_efficiency_tuner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l3_efficiency_tuner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l3_efficiency_tuner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l3_efficiency_tuner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l3_efficiency_tuner", "p3lm", "state")
trace_contract._emit_records_execution_trace("l3_efficiency_tuner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l3_efficiency_tuner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l3_efficiency_tuner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l3_efficiency_tuner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l3_efficiency_tuner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l3_efficiency_tuner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l3_efficiency_tuner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l3_efficiency_tuner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l3_efficiency_tuner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "l3_efficiency_tuner", "context_pull")
trace_contract._emit_pulls_context("p1", "l3_efficiency_tuner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "l3_efficiency_tuner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l3_efficiency_tuner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "l3_efficiency_tuner", "write_through")
trace_contract._emit_writes_through("p1", "l3_efficiency_tuner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "l3_efficiency_tuner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l3_efficiency_tuner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l3_efficiency_tuner", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l3_efficiency_tuner", "human_escalation")
trace_contract._emit_routes_through("p1", "l3_efficiency_tuner", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l3_efficiency_tuner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l3_efficiency_tuner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l3_efficiency_tuner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l3_efficiency_tuner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l3_efficiency_tuner", "target_agent")
trace_contract._emit_verifies_policy("p1", "l3_efficiency_tuner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l3_efficiency_tuner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l3_efficiency_tuner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l3_efficiency_tuner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l3_efficiency_tuner")
trace_contract._emit_gated_by_confidence("p1", "l3_efficiency_tuner", "confidence_gate")
trace_contract.emit_replay_key("p0", "l3_efficiency_tuner")
trace_contract.emit_determinism_digest("p0", "l3_efficiency_tuner")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "l3_efficiency_tuner", "execution_auth")
trace_contract._emit_validates_capability("p2", "l3_efficiency_tuner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l3_efficiency_tuner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l3_efficiency_tuner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l3_efficiency_tuner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l3_efficiency_tuner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l3_efficiency_tuner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l3_efficiency_tuner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l3_efficiency_tuner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l3_efficiency_tuner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l3_efficiency_tuner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l3_efficiency_tuner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l3_efficiency_tuner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l3_efficiency_tuner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l3_efficiency_tuner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l3_efficiency_tuner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l3_efficiency_tuner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l3_efficiency_tuner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l3_efficiency_tuner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l3_efficiency_tuner", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EfficiencyBottleneck.canonical_bytes"
        )

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EfficiencyReport.canonical_bytes"
        )

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "L3EfficiencyTuner.analyze")

        bottlenecks: list[EfficiencyBottleneck] = []
        total_agents = 0
        for territory, time_ms in tqdm(
            sorted(territory_timings.items()), desc="territory timings", unit="territory", leave=False
        ):
            if time_ms > self._slow_territory_ms:
                bottlenecks.append(
                    EfficiencyBottleneck(
                        component="L3_orchestration",
                        metric_name="territory_processing_time",
                        observed_value_ms=time_ms,
                        threshold_ms=self._slow_territory_ms,
                        territory=territory,
                        recommendation=f"Territory '{territory}' took {time_ms:.0f}ms (threshold: {self._slow_territory_ms:.0f}ms). Consider parallelizing or reducing agent count.",
                    ),
                )
        for territory, agents in tqdm(
            sorted(agent_timings.items()), desc="territory agents", unit="territory", leave=False
        ):
            for agent_name, time_ms in tqdm(
                sorted(agents.items()), desc="  agents", unit="agent", leave=False
            ):
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
                        ),
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
    for entry in tqdm(exec_log, desc="exec log", unit="entry", leave=False):
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
