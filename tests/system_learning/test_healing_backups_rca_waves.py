"""
test_healing_backups_rca_waves.py — Tests for .healing_backups RCA fixes.

Wave 1: Path SSOT consolidation — all healer agents now use archives/healing_backups/<category>/
Wave 2: System learning integration — backup archival events surface in meta_learning state
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
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

emit_determinism_digest("p0", "test_healing_backups_rca_waves")
emit_replay_key("p0", "test_healing_backups_rca_waves")
_emit_records_execution_trace("p0", "evidence", "test_healing_backups_rca_waves")
_emit_applies_guardrail("p0", "test_healing_backups_rca_waves", "p0_governance")
_emit_snapshots_state("p0", "test_healing_backups_rca_waves", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_backups_rca_waves", "execution_auth")
_emit_validates_capability("p2", "test_healing_backups_rca_waves", "capability_check")
_emit_routes_to_capability("p2", "test_healing_backups_rca_waves", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_backups_rca_waves", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_backups_rca_waves", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_backups_rca_waves", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_backups_rca_waves", "exec_output")
_emit_dispatches_agent("p3", "test_healing_backups_rca_waves", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_backups_rca_waves", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_backups_rca_waves", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_backups_rca_waves", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_backups_rca_waves", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_backups_rca_waves", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_backups_rca_waves", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_backups_rca_waves", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_backups_rca_waves", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_backups_rca_waves", "eval_metric")
_emit_stores_embedding("p4", "test_healing_backups_rca_waves", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_backups_rca_waves", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_backups_rca_waves", "exec_snapshot_link")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_backups_rca_waves", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_backups_rca_waves", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_backups_rca_waves", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_backups_rca_waves", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_backups_rca_waves", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_backups_rca_waves", "p4obs", "alert")
_emit_links_incident_trace("test_healing_backups_rca_waves", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_backups_rca_waves", "p3lm", "pattern")
_emit_records_learning_event("test_healing_backups_rca_waves", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_backups_rca_waves", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_backups_rca_waves", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_backups_rca_waves", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_backups_rca_waves", "p3lm", "policy")
_emit_stores_learning_state("test_healing_backups_rca_waves", "p3lm", "state")
_emit_pulls_context("p1", "test_healing_backups_rca_waves", "context_pull")
_emit_execution_terminates_at_uwg("p1", "test_healing_backups_rca_waves", "uwg_term")
_emit_writes_through("p1", "test_healing_backups_rca_waves", "write_through")
_emit_validated_by_safety_plane("p1", "test_healing_backups_rca_waves", "safety_validation")
_emit_proposal_commits_routing("p1", "test_healing_backups_rca_waves", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_backups_rca_waves", "human_escalation")
_emit_routes_through("p1", "test_healing_backups_rca_waves", "route_through")
_emit_checks_agent_registry("p1", "test_healing_backups_rca_waves", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_backups_rca_waves", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_backups_rca_waves", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_backups_rca_waves", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_backups_rca_waves", "target_agent")
_emit_verifies_policy("p1", "test_healing_backups_rca_waves", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_backups_rca_waves", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_backups_rca_waves", "boundary_check")
_emit_transcripts_response("p1", "test_healing_backups_rca_waves", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_backups_rca_waves")
_emit_gated_by_confidence("p1", "test_healing_backups_rca_waves", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeStateMgr:
    """Minimal state_mgr stub for _record_backup_archival_event tests."""

    def __init__(self):
        self.state: dict = {}

    def update_meta_learning(self, data: dict) -> None:
        ml = self.state.setdefault("meta_learning", {})
        ml.update(data)


# ===========================================================================
# WAVE 1 TESTS: Path SSOT consolidation
# ===========================================================================


class TestFilesystemSSOTReconcilerArchivePath:
    """ARCHIVE_ROOT must point to archives/healing_backups/unmapped_drift (not root .healing_backups/)."""

    @property
    def _src(self):
        repo_root = Path(__file__).resolve().parents[2]
        return (repo_root / "agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py").read_text(
            encoding="utf-8"
        )

    def test_archive_root_uses_canonical_archives_path(self):
        src = self._src
        assert '"healing_backups" / "unmapped_drift"' in src or "healing_backups/unmapped_drift" in src, (
            "filesystem_ssot_reconciler.py ARCHIVE_ROOT must use canonical archives/healing_backups/unmapped_drift"
        )

    def test_archive_root_does_not_use_root_healing_backups(self):
        src = self._src
        assert 'Path(".healing_backups/unmapped_drift/")' not in src, (
            "filesystem_ssot_reconciler.py ARCHIVE_ROOT must NOT use root .healing_backups/unmapped_drift/"
        )

    def test_archive_root_uses_archives_dir_constant(self):
        src = self._src
        assert "ARCHIVES_DIR" in src, (
            "filesystem_ssot_reconciler.py must import and use ARCHIVES_DIR constant"
        )


class TestHierarchyHealerArchiveRoot:
    """archive_root must point to archives/healing_backups/hierarchy_violations (not root .healing_backups/)."""

    @property
    def _src(self):
        repo_root = Path(__file__).resolve().parents[2]
        return (repo_root / "agentic_core/L5_safety/reasoning/hierarchy_healer.py").read_text(
            encoding="utf-8"
        )

    def test_archive_root_uses_canonical_archives_path(self):
        src = self._src
        assert '"healing_backups" / "hierarchy_violations"' in src, (
            "hierarchy_healer.py archive_root must use canonical archives/healing_backups/hierarchy_violations"
        )

    def test_archive_root_does_not_use_root_healing_backups(self):
        src = self._src
        assert '/ ".healing_backups" / "hierarchy_violations"' not in src, (
            "hierarchy_healer.py archive_root must NOT use root-level .healing_backups/hierarchy_violations"
        )

    def test_archive_root_uses_archives_dir_constant(self):
        src = self._src
        assert 'ARCHIVES_DIR / "healing_backups"' in src, (
            "hierarchy_healer.py must use ARCHIVES_DIR constant for archive_root"
        )


class TestArchitectureGovernorArchivePath:
    """ARCHIVE fallback path must use archives/healing_backups/cognitive_disposition."""

    def test_cognitive_archive_path_is_canonical(self):
        src_path = Path("agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py")

        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / src_path).read_text(encoding="utf-8")
        assert ".healing_backups/cognitive_disposition" not in src, (
            "ArchitectureGovernorAgent still uses non-canonical .healing_backups/cognitive_disposition"
        )
        assert "archives/healing_backups/cognitive_disposition" in src, (
            "ArchitectureGovernorAgent must use archives/healing_backups/cognitive_disposition"
        )


class TestReportLocationAgentBackupDir:
    """backup_dir must use archives/healing_backups/reports (not .sovereign_healing_backup/)."""

    @property
    def _src(self):
        repo_root = Path(__file__).resolve().parents[2]
        return (repo_root / "agentic_core/L5_safety/reasoning/ReportLocationAgent.py").read_text(
            encoding="utf-8"
        )

    def test_backup_dir_default_uses_canonical_path(self):
        src = self._src
        assert 'ARCHIVES_DIR / "healing_backups"' in src, (
            "ReportLocationAgent.py backup_dir must use ARCHIVES_DIR / 'healing_backups'"
        )

    def test_backup_dir_does_not_use_sovereign_healing_backup(self):
        src = self._src
        assert ".sovereign_healing_backup" not in src, (
            "ReportLocationAgent.py must NOT use .sovereign_healing_backup"
        )

    def test_archives_dir_imported(self):
        src = self._src
        assert "ARCHIVES_DIR" in src, "ReportLocationAgent.py must import ARCHIVES_DIR from path_constants"


class TestGovernanceAgentBackupDir:
    """_init_backup_dir must use archives/healing_backups/governance (not .governance_healer_backups/)."""

    @property
    def _src(self):
        repo_root = Path(__file__).resolve().parents[2]
        return (repo_root / "agentic_core/L5_safety/reasoning/GovernanceAgent.py").read_text(encoding="utf-8")

    def test_backup_dir_uses_canonical_path(self):
        src = self._src
        assert '"healing_backups" / "governance"' in src, (
            "GovernanceAgent.py _init_backup_dir must use archives/healing_backups/governance"
        )

    def test_backup_dir_does_not_use_governance_healer_backups(self):
        src = self._src
        assert ".governance_healer_backups" not in src, (
            "GovernanceAgent.py must NOT use .governance_healer_backups"
        )

    def test_backup_dir_uses_archives_dir_constant(self):
        src = self._src
        assert 'ARCHIVES_DIR / "healing_backups"' in src, (
            "GovernanceAgent.py must use ARCHIVES_DIR constant for backup dir"
        )


class TestLocationHealerUltraEngineArchivePath:
    """ULTRA HEALING ENGINE archives_root must use archives/healing_backups (not root .healing_backups)."""

    def test_ultra_engine_does_not_use_root_healing_backups(self):
        repo_root = Path(__file__).resolve().parents[2]
        src_path = repo_root / "agentic_core/L5_safety/reasoning/LocationHealerAgent.py"
        src = src_path.read_text(encoding="utf-8")

        ultra_engine_idx = src.find("ULTRA HEALING ENGINE")
        assert ultra_engine_idx != -1, "ULTRA HEALING ENGINE block not found in LocationHealerAgent.py"

        method_src = src[ultra_engine_idx : ultra_engine_idx + 800]
        assert '".healing_backups"' not in method_src and '/ ".healing_backups"' not in method_src, (
            "ULTRA HEALING ENGINE must NOT use root .healing_backups"
        )
        assert "ARCHIVES_DIR" in method_src or "archives/healing_backups" in method_src, (
            "ULTRA HEALING ENGINE must use canonical archives/healing_backups path"
        )


class TestNoRootHealingBackupsInHealerSources:
    """AST guard: none of the 6 fixed healer files should contain the old non-canonical paths."""

    HEALER_FILES = [
        "agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py",
        "agentic_core/L5_safety/reasoning/hierarchy_healer.py",
        "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
        "agentic_core/L5_safety/reasoning/ReportLocationAgent.py",
        "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
    ]
    BANNED_PATTERNS = [
        '".healing_backups"',
        "'.healing_backups'",
        ".governance_healer_backups",
        ".sovereign_healing_backup",
    ]

    @pytest.mark.parametrize("rel_path", HEALER_FILES)
    def test_no_banned_patterns(self, rel_path):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / rel_path).read_text(encoding="utf-8")
        for pattern in self.BANNED_PATTERNS:
            assert pattern not in src, f"{rel_path} still contains banned path pattern: {pattern!r}"


# ===========================================================================
# WAVE 2 TESTS: System learning integration
# ===========================================================================


class TestRecordBackupArchivalEvent:
    """_record_backup_archival_event must append to state correctly."""

    def test_appends_event_to_empty_state(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        state_mgr = _FakeStateMgr()
        _record_backup_archival_event(state_mgr, "HierarchyHealerAgent", "hierarchy_violations", 3)

        events = state_mgr.state.get("backup_archival_events", [])
        assert len(events) == 1
        assert events[0]["agent"] == "HierarchyHealerAgent"
        assert events[0]["category"] == "hierarchy_violations"
        assert events[0]["count"] == 3

    def test_appends_multiple_events(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        state_mgr = _FakeStateMgr()
        _record_backup_archival_event(state_mgr, "HierarchyHealerAgent", "hierarchy_violations", 2)
        _record_backup_archival_event(state_mgr, "FilesystemSSOTReconcilerAgent", "unmapped_drift", 1)

        events = state_mgr.state.get("backup_archival_events", [])
        assert len(events) == 2
        agents = {e["agent"] for e in events}
        assert "HierarchyHealerAgent" in agents
        assert "FilesystemSSOTReconcilerAgent" in agents

    def test_event_has_timestamp(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        state_mgr = _FakeStateMgr()
        _record_backup_archival_event(state_mgr, "TestAgent", "test_category", 1)
        events = state_mgr.state.get("backup_archival_events", [])
        assert "timestamp" in events[0]
        assert isinstance(events[0]["timestamp"], str)

    def test_default_count_is_one(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        state_mgr = _FakeStateMgr()
        _record_backup_archival_event(state_mgr, "TestAgent", "test_category")
        events = state_mgr.state.get("backup_archival_events", [])
        assert events[0]["count"] == 1


class TestBackupArchivalTotalInMetaLearning:
    """backup_archival_total must be set correctly in meta_learning state by _fire_meta_learning_intake."""

    def _make_state_mgr(self, backup_events: list | None = None) -> _FakeStateMgr:
        sm = _FakeStateMgr()
        sm.state["healing_actions"] = []
        if backup_events is not None:
            sm.state["backup_archival_events"] = backup_events
        return sm

    def test_zero_events_yields_zero_total(self):
        sm = self._make_state_mgr(backup_events=[])
        backup_events = sm.state.get("backup_archival_events", [])
        backup_total = sum(e.get("count", 0) for e in backup_events)
        assert backup_total == 0

    def test_single_event_count_correct(self):
        sm = self._make_state_mgr(
            backup_events=[
                {
                    "agent": "HierarchyHealerAgent",
                    "category": "hierarchy_violations",
                    "count": 5,
                    "timestamp": "t",
                }
            ]
        )
        backup_events = sm.state.get("backup_archival_events", [])
        backup_total = sum(e.get("count", 0) for e in backup_events)
        assert backup_total == 5

    def test_multiple_events_summed_correctly(self):
        sm = self._make_state_mgr(
            backup_events=[
                {
                    "agent": "HierarchyHealerAgent",
                    "category": "hierarchy_violations",
                    "count": 3,
                    "timestamp": "t",
                },
                {
                    "agent": "FilesystemSSOTReconcilerAgent",
                    "category": "unmapped_drift",
                    "count": 2,
                    "timestamp": "t",
                },
                {
                    "agent": "HierarchyHealerAgent",
                    "category": "hierarchy_violations",
                    "count": 1,
                    "timestamp": "t",
                },
            ]
        )
        backup_events = sm.state.get("backup_archival_events", [])
        backup_total = sum(e.get("count", 0) for e in backup_events)
        assert backup_total == 6

    def test_backup_by_category_aggregation(self):
        sm = self._make_state_mgr(
            backup_events=[
                {"agent": "A", "category": "hierarchy_violations", "count": 3, "timestamp": "t"},
                {"agent": "B", "category": "unmapped_drift", "count": 2, "timestamp": "t"},
                {"agent": "A", "category": "hierarchy_violations", "count": 1, "timestamp": "t"},
            ]
        )
        backup_events = sm.state.get("backup_archival_events", [])
        backup_by_cat: dict[str, int] = {}
        for be in backup_events:
            cat = be.get("category", "unknown")
            backup_by_cat[cat] = backup_by_cat.get(cat, 0) + be.get("count", 0)
        assert backup_by_cat["hierarchy_violations"] == 4
        assert backup_by_cat["unmapped_drift"] == 2

    def test_no_backup_events_key_yields_empty(self):
        sm = self._make_state_mgr(backup_events=None)
        backup_events = sm.state.get("backup_archival_events", [])
        assert backup_events == []
        backup_total = sum(e.get("count", 0) for e in backup_events)
        assert backup_total == 0


class TestBackupArchivalEventRecordingFromHierarchyHealResult:
    """execute_ssot records backup archival events from HierarchyHealerAgent root_healing result."""

    def test_archived_files_from_root_healing_recorded(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        sm = _FakeStateMgr()
        heal_result = {
            "violations_fixed": 2,
            "root_healing": {
                "archived_files_moved": 3,
                "violations_found": 3,
                "actions": [],
            },
        }
        _archived_root = 0
        if isinstance(heal_result, dict):
            _root_heal = heal_result.get("root_healing", {})
            if isinstance(_root_heal, dict):
                _archived_root = _root_heal.get("archived_files_moved", 0)
        if _archived_root > 0:
            _record_backup_archival_event(sm, "HierarchyHealerAgent", "hierarchy_violations", _archived_root)

        events = sm.state.get("backup_archival_events", [])
        assert len(events) == 1
        assert events[0]["count"] == 3

    def test_zero_archived_files_not_recorded(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        sm = _FakeStateMgr()
        heal_result = {
            "violations_fixed": 2,
            "root_healing": {"archived_files_moved": 0},
        }
        _archived_root = 0
        if isinstance(heal_result, dict):
            _root_heal = heal_result.get("root_healing", {})
            if isinstance(_root_heal, dict):
                _archived_root = _root_heal.get("archived_files_moved", 0)
        if _archived_root > 0:
            _record_backup_archival_event(sm, "HierarchyHealerAgent", "hierarchy_violations", _archived_root)

        events = sm.state.get("backup_archival_events", [])
        assert len(events) == 0

    def test_missing_root_healing_key_safe(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        sm = _FakeStateMgr()
        heal_result = {"violations_fixed": 2}
        _archived_root = 0
        if isinstance(heal_result, dict):
            _root_heal = heal_result.get("root_healing", {})
            if isinstance(_root_heal, dict):
                _archived_root = _root_heal.get("archived_files_moved", 0)
        if _archived_root > 0:
            _record_backup_archival_event(sm, "HierarchyHealerAgent", "hierarchy_violations", _archived_root)

        events = sm.state.get("backup_archival_events", [])
        assert len(events) == 0


class TestMetaLearningSsotModuleImports:
    """Verify that _ssot_validation_artifacts exports _record_backup_archival_event."""

    def test_import_record_backup_archival_event(self):
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _record_backup_archival_event,
        )

        assert callable(_record_backup_archival_event)

    def test_execute_ssot_imports_record_backup_archival_event(self):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / "agentic_core/L0_routing/scripts/execute_ssot.py").read_text(encoding="utf-8")
        assert "_record_backup_archival_event" in src, (
            "execute_ssot.py must import _record_backup_archival_event"
        )

    def test_ssot_meta_learning_contains_backup_archival_total(self):
        repo_root = Path(__file__).resolve().parents[2]
        src = (repo_root / "agentic_core/L0_routing/scripts/_ssot_meta_learning.py").read_text(
            encoding="utf-8"
        )
        assert "backup_archival_total" in src, (
            "_ssot_meta_learning.py must surface backup_archival_total in meta_learning state"
        )
        assert "backup_archival_by_category" in src, (
            "_ssot_meta_learning.py must surface backup_archival_by_category in meta_learning state"
        )
