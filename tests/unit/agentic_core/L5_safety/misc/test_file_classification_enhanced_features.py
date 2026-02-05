"""
Unit tests for FileClassificationAgent enhanced features.

Tests for new functionality added in the latest enhancement:
1. cleanup_redundant_conflicts method
2. update_file_header method
3. sync_companion_test method
4. refactor_non_python_assets method
5. Enhanced _orchestrate_audit method integration
"""

# Add project root to path
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestCleanupRedundantConflicts:
    """Test the cleanup_redundant_conflicts method."""

    def test_cleanup_redundant_conflicts_dry_run(self):
        """Test that dry_run mode doesn't delete files."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        # Create agent instance (bypassing SovereignBaseAgent)
        agent = object.__new__(FileClassificationAgent)
        agent.dry_run = True
        agent.project_root = Path.cwd()

        # Should return early in dry run
        agent.cleanup_redundant_conflicts(Path.cwd())  # Should not crash

    def test_cleanup_redundant_conflicts_identical_files(self):
        """Test cleanup of byte-identical conflict files."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create original file
            original_file = tmpdir / "TestFile.py"
            original_content = b"class TestFile:\n    pass\n"
            original_file.write_bytes(original_content)

            # Create identical conflict file
            timestamp = int(time.time())
            conflict_file = tmpdir / f"TestFile.py.CONFLICT_{timestamp}"
            conflict_file.write_bytes(original_content)

            # Create agent and cleanup
            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

            # Mock print to capture output
            with patch("builtins.print") as mock_print:
                agent.cleanup_redundant_conflicts(tmpdir)

            # Conflict file should be deleted
            assert not conflict_file.exists()
            assert original_file.exists()

            # Should have printed deletion message
            mock_print.assert_any_call(f"  [DELETE] Redundant backup: {conflict_file.name}")

    def test_cleanup_redundant_conflicts_different_files(self):
        """Test that different conflict files are not deleted."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create original file
            original_file = tmpdir / "TestFile.py"
            original_content = b"class TestFile:\n    pass\n"
            original_file.write_bytes(original_content)

            # Create different conflict file
            timestamp = int(time.time())
            conflict_file = tmpdir / f"TestFile.py.CONFLICT_{timestamp}"
            different_content = b"class TestFile:\n    pass\n    # Different comment\n"
            conflict_file.write_bytes(different_content)

            # Create agent and cleanup
            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

            agent.cleanup_redundant_conflicts(tmpdir)

            # Both files should still exist
            assert original_file.exists()
            assert conflict_file.exists()


class TestUpdateFileHeader:
    """Test the update_file_header method."""

    def test_update_file_header_dry_run(self):
        """Test that dry_run mode doesn't modify files."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test file
            test_file = tmpdir / "OldName.py"
            content = '"""File: OldName.py\nPath: OldName.py\n"""'
            test_file.write_text(content)

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = True

            agent.update_file_header(test_file, "OldName.py", "NewName.py")

            # File should be unchanged
            assert test_file.read_text() == content

    def test_update_file_header_updates_content(self):
        """Test that file headers are updated correctly."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test file with old name in header
            test_file = tmpdir / "OldName.py"
            content = '"""File: OldName.py\nPath: some/path/OldName.py\n"""\nclass OldName:\n    pass\n'
            test_file.write_text(content)

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False

            agent.update_file_header(test_file, "OldName.py", "NewName.py")

            # File should be updated
            updated_content = test_file.read_text()
            assert "NewName.py" in updated_content
            assert "OldName.py" not in updated_content

    def test_update_file_header_handles_exceptions(self):
        """Test that exceptions are handled gracefully."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        # Create agent
        agent = object.__new__(FileClassificationAgent)
        agent.dry_run = False

        # Should not crash on non-existent file
        agent.update_file_header(Path("/nonexistent/file.py"), "Old.py", "New.py")


