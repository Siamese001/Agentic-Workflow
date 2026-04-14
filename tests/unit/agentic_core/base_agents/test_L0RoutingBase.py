"""Tests for phase-hardened L0RoutingBase behaviors."""

import pytest

from agentic_core.base_agents.L0RoutingBase import L0RoutingBase


@pytest.mark.unit
class TestL0RoutingBaseHardening:
    """Behavioral coverage for phase-hardened L0RoutingBase."""

    def test_self_tests_pass_after_normal_init(self):
        """Happy: _run_self_tests reports passed=1 when _initialized is True after init."""
        agent = L0RoutingBase()
        result = agent._run_self_tests()
        assert result["passed"] == 1
        assert result["failed"] == 0
        assert result["tests"][0]["status"] == "passed"

    def test_heal_fails_when_no_file_key(self):
        """Failure: heal() returns status=failed when violation has no file or file_path."""
        agent = L0RoutingBase()
        result = agent.heal({"type": "import_error", "message": "broken"})
        assert result["status"] == "failed"
        assert "missing file path" in result["errors"]

    def test_heal_fails_when_file_path_is_empty_string(self):
        """Edge: heal() treats empty-string file_path as missing (falsy guard)."""
        agent = L0RoutingBase()
        result = agent.heal({"file": "", "file_path": "", "type": "x"})
        assert result["status"] == "failed"
        assert "missing file path" in result["errors"]
