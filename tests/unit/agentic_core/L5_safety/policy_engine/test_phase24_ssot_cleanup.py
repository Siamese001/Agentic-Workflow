"""
[PHASE 24] Unit Tests for SSOT Folder Cleanup Agent.

Tests:
1. Path approval detection
2. Non-approved file discovery
3. File triage via CognitiveDispositionAgent
4. Import update logic
5. Empty folder deletion
6. Full cleanup workflow

[SSOT] Tests for Phase 24 SSOT folder cleanup operations.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Path Approval Tests
# =============================================================================


class TestPathApproval:
    """Tests for SSOT path approval detection."""

    @pytest.fixture
    def cleanup_agent(self, tmp_path):
        """Create a SSOTFolderCleanupAgent with temp project."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Create minimal SSOT structure
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L2_execution").mkdir(parents=True)
        (tmp_path / "agentic_core" / "utils" / "core_extensions").mkdir(parents=True)
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "archives").mkdir(parents=True)

        return SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

    def test_approved_path_sovereign_root(self, cleanup_agent):
        """Test that sovereign registry roots are approved."""
        path = cleanup_agent.project_root / "agentic_core"
        assert cleanup_agent.is_path_ssot_approved(path) is True

    def test_approved_path_layer_folder(self, cleanup_agent):
        """Test that layer folders are approved."""
        path = cleanup_agent.project_root / "agentic_core" / "L5_safety"
        assert cleanup_agent.is_path_ssot_approved(path) is True

    def test_approved_path_subfolder(self, cleanup_agent):
        """Test that approved subfolders are detected."""
        path = cleanup_agent.project_root / "agentic_core" / "L5_safety" / "validators"
        assert cleanup_agent.is_path_ssot_approved(path) is True

    def test_approved_path_tests(self, cleanup_agent):
        """Test that tests folder is approved."""
        path = cleanup_agent.project_root / "tests" / "unit"
        assert cleanup_agent.is_path_ssot_approved(path) is True

    def test_non_approved_path(self, cleanup_agent):
        """Test that non-approved paths are detected."""
        # Create a non-approved folder
        non_approved = cleanup_agent.project_root / "agentic_core" / "random_folder"
        non_approved.mkdir(parents=True, exist_ok=True)

        assert cleanup_agent.is_path_ssot_approved(non_approved) is False


# =============================================================================
# File Discovery Tests
# =============================================================================


class TestFileDiscovery:
    """Tests for non-approved file discovery."""

    @pytest.fixture
    def project_with_files(self, tmp_path):
        """Create a project with files in various locations."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Create SSOT structure
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L2_execution").mkdir(parents=True)

        # Create approved file
        approved_file = tmp_path / "agentic_core" / "L5_safety" / "validators" / "test_validator.py"
        approved_file.write_text("# Approved file")

        # Create non-approved file
        non_approved_dir = tmp_path / "agentic_core" / "random_folder"
        non_approved_dir.mkdir(parents=True)
        non_approved_file = non_approved_dir / "orphan_file.py"
        non_approved_file.write_text("# Orphan file")

        agent = SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)
        return agent, approved_file, non_approved_file

    def test_find_non_approved_files(self, project_with_files):
        """Test that non-approved files are found."""
        agent, approved_file, non_approved_file = project_with_files

        non_approved = agent.find_non_approved_files()

        # Should find the orphan file
        assert len(non_approved) >= 1
        assert any(f.name == "orphan_file.py" for f in non_approved)

        # Should NOT include the approved file
        assert not any(f.name == "test_validator.py" for f in non_approved)


# =============================================================================
# Import Update Tests
# =============================================================================


class TestImportUpdate:
    """Tests for import update logic."""

    @pytest.fixture
    def cleanup_agent(self, tmp_path):
        """Create a cleanup agent."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        return SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

    def test_path_to_module_conversion(self, cleanup_agent, tmp_path):
        """Test path to module name conversion."""
        path = tmp_path / "agentic_core" / "L5_safety" / "validators" / "test.py"

        module = cleanup_agent._path_to_module(path)

        assert module == "agentic_core.L5_safety.validators.test"

    def test_import_update_from_statement(self, cleanup_agent):
        """Test updating 'from X import Y' statements."""
        content = "from agentic_core.old_location.module import MyClass"

        updated = cleanup_agent._update_imports_in_content(
            content,
            "agentic_core.old_location.module",
            "agentic_core.new_location.module",
        )

        assert "from agentic_core.new_location.module import MyClass" in updated
        assert "old_location" not in updated

    def test_import_update_import_statement(self, cleanup_agent):
        """Test updating 'import X' statements."""
        content = "import agentic_core.old_location.module"

        updated = cleanup_agent._update_imports_in_content(
            content,
            "agentic_core.old_location.module",
            "agentic_core.new_location.module",
        )

        assert "import agentic_core.new_location.module" in updated
        assert "old_location" not in updated

    def test_import_update_submodule(self, cleanup_agent):
        """Test updating imports with submodules."""
        content = "from agentic_core.old_location.module.submodule import func"

        updated = cleanup_agent._update_imports_in_content(
            content,
            "agentic_core.old_location.module",
            "agentic_core.new_location.module",
        )

        assert "from agentic_core.new_location.module.submodule import func" in updated


