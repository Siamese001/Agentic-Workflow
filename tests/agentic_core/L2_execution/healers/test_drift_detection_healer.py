"""
Tests for the drift_detection_healer (plan-only, no repo mutations).

Proves:
1. Healer produces sorted planned actions from evidence.
2. Missing evidence yields empty changes_made.
3. Status is always SKIPPED (dry-run).
4. Notes are correct.
"""

from __future__ import annotations

from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.types.heal_contract import HealStatus


class TestDriftDetectionHealer:
    """Proves healer produces correct plan-only output."""

    def test_planned_actions_sorted(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "drift found",
            "evidence": {
                "forbidden_folders": ["z_folder", "a_folder"],
                "archived_files_at_root": ["old_readme.bak"],
                "duplicate_folders": ["utils_copy"],
            },
        }
        result = heal_guardian_drift_detection(check)
        assert result.changes_made == (
            "would_remove_archived_file:old_readme.bak",
            "would_remove_root_folder:a_folder",
            "would_remove_root_folder:z_folder",
            "would_resolve_duplicate_folder:utils_copy",
        )

    def test_status_skipped(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {"forbidden_folders": ["tmp"]},
        }
        result = heal_guardian_drift_detection(check)
        assert result.status == HealStatus.SKIPPED

    def test_notes_correct(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {},
        }
        result = heal_guardian_drift_detection(check)
        assert result.notes == "dry-run healer planned actions"

    def test_check_id_passthrough(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {},
        }
        result = heal_guardian_drift_detection(check)
        assert result.check_id == "guardian_drift_detection"

    def test_missing_evidence_keys_empty_changes(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {},
        }
        result = heal_guardian_drift_detection(check)
        assert result.changes_made == ()
        assert result.status == HealStatus.SKIPPED

    def test_no_evidence_field_empty_changes(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
        }
        result = heal_guardian_drift_detection(check)
        assert result.changes_made == ()

    def test_non_dict_evidence_empty_changes(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": "not_a_dict",
        }
        result = heal_guardian_drift_detection(check)
        assert result.changes_made == ()

    def test_empty_string_entries_ignored(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {
                "forbidden_folders": ["valid", "", "also_valid"],
            },
        }
        result = heal_guardian_drift_detection(check)
        assert result.changes_made == (
            "would_remove_root_folder:also_valid",
            "would_remove_root_folder:valid",
        )

    def test_rollback_info_is_none(self) -> None:
        check = {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "",
            "evidence": {"forbidden_folders": ["x"]},
        }
        result = heal_guardian_drift_detection(check)
        assert result.rollback_info is None