class TestSyncCompanionTest:
    """Test the sync_companion_test method."""

    def test_sync_companion_test_no_tests_dir(self):
        """Test behavior when tests directory doesn't exist."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create source file
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            # Create agent (no tests directory)
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should not attempt rename
            agent.resolve_collision_and_rename.assert_not_called()

    def test_sync_companion_test_test_prefix_pattern(self):
        """Test renaming test files with test_ prefix."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            tests_dir = tmpdir / "tests"
            tests_dir.mkdir()

            # Create source and test files
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            test_file = tests_dir / "test_OldName.py"
            test_file.write_text("def test_old_name():\n    pass\n")

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should attempt rename with correct new name
            agent.resolve_collision_and_rename.assert_called_once_with(test_file, "test_NewName.py")

    def test_sync_companion_test_suffix_pattern(self):
        """Test renaming test files with _test suffix."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            tests_dir = tmpdir / "tests"
            tests_dir.mkdir()

            # Create source and test files
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            test_file = tests_dir / "OldName_test.py"
            test_file.write_text("def test_old_name():\n    pass\n")

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should attempt rename with correct new name
            agent.resolve_collision_and_rename.assert_called_once_with(test_file, "NewName_test.py")


class TestRefactorNonPythonAssets:
    """Test the refactor_non_python_assets method."""

    def test_refactor_non_python_assets_updates_json(self):
        """Test that JSON files are updated."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create config file with old name
            config_file = tmpdir / "config.json"
            content = '{"agents": ["OldName"], "main_class": "OldName"}'
            config_file.write_text(content)

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.dry_run = False

            with patch("builtins.print") as mock_print:
                agent.refactor_non_python_assets("OldName", "NewName")

            # File should be updated
            updated_content = config_file.read_text()
            assert "NewName" in updated_content
            assert "OldName" not in updated_content

            # Should print update message
            mock_print.assert_any_call("  [CONFIG] Updating reference in config.json")

    def test_refactor_non_python_assets_updates_yaml(self):
        """Test that YAML files are updated."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_dir = tmpdir / "config"
            config_dir.mkdir()

            # Create YAML file with old name
            yaml_file = config_dir / "settings.yaml"
            content = "agents:\n  - OldName\nmain_class: OldName\n"
            yaml_file.write_text(content)

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.dry_run = False

            agent.refactor_non_python_assets("OldName", "NewName")

            # File should be updated
            updated_content = yaml_file.read_text()
            assert "NewName" in updated_content
            assert "OldName" not in updated_content

    def test_refactor_non_python_assets_dry_run(self):
        """Test that dry_run mode doesn't modify files."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create config file
            config_file = tmpdir / "config.json"
            content = '{"agents": ["OldName"]}'
            config_file.write_text(content)

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.dry_run = True

            agent.refactor_non_python_assets("OldName", "NewName")

            # File should be unchanged
            assert config_file.read_text() == content


