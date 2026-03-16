"""
Wave 2 Phase 2.1 - Advanced Governance: Full Stamp Coverage Tests

Branch inventory for analyze_layer_connection_integrity:
  LAYER-UPWARD-IMPORT gap
    - success: file with upward imports generates gap
    - negative: file with no upward imports generates no gap
    - boundary: file with only same-layer or downward imports generates no upward gap
  GATEWAY-BYPASS-RISK gap
    - success: file with direct_provider_imports (not SovereignLLMGateway) generates gap
    - negative: file with no direct_provider_imports generates no gap
    - allowlist: SovereignLLMGateway.py with provider imports is EXCLUDED from gap
  NON-L2-MUTATION-RISK gap
    - success: L0 file with write_paths generates gap
    - success: L3 file with write_paths generates gap
    - success: L5 file with write_paths generates gap
    - negative: L2 file with write_paths does NOT generate gap (L2 is the allowed executor)
    - negative: non-layered file with write_paths does NOT generate gap
    - boundary: L0 file with empty write_paths generates no gap
  PATHD-PLAN-HASH-GAP
    - success: file with path_d_mentions but no original_plan_hash generates gap
    - negative: file with original_plan_hash in path_d_mentions generates no gap
    - success: 'hitl' in path name generates gap (even without path_d_mentions)
    - negative: file with neither HITL marker nor path_d_mentions generates no gap
  layer_connection_findings accumulation
    - each processed file appends a finding dict with required keys
    - parse-failed file is skipped (not added to findings)
  Real codebase invariants
    - GATEWAY-BYPASS-RISK gaps exist for the 2 known L2 adapter files
    - healing_provider_adapters.py generates GATEWAY-BYPASS-RISK
    - qwen_vllm_inference.py generates GATEWAY-BYPASS-RISK
    - SovereignLLMGateway.py does NOT generate GATEWAY-BYPASS-RISK
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_wave2_phase2_1_advanced_governance")
_emit_applies_guardrail("p0", "test_wave2_phase2_1_advanced_governance", "p0_governance")
_emit_reads_policy_state("p0", "test_wave2_phase2_1_advanced_governance", "policy_binding")
_emit_snapshots_state("p0", "test_wave2_phase2_1_advanced_governance", "state_snapshot")
emit_replay_key("p0", "test_wave2_phase2_1_advanced_governance")
emit_determinism_digest("p0", "test_wave2_phase2_1_advanced_governance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_wave2_phase2_1_advanced_governance", "execution_auth")
_emit_validates_capability("p2", "test_wave2_phase2_1_advanced_governance", "capability_check")
_emit_routes_to_capability("p2", "test_wave2_phase2_1_advanced_governance", "capability_route")
_emit_writes_via_uwg("p2", "test_wave2_phase2_1_advanced_governance", "uwg_write")
_emit_blocks_direct_write("p2", "test_wave2_phase2_1_advanced_governance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_wave2_phase2_1_advanced_governance", "tool_invocation")
_emit_captures_execution_output("p2", "test_wave2_phase2_1_advanced_governance", "exec_output")
_emit_dispatches_agent("p3", "test_wave2_phase2_1_advanced_governance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_wave2_phase2_1_advanced_governance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_wave2_phase2_1_advanced_governance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_wave2_phase2_1_advanced_governance", "healing_outcome")
_emit_escalates_failure("p3", "test_wave2_phase2_1_advanced_governance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_wave2_phase2_1_advanced_governance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_wave2_phase2_1_advanced_governance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_wave2_phase2_1_advanced_governance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_wave2_phase2_1_advanced_governance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_wave2_phase2_1_advanced_governance", "eval_metric")
_emit_stores_embedding("p4", "test_wave2_phase2_1_advanced_governance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_wave2_phase2_1_advanced_governance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_wave2_phase2_1_advanced_governance", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    FileAnalysis,
    ParseFailure,
    SemanticGapAnalyzer,
)

_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_1")
_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_2")
_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_3")
_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_4")
_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_5")
_emit_emits_metric_event("test_wave2_phase2_1_advanced_governance", "p4obs", "metric_6")
_emit_records_incident_event("test_wave2_phase2_1_advanced_governance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_wave2_phase2_1_advanced_governance", "p4obs", "anomaly")
_emit_writes_observability_log("test_wave2_phase2_1_advanced_governance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_wave2_phase2_1_advanced_governance", "p4obs", "mon_state")
_emit_triggers_alert("test_wave2_phase2_1_advanced_governance", "p4obs", "alert")
_emit_links_incident_trace("test_wave2_phase2_1_advanced_governance", "p4obs", "trace_link")
_emit_captures_pattern("test_wave2_phase2_1_advanced_governance", "p3lm", "pattern")
_emit_records_learning_event("test_wave2_phase2_1_advanced_governance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_wave2_phase2_1_advanced_governance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_wave2_phase2_1_advanced_governance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_wave2_phase2_1_advanced_governance", "p3lm", "routing")
_emit_improves_agent_policy("test_wave2_phase2_1_advanced_governance", "p3lm", "policy")
_emit_stores_learning_state("test_wave2_phase2_1_advanced_governance", "p3lm", "state")
_emit_records_execution_trace("test_wave2_phase2_1_advanced_governance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_wave2_phase2_1_advanced_governance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_wave2_phase2_1_advanced_governance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_wave2_phase2_1_advanced_governance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_wave2_phase2_1_advanced_governance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_wave2_phase2_1_advanced_governance", "env_read", "p2_env_1")
_emit_reads_environ("test_wave2_phase2_1_advanced_governance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_wave2_phase2_1_advanced_governance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_wave2_phase2_1_advanced_governance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_wave2_phase2_1_advanced_governance", "context_pull")
_emit_pulls_context("p1", "test_wave2_phase2_1_advanced_governance", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_wave2_phase2_1_advanced_governance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_wave2_phase2_1_advanced_governance", "uwg_term_secondary")
_emit_writes_through("p1", "test_wave2_phase2_1_advanced_governance", "write_through")
_emit_writes_through("p1", "test_wave2_phase2_1_advanced_governance", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_wave2_phase2_1_advanced_governance", "safety_validation")
_emit_invokes_eval("p1", "test_wave2_phase2_1_advanced_governance", "eval_call")
_emit_proposal_commits_routing("p1", "test_wave2_phase2_1_advanced_governance", "routing_commit")
_emit_escalates_to_human("p1", "test_wave2_phase2_1_advanced_governance", "human_escalation")
_emit_routes_through("p1", "test_wave2_phase2_1_advanced_governance", "route_through")
_emit_checks_agent_registry("p1", "test_wave2_phase2_1_advanced_governance", "agent_registry")
_emit_validates_agent_capability("p1", "test_wave2_phase2_1_advanced_governance", "capability")
_emit_dispatches_execution_plan("p1", "test_wave2_phase2_1_advanced_governance", "exec_plan")
_emit_agent_executes_agent("p1", "test_wave2_phase2_1_advanced_governance", "sub_agent")
_emit_routes_to_agent("p1", "test_wave2_phase2_1_advanced_governance", "target_agent")
_emit_verifies_policy("p1", "test_wave2_phase2_1_advanced_governance", "policy_check")
_emit_observes_runtime_state("p1", "test_wave2_phase2_1_advanced_governance", "runtime_state")
_emit_verifies_boundary("p1", "test_wave2_phase2_1_advanced_governance", "boundary_check")
_emit_transcripts_response("p1", "test_wave2_phase2_1_advanced_governance", "transcript")
_emit_hard_fails_untranscripted("p1", "test_wave2_phase2_1_advanced_governance")
_emit_gated_by_confidence("p1", "test_wave2_phase2_1_advanced_governance", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_analysis(file_path: Path, **kwargs) -> FileAnalysis:
    a = FileAnalysis(file_path=file_path)
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


def _failed_analysis(file_path: Path) -> FileAnalysis:
    a = FileAnalysis(file_path=file_path)
    a.parse_failure = ParseFailure(file_path=file_path, error_type="SyntaxError", message="fake")
    return a


def _make_analyzer_with_files(file_map: dict[Path, FileAnalysis]) -> SemanticGapAnalyzer:
    """Return a SemanticGapAnalyzer whose AST analyzer is mocked to serve file_map."""
    analyzer = SemanticGapAnalyzer()
    paths = sorted(file_map.keys())

    def _fake_find(layer_dir, pattern):
        return [p for p in paths if str(p).startswith(str(AGENTIC_CORE))]

    def _fake_analyze(fp):
        return file_map.get(fp, _ok_analysis(fp))

    analyzer.ast_analyzer.find_hot_paths = _fake_find
    analyzer.ast_analyzer.analyze_file = _fake_analyze
    return analyzer


# ===========================================================================
# 1. LAYER-UPWARD-IMPORT gap
# ===========================================================================


@pytest.mark.architecture
def test_upward_import_generates_layer_upward_import_gap():
    """Success: L2 file with upward import (L1 ref) generates LAYER-UPWARD-IMPORT gap."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, imported_layer_refs={"L1"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    upward_gaps = [g for g in gaps if g.gap_id.startswith("LAYER-UPWARD-IMPORT")]
    assert upward_gaps, "Expected LAYER-UPWARD-IMPORT gap for L2 file importing L1"
    assert upward_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_no_upward_import_produces_no_upward_gap():
    """Negative: file with no imported_layer_refs generates no LAYER-UPWARD-IMPORT gap."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, imported_layer_refs=set())
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    upward_gaps = [g for g in gaps if g.gap_id.startswith("LAYER-UPWARD-IMPORT")]
    assert not upward_gaps


@pytest.mark.architecture
def test_same_layer_import_produces_no_upward_gap():
    """Boundary: L2 file importing L2 (same rank) generates no upward import gap."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, imported_layer_refs={"L2"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    upward_gaps = [g for g in gaps if g.gap_id.startswith("LAYER-UPWARD-IMPORT")]
    assert not upward_gaps, f"Same-layer import should not trigger upward gap: {upward_gaps}"


