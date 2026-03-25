"""E2E traversal tests for execute_ssot against all major architecture surfaces.

Coverage matrix
---------------
ADG Gaps (fixes)
  [ADG-2] _ssot_pipeline._emit_adg_pre_run_artifact — GuardianPrioritizer wired into guardian_scope
  [ADG-3] execute_ssot.execute_phase4_validation_impl — ADG signals injected into ArchitectureGovernorAgent

Major Architecture Surfaces
  [S-REDIS]    redis_cache_client — DeterministicRedisCache contract invariants
  [S-SEMCACHE] sovereign_semantic_cache — mission-isolated key derivation
  [S-BGE]      embedding_factory — kill-switch, error types, lazy loading
  [S-PROMPTS]  prompt_registry_util — register/get/render/persist/search/delete
  [S-SL]       system_learning_memory_bridge — persist success/failure via _record_healing_action
  [S-PIPE]     _ssot_pipeline — EXECUTION_PLAN, AGENT_PIPELINE, CANONICAL_ROSTER_KEYS invariants
  [S-ADG-INT]  execute_ssot_integration — build_pre_run_report graceful degradation
  [S-ADG-GP]   GuardianPrioritizer — roster compatibility and ordered output

NOTE: adg_burndown_gate tests live in test_adg_burndown_gate_surfaces.py (separate file)
because that module replaces sys.stdout/sys.stderr at import time on Windows.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Force register SL bridge so patch() can resolve it regardless of test ordering
import system_learning.adapters.system_learning_memory_bridge as _sl_bridge_mod  # noqa: F401
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_execute_ssot_adg_surfaces")
# REMOVED: _emit_applies_guardrail("p0", "test_execute_ssot_adg_surfaces", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_execute_ssot_adg_surfaces", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_adg_surfaces", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_execute_ssot_adg_surfaces", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_execute_ssot_adg_surfaces", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_execute_ssot_adg_surfaces", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_execute_ssot_adg_surfaces", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_execute_ssot_adg_surfaces", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_execute_ssot_adg_surfaces", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_execute_ssot_adg_surfaces", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_execute_ssot_adg_surfaces", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_execute_ssot_adg_surfaces", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_execute_ssot_adg_surfaces", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_execute_ssot_adg_surfaces", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_execute_ssot_adg_surfaces", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_execute_ssot_adg_surfaces", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_adg_surfaces", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_adg_surfaces", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_adg_surfaces", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_adg_surfaces", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_adg_surfaces", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_execute_ssot_adg_surfaces", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_execute_ssot_adg_surfaces", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_adg_surfaces", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_adg_surfaces", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_adg_surfaces", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_adg_surfaces", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_adg_surfaces", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_adg_surfaces", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_adg_surfaces", "write_through")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_adg_surfaces", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_execute_ssot_adg_surfaces", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_execute_ssot_adg_surfaces", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_execute_ssot_adg_surfaces", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_execute_ssot_adg_surfaces", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_execute_ssot_adg_surfaces", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_execute_ssot_adg_surfaces", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_execute_ssot_adg_surfaces", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_execute_ssot_adg_surfaces", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_execute_ssot_adg_surfaces", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_execute_ssot_adg_surfaces", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_execute_ssot_adg_surfaces", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_execute_ssot_adg_surfaces", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_execute_ssot_adg_surfaces", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_execute_ssot_adg_surfaces", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_execute_ssot_adg_surfaces")
# REMOVED: _emit_gated_by_confidence("p1", "test_execute_ssot_adg_surfaces", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_execute_ssot_adg_surfaces")
# REMOVED: emit_determinism_digest("p0", "test_execute_ssot_adg_surfaces")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_execute_ssot_adg_surfaces", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_execute_ssot_adg_surfaces", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_execute_ssot_adg_surfaces", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_execute_ssot_adg_surfaces", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_execute_ssot_adg_surfaces", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_execute_ssot_adg_surfaces", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_execute_ssot_adg_surfaces", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_execute_ssot_adg_surfaces", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_execute_ssot_adg_surfaces", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_execute_ssot_adg_surfaces", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_execute_ssot_adg_surfaces", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_execute_ssot_adg_surfaces", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_execute_ssot_adg_surfaces", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_execute_ssot_adg_surfaces", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_execute_ssot_adg_surfaces", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_execute_ssot_adg_surfaces", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_execute_ssot_adg_surfaces", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_execute_ssot_adg_surfaces", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_execute_ssot_adg_surfaces", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_execute_ssot_adg_surfaces", "exec_snapshot_link")

_SL_BRIDGE_PATCH = "system_learning.adapters.system_learning_memory_bridge.get_sl_memory_bridge"

_REPO_ROOT = Path(__file__).resolve().parents[5]

# ---------------------------------------------------------------------------
# Pre-seed the missing agentic_core.adg.runtime.execution_proof stub so that
# importing agentic_core.adg.runtime.behavioral_index / cache_loader doesn't
# fail when the broken __init__.py tries to import it.
# ---------------------------------------------------------------------------
if "agentic_core.adg.runtime.execution_proof" not in sys.modules:
    _ep_mock = MagicMock()
    _ep_mock.ExecutionProofRecorder = MagicMock
    _ep_mock.ExecutionProofReport = MagicMock
    _ep_mock.ExecutionTrace = MagicMock
    sys.modules["agentic_core.adg.runtime.execution_proof"] = _ep_mock


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_empty_scan_result():
    from agentic_core.adg.extraction.static_scanner import ScanResult

    r = ScanResult(commit_sha="test")
    r.modules = []
    r.edges = []
    r.compute_digest()
    return r


def _make_cross_layer_scan_result():
    from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
    from agentic_core.adg.schema_util import canonical_name

    r = ScanResult(commit_sha="xl")
    r.modules = [
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L5_safety/config/structure_blueprint_config.py",
    ]
    r.edges = [
        Edge(
            from_name=canonical_name("Module", "agentic_core/L0_routing/config/path_constants.py"),
            relation_type="imports",
            to_name=canonical_name("Module", "agentic_core/L5_safety/config/structure_blueprint_config.py"),
            edge_kind="import",
            source_file="agentic_core/L0_routing/config/path_constants.py",
            line_no=1,
        )
    ]
    r.compute_digest()
    return r


# ===========================================================================
# [ADG-2] _ssot_pipeline._emit_adg_pre_run_artifact — GuardianPrioritizer wiring
# ===========================================================================


class TestEmitADGPreRunArtifactGuardianPrioritizer:
    """_emit_adg_pre_run_artifact must populate guardian_scope via GuardianPrioritizer."""

    def _make_mock_report(self, adg_available: bool = True, route_mode: str = "NORMAL") -> MagicMock:
        report = MagicMock()
        report.adg_available = adg_available
        report.adg_error = "" if adg_available else "ADG not available in test"
        report.impacted_modules = []
        report.impacted_module_count = 0
        report.impacted_tests = []
        report.impacted_test_count = 0
        report.risk_score = 0
        report.route_mode = route_mode
        report.layer_violation_count = 0
        report.impact_digest = "abc123"
        report.summary = (
            f"route_mode={route_mode} risk=0 impacted=0 modules tests=0 violations=0 digest=abc123"
        )
        report.scope_widening_events = []
        report.uncovered_changed_files = []
        return report

    @pytest.mark.unit
    def test_guardian_scope_populated_when_adg_available(self) -> None:
        """When ADG is available and GuardianPrioritizer runs, guardian_scope is populated."""
        from agentic_core.adg.applications.guardian_prioritizer_types import (
            GuardianPriorityScore,
            PrioritizationResult,
        )
        from agentic_core.L0_routing.scripts._ssot_pipeline import (
            CANONICAL_ROSTER_KEYS,
            _emit_adg_pre_run_artifact,
        )

        mock_scores = [
            GuardianPriorityScore(guardian_id=gid, score=0) for gid in sorted(CANONICAL_ROSTER_KEYS)
        ]
        mock_prio_result = PrioritizationResult(
            scores=mock_scores,
            adg_signals_digest="deadbeef01234567",
        )
        mock_prioritizer = MagicMock()
        mock_prioritizer.prioritize.return_value = mock_prio_result

        tmp = Path(tempfile.mkdtemp())
        try:
            with (
                patch(
                    "agentic_core.adg.applications.PreRunADGReport.build_pre_run_report",
                    return_value=self._make_mock_report(adg_available=True),
                ),
                patch(
                    "agentic_core.adg.applications.guardian_prioritizer_types.GuardianPrioritizer",
                    return_value=mock_prioritizer,
                ),
                patch(
                    "agentic_core.adg.runtime.cache_loader.load_or_scan",
                    return_value=_make_empty_scan_result(),
                ),
            ):
# REMOVED:                 _emit_adg_pre_run_artifact(tmp)

            artifacts = list((tmp / "artifacts" / "adg").glob("execution_impact_*.json"))
            assert len(artifacts) == 1
            payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
            assert isinstance(payload["guardian_scope"], list)
            assert payload["guardian_scope"] == sorted(CANONICAL_ROSTER_KEYS)
            assert payload.get("guardian_priority_digest") == "deadbeef01234567"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_guardian_scope_empty_when_adg_unavailable(self) -> None:
        """When ADG is unavailable, guardian_scope stays empty (graceful degradation)."""
        from agentic_core.L0_routing.scripts._ssot_pipeline import _emit_adg_pre_run_artifact

        tmp = Path(tempfile.mkdtemp())
        try:
            with patch(
                "agentic_core.adg.applications.PreRunADGReport.build_pre_run_report",
                return_value=self._make_mock_report(adg_available=False),
            ):
# REMOVED:                 _emit_adg_pre_run_artifact(tmp)

            artifacts = list((tmp / "artifacts" / "adg").glob("execution_impact_*.json"))
            assert len(artifacts) == 1
            payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
            assert payload["guardian_scope"] == []
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_guardian_prioritizer_failure_does_not_block_artifact_write(self) -> None:
        """If GuardianPrioritizer raises, artifact is still written (fail-open)."""
        from agentic_core.L0_routing.scripts._ssot_pipeline import _emit_adg_pre_run_artifact

        tmp = Path(tempfile.mkdtemp())
        try:
            with (
                patch(
                    "agentic_core.adg.applications.PreRunADGReport.build_pre_run_report",
                    return_value=self._make_mock_report(adg_available=True),
                ),
                patch(
                    "agentic_core.adg.applications.guardian_prioritizer_types.GuardianPrioritizer",
                    side_effect=RuntimeError("ADG scan exploded"),
                ),
                patch(
                    "agentic_core.adg.runtime.cache_loader.load_or_scan",
                    return_value=_make_empty_scan_result(),
                ),
            ):
                _emit_adg_pre_run_artifact(tmp)  # must not raise

            artifacts = list((tmp / "artifacts" / "adg").glob("execution_impact_*.json"))
            assert len(artifacts) == 1
            payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
            assert payload["guardian_scope"] == []
            assert any("GuardianPrioritizer" in w for w in payload.get("warnings", []))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_artifact_has_required_top_level_keys(self) -> None:
        """Emitted artifact always has the mandatory keys regardless of ADG state."""
        from agentic_core.L0_routing.scripts._ssot_pipeline import _emit_adg_pre_run_artifact

        tmp = Path(tempfile.mkdtemp())
        try:
            with patch(
                "agentic_core.adg.applications.PreRunADGReport.build_pre_run_report",
                side_effect=RuntimeError("ADG import failed"),
            ):
# REMOVED:                 _emit_adg_pre_run_artifact(tmp)

            artifacts = list((tmp / "artifacts" / "adg").glob("execution_impact_*.json"))
            assert len(artifacts) == 1
            payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
            required = {
                "emitted_by",
                "timestamp",
                "target_file",
                "adg_available",
                "impacted_modules",
                "impacted_module_count",
                "risk_score",
                "route_mode",
                "guardian_scope",
                "warnings",
            }
            for key in required:
                assert key in payload, f"Missing required key in artifact: {key}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# [ADG-3] execute_phase4_validation_impl — ADG signal injection
# ===========================================================================


class TestPhase4ADGSignalInjection:
    """execute_phase4_validation_impl must inject ADG signals before calling arch_gov."""

    def _make_state_mgr(self):
        sm = MagicMock()
        sm.state = {}
        return sm

    def _make_agents(self, gov_report=None):
        arch_gov_instance = MagicMock()
        arch_gov_instance.comprehensive_territory_audit.return_value = (
            gov_report if gov_report is not None else {"layer_violations": [], "naming_violations": []}
        )
        arch_gov_instance.check_file_sizes.return_value = []
        arch_gov_instance.adg_signals = {}
        arch_gov_cls = MagicMock(return_value=arch_gov_instance)
        return {"arch_governor": arch_gov_cls}, arch_gov_instance

    @pytest.mark.unit
    def test_adg_arch_signals_stored_in_state_when_available(self) -> None:
        """ADG cross-layer signals must be written to state_mgr.state['adg_arch_signals']."""
        import agentic_core.adg.runtime.behavioral_index as _bi_mod
        from agentic_core.L0_routing.scripts.execute_ssot import execute_phase4_validation_impl

        state_mgr = self._make_state_mgr()
        agents, _ = self._make_agents()

        mock_gp = MagicMock()
        mock_gp.get_signals.return_value = {
            "cross_layer_violations": [{"from": "L0", "to": "L5"}],
            "layer_hotspots": [{"key": "L0->L5", "count": 3}],
            "upward_mutations": [],
        }
        mock_adg_idx = MagicMock()
        mock_adg_idx._result = _make_empty_scan_result()

        with (
            patch.object(_bi_mod, "ADGBehavioralIndex") as mock_idx_cls,
            patch(
                "agentic_core.adg.applications.guardian_prioritizer_types.GuardianPrioritizer",
                return_value=mock_gp,
            ),
            patch(
                "agentic_core.adg.runtime.cache_loader.load_or_scan",
                return_value=_make_empty_scan_result(),
            ),
        ):
            mock_idx_cls.from_latest = MagicMock(return_value=mock_adg_idx)
            execute_phase4_validation_impl(agents, "agentic_core", state_mgr)

        assert "adg_arch_signals" in state_mgr.state
        stored = state_mgr.state["adg_arch_signals"]
        assert "cross_layer_violations" in stored
        assert "layer_hotspots" in stored
        assert "upward_mutations" in stored

    @pytest.mark.unit
    def test_adg_signal_injection_failure_does_not_abort_phase4(self) -> None:
        """If ADG signal injection raises, phase4 still calls comprehensive_territory_audit."""
        import agentic_core.adg.runtime.behavioral_index as _bi_mod
        from agentic_core.L0_routing.scripts.execute_ssot import execute_phase4_validation_impl

        state_mgr = self._make_state_mgr()
        agents, arch_gov_inst = self._make_agents()

        with patch.object(_bi_mod, "ADGBehavioralIndex", side_effect=ImportError("ADG not installed")):
            execute_phase4_validation_impl(agents, "agentic_core", state_mgr)

        arch_gov_inst.comprehensive_territory_audit.assert_called_once()

    @pytest.mark.unit
    def test_adg_cross_layer_signals_merged_into_gov_report(self) -> None:
        """ADG cross-layer violations must be present in state or merged into gov_report."""
        import agentic_core.adg.runtime.behavioral_index as _bi_mod
        from agentic_core.L0_routing.scripts.execute_ssot import execute_phase4_validation_impl

        state_mgr = self._make_state_mgr()
        base_report = {"layer_violations": [], "naming_violations": []}
        agents, _ = self._make_agents(gov_report=base_report)

        mock_gp = MagicMock()
        mock_gp.get_signals.return_value = {
            "cross_layer_violations": [{"from": "L0/foo.py", "to": "L5/bar.py"}],
            "layer_hotspots": [{"key": "L0->L5", "count": 1}],
            "upward_mutations": [],
        }
        mock_adg_idx = MagicMock()
        mock_adg_idx._result = _make_empty_scan_result()

        with (
            patch.object(_bi_mod, "ADGBehavioralIndex") as mock_idx_cls,
            patch(
                "agentic_core.adg.applications.guardian_prioritizer_types.GuardianPrioritizer",
                return_value=mock_gp,
            ),
            patch(
                "agentic_core.adg.runtime.cache_loader.load_or_scan",
                return_value=_make_empty_scan_result(),
            ),
        ):
            mock_idx_cls.from_latest = MagicMock(return_value=mock_adg_idx)
            result_tuple = execute_phase4_validation_impl(agents, "agentic_core", state_mgr)

        gov_report = result_tuple[0] if isinstance(result_tuple, tuple) else result_tuple
        has_in_report = gov_report is not None and "adg_cross_layer_violations" in gov_report
        has_in_state = "adg_arch_signals" in state_mgr.state
        assert has_in_report or has_in_state

    @pytest.mark.unit
    def test_phase4_returns_none_when_gov_report_is_none(self) -> None:
        """When arch_gov returns None, phase4 returns (None, None)."""
        import agentic_core.adg.runtime.behavioral_index as _bi_mod
        from agentic_core.L0_routing.scripts.execute_ssot import execute_phase4_validation_impl

        state_mgr = self._make_state_mgr()
        agents, arch_gov_inst = self._make_agents(gov_report=None)
        arch_gov_inst.comprehensive_territory_audit.return_value = None

        with patch.object(_bi_mod, "ADGBehavioralIndex", side_effect=ImportError("skip")):
            result = execute_phase4_validation_impl(agents, "agentic_core", state_mgr)

        assert result == (None, None)


# ===========================================================================
# [S-REDIS] Redis cache client surface
# ===========================================================================


class TestRedisCacheClientSurface:
    """redis_cache_client.DeterministicRedisCache contract invariants."""

    @pytest.mark.unit
    def test_get_hot_cache_returns_cache_instance(self) -> None:
        from agentic_core.cache.redis_cache_client import get_hot_cache

        cache = get_hot_cache()
        assert cache is not None
        assert hasattr(cache, "get")
        assert hasattr(cache, "set")

    @pytest.mark.unit
    def test_get_hot_cache_is_singleton(self) -> None:
        from agentic_core.cache.redis_cache_client import get_hot_cache

        c1 = get_hot_cache()
        c2 = get_hot_cache()
        assert c1 is c2

    @pytest.mark.unit
    def test_canonical_json_bytes_is_deterministic(self) -> None:
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"z": 1, "a": [3, 1, 2], "m": {"k": "v"}}
        b1 = canonical_json_bytes(obj)
        b2 = canonical_json_bytes(obj)
        assert b1 == b2
        assert isinstance(b1, bytes)

    @pytest.mark.unit
    def test_canonical_json_bytes_sorts_keys(self) -> None:
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        b1 = canonical_json_bytes({"b": 1, "a": 2})
        b2 = canonical_json_bytes({"a": 2, "b": 1})
        assert b1 == b2

    @pytest.mark.unit
    def test_canonical_json_bytes_rejects_nan(self) -> None:
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(ValueError):
            canonical_json_bytes({"x": float("nan")})

    @pytest.mark.unit
    def test_content_hash_returns_64_char_hex(self) -> None:
        from agentic_core.cache.redis_cache_client import content_hash

        h = content_hash(b"hello world")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    @pytest.mark.unit
    def test_cache_set_and_get_roundtrip(self) -> None:
        """Cache set/get must not raise; returns bytes or None (LRU fallback)."""
        from agentic_core.cache.redis_cache_client import get_hot_cache

        cache = get_hot_cache()
        try:
            cache.set("test_key_adg_surface", b"value", ttl_seconds=5)
            val = cache.get("test_key_adg_surface")
            assert val is None or val == b"value"
        except Exception as exc:
            pytest.fail(f"Cache get/set raised unexpectedly: {exc}")

    @pytest.mark.unit
    def test_cache_replay_mode_returns_none(self) -> None:
        """replay_mode=True must return None unconditionally (determinism invariant)."""
        from agentic_core.cache.redis_cache_client import get_hot_cache

        cache = get_hot_cache()
        cache.set("replay_test_key", b"stored_value", ttl_seconds=60)
        val = cache.get("replay_test_key", replay_mode=True)
        assert val is None


# ===========================================================================
# [S-SEMCACHE] Sovereign Semantic Cache surface
# ===========================================================================


class TestSovereignSemanticCacheSurface:
    """SovereignSemanticCache mission-isolated key derivation."""

    @pytest.mark.unit
    def test_cache_key_is_mission_isolated(self) -> None:
        """Two different mission_ids must produce different cache keys for the same file."""
        import hashlib

        file_path = "agentic_core/L0_routing/scripts/execute_ssot.py"

        def _cache_key(mission_id: str, fp: str) -> str:
            path_hash = hashlib.sha256(str(Path(fp)).encode()).hexdigest()[:16]
            return f"semantic:{mission_id}:{path_hash}"

        k1 = _cache_key("mission-A", file_path)
        k2 = _cache_key("mission-B", file_path)
        assert k1 != k2
        assert "mission-A" in k1
        assert "mission-B" in k2

    @pytest.mark.unit
    def test_cache_key_is_path_hash_not_raw_path(self) -> None:
        """Cache key must use SHA-256 hash of path, not embed the raw path string."""
        import hashlib

        file_path = "agentic_core/L0_routing/scripts/execute_ssot.py"
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        key = f"semantic:mission-X:{path_hash}"
        assert file_path not in key
        assert len(path_hash) == 16

    @pytest.mark.unit
    def test_sovereign_semantic_cache_module_importable(self) -> None:
        """The module must import without requiring a live Redis connection."""
        with patch("agentic_core.L4_state.memory.sovereign_semantic_cache.get_redis_client"):
            import importlib as _il

            mod = _il.import_module("agentic_core.L4_state.memory.sovereign_semantic_cache")
            assert hasattr(mod, "SovereignSemanticCache")


# ===========================================================================
# [S-BGE] Embedding factory surface
# ===========================================================================


class TestEmbeddingFactorySurface:
    """embedding_factory kill-switch and contract enforcement.

    agentic_core.replay.replay_envelope is missing from this repo (archived module).
    All tests in this class pre-seed sys.modules with a minimal stub before
    reloading the embedding_factory so imports succeed.
    """

    @staticmethod
    def _seed_replay_mock():
        replay_env_mock = MagicMock()
        replay_env_mock.create_deterministic_cache_key = MagicMock(return_value="test_key")
        replay_pkg_mock = MagicMock()
        replay_pkg_mock.replay_envelope = replay_env_mock
        sys.modules.setdefault("agentic_core.replay", replay_pkg_mock)
        sys.modules["agentic_core.replay.replay_envelope"] = replay_env_mock
        return replay_env_mock

    @pytest.mark.unit
    def test_embedding_factory_importable_with_replay_mock(self) -> None:
        """embedding_factory must import cleanly when agentic_core.replay is mocked."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        assert hasattr(_ef, "EmbeddingDisabledError")
        assert hasattr(_ef, "EmbeddingSovereigntyViolationError")
        assert hasattr(_ef, "is_enabled")
        assert hasattr(_ef, "EmbeddingClient")

    @pytest.mark.unit
    def test_embedding_enabled_env_var_true(self) -> None:
        """EMBEDDING_ENABLED=true → is_enabled() returns True."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            assert _ef.is_enabled() is True

    @pytest.mark.unit
    def test_embedding_disabled_via_killswitch(self) -> None:
        """EMBEDDING_ENABLED=false → is_enabled() returns False."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            assert _ef.is_enabled() is False

    @pytest.mark.unit
    def test_embedding_disabled_error_is_runtime_error(self) -> None:
        """EmbeddingDisabledError must inherit RuntimeError."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        assert issubclass(_ef.EmbeddingDisabledError, RuntimeError)

    @pytest.mark.unit
    def test_embedding_sovereignty_violation_error_is_runtime_error(self) -> None:
        """EmbeddingSovereigntyViolationError must inherit RuntimeError."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        assert issubclass(_ef.EmbeddingSovereigntyViolationError, RuntimeError)

    @pytest.mark.unit
    def test_embedding_client_protocol_has_required_methods(self) -> None:
        """EmbeddingClient protocol must expose get_embedding and get_embeddings_batch."""
        self._seed_replay_mock()
        import importlib as _il

        import agentic_core.embeddings.embedding_factory as _ef

        _il.reload(_ef)
        assert hasattr(_ef.EmbeddingClient, "get_embedding")
        assert hasattr(_ef.EmbeddingClient, "get_embeddings_batch")


