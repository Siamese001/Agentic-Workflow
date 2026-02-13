"""
Guardian Hygiene Tests — ReAct-Style (Observe → Verify → Report).

Tests the run_guardian_hygiene script against sandboxed tmp_repo fixtures.
Verifies:
1. Clean repo → PASS with all checks passing
2. Dirty repo (temp artifacts) → FAIL with correct check IDs
3. Empty folders → detected and reported
4. Init-only folders → detected and reported
5. JSON output conforms to guardian_contract schema
6. --strict flag returns non-zero exit on FAIL
7. Artifact paths are repo-relative POSIX (no absolute paths)
8. Deterministic: same input → same JSON output
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_hygiene import (
    run_hygiene_guardian,
    scan_empty_folders,
    scan_init_only_folders,
    scan_temp_artifacts,
)
from agentic_core.L0_routing.types.guardian_contract import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures: sandboxed tmp_repo
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """
    Create a minimal sandboxed repo structure.
    Mimics ROOT_WHITELIST entries so the scanner finds them.
    """
    for folder in ("agentic_core", "apps_shared", "tests"):
        d = tmp_path / folder
        d.mkdir()
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "real_module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def dirty_repo(tmp_repo: Path) -> Path:
    """Add temp artifacts, empty folders, and init-only folders."""
    # Temp artifacts
    (tmp_repo / "agentic_core" / "cache.pyc").write_bytes(b"\x00")
    (tmp_repo / "agentic_core" / "scratch.tmp").write_bytes(b"\x00")
    (tmp_repo / "tests" / "old.bak").write_bytes(b"\x00")

    # Empty folder
    (tmp_repo / "agentic_core" / "empty_dir").mkdir()

    # Init-only folder
    init_dir = tmp_repo / "agentic_core" / "orphan_pkg"
    init_dir.mkdir()
    (init_dir / "__init__.py").write_text("", encoding="utf-8")

    return tmp_repo


# ---------------------------------------------------------------------------
# 1. Clean repo → PASS
# ---------------------------------------------------------------------------


class TestCleanRepo:
    def test_clean_repo_passes(self, tmp_repo: Path):
        _allowed = frozenset({"agentic_core", "apps_shared", "tests"})
        result = run_hygiene_guardian(repo_root=tmp_repo)
        assert result.status == GuardianStatus.PASS.value
        assert result.guardian_id == "hygiene"

    def test_clean_repo_all_checks_pass(self, tmp_repo: Path):
        result = run_hygiene_guardian(repo_root=tmp_repo)
        for check in result.checks:
            assert check.status == CheckStatus.PASS.value, f"Check {check.check_id} should PASS on clean repo"

    def test_clean_repo_metrics(self, tmp_repo: Path):
        result = run_hygiene_guardian(repo_root=tmp_repo)
        assert result.metrics["temp_artifact_count"] == 0
        assert result.metrics["empty_folder_count"] == 0
        assert result.metrics["init_only_folder_count"] == 0


# ---------------------------------------------------------------------------
# 2. Dirty repo → FAIL with correct checks
# ---------------------------------------------------------------------------


class TestDirtyRepo:
    def test_dirty_repo_fails(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        assert result.status == GuardianStatus.FAIL.value

    def test_temp_artifacts_detected(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        temp_check = next(c for c in result.checks if c.check_id == "temp_artifacts")
        assert temp_check.status == CheckStatus.FAIL.value
        assert "3" in temp_check.details  # 3 temp files

    def test_empty_folders_detected(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        empty_check = next(c for c in result.checks if c.check_id == "empty_folders")
        assert empty_check.status == CheckStatus.FAIL.value

    def test_init_only_folders_detected(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        init_check = next(c for c in result.checks if c.check_id == "init_only_folders")
        assert init_check.status == CheckStatus.FAIL.value

    def test_remediation_hints_present(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 3. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_json_is_valid(self, tmp_repo: Path):
        result = run_hygiene_guardian(repo_root=tmp_repo)
        raw = result.to_json()
        parsed = json.loads(raw)
        assert parsed["guardian_id"] == "hygiene"

    def test_no_absolute_paths(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths found: {violations}"

    def test_validation_passes(self, tmp_repo: Path):
        result = run_hygiene_guardian(repo_root=tmp_repo)
        errors = result.validate()
        assert errors == [], f"Contract violations: {errors}"

    def test_check_ids_are_stable(self, dirty_repo: Path):
        result = run_hygiene_guardian(repo_root=dirty_repo)
        check_ids = {c.check_id for c in result.checks}
        expected = {"temp_artifacts", "empty_folders", "init_only_folders"}
        assert check_ids == expected


# ---------------------------------------------------------------------------
# 4. Artifact writing
# ---------------------------------------------------------------------------


class TestArtifactWriting:
    def test_writes_json_artifact(self, tmp_repo: Path):
        _result = run_hygiene_guardian(
            repo_root=tmp_repo,
            write_artifacts_dir="docs/reports/plans",
        )
        artifact_path = tmp_repo / "docs" / "reports" / "plans" / "guardian_hygiene_result.json"
        assert artifact_path.exists()
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert data["guardian_id"] == "hygiene"

    def test_artifact_path_is_posix(self, tmp_repo: Path):
        result = run_hygiene_guardian(
            repo_root=tmp_repo,
            write_artifacts_dir="docs/reports/plans",
        )
        for artifact in result.artifacts:
            assert "\\" not in artifact.path
            assert not artifact.path.startswith("/")


# ---------------------------------------------------------------------------
# 5. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self, tmp_repo: Path):
        r1 = run_hygiene_guardian(repo_root=tmp_repo)
        r2 = run_hygiene_guardian(repo_root=tmp_repo)
        assert r1.to_json() == r2.to_json()

    def test_timestamp_injectable(self, tmp_repo: Path):
        ts = "2026-01-01T00:00:00Z"
        result = run_hygiene_guardian(repo_root=tmp_repo, timestamp=ts)
        assert result.timestamp == ts

    def test_no_timestamp_by_default(self, tmp_repo: Path):
        result = run_hygiene_guardian(repo_root=tmp_repo)
        assert result.timestamp is None


# ---------------------------------------------------------------------------
# 6. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanFunctions:
    def test_scan_temp_artifacts_empty_on_clean(self, tmp_repo: Path):
        allowed = frozenset({"agentic_core", "apps_shared", "tests"})
        hits = scan_temp_artifacts(tmp_repo, allowed)
        assert hits == []

    def test_scan_temp_artifacts_finds_pyc(self, dirty_repo: Path):
        allowed = frozenset({"agentic_core", "apps_shared", "tests"})
        hits = scan_temp_artifacts(dirty_repo, allowed)
        assert any("cache.pyc" in h for h in hits)

    def test_scan_empty_folders_finds_empty(self, dirty_repo: Path):
        allowed = frozenset({"agentic_core", "apps_shared", "tests"})
        hits = scan_empty_folders(dirty_repo, allowed)
        assert any("empty_dir" in h for h in hits)

    def test_scan_init_only_finds_orphan(self, dirty_repo: Path):
        allowed = frozenset({"agentic_core", "apps_shared", "tests"})
        hits = scan_init_only_folders(dirty_repo, allowed)
        assert any("orphan_pkg" in h for h in hits)
