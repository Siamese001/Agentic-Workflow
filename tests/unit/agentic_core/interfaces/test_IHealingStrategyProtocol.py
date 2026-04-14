"""Behavioral tests for IHealingStrategyProtocol.py (phase: async centralization, ImportError handling)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestChaosResilienceCanHeal:
    # --- happy path ---

    def test_can_heal_all_supported_violation_types(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        supported = [
            "resilience_check",
            "post_healing_validation",
            "chaos_test_required",
            "system_stability_check",
        ]
        with patch("agentic_core.interfaces.IHealingStrategyProtocol._emit_records_execution_trace"):
            for vtype in supported:
                assert strategy.can_heal({"type": vtype}) is True, f"Expected True for {vtype}"

    # --- failure path ---

    def test_can_heal_unsupported_violation_returns_false(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        with patch("agentic_core.interfaces.IHealingStrategyProtocol._emit_records_execution_trace"):
            assert strategy.can_heal({"type": "unknown_violation"}) is False
            assert strategy.can_heal({"type": "memory_leak"}) is False

    # --- edge case ---

    def test_can_heal_missing_type_key_returns_false(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        with patch("agentic_core.interfaces.IHealingStrategyProtocol._emit_records_execution_trace"):
            assert strategy.can_heal({}) is False


@pytest.mark.unit
class TestChaosResilienceHeal:
    # --- happy path ---

    def test_heal_with_zero_failures_returns_success(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        strategy._initialized = True
        strategy._agent = MagicMock()
        run_result = {
            "failures_detected": 0,
            "tests_executed": 5,
            "recovery_metrics": {"mean_ttf": 0.1},
            "scenarios_tested": ["s1", "s2"],
        }
        with patch("agentic_core.interfaces.IHealingStrategyProtocol._run_agent", return_value=run_result):
            result = strategy.heal({"type": "resilience_check"}, {})
        assert result["success"] is True
        assert result["resilience_score"] == 1.0

    # --- failure path ---

    def test_heal_agent_unavailable_returns_stub(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        strategy._initialized = True
        strategy._agent = None  # simulates import failure
        result = strategy.heal({"type": "resilience_check"}, {})
        assert result["success"] is True
        assert result["status"] == "agent_unavailable"
        assert result["scenarios_tested"] == 0

    def test_heal_agent_run_exception_returns_failure(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        strategy._initialized = True
        strategy._agent = MagicMock()
        with patch(
            "agentic_core.interfaces.IHealingStrategyProtocol._run_agent",
            side_effect=RuntimeError("chaos agent crashed"),
        ):
            result = strategy.heal({"type": "resilience_check"}, {})
        assert result["success"] is False
        assert "chaos agent crashed" in result["error"]

    # --- edge case ---

    def test_heal_nonzero_failures_lowers_resilience_score(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        strategy._initialized = True
        strategy._agent = MagicMock()
        run_result = {
            "failures_detected": 2,
            "tests_executed": 4,
            "recovery_metrics": {},
            "scenarios_tested": [],
        }
        with patch("agentic_core.interfaces.IHealingStrategyProtocol._run_agent", return_value=run_result):
            result = strategy.heal({"type": "resilience_check"}, {})
        assert result["success"] is False
        assert result["resilience_score"] < 1.0


@pytest.mark.unit
class TestRegisterChaosHealing:
    # --- failure path ---

    def test_orchestrator_import_error_returns_failure(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import register_chaos_healing

        key = "agentic_core.L5_safety.types.healing_orchestration_types"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None  # blocks import
            result = register_chaos_healing()
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result["success"] is False
        assert result["registered"] == []
        assert len(result["errors"]) > 0

    # --- edge case ---

    def test_orchestrator_import_error_errors_contains_message(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import register_chaos_healing

        key = "agentic_core.L5_safety.types.healing_orchestration_types"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None
            result = register_chaos_healing()
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert any("HealingSovereignOrchestrator" in e or "import" in e.lower() for e in result["errors"])


@pytest.mark.unit
class TestGetIntegrationStatusHealing:
    # --- happy path ---

    def test_includes_supported_violations(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        assert "supported_violations" in status
        assert "resilience_check" in status["supported_violations"]

    # --- failure path (wrong key name would break callers) ---

    def test_includes_strategies_available(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        assert "strategies_available" in status
        assert "chaos_resilience" in status["strategies_available"]

    # --- edge case ---

    def test_chaos_strategy_initialized_key_present(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        assert "chaos_strategy_initialized" in status
