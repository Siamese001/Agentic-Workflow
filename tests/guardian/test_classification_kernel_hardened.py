"""Test ClassificationKernelHardened functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestClassificationKernelHardened:
    """Test ClassificationKernelHardened functionality."""

    def test_classification_kernel_hardened_imports(self):
        """Test classification_kernel_hardened module imports."""
        from agentic_core import classification_kernel_hardened
        assert classification_kernel_hardened is not None

    def test_classification_kernel_hardened_class(self):
        """Test ClassificationKernelHardened class exists."""
        from agentic_core import ClassificationKernelHardened
        assert ClassificationKernelHardened is not None

    def test_classification_kernel_hardened_callable(self):
        """Test classification_kernel_hardened functions are callable."""
        from agentic_core import validate_classification_kernel_hardened
        assert callable(validate_classification_kernel_hardened)
