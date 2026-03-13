"""Tests for WriteGovernorMixin — UWG write path enforcement."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.write_governor_mixin import WriteGovernorMixin
from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
)


class _Agent(WriteGovernorMixin):
    pass


class TestWriteGovernorMixinAllowedPaths:
    def test_governed_write_allowed_path_returns_mutation_record(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_write("artifacts/output.json", b"{}")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True

    def test_governed_write_str_data_encoded(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_write("artifacts/output.txt", "hello")
        assert isinstance(result, MutationRecord)
        assert result.data_hash is not None

    def test_governed_append_allowed_path(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_append("logs/run.log", b"line\n")
        assert isinstance(result, MutationRecord)
        assert result.operation == "append"

    def test_governed_delete_allowed_path(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_delete("artifacts/old.json")
        assert isinstance(result, MutationRecord)
        assert result.operation == "delete"

    def test_governed_rename_allowed_paths(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_rename("artifacts/a.json", "artifacts/b.json")
        assert isinstance(result, MutationRecord)
        assert result.operation == "rename"


class TestWriteGovernorMixinBlockedPaths:
    def test_governed_write_blocked_extension_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_write("src/evil.py", b"pass")

    def test_governed_write_blocked_path_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_write("secret/config.json", b"{}")

    def test_governed_append_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_append("core/engine.py", b"extra")

    def test_governed_delete_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_delete("agentic_core/L0_routing/important.py")

    def test_assert_write_governed_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError):
            agent.assert_write_governed("src/bad.py")


class TestWriteGovernorMixinReplayMode:
    def test_governed_write_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_write("src/evil.py", b"pass")
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True

    def test_governed_append_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_append("src/evil.py", b"extra")
        assert isinstance(result, SimulationResult)

    def test_governed_delete_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_delete("src/evil.py")
        assert isinstance(result, SimulationResult)

    def test_governed_rename_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_rename("src/a.py", "src/b.py")
        assert isinstance(result, SimulationResult)


class TestWriteGovernorMixinGatewayInjection:
    def test_default_gateway_is_global_instance(self):
        from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway

        agent = _Agent()
        assert agent._get_uwg() is get_write_gateway()

    def test_set_write_gateway_overrides(self):
        agent = _Agent()
        custom = UniversalWriteGateway(replay_mode=True)
        agent.set_write_gateway(custom)
        assert agent._get_uwg() is custom

    def test_get_write_stats_proxies_to_gateway(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        stats = agent.get_write_stats()
        assert "total_mutations" in stats
        assert "replay_mode" in stats

    def test_assert_write_governed_allowed_path_returns_true(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        assert agent.assert_write_governed("artifacts/ok.json") is True

    def test_mutation_ledger_records_blocked_write(self):
        agent = _Agent()
        gw = UniversalWriteGateway(replay_mode=False)
        agent.set_write_gateway(gw)
        with pytest.raises(ToolNotAllowedError):
            agent.governed_write("src/bad.py", b"pass")
        ledger = gw.get_mutation_ledger()
        assert any(r.permitted is False for r in ledger)
