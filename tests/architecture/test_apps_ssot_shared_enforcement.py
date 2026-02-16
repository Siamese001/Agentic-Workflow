"""
Tests proving apps_* SSOT enforcement uses the SAME core logic as agentic_core.

Phase 1 Wave 2: Validates that apps_* paths are evaluated by the same
validation functions and produce the same violations as agentic_core would.
"""

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)

pytestmark = pytest.mark.governance


@pytest.fixture
def fca():
    """Create a FileClassificationAgent instance."""
    return FileClassificationAgent()


class TestSharedEnforcementLogic:
    """Prove that apps_* and agentic_core use the SAME validation functions."""

    @pytest.mark.parametrize(
        "path_template,expected_violation",
        [
            # agentic_core config/ violations
            ("agentic_core/L5_safety/config/bad_file.py", True),
            # apps_shared config/ violations (SAME LOGIC)
            ("apps_shared/config/bad_file.py", True),
            # apps_lic config/ violations (SAME LOGIC)
            ("apps_lic/config/bad_file.py", True),
            # apps_rg config/ violations (SAME LOGIC)
            ("apps_rg/config/bad_file.py", True),
            # Valid config files (no violation)
            ("agentic_core/L5_safety/config/good_config.py", False),
            ("apps_shared/config/good_config.py", False),
        ],
    )
    def test_config_suffix_enforcement_shared(
        self, fca: FileClassificationAgent, path_template: str, expected_violation: bool, tmp_path: Path
    ):
        """Config suffix enforcement applies identically to agentic_core and apps_*."""
        test_file = tmp_path / path_template
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# test file\n")

        result = fca.validate_folder_suffix_consistency(test_file)

        if expected_violation:
            assert result is not None, f"Expected violation for {path_template}"
            assert "config" in result.get("folder", ""), (
                f"Expected config folder violation for {path_template}"
            )
        else:
            assert result is None, f"Expected no violation for {path_template}"

    @pytest.mark.parametrize(
        "path_template,expected_violation",
        [
            # agentic_core utils/ violations
            ("agentic_core/L5_safety/utils/bad_file.py", True),
            # apps_shared utils/ violations (SAME LOGIC)
            ("apps_shared/utils/bad_file.py", True),
            # apps_lic utils/ violations (SAME LOGIC)
            ("apps_lic/utils/bad_file.py", True),
            # apps_rg utils/ violations (SAME LOGIC)
            ("apps_rg/utils/bad_file.py", True),
            # Valid util files (no violation)
            ("agentic_core/L5_safety/utils/good_util.py", False),
            ("apps_shared/utils/good_util.py", False),
        ],
    )
    def test_utils_suffix_enforcement_shared(
        self, fca: FileClassificationAgent, path_template: str, expected_violation: bool, tmp_path: Path
    ):
        """Utils suffix enforcement applies identically to agentic_core and apps_*."""
        test_file = tmp_path / path_template
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# test file\n")

        result = fca.validate_folder_suffix_consistency(test_file)

        if expected_violation:
            assert result is not None, f"Expected violation for {path_template}"
            assert "utils" in result.get("folder", ""), f"Expected utils folder violation for {path_template}"
        else:
            assert result is None, f"Expected no violation for {path_template}"


class TestNegativeCases:
    """Negative test cases for apps_* enforcement."""

    def test_pascalcase_in_apps_config_rejected(self, fca: FileClassificationAgent, tmp_path: Path):
        """PascalCase file under apps_*/config/ is rejected."""
        test_file = tmp_path / "apps_shared/config/BadConfig.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# PascalCase config file\n")

        result = fca.validate_folder_suffix_consistency(test_file)
        assert result is not None, "PascalCase file in config/ should be rejected"

    def test_snake_case_missing_config_suffix_rejected(self, fca: FileClassificationAgent, tmp_path: Path):
        """snake_case but missing _config.py under apps_*/config/ is rejected."""
        test_file = tmp_path / "apps_rg/config/some_loader.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Missing _config suffix\n")

        result = fca.validate_folder_suffix_consistency(test_file)
        assert result is not None, "File missing _config.py suffix should be rejected"
        assert "_config.py" in str(result.get("expected_suffixes", []))

    def test_util_file_in_config_rejected(self, fca: FileClassificationAgent, tmp_path: Path):
        """*_util.py under apps_*/config/ is rejected (should be in utils/)."""
        test_file = tmp_path / "apps_lic/config/helper_util.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Utility in wrong folder\n")

        result = fca.validate_folder_suffix_consistency(test_file)
        # _util.py is not in config's allowed suffixes, so it should be rejected
        assert result is not None, "*_util.py in config/ should be rejected"

    def test_non_util_in_utils_rejected(self, fca: FileClassificationAgent, tmp_path: Path):
        """non-_util.py under apps_*/utils/ is rejected."""
        # Create the file structure so parent.name == "utils"
        utils_dir = tmp_path / "apps_shared" / "utils"
        utils_dir.mkdir(parents=True, exist_ok=True)
        # Use a filename that doesn't match any allowed suffix (_util.py, _mixin.py, _helper.py)
        test_file = utils_dir / "bad_file.py"
        test_file.write_text("# Missing _util suffix\n")

        # Verify the parent folder is correctly named
        assert test_file.parent.name == "utils", f"Parent should be 'utils', got '{test_file.parent.name}'"

        result = fca.validate_folder_suffix_consistency(test_file)
        assert result is not None, "File missing _util.py suffix in utils/ should be rejected"

    def test_init_files_exempt(self, fca: FileClassificationAgent, tmp_path: Path):
        """__init__.py files are exempt from suffix enforcement."""
        test_file = tmp_path / "apps_shared/config/__init__.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Init file\n")

        result = fca.validate_folder_suffix_consistency(test_file)
        assert result is None, "__init__.py should be exempt"


class TestEnforcementFunctionIdentity:
    """Prove that the SAME function is called for both agentic_core and apps_*."""

    def test_same_function_for_agentic_core_and_apps(self, fca: FileClassificationAgent, tmp_path: Path):
        """The same validate_folder_suffix_consistency function handles both paths."""
        # Create test files in both locations
        agentic_file = tmp_path / "agentic_core/L5_safety/config/test_file.py"
        apps_file = tmp_path / "apps_shared/config/test_file.py"

        for f in [agentic_file, apps_file]:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("# test\n")

        # Call the SAME function for both
        agentic_result = fca.validate_folder_suffix_consistency(agentic_file)
        apps_result = fca.validate_folder_suffix_consistency(apps_file)

        # Both should produce violations (missing _config suffix)
        assert agentic_result is not None
        assert apps_result is not None

        # Both should have the same structure
        assert agentic_result.keys() == apps_result.keys()
        assert agentic_result["folder"] == apps_result["folder"] == "config"
        assert agentic_result["expected_suffixes"] == apps_result["expected_suffixes"]
