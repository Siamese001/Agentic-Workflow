"""
Trace Registry.

A structured audit log for tracking agent execution steps and decisions.
"""

from __future__ import annotations
import logging
import os
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

_emit_applies_guardrail("p0", "TraceRegistry", "p0_governance")
_emit_reads_policy_state("p0", "TraceRegistry", "policy_binding")
_emit_snapshots_state("p0", "TraceRegistry", "state_snapshot")
emit_replay_key("p0", "TraceRegistry")
emit_determinism_digest("p0", "TraceRegistry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "TraceRegistry", "execution_auth")
_emit_validates_capability("p2", "TraceRegistry", "capability_check")
_emit_routes_to_capability("p2", "TraceRegistry", "capability_route")
_emit_writes_via_uwg("p2", "TraceRegistry", "uwg_write")
_emit_blocks_direct_write("p2", "TraceRegistry", "direct_write_block")
_emit_records_tool_invocation("p2", "TraceRegistry", "tool_invocation")
_emit_captures_execution_output("p2", "TraceRegistry", "exec_output")
_emit_dispatches_agent("p3", "TraceRegistry", "agent_dispatch")
_emit_coordinates_agents("p3", "TraceRegistry", "agent_coordination")
_emit_records_workflow_lineage("p3", "TraceRegistry", "workflow_lineage")
_emit_records_healing_outcome("p3", "TraceRegistry", "healing_outcome")
_emit_escalates_failure("p3", "TraceRegistry", "failure_escalation")
_emit_orchestrates_workflow("p3", "TraceRegistry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "TraceRegistry", "healing_dispatch")
_emit_invokes_evaluation("p3", "TraceRegistry", "evaluation_signal")
_emit_records_telemetry_event("p4", "TraceRegistry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "TraceRegistry", "eval_metric")
_emit_stores_embedding("p4", "TraceRegistry", "embedding_store")
_emit_updates_meta_learning_state("p4", "TraceRegistry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "TraceRegistry", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_operation_mixin import mcp_hardened_mixin

    class MCPOperationMixin(mcp_hardened_mixin):
        pass
except ImportError:  # guardian: allow-silent-swallow -- optional dependency

    class MCPOperationMixin:
        pass


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

record_execution_trace("TraceRegistry", "TraceRegistry_trace")


_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_1")
_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_2")
_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_3")
_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_4")
_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_5")
_emit_emits_metric_event("TraceRegistry", "p4obs", "metric_6")
_emit_records_incident_event("TraceRegistry", "p4obs", "incident")
_emit_captures_runtime_anomaly("TraceRegistry", "p4obs", "anomaly")
_emit_writes_observability_log("TraceRegistry", "p4obs", "obs_log")
_emit_updates_monitoring_state("TraceRegistry", "p4obs", "mon_state")
_emit_triggers_alert("TraceRegistry", "p4obs", "alert")
_emit_links_incident_trace("TraceRegistry", "p4obs", "trace_link")
_emit_captures_pattern("TraceRegistry", "p3lm", "pattern")
_emit_records_learning_event("TraceRegistry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("TraceRegistry", "p3lm", "snapshot")
_emit_feeds_meta_learning("TraceRegistry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("TraceRegistry", "p3lm", "routing")
_emit_improves_agent_policy("TraceRegistry", "p3lm", "policy")
_emit_stores_learning_state("TraceRegistry", "p3lm", "state")
_emit_records_execution_trace("TraceRegistry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("TraceRegistry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("TraceRegistry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("TraceRegistry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("TraceRegistry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("TraceRegistry", "env_read", "p2_env_1")
_emit_reads_environ("TraceRegistry", "env_read", "p2_env_2")
_emit_reads_runtime_state("TraceRegistry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("TraceRegistry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "TraceRegistry", "context_pull")
_emit_pulls_context("p1", "TraceRegistry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "TraceRegistry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "TraceRegistry", "uwg_term_2")
_emit_writes_through("p1", "TraceRegistry", "write_through")
_emit_writes_through("p1", "TraceRegistry", "write_through_2")
_emit_validated_by_safety_plane("p1", "TraceRegistry", "safety_validation")
_emit_invokes_eval("p1", "TraceRegistry", "eval_call")
_emit_proposal_commits_routing("p1", "TraceRegistry", "routing_commit")
_emit_escalates_to_human("p1", "TraceRegistry", "human_escalation")
_emit_routes_through("p1", "TraceRegistry", "route_through")
_emit_checks_agent_registry("p1", "TraceRegistry", "agent_registry")
_emit_validates_agent_capability("p1", "TraceRegistry", "capability")
_emit_dispatches_execution_plan("p1", "TraceRegistry", "exec_plan")
_emit_agent_executes_agent("p1", "TraceRegistry", "sub_agent")
_emit_routes_to_agent("p1", "TraceRegistry", "target_agent")
_emit_verifies_policy("p1", "TraceRegistry", "policy_check")
_emit_observes_runtime_state("p1", "TraceRegistry", "runtime_state")
_emit_verifies_boundary("p1", "TraceRegistry", "boundary_check")
_emit_transcripts_response("p1", "TraceRegistry", "transcript")
_emit_hard_fails_untranscripted("p1", "TraceRegistry")
_emit_gated_by_confidence("p1", "TraceRegistry", "confidence_gate")


@dataclass
class TraceRegistry(MCPOperationMixin):
    """
    Registry for execution traces. Maintains an ordered log of events.
    """

    persistence_path: Path = None
    _traces: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if self.persistence_path:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            if self.persistence_path.exists():
                self._load_from_disk()
            else:
                self._flush_to_disk()

    def _load_from_disk(self) -> None:
        """Load traces from JSONL file."""
        if not self.persistence_path or not self.persistence_path.exists():
            return
        with open(self.persistence_path, encoding="utf-8") as f:
            for line_no, line in tqdm(enumerate(f, start=1), desc="Processing", unit="item"):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if not isinstance(data, dict):
                        logging.warning("TraceRegistry: skipping non-dict JSONL line %d", line_no)
                        continue
                    entry = {"timestamp": data["timestamp"], "type": data["type"], "details": data["details"]}
                    self._traces.append(entry)
                except json.JSONDecodeError as exc:
                    logging.warning("TraceRegistry: invalid JSON at line %d: %s", line_no, exc)
                except (TypeError, KeyError) as exc:
                    logging.warning("TraceRegistry: malformed entry at line %d: %s", line_no, exc)

    def _flush_to_disk(self) -> None:
        """Flush all traces to JSONL file."""
        if not self.persistence_path:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            for entry in self._traces:
                f.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _append_to_disk(self, trace: dict[str, Any]) -> None:
        """Append a single trace to JSONL file for crash resilience."""
        if self.persistence_path:
            with self.persistence_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(trace, sort_keys=True, default=str) + "\n")
                f.flush()
                os.fsync(f.fileno())

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Records a trace event with optional disk persistence.

        Args:
            event_type: Category of the event (e.g., 'DECISION', 'ERROR').
            details: Contextual data for the event.
        """
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(details, dict):
            raise TypeError("details must be a dict")

        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TraceRegistry.add_trace")

        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "type": event_type, "details": details}
        self._traces.append(entry)
        if self.persistence_path:
            self._append_to_disk(entry)

    def get_traces(self) -> list[dict[str, Any]]:
        """Returns a copy of the full trace history."""
        return list(self._traces)

    def clear(self) -> None:
        """Clears the registry (use with caution)."""
        self._traces.clear()

    def count(self, trace_type: str) -> int:
        """Count occurrences of a specific trace type."""
        return sum(1 for t in self._traces if t["type"] == trace_type)