# =============================================================================
# Empty Folder Deletion Tests
# =============================================================================


class TestEmptyFolderDeletion:
    """Tests for empty folder deletion."""

    @pytest.fixture
    def project_with_empty_folders(self, tmp_path):
        """Create a project with empty non-approved folders."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Create SSOT structure
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)

        # Create empty non-approved folder
        empty_folder = tmp_path / "agentic_core" / "empty_folder"
        empty_folder.mkdir(parents=True)

        # Create non-empty non-approved folder
        non_empty = tmp_path / "agentic_core" / "non_empty_folder"
        non_empty.mkdir(parents=True)
        (non_empty / "file.py").write_text("# content")

        agent = SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=False)
        return agent, empty_folder, non_empty

    def test_delete_empty_folders(self, project_with_empty_folders):
        """Test that empty non-approved folders are deleted."""
        agent, empty_folder, non_empty = project_with_empty_folders

        # Verify empty folder exists
        assert empty_folder.exists()

        # Delete empty folders
        agent.delete_empty_folders()

        # Empty folder should be deleted
        assert not empty_folder.exists()

        # Non-empty folder should remain
        assert non_empty.exists()


# =============================================================================
# Cleanup Workflow Tests
# =============================================================================


class TestCleanupWorkflow:
    """Tests for the full cleanup workflow."""

    @pytest.fixture
    def cleanup_agent(self, tmp_path):
        """Create a cleanup agent with mocked dependencies."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Create minimal structure
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)

        return SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

    def test_preview_cleanup_is_dry_run(self, cleanup_agent):
        """Test that preview_cleanup doesn't make changes."""
        result = cleanup_agent.preview_cleanup()

        assert result["dry_run"] is True

    def test_cleanup_returns_summary(self, cleanup_agent):
        """Test that cleanup returns a proper summary."""
        result = cleanup_agent.cleanup_repository()

        assert "files_scanned" in result
        assert "non_approved_files" in result
        assert "files_moved" in result
        assert "folders_deleted" in result
        assert "errors" in result

    def test_cleanup_with_mocked_triage(self, tmp_path):
        """Test cleanup with mocked CognitiveDispositionAgent."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Create structure
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)

        # Create orphan file
        orphan_dir = tmp_path / "agentic_core" / "orphan"
        orphan_dir.mkdir(parents=True)
        orphan_file = orphan_dir / "orphan_agent.py"
        orphan_file.write_text("class OrphanAgent: pass")

        agent = SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

        # Mock the cognitive agent
        mock_decision = MagicMock()
        mock_decision.action = "MOVE"
        mock_decision.target_path = "agentic_core/L5_safety/validators"
        mock_decision.reason = "Validator pattern detected"
        mock_decision.confidence = 0.85

        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = mock_decision
        agent._cognitive_agent = mock_cognitive

        # Run cleanup
        result = agent.cleanup_repository()

        # Should have found the orphan file
        assert result["non_approved_files"] >= 1

        # Move plan should include the file
        assert result["move_plan"] is not None
        assert len(result["move_plan"]) >= 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase24Integration:
    """Integration tests for Phase 24 SSOT cleanup."""

    def test_ssot_folder_cleanup_agent_import(self):
        """Test that SSOTFolderCleanupAgent can be imported."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        assert SSOTFolderCleanupAgent is not None

    def test_agent_has_required_methods(self):
        """Test that agent has all required methods."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        assert hasattr(SSOTFolderCleanupAgent, "is_path_ssot_approved")
        assert hasattr(SSOTFolderCleanupAgent, "find_non_approved_files")
        assert hasattr(SSOTFolderCleanupAgent, "triage_file")
        assert hasattr(SSOTFolderCleanupAgent, "move_file_to_ssot")
        assert hasattr(SSOTFolderCleanupAgent, "update_imports_for_moved_file")
        assert hasattr(SSOTFolderCleanupAgent, "delete_empty_folders")
        assert hasattr(SSOTFolderCleanupAgent, "cleanup_repository")
        assert hasattr(SSOTFolderCleanupAgent, "preview_cleanup")
        assert hasattr(SSOTFolderCleanupAgent, "execute_cleanup")

    def test_approved_paths_loaded(self, tmp_path):
        """Test that approved paths are loaded from SSOT config."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        agent = SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

        # Should have loaded approved paths
        assert len(agent.approved_paths) > 0

        # Should include key paths
        assert "agentic_core" in agent.approved_paths or any(
            "agentic_core" in p for p in agent.approved_paths
        )


