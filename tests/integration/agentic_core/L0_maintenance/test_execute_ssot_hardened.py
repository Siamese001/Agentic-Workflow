"""
File: tests/integration/agentic_core/L0_maintenance/test_execute_ssot_hardened.py
"""

from unittest.mock import MagicMock

from agentic_core.L0_maintenance.scripts.execute_ssot import (
    SovereignDecisionEngine,
    execute_phase2_reconciliation,
)


class MockHealer:
    def __init__(self, name, fail=False):
        self.name = name
        self.fail = fail

    def heal(self, violation):
        if self.fail:
            raise RuntimeError("Simulated crash")
        return {"success": True, "diff": "fixed"}


def test_phase2_atomic_rollback():
    """Verify engine releases lock even when agent crashes."""
    engine = SovereignDecisionEngine()
    state_mgr = MagicMock()

    agents = {"CrashAgent": MockHealer("CrashAgent", fail=True)}
    plan = {
        "violations_found": [{"type": "TEST", "suggested_agent": "CrashAgent", "file": "test.py"}]
    }

    # Engine mocks
    engine.calculate_healing_confidence = MagicMock(return_value=MagicMock(value=0.9))
    engine.should_proceed_with_healing = MagicMock(return_value=(True, "GO"))

    result = execute_phase2_reconciliation(
        agents=agents,
        territory="test",
        decision_engine=engine,
        state_mgr=state_mgr,
        plan=plan,
    )

    assert result["status"] == "partial_success"
    assert result["errors"] == 1

    # CRITICAL: Verify lock was released
    assert engine._atomic_lock is False
    assert engine._sovereignty_token is None


def test_phase2_sovereignty_denial():
    """Verify execution blocks if token denied (e.g. stack overflow simulation)."""
    engine = SovereignDecisionEngine()
    state_mgr = MagicMock()

    # Simulate locked state
    engine._atomic_lock = True

    agents = {"GoodAgent": MockHealer("GoodAgent")}
    plan = {
        "violations_found": [{"type": "TEST", "suggested_agent": "GoodAgent", "file": "test.py"}]
    }

    engine.calculate_healing_confidence = MagicMock(return_value=MagicMock(value=0.9))
    engine.should_proceed_with_healing = MagicMock(return_value=(True, "GO"))

    result = execute_phase2_reconciliation(
        agents=agents,
        territory="test",
        decision_engine=engine,
        state_mgr=state_mgr,
        plan=plan,
    )

    assert result["errors"] == 1
    assert result["status"] == "partial_success"
    assert result["error_message"] is None or len(result["error_message"]) > 0
