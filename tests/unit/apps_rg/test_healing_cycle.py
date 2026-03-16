"""3.9: Baseline tests for HealingCycle (3.3) in RgHealingOrchestrator."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_cycle")
_emit_applies_guardrail("p0", "test_healing_cycle", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_cycle", "policy_binding")
_emit_snapshots_state("p0", "test_healing_cycle", "state_snapshot")
emit_replay_key("p0", "test_healing_cycle")
emit_determinism_digest("p0", "test_healing_cycle")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHealingCycle:
    def test_execute_no_signals_converges(self):
        from apps_rg.reasoning.healing_cycle import HealingCycle

        ctx = MagicMock()
        ctx.signals = set()
        ctx.trace_id = "trace-test-001"

        cycle = HealingCycle(ctx, cycle_num=1)
        result = asyncio.run(cycle.execute("default"))

        assert result["converged"] is True
        assert result["status"] == "success"
        assert result["cycle_num"] == 1

    def test_execute_with_signals_processes_them(self):
        from apps_rg.reasoning.healing_cycle import HealingCycle

        ctx = MagicMock()
        signals_mock = MagicMock()
        signals_mock.__iter__ = MagicMock(return_value=iter(["signal_a", "signal_b"]))
        signals_mock.discard = MagicMock()
        ctx.signals = signals_mock
        ctx.trace_id = "trace-test-002"

        cycle = HealingCycle(ctx, cycle_num=2)
        result = asyncio.run(cycle.execute("default"))

        assert isinstance(result, dict)
        assert "converged" in result
        assert result["cycle_num"] == 2

    def test_execute_returns_required_keys(self):
        from apps_rg.reasoning.healing_cycle import HealingCycle

        ctx = MagicMock()
        ctx.signals = set()
        ctx.trace_id = "trace-003"

        cycle = HealingCycle(ctx, cycle_num=1)
        result = asyncio.run(cycle.execute("aggressive"))

        required_keys = {
            "status",
            "strategy",
            "cycle_num",
            "passed_agents",
            "failed_agents",
            "converged",
            "rollback_triggered",
        }
        assert required_keys.issubset(result.keys())
