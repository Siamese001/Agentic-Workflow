"""
Guardian Hygiene Tests — ReAct-Style (Observe → Verify → Report).

Tests the run_guardian_hygiene script against sandboxed tmp_path fixtures.

Verifies:
1. Clean repo → PASS (all three checks pass)
2. Temp artifact present → FAIL (temp_artifacts check)
3. Empty folder present → FAIL (empty_folders check)
4. Init-only folder present → FAIL (init_only_folders check)
5. Schema compliance of result
6. Determinism: same input → same JSON output
7. Scan budget exceeded → FAIL with ScanBudgetExceeded evidence
8. Exception handling paths → result does not crash
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_hygiene import (
    run_hygiene_guardian,
    scan_empty_folders,
    scan_init_only_folders,
    scan_temp_artifacts,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian

# Use a root name that exists in ROOT_WHITELIST so the scanner actually enters it.
# TESTS_DIR is in ROOT_WHITELIST and is the simplest safe choice for tmp_path fixtures.
_SCAN_ROOT = TESTS_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    """Repo with no temp artifacts, no empty folders, no init-only folders."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    pkg = src / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""pkg"""\n', encoding="utf-8")
    (pkg / "module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_with_temp_artifact(tmp_path: Path) -> Path:
    """Repo containing a .pyc temp artifact inside allowed root."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    (src / "stale.pyc").write_bytes(b"\x00" * 10)
    return tmp_path


@pytest.fixture
def repo_with_empty_folder(tmp_path: Path) -> Path:
    """Repo containing a genuinely empty folder (no .gitkeep)."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    (src / "empty_dir").mkdir()
    return tmp_path


@pytest.fixture
def repo_with_init_only_folder(tmp_path: Path) -> Path:
    """Repo containing a folder with only __init__.py."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    init_pkg = src / "init_only_pkg"
    init_pkg.mkdir()
    (init_pkg / "__init__.py").write_text("", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Clean repo → PASS
# ---------------------------------------------------------------------------


class TestCleanRepoPass:
    def test_clean_repo_returns_pass(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_clean_repo_all_checks_pass(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        fail_checks = [c for c in result.checks if c.status == CheckStatus.FAIL.value]
        assert fail_checks == [], f"Unexpected FAIL checks: {[c.check_id for c in fail_checks]}"

    def test_clean_repo_has_three_checks(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        check_ids = {c.check_id for c in result.checks}
        assert "temp_artifacts" in check_ids
        assert "empty_folders" in check_ids
        assert "init_only_folders" in check_ids

    def test_clean_repo_metrics_populated(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.metrics.get("temp_artifact_count") == 0
        assert result.metrics.get("empty_folder_count") == 0
        assert result.metrics.get("init_only_folder_count") == 0


# ---------------------------------------------------------------------------
# 2. Temp artifact present → FAIL
# ---------------------------------------------------------------------------


class TestTempArtifactFail:
    def test_temp_artifact_returns_fail(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert result.status == GuardianStatus.FAIL.value

    def test_temp_artifact_check_id_fails(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        ta_check = next((c for c in result.checks if c.check_id == "temp_artifacts"), None)
        assert ta_check is not None
        assert ta_check.status == CheckStatus.FAIL.value

    def test_temp_artifact_evidence_contains_path(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        ta_check = next(c for c in result.checks if c.check_id == "temp_artifacts")
        paths = ta_check.evidence.get("paths", [])
        assert len(paths) >= 1
        assert any("stale.pyc" in p for p in paths)

    def test_temp_artifact_remediation_hints_present(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert len(result.remediation_hints) > 0

    def test_temp_artifact_metric_nonzero(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert result.metrics.get("temp_artifact_count", 0) >= 1


# ---------------------------------------------------------------------------
# 3. Empty folder present → FAIL
# ---------------------------------------------------------------------------


class TestEmptyFolderFail:
    def test_empty_folder_returns_fail(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        assert result.status == GuardianStatus.FAIL.value

    def test_empty_folder_check_id_fails(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        ef_check = next((c for c in result.checks if c.check_id == "empty_folders"), None)
        assert ef_check is not None
        assert ef_check.status == CheckStatus.FAIL.value

    def test_empty_folder_evidence_contains_path(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        ef_check = next(c for c in result.checks if c.check_id == "empty_folders")
        paths = ef_check.evidence.get("paths", [])
        assert any("empty_dir" in p for p in paths)

    def test_empty_folder_metric_nonzero(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        assert result.metrics.get("empty_folder_count", 0) >= 1


# ---------------------------------------------------------------------------
# 4. Init-only folder present → FAIL
# ---------------------------------------------------------------------------


class TestInitOnlyFolderFail:
    def test_init_only_returns_fail(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        assert result.status == GuardianStatus.FAIL.value

    def test_init_only_check_id_fails(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        io_check = next((c for c in result.checks if c.check_id == "init_only_folders"), None)
        assert io_check is not None
        assert io_check.status == CheckStatus.FAIL.value

    def test_init_only_evidence_contains_path(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        io_check = next(c for c in result.checks if c.check_id == "init_only_folders")
        paths = io_check.evidence.get("paths", [])
        assert any("init_only_pkg" in p for p in paths)

    def test_init_only_metric_nonzero(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        assert result.metrics.get("init_only_folder_count", 0) >= 1


# ---------------------------------------------------------------------------
# 5. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_schema_compatibility(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_validate_passes(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        errors = result.validate()
        assert errors == [], f"Contract violations: {errors}"

    def test_guardian_id_is_stable(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.guardian_id == "hygiene"

    def test_status_is_known_value(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.status in {"PASS", "FAIL", "ERROR"}

    def test_check_ids_are_registered(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        from agentic_core.L0_routing.types.guardian_registry_types import ALL_GUARDIANS

        spec = next(g for g in ALL_GUARDIANS if g.guardian_id == "hygiene")
        emitted_ids = {c.check_id for c in result.checks}
        for cid in spec.check_ids:
            assert cid in emitted_ids, f"Registered check_id '{cid}' not emitted"


# ---------------------------------------------------------------------------
# 6. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self, clean_repo: Path):
        r1 = run_hygiene_guardian(repo_root=clean_repo)
        r2 = run_hygiene_guardian(repo_root=clean_repo)
        assert r1.to_dict() == r2.to_dict()

    def test_timestamp_injectable(self, clean_repo: Path):
        ts = "2026-01-01T00:00:00Z"
        result = run_hygiene_guardian(repo_root=clean_repo, timestamp=ts)
        assert result.timestamp == ts

    def test_fail_result_same_output_twice(self, repo_with_temp_artifact: Path):
        r1 = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        r2 = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert r1.to_dict() == r2.to_dict()


# ---------------------------------------------------------------------------
# 7. Scan-function unit tests (pure functions, no side-effects)
# ---------------------------------------------------------------------------


class TestScanFunctions:
    def test_scan_temp_artifacts_finds_pyc(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "bad.pyc").write_bytes(b"\x00")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert not isinstance(hits, type(None))
        assert any("bad.pyc" in h for h in hits)

    def test_scan_temp_artifacts_finds_bak(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "old.bak").write_text("x", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert any("old.bak" in h for h in hits)

    def test_scan_temp_artifacts_clean_returns_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "good.py").write_text("x = 1\n", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert hits == []

    def test_scan_temp_artifacts_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_temp_artifacts(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []

    def test_scan_empty_folders_finds_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "hollow").mkdir()
        hits = scan_empty_folders(tmp_path, frozenset({TESTS_DIR}))
        assert any("hollow" in h for h in hits)

    def test_scan_empty_folders_clean_returns_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "pkg").mkdir()
        (src / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        hits = scan_empty_folders(tmp_path, frozenset({TESTS_DIR}))
        assert hits == []

    def test_scan_empty_folders_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_empty_folders(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []

    def test_scan_init_only_folders_finds_violation(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        pkg = src / "lonely_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        hits = scan_init_only_folders(tmp_path, frozenset({TESTS_DIR}))
        assert any("lonely_pkg" in h for h in hits)

    def test_scan_init_only_folders_normal_pkg_not_flagged(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        pkg = src / "normal_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "logic.py").write_text("x = 1\n", encoding="utf-8")
        hits = scan_init_only_folders(tmp_path, frozenset({TESTS_DIR}))
        assert not any("normal_pkg" in h for h in hits)

    def test_scan_init_only_folders_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_init_only_folders(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []


# ---------------------------------------------------------------------------
# 8. Edge cases: empty allowed_roots, multiple violations, PASS boundary
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_allowed_roots_returns_pass(self, tmp_path: Path):
        result = run_hygiene_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.PASS.value

    def test_multiple_violations_all_reported(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / "stale.pyc").write_bytes(b"\x00")
        (src / "hollow").mkdir()
        init_pkg = src / "init_pkg"
        init_pkg.mkdir()
        (init_pkg / "__init__.py").write_text("", encoding="utf-8")
        result = run_hygiene_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.FAIL.value
        fail_ids = {c.check_id for c in result.checks if c.status == CheckStatus.FAIL.value}
        assert "temp_artifacts" in fail_ids
        assert "empty_folders" in fail_ids
        assert "init_only_folders" in fail_ids

    def test_gitkeep_file_is_not_flagged_as_artifact(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / ".gitkeep").write_text("", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert not any(".gitkeep" in h for h in hits)

    def test_nonexistent_repo_root_still_returns_result(self, tmp_path: Path):
        nonexistent = tmp_path / "does_not_exist"
        result = run_hygiene_guardian(repo_root=nonexistent)
        assert result.guardian_id == "hygiene"
        assert result.status in {"PASS", "FAIL", "ERROR"}

    def test_tmp_extension_detected(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / "scratch.tmp").write_text("x", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert any("scratch.tmp" in h for h in hits)

    def test_swp_extension_detected(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / ".file.swp").write_bytes(b"\x00")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert any(".swp" in h for h in hits)
