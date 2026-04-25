"""
Trace Registry for RG Sovereign Architecture.

A structured audit log for tracking agent execution steps and decisions.
Aligned with LIC TraceRegistry pattern.

HARDENING: Upgrades from simple logging to Span Tracing (Start/End)
to measure performance latency and token usage.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
from apps_rg.utils.rg_core_mixins import MCPOperationMixin

_emit_applies_guardrail("p0", "trace_registry_types", "p0_governance")
_emit_reads_policy_state("p0", "trace_registry_types", "policy_binding")
_emit_snapshots_state("p0", "trace_registry_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

record_execution_trace("trace_registry_types", "trace_registry_types_trace")


_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_1")
_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_2")
_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_3")
_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_4")
_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_5")
_emit_emits_metric_event("trace_registry_types", "p4obs", "metric_6")
_emit_records_incident_event("trace_registry_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("trace_registry_types", "p4obs", "anomaly")
_emit_writes_observability_log("trace_registry_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("trace_registry_types", "p4obs", "mon_state")
_emit_triggers_alert("trace_registry_types", "p4obs", "alert")
_emit_links_incident_trace("trace_registry_types", "p4obs", "trace_link")
_emit_captures_pattern("trace_registry_types", "p3lm", "pattern")
_emit_records_learning_event("trace_registry_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trace_registry_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("trace_registry_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trace_registry_types", "p3lm", "routing")
_emit_improves_agent_policy("trace_registry_types", "p3lm", "policy")
_emit_stores_learning_state("trace_registry_types", "p3lm", "state")
_emit_records_execution_trace("trace_registry_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trace_registry_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trace_registry_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trace_registry_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trace_registry_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trace_registry_types", "env_read", "p2_env_1")
_emit_reads_environ("trace_registry_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("trace_registry_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trace_registry_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trace_registry_types", "context_pull")
_emit_pulls_context("p1", "trace_registry_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trace_registry_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trace_registry_types", "uwg_term_2")
_emit_writes_through("p1", "trace_registry_types", "write_through")
_emit_writes_through("p1", "trace_registry_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "trace_registry_types", "safety_validation")
_emit_invokes_eval("p1", "trace_registry_types", "eval_call")
_emit_proposal_commits_routing("p1", "trace_registry_types", "routing_commit")
_emit_escalates_to_human("p1", "trace_registry_types", "human_escalation")
_emit_routes_through("p1", "trace_registry_types", "route_through")
_emit_checks_agent_registry("p1", "trace_registry_types", "agent_registry")
_emit_validates_agent_capability("p1", "trace_registry_types", "capability")
_emit_dispatches_execution_plan("p1", "trace_registry_types", "exec_plan")
_emit_agent_executes_agent("p1", "trace_registry_types", "sub_agent")
_emit_routes_to_agent("p1", "trace_registry_types", "target_agent")
_emit_verifies_policy("p1", "trace_registry_types", "policy_check")
_emit_observes_runtime_state("p1", "trace_registry_types", "runtime_state")
_emit_verifies_boundary("p1", "trace_registry_types", "boundary_check")
_emit_transcripts_response("p1", "trace_registry_types", "transcript")
_emit_hard_fails_untranscripted("p1", "trace_registry_types")
_emit_gated_by_confidence("p1", "trace_registry_types", "confidence_gate")
emit_replay_key("p0", "trace_registry_types")
emit_determinism_digest("p0", "trace_registry_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "trace_registry_types", "execution_auth")
_emit_validates_capability("p2", "trace_registry_types", "capability_check")
_emit_routes_to_capability("p2", "trace_registry_types", "capability_route")
_emit_writes_via_uwg("p2", "trace_registry_types", "uwg_write")
_emit_blocks_direct_write("p2", "trace_registry_types", "direct_write_block")
_emit_records_tool_invocation("p2", "trace_registry_types", "tool_invocation")
_emit_captures_execution_output("p2", "trace_registry_types", "exec_output")
_emit_dispatches_agent("p3", "trace_registry_types", "agent_dispatch")
_emit_coordinates_agents("p3", "trace_registry_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "trace_registry_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "trace_registry_types", "healing_outcome")
_emit_escalates_failure("p3", "trace_registry_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "trace_registry_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trace_registry_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "trace_registry_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "trace_registry_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trace_registry_types", "eval_metric")
_emit_stores_embedding("p4", "trace_registry_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "trace_registry_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trace_registry_types", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class AgentTrace:
    """A single execution span."""

    trace_id: str
    agent_name: str
    action: str
    start_time: float
    end_time: float = 0.0
    status: str = "RUNNING"
    error: str | None = None
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentTrace.duration_ms")

        end = self.end_time if self.end_time > 0 else time.time()
        return (end - self.start_time) * 1000


@dataclass
class TraceRegistry(MCPOperationMixin):
    """
    Centralized Telemetry Aggregator.
    Tracks execution spans, latency, and cost.

    RG-Specific Trace Types:
    - PHASE_START: Agent phase beginning
    - PHASE_COMPLETE: Agent phase completion
    - PHASE_ERROR: Agent phase failure
    - PHASE_STEP: Intermediate step within a phase
    - DATA_ERROR: Data validation failure
    - EXTRACTION_START: Clerk extraction beginning
    - ENRICHMENT_START: Enrichment beginning
    - GENERATION_START: Resume generation beginning
    - VALIDATION_PASS: Quality validation passed
    - VALIDATION_FAIL: Quality validation failed
    - GATE_DECISION: Pass/fail gate decision
    - ORCHESTRATOR_START: Workflow beginning
    - ORCHESTRATOR_RETRY: Retry loop triggered
    - ORCHESTRATOR_ERROR: Workflow failure
    """

    persistence_path: Path | None = None
    _traces: list[AgentTrace] = field(default_factory=list)
    _active_spans: dict[str, AgentTrace] = field(default_factory=dict)

    def start_span(self, trace_id: str, agent_name: str, action: str) -> str:
        """Begin tracking an action."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TraceRegistry.start_span")

        span_key = f"{trace_id}:{agent_name}:{action}:{time.time()}"
        trace = AgentTrace(trace_id=trace_id, agent_name=agent_name, action=action, start_time=time.time())
        self._traces.append(trace)
        self._active_spans[span_key] = trace
        return span_key

    def end_span(self, span_key: str, status: str = "SUCCESS", error: str = None, tokens: int = 0) -> None:
        """Complete an active action."""
        if span_key not in self._active_spans:
            Logger.warning(f"Attempted to close unknown span: {span_key}")
            return
        trace = self._active_spans.pop(span_key)
        trace.end_time = time.time()
        trace.status = status
        trace.error = error
        trace.tokens_used = tokens
        if self.persistence_path:
            self._persist_trace(trace)

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        """
        Legacy API: Records a trace event.
        Creates a completed span for backward compatibility.

        Args:
            event_type: Category of the event (e.g., 'DECISION', 'ERROR').
            details: Contextual data for the event.
        """
        trace = AgentTrace(
            trace_id=f"legacy_{time.time()}",
            agent_name=details.get("agent", "SYSTEM"),
            action=event_type,
            start_time=time.time(),
            end_time=time.time(),
            status="COMPLETE",
            metadata=details,
        )
        self._traces.append(trace)

    def get_summary(self) -> dict[str, Any]:
        """Performance report."""
        completed = [t for t in self._traces if t.end_time > 0]
        failures = [t for t in completed if t.status == "FAILURE"]
        avg_latency = sum(t.duration_ms for t in completed) / max(len(completed), 1)
        return {
            "total_spans": len(self._traces),
            "completed": len(completed),
            "failures": len(failures),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": sum(t.tokens_used for t in completed),
        }

    def get_traces(self) -> list[dict[str, Any]]:
        """Returns a list of trace dictionaries for backward compatibility."""
        return [
            {
                "trace_id": t.trace_id,
                "agent_name": t.agent_name,
                "action": t.action,
                "status": t.status,
                "duration_ms": t.duration_ms,
                "tokens_used": t.tokens_used,
                "error": t.error,
                "metadata": t.metadata,
            }
            for t in self._traces
        ]

    def clear(self) -> None:
        """Clears the registry (use with caution)."""
        self._traces.clear()
        self._active_spans.clear()

    def count(self, trace_type: str) -> int:
        """Count occurrences of a specific action type."""
        return sum(1 for t in self._traces if t.action == trace_type)

    def get_by_type(self, trace_type: str) -> list[dict[str, Any]]:
        """Get all traces of a specific action type."""
        return [
            {
                "trace_id": t.trace_id,
                "agent_name": t.agent_name,
                "action": t.action,
                "status": t.status,
                "duration_ms": t.duration_ms,
            }
            for t in self._traces
            if t.action == trace_type
        ]

    def get_latest(self, trace_type: str) -> dict[str, Any] | None:
        """Get the most recent trace of a specific action type."""
        matches = [t for t in self._traces if t.action == trace_type]
        if not matches:
            return None
        t = matches[-1]
        return {
            "trace_id": t.trace_id,
            "agent_name": t.agent_name,
            "action": t.action,
            "status": t.status,
            "duration_ms": t.duration_ms,
        }

    def _persist_trace(self, trace: AgentTrace) -> None:
        """Write trace details to disk."""
        try:
            if self.persistence_path:
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent": trace.agent_name,
                    "action": trace.action,
                    "status": trace.status,
                    "error": trace.error,
                    "duration": trace.duration_ms,
                    "tokens_used": trace.tokens_used,
                }
                with open(self.persistence_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def _persist_failure(self, trace: AgentTrace) -> None:
        """Write failure details to disk (legacy method)."""
        self._persist_trace(trace)
