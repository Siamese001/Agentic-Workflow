"""Test AdgRuntimeAcceleration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgRuntimeAcceleration:
    """Test AdgRuntimeAcceleration functionality."""

    def test_runtime_acceleration_imports(self):
        """Test runtime acceleration module imports."""
        from tools.adg import runtime_acceleration
        assert runtime_acceleration is not None

    def test_runtime_accelerator_class(self):
        """Test runtime accelerator class exists."""
        from tools.adg.runtime_acceleration import RuntimeAccelerator
        assert RuntimeAccelerator is not None

    def test_accelerate_runtime(self):
        """Test accelerate runtime function."""
        from tools.adg.runtime_acceleration import accelerate_runtime
        assert callable(accelerate_runtime)