class TestEnhancedOrchestrateAudit:
    """Test the enhanced _orchestrate_audit method."""

    def test_orchestrate_audit_calls_new_methods(self):
        """Test that _orchestrate_audit calls the new helper methods."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        # Create agent with mocked methods
        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd()
        agent.dry_run = True
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "deep_refactors": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
                # WINDSURF IMPLEMENTATION: New categories
                "ORCHESTRATOR": 0,
                "VALIDATOR": 0,
                "FACTORY": 0,
                "CONFIG": 0,
                "ADAPTER": 0,
            },
        }
        agent.file_registry = []

        # Mock all the new methods
        agent.cleanup_redundant_conflicts = MagicMock()
        agent.update_file_header = MagicMock()
        agent.sync_companion_test = MagicMock()
        agent.refactor_non_python_assets = MagicMock()

        # Mock other required methods
        agent.verify_environment = MagicMock(return_value=True)
        agent.classify_file = MagicMock(return_value="AGENT")
        agent.get_compliant_name = MagicMock(return_value=None)  # No violations
        agent.resolve_collision_and_rename = MagicMock(return_value=False)

        # Mock print to avoid output
        with patch("builtins.print"):
            agent._orchestrate_audit(Path.cwd())

        # cleanup_redundant_conflicts should be called at the end
        agent.cleanup_redundant_conflicts.assert_called_once_with(Path.cwd())

    def test_orchestrate_audit_integration_flow(self):
        """Test the complete integration flow when a file is renamed."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a test file that needs renaming
            test_file = tmpdir / "OldName.py"
            test_file.write_text("class OldName:\n    pass\n")

            # Create agent
            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.dry_run = False
            agent.validate_only = False
            agent.stats = {
                "analyzed": 0,
                "compliant": 0,
                "renamed": 0,
                "imports_fixed": 0,
                "deep_refactors": 0,
                "collisions_resolved": 0,
                "violations": {
                    "AGENT": 0,
                    "CLASS": 0,
                    "MIXIN": 0,
                    "UTILITY": 0,
                    "PROTOCOL": 0,
                    "ENGINE": 0,
                    "STUB": 0,
                    "TEST": 0,
                    "SCRIPT": 0,
                    "TYPES": 0,
                    "GATEWAY": 0,
                    # WINDSURF IMPLEMENTATION: New categories
                    "ORCHESTRATOR": 0,
                    "VALIDATOR": 0,
                    "FACTORY": 0,
                    "CONFIG": 0,
                    "ADAPTER": 0,
                },
            }
            agent.file_registry = [test_file]

            # Mock methods to verify they're called
            agent.update_file_header = MagicMock()
            agent.sync_companion_test = MagicMock()
            agent.refactor_non_python_assets = MagicMock()
            agent.cleanup_redundant_conflicts = MagicMock()

            # Mock other methods
            agent.verify_environment = MagicMock(return_value=True)
            agent.classify_file = MagicMock(return_value="AGENT")
            agent.get_compliant_name = MagicMock(return_value="NewNameAgent.py")
            agent.deep_refactor_name = MagicMock(return_value=1)
            agent.update_imports = MagicMock(return_value=1)

            # Mock resolve_collision_and_rename to actually rename the file
            def mock_rename(src, dest_name):
                dest = src.parent / dest_name
                src.rename(dest)
                return True

            agent.resolve_collision_and_rename = MagicMock(side_effect=mock_rename)

            # Mock get_python_files_fast to return our test file
            with patch(
                "agentic_core.L5_safety.validators.FileClassificationAgent.get_python_files_fast",
                return_value=[test_file],
            ):
                # Mock print to avoid output
                with patch("builtins.print"):
                    agent._orchestrate_audit(tmpdir)

            # Verify new methods were called
            agent.update_file_header.assert_called_once()
            agent.sync_companion_test.assert_called_once()
            agent.refactor_non_python_assets.assert_called_once()
            agent.cleanup_redundant_conflicts.assert_called_once()


class TestMethodSignatures:
    """Test that new methods have correct signatures."""

    def test_cleanup_redundant_conflicts_signature(self):
        """Test cleanup_redundant_conflicts method signature."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.cleanup_redundant_conflicts
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "root"], f"Expected ['self', 'root'], got {params}"
        assert (
            sig.parameters["root"].annotation == Path
            or str(sig.parameters["root"].annotation) == "<class 'pathlib.Path'>"
        )

    def test_update_file_header_signature(self):
        """Test update_file_header method signature."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.update_file_header
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "path", "old_name", "new_name"]
        assert (
            sig.parameters["path"].annotation == Path
            or str(sig.parameters["path"].annotation) == "<class 'pathlib.Path'>"
        )

    def test_sync_companion_test_signature(self):
        """Test sync_companion_test method signature."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.sync_companion_test
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "src_path", "new_name"]
        assert (
            sig.parameters["src_path"].annotation == Path
            or str(sig.parameters["src_path"].annotation) == "<class 'pathlib.Path'>"
        )

    def test_refactor_non_python_assets_signature(self):
        """Test refactor_non_python_assets method signature."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.refactor_non_python_assets
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "old_name", "new_name"]


