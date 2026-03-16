"""
Tests for the drift_detection_healer.

Proves:
1. Dry-run produces sorted planned actions from evidence.
2. Missing evidence yields empty changes_made.
3. Apply mode mutates only within sandbox tmp_path.
4. Idempotency: second apply makes zero additional changes.
5. Non-empty folders are not removed (PARTIAL).
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.types.heal_contract_types import HealStatus
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
)

_emit_records_execution_trace("p0", "evidence", "test_drift_detection_healer")
_emit_applies_guardrail("p0", "test_drift_detection_healer", "p0_governance")
_emit_reads_policy_state("p0", "test_drift_detection_healer", "policy_binding")
_emit_snapshots_state("p0", "test_drift_detection_healer", "state_snapshot")
emit_replay_key("p0", "test_drift_detection_healer")
emit_determinism_digest("p0", "test_drift_detection_healer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_drift_detection_healer", "execution_auth")
_emit_validates_capability("p2", "test_drift_detection_healer", "capability_check")
_emit_routes_to_capability("p2", "test_drift_detection_healer", "capability_route")
_emit_writes_via_uwg("p2", "test_drift_detection_healer", "uwg_write")
_emit_blocks_direct_write("p2", "test_drift_detection_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_drift_detection_healer", "tool_invocation")
_emit_captures_execution_output("p2", "test_drift_detection_healer", "exec_output")
_emit_dispatches_agent("p3", "test_drift_detection_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_drift_detection_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_drift_detection_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_drift_detection_healer", "healing_outcome")
_emit_escalates_failure("p3", "test_drift_detection_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_drift_detection_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_drift_detection_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_drift_detection_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_drift_detection_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_drift_detection_healer", "eval_metric")
_emit_stores_embedding("p4", "test_drift_detection_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_drift_detection_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_drift_detection_healer", "exec_snapshot_link")


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


class TestDriftDetectionHealerApply:
    """Proves apply mode performs safe mutations only within sandbox."""

    @staticmethod
    def _make_check(
        forbidden_folders: list[str] | None = None,
        archived_files: list[str] | None = None,
        duplicate_folders: list[str] | None = None,
    ) -> dict:
        evidence: dict = {}
        if forbidden_folders is not None:
            evidence["forbidden_folders"] = forbidden_folders
        if archived_files is not None:
            evidence["archived_files_at_root"] = archived_files
        if duplicate_folders is not None:
            evidence["duplicate_folders"] = duplicate_folders
        return {
            "check_id": "guardian_drift_detection",
            "status": "FAIL",
            "details": "test",
            "evidence": evidence,
        }

    def test_apply_removes_empty_forbidden_folder(self, tmp_path: Path) -> None:
        (tmp_path / "bad_folder").mkdir()
        check = self._make_check(forbidden_folders=["bad_folder"])
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert not (tmp_path / "bad_folder").exists()
        assert "removed_root_folder:bad_folder" in result.changes_made
        assert result.status == HealStatus.HEALED

    def test_apply_removes_archived_file(self, tmp_path: Path) -> None:
        (tmp_path / "old.bak").write_text("content", encoding="utf-8")
        check = self._make_check(archived_files=["old.bak"])
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert not (tmp_path / "old.bak").exists()
        assert "removed_archived_file:old.bak" in result.changes_made
        assert result.status == HealStatus.HEALED

    def test_apply_skips_non_empty_folder(self, tmp_path: Path) -> None:
        folder = tmp_path / "non_empty"
        folder.mkdir()
        (folder / "keep.txt").write_text("data", encoding="utf-8")
        check = self._make_check(forbidden_folders=["non_empty"])
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert (tmp_path / "non_empty").exists()
        assert result.status == HealStatus.PARTIAL
        assert result.changes_made == ()

    def test_apply_duplicate_folders_never_touched(self, tmp_path: Path) -> None:
        (tmp_path / "dup_a").mkdir()
        (tmp_path / "dup_b").mkdir()
        check = self._make_check(duplicate_folders=["dup_a"])
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert (tmp_path / "dup_a").exists()
        assert result.status == HealStatus.PARTIAL

    def test_apply_idempotent(self, tmp_path: Path) -> None:
        (tmp_path / "empty_dir").mkdir()
        (tmp_path / "old.bak").write_text("x", encoding="utf-8")
        check = self._make_check(
            forbidden_folders=["empty_dir"],
            archived_files=["old.bak"],
        )
        r1 = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert len(r1.changes_made) == 2
        assert r1.status == HealStatus.HEALED

        r2 = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert r2.changes_made == ()
        assert r2.status == HealStatus.HEALED
        assert r2.notes == "healed: nothing to do"

    def test_apply_without_repo_root_fails(self) -> None:
        check = self._make_check(forbidden_folders=["x"])
        result = heal_guardian_drift_detection(check, apply=True)
        assert result.status == HealStatus.FAILED
        assert "repo_root" in (result.notes or "")

    def test_dry_run_does_not_mutate(self, tmp_path: Path) -> None:
        (tmp_path / "bad_folder").mkdir()
        (tmp_path / "old.bak").write_text("x", encoding="utf-8")
        check = self._make_check(
            forbidden_folders=["bad_folder"],
            archived_files=["old.bak"],
        )
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=False)
        assert (tmp_path / "bad_folder").exists()
        assert (tmp_path / "old.bak").exists()
        assert result.status == HealStatus.SKIPPED

    def test_apply_mixed_results(self, tmp_path: Path) -> None:
        (tmp_path / "empty_bad").mkdir()
        non_empty = tmp_path / "full_bad"
        non_empty.mkdir()
        (non_empty / "file.txt").write_text("data", encoding="utf-8")
        (tmp_path / "archive.bak").write_text("old", encoding="utf-8")
        check = self._make_check(
            forbidden_folders=["empty_bad", "full_bad"],
            archived_files=["archive.bak"],
            duplicate_folders=["some_dup"],
        )
        result = heal_guardian_drift_detection(check, repo_root=tmp_path, apply=True)
        assert not (tmp_path / "empty_bad").exists()
        assert (tmp_path / "full_bad").exists()
        assert not (tmp_path / "archive.bak").exists()
        assert result.status == HealStatus.PARTIAL
        assert "removed_archived_file:archive.bak" in result.changes_made
        assert "removed_root_folder:empty_bad" in result.changes_made
        assert result.changes_made == tuple(sorted(result.changes_made))
