"""3.9: Baseline tests for HealingCycle (3.3) in RgHealingOrchestrator."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_healing_cycle", "execution_auth")
_emit_validates_capability("p2", "test_healing_cycle", "capability_check")
_emit_routes_to_capability("p2", "test_healing_cycle", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_cycle", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_cycle", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_cycle", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_cycle", "exec_output")
_emit_dispatches_agent("p3", "test_healing_cycle", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_cycle", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_cycle", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_cycle", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_cycle", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_cycle", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_cycle", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_cycle", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_cycle", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_cycle", "eval_metric")
_emit_stores_embedding("p4", "test_healing_cycle", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_cycle", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_cycle", "exec_snapshot_link")


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