class TestSmartSnakeCaseConversion:
    """Test the _to_smart_snake_case method for acronym preservation."""

    def test_smart_snake_case_simple(self):
        """Test basic PascalCase to snake_case conversion."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd()

        assert agent._to_smart_snake_case("MyClass") == "my_class"
        assert agent._to_smart_snake_case("SimpleTest") == "simple_test"

    def test_smart_snake_case_with_acronyms(self):
        """Test that acronyms are preserved correctly."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd()

        # PIISanitizer should become pii_sanitizer, not p_i_i_sanitizer
        assert agent._to_smart_snake_case("PIISanitizer") == "pii_sanitizer"
        assert agent._to_smart_snake_case("PDFLoader") == "pdf_loader"
        assert agent._to_smart_snake_case("HTTPClient") == "http_client"
        assert agent._to_smart_snake_case("XMLParser") == "xml_parser"

    def test_smart_snake_case_mixed(self):
        """Test mixed acronyms and regular words."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd()

        assert agent._to_smart_snake_case("MyPDFReader") == "my_pdf_reader"
        assert agent._to_smart_snake_case("HTTPSConnectionManager") == "https_connection_manager"

    def test_smart_snake_case_already_lowercase(self):
        """Test that lowercase names are handled correctly."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd()

        assert agent._to_smart_snake_case("myclass") == "myclass"
        assert agent._to_smart_snake_case("test") == "test"


