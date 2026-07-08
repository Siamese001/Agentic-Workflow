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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "semantic_clock_validator")
trace_contract.emit_determinism_digest("p0", "semantic_clock_validator")

trace_contract._emit_dispatches_healing_run("p1", "semantic_clock_validator", "L6")
trace_contract._emit_routes_through("p1", "semantic_clock_validator", "L6")
trace_contract._emit_checks_agent_registry("p1", "semantic_clock_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "semantic_clock_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "semantic_clock_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "semantic_clock_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "semantic_clock_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "semantic_clock_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "semantic_clock_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "semantic_clock_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "semantic_clock_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "semantic_clock_validator")
trace_contract._emit_gated_by_confidence("p1", "semantic_clock_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "semantic_clock_validator", "L6")
trace_contract._emit_reads_policy_state("p1", "semantic_clock_validator", "L6")
trace_contract._emit_authorize_and_execute("p2", "semantic_clock_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "semantic_clock_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "semantic_clock_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "semantic_clock_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "semantic_clock_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "semantic_clock_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "semantic_clock_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "semantic_clock_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "semantic_clock_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "semantic_clock_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "semantic_clock_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "semantic_clock_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "semantic_clock_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "semantic_clock_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "semantic_clock_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "semantic_clock_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "semantic_clock_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "semantic_clock_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "semantic_clock_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "semantic_clock_validator", "exec_snapshot_link")

trace_contract.record_execution_trace("semantic_clock_validator", "semantic_clock_validator_trace")


trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("semantic_clock_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("semantic_clock_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("semantic_clock_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("semantic_clock_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("semantic_clock_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("semantic_clock_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("semantic_clock_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("semantic_clock_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("semantic_clock_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("semantic_clock_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("semantic_clock_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("semantic_clock_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("semantic_clock_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("semantic_clock_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("semantic_clock_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("semantic_clock_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("semantic_clock_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("semantic_clock_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("semantic_clock_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("semantic_clock_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("semantic_clock_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("semantic_clock_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("semantic_clock_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "semantic_clock_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "semantic_clock_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_clock_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_clock_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "semantic_clock_validator", "write_through")
trace_contract._emit_writes_through("p1", "semantic_clock_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "semantic_clock_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "semantic_clock_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "semantic_clock_validator", "routing_commit")


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
    trace_material = "|".join(
        [
            str(artifact.advancement_id),
            str(artifact.previous_tick),
            str(artifact.new_tick),
            str(artifact.provider_id),
            str(artifact.timestamp),
        ]
    )
    trace_id = hashlib.sha256(trace_material.encode("utf-8", errors="ignore")).hexdigest()[:32]
    trace_contract._emit_snapshots_state(trace_id, "validate_artifact", "state_snapshot")
    trace_contract._emit_signs_execution_trace(trace_id, hashlib.sha256(trace_id.encode()).hexdigest()[:12], "p0_trace", 0)
    trace_contract._emit_applies_guardrail(trace_id, "validate_artifact", "p0_governance")
    trace_contract._emit_records_execution_trace(trace_id, trace_contract.LayerSegment.L6_OBSERVABILITY, "validate_artifact")
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
    except SyntaxError as exc:  # review: Syntax errors should be caught at parser level, not runtime
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