# ===========================================================================
# [S-PROMPTS] Prompt Registry surface
# ===========================================================================


class TestPromptRegistrySurface:
    """PromptRegistry register/get/render/search/delete contract."""

    @pytest.mark.unit
    def test_register_and_get_template(self) -> None:
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            registry = PromptRegistry(registry_path=tmp / "test_registry.json", enable_logging=False)
            tmpl = PromptTemplate(
                template_id="t_adg_001",
                name="ADG Test Template",
                category=PromptCategory.TASK_TEMPLATE,
                content="Run ADG for {territory}.",
                version="1.0.0",
                variables=["territory"],
            )
            registry.register(tmpl)
            retrieved = registry.get("t_adg_001")
            assert retrieved is not None
            assert retrieved.template_id == "t_adg_001"
            assert retrieved.category == PromptCategory.TASK_TEMPLATE
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_render_substitutes_variables(self) -> None:
        from apps_shared.utils.prompt_registry_util import PromptCategory, PromptTemplate

        tmpl = PromptTemplate(
            template_id="t_render",
            name="Render Test",
            category=PromptCategory.REASONING_TEMPLATE,
            content="Territory={territory} Agent={agent}",
            version="1.0.0",
            variables=["territory", "agent"],
        )
        rendered = tmpl.render(territory="agentic_core", agent="LocationHealerAgent")
        assert rendered == "Territory=agentic_core Agent=LocationHealerAgent"

    @pytest.mark.unit
    def test_find_by_category_counts_registered_templates(self) -> None:
        """find_by_category returns only templates matching the given category.

        Counts defaults seeded at construction time, then verifies 3 more are added.
        """
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            registry = PromptRegistry(registry_path=tmp / "cat_test.json", enable_logging=False)
            defaults_safety = len(registry.find_by_category(PromptCategory.SAFETY_POLICY))
            for i in range(3):
                registry.register(
                    PromptTemplate(
                        template_id=f"safety_new_{i}",
                        name=f"Safety New {i}",
                        category=PromptCategory.SAFETY_POLICY,
                        content=f"safety policy {i}",
                        version="1.0.0",
                    )
                )
            safety_tmpls = registry.find_by_category(PromptCategory.SAFETY_POLICY)
            assert len(safety_tmpls) == defaults_safety + 3
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_delete_removes_template(self) -> None:
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            registry = PromptRegistry(registry_path=tmp / "del_test.json", enable_logging=False)
            registry.register(
                PromptTemplate(
                    template_id="to_delete",
                    name="Delete Me",
                    category=PromptCategory.EXAMPLE,
                    content="content",
                    version="1.0.0",
                )
            )
            assert registry.get("to_delete") is not None
            deleted = registry.delete("to_delete")
            assert deleted is True
            assert registry.get("to_delete") is None
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_search_by_name_substring(self) -> None:
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            registry = PromptRegistry(registry_path=tmp / "search_test.json", enable_logging=False)
            registry.register(
                PromptTemplate(
                    template_id="heal_001",
                    name="Healing Template Alpha",
                    category=PromptCategory.TASK_TEMPLATE,
                    content="heal",
                    version="1.0.0",
                )
            )
            results = registry.search("healing")
            assert any(t.template_id == "heal_001" for t in results)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_persists_and_reloads_from_disk(self) -> None:
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            reg_path = tmp / "persist_test.json"
            registry = PromptRegistry(registry_path=reg_path, enable_logging=False)
            registry.register(
                PromptTemplate(
                    template_id="persist_001",
                    name="Persist Test",
                    category=PromptCategory.SYSTEM_INSTRUCTION,
                    content="system instruction",
                    version="1.0.0",
                )
            )
            registry2 = PromptRegistry(registry_path=reg_path, enable_logging=False)
            retrieved = registry2.get("persist_001")
            assert retrieved is not None
            assert retrieved.name == "Persist Test"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_task_template_not_in_safety_policy_category(self) -> None:
        """Templates registered under TASK_TEMPLATE must not appear in SAFETY_POLICY results."""
        from apps_shared.utils.prompt_registry_util import (
            PromptCategory,
            PromptRegistry,
            PromptTemplate,
        )

        tmp = Path(tempfile.mkdtemp())
        try:
            registry = PromptRegistry(registry_path=tmp / "isolation.json", enable_logging=False)
            registry.register(
                PromptTemplate(
                    template_id="task_iso_001",
                    name="Task Isolation",
                    category=PromptCategory.TASK_TEMPLATE,
                    content="task content",
                    version="1.0.0",
                )
            )
            safety_tmpls = registry.find_by_category(PromptCategory.SAFETY_POLICY)
            assert not any(t.template_id == "task_iso_001" for t in safety_tmpls)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# [S-SL] System Learning surface (memory bridge)
