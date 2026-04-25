"""Tests for SSOTFolderCleanupAgent.py module.

This is a deprecated shim that delegates to ssot_folder_cleanup_util.
Tests verify deprecation warning and delegation behavior.
"""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent import (
    SSOTFolderCleanupAgent,
)


class TestSSOTFolderCleanupAgentDeprecation:
    """Tests for deprecation warning."""

    def test_class_emits_deprecation_warning(self):
        """Test that instantiating SSOTFolderCleanupAgent emits deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = SSOTFolderCleanupAgent()

            # Check that deprecation warning was issued
            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)
            assert any("deprecated" in str(warning.message).lower() for warning in w)


class TestSSOTFolderCleanupAgentDelegation:
    """Tests that methods delegate to ssot_folder_cleanup_util."""

    def test_find_non_approved_files_delegates(self):
        """Test that find_non_approved_files delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.find_non_approved_files", return_value=["file1.py", "file2.py"]) as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                result = agent.find_non_approved_files("repo_root")
            
            mock_util.assert_called_once_with("repo_root")
            assert result == ["file1.py", "file2.py"]

    def test_move_file_to_ssot_delegates(self):
        """Test that move_file_to_ssot delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.move_file_to_ssot") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.move_file_to_ssot("source", "dest")
            
            mock_util.assert_called_once_with("source", "dest")

    def test_update_imports_for_moved_file_delegates(self):
        """Test that update_imports_for_moved_file delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.update_imports_for_moved_file") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.update_imports_for_moved_file("file_path", "old_path", "new_path")
            
            mock_util.assert_called_once_with("file_path", "old_path", "new_path")

    def test_delete_empty_folders_delegates(self):
        """Test that delete_empty_folders delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.delete_empty_folders") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.delete_empty_folders("repo_root")
            
            mock_util.assert_called_once_with("repo_root")

    def test_cleanup_repository_delegates(self):
        """Test that cleanup_repository delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.cleanup_repository") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.cleanup_repository("repo_root")
            
            mock_util.assert_called_once_with("repo_root")

    def test_preview_cleanup_delegates(self):
        """Test that preview_cleanup delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.preview_cleanup") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.preview_cleanup("repo_root")
            
            mock_util.assert_called_once_with("repo_root")

    def test_execute_cleanup_delegates(self):
        """Test that execute_cleanup delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.execute_cleanup") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.execute_cleanup("repo_root")
            
            mock_util.assert_called_once_with("repo_root")

    def test_heal_repository_delegates(self):
        """Test that heal_repository delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.heal_repository") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.heal_repository("repo_root")
            
            mock_util.assert_called_once_with("repo_root")

    def test_is_path_ssot_approved_delegates(self):
        """Test that is_path_ssot_approved delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.is_path_ssot_approved", return_value=True) as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                result = agent.is_path_ssot_approved("file_path")
            
            mock_util.assert_called_once_with("file_path")
            assert result is True

    def test_triage_file_delegates(self):
        """Test that triage_file delegates to utility."""
        with patch("agentic_core.L0_routing.reasoning.ssot_folder_cleanup_util.triage_file") as mock_util:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                agent = SSOTFolderCleanupAgent()
                agent.triage_file("file_path")
            
            mock_util.assert_called_once_with("file_path")
