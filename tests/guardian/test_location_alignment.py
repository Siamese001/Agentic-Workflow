"""
Tests for the location_alignment guardian.

Proves:
1. Contract validity — produces schema-valid GuardianResult
2. No side effects — only explicit output JSON written, no other files modified
3. Stable check_id set — emitted check_ids == {"misplaced_files", "missing_directories"}
4. Determinism — identical results across runs
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.scripts.run_guardian_location_alignment import (
    GUARDIAN_ID,
    run_location_alignment_guardian,
    scan_misplaced_files,
    scan_missing_directories,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)

# ---------------------------------------------------------------------------
# Test configuration — minimal fixture config independent of real repo
# ---------------------------------------------------------------------------

FIXTURE_ROOTS = frozenset({"src", "lib"})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    """Minimal repo tree that passes all location checks."""
    # Create required sovereign roots
    for root in FIXTURE_ROOTS:
        root_dir = tmp_path / root
        root_dir.mkdir()
        (root_dir / "__init__.py").write_text("", encoding="utf-8")
        # Put .py files in subfolders (not at root)
        sub = root_dir / "engines"
        sub.mkdir()
        (sub / "__init__.py").write_text("", encoding="utf-8")
        (sub / "core_engine.py").write_text("pass\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def missing_dirs_repo(tmp_path: Path) -> Path:
    """Repo missing required sovereign roots."""
    # Create only one of the two required roots
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("", encoding="utf-8")
    # "lib" is intentionally missing
    return tmp_path


@pytest.fixture()
def misplaced_repo(tmp_path: Path) -> Path:
    """Repo with misplaced files at territory root and forbidden patterns."""
    for root in FIXTURE_ROOTS:
        root_dir = tmp_path / root
        root_dir.mkdir()
        (root_dir / "__init__.py").write_text("", encoding="utf-8")

    # Misplaced: .py file at territory root (not in subfolder)
    (tmp_path / "src" / "floating_module.py").write_text("x = 1\n", encoding="utf-8")

    # Forbidden pattern: backup file in subfolder
    engines = tmp_path / "lib" / "engines"
    engines.mkdir()
    (engines / "old_engine.py.bak").write_text("", encoding="utf-8")

    return tmp_path


@pytest.fixture()
def dirty_repo(tmp_path: Path) -> Path:
    """Repo with BOTH missing directories and misplaced files."""
    # Only create "src", leave "lib" missing
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    # Floating file at root level
    (src / "orphan.py").write_text("pass\n", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanMissingDirectories:
    def test_clean_no_missing(self, clean_repo: Path) -> None:
        assert scan_missing_directories(clean_repo, FIXTURE_ROOTS) == []

    def test_detects_missing(self, missing_dirs_repo: Path) -> None:
        missing = scan_missing_directories(missing_dirs_repo, FIXTURE_ROOTS)
        assert "lib" in missing
        assert "src" not in missing

    def test_detects_file_not_dir(self, tmp_path: Path) -> None:
        # Create "src" as a file, not a directory
        (tmp_path / "src").write_text("not a dir", encoding="utf-8")
        missing = scan_missing_directories(tmp_path, frozenset({"src"}))
        assert missing == ["src"]

    def test_sorted_output(self, tmp_path: Path) -> None:
        roots = frozenset({"zebra", "alpha", "middle"})
        missing = scan_missing_directories(tmp_path, roots)
        assert missing == sorted(missing)

    def test_empty_roots(self, tmp_path: Path) -> None:
        assert scan_missing_directories(tmp_path, frozenset()) == []


class TestScanMisplacedFiles:
    def test_clean_no_misplaced(self, clean_repo: Path) -> None:
        assert scan_misplaced_files(clean_repo, FIXTURE_ROOTS) == []

    def test_detects_floating_file(self, misplaced_repo: Path) -> None:
        hits = scan_misplaced_files(misplaced_repo, FIXTURE_ROOTS)
        assert any("floating_module.py" in h for h in hits)

    def test_detects_forbidden_pattern(self, misplaced_repo: Path) -> None:
        hits = scan_misplaced_files(misplaced_repo, FIXTURE_ROOTS)
        assert any(".bak" in h for h in hits)

    def test_init_py_not_flagged(self, clean_repo: Path) -> None:
        # __init__.py at root level is allowed
        hits = scan_misplaced_files(clean_repo, FIXTURE_ROOTS)
        assert not any("__init__.py" in h for h in hits)

    def test_sorted_output(self, misplaced_repo: Path) -> None:
        hits = scan_misplaced_files(misplaced_repo, FIXTURE_ROOTS)
        assert hits == sorted(hits)

    def test_nonexistent_root_skipped(self, tmp_path: Path) -> None:
        assert scan_misplaced_files(tmp_path, frozenset({"nonexistent"})) == []

    def test_pycache_skipped(self, tmp_path: Path) -> None:
        root = tmp_path / "src"
        root.mkdir()
        cache = root / "__pycache__"
        cache.mkdir()
        (cache / "mod.cpython-312.pyc").write_text("", encoding="utf-8")
        assert scan_misplaced_files(tmp_path, frozenset({"src"})) == []


# ---------------------------------------------------------------------------
# Guardian runner contract tests
# ---------------------------------------------------------------------------


class TestLocationAlignmentGuardianContract:
    """Proves GuardianResult schema validity."""

    def test_clean_repo_pass(self, clean_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=clean_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert result.guardian_id == GUARDIAN_ID
        assert result.status == GuardianStatus.PASS.value

    def test_missing_dirs_fail(self, missing_dirs_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=missing_dirs_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert result.status == GuardianStatus.FAIL.value

    def test_misplaced_fail(self, misplaced_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=misplaced_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert result.status == GuardianStatus.FAIL.value

    def test_schema_compatibility_clean(self, clean_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=clean_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_schema_compatibility_dirty(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_no_absolute_paths(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths found: {violations}"

    def test_validate_method_clean(self, clean_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=clean_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert result.validate() == []

    def test_validate_method_dirty(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert result.validate() == []


# ---------------------------------------------------------------------------
# No side effects
# ---------------------------------------------------------------------------


class TestLocationAlignmentNoSideEffects:
    """Prove the guardian writes nothing except the explicit output JSON."""

    def test_no_writes_without_artifact_dir(self, dirty_repo: Path) -> None:
        before = self._snapshot(dirty_repo)

        run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )

        after = self._snapshot(dirty_repo)
        assert before == after, f"New files created: {after - before}"

    def test_only_output_json_written(self, dirty_repo: Path) -> None:
        out_dir = "guardian_output"
        before = self._snapshot(dirty_repo)

        run_location_alignment_guardian(
            repo_root=dirty_repo,
            write_artifacts_dir=out_dir,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )

        after = self._snapshot(dirty_repo)
        new_files = after - before
        assert len(new_files) == 1
        new_file = new_files.pop()
        assert "guardian_location_alignment_result.json" in new_file

        # Verify written JSON is parseable
        full_path = dirty_repo / new_file
        data = json.loads(full_path.read_text(encoding="utf-8"))
        assert data["guardian_id"] == GUARDIAN_ID

    @staticmethod
    def _snapshot(root: Path) -> set[str]:
        return {str(f.relative_to(root)) for f in root.rglob("*") if f.is_file()}


# ---------------------------------------------------------------------------
# Stable check_id set
# ---------------------------------------------------------------------------


class TestLocationAlignmentStableCheckIds:
    """Prove emitted check_id set is exactly {"misplaced_files", "missing_directories"}."""

    def test_check_ids_clean(self, clean_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=clean_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"misplaced_files", "missing_directories"}

    def test_check_ids_dirty(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"misplaced_files", "missing_directories"}

    def test_check_ids_empty_dir(self, tmp_path: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=tmp_path,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        check_ids = {c.check_id for c in result.checks}
        assert check_ids == {"misplaced_files", "missing_directories"}

    def test_exactly_two_checks(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert len(result.checks) == 2


# ---------------------------------------------------------------------------
# Evidence determinism
# ---------------------------------------------------------------------------


class TestLocationAlignmentEvidenceDeterminism:
    """Prove evidence lists are sorted and stable across runs."""

    def test_evidence_sorted_misplaced(self, misplaced_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=misplaced_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        for check in result.checks:
            if check.check_id == "misplaced_files":
                paths = check.evidence.get("paths", [])
                assert paths == sorted(paths)

    def test_evidence_sorted_missing(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        for check in result.checks:
            if check.check_id == "missing_directories":
                dirs = check.evidence.get("directories", [])
                assert dirs == sorted(dirs)

    def test_idempotent_runs(self, dirty_repo: Path) -> None:
        kwargs = {
            "repo_root": dirty_repo,
            "required_roots": FIXTURE_ROOTS,
            "scan_roots": FIXTURE_ROOTS,
        }
        r1 = run_location_alignment_guardian(**kwargs)
        r2 = run_location_alignment_guardian(**kwargs)
        assert r1.to_dict() == r2.to_dict()

    def test_metrics_present(self, dirty_repo: Path) -> None:
        result = run_location_alignment_guardian(
            repo_root=dirty_repo,
            required_roots=FIXTURE_ROOTS,
            scan_roots=FIXTURE_ROOTS,
        )
        assert "misplaced_file_count" in result.metrics
        assert "missing_directory_count" in result.metrics
        assert "total_checks" in result.metrics
