"""Phase 7.1: ADG Determinism test -- digest is stable across two invocations.

Markers: architecture, determinism
"""

from __future__ import annotations

from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_digest_stable")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_digest_stable", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_digest_stable", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_digest_stable", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_digest_stable", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_digest_stable", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_digest_stable", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_digest_stable", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_digest_stable", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_digest_stable", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_digest_stable", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_digest_stable", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_digest_stable", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_digest_stable", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_digest_stable", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_digest_stable", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_digest_stable", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_digest_stable", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_digest_stable", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_digest_stable", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_digest_stable", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_digest_stable", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_digest_stable", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_digest_stable", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_digest_stable", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_digest_stable", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_digest_stable", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_digest_stable", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_digest_stable", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_digest_stable", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_digest_stable", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_digest_stable", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_digest_stable", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_digest_stable", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_digest_stable", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_digest_stable", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_digest_stable", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_digest_stable", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_digest_stable", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_digest_stable", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_digest_stable", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_digest_stable", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_digest_stable", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_digest_stable", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_digest_stable", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_digest_stable", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_digest_stable", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_digest_stable")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_digest_stable", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_digest_stable")
# REMOVED: emit_determinism_digest("p0", "test_adg_digest_stable")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_digest_stable", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_digest_stable", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_digest_stable", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_digest_stable", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_digest_stable", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_digest_stable", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_digest_stable", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_digest_stable", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_digest_stable", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_digest_stable", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_digest_stable", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_digest_stable", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_digest_stable", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_digest_stable", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_digest_stable", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_digest_stable", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_digest_stable", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_digest_stable", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_digest_stable", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_digest_stable", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture(scope="module")
def scan_cache_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("adg_digest_stable") / "scan_result_cache.json"


def _make_scanner(cache_path: Path):
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    return ADGStaticScanner(repo_root=REPO_ROOT, cache_path=cache_path)


@pytest.fixture(scope="module")
def full_scan_result(scan_cache_path: Path):
    return _make_scanner(scan_cache_path).scan(commit_sha="module-full-scan")


@pytest.mark.architecture
@pytest.mark.determinism
@pytest.mark.timeout(420)
def test_adg_digest_stable_two_runs(full_scan_result, scan_cache_path: Path) -> None:
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
        from agentic_core.adg.artifact.builder_types import build_artifact
        """Scanner digest must be identical across two independent invocations."""
        result_1 = full_scan_result
        result_2 = _make_scanner(scan_cache_path).scan(commit_sha="test-run-2")

    result_2 = _make_scanner(scan_cache_path).scan(commit_sha="test-run-2")

    assert result_1.digest, "First scan produced empty digest"
    assert result_2.digest, "Second scan produced empty digest"
    assert result_1.digest == result_2.digest, (
        f"Digest mismatch:\n  run1: {result_1.digest}\n  run2: {result_2.digest}\n"
        f"  edges1: {len(result_1.edges)}\n  edges2: {len(result_2.edges)}"
    )


@pytest.mark.architecture
@pytest.mark.determinism
@pytest.mark.timeout(300)
def test_adg_artifact_digest_stable_two_builds(full_scan_result) -> None:
#  # MOVED: from agentic_core.adg.artifact.builder_types import build_artifact

    artifact_1 = build_artifact(full_scan_result)
    artifact_2 = build_artifact(full_scan_result)

    assert artifact_1.artifact_digest
    assert artifact_2.artifact_digest
    assert artifact_1.artifact_digest == artifact_2.artifact_digest
    assert len(artifact_1.entities) == len(artifact_2.entities)
    assert len(artifact_1.relations) == len(artifact_2.relations)


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_digest_is_sha256_hex(full_scan_result) -> None:
    """Digest must be a 64-character lowercase hex string (SHA-256)."""
    result = full_scan_result

    assert len(result.digest) == 64, f"Expected 64-char hex, got: {result.digest!r}"
    assert result.digest == result.digest.lower(), "Digest must be lowercase"
    assert all(c in "0123456789abcdef" for c in result.digest)


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_edge_list_sorted(full_scan_result) -> None:
    """Edge list in ScanResult must be in stable sorted order."""
    result = full_scan_result

    assert len(result.edges) > 0, "Expected at least one edge from scan"
    for i in range(len(result.edges) - 1):
        a = result.edges[i]
        b = result.edges[i + 1]
        assert a <= b, f"Edge list not sorted at index {i}:\n  [{i}]: {a}\n  [{i + 1}]: {b}"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_modules_sorted(full_scan_result) -> None:
    """Module list must be in deterministic sorted order."""
    result = full_scan_result

    assert result.modules == sorted(result.modules), "Module list is not sorted"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_canonical_edge_text_stable(full_scan_result) -> None:
    """canonical_edge_text() must produce identical output on two calls."""
    result = full_scan_result

    text_1 = result.canonical_edge_text()
    text_2 = result.canonical_edge_text()
    assert text_1 == text_2, "canonical_edge_text() is not idempotent"


@pytest.mark.architecture
@pytest.mark.determinism
def test_adg_scan_files_subset_digest_differs_from_full(
    full_scan_result,
    scan_cache_path: Path,
) -> None:
    """Scanning a subset of files must produce a different digest than full scan."""
    scanner = _make_scanner(scan_cache_path)
    full_result = full_scan_result
    subset_result = scanner.scan_files(
        ["agentic_core/L2_execution/UniversalWriteGateway.py"],
        commit_sha="subset",
    )
    assert full_result.digest != subset_result.digest, (
        "Subset scan should produce a different digest from full scan"
    )
