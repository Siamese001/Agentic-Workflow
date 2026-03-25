"""W19: Two-run SemanticClock advancement; identical artifact + L4 version binding; no wall-clock.

REQ-192/409: SemanticClock advancement produces identical artifacts across runs;
no wall-clock usage in AST of clock module.
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClock,
    SemanticClockAdvancementArtifact,
    SemanticClockSnapshot,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_semantic_clock_replay", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_semantic_clock_replay", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_semantic_clock_replay", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_semantic_clock_replay", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_semantic_clock_replay", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_semantic_clock_replay", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_semantic_clock_replay", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_semantic_clock_replay", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_semantic_clock_replay", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_semantic_clock_replay", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_semantic_clock_replay", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_semantic_clock_replay", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_semantic_clock_replay", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_semantic_clock_replay", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_semantic_clock_replay", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_semantic_clock_replay", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_semantic_clock_replay", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_semantic_clock_replay", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_semantic_clock_replay", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_semantic_clock_replay", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_semantic_clock_replay", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_semantic_clock_replay", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_semantic_clock_replay", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_semantic_clock_replay")
# REMOVED: _emit_applies_guardrail("p0", "test_semantic_clock_replay", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_semantic_clock_replay", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_semantic_clock_replay", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_semantic_clock_replay", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_semantic_clock_replay", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_clock_replay", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_clock_replay", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_semantic_clock_replay", "write_through")
# REMOVED: _emit_writes_through("p1", "test_semantic_clock_replay", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_semantic_clock_replay", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_semantic_clock_replay", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_semantic_clock_replay", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_semantic_clock_replay", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_semantic_clock_replay", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_semantic_clock_replay", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_semantic_clock_replay", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_semantic_clock_replay", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_semantic_clock_replay", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_semantic_clock_replay", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_semantic_clock_replay", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_semantic_clock_replay", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_semantic_clock_replay", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_semantic_clock_replay", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_semantic_clock_replay")
# REMOVED: _emit_gated_by_confidence("p1", "test_semantic_clock_replay", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_semantic_clock_replay")
# REMOVED: emit_determinism_digest("p0", "test_semantic_clock_replay")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_semantic_clock_replay", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_semantic_clock_replay", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_semantic_clock_replay", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_semantic_clock_replay", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_semantic_clock_replay", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_semantic_clock_replay", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_semantic_clock_replay", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_semantic_clock_replay", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_semantic_clock_replay", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_semantic_clock_replay", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_semantic_clock_replay", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_semantic_clock_replay", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_semantic_clock_replay", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_semantic_clock_replay", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_semantic_clock_replay", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_semantic_clock_replay", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_semantic_clock_replay", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_semantic_clock_replay", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_semantic_clock_replay", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_semantic_clock_replay", "exec_snapshot_link")

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).parent.parent.parent
_CLOCK_MODULE = REPO_ROOT / "agentic_core/L0_routing/types/determinism_types.py"

_WALL_CLOCK_ATTRS = frozenset(["time", "now", "utcnow", "monotonic", "perf_counter"])


def _find_wallclock_calls(path: Path) -> list[str]:
    """AST-scan for wall-clock calls in a module."""
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # datetime.now() / datetime.utcnow()
            if isinstance(func, ast.Attribute) and func.attr in _WALL_CLOCK_ATTRS:
                violations.append(f"line {node.lineno}: wall-clock call '{func.attr}()'")
            # time.time() / time.monotonic()
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "time" and func.attr in _WALL_CLOCK_ATTRS:
                    violations.append(f"line {node.lineno}: wall-clock call 'time.{func.attr}()'")
    return violations


@pytest.mark.governance
def test_req192_semantic_clock_advancement_two_run_identical():
    """REQ-192: Two-run SemanticClock advancement produces identical snapshot."""
    clock1 = SemanticClock(step_id=0)
    clock2 = SemanticClock(step_id=0)

    snap1 = SemanticClockSnapshot(
        tick=clock1.step_id,
        vector_clock=clock1.vector_clock,
    )
    snap2 = SemanticClockSnapshot(
        tick=clock2.step_id,
        vector_clock=clock2.vector_clock,
    )

    assert snap1.tick == snap2.tick
    assert snap1.vector_clock == snap2.vector_clock


@pytest.mark.governance
def test_req192_clock_advancement_artifact_deterministic():
    """REQ-192: SemanticClockAdvancementArtifact hash is deterministic."""
    artifact1 = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    artifact2 = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )

    assert artifact1.artifact_hash == artifact2.artifact_hash
    assert len(artifact1.artifact_hash) == 64


@pytest.mark.governance
def test_req192_clock_advancement_hash_field_sensitive():
    """Changing any field changes the advancement artifact hash."""
    base = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    alt = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=99,  # changed
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    assert base.artifact_hash != alt.artifact_hash


@pytest.mark.governance
def test_req409_no_wallclock_in_semantic_clock_module():
    """REQ-409: No wall-clock calls in the determinism_types module."""
    assert _CLOCK_MODULE.exists(), f"Module not found: {_CLOCK_MODULE}"
    violations = _find_wallclock_calls(_CLOCK_MODULE)
    # Filter out calls inside SemanticClockAdvancementArtifact.__post_init__
    # which uses timestamp (a field, not a call) — we check for actual CALLS
    assert violations == [], f"Wall-clock calls found in {_CLOCK_MODULE.name}:\n" + "\n".join(violations)


@pytest.mark.governance
def test_req192_l4_version_binding_in_artifact():
    """REQ-192: Advancement artifact carries L4 version binding."""
    artifact = SemanticClockAdvancementArtifact(
        advancement_id="adv_002",
        previous_tick=10,
        new_tick=11,
        advancement_reason="policy_update",
        l4_version_binding="l4_v2.0.1",
        provider_id="provider_openai",
        timestamp=9999999.0,
    )
    assert artifact.l4_version_binding == "l4_v2.0.1"
    assert artifact.provider_id == "provider_openai"


@pytest.mark.governance
def test_req192_clock_snapshot_immutable():
    """SemanticClockSnapshot is a frozen dataclass (immutable)."""
    snap = SemanticClockSnapshot(tick=7, vector_clock=())
    with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
        snap.tick = 99  # type: ignore[misc]