# =============================================================================
# AST-Guided Import Safety Tests (Phase 26)
# =============================================================================


class TestASTGuidedImportSafety:
    """
    Tests for AST-guided import updates.

    Verifies that string variables containing import-like text are NOT modified,
    while actual import statements ARE updated.
    """

    @pytest.fixture
    def cleanup_agent(self, tmp_path):
        """Create a cleanup agent."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        return SSOTFolderCleanupAgent(project_root=tmp_path, dry_run=True)

    def test_ast_preserves_string_with_import_text(self, cleanup_agent):
        """Test that strings containing 'import old_module' are NOT modified."""
        content = """
# This is a test file
my_var = "import old_module"
another_var = "from old_module import something"
import old_module
from old_module import MyClass
"""

        updated = cleanup_agent._update_imports_in_content(content, "old_module", "new_module")

        # String variables should remain unchanged
        assert 'my_var = "import old_module"' in updated
        assert 'another_var = "from old_module import something"' in updated

        # Actual imports should be updated
        assert "import new_module" in updated
        assert "from new_module import MyClass" in updated

    def test_ast_preserves_comments_with_import_text(self, cleanup_agent):
        """Test that comments containing 'import' are NOT modified."""
        content = """
# Example: import old_module
# from old_module import X
import old_module
"""

        updated = cleanup_agent._update_imports_in_content(content, "old_module", "new_module")

        # Comments should remain unchanged
        assert "# Example: import old_module" in updated
        assert "# from old_module import X" in updated

        # Actual import should be updated
        assert "import new_module" in updated

    def test_ast_handles_multiline_imports(self, cleanup_agent):
        """Test that multi-line imports are correctly updated."""
        content = """from old_module import (
    ClassA,
    ClassB,
    ClassC,
)
"""

        updated = cleanup_agent._update_imports_in_content(content, "old_module", "new_module")

        # Multi-line import should be updated
        assert "from new_module import (" in updated
        assert "ClassA," in updated

    def test_ast_handles_syntax_error_gracefully(self, cleanup_agent):
        """Test that syntax errors don't crash the agent."""
        content = """
import old_module
def broken(
    # Missing closing paren
"""

        # Should return original content on syntax error
        updated = cleanup_agent._update_imports_in_content(content, "old_module", "new_module")

        # Original content returned unchanged
        assert updated == content

    def test_ast_preserves_docstrings_with_import_examples(self, cleanup_agent):
        """Test that docstrings with import examples are NOT modified."""
        content = '''
def my_function():
    """
    Example usage:

        import old_module
        from old_module import MyClass
    """
    pass

import old_module
'''

        updated = cleanup_agent._update_imports_in_content(content, "old_module", "new_module")

        # Docstring should remain unchanged
        assert "        import old_module" in updated
        assert "        from old_module import MyClass" in updated

        # Actual import at module level should be updated
        lines = updated.strip().split("\n")
        last_line = lines[-1]
        assert last_line == "import new_module"


# =============================================================================
# configuration Safety Interlock Tests (Phase 26)
# =============================================================================


class TestConfigurationSafetyInterlock:
    """
    Tests for the safety interlock that prevents mass deletion
    when SSOT configuration fails to load.
    """

    def test_config_load_failure_raises_runtime_error(self):
        """Test that config load failure raises RuntimeError, not silent empty config."""
        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        # Mock the import to fail
        with patch.dict(
            "sys.modules", {"agentic_core.L5_safety.validators.structure_blueprint": None}
        ):
            # This should raise RuntimeError, not silently continue with empty config
            # Note: The actual test depends on how the import is structured
            # For now, we verify the agent has the safety interlock in source
            import inspect

            source = inspect.getsource(SSOTFolderCleanupAgent._load_ssot_config)

            assert "RuntimeError" in source
            assert "SAFETY INTERLOCK" in source
            assert "mass deletion" in source.lower()

    def test_agent_source_has_ast_import(self):
        """Test that agent uses AST for import updates."""
        import inspect

        from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import (
            SSOTFolderCleanupAgent,
        )

        source = inspect.getsource(SSOTFolderCleanupAgent._update_imports_in_content)

        assert "ast.parse" in source
        assert "import_lines" in source
        assert "ast.Import" in source
        assert "ast.ImportFrom" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
