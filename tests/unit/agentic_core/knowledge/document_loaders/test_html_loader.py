"""Tests for HTMLDocumentLoader — stdlib-first HTML text extraction."""

from pathlib import Path

from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
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

# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_html_loader", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_html_loader", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_html_loader", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_html_loader", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_html_loader", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_html_loader", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_html_loader", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_html_loader", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_html_loader", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_html_loader", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_html_loader", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_html_loader", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_html_loader", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_html_loader", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_html_loader", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_html_loader", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_html_loader", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_html_loader", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_html_loader", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_html_loader", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_html_loader", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_html_loader", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_html_loader", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_html_loader")
# REMOVED: _emit_applies_guardrail("p0", "test_html_loader", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_html_loader", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_html_loader", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_html_loader", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_html_loader", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_html_loader", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_html_loader", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_html_loader", "write_through")
# REMOVED: _emit_writes_through("p1", "test_html_loader", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_html_loader", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_html_loader", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_html_loader", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_html_loader", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_html_loader", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_html_loader", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_html_loader", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_html_loader", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_html_loader", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_html_loader", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_html_loader", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_html_loader", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_html_loader", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_html_loader", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_html_loader")
# REMOVED: _emit_gated_by_confidence("p1", "test_html_loader", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_html_loader")
# REMOVED: emit_determinism_digest("p0", "test_html_loader")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_html_loader", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_html_loader", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_html_loader", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_html_loader", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_html_loader", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_html_loader", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_html_loader", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_html_loader", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_html_loader", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_html_loader", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_html_loader", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_html_loader", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_html_loader", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_html_loader", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_html_loader", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_html_loader", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_html_loader", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_html_loader", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_html_loader", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_html_loader", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def test_html_loader_extracts_visible_text(tmp_path: Path):
    """Visible text is extracted and HTML tags are stripped."""
    html_file = tmp_path / "sample.html"
    html_file.write_text(
        "<html><head><title>T</title></head><body><h1>Hello</h1><p>World</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "Hello" in result
    assert "World" in result
    assert "<" not in result


def test_html_loader_strips_script_and_style(tmp_path: Path):
    """Script and style blocks are removed from output."""
    html_file = tmp_path / "scripted.html"
    html_file.write_text(
        "<html><body><script>var x = 1;</script><style>.a{color:red}</style><p>Visible</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "Visible" in result
    assert "var x" not in result
    assert "color:red" not in result


def test_html_loader_returns_empty_on_missing_file(tmp_path: Path):
    """Missing file returns empty string, no exception."""
    result = HTMLDocumentLoader.load_file(tmp_path / "nonexistent.html")
    assert result == ""


def test_html_loader_handles_entities(tmp_path: Path):
    """HTML entities are unescaped to their character equivalents."""
    html_file = tmp_path / "entities.html"
    html_file.write_text(
        "<html><body><p>&amp; hello &quot;world&quot;</p></body></html>",
        encoding="utf-8",
    )
    result = HTMLDocumentLoader.load_file(html_file)
    assert "& hello" in result
    assert '"world"' in result
    assert "&amp;" not in result
    assert "&quot;" not in result
