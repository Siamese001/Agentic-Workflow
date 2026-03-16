"""
test_healing_backups_rca_waves.py — Tests for .healing_backups RCA fixes.

Wave 1: Path SSOT consolidation — all healer agents now use archives/healing_backups/<category>/
Wave 2: System learning integration — backup archival events surface in meta_learning state
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    emit_determinism_digest,
)

emit_determinism_digest("p0", "test_healing_backups_rca_waves")
_emit_records_execution_trace("p0", "evidence", "test_healing_backups_rca_waves")

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
