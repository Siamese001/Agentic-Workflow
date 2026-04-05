"""Test gatekeeper_lock_util functionality."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.gatekeeper_lock_util"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test."""
    return importlib.import_module(MODULE_PATH)


@pytest.mark.unit
class TestGatekeeperLockUtil:
    """Test gatekeeper_lock_util functionality."""

    def test_gatekeeper_lock_util_imports(self, mod):
        """Test gatekeeper_lock_util module imports."""
        assert mod.__name__ == MODULE_PATH

    def test_gatekeeper_lock_util_public_api(self, mod):
        """Test gatekeeper_lock_util exposes the expected callable API."""
        assert callable(mod.get_staged_files)
        assert callable(mod.get_commit_message)
        assert callable(mod.check_env_bypass)
        assert callable(mod.check_commit_message_override)
        assert callable(mod.main)
