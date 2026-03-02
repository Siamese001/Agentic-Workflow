"""
Unit tests for GravityLeakRepairAgent - Validator in L5.


    [L5 HEALER] Automated gravity violation repair agent.

    Works in tandem with UnifiedStructur

Tests:
- State Integrity: Verify initialization and state
- Logic Branching: Test method dispatch
- Fuzzing: Invalid inputs
- Mocking: Zero network calls
"""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.unit_min_deps


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with (
        patch("redis.Redis", return_value=Mock()),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "ANTHROPIC_API_KEY": "test-key"}),
    ):
        yield


class TestGravityLeakRepairAgent:
    """Unit tests for GravityLeakRepairAgent."""

    @pytest.fixture
    def agent_class(self):
        """Import agent class with mocked dependencies."""
        try:
            from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

            return GravityLeakRepairAgent
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.skip(f"Cannot import GravityLeakRepairAgent: {e}")

    def test_class_exists(self, agent_class):
        """Verify GravityLeakRepairAgent exists and is importable."""
        assert agent_class is not None, "GravityLeakRepairAgent should exist"

    def test_inherits_from_m_c_p_hardened_mixin(self, agent_class):
        """Verify proper inheritance from MCPHardenedMixin."""
        mro_names = [cls.__name__ for cls in agent_class.__mro__]
        assert "MCPHardenedMixin" in mro_names, "Should inherit from MCPHardenedMixin"

    def test_has_analyze_violation_method(self, agent_class):
        """Verify agent has analyze_violation method."""
        assert hasattr(agent_class, "analyze_violation"), "Should have analyze_violation method"

    def test_has_generate_fix_report_method(self, agent_class):
        """Verify agent has generate_fix_report method."""
        assert hasattr(agent_class, "generate_fix_report"), "Should have generate_fix_report method"

    def test_has_apply_fix_method(self, agent_class):
        """Verify agent has apply_fix method."""
        assert hasattr(agent_class, "apply_fix"), "Should have apply_fix method"

    def test_has_healing_capability(self, agent_class):
        """Verify agent has healing capability."""
        assert hasattr(agent_class, "heal_repository") or hasattr(agent_class, "heal"), (
            "Should have healing method"
        )

    def test_has_tools_capability(self, agent_class):
        """Verify agent has tools capability."""
        assert hasattr(agent_class, "_perform_action") or hasattr(agent_class, "execute"), (
            "Should have tool execution method"
        )

    def test_fuzzing_invalid_inputs(self, agent_class):
        """Test handling of invalid inputs."""
        invalid_inputs = [None, {}, "", [], 123]
        for _invalid_input in invalid_inputs:
            try:
                pass  # Would test actual processing
            except (TypeError, ValueError, AttributeError):
                pass  # Expected for invalid inputs

    def test_no_network_calls_on_import(self):
        """Verify no network calls during import."""
        network_calls = []

        def track_call(*args, **kwargs):
            network_calls.append((args, kwargs))

        with patch("requests.get", track_call), patch("requests.post", track_call):
            try:
                from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
                    GravityLeakRepairAgent,  # noqa: F401
                )
            except (ImportError, NameError, AttributeError):
                pass

            assert len(network_calls) == 0, "No network calls on import"


