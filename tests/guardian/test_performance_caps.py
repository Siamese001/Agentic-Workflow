"""
Phase 5 / 3b: Algorithmic Performance Caps - In-Code Enforcement.

Ensures that guardians enforce performance bounds in their implementation,
not just in tests. Cap breaches produce FAIL with remediation hints (not ERROR).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_hygiene import (
    run_hygiene_guardian,
    scan_temp_artifacts,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    IGNORE_PATTERNS,
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
    CheckStatus,
    GuardianStatus,
    ScanBudgetExceeded,
)

pytestmark = pytest.mark.guardian


@pytest.fixture
def massive_repo(tmp_path: Path) -> Path:
    """Create a repo with many files to test scan bounds."""
    repo = tmp_path / "repo"
    repo.mkdir()

    core = repo / "agentic_core"
    core.mkdir()

    for i in range(100):
        (core / f"file_{i}.py").write_text(f"# file {i}\n", encoding="utf-8")

    return repo


@pytest.fixture
def deep_repo(tmp_path: Path) -> Path:
    """Create a repo with deep nesting to test depth bounds."""
    repo = tmp_path / "repo"
    current = repo / "agentic_core"
    current.mkdir(parents=True)

    for i in range(MAX_FOLDER_DEPTH + 5):
        current = current / f"level_{i}"
        current.mkdir()
        (current / f"file_{i}.tmp").write_text("temp", encoding="utf-8")

    return repo


class TestScanBoundsEnforcement:
    """Scan functions must enforce MAX_FILES_PER_SCAN and MAX_FOLDER_DEPTH."""

    def test_scan_respects_file_count_limit(self, massive_repo: Path):
        """Scan must not exceed MAX_FILES_PER_SCAN."""
        allowed_roots = frozenset({"agentic_core"})

        results = scan_temp_artifacts(massive_repo, allowed_roots)
        assert isinstance(results, list)

    def test_scan_respects_depth_limit(self, deep_repo: Path):
        """Scan must skip files beyond MAX_FOLDER_DEPTH."""
        allowed_roots = frozenset({"agentic_core"})

        results = scan_temp_artifacts(deep_repo, allowed_roots)
        assert isinstance(results, list), "Small repo should return list, not sentinel"

        for path_str in results:
            depth = len(Path(path_str).parts)
            assert depth <= MAX_FOLDER_DEPTH, f"Path {path_str} exceeds MAX_FOLDER_DEPTH ({MAX_FOLDER_DEPTH})"

    def test_scan_skips_ignored_patterns(self, tmp_path: Path):
        """Scan must skip directories matching IGNORE_PATTERNS."""
        repo = tmp_path / "repo"
        core = repo / "agentic_core"
        core.mkdir(parents=True)

        for pattern in IGNORE_PATTERNS:
            ignored_dir = core / pattern
            ignored_dir.mkdir()
            (ignored_dir / "file.tmp").write_text("temp", encoding="utf-8")

        (core / "real.tmp").write_text("temp", encoding="utf-8")

        allowed_roots = frozenset({"agentic_core"})
        results = scan_temp_artifacts(repo, allowed_roots)
        assert isinstance(results, list)

        assert len(results) == 1
        assert "real.tmp" in results[0]

        for path_str in results:
            for pattern in IGNORE_PATTERNS:
                assert pattern not in path_str, f"Found file in ignored pattern {pattern}: {path_str}"


class TestPerformanceConstantsLocked:
    """Performance constants must be immutable and documented."""

    def test_max_files_per_scan_is_reasonable(self):
        assert MAX_FILES_PER_SCAN == 10_000
        assert isinstance(MAX_FILES_PER_SCAN, int)

    def test_max_folder_depth_is_reasonable(self):
        assert MAX_FOLDER_DEPTH == 10
        assert isinstance(MAX_FOLDER_DEPTH, int)

    def test_ignore_patterns_is_frozen(self):
        assert isinstance(IGNORE_PATTERNS, frozenset)
        assert ".git" in IGNORE_PATTERNS
        assert "__pycache__" in IGNORE_PATTERNS
        assert "node_modules" in IGNORE_PATTERNS

    def test_ignore_patterns_has_minimum_coverage(self):
        required = {".git", "__pycache__", ".pytest_cache", ".nox"}
        assert required.issubset(IGNORE_PATTERNS), f"Missing required patterns: {required - IGNORE_PATTERNS}"


class TestBudgetCapHandling:
    """Cap breaches produce FAIL with check_id + remediation hints (not exceptions)."""

    def test_exceeding_file_limit_returns_sentinel(self, tmp_path: Path):
        """Scanning more than MAX_FILES_PER_SCAN returns ScanBudgetExceeded."""
        repo = tmp_path / "repo"
        core = repo / "agentic_core"
        core.mkdir(parents=True)

        for i in range(MAX_FILES_PER_SCAN + 100):
            (core / f"file_{i}.tmp").write_text("temp", encoding="utf-8")

        allowed_roots = frozenset({"agentic_core"})
        result = scan_temp_artifacts(repo, allowed_roots)

        assert isinstance(result, ScanBudgetExceeded), "Cap breach must return ScanBudgetExceeded, not raise"
        assert result.cap_name == "MAX_FILES_PER_SCAN"
        assert result.limit == MAX_FILES_PER_SCAN

    def test_sentinel_carries_details(self, tmp_path: Path):
        """ScanBudgetExceeded must carry details and remediation hints."""
        repo = tmp_path / "repo"
        core = repo / "agentic_core"
        core.mkdir(parents=True)

        for i in range(MAX_FILES_PER_SCAN + 10):
            (core / f"file_{i}.tmp").write_text("temp", encoding="utf-8")

        allowed_roots = frozenset({"agentic_core"})
        result = scan_temp_artifacts(repo, allowed_roots)

        assert isinstance(result, ScanBudgetExceeded)
        assert str(MAX_FILES_PER_SCAN) in result.details
        assert len(result.remediation_hints) >= 1
        assert any("IGNORE_PATTERNS" in h for h in result.remediation_hints)

    def test_guardian_emits_fail_not_error_on_cap_breach(self, tmp_path: Path):
        """run_hygiene_guardian must emit FAIL (not ERROR) on cap breach."""
        repo = tmp_path / "repo"
        core = repo / "agentic_core"
        core.mkdir(parents=True)

        for i in range(MAX_FILES_PER_SCAN + 100):
            (core / f"file_{i}.tmp").write_text("temp", encoding="utf-8")

        result = run_hygiene_guardian(repo_root=repo)

        assert result.status == GuardianStatus.FAIL.value, (
            f"Cap breach should produce FAIL, not {result.status}"
        )
        # Must NOT be ERROR
        assert result.status != GuardianStatus.ERROR.value

        # Must contain scan_budget_exceeded check
        budget_checks = [c for c in result.checks if c.check_id == "scan_budget_exceeded"]
        assert len(budget_checks) == 1, "Expected exactly one scan_budget_exceeded check"
        assert budget_checks[0].status == CheckStatus.FAIL.value
        assert "MAX_FILES_PER_SCAN" in budget_checks[0].details

    def test_guardian_remediation_hints_on_cap_breach(self, tmp_path: Path):
        """Cap breach must include actionable remediation hints."""
        repo = tmp_path / "repo"
        core = repo / "agentic_core"
        core.mkdir(parents=True)

        for i in range(MAX_FILES_PER_SCAN + 50):
            (core / f"file_{i}.tmp").write_text("temp", encoding="utf-8")

        result = run_hygiene_guardian(repo_root=repo)

        assert len(result.remediation_hints) >= 1, "Must include remediation hints"
        hints_text = " ".join(result.remediation_hints)
        assert "IGNORE_PATTERNS" in hints_text, "Hints should mention IGNORE_PATTERNS"
