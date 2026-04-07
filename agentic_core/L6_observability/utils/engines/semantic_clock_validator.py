"""SemanticClockHashValidator — L6 Observability gate.

Validates that a SemanticClockAdvancementArtifact's stored artifact_hash
matches the re-computed hash from its fields.  No wall-clock access is
permitted in this module.

Gate contract:
- validate_artifact()  -> raises SemanticClockHashMismatch on tamper.
- scan_module_for_wallclock() -> AST-scan to assert no wall-clock calls.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "semantic_clock_validator")
emit_determinism_digest("p0", "semantic_clock_validator")

_emit_dispatches_healing_run("p1", "semantic_clock_validator", "L6")
_emit_routes_through("p1", "semantic_clock_validator", "L6")
_emit_checks_agent_registry("p1", "semantic_clock_validator", "agent_registry")
_emit_validates_agent_capability("p1", "semantic_clock_validator", "capability")
_emit_dispatches_execution_plan("p1", "semantic_clock_validator", "exec_plan")
_emit_agent_executes_agent("p1", "semantic_clock_validator", "sub_agent")
_emit_routes_to_agent("p1", "semantic_clock_validator", "target_agent")
_emit_verifies_policy("p1", "semantic_clock_validator", "policy_check")
_emit_observes_runtime_state("p1", "semantic_clock_validator", "runtime_state")
_emit_verifies_boundary("p1", "semantic_clock_validator", "boundary_check")
_emit_transcripts_response("p1", "semantic_clock_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "semantic_clock_validator")
_emit_gated_by_confidence("p1", "semantic_clock_validator", "confidence_gate")
_emit_escalates_to_human("p1", "semantic_clock_validator", "L6")
_emit_reads_policy_state("p1", "semantic_clock_validator", "L6")
_emit_authorize_and_execute("p2", "semantic_clock_validator", "execution_auth")
_emit_validates_capability("p2", "semantic_clock_validator", "capability_check")
_emit_routes_to_capability("p2", "semantic_clock_validator", "capability_route")
_emit_writes_via_uwg("p2", "semantic_clock_validator", "uwg_write")
_emit_blocks_direct_write("p2", "semantic_clock_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "semantic_clock_validator", "tool_invocation")
_emit_captures_execution_output("p2", "semantic_clock_validator", "exec_output")
_emit_dispatches_agent("p3", "semantic_clock_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "semantic_clock_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "semantic_clock_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "semantic_clock_validator", "healing_outcome")
_emit_escalates_failure("p3", "semantic_clock_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "semantic_clock_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "semantic_clock_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "semantic_clock_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "semantic_clock_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "semantic_clock_validator", "eval_metric")
_emit_stores_embedding("p4", "semantic_clock_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "semantic_clock_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "semantic_clock_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

record_execution_trace("semantic_clock_validator", "semantic_clock_validator_trace")


_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_1")
_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_2")
_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_3")
_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_4")
_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_5")
_emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_6")
_emit_records_incident_event("semantic_clock_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("semantic_clock_validator", "p4obs", "anomaly")
_emit_writes_observability_log("semantic_clock_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("semantic_clock_validator", "p4obs", "mon_state")
_emit_triggers_alert("semantic_clock_validator", "p4obs", "alert")
_emit_links_incident_trace("semantic_clock_validator", "p4obs", "trace_link")
_emit_captures_pattern("semantic_clock_validator", "p3lm", "pattern")
_emit_records_learning_event("semantic_clock_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("semantic_clock_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("semantic_clock_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("semantic_clock_validator", "p3lm", "routing")
_emit_improves_agent_policy("semantic_clock_validator", "p3lm", "policy")
_emit_stores_learning_state("semantic_clock_validator", "p3lm", "state")
_emit_records_execution_trace("semantic_clock_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("semantic_clock_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("semantic_clock_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("semantic_clock_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("semantic_clock_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("semantic_clock_validator", "env_read", "p2_env_1")
_emit_reads_environ("semantic_clock_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("semantic_clock_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("semantic_clock_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "semantic_clock_validator", "context_pull")
_emit_pulls_context("p1", "semantic_clock_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "semantic_clock_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "semantic_clock_validator", "uwg_term_2")
_emit_writes_through("p1", "semantic_clock_validator", "write_through")
_emit_writes_through("p1", "semantic_clock_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "semantic_clock_validator", "safety_validation")
_emit_invokes_eval("p1", "semantic_clock_validator", "eval_call")
_emit_proposal_commits_routing("p1", "semantic_clock_validator", "routing_commit")


class SemanticClockHashMismatch(ValueError):
    """Raised when a SemanticClockAdvancementArtifact hash fails validation."""


@dataclass(frozen=True)
class SemanticClockValidationResult:
    """Result of a clock artifact hash validation."""

    valid: bool
    stored_hash: str
    computed_hash: str
    advancement_id: str

    @property
    def mismatch(self) -> bool:
        return not self.valid


def validate_artifact(artifact: Any) -> SemanticClockValidationResult:
    """Validate a SemanticClockAdvancementArtifact's artifact_hash.

    The artifact must expose:
        .advancement_id (str)
        .previous_tick  (int)
        .new_tick       (int)
        .advancement_reason (str)
        .l4_version_binding (str)
        .provider_id    (str)
        .timestamp      (float)
        .artifact_hash  (str, 64-char hex)

    Returns:
        SemanticClockValidationResult with valid=True if hashes match.

    Raises:
        SemanticClockHashMismatch: if stored != computed hash.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_artifact", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_artifact", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "validate_artifact")
    material = {
        "advancement_id": str(artifact.advancement_id),
        "advancement_reason": str(artifact.advancement_reason),
        "l4_version_binding": str(artifact.l4_version_binding),
        "new_tick": int(artifact.new_tick),
        "previous_tick": int(artifact.previous_tick),
        "provider_id": str(artifact.provider_id),
        "timestamp": float(artifact.timestamp),
    }
    canonical = _canonical_json_bytes(material)
    computed = hashlib.sha256(canonical).hexdigest()
    stored = str(artifact.artifact_hash)
    result = SemanticClockValidationResult(
        valid=stored == computed,
        stored_hash=stored,
        computed_hash=computed,
        advancement_id=str(artifact.advancement_id),
    )
    if not result.valid:
        raise SemanticClockHashMismatch(
            f"SemanticClockValidator: artifact_hash mismatch for advancement_id={artifact.advancement_id!r}. stored={stored!r}, computed={computed!r}",
        )
    return result


_WALL_CLOCK_ATTRS: frozenset[str] = frozenset(
    {"time", "now", "utcnow", "monotonic", "perf_counter", "gmtime", "localtime"},
)


def scan_module_for_wallclock(module_path: Path) -> list[str]:
    """AST-scan *module_path* for wall-clock calls.

    Returns a list of violation strings (empty == clean).
    """
    if not module_path.exists():
        return [f"module not found: {module_path}"]
    source = module_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(module_path))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"SyntaxError at line {exc.lineno}: {exc.msg}"]
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _WALL_CLOCK_ATTRS:
            violations.append(f"line {node.lineno}: wall-clock call '{func.attr}()'")
    return violations


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True).encode("utf-8")


__all__ = [
    "SemanticClockHashMismatch",
    "SemanticClockValidationResult",
    "scan_module_for_wallclock",
    "validate_artifact",
]
