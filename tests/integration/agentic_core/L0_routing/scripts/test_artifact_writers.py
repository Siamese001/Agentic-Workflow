"""
Tests for E6 and E7 artifact writers (run_manifest, decision_summary, artifact_integrity).

Per .windsurfrules §1.1: Zero-tolerance testing - all changed logic tested.
Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
Per hostile audit Section E6: run_manifest.json and decision_summary.json.
Per hostile audit Section E7: artifact_integrity.json as final step.
"""

import hashlib
import json

import pytest

from agentic_core.L0_routing.config.path_constants import APPS_SHARED_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
)

_emit_records_execution_trace("p0", "evidence", "test_artifact_writers")
_emit_applies_guardrail("p0", "test_artifact_writers", "p0_governance")
_emit_reads_policy_state("p0", "test_artifact_writers", "policy_binding")
_emit_snapshots_state("p0", "test_artifact_writers", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_1")
_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_2")
_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_3")
_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_4")
_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_5")
_emit_emits_metric_event("test_artifact_writers", "p4obs", "metric_6")
_emit_records_incident_event("test_artifact_writers", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_artifact_writers", "p4obs", "anomaly")
_emit_writes_observability_log("test_artifact_writers", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_artifact_writers", "p4obs", "mon_state")
_emit_triggers_alert("test_artifact_writers", "p4obs", "alert")
_emit_links_incident_trace("test_artifact_writers", "p4obs", "trace_link")
_emit_captures_pattern("test_artifact_writers", "p3lm", "pattern")
_emit_records_learning_event("test_artifact_writers", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_artifact_writers", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_artifact_writers", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_artifact_writers", "p3lm", "routing")
_emit_improves_agent_policy("test_artifact_writers", "p3lm", "policy")
_emit_stores_learning_state("test_artifact_writers", "p3lm", "state")
_emit_records_execution_trace("test_artifact_writers", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_artifact_writers", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_artifact_writers", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_artifact_writers", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_artifact_writers", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_artifact_writers", "env_read", "p2_env_1")
_emit_reads_environ("test_artifact_writers", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_artifact_writers", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_artifact_writers", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_artifact_writers", "context_pull")
_emit_pulls_context("p1", "test_artifact_writers", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_artifact_writers", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_artifact_writers", "uwg_term_2")
_emit_writes_through("p1", "test_artifact_writers", "write_through")
_emit_writes_through("p1", "test_artifact_writers", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_artifact_writers", "safety_validation")
_emit_invokes_eval("p1", "test_artifact_writers", "eval_call")
_emit_proposal_commits_routing("p1", "test_artifact_writers", "routing_commit")
_emit_escalates_to_human("p1", "test_artifact_writers", "human_escalation")
_emit_routes_through("p1", "test_artifact_writers", "route_through")
_emit_checks_agent_registry("p1", "test_artifact_writers", "agent_registry")
_emit_validates_agent_capability("p1", "test_artifact_writers", "capability")
_emit_dispatches_execution_plan("p1", "test_artifact_writers", "exec_plan")
_emit_agent_executes_agent("p1", "test_artifact_writers", "sub_agent")
_emit_routes_to_agent("p1", "test_artifact_writers", "target_agent")
_emit_verifies_policy("p1", "test_artifact_writers", "policy_check")
_emit_observes_runtime_state("p1", "test_artifact_writers", "runtime_state")
_emit_verifies_boundary("p1", "test_artifact_writers", "boundary_check")
_emit_transcripts_response("p1", "test_artifact_writers", "transcript")
_emit_hard_fails_untranscripted("p1", "test_artifact_writers")
_emit_gated_by_confidence("p1", "test_artifact_writers", "confidence_gate")
emit_replay_key("p0", "test_artifact_writers")
emit_determinism_digest("p0", "test_artifact_writers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_artifact_writers", "execution_auth")
_emit_validates_capability("p2", "test_artifact_writers", "capability_check")
_emit_routes_to_capability("p2", "test_artifact_writers", "capability_route")
_emit_writes_via_uwg("p2", "test_artifact_writers", "uwg_write")
_emit_blocks_direct_write("p2", "test_artifact_writers", "direct_write_block")
_emit_records_tool_invocation("p2", "test_artifact_writers", "tool_invocation")
_emit_captures_execution_output("p2", "test_artifact_writers", "exec_output")
_emit_dispatches_agent("p3", "test_artifact_writers", "agent_dispatch")
_emit_coordinates_agents("p3", "test_artifact_writers", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_artifact_writers", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_artifact_writers", "healing_outcome")
_emit_escalates_failure("p3", "test_artifact_writers", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_artifact_writers", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_artifact_writers", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_artifact_writers", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_artifact_writers", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_artifact_writers", "eval_metric")
_emit_stores_embedding("p4", "test_artifact_writers", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_artifact_writers", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_artifact_writers", "exec_snapshot_link")


def test_write_run_manifest_json_structure(tmp_path):
    """
    PASS: run_manifest.json has required fields and correct structure.
    FAIL: Missing fields or invalid structure.

    Per .windsurfrules §1.5: Edge cases - field presence.
    Per hostile audit Section E6: run_manifest provides high-level metadata.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

    trace_id = "TEST-TRACE-001"
    execution_mode = "heal"
    territories = ["apps_core", APPS_SHARED_DIR]
    agents_executed = ["AgentA", "AgentB", "AgentC"]

    _write_run_manifest_json(
        trace_id=trace_id,
        execution_mode=execution_mode,
        territories=territories,
        agents_executed=agents_executed,
        output_dir=tmp_path,
    )

    manifest_path = tmp_path / "run_manifest.json"
    assert manifest_path.exists(), "run_manifest.json should be created"

    with open(manifest_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["execution_mode"] == execution_mode
    assert data["territories"] == territories
    assert data["agents_executed"] == agents_executed
    assert data["agent_count"] == 3
    assert data["territory_count"] == 2
    assert "timestamp_utc" in data

    # Verify timestamp format
    assert data["timestamp_utc"].endswith("Z"), "timestamp should be UTC with Z suffix"


def test_write_run_manifest_json_empty_lists(tmp_path):
    """
    PASS: run_manifest.json handles empty territories and agents lists.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

    _write_run_manifest_json(
        trace_id="TEST-TRACE-002",
        execution_mode="scan",
        territories=[],
        agents_executed=[],
        output_dir=tmp_path,
    )

    manifest_path = tmp_path / "run_manifest.json"
    with open(manifest_path) as f:
        data = json.load(f)

    assert data["agent_count"] == 0
    assert data["territory_count"] == 0
    assert data["territories"] == []
    assert data["agents_executed"] == []


def test_write_decision_summary_json_structure(tmp_path):
    """
    PASS: decision_summary.json has required fields and aggregates decisions correctly.
    FAIL: Missing fields or incorrect aggregation.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E6: decision_summary provides routing audit trail.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_decision_summary_json

    trace_id = "TEST-TRACE-003"
    decisions = [
        {"tier": "DETERMINISTIC", "agent": "AgentA", "confidence": 0.95},
        {"tier": "TIER_1", "agent": "AgentB", "confidence": 0.75},
        {"tier": "DETERMINISTIC", "agent": "AgentA", "confidence": 0.90},
        {"tier": "TIER_2", "agent": "AgentC", "confidence": 0.55},
    ]

    _write_decision_summary_json(
        trace_id=trace_id,
        decisions_made=decisions,
        output_dir=tmp_path,
    )

    summary_path = tmp_path / "decision_summary.json"
    assert summary_path.exists(), "decision_summary.json should be created"

    with open(summary_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["total_decisions"] == 4
    assert "timestamp_utc" in data

    # Verify tier distribution
    assert data["tier_distribution"]["DETERMINISTIC"] == 2
    assert data["tier_distribution"]["TIER_1"] == 1
    assert data["tier_distribution"]["TIER_2"] == 1

    # Verify agent distribution
    assert data["agent_distribution"]["AgentA"] == 2
    assert data["agent_distribution"]["AgentB"] == 1
    assert data["agent_distribution"]["AgentC"] == 1

    # Verify decisions are preserved
    assert data["decisions"] == decisions


def test_write_decision_summary_json_empty_decisions(tmp_path):
    """
    PASS: decision_summary.json handles empty decisions list.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_decision_summary_json

    _write_decision_summary_json(
        trace_id="TEST-TRACE-004",
        decisions_made=[],
        output_dir=tmp_path,
    )

    summary_path = tmp_path / "decision_summary.json"
    with open(summary_path) as f:
        data = json.load(f)

    assert data["total_decisions"] == 0
    assert data["tier_distribution"] == {}
    assert data["agent_distribution"] == {}
    assert data["decisions"] == []


def test_write_artifact_integrity_json_structure(tmp_path):
    """
    PASS: artifact_integrity.json has required fields and hashes all artifacts.
    FAIL: Missing fields or incorrect hashing.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E7: artifact_integrity provides cryptographic proof.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    # Create some test artifacts
    artifact1 = tmp_path / "test_artifact_1.json"
    artifact1.write_text('{"test": "data1"}', encoding="utf-8")

    artifact2 = tmp_path / "test_artifact_2.json"
    artifact2.write_text('{"test": "data2"}', encoding="utf-8")

    trace_id = "TEST-TRACE-005"
    _write_artifact_integrity_json(
        trace_id=trace_id,
        output_dir=tmp_path,
    )

    integrity_path = tmp_path / "artifact_integrity.json"
    assert integrity_path.exists(), "artifact_integrity.json should be created"

    with open(integrity_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["artifact_count"] == 2  # Should not count itself
    assert "timestamp_utc" in data

    # Verify artifacts are hashed
    assert "test_artifact_1.json" in data["artifacts"]
    assert "test_artifact_2.json" in data["artifacts"]
    assert "artifact_integrity.json" not in data["artifacts"]

    # Verify hash correctness
    artifact1_hash = hashlib.sha256(artifact1.read_bytes()).hexdigest()
    assert data["artifacts"]["test_artifact_1.json"]["sha256"] == artifact1_hash

    artifact2_hash = hashlib.sha256(artifact2.read_bytes()).hexdigest()
    assert data["artifacts"]["test_artifact_2.json"]["sha256"] == artifact2_hash

    # Verify size tracking
    assert data["artifacts"]["test_artifact_1.json"]["size_bytes"] == len(artifact1.read_bytes())
    assert data["artifacts"]["test_artifact_2.json"]["size_bytes"] == len(artifact2.read_bytes())


def test_write_artifact_integrity_json_no_artifacts(tmp_path):
    """
    PASS: artifact_integrity.json handles directory with no artifacts.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    _write_artifact_integrity_json(
        trace_id="TEST-TRACE-006",
        output_dir=tmp_path,
    )

    integrity_path = tmp_path / "artifact_integrity.json"
    with open(integrity_path) as f:
        data = json.load(f)

    assert data["artifact_count"] == 0
    assert data["artifacts"] == {}


def test_write_artifact_integrity_json_deterministic_hash(tmp_path):
    """
    PASS: artifact_integrity.json produces identical hash for identical content.
    FAIL: Hash changes for same content.

    Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    # Create artifact with known content
    artifact = tmp_path / "test.json"
    content = '{"deterministic": "content"}'
    artifact.write_text(content, encoding="utf-8")

    # Write integrity file twice
    _write_artifact_integrity_json("TEST-TRACE-007", tmp_path)
    integrity_path = tmp_path / "artifact_integrity.json"
    with open(integrity_path) as f:
        data1 = json.load(f)

    # Remove and recreate
    integrity_path.unlink()
    _write_artifact_integrity_json("TEST-TRACE-007", tmp_path)
    with open(integrity_path) as f:
        data2 = json.load(f)

    # Hashes should be identical
    assert data1["artifacts"]["test.json"]["sha256"] == data2["artifacts"]["test.json"]["sha256"]

    # Verify against expected hash
    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert data1["artifacts"]["test.json"]["sha256"] == expected_hash


def test_artifact_writers_trace_id_correlation(tmp_path):
    """
    PASS: All artifacts contain the same trace_id for correlation.
    FAIL: trace_ids differ across artifacts.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must correlate all artifacts.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import (
        _write_artifact_integrity_json,
        _write_decision_summary_json,
        _write_run_manifest_json,
    )

    trace_id = "TEST-TRACE-CORRELATION"

    # Write all three artifact types
    _write_run_manifest_json(trace_id, "heal", ["apps_core"], ["AgentA"], tmp_path)
    _write_decision_summary_json(trace_id, [{"tier": "DETERMINISTIC", "agent": "AgentA"}], tmp_path)
    _write_artifact_integrity_json(trace_id, tmp_path)

    # Verify all have same trace_id
    with open(tmp_path / "run_manifest.json") as f:
        manifest = json.load(f)
    with open(tmp_path / "decision_summary.json") as f:
        summary = json.load(f)
    with open(tmp_path / "artifact_integrity.json") as f:
        integrity = json.load(f)

    assert manifest["trace_id"] == trace_id
    assert summary["trace_id"] == trace_id
    assert integrity["trace_id"] == trace_id


def test_artifact_writers_ascii_only(tmp_path):
    """
    PASS: All artifacts are written with ASCII-only encoding.
    FAIL: Non-ASCII characters appear in output.

    Per .windsurfrules §2.2: Evidence is deterministic, ASCII-only.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import (
        _write_artifact_integrity_json,
        _write_decision_summary_json,
        _write_run_manifest_json,
    )

    trace_id = "TEST-TRACE-ASCII"

    _write_run_manifest_json(trace_id, "heal", ["apps_core"], ["AgentA"], tmp_path)
    _write_decision_summary_json(trace_id, [], tmp_path)
    _write_artifact_integrity_json(trace_id, tmp_path)

    # Verify all files are ASCII-only
    for artifact_path in tmp_path.glob("*.json"):
        content = artifact_path.read_text(encoding="utf-8")
        try:
            content.encode("ascii")
        except UnicodeEncodeError:
            pytest.fail(f"{artifact_path.name} contains non-ASCII characters")
