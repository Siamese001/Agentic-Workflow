"""Tests for ops_scripts/ci/infra_wiring_scan.py"""

from __future__ import annotations

from pathlib import Path

import pytest

from ops_scripts.ci.infra_wiring_scan import (
    AGENTIC_CORE_INFRA_SUBDIRS,
    ALLOWED_DIRS,
    SANCTIONED_ADAPTER_FILES,
    is_allowed_path,
    scan_directory,
    scan_file,
)


# ---------------------------------------------------------------------------
# scan_file — happy path, failure path, edge case
# ---------------------------------------------------------------------------


class TestScanFile:
    """Tests for scan_file()."""

    def test_clean_file_returns_none(self, tmp_path: Path) -> None:
        """Happy path: file with no forbidden imports returns None."""
        f = tmp_path / "clean.py"
        f.write_text("import os\nimport json\nprint('hello')\n", encoding="utf-8")
        assert scan_file(f) is None

    def test_detects_forbidden_import(self, tmp_path: Path) -> None:
        """Happy path: detects a forbidden import and returns (line, pattern)."""
        f = tmp_path / "bad.py"
        f.write_text("import os\nimport redis\nprint('ok')\n", encoding="utf-8")
        result = scan_file(f)
        assert result is not None
        assert len(result) == 1
        line_num, pattern = result[0]
        assert line_num == 2
        assert pattern == "import redis"

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        """Failure path: unreadable file returns None (logged, not raised)."""
        missing = tmp_path / "does_not_exist.py"
        assert scan_file(missing) is None

    def test_comment_line_not_flagged(self, tmp_path: Path) -> None:
        """Edge case: commented-out import should not be flagged."""
        f = tmp_path / "commented.py"
        f.write_text("# import redis\n# from chromadb import Client\n", encoding="utf-8")
        assert scan_file(f) is None

    def test_multiple_forbidden_imports(self, tmp_path: Path) -> None:
        """Edge case: multiple different forbidden imports detected."""
        f = tmp_path / "multi.py"
        f.write_text("import redis\nimport chromadb\nimport boto3\n", encoding="utf-8")
        result = scan_file(f)
        assert result is not None
        assert len(result) == 3
        patterns = {r[1] for r in result}
        assert "import redis" in patterns
        assert "import chromadb" in patterns
        assert "import boto3" in patterns

    def test_from_import_detected(self, tmp_path: Path) -> None:
        """Edge case: 'from X import ...' style detected."""
        f = tmp_path / "from_style.py"
        f.write_text("from openai import OpenAI\n", encoding="utf-8")
        result = scan_file(f)
        assert result is not None
        assert result[0][1] == "from openai"


# ---------------------------------------------------------------------------
# is_allowed_path — happy path, failure path, edge case
# ---------------------------------------------------------------------------


