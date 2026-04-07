"""Test RepoSignalService functionality for apps_exec."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRepoSignalService:
    """Test RepoSignalService functionality."""

    @patch("apps_exec.services.repo_signal_service.RepoSignalAdapter")
    def test_init_with_repo_root(self, mock_adapter):
        """Test initialization with custom repo root."""
        from apps_exec.services.repo_signal_service import RepoSignalService

        custom_root = Path("/custom/repo")
        service = RepoSignalService(repo_root=custom_root)

        assert service.repo_root == custom_root
        mock_adapter.assert_called_once_with(custom_root)

    @patch("apps_exec.services.repo_signal_service.RepoSignalAdapter")
    def test_init_default_repo_root(self, mock_adapter):
        """Test initialization with default repo root."""
        from apps_exec.services.repo_signal_service import RepoSignalService

        service = RepoSignalService()

        assert service.repo_root is not None
        mock_adapter.assert_called_once()

    @patch("apps_exec.services.repo_signal_service.RepoSignalAdapter")
    def test_collect(self, mock_adapter):
        """Test collecting repo signals."""
        from apps_exec.services.repo_signal_service import RepoSignalService

        mock_shared = MagicMock()
        mock_shared.captured_at = "2024-01-01T00:00:00"
        mock_shared.adg = {"nodes": 100}
        mock_shared.tests = {"total": 50}
        mock_shared.ci = {"status": "passing"}
        mock_shared.governance = {"violations": 0}
        mock_shared.provenance = {"source": "test"}
        mock_shared.baseline = {"score": 0.9}

        mock_adapter.return_value.collect.return_value = mock_shared

        service = RepoSignalService()
        snapshot = service.collect()

        assert snapshot.captured_at == "2024-01-01T00:00:00"
