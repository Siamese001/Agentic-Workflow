"""Unit tests for FileClassificationAgent helper methods.

Tests follow MECE principle: Mutually Exclusive, Collectively Exhaustive
coverage of helper methods like cleanup, update_file_header, etc.
"""

import tempfile
from pathlib import Path
import pytest
import sys
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestCleanupRedundantConflicts:
    """Test cleanup_redundant_conflicts method."""

    def test_cleanup_redundant_conflicts_dry_run(self):
        """Test that dry_run mode doesn't delete files."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.dry_run = True
        agent.project_root = Path.cwd()

        # Should return early in dry run
        agent.cleanup_redundant_conflicts(Path.cwd())  # Should not crash

    def test_cleanup_redundant_conflicts_identical_files(self):
        """Test cleanup of byte-identical conflict files."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create original file
            original_file = tmpdir / "TestFile.py"
            original_content = b"class TestFile:\n    pass\n"
            original_file.write_bytes(original_content)

            # Create identical conflict file
            conflict_file = tmpdir / "TestFile.conflict.py"
            conflict_file.write_bytes(original_content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

            with patch("builtins.print") as mock_print:
                agent.cleanup_redundant_conflicts(tmpdir)

            # Conflict file should be deleted
            assert not conflict_file.exists()
            assert original_file.exists()

            # Should have printed deletion message
            mock_print.assert_any_call(f"  [DELETE] Redundant backup: {conflict_file.name}")

    def test_cleanup_redundant_conflicts_different_files(self):
        """Test that different conflict files are not deleted."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create original file
            original_file = tmpdir / "TestFile.py"
            original_content = b"class TestFile:\n    pass\n"
            original_file.write_bytes(original_content)

            # Create different conflict file
            conflict_file = tmpdir / "TestFile.conflict.py"
            different_content = b"class TestFile:\n    pass\n# Different\n"
            conflict_file.write_bytes(different_content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

            with patch("builtins.print"):
                agent.cleanup_redundant_conflicts(tmpdir)

            # Both files should still exist
            assert original_file.exists()
            assert conflict_file.exists()


class TestUpdateFileHeader:
    """Test update_file_header method."""

    def test_update_file_header_dry_run(self):
        """Test that dry_run mode doesn't modify files."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test file
            test_file = tmpdir / "OldName.py"
            content = '"""File: OldName.py\nPath: OldName.py\n"""'
            test_file.write_text(content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = True

            agent.update_file_header(test_file, "OldName.py", "NewName.py")

            # File should be unchanged
            assert test_file.read_text() == content

    def test_update_file_header_updates_content(self):
        """Test that file headers are updated correctly."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test file with old name in header
            test_file = tmpdir / "OldName.py"
            content = '"""File: OldName.py\nPath: some/path/OldName.py\n"""\nclass OldName:\n    pass\n'
            test_file.write_text(content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False

            agent.update_file_header(test_file, "OldName.py", "NewName.py")

            # File should be updated
            updated_content = test_file.read_text()
            assert "NewName.py" in updated_content
            assert "OldName.py" not in updated_content

    def test_update_file_header_handles_exceptions(self):
        """Test that exceptions are handled gracefully."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Create agent
        agent = object.__new__(FileClassificationAgent)
        agent.dry_run = False

        # Should not crash on non-existent file
        agent.update_file_header(Path("/nonexistent/file.py"), "Old.py", "New.py")


class TestSyncCompanionTest:
    """Test sync_companion_test method."""

    def test_sync_companion_test_no_tests_dir(self):
        """Test behavior when tests directory doesn't exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create source file
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should not attempt rename
            agent.resolve_collision_and_rename.assert_not_called()

    def test_sync_companion_test_test_prefix_pattern(self):
        """Test renaming test files with test_ prefix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            tests_dir = tmpdir / "tests"
            tests_dir.mkdir()

            # Create source and test files
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            test_file = tests_dir / "test_old_name.py"
            test_file.write_text("class TestOldName:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should attempt rename with correct new name
            agent.resolve_collision_and_rename.assert_called_once_with(test_file, "test_new_name.py")

    def test_sync_companion_test_suffix_pattern(self):
        """Test renaming test files with _test suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            tests_dir = tmpdir / "tests"
            tests_dir.mkdir()

            # Create source and test files
            src_file = tmpdir / "OldName.py"
            src_file.write_text("class OldName:\n    pass\n")

            test_file = tests_dir / "old_name_test.py"
            test_file.write_text("class OldNameTest:\n    pass\n")

            agent = object.__new__(FileClassificationAgent)
            agent.project_root = tmpdir
            agent.resolve_collision_and_rename = MagicMock()

            agent.sync_companion_test(src_file, "NewName.py")

            # Should attempt rename with correct new name
            agent.resolve_collision_and_rename.assert_called_once_with(test_file, "new_name_test.py")


class TestRefactorNonPythonAssets:
    """Test refactor_non_python_assets method."""

    def test_refactor_non_python_assets_updates_json(self):
        """Test that JSON files are updated."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create config file with old name
            config_file = tmpdir / "config.json"
            content = '{"agents": ["OldName"], "main_class": "OldName"}'
            config_file.write_text(content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

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
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
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

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = False
            agent.project_root = tmpdir

            agent.refactor_non_python_assets("OldName", "NewName")

            # File should be updated
            updated_content = yaml_file.read_text()
            assert "NewName" in updated_content
            assert "OldName" not in updated_content

    def test_refactor_non_python_assets_dry_run(self):
        """Test that dry_run mode doesn't modify files."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create config file
            config_file = tmpdir / "config.json"
            content = '{"agents": ["OldName"]}'
            config_file.write_text(content)

            agent = object.__new__(FileClassificationAgent)
            agent.dry_run = True
            agent.project_root = tmpdir

            agent.refactor_non_python_assets("OldName", "NewName")

            # File should be unchanged
            assert config_file.read_text() == content


class TestMethodSignatures:
    """Test that helper methods have correct signatures."""

    def test_cleanup_redundant_conflicts_signature(self):
        """Test cleanup_redundant_conflicts method signature."""
        import inspect

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.cleanup_redundant_conflicts
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "root"], f"Expected ['self', 'root'], got {params}"
        assert sig.parameters["root"].annotation == Path, (
            f"Expected Path annotation for root, got {sig.parameters['root'].annotation}"
        )

    def test_update_file_header_signature(self):
        """Test update_file_header method signature."""
        import inspect

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.update_file_header
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "path", "old_name", "new_name"]
        assert sig.parameters["path"].annotation == Path, (
            f"Expected Path annotation for path, got {sig.parameters['path'].annotation}"
        )

    def test_sync_companion_test_signature(self):
        """Test sync_companion_test method signature."""
        import inspect

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.sync_companion_test
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "src_path", "new_name"]
        assert sig.parameters["src_path"].annotation == Path, (
            f"Expected Path annotation for src_path, got {sig.parameters['src_path'].annotation}"
        )

    def test_refactor_non_python_assets_signature(self):
        """Test refactor_non_python_assets method signature."""
        import inspect

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent.refactor_non_python_assets
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "old_name", "new_name"]

    def test_to_smart_snake_case_signature(self):
        """Test _to_smart_snake_case method signature."""
        import inspect

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        method = FileClassificationAgent._to_smart_snake_case
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert params == ["self", "name"]
        assert sig.parameters["name"].annotation == str, (
            f"Expected str annotation for name, got {sig.parameters['name'].annotation}"
        )
        assert sig.return_annotation == str, f"Expected str return annotation, got {sig.return_annotation}"