# ===========================================================================


class TestSystemLearningBridgeSurface:
    """_record_healing_action wires system_learning_memory_bridge persist calls."""

    @pytest.mark.unit
    def test_record_healing_action_calls_persist_success_rate_on_success(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}
        mock_bridge = MagicMock()

        with patch(_SL_BRIDGE_PATCH, return_value=mock_bridge):
            _record_healing_action(
                mock_state_mgr,
                agent="LocationHealerAgent",
                territory="agentic_core",
                routing_tier="DETERMINISTIC",
                confidence=0.9,
                fix_summary="moved 1 file",
                outcome="SUCCESS",
            )

        mock_bridge.persist_healing_success_rate.assert_called_once()
        call_kwargs = mock_bridge.persist_healing_success_rate.call_args.kwargs
        assert call_kwargs.get("rate") == 1.0

    @pytest.mark.unit
    def test_record_healing_action_calls_persist_failure_pattern_on_failure(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}
        mock_bridge = MagicMock()

        with patch(_SL_BRIDGE_PATCH, return_value=mock_bridge):
            _record_healing_action(
                mock_state_mgr,
                agent="ArchitectureGovernorAgent",
                territory="agentic_core",
                routing_tier="DETERMINISTIC",
                confidence=0.3,
                fix_summary="governance check failed",
                outcome="FAILURE",
            )

        mock_bridge.persist_healing_success_rate.assert_called_once()
        mock_bridge.persist_failure_pattern.assert_called_once()
        call_kwargs = mock_bridge.persist_healing_success_rate.call_args.kwargs
        assert call_kwargs.get("rate") == 0.0

    @pytest.mark.unit
    def test_record_healing_action_success_does_not_call_persist_failure_pattern(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}
        mock_bridge = MagicMock()

        with patch(_SL_BRIDGE_PATCH, return_value=mock_bridge):
            _record_healing_action(
                mock_state_mgr,
                agent="HierarchyHealerAgent",
                territory="agentic_core",
                routing_tier="DETERMINISTIC",
                confidence=0.95,
                fix_summary="hierarchy fixed",
                outcome="SUCCESS",
            )

        mock_bridge.persist_failure_pattern.assert_not_called()

    @pytest.mark.unit
    def test_sl_bridge_error_does_not_raise_from_record_healing_action(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}

        with patch(_SL_BRIDGE_PATCH, side_effect=RuntimeError("bridge unavailable")):
            try:
                _record_healing_action(
                    mock_state_mgr,
                    agent="DependencyPruningAgent",
                    territory="agentic_core",
                    routing_tier="DETERMINISTIC",
                    confidence=0.5,
                    fix_summary="deps pruned",
                    outcome="SUCCESS",
                )
            except Exception as exc:
                pytest.fail(f"_record_healing_action raised on bridge failure: {exc}")

    @pytest.mark.unit
    def test_healing_action_appended_to_state(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import _record_healing_action

        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}
        mock_bridge = MagicMock()

        with patch(_SL_BRIDGE_PATCH, return_value=mock_bridge):
            _record_healing_action(
                mock_state_mgr,
                agent="RootHygieneHealerAgent",
                territory="agentic_core",
                routing_tier="DETERMINISTIC",
                confidence=1.0,
                fix_summary="root clean",
                outcome="SUCCESS",
            )

        actions = mock_state_mgr.state["healing_actions"]
        assert len(actions) == 1
        action = actions[0]
        assert action["agent"] == "RootHygieneHealerAgent"
        assert action["outcome"] == "SUCCESS"
        assert action["territory"] == "agentic_core"


