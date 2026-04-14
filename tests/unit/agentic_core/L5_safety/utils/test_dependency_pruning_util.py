"""Tests for dependency_pruning_util module."""

from __future__ import annotations

from pathlib import Path

import pytest

_dependency_pruning_util = pytest.importorskip(
    "agentic_core.L5_safety.utils.dependency_pruning_util",
    reason="Requires dependency pruning utility from the monorepo checkout.",
)
DependencyMatch = _dependency_pruning_util.DependencyMatch
DependencyPruningUtil = _dependency_pruning_util.DependencyPruningUtil
PruneAction = _dependency_pruning_util.PruneAction


class TestPruningResultDataclass:
    """Tests for PruningResult dataclass."""

    def test_pruning_result_creation(self):
        """Test PruningResult can be created."""
        result = PruningResult(
            unused_found=5,
            removed=3,
            dry_run=True,
            packages=["pkg1", "pkg2"],
            adg_dead_import_signals=2,
        )

        assert result.unused_found == 5
        assert result.removed == 3
        assert result.dry_run is True
        assert len(result.packages) == 2
        assert result.adg_dead_import_signals == 2

    def test_pruning_result_to_dict(self):
        """Test PruningResult to_dict method."""
        result = PruningResult(
            unused_found=0,
            removed=0,
            dry_run=False,
            packages=[],
        )

        d = result.to_dict()
        assert d["unused_found"] == 0
        assert d["removed"] == 0
        assert d["dry_run"] is False
        assert d["packages"] == []


class TestSafeExecute:
    """Tests for safe_execute function."""

    def test_safe_execute_success(self):
        """Test successful command execution."""
        result = safe_execute(["python", "--version"])

        assert result is not None
        assert result.returncode == 0

    def test_safe_execute_nonexistent_command(self):
        """Test handling of non-existent command."""
        result = safe_execute(["nonexistent_command_xyz"])

        assert result is None

    def test_safe_execute_with_cwd(self, tmp_path):
        """Test command execution with custom working directory."""
        result = safe_execute(["python", "-c", "import os; print(os.getcwd())"], cwd=tmp_path)

        assert result is not None
        assert str(tmp_path) in result.stdout


class TestFindUnusedDeptry:
    """Tests for find_unused_deptry function."""

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.safe_execute")
    def test_find_unused_deptry_success(self, mock_safe_execute, tmp_path):
        """Test successful deptry execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"unused": ["pkg1", "pkg2"]}'
        mock_safe_execute.return_value = mock_result

        result = find_unused_deptry(tmp_path)

        assert result == ["pkg1", "pkg2"]
        mock_safe_execute.assert_called_once_with(["deptry", ".", "--json"], cwd=tmp_path)

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.safe_execute")
    def test_find_unused_deptry_failure(self, mock_safe_execute, tmp_path):
        """Test deptry execution failure."""
        mock_safe_execute.return_value = None

        result = find_unused_deptry(tmp_path)

        assert result == []

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.safe_execute")
    def test_find_unused_deptry_bad_json(self, mock_safe_execute, tmp_path):
        """Test handling of invalid JSON output."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"
        mock_safe_execute.return_value = mock_result

        result = find_unused_deptry(tmp_path)

        assert result == []

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.safe_execute")
    def test_find_unused_deptry_missing_key(self, mock_safe_execute, tmp_path):
        """Test handling of JSON without 'unused' key."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"other": "data"}'
        mock_safe_execute.return_value = mock_result

        result = find_unused_deptry(tmp_path)

        assert result == []


class TestRemoveFromRequirementsTxt:
    """Tests for remove_from_requirements_txt function."""

    def test_remove_from_requirements_txt_dry_run(self, tmp_path):
        """Test dry run mode - returns count but doesn't modify file."""
        req_file = tmp_path / "requirements.txt"
        original_content = "numpy==1.0.0\nunused_pkg==2.0.0\n"
        req_file.write_text(original_content)

        result = remove_from_requirements_txt(["unused_pkg"], req_file, dry_run=True)

        assert result["removed"] == 1
        # In dry_run mode, file should NOT be modified (write happens only when dry_run=False)
        content = req_file.read_text()
        assert content == original_content  # File unchanged in dry_run mode

    def test_remove_from_requirements_txt_actual_remove(self, tmp_path):
        """Test actual removal mode."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("numpy==1.0.0\nunused_pkg==2.0.0\n")

        result = remove_from_requirements_txt(["unused_pkg"], req_file, dry_run=False)

        assert result["removed"] == 1
        content = req_file.read_text()
        assert "unused_pkg" not in content
        assert "numpy==1.0.0" in content

    def test_remove_from_requirements_txt_nonexistent_file(self, tmp_path):
        """Test handling of non-existent requirements file."""
        nonexistent = tmp_path / "requirements.txt"

        result = remove_from_requirements_txt(["pkg"], nonexistent)

        assert result["removed"] == 0

    def test_remove_from_requirements_txt_case_insensitive(self, tmp_path):
        """Test case-insensitive package matching."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("Unused_Pkg==2.0.0\n")

        result = remove_from_requirements_txt(["unused_pkg"], req_file, dry_run=True)

        assert result["removed"] == 1


class TestDependencyPruner:
    """Tests for DependencyPruner class."""

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_pruner_scan_no_unused(self, mock_find_unused, tmp_path):
        """Test scan with no unused dependencies."""
        mock_find_unused.return_value = []

        pruner = DependencyPruner(tmp_path)
        result = pruner.scan()

        assert result.unused_found == 0
        assert result.removed == 0
        assert result.packages == []

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_pruner_scan_with_unused(self, mock_find_unused, tmp_path):
        """Test scan with unused dependencies."""
        mock_find_unused.return_value = ["unused_pkg1", "unused_pkg2"]

        pruner = DependencyPruner(tmp_path)
        result = pruner.scan()

        assert result.unused_found == 2
        assert "unused_pkg1" in result.packages
        assert "unused_pkg2" in result.packages

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_pruner_prune_no_unused(self, mock_find_unused, tmp_path):
        """Test prune with no unused dependencies."""
        mock_find_unused.return_value = []

        pruner = DependencyPruner(tmp_path, dry_run=True)
        result = pruner.prune()

        assert result.unused_found == 0
        assert result.removed == 0

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_pruner_heal_repository(self, mock_find_unused, tmp_path):
        """Test heal_repository method."""
        mock_find_unused.return_value = []

        pruner = DependencyPruner(tmp_path, dry_run=True)
        result = pruner.heal_repository(dry_run=True)

        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "errors" in result
        assert "skipped" in result
        assert "packages" in result

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_pruner_heal_single_violation(self, mock_find_unused, tmp_path):
        """Test heal method for single violation."""
        # Create requirements.txt for the heal method
        (tmp_path / "requirements.txt").write_text("unused_pkg==1.0.0\n")
        mock_find_unused.return_value = ["unused_pkg"]

        pruner = DependencyPruner(tmp_path, dry_run=True)
        result = pruner.heal({"package": "unused_pkg"})

        assert "violations_fixed" in result
        assert "violations_found" in result


class TestPruneDependenciesConvenience:
    """Tests for prune_dependencies convenience function."""

    @patch("agentic_core.L5_safety.utils.dependency_pruning_util.find_unused_deptry")
    def test_prune_dependencies_convenience(self, mock_find_unused, tmp_path):
        """Test the prune_dependencies convenience function."""
        mock_find_unused.return_value = []

        result = prune_dependencies(tmp_path, dry_run=True)

        assert isinstance(result, PruningResult)
        assert result.unused_found == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
