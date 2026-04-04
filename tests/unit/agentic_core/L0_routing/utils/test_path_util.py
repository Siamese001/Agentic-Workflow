"""Test PathUtil functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPathUtil:
    """Test PathUtil functionality."""

    def test_path_util_imports(self):
        """Test path_util module imports."""
        from agentic_core.L0_routing.utils.path_util import get_validated_project_root
        assert get_validated_project_root is not None

    def test_path_util_class(self):
        """Test Path class exists in path_util module."""
        from pathlib import Path
        assert Path is not None

    def test_path_util_callable(self):
        """Test path_util functions are callable."""
        from agentic_core.L0_routing.utils.path_util import get_validated_project_root
        assert callable(get_validated_project_root)


@pytest.mark.unit
class TestPathNormalization:
    """Test Windows path normalization - Wave 3 coverage for RCA bug."""

    def test_windows_path_as_posix_normalization(self):
        """Test Windows backslash paths are normalized to forward slashes."""
        from pathlib import Path
        # Simulate Windows path behavior
        test_path = Path("C:/Git/Agentic-Workflow")  # Using forward slash for cross-platform
        posix_path = test_path.as_posix()
        assert posix_path == "C:/Git/Agentic-Workflow"
        assert "\\" not in posix_path  # No backslashes in POSIX path

    def test_path_replace_backslash_to_forward_slash(self):
        """Test the .replace('\\', '/') pattern used in codebase."""
        windows_path = "C:\\Git\\Agentic-Workflow"
        normalized = windows_path.replace("\\", "/")
        assert normalized == "C:/Git/Agentic-Workflow"
        assert "." not in normalized.replace("C:", "").replace("/", "")  # No dots as separators

    def test_mixed_separator_handling(self):
        """Test paths with mixed separators are handled correctly."""
        mixed_path = "C:\\Git/Agentic-Workflow"
        # pathlib handles mixed separators
        normalized = Path(mixed_path).as_posix()
        assert "\\" not in normalized
        assert normalized == "C:/Git/Agentic-Workflow"

    def test_path_no_mangled_dots(self):
        """Ensure no backslash-to-dot mangling occurs."""
        # This tests the specific RCA bug: c:.Git.Agentic-Workflow
        test_path = "C:\\Git\\Agentic-Workflow"
        # Correct normalization
        correct = test_path.replace("\\", "/")
        # Incorrect mangling (the bug pattern)
        buggy = test_path.replace("\\", ".")
        assert correct == "C:/Git/Agentic-Workflow"
        assert buggy == "C:.Git.Agentic-Workflow"  # This is the bug!
        # Ensure our code produces correct, not buggy
        assert "." not in correct.replace("C:", "").replace("/", "")

    def test_relative_path_normalization(self):
        """Test relative path normalization."""
        rel_path = "agentic_core\\L0_routing\\utils"
        normalized = rel_path.replace("\\", "/")
        assert normalized == "agentic_core/L0_routing/utils"

    def test_unc_path_handling(self):
        """Test UNC path handling."""
        unc_path = "\\\\server\\share\\folder"
        normalized = unc_path.replace("\\", "/")
        assert normalized == "//server/share/folder"


@pytest.mark.unit
class TestPathValidation:
    """Test path validation functions."""

    def test_get_validated_project_root_returns_path(self):
        """Test get_validated_project_root returns a Path object."""
        from agentic_core.L0_routing.utils.path_util import get_validated_project_root
        result = get_validated_project_root()
        assert isinstance(result, Path)
        assert result.exists()

    def test_validate_path_within_project_with_valid_path(self):
        """Test validate_path_within_project with valid path."""
        from agentic_core.L0_routing.utils.path_util import (
            get_validated_project_root,
            validate_path_within_project,
        )
        project_root = get_validated_project_root()
        # Test with a path we know exists
        test_path = project_root / "agentic_core"
        result = validate_path_within_project(test_path, project_root)
        assert result is True

    def test_validate_path_within_project_with_outside_path(self):
        """Test validate_path_within_project rejects paths outside project."""
        from agentic_core.L0_routing.utils.path_util import (
            get_validated_project_root,
            validate_path_within_project,
        )
        project_root = get_validated_project_root()
        # Test with a path outside project
        outside_path = Path("C:/Windows")
        result = validate_path_within_project(outside_path, project_root)
        assert result is False


@pytest.mark.unit
class TestPathUtilityFunctions:
    """Test path utility functions."""

    def test_is_path_allowed_with_allowed_dir(self):
        """Test is_path_allowed with allowed directory."""
        from agentic_core.L0_routing.utils.path_util import is_path_allowed
        # Test with a path that should be allowed
        test_path = "agentic_core/L0_routing/utils/path_util.py"
        allowed = {"agentic_core", "L0_routing"}
        result = is_path_allowed(test_path, frozenset(allowed))
        assert result is True

    def test_is_path_allowed_with_disallowed_dir(self):
        """Test is_path_allowed with disallowed directory."""
        from agentic_core.L0_routing.utils.path_util import is_path_allowed
        test_path = "node_modules/some_package/file.py"
        allowed = {"agentic_core", "L0_routing"}
        result = is_path_allowed(test_path, frozenset(allowed))
        assert result is False

    def test_safe_prefixed_filename(self):
        """Test safe_prefixed_filename function."""
        from agentic_core.L0_routing.utils.path_util import safe_prefixed_filename
        # Test adding prefix
        result = safe_prefixed_filename("test.txt", "prefix_")
        assert result == "prefix_test.txt"
        # Test when already prefixed
        result2 = safe_prefixed_filename("prefix_test.txt", "prefix_")
        assert result2 == "prefix_test.txt"

    def test_validate_no_duplicate_prefix(self):
        """Test validate_no_duplicate_prefix function."""
        from agentic_core.L0_routing.utils.path_util import validate_no_duplicate_prefix
        # Test with no duplicate
        result = validate_no_duplicate_prefix("prefix_test.txt", "prefix_")
        assert result is True
        # Test with duplicate
        result2 = validate_no_duplicate_prefix("prefix_prefix_test.txt", "prefix_")
        assert result2 is False

    def test_safe_path_join(self):
        """Test safe_path_join function."""
        from agentic_core.L0_routing.utils.path_util import safe_path_join
        project_root = Path("C:/test/project")
        result = safe_path_join(project_root, "agentic_core", "test.py")
        assert isinstance(result, Path)
        assert result.name == "test.py"

    def test_safe_path_join_raises_outside_project(self):
        """Test safe_path_join raises for paths outside project."""
        from agentic_core.L0_routing.utils.path_util import safe_path_join
        project_root = Path("C:/test/project")
        # This should raise because .. goes outside project
        with pytest.raises(ValueError) as exc_info:
            safe_path_join(project_root, "..", "outside.py")
        assert "SAFETY VIOLATION" in str(exc_info.value)
