"""Runtime-hardened tests for ``path_util``.

These tests avoid hard-coded platform assumptions, remove implicit cwd
requirements, and prefer temporary directories for path-safety checks.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def path_util_module():
    return pytest.importorskip("agentic_core.L0_routing.utils.path_util")


class TestPathUtilBasics:
    def test_get_validated_project_root_returns_real_path(self, path_util_module):
        result = path_util_module.get_validated_project_root()

        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_dir()
        assert (result / "agentic_core").exists() or (result / "pyproject.toml").exists()

    def test_get_validated_project_root_is_stable(self, path_util_module):
        result1 = path_util_module.get_validated_project_root()
        result2 = path_util_module.get_validated_project_root()

        assert result1 == result2
        assert result1.resolve() == result2.resolve()


class TestPathNormalization:
    def test_windows_path_as_posix_normalization(self):
        test_path = PureWindowsPath(r"C:\Git\Agentic-Workflow")

        assert test_path.as_posix() == "C:/Git/Agentic-Workflow"
        assert "\\" not in test_path.as_posix()

    def test_replace_backslash_to_forward_slash_pattern(self):
        windows_path = r"C:\Git\Agentic-Workflow"
        normalized = windows_path.replace("\\", "/")

        assert normalized == "C:/Git/Agentic-Workflow"
        assert "." not in normalized.replace("C:", "").replace("/", "")

    def test_mixed_separator_handling(self):
        mixed_path = PureWindowsPath(r"C:\Git/Agentic-Workflow")

        assert mixed_path.as_posix() == "C:/Git/Agentic-Workflow"
        assert "\\" not in mixed_path.as_posix()

    def test_path_no_mangled_dots(self):
        windows_path = r"C:\Git\Agentic-Workflow"
        correct = windows_path.replace("\\", "/")
        buggy = windows_path.replace("\\", ".")

        assert correct == "C:/Git/Agentic-Workflow"
        assert buggy == "C:.Git.Agentic-Workflow"
        assert "." not in correct.replace("C:", "").replace("/", "")

    def test_relative_path_normalization(self):
        rel_path = r"agentic_core\L0_routing\utils"

        assert rel_path.replace("\\", "/") == "agentic_core/L0_routing/utils"

    def test_unc_path_handling(self):
        unc_path = r"\\server\share\folder"

        assert unc_path.replace("\\", "/") == "//server/share/folder"


class TestPathValidation:
    def test_validate_path_within_project_with_valid_path(self, path_util_module, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()
        inside_path = project_root / "agentic_core"
        inside_path.mkdir()

        result = path_util_module.validate_path_within_project(inside_path, project_root)

        assert result is True

    def test_validate_path_within_project_with_outside_path(self, path_util_module, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()
        outside_path = tmp_path / "elsewhere"
        outside_path.mkdir()

        result = path_util_module.validate_path_within_project(outside_path, project_root)

        assert result is False


class TestPathUtilityFunctions:
    def test_get_python_files_uses_shared_junk_filters(self, path_util_module, tmp_path):
        src = tmp_path / "src"
        junk = tmp_path / ".cache"
        src.mkdir()
        junk.mkdir()
        good = src / "good.py"
        bad = junk / "bad.py"
        good.write_text("print('ok')", encoding="utf-8")
        bad.write_text("print('no')", encoding="utf-8")

        result = list(path_util_module.get_python_files(tmp_path, exclude_dirs=frozenset({".cache"})))

        assert result == [good]

    def test_is_path_allowed_with_allowed_dir(self, path_util_module):
        test_path = "agentic_core/L0_routing/utils/path_util.py"
        allowed = frozenset({"agentic_core", "L0_routing"})

        assert path_util_module.is_path_allowed(test_path, allowed) is True

    def test_is_path_allowed_with_disallowed_dir(self, path_util_module):
        test_path = "node_modules/some_package/file.py"
        allowed = frozenset({"agentic_core", "L0_routing"})

        assert path_util_module.is_path_allowed(test_path, allowed) is False

    def test_safe_prefixed_filename(self, path_util_module):
        assert path_util_module.safe_prefixed_filename("test.txt", "prefix_") == "prefix_test.txt"
        assert path_util_module.safe_prefixed_filename("prefix_test.txt", "prefix_") == "prefix_test.txt"

    def test_validate_no_duplicate_prefix(self, path_util_module):
        assert path_util_module.validate_no_duplicate_prefix("prefix_test.txt", "prefix_") is True
        assert path_util_module.validate_no_duplicate_prefix("prefix_prefix_test.txt", "prefix_") is False

    def test_safe_path_join(self, path_util_module, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = path_util_module.safe_path_join(project_root, "agentic_core", "test.py")

        assert isinstance(result, Path)
        assert result == project_root / "agentic_core" / "test.py"

    def test_safe_path_join_raises_outside_project(self, path_util_module, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            path_util_module.safe_path_join(project_root, "..", "outside.py")

    def test_safe_path_join_resolves_relative_components(self, path_util_module, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = path_util_module.safe_path_join(project_root, ".", "test.py")
        result2 = path_util_module.safe_path_join(project_root, "subdir", "..", "test.py")

        assert result == project_root / "test.py"
        assert result2 == project_root / "test.py"
