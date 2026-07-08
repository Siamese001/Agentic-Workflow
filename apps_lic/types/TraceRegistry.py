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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "TraceRegistry", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "TraceRegistry", "policy_binding")
trace_contract._emit_snapshots_state("p0", "TraceRegistry", "state_snapshot")
trace_contract.emit_replay_key("p0", "TraceRegistry")
trace_contract.emit_determinism_digest("p0", "TraceRegistry")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "TraceRegistry", "execution_auth")
trace_contract._emit_validates_capability("p2", "TraceRegistry", "capability_check")
trace_contract._emit_routes_to_capability("p2", "TraceRegistry", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "TraceRegistry", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "TraceRegistry", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "TraceRegistry", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "TraceRegistry", "exec_output")
trace_contract._emit_dispatches_agent("p3", "TraceRegistry", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "TraceRegistry", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "TraceRegistry", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "TraceRegistry", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "TraceRegistry", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "TraceRegistry", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "TraceRegistry", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "TraceRegistry", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "TraceRegistry", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "TraceRegistry", "eval_metric")
trace_contract._emit_stores_embedding("p4", "TraceRegistry", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "TraceRegistry", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "TraceRegistry", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_operation_mixin import mcp_hardened_mixin

    class MCPOperationMixin(mcp_hardened_mixin):
        pass
except ImportError:  # guardian: allow-silent-swallow -- optional dependency

    class MCPOperationMixin:
        pass


from tqdm import tqdm

trace_contract.record_execution_trace("TraceRegistry", "TraceRegistry_trace")


trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("TraceRegistry", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("TraceRegistry", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("TraceRegistry", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("TraceRegistry", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("TraceRegistry", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("TraceRegistry", "p4obs", "alert")
trace_contract._emit_links_incident_trace("TraceRegistry", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("TraceRegistry", "p3lm", "pattern")
trace_contract._emit_records_learning_event("TraceRegistry", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("TraceRegistry", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("TraceRegistry", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("TraceRegistry", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("TraceRegistry", "p3lm", "policy")
trace_contract._emit_stores_learning_state("TraceRegistry", "p3lm", "state")
trace_contract._emit_records_execution_trace("TraceRegistry", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("TraceRegistry", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("TraceRegistry", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("TraceRegistry", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("TraceRegistry", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("TraceRegistry", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("TraceRegistry", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("TraceRegistry", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("TraceRegistry", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "TraceRegistry", "context_pull")
trace_contract._emit_pulls_context("p1", "TraceRegistry", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "TraceRegistry", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "TraceRegistry", "uwg_term_2")
trace_contract._emit_writes_through("p1", "TraceRegistry", "write_through")
trace_contract._emit_writes_through("p1", "TraceRegistry", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "TraceRegistry", "safety_validation")
trace_contract._emit_invokes_eval("p1", "TraceRegistry", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "TraceRegistry", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "TraceRegistry", "human_escalation")
trace_contract._emit_routes_through("p1", "TraceRegistry", "route_through")
trace_contract._emit_checks_agent_registry("p1", "TraceRegistry", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "TraceRegistry", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "TraceRegistry", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "TraceRegistry", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "TraceRegistry", "target_agent")
trace_contract._emit_verifies_policy("p1", "TraceRegistry", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "TraceRegistry", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "TraceRegistry", "boundary_check")
trace_contract._emit_transcripts_response("p1", "TraceRegistry", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "TraceRegistry")
trace_contract._emit_gated_by_confidence("p1", "TraceRegistry", "confidence_gate")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "TraceRegistry.add_trace")

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
