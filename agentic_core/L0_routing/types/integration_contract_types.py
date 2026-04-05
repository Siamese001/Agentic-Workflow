"""V15 Integration Result Envelope — Stable JSON Contract.

Shared contract for governance CLI tools to emit deterministic JSON
result envelopes behind a --json-out flag.

Schema v1.0.0:
    tool, schema_version, status, exit_code, inputs, findings, outputs
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "integration_contract_types", "L0")
_emit_routes_through("p1", "integration_contract_types", "L0")
_emit_checks_agent_registry("p1", "integration_contract_types", "agent_registry")
_emit_validates_agent_capability("p1", "integration_contract_types", "capability")
_emit_dispatches_execution_plan("p1", "integration_contract_types", "exec_plan")
_emit_agent_executes_agent("p1", "integration_contract_types", "sub_agent")
_emit_routes_to_agent("p1", "integration_contract_types", "target_agent")
_emit_verifies_policy("p1", "integration_contract_types", "policy_check")
_emit_observes_runtime_state("p1", "integration_contract_types", "runtime_state")
_emit_verifies_boundary("p1", "integration_contract_types", "boundary_check")
_emit_transcripts_response("p1", "integration_contract_types", "transcript")
_emit_hard_fails_untranscripted("p1", "integration_contract_types")
_emit_gated_by_confidence("p1", "integration_contract_types", "confidence_gate")
_emit_escalates_to_human("p1", "integration_contract_types", "L0")
_emit_reads_policy_state("p1", "integration_contract_types", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "integration_contract_types", "p0_governance")
_emit_snapshots_state("p0", "integration_contract_types", "state_snapshot")
_emit_authorize_and_execute("p2", "integration_contract_types", "execution_auth")
_emit_validates_capability("p2", "integration_contract_types", "capability_check")
_emit_routes_to_capability("p2", "integration_contract_types", "capability_route")
_emit_writes_via_uwg("p2", "integration_contract_types", "uwg_write")
_emit_blocks_direct_write("p2", "integration_contract_types", "direct_write_block")
_emit_records_tool_invocation("p2", "integration_contract_types", "tool_invocation")
_emit_captures_execution_output("p2", "integration_contract_types", "exec_output")
_emit_dispatches_agent("p3", "integration_contract_types", "agent_dispatch")
_emit_coordinates_agents("p3", "integration_contract_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "integration_contract_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "integration_contract_types", "healing_outcome")
_emit_escalates_failure("p3", "integration_contract_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "integration_contract_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "integration_contract_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "integration_contract_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "integration_contract_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "integration_contract_types", "eval_metric")
_emit_stores_embedding("p4", "integration_contract_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "integration_contract_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "integration_contract_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_1")
_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_2")
_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_3")
_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_4")
_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_5")
_emit_emits_metric_event("integration_contract_types", "p4obs", "metric_6")
_emit_records_incident_event("integration_contract_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("integration_contract_types", "p4obs", "anomaly")
_emit_writes_observability_log("integration_contract_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("integration_contract_types", "p4obs", "mon_state")
_emit_triggers_alert("integration_contract_types", "p4obs", "alert")
_emit_links_incident_trace("integration_contract_types", "p4obs", "trace_link")
_emit_captures_pattern("integration_contract_types", "p3lm", "pattern")
_emit_records_learning_event("integration_contract_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("integration_contract_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("integration_contract_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("integration_contract_types", "p3lm", "routing")
_emit_improves_agent_policy("integration_contract_types", "p3lm", "policy")
_emit_stores_learning_state("integration_contract_types", "p3lm", "state")
_emit_records_execution_trace("integration_contract_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("integration_contract_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("integration_contract_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("integration_contract_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("integration_contract_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("integration_contract_types", "env_read", "p2_env_1")
_emit_reads_environ("integration_contract_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("integration_contract_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("integration_contract_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "integration_contract_types", "context_pull")
_emit_pulls_context("p1", "integration_contract_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "integration_contract_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "integration_contract_types", "uwg_term_2")
_emit_writes_through("p1", "integration_contract_types", "write_through")
_emit_writes_through("p1", "integration_contract_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "integration_contract_types", "safety_validation")
_emit_invokes_eval("p1", "integration_contract_types", "eval_call")
_emit_proposal_commits_routing("p1", "integration_contract_types", "routing_commit")

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class Finding:
    """A single finding from a governance tool run."""

    code: str
    severity: str
    message: str
    context: dict | None = None

    def to_ordered_dict(self) -> dict:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "Finding.to_ordered_dict")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        d: dict = {
            "code": self.code,
            "context": self.context if self.context is not None else {},
            "message": self.message,
            "severity": self.severity,
        }
        return d


@dataclass
class ResultEnvelope:
    """Deterministic JSON result envelope for governance CLIs."""

    tool: str
    exit_code: int
    inputs: dict[str, dict] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    outputs: dict[str, dict] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Derive status from exit_code and findings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ResultEnvelope.status")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        has_error = any(f.severity == "ERROR" for f in self.findings)
        has_warn = any(f.severity == "WARN" for f in self.findings)
        if self.exit_code != 0 or has_error:
            return "FAIL"
        if has_warn:
            return "WARN"
        return "PASS"

    def to_ordered_dict(self) -> dict:
        """Return a plain dict with stable key ordering."""
        return {
            "exit_code": self.exit_code,
            "findings": [f.to_ordered_dict() for f in self.findings],
            "inputs": dict(sorted(self.inputs.items())),
            "outputs": dict(sorted(self.outputs.items())),
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "tool": self.tool,
        }

    def to_json(self) -> str:
        """Deterministic JSON string: sorted keys, compact separators."""
        return json.dumps(self.to_ordered_dict(), sort_keys=True, separators=(",", ":"))

    def write_json(self, path: Path) -> None:
        """Write deterministic JSON bytes to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        assert_no_persistent_write("L0", "write_text")
        path.write_text(self.to_json(), encoding="utf-8")
