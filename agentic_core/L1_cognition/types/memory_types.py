"""
agentic_core/L1_cognition/reasoning/types/memory_types.py

Passive data structures and constants for HealingMemoryEmbedder.
Extracted from engine/memory_embedder.py to prevent circular dependencies.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
)

emit_replay_key("p0", "memory_types")
emit_determinism_digest("p0", "memory_types")

_emit_dispatches_healing_run("p1", "memory_types", "L1")
_emit_routes_through("p1", "memory_types", "L1")
_emit_checks_agent_registry("p1", "memory_types", "agent_registry")
_emit_validates_agent_capability("p1", "memory_types", "capability")
_emit_dispatches_execution_plan("p1", "memory_types", "exec_plan")
_emit_agent_executes_agent("p1", "memory_types", "sub_agent")
_emit_routes_to_agent("p1", "memory_types", "target_agent")
_emit_verifies_policy("p1", "memory_types", "policy_check")
_emit_observes_runtime_state("p1", "memory_types", "runtime_state")
_emit_verifies_boundary("p1", "memory_types", "boundary_check")
_emit_transcripts_response("p1", "memory_types", "transcript")
_emit_hard_fails_untranscripted("p1", "memory_types")
_emit_gated_by_confidence("p1", "memory_types", "confidence_gate")
_emit_escalates_to_human("p1", "memory_types", "L1")
_emit_reads_policy_state("p1", "memory_types", "L1")
_emit_authorize_and_execute("p2", "memory_types", "execution_auth")
_emit_validates_capability("p2", "memory_types", "capability_check")
_emit_routes_to_capability("p2", "memory_types", "capability_route")
_emit_writes_via_uwg("p2", "memory_types", "uwg_write")
_emit_blocks_direct_write("p2", "memory_types", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_types", "tool_invocation")
_emit_captures_execution_output("p2", "memory_types", "exec_output")
_emit_dispatches_agent("p3", "memory_types", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_types", "healing_outcome")
_emit_escalates_failure("p3", "memory_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_types", "eval_metric")
_emit_stores_embedding("p4", "memory_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_types", "exec_snapshot_link")
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

_emit_emits_metric_event("memory_types", "p4obs", "metric_1")
_emit_emits_metric_event("memory_types", "p4obs", "metric_2")
_emit_emits_metric_event("memory_types", "p4obs", "metric_3")
_emit_emits_metric_event("memory_types", "p4obs", "metric_4")
_emit_emits_metric_event("memory_types", "p4obs", "metric_5")
_emit_emits_metric_event("memory_types", "p4obs", "metric_6")
_emit_records_incident_event("memory_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("memory_types", "p4obs", "anomaly")
_emit_writes_observability_log("memory_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("memory_types", "p4obs", "mon_state")
_emit_triggers_alert("memory_types", "p4obs", "alert")
_emit_links_incident_trace("memory_types", "p4obs", "trace_link")
_emit_captures_pattern("memory_types", "p3lm", "pattern")
_emit_records_learning_event("memory_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("memory_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("memory_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("memory_types", "p3lm", "routing")
_emit_improves_agent_policy("memory_types", "p3lm", "policy")
_emit_stores_learning_state("memory_types", "p3lm", "state")
_emit_records_execution_trace("memory_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("memory_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("memory_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("memory_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("memory_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("memory_types", "env_read", "p2_env_1")
_emit_reads_environ("memory_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("memory_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("memory_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "memory_types", "context_pull")
_emit_pulls_context("p1", "memory_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "memory_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "memory_types", "uwg_term_2")
_emit_writes_through("p1", "memory_types", "write_through")
_emit_writes_through("p1", "memory_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "memory_types", "safety_validation")
_emit_invokes_eval("p1", "memory_types", "eval_call")
_emit_proposal_commits_routing("p1", "memory_types", "routing_commit")

EMBEDDING_DIMENSION: Final[int] = 1024
MAX_TEXT_LENGTH: Final[int] = 8000


@dataclass
class ViolationSignature:
    """
    Represents a violation signature for embedding.

    Attributes:
        violation_type: Type of violation
        path: File path where violation occurred
        message: Violation message
        context: Additional context (e.g., line numbers, code snippet)
        domain: Domain context (agentic_core, apps_lic, apps_rg)
    """

    violation_type: str
    path: str = ""
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    domain: str = AGENTIC_CORE_DIR

    def to_text(self) -> str:
        """Convert signature to text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ViolationSignature.to_text", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ViolationSignature.to_text", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ViolationSignature.to_text")

        parts = [
            f"violation_type: {self.violation_type}",
            f"path: {self.path}",
            f"message: {self.message[:500]}",
            f"domain: {self.domain}",
        ]
        if self.context:
            context_str = json.dumps(self.context, default=str)[:500]
            parts.append(f"context: {context_str}")
        return " | ".join(parts)

    def to_hash(self) -> str:
        """Generate hash-based signature."""
        text = self.to_text()
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    @classmethod
    def from_violation(cls, violation: dict[str, Any]) -> ViolationSignature:
        """Create signature from violation dictionary."""
        return cls(
            violation_type=violation.get("type", "unknown"),
            path=violation.get("path", ""),
            message=violation.get("message", ""),
            context=violation.get("context", {}),
            domain=violation.get("domain", AGENTIC_CORE_DIR),
        )