class TestPrimaryClassCentricDetection:
    """Test the refactored primary-class-centric detection logic."""

    def test_primary_class_detection_matches_filename(self):
        """Test that primary class is determined by filename match."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create file with multiple classes where one matches filename
            test_file = tmpdir / "MyAgent.py"
            test_file.write_text(
                "class HelperClass:\n    pass\n\nclass MyAgent:\n    pass\n\nclass AnotherHelper:\n    pass\n"
            )

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "AGENT", f"Expected AGENT (primary class MyAgent), got {file_type}"

    def test_primary_class_fallback_to_first_class(self):
        """Test fallback to first class when no filename match."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create file with classes that don't match filename
            test_file = tmpdir / "utilities.py"
            test_file.write_text("class MyHelper:\n    pass\n\nclass AnotherClass:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            # First class (MyHelper) is used - should be CLASS
            assert file_type == "CLASS", f"Expected CLASS, got {file_type}"


class TestExceptionClassification:
    """Test that Exception classes are classified as CLASS."""

    def test_exception_class_by_name(self):
        """Test that classes ending in Error or Exception are CLASS."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create custom exception file
            test_file = tmpdir / "CustomError.py"
            test_file.write_text("class CustomError(Exception):\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "CLASS", f"Expected CLASS for exception, got {file_type}"

    def test_exception_class_by_inheritance(self):
        """Test that classes inheriting from Exception are CLASS."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create custom exception with non-Error/Exception name
            test_file = tmpdir / "ValidationFailure.py"
            test_file.write_text("class ValidationFailure(Exception):\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "CLASS", f"Expected CLASS for exception subclass, got {file_type}"


class TestMixinPriorityElevation:
    """Test that MIXIN priority is elevated to prevent override."""

    def test_mixin_not_overridden_by_orchestrator_patterns(self):
        """Test that Mixin files are not misclassified as Orchestrator."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mixin that has workflow-like content
            test_file = tmpdir / "WorkflowMixin.py"
            test_file.write_text(
                "class WorkflowMixin:\n    def orchestrate(self): pass\n    def coordinate(self): pass\n"
            )

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "MIXIN", f"Expected MIXIN, got {file_type}"


class TestAgentExclusionFromScript:
    """Test that Agents are not misclassified as SCRIPT."""

    def test_agent_with_main_guard_stays_agent(self):
        """Test that Agent with if __name__ == '__main__' stays AGENT."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create agent with main guard (common for testing)
            test_file = tmpdir / "MyAgent.py"
            test_file.write_text(
                "class MyAgent:\n"
                "    def execute(self): pass\n\n"
                "if __name__ == '__main__':\n"
                "    agent = MyAgent()\n"
                "    agent.execute()\n"
            )

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "AGENT", f"Expected AGENT despite main guard, got {file_type}"

    def test_agent_inheriting_base_with_argparse_stays_agent(self):
        """Test that Agent using argparse stays AGENT."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create agent that imports argparse
            test_file = tmpdir / "CLIAgent.py"
            test_file.write_text("import argparse\n\nclass CLIAgent:\n    def run(self): pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            assert file_type == "AGENT", f"Expected AGENT despite argparse, got {file_type}"


class TestOrchestratorNamingFix:
    """Test that ORCHESTRATOR naming strips Agent/Service suffixes."""

    def test_orchestrator_strips_agent_suffix(self):
        """Test that Agent suffix is stripped before adding Orchestrator."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            test_file = tmpdir / "MyOrchestratorAgent.py"
            test_file.write_text("class MyOrchestratorAgent:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            new_name = agent.get_compliant_name(test_file, file_type)

            # Should be MyOrchestrator.py, not MyOrchestratorAgentOrchestrator.py
            if new_name:
                assert "AgentOrchestrator" not in new_name, f"Should not have AgentOrchestrator: {new_name}"

    def test_orchestrator_strips_service_suffix(self):
        """Test that Service suffix is stripped before adding Orchestrator."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            test_file = tmpdir / "ConfigurationService.py"
            test_file.write_text("class ConfigurationService:\n    def orchestrate(self): pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            if file_type == "ORCHESTRATOR":
                new_name = agent.get_compliant_name(test_file, file_type)
                if new_name:
                    assert "ServiceOrchestrator" not in new_name, (
                        f"Should not have ServiceOrchestrator: {new_name}"
                    )


class TestAdapterNamingFix:
    """Test that ADAPTER naming strips Agent suffix."""

    def test_adapter_strips_agent_suffix(self):
        """Test that Agent suffix is stripped before adding Strategy."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            test_file = tmpdir / "MyStrategyAgent.py"
            test_file.write_text("class MyStrategyAgent:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            if file_type == "ADAPTER":
                new_name = agent.get_compliant_name(test_file, file_type)
                if new_name:
                    assert "AgentStrategy" not in new_name, f"Should not have AgentStrategy: {new_name}"


class TestValidatorConfigSnakeCase:
    """Test that VALIDATOR and CONFIG use _to_smart_snake_case."""

    def test_validator_uses_smart_snake_case(self):
        """Test validator naming uses smart snake_case for acronyms."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            test_file = tmpdir / "PIIValidator.py"
            test_file.write_text("class PIIValidator:\n    def validate(self): pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            if file_type == "VALIDATOR":
                new_name = agent.get_compliant_name(test_file, file_type)
                if new_name:
                    # Should preserve PII as pii, not p_i_i
                    assert "p_i_i" not in new_name, f"Should use smart snake_case: {new_name}"

    def test_config_uses_smart_snake_case(self):
        """Test config naming uses smart snake_case for acronyms."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            test_file = tmpdir / "APIConfig.py"
            test_file.write_text("class APIConfig:\n    API_KEY = 'test'\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir

            file_type = agent.classify_file(test_file)
            if file_type == "CONFIG":
                new_name = agent.get_compliant_name(test_file, file_type)
                if new_name:
                    # Should preserve API as api, not a_p_i
                    assert "a_p_i" not in new_name, f"Should use smart snake_case: {new_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
