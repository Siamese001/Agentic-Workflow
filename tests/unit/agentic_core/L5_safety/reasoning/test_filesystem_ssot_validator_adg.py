"""Test FilesystemSsotValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFilesystemSsotValidatorAdg:
    """Test FilesystemSsotValidatorAdg functionality."""

    def test_filesystem_ssot_validator_adg_imports(self):
        """Test filesystem_ssot_validator_adg module imports."""
        from agentic_core import filesystem_ssot_validator_adg

        assert filesystem_ssot_validator_adg is not None

    def test_filesystem_ssot_validator_adg_class(self):
        """Test FilesystemSsotValidatorAdg class exists."""
        from agentic_core import FilesystemSsotValidatorAdg

        assert FilesystemSsotValidatorAdg is not None

    def test_filesystem_ssot_validator_adg_callable(self):
        """Test filesystem_ssot_validator_adg functions are callable."""
        from agentic_core import validate_filesystem_ssot_validator_adg

        assert callable(validate_filesystem_ssot_validator_adg)
