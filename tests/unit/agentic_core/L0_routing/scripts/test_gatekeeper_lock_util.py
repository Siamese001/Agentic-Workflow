"""Test GatekeeperLockUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGatekeeperLockUtil:
    """Test GatekeeperLockUtil functionality."""

    def test_gatekeeper_lock_util_imports(self):
        """Test gatekeeper_lock_util module imports."""
        from agentic_core import gatekeeper_lock_util
        assert gatekeeper_lock_util is not None

    def test_gatekeeper_lock_util_class(self):
        """Test GatekeeperLockUtil class exists."""
        from agentic_core import GatekeeperLockUtil
        assert GatekeeperLockUtil is not None

    def test_gatekeeper_lock_util_callable(self):
        """Test gatekeeper_lock_util functions are callable."""
        from agentic_core import validate_gatekeeper_lock_util
        assert callable(validate_gatekeeper_lock_util)