class TestIsAllowedPath:
    """Tests for is_allowed_path()."""

    def test_tools_dir_allowed(self) -> None:
        """Happy path: files in tools/ are allowed."""
        p = Path("C:/Git/Agentic-Workflow/tools/mcp/redis_mcp_server.py")
        assert is_allowed_path(p) is True

    def test_apps_surface_not_allowed(self) -> None:
        """Failure path: files in apps_eval/ are NOT allowed."""
        p = Path("C:/Git/Agentic-Workflow/apps_eval/services/repo_signal_service.py")
        assert is_allowed_path(p) is False

    def test_apps_shared_allowed(self) -> None:
        """Edge case: apps_shared/ is shared infra, allowed."""
        p = Path("C:/Git/Agentic-Workflow/apps_shared/mixins/apps_tracing_mixin.py")
        assert is_allowed_path(p) is True

    def test_sanctioned_adapter_allowed(self) -> None:
        """Happy path: sanctioned adapter file in agentic_core is allowed."""
        p = Path("C:/Git/Agentic-Workflow/agentic_core/cache/redis_cache_client.py")
        assert is_allowed_path(p) is True

    def test_agentic_core_adg_subdir_allowed(self) -> None:
        """Happy path: agentic_core/adg/ is infrastructure tooling."""
        p = Path("C:/Git/Agentic-Workflow/agentic_core/adg/extraction/batch_operations.py")
        assert is_allowed_path(p) is True

    def test_agentic_core_nonsanctioned_not_allowed(self) -> None:
        """Failure path: random agentic_core file not in allowlist is blocked."""
        p = Path("C:/Git/Agentic-Workflow/agentic_core/L1_cognition/reasoning/some_module.py")
        assert is_allowed_path(p) is False

    def test_all_allowed_dirs_recognized(self) -> None:
        """Edge case: every ALLOWED_DIR entry is recognized."""
        for d in ALLOWED_DIRS:
            p = Path(f"C:/Git/repo/{d}/subdir/file.py")
            assert is_allowed_path(p) is True, f"{d} not recognized"

    def test_all_sanctioned_adapters_recognized(self) -> None:
        """Edge case: every SANCTIONED_ADAPTER_FILES entry is recognized."""
        for adapter in SANCTIONED_ADAPTER_FILES:
            p = Path(f"C:/Git/repo/agentic_core/somewhere/{adapter}")
            assert is_allowed_path(p) is True, f"{adapter} not recognized"

    def test_all_infra_subdirs_recognized(self) -> None:
        """Edge case: every AGENTIC_CORE_INFRA_SUBDIRS entry is recognized."""
        for subdir in AGENTIC_CORE_INFRA_SUBDIRS:
            p = Path(f"C:/Git/repo/agentic_core/{subdir}/file.py")
            assert is_allowed_path(p) is True, f"agentic_core/{subdir} not recognized"


# ---------------------------------------------------------------------------
# scan_directory — happy path, failure path, edge case
# ---------------------------------------------------------------------------


class TestScanDirectory:
    """Tests for scan_directory()."""

    def _make_tree(self, tmp_path: Path) -> Path:
        """Create a minimal repo tree for testing."""
        root = tmp_path / "repo"
        # Clean agentic_core file
        ac = root / "agentic_core" / "L1_cognition" / "reasoning"
        ac.mkdir(parents=True)
        (ac / "clean.py").write_text("import os\n", encoding="utf-8")
        # Sanctioned adapter
        cache = root / "agentic_core" / "cache"
        cache.mkdir(parents=True)
        (cache / "redis_cache_client.py").write_text("import redis\n", encoding="utf-8")
        # Violation in apps_eval
        ae = root / "apps_eval" / "services"
        ae.mkdir(parents=True)
        (ae / "bad_service.py").write_text("import sqlite3\n", encoding="utf-8")
        # Clean apps_shared (allowed)
        ash = root / "apps_shared" / "utils"
        ash.mkdir(parents=True)
        (ash / "shared.py").write_text("import redis\n", encoding="utf-8")
        return root

    def test_finds_apps_violations(self, tmp_path: Path) -> None:
        """Happy path: detects violations in apps_eval."""
        root = self._make_tree(tmp_path)
        violations = scan_directory(root)
        violation_files = {Path(k).name for k in violations}
        assert "bad_service.py" in violation_files

    def test_skips_sanctioned_adapters(self, tmp_path: Path) -> None:
        """Failure path (would-be false positive): sanctioned adapters not flagged."""
        root = self._make_tree(tmp_path)
        violations = scan_directory(root)
        violation_files = {Path(k).name for k in violations}
        assert "redis_cache_client.py" not in violation_files

    def test_skips_apps_shared(self, tmp_path: Path) -> None:
        """Edge case: apps_shared is not scanned."""
        root = self._make_tree(tmp_path)
        violations = scan_directory(root)
        violation_files = {Path(k).name for k in violations}
        assert "shared.py" not in violation_files

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        """Edge case: empty repo returns empty violations dict."""
        root = tmp_path / "empty_repo"
        root.mkdir()
        violations = scan_directory(root)
        assert violations == {}
