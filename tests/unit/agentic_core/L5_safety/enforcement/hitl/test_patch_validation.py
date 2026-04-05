"""Test PatchValidation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPatchValidation:
    """Test PatchValidation functionality."""

    def test_patch_validation_imports(self):
        """Test patch_validation module imports."""
        from agentic_core import patch_validation
        assert patch_validation is not None

    def test_patch_validation_class(self):
        """Test PatchValidation class exists."""
        from agentic_core import PatchValidation
        assert PatchValidation is not None

    def test_patch_validation_callable(self):
        """Test patch_validation functions are callable."""
        from agentic_core import validate_patch_validation
        assert callable(validate_patch_validation)