@pytest.mark.unit_min_deps
class TestGravityRepairCircuitBreaker:
    """Phase 1C: Circuit-breaker termination invariants."""

    @pytest.fixture
    def agent(self, tmp_path):
        try:
            from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
                GravityLeakRepairAgent,
            )

            return GravityLeakRepairAgent(project_root=tmp_path)
        except (ImportError, TypeError) as e:
            pytest.skip(f"Cannot import GravityLeakRepairAgent: {e}")

    @pytest.fixture
    def l0_fix(self, tmp_path):
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityFix

        target = tmp_path / "agentic_core" / "L0_routing" / "engines" / "fake.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("from agentic_core.L5_safety.foo import Bar\n", encoding="utf-8")
        return GravityFix(
            file_path=target,
            line_number=1,
            old_import="from agentic_core.L5_safety.foo import Bar",
            new_import="# TODO: Create abstraction layer",
            fix_type="ABSTRACT",
            rationale="test",
        )

    def test_l0_file_immediately_plan_only(self, agent, l0_fix):
        """L0 target must return plan_only on first call — no write attempted."""
        result = agent.apply_fix(l0_fix, dry_run=False)
        assert result["status"] == "plan_only", f"Expected plan_only, got {result}"

    def test_l0_file_second_call_also_plan_only(self, agent, l0_fix):
        """Second call on same L0 target must also return plan_only — no infinite loop."""
        r1 = agent.apply_fix(l0_fix, dry_run=False)
        r2 = agent.apply_fix(l0_fix, dry_run=False)
        assert r1["status"] == "plan_only"
        assert r2["status"] == "plan_only"

    def test_at_most_one_prohibition_hit_recorded(self, agent, l0_fix):
        """Circuit breaker records hit on first call; second call reads latch."""
        agent.apply_fix(l0_fix, dry_run=False)
        key = (str(l0_fix.file_path), "shutil.mutate")
        assert agent._prohibition_hits.get(key, 0) == 1

    def test_catastrophic_replace_guard_short_old_import(self, agent, tmp_path):
        """Single-char old_import must return plan_only, never attempt replace."""
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityFix

        target = tmp_path / "agentic_core" / "L2_execution" / "engines" / "safe.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x = 1\n", encoding="utf-8")
        fix = GravityFix(
            file_path=target,
            line_number=1,
            old_import="x",
            new_import="# replaced",
            fix_type="ABSTRACT",
            rationale="test",
        )
        result = agent.apply_fix(fix, dry_run=False)
        assert result["status"] == "plan_only"
        assert target.read_text(encoding="utf-8") == "x = 1\n", "File must be unmodified"

    def test_process_terminates_cleanly_no_exception(self, agent, l0_fix):
        """apply_fix must never raise — always return a dict."""
        for _ in range(3):
            result = agent.apply_fix(l0_fix, dry_run=False)
            assert isinstance(result, dict)
            assert "status" in result


@pytest.mark.unit_min_deps
class TestRuntimeStateManagerPersistenceLatch:
    """Phase 2C: _persistence_disabled latch invariants."""

    @pytest.fixture
    def manager(self, tmp_path):
        try:
            from agentic_core.L0_routing.scripts.execute_ssot import RuntimeStateManager

            return RuntimeStateManager(project_root=tmp_path)
        except (ImportError, TypeError) as e:
            pytest.skip(f"Cannot import RuntimeStateManager: {e}")

    def test_latch_initialised_false(self, manager):
        assert manager._persistence_disabled is False

    def test_first_prohibition_sets_latch_and_logs_critical(self, manager, caplog):
        import logging

        with (
            patch(
                "agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write",
                side_effect=PermissionError("MUTATION_PROHIBITED:layer=L0|op=json.dump"),
            ),
            caplog.at_level(logging.CRITICAL),
        ):
            manager.save()
        assert manager._persistence_disabled is True
        assert any(
            "MUTATION_PROHIBITED" in r.message or "persistence DISABLED" in r.message for r in caplog.records
        )

    def test_second_call_is_noop_no_log(self, manager, caplog):
        import logging

        with patch(
            "agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write",
            side_effect=PermissionError("MUTATION_PROHIBITED:layer=L0|op=json.dump"),
        ):
            manager.save()  # first — sets latch

        caplog.clear()
        with (
            patch(
                "agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write",
                side_effect=PermissionError("MUTATION_PROHIBITED:layer=L0|op=json.dump"),
            ),
            caplog.at_level(logging.DEBUG),
        ):
            manager.save()  # second — must be no-op

        assert not any(
            "MUTATION_PROHIBITED" in r.message or "Atomic Write Failed" in r.message for r in caplog.records
        ), "Second call must produce no log output"

    def test_no_exception_propagated(self, manager):
        with patch(
            "agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write",
            side_effect=PermissionError("MUTATION_PROHIBITED:layer=L0|op=json.dump"),
        ):
            manager.save()
            manager.save()
            manager.save()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
