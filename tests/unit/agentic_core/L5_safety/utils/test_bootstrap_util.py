"""
Unit Tests for bootstrap_util - Micro-wave 10A

Tests the bootstrap utility functions including:
- Redis connection verification
- Critical file verification
- Bootstrap health checks
- Healing operations
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest


class TestVerifyRedisConnection:
    """Tests for verify_redis_connection function."""

    def test_verify_redis_connection_none_returns_false(self):
        """Test that None client returns False."""
        from agentic_core.L5_safety.utils.bootstrap_util import verify_redis_connection

        result = verify_redis_connection(None)
        assert result is False

    def test_verify_redis_connection_import_error_returns_false(self):
        """Test that ImportError returns False."""
        from agentic_core.L5_safety.utils.bootstrap_util import verify_redis_connection

        with patch.dict('sys.modules', {'agentic_core.L4_state.caching.redis_adapter': None}):
            result = verify_redis_connection()
            assert result is False

    def test_verify_redis_connection_success(self):
        """Test successful Redis connection."""
        from agentic_core.L5_safety.utils.bootstrap_util import verify_redis_connection

        mock_client = Mock()
        mock_client.get.return_value = "ok"

        result = verify_redis_connection(mock_client)
        assert result is True
        mock_client.set.assert_called_once_with("bootstrap_check", "ok", ex=5)

    def test_verify_redis_connection_failure(self):
        """Test failed Redis connection."""
        from agentic_core.L5_safety.utils.bootstrap_util import verify_redis_connection

        mock_client = Mock()
        mock_client.get.return_value = None

        result = verify_redis_connection(mock_client)
        assert result is False


class TestVerifyCriticalFiles:
    """Tests for verify_critical_files function."""

    def test_verify_critical_files_all_present(self, tmp_path):
        """Test when all critical files exist."""
        from agentic_core.L5_safety.utils.bootstrap_util import CRITICAL_FILES, verify_critical_files

        # Create required files based on CRITICAL_FILES
        for file_path in CRITICAL_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()

        present, missing = verify_critical_files(tmp_path)

        assert len(missing) == 0
        assert len(present) == len(CRITICAL_FILES)
        for file_path in CRITICAL_FILES:
            assert file_path in present

    def test_verify_critical_files_some_missing(self, tmp_path):
        """Test when some critical files are missing."""
        from agentic_core.L5_safety.utils.bootstrap_util import CRITICAL_FILES, verify_critical_files

        # Only create first file
        first_file = CRITICAL_FILES[0]
        full_path = tmp_path / first_file
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()

        present, missing = verify_critical_files(tmp_path)

        assert first_file in present
        for missing_file in CRITICAL_FILES[1:]:
            assert missing_file in missing

    def test_verify_critical_files_empty_directory(self, tmp_path):
        """Test with empty directory."""
        from agentic_core.L5_safety.utils.bootstrap_util import CRITICAL_FILES, verify_critical_files

        present, missing = verify_critical_files(tmp_path)

        assert len(present) == 0
        assert len(missing) == len(CRITICAL_FILES)


class TestRunBootstrap:
    """Tests for run_bootstrap function."""

    def test_run_bootstrap_returns_result_object(self, tmp_path):
        """Test bootstrap returns BootstrapResult."""
        from agentic_core.L5_safety.utils.bootstrap_util import BootstrapResult, run_bootstrap

        result = run_bootstrap(tmp_path)

        assert isinstance(result, BootstrapResult)
        assert hasattr(result, 'status')
        assert hasattr(result, 'redis_connected')
        assert hasattr(result, 'critical_files_present')
        assert hasattr(result, 'critical_files_missing')


class TestHealBootstrapIssues:
    """Tests for heal_bootstrap_issues function."""

    def test_heal_bootstrap_issues_nonexistent_path(self, tmp_path):
        """Test healing with non-existent target path."""
        from agentic_core.L5_safety.utils.bootstrap_util import heal_bootstrap_issues

        fake_path = tmp_path / "nonexistent"
        result = heal_bootstrap_issues(tmp_path, str(fake_path))

        assert "errors" in result
        assert any("does not exist" in e for e in result["errors"])
        assert "violations_found" in result
        assert "violations_fixed" in result

    def test_heal_bootstrap_issues_valid_path(self, tmp_path):
        """Test healing with valid path."""
        from agentic_core.L5_safety.utils.bootstrap_util import CRITICAL_FILES, heal_bootstrap_issues

        # Create required files
        for file_path in CRITICAL_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()

        result = heal_bootstrap_issues(tmp_path)

        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "errors" in result
        assert "skipped" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["skipped"], list)


class TestBootstrapResult:
    """Tests for BootstrapResult dataclass."""

    def test_bootstrap_result_creation(self):
        """Test BootstrapResult can be created with required fields."""
        from agentic_core.L5_safety.utils.bootstrap_util import BootstrapResult

        result = BootstrapResult(
            status="healthy",
            redis_connected=True,
            critical_files_present=["file1", "file2"],
            critical_files_missing=[],
        )

        assert result.status == "healthy"
        assert result.redis_connected is True
        assert len(result.critical_files_present) == 2
        assert len(result.critical_files_missing) == 0

    def test_bootstrap_result_to_dict(self):
        """Test BootstrapResult to_dict method."""
        from agentic_core.L5_safety.utils.bootstrap_util import BootstrapResult

        result = BootstrapResult(
            status="degraded",
            redis_connected=False,
            critical_files_present=[],
            critical_files_missing=["missing"],
        )

        d = result.to_dict()
        assert d["status"] == "degraded"
        assert d["redis_connected"] is False
        assert "critical_files_present" in d
        assert "critical_files_missing" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
