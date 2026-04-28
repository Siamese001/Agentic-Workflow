"""Tests for KillSwitch - emergency execution halt mechanism."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.kill_switch import KillSwitch


class TestKillSwitch:
    def test_init_inactive(self):
        ks = KillSwitch()
        assert ks.is_active() is False

    def test_activate(self):
        ks = KillSwitch()
        ks.activate(reason="emergency")
        assert ks.is_active() is True

    def test_activate_records_reason(self):
        ks = KillSwitch()
        ks.activate(reason="policy_violation")
        assert ks.get_reason() == "policy_violation"

    def test_deactivate(self):
        ks = KillSwitch()
        ks.activate(reason="test")
        ks.deactivate()
        assert ks.is_active() is False

    def test_check_blocks_when_active(self):
        ks = KillSwitch()
        ks.activate(reason="halt")
        with pytest.raises(RuntimeError):
            ks.check()

    def test_check_passes_when_inactive(self):
        ks = KillSwitch()
        ks.check()  # no raise

    def test_emit_event_on_activate(self):
        ks = KillSwitch()
        listener = Mock()
        ks.add_listener(listener)
        ks.activate(reason="test")
        listener.on_activate.assert_called_once()

    def test_get_status(self):
        ks = KillSwitch()
        status = ks.get_status()
        assert "active" in status
