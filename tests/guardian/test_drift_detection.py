"""
Tests for the drift_detection guardian.

Proves:
1. Contract validity — produces schema-valid GuardianResult
2. No side effects — only explicit output JSON written, no other files modified
3. Stable check_id set — emitted check_ids == {"root_drift"}
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_maintenance.scripts.run_guardian_drift_detection import (
    GUARDIAN_ID,
    run_drift_detection_guardian,
    scan_archived_files_at_root,
    scan_duplicate_ssot_folders,
    scan_forbidden_root_folders,
)
from agentic_core.L0_maintenance.types.guardian_contract import (
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    """Minimal repo tree that passes all drift checks."""
    (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L0_maintenance" / "logs").mkdir(parents=True)
    (tmp_path / "agentic_core" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("# clean\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def dirty_repo(tmp_path: Path) -> Path:
    """Repo tree with all three drift conditions triggered."""
    # SSOT locations (must exist for duplicate detection)
    (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L0_maintenance" / "logs").mkdir(parents=True)

    # Drift condition 1: forbidden folders at root
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()

    # Drift condition 2: archived files at root
    (tmp_path / "old_config.backup").write_text("x", encoding="utf-8")
    (tmp_path / "removed.archived").write_text("y", encoding="utf-8")

    # Drift condition 3: duplicates (scripts/ and logs/ at root + SSOT)
    # Already created above

    return tmp_path


# ---------------------------------------------------------------------------
# Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanForbiddenRootFolders:
    def test_clean_repo_no_hits(self, clean_repo: Path) -> None:
        assert scan_forbidden_root_folders(clean_repo) == []

    def test_dirty_repo_detects_forbidden(self, dirty_repo: Path) -> None:
        hits = scan_forbidden_root_folders(dirty_repo)
        assert "scripts" in hits
        assert "logs" in hits
        assert hits == sorted(hits)

    def test_only_forbidden_names_detected(self, tmp_path: Path) -> None:
        (tmp_path / "allowed_folder").mkdir()
        (tmp_path / "src").mkdir()
        assert scan_forbidden_root_folders(tmp_path) == []

    def test_files_not_detected(self, tmp_path: Path) -> None:
        (tmp_path / "scripts").write_text("file not dir", encoding="utf-8")
        assert scan_forbidden_root_folders(tmp_path) == []


class TestScanArchivedFilesAtRoot:
    def test_clean_repo_no_hits(self, clean_repo: Path) -> None:
        assert scan_archived_files_at_root(clean_repo) == []

    def test_dirty_repo_detects_archived(self, dirty_repo: Path) -> None:
        hits = scan_archived_files_at_root(dirty_repo)
        assert len(hits) == 2
        assert hits == sorted(hits)

    def test_all_patterns_detected(self, tmp_path: Path) -> None:
        (tmp_path / "a.archived").write_text("", encoding="utf-8")
        (tmp_path / "b.backup").write_text("", encoding="utf-8")
        (tmp_path / "c.old").write_text("", encoding="utf-8")
        hits = scan_archived_files_at_root(tmp_path)
        assert len(hits) == 3

    def test_dirs_not_detected(self, tmp_path: Path) -> None:
        (tmp_path / "something.archived").mkdir()
        assert scan_archived_files_at_root(tmp_path) == []


class TestScanDuplicateSSOTFolders:
    def test_clean_repo_no_hits(self, clean_repo: Path) -> None:
        # clean_repo has SSOT dirs but no root duplicates
        assert scan_duplicate_ssot_folders(clean_repo) == []

    def test_dirty_repo_detects_duplicates(self, dirty_repo: Path) -> None:
        hits = scan_duplicate_ssot_folders(dirty_repo)
        names = [d["name"] for d in hits]
        assert "scripts" in names
        assert "logs" in names
        assert names == sorted(names)

    def test_no_ssot_path_no_duplicate(self, tmp_path: Path) -> None:
        # Root folder exists but SSOT location does not
        (tmp_path / "scripts").mkdir()
        assert scan_duplicate_ssot_folders(tmp_path) == []

    def test_no_root_folder_no_duplicate(self, tmp_path: Path) -> None:
        # SSOT location exists but root folder does not
        (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").mkdir(
            parents=True,
        )
        assert scan_duplicate_ssot_folders(tmp_path) == []


# ---------------------------------------------------------------------------
# Guardian runner contract tests
# ---------------------------------------------------------------------------


class TestDriftDetectionGuardianContract:
    """Proves GuardianResult schema validity."""

    def test_clean_repo_pass(self, clean_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=clean_repo)
        assert result.guardian_id == GUARDIAN_ID
        assert result.status == GuardianStatus.PASS.value

    def test_dirty_repo_fail(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        assert result.guardian_id == GUARDIAN_ID
        assert result.status == GuardianStatus.FAIL.value

    def test_schema_compatibility_clean(self, clean_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=clean_repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_schema_compatibility_dirty(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_no_absolute_paths(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths found: {violations}"

    def test_validate_method_clean(self, clean_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=clean_repo)
        assert result.validate() == []

    def test_validate_method_dirty(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        assert result.validate() == []


# ---------------------------------------------------------------------------
# No side effects
# ---------------------------------------------------------------------------


class TestDriftDetectionNoSideEffects:
    """Prove the guardian writes nothing except the explicit output JSON."""

    def test_no_writes_without_artifact_dir(self, dirty_repo: Path) -> None:
        # Snapshot files before
        before = set()
        for item in dirty_repo.rglob("*"):
            if item.is_file():
                before.add(str(item.relative_to(dirty_repo)))

        run_drift_detection_guardian(repo_root=dirty_repo)

        # Snapshot files after
        after = set()
        for item in dirty_repo.rglob("*"):
            if item.is_file():
                after.add(str(item.relative_to(dirty_repo)))

        assert before == after, f"New files created: {after - before}"

    def test_only_output_json_written(self, dirty_repo: Path) -> None:
        out_dir = "guardian_output"
        before = set()
        for item in dirty_repo.rglob("*"):
            if item.is_file():
                before.add(str(item.relative_to(dirty_repo)))

        run_drift_detection_guardian(
            repo_root=dirty_repo,
            write_artifacts_dir=out_dir,
        )

        after = set()
        for item in dirty_repo.rglob("*"):
            if item.is_file():
                after.add(str(item.relative_to(dirty_repo)))

        new_files = after - before
        assert len(new_files) == 1
        new_file = new_files.pop()
        assert "guardian_drift_detection_result.json" in new_file

        # Verify written JSON is parseable
        full_path = dirty_repo / new_file
        data = json.loads(full_path.read_text(encoding="utf-8"))
        assert data["guardian_id"] == GUARDIAN_ID


# ---------------------------------------------------------------------------
# Stable check_id set
# ---------------------------------------------------------------------------


class TestDriftDetectionStableCheckIds:
    """Prove emitted check_id set is exactly {"root_drift"}."""

    def test_check_ids_clean(self, clean_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=clean_repo)
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"root_drift"}

    def test_check_ids_dirty(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"root_drift"}

    def test_check_ids_empty_dir(self, tmp_path: Path) -> None:
        result = run_drift_detection_guardian(repo_root=tmp_path)
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"root_drift"}

    def test_exactly_one_check(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        assert len(result.checks) == 1


# ---------------------------------------------------------------------------
# Evidence determinism
# ---------------------------------------------------------------------------


class TestDriftDetectionEvidenceDeterminism:
    """Prove evidence lists are sorted and stable across runs."""

    def test_evidence_sorted(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        check = result.checks[0]
        ev = check.evidence
        assert ev["forbidden_folders"] == sorted(ev["forbidden_folders"])
        assert ev["archived_files_at_root"] == sorted(ev["archived_files_at_root"])
        names = [d["name"] for d in ev["duplicate_folders"]]
        assert names == sorted(names)

    def test_idempotent_runs(self, dirty_repo: Path) -> None:
        r1 = run_drift_detection_guardian(repo_root=dirty_repo)
        r2 = run_drift_detection_guardian(repo_root=dirty_repo)
        assert r1.to_dict() == r2.to_dict()

    def test_metrics_present(self, dirty_repo: Path) -> None:
        result = run_drift_detection_guardian(repo_root=dirty_repo)
        assert "forbidden_folder_count" in result.metrics
        assert "archived_file_count" in result.metrics
        assert "duplicate_folder_count" in result.metrics
        assert "drift_detected" in result.metrics
        assert result.metrics["drift_detected"] is True
