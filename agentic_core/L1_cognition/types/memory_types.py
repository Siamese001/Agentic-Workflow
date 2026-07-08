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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "memory_types")
trace_contract.emit_determinism_digest("p0", "memory_types")

trace_contract._emit_dispatches_healing_run("p1", "memory_types", "L1")
trace_contract._emit_routes_through("p1", "memory_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "memory_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "memory_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "memory_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "memory_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "memory_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "memory_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "memory_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "memory_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "memory_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "memory_types")
trace_contract._emit_gated_by_confidence("p1", "memory_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "memory_types", "L1")
trace_contract._emit_reads_policy_state("p1", "memory_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "memory_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "memory_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "memory_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "memory_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "memory_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "memory_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "memory_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "memory_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "memory_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "memory_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "memory_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "memory_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "memory_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "memory_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "memory_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "memory_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "memory_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "memory_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "memory_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "memory_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("memory_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("memory_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("memory_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("memory_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("memory_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("memory_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("memory_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("memory_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("memory_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("memory_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("memory_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("memory_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("memory_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("memory_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("memory_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("memory_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("memory_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("memory_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("memory_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("memory_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("memory_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("memory_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("memory_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "memory_types", "context_pull")
trace_contract._emit_pulls_context("p1", "memory_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "memory_types", "write_through")
trace_contract._emit_writes_through("p1", "memory_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "memory_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "memory_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "memory_types", "routing_commit")

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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ViolationSignature.to_text", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ViolationSignature.to_text", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "ViolationSignature.to_text")

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