# ===========================================================================
# [S-PIPE] _ssot_pipeline structure invariants
# ===========================================================================


class TestSSoTPipelineStructureInvariants:
    """EXECUTION_PLAN, AGENT_PIPELINE and CANONICAL_ROSTER_KEYS structural contracts."""

    @pytest.mark.unit
    def test_execution_plan_has_required_phases(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import EXECUTION_PLAN

        phases = [p["phase"] for p in EXECUTION_PLAN]
        assert "1" in phases
        assert "7" in phases
        assert len(EXECUTION_PLAN) >= 6

    @pytest.mark.unit
    def test_agent_pipeline_is_ordered_list(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import AGENT_PIPELINE

        assert isinstance(AGENT_PIPELINE, list)
        assert len(AGENT_PIPELINE) >= 5
        assert AGENT_PIPELINE.index("reconciler") < AGENT_PIPELINE.index("location")

    @pytest.mark.unit
    def test_canonical_roster_keys_is_frozenset(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import CANONICAL_ROSTER_KEYS

        assert isinstance(CANONICAL_ROSTER_KEYS, frozenset)
        assert "reconciler" in CANONICAL_ROSTER_KEYS
        assert "arch_governor" in CANONICAL_ROSTER_KEYS
        assert "location" in CANONICAL_ROSTER_KEYS

    @pytest.mark.unit
    def test_pipeline_subphases_four_slots(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import PIPELINE_SUBPHASES

        assert set(PIPELINE_SUBPHASES) == {"pre_commit", "validate", "execute", "heal"}

    @pytest.mark.unit
    def test_agent_dependencies_arch_governor_depends_on_location(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import AGENT_DEPENDENCIES

        assert "location" in AGENT_DEPENDENCIES.get("arch_governor", [])

    @pytest.mark.unit
    def test_resolve_agent_subset_closure_includes_dependencies(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import resolve_agent_subset

        result = resolve_agent_subset(["arch_governor"])
        assert "reconciler" in result
        assert "location" in result
        assert "hierarchy" in result
        assert "arch_governor" in result

    @pytest.mark.unit
    def test_resolve_agent_subset_raises_on_unknown_key(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import resolve_agent_subset

        with pytest.raises(ValueError, match="Unknown agent key"):
            resolve_agent_subset(["nonexistent_agent_xyz"])

    @pytest.mark.unit
    def test_execution_plan_phase4_contains_arch_governor(self) -> None:
        from agentic_core.L0_routing.scripts._ssot_pipeline import EXECUTION_PLAN

        phase4 = next((p for p in EXECUTION_PLAN if p["phase"] == "4"), None)
        assert phase4 is not None
        agent_keys = [a["key"] for a in phase4["agents"]]
        assert "arch_governor" in agent_keys


# ===========================================================================
# [S-ADG-INT] execute_ssot_integration.build_pre_run_report surface
# ===========================================================================


class TestExecuteSSOTIntegrationSurface:
    """build_pre_run_report graceful degradation and structure contracts."""

    @pytest.mark.unit
    def test_returns_unavailable_report_on_runtime_error(self) -> None:
        """build_pre_run_report must return unavailable report when ADG scan fails."""
        import agentic_core.adg.runtime.cache_loader as _cl_mod
        from agentic_core.adg.applications.PreRunADGReport import build_pre_run_report

        tmp = Path(tempfile.mkdtemp())
        try:
            with patch.object(_cl_mod, "load_or_scan", side_effect=RuntimeError("ADG scan failed")):
                report = build_pre_run_report(changed_files=["some/file.py"], repo_root=tmp)

            assert report.adg_available is False
            assert report.route_mode == "NORMAL"
            assert report.risk_score == 0
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @pytest.mark.unit
    def test_unavailable_classmethod_sets_changed_files(self) -> None:
        from agentic_core.adg.applications.PreRunADGReport import PreRunADGReport

        report = PreRunADGReport.unavailable(["a.py", "b.py"], "test reason")
        assert report.adg_available is False
        assert sorted(report.changed_files) == ["a.py", "b.py"]
        assert report.adg_error == "test reason"
        assert report.route_mode == "NORMAL"

    @pytest.mark.unit
    def test_pre_run_report_to_dict_has_summary_key(self) -> None:
        from agentic_core.adg.applications.PreRunADGReport import PreRunADGReport

        report = PreRunADGReport.unavailable([], "no adg")
        d = report.to_dict()
        assert "summary" in d
        assert "route_mode" in d
        assert "risk_score" in d
        assert "adg_available" in d

    @pytest.mark.unit
    def test_emit_pre_run_log_handles_unavailable_gracefully(self) -> None:
        from agentic_core.adg.applications.PreRunADGReport import (
            PreRunADGReport,
            emit_pre_run_log,
        )

        report = PreRunADGReport.unavailable([], "ADG offline")
        emit_pre_run_log(report)  # must not raise


# ===========================================================================
# [S-ADG-GP] GuardianPrioritizer — roster compatibility and ordered output
# ===========================================================================


class TestGuardianPrioritizerPipelineIntegration:
    """GuardianPrioritizer.prioritize must produce ordered output compatible with pipeline roster."""

    @pytest.mark.unit
    def test_prioritize_with_canonical_roster_keys(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer_types import GuardianPrioritizer
        from agentic_core.L0_routing.scripts._ssot_pipeline import CANONICAL_ROSTER_KEYS

        scan = _make_empty_scan_result()
        prio = GuardianPrioritizer(scan).prioritize(guardian_ids=list(CANONICAL_ROSTER_KEYS))
        scored_ids = {s.guardian_id for s in prio.scores}
        for key in CANONICAL_ROSTER_KEYS:
            assert key in scored_ids, f"Roster key {key!r} missing from prioritization output"

    @pytest.mark.unit
    def test_cross_layer_violation_raises_hierarchy_compliance_priority(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer_types import GuardianPrioritizer
        from agentic_core.L0_routing.scripts._ssot_pipeline import CANONICAL_ROSTER_KEYS

        empty_scan = _make_empty_scan_result()
        cl_scan = _make_cross_layer_scan_result()

        prio_empty = GuardianPrioritizer(empty_scan).prioritize(guardian_ids=list(CANONICAL_ROSTER_KEYS))
        prio_cl = GuardianPrioritizer(cl_scan).prioritize(guardian_ids=list(CANONICAL_ROSTER_KEYS))

        def _score(prio, gid):
            return next((s.score for s in prio.scores if s.guardian_id == gid), 0)

        assert _score(prio_cl, "hierarchy_compliance") >= _score(prio_empty, "hierarchy_compliance")

    @pytest.mark.unit
    def test_ordered_output_is_list_of_strings_when_extracted(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer_types import GuardianPrioritizer
        from agentic_core.L0_routing.scripts._ssot_pipeline import CANONICAL_ROSTER_KEYS

        scan = _make_empty_scan_result()
        prio = GuardianPrioritizer(scan).prioritize(guardian_ids=list(CANONICAL_ROSTER_KEYS))
        guardian_scope = [s.guardian_id for s in prio.ordered()]
        assert all(isinstance(gid, str) for gid in guardian_scope)
        assert set(guardian_scope) == set(CANONICAL_ROSTER_KEYS)

    @pytest.mark.unit
    def test_priority_digest_is_16_char_hex(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer_types import GuardianPrioritizer

        scan = _make_empty_scan_result()
        prio = GuardianPrioritizer(scan).prioritize()
        assert len(prio.adg_signals_digest) == 16
        assert all(c in "0123456789abcdef" for c in prio.adg_signals_digest)