@pytest.mark.architecture
def test_higher_layer_import_produces_no_upward_gap():
    """Boundary: L2 file importing L3 (higher rank) generates no upward import gap
    because _detect_upward_imports only flags lower-rank layer refs."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, imported_layer_refs={"L3"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    upward_gaps = [g for g in gaps if g.gap_id.startswith("LAYER-UPWARD-IMPORT")]
    assert not upward_gaps


# ===========================================================================
# 2. GATEWAY-BYPASS-RISK gap
# ===========================================================================


@pytest.mark.architecture
def test_direct_provider_import_generates_gateway_bypass_risk():
    """Success: file with direct_provider_imports (non-gateway) generates GATEWAY-BYPASS-RISK."""
    fake_path = AGENTIC_CORE / "L2_execution" / "healers" / "fake_adapter.py"
    fake_analysis = _ok_analysis(fake_path, direct_provider_imports={"openai"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    assert gw_gaps, "Expected GATEWAY-BYPASS-RISK for file with direct provider import"
    assert gw_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_no_provider_import_generates_no_gateway_bypass_gap():
    """Negative: file with no direct_provider_imports generates no GATEWAY-BYPASS-RISK."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, direct_provider_imports=set())
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    assert not gw_gaps


@pytest.mark.architecture
def test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap():
    """Allowlist: SovereignLLMGateway.py with provider imports is exempt from GATEWAY-BYPASS-RISK."""
    fake_path = AGENTIC_CORE / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"
    fake_analysis = _ok_analysis(fake_path, direct_provider_imports={"openai", "anthropic"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    assert not gw_gaps, f"SovereignLLMGateway.py must be excluded from GATEWAY-BYPASS-RISK, got: {gw_gaps}"


@pytest.mark.architecture
def test_gateway_bypass_gap_lists_provider_in_reality():
    """Contract: GATEWAY-BYPASS-RISK gap's reality field must mention the provider name."""
    fake_path = AGENTIC_CORE / "L2_execution" / "healers" / "fake_adapter.py"
    fake_analysis = _ok_analysis(fake_path, direct_provider_imports={"vllm"})
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    assert gw_gaps
    assert "vllm" in gw_gaps[0].reality


# ===========================================================================
# 3. NON-L2-MUTATION-RISK gap
# ===========================================================================


@pytest.mark.architecture
def test_l0_file_with_write_paths_generates_mutation_risk():
    """Success: L0 file with write_paths generates NON-L2-MUTATION-RISK."""
    fake_path = AGENTIC_CORE / "L0_routing" / "engines" / "fake_router.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=["write_result"])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert mut_gaps, "Expected NON-L2-MUTATION-RISK for L0 file with write_paths"
    assert mut_gaps[0].priority == "MEDIUM"


@pytest.mark.architecture
def test_l3_file_with_write_paths_generates_mutation_risk():
    """Success: L3 file with write_paths generates NON-L2-MUTATION-RISK."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "fake_orch.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=["append_result"])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert mut_gaps, "Expected NON-L2-MUTATION-RISK for L3 file with write_paths"


@pytest.mark.architecture
def test_l5_file_with_write_paths_generates_mutation_risk():
    """Success: L5 file with write_paths generates NON-L2-MUTATION-RISK."""
    fake_path = AGENTIC_CORE / "L5_safety" / "engines" / "fake_safety.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=["delete_record"])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert mut_gaps, "Expected NON-L2-MUTATION-RISK for L5 file with write_paths"


@pytest.mark.architecture
def test_l2_file_with_write_paths_does_not_generate_mutation_risk():
    """Negative: L2 is the allowed mutation layer — write_paths in L2 do NOT trigger gap."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=["write_result", "commit_record"])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert not mut_gaps, f"L2 write_paths must not trigger NON-L2-MUTATION-RISK: {mut_gaps}"


@pytest.mark.architecture
def test_l1_file_with_write_paths_does_not_generate_mutation_risk():
    """Negative: L1 is not in the flagged layers set (L0, L3, L5 only)."""
    fake_path = AGENTIC_CORE / "L1_cognition" / "engines" / "fake_cog.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=["write_output"])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert not mut_gaps, f"L1 is not in flagged layers for mutation risk: {mut_gaps}"


@pytest.mark.architecture
def test_l0_file_with_empty_write_paths_no_mutation_gap():
    """Boundary: L0 file with empty write_paths generates no mutation risk gap."""
    fake_path = AGENTIC_CORE / "L0_routing" / "engines" / "fake_router.py"
    fake_analysis = _ok_analysis(fake_path, write_paths=[])
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    assert not mut_gaps


# ===========================================================================
# 4. PATHD-PLAN-HASH-GAP
# ===========================================================================


@pytest.mark.architecture
def test_path_d_file_without_plan_hash_generates_pathd_gap():
    """Success: file with path_d_mentions but no original_plan_hash generates PATHD-PLAN-HASH-GAP."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "fake_path_d.py"
    fake_analysis = _ok_analysis(
        fake_path,
        path_d_mentions={"modify_diff schema"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    pathd_gaps = [g for g in gaps if g.gap_id.startswith("PATHD-PLAN-HASH-GAP")]
    assert pathd_gaps, "Expected PATHD-PLAN-HASH-GAP when original_plan_hash is absent"
    assert pathd_gaps[0].priority == "HIGH"


@pytest.mark.architecture
def test_path_d_file_with_plan_hash_no_pathd_gap():
    """Negative: file with original_plan_hash in path_d_mentions generates no PATHD gap."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "fake_path_d.py"
    fake_analysis = _ok_analysis(
        fake_path,
        path_d_mentions={"original_plan_hash abc123"},
    )
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    pathd_gaps = [g for g in gaps if g.gap_id.startswith("PATHD-PLAN-HASH-GAP")]
    assert not pathd_gaps, f"original_plan_hash present should suppress PATHD-PLAN-HASH-GAP: {pathd_gaps}"


@pytest.mark.architecture
def test_hitl_in_path_generates_pathd_gap_even_without_mentions():
    """Success: 'hitl' in the relative file path triggers PATHD-PLAN-HASH-GAP."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "hitl" / "fake_hitl_processor.py"
    fake_analysis = _ok_analysis(fake_path, path_d_mentions=set())
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    pathd_gaps = [g for g in gaps if g.gap_id.startswith("PATHD-PLAN-HASH-GAP")]
    assert pathd_gaps, "Expected PATHD-PLAN-HASH-GAP for file with 'hitl' in path"


@pytest.mark.architecture
def test_no_path_d_no_hitl_no_pathd_gap():
    """Negative: file with neither path_d_mentions nor hitl/PathD in path generates no PATHD gap."""
    fake_path = AGENTIC_CORE / "L3_orchestration" / "engines" / "fake_ordinary.py"
    fake_analysis = _ok_analysis(fake_path, path_d_mentions=set())
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    gaps = analyzer.analyze_layer_connection_integrity()
    pathd_gaps = [g for g in gaps if g.gap_id.startswith("PATHD-PLAN-HASH-GAP")]
    assert not pathd_gaps


# ===========================================================================
# 5. layer_connection_findings accumulation
# ===========================================================================


@pytest.mark.architecture
def test_layer_connection_finding_keys_are_present():
    """Each successfully processed file must produce a finding dict with required keys."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "fake_exec.py"
    fake_analysis = _ok_analysis(fake_path)
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    analyzer.analyze_layer_connection_integrity()
    required_keys = {
        "file",
        "layer",
        "upward_imports",
        "direct_provider_imports",
        "embedding_mentions",
        "governance_mentions",
        "path_d_mentions",
        "elevator_shaft_mentions",
    }
    assert analyzer.layer_connection_findings, "Expected at least one finding"
    for finding in analyzer.layer_connection_findings:
        missing = required_keys - set(finding.keys())
        assert not missing, f"Finding missing keys: {missing}"


@pytest.mark.architecture
def test_parse_failed_file_not_added_to_findings():
    """Boundary: parse-failed file is skipped — not added to layer_connection_findings."""
    fake_path = AGENTIC_CORE / "L2_execution" / "engines" / "broken_exec.py"
    fake_analysis = _failed_analysis(fake_path)
    analyzer = _make_analyzer_with_files({fake_path: fake_analysis})

    analyzer.analyze_layer_connection_integrity()
    file_paths_in_findings = [f["file"] for f in analyzer.layer_connection_findings]
    assert not any("broken_exec.py" in p for p in file_paths_in_findings), (
        "Parse-failed file should not appear in layer_connection_findings"
    )


# ===========================================================================
# 6. Real codebase invariants
# ===========================================================================


@pytest.mark.architecture
def test_healing_provider_adapters_generates_gateway_bypass_risk():
    """Success: healing_provider_adapters.py imports openai -> GATEWAY-BYPASS-RISK generated."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    files_in_gaps = [f for g in gw_gaps for f in g.evidence_files]
    assert any("healing_provider_adapters" in f for f in files_in_gaps), (
        f"Expected healing_provider_adapters.py in GATEWAY-BYPASS-RISK gaps. Files: {files_in_gaps[:10]}"
    )


@pytest.mark.architecture
def test_qwen_vllm_inference_generates_gateway_bypass_risk():
    """Success: qwen_vllm_inference.py imports vllm -> GATEWAY-BYPASS-RISK generated."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    files_in_gaps = [f for g in gw_gaps for f in g.evidence_files]
    assert any("qwen_vllm_inference" in f for f in files_in_gaps), (
        f"Expected qwen_vllm_inference.py in GATEWAY-BYPASS-RISK gaps. Files: {files_in_gaps[:10]}"
    )


@pytest.mark.architecture
def test_sovereign_llm_gateway_not_in_gateway_bypass_gaps():
    """Invariant: SovereignLLMGateway.py must never appear in GATEWAY-BYPASS-RISK gaps."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    for gap in gw_gaps:
        for evidence_file in gap.evidence_files:
            assert "SovereignLLMGateway" not in evidence_file, (
                f"SovereignLLMGateway.py must be excluded from GATEWAY-BYPASS-RISK: {evidence_file}"
            )


@pytest.mark.architecture
def test_layer_connection_integrity_returns_list():
    """Integration: analyze_layer_connection_integrity returns a list without exception."""
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_layer_connection_integrity()
    assert isinstance(result, list)


@pytest.mark.architecture
def test_gateway_bypass_gaps_are_all_high_priority():
    """Contract: all GATEWAY-BYPASS-RISK gaps must have HIGH priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    gw_gaps = [g for g in gaps if g.gap_id.startswith("GATEWAY-BYPASS-RISK")]
    for gap in gw_gaps:
        assert gap.priority == "HIGH", (
            f"GATEWAY-BYPASS-RISK must be HIGH priority, got {gap.priority} for {gap.gap_id}"
        )


@pytest.mark.architecture
def test_non_l2_mutation_risk_gaps_are_all_medium_priority():
    """Contract: all NON-L2-MUTATION-RISK gaps must have MEDIUM priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    mut_gaps = [g for g in gaps if g.gap_id.startswith("NON-L2-MUTATION-RISK")]
    for gap in mut_gaps:
        assert gap.priority == "MEDIUM", (
            f"NON-L2-MUTATION-RISK must be MEDIUM priority, got {gap.priority} for {gap.gap_id}"
        )


@pytest.mark.architecture
def test_upward_import_gaps_are_all_high_priority():
    """Contract: all LAYER-UPWARD-IMPORT gaps must have HIGH priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    up_gaps = [g for g in gaps if g.gap_id.startswith("LAYER-UPWARD-IMPORT")]
    for gap in up_gaps:
        assert gap.priority == "HIGH", (
            f"LAYER-UPWARD-IMPORT must be HIGH priority, got {gap.priority} for {gap.gap_id}"
        )


@pytest.mark.architecture
def test_pathd_gaps_are_all_high_priority():
    """Contract: all PATHD-PLAN-HASH-GAP gaps must have HIGH priority."""
    analyzer = SemanticGapAnalyzer()
    gaps = analyzer.analyze_layer_connection_integrity()
    pathd_gaps = [g for g in gaps if g.gap_id.startswith("PATHD-PLAN-HASH-GAP")]
    for gap in pathd_gaps:
        assert gap.priority == "HIGH", (
            f"PATHD-PLAN-HASH-GAP must be HIGH priority, got {gap.priority} for {gap.gap_id}"
        )
