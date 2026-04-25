"""Tests for the UWG rollback executor."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    NoopRollbackHandler,
    RollbackOutcome,
    RollbackPlan,
    RollbackStep,
    SequentialRollbackExecutor,
)
from agentic_core.L3_orchestration.exit_eval.v6.rollback import (
    FailingRollbackHandler,
    RollbackHandler,
)


# ---- RollbackPlan parsing ----


def test_plan_from_empty_dict() -> None:
    plan = RollbackPlan.from_dict(None)
    assert plan.steps == []


def test_plan_from_list_shape() -> None:
    plan = RollbackPlan.from_dict([{"kind": "undo_write", "target": "row-1"}])
    assert len(plan.steps) == 1
    assert plan.steps[0].kind == "undo_write"


def test_plan_from_steps_dict_shape() -> None:
    plan = RollbackPlan.from_dict({"steps": [{"kind": "a"}, {"kind": "b"}]})
    assert [s.kind for s in plan.steps] == ["a", "b"]


def test_plan_from_string_steps_normalizes() -> None:
    plan = RollbackPlan.from_dict({"steps": ["restore", "invalidate_cache"]})
    assert [s.kind for s in plan.steps] == ["restore", "invalidate_cache"]


def test_plan_abort_flag_default_true() -> None:
    plan = RollbackPlan.from_dict({"steps": ["x"]})
    assert plan.abort_on_first_failure is True


def test_plan_abort_flag_explicit_false() -> None:
    plan = RollbackPlan.from_dict({"steps": ["x"], "abort_on_first_failure": False})
    assert plan.abort_on_first_failure is False


# ---- SequentialRollbackExecutor ----


def test_executor_skipped_when_no_steps() -> None:
    executor = SequentialRollbackExecutor()
    result = executor.execute(RollbackPlan())
    assert result.outcome is RollbackOutcome.SKIPPED_NO_PLAN


def test_executor_runs_steps_in_order() -> None:
    handler = NoopRollbackHandler()
    executor = SequentialRollbackExecutor({"undo": handler, "invalidate": handler})
    plan = RollbackPlan(
        steps=[
            RollbackStep(kind="undo", target="t1"),
            RollbackStep(kind="invalidate", target="cache"),
        ]
    )
    result = executor.execute(plan)
    assert result.outcome is RollbackOutcome.EXECUTED
    assert result.executed == ["undo", "invalidate"]
    assert [s.kind for s in handler.calls] == ["undo", "invalidate"]


def test_executor_aborts_on_first_failure() -> None:
    noop = NoopRollbackHandler()
    failing = FailingRollbackHandler("boom")
    executor = SequentialRollbackExecutor({"ok": noop, "bad": failing})
    plan = RollbackPlan(
        steps=[
            RollbackStep(kind="ok"),
            RollbackStep(kind="bad"),
            RollbackStep(kind="ok"),
        ]
    )
    result = executor.execute(plan)
    assert result.outcome is RollbackOutcome.FAILED
    assert result.executed == ["ok"]
    assert result.failed_step == "bad"
    assert "boom" in result.error


def test_executor_continues_on_failure_when_abort_disabled() -> None:
    noop = NoopRollbackHandler()
    failing = FailingRollbackHandler("ignored")
    executor = SequentialRollbackExecutor({"ok": noop, "bad": failing})
    plan = RollbackPlan(
        steps=[RollbackStep(kind="bad"), RollbackStep(kind="ok")],
        abort_on_first_failure=False,
    )
    result = executor.execute(plan)
    # Reaches end with ok executed, but outcome is EXECUTED (no abort).
    assert result.outcome is RollbackOutcome.EXECUTED
    assert "ok" in result.executed


def test_executor_unknown_kind_raises_via_handler_resolve() -> None:
    executor = SequentialRollbackExecutor()  # no handlers, no default
    plan = RollbackPlan(steps=[RollbackStep(kind="missing")])
    result = executor.execute(plan)
    assert result.outcome is RollbackOutcome.FAILED
    assert "missing" in result.failed_step


def test_executor_default_handler_used_when_kind_unknown() -> None:
    fallback = NoopRollbackHandler()
    executor = SequentialRollbackExecutor(default_handler=fallback)
    plan = RollbackPlan(steps=[RollbackStep(kind="anything")])
    result = executor.execute(plan)
    assert result.outcome is RollbackOutcome.EXECUTED
    assert len(fallback.calls) == 1


def test_executor_register_after_construction() -> None:
    executor = SequentialRollbackExecutor()
    handler = NoopRollbackHandler()
    executor.register("undo", handler)
    plan = RollbackPlan(steps=[RollbackStep(kind="undo")])
    result = executor.execute(plan)
    assert result.outcome is RollbackOutcome.EXECUTED


# ---- integration: U5 failure triggers rollback ----


def test_u5_failure_triggers_rollback_executor(tmp_path) -> None:
    """End-to-end: a U5 refresh failure with a rollback_plan invokes the executor."""
    from agentic_core.L3_orchestration.exit_eval.v6 import (
        UwgOutcome,
        aggregate_decision,
        build_x3c_commit_request,
        default_backends,
        process_commit_request,
        run_all_x1_gates,
    )
    from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition

    from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_packet

    # Build a commit packet whose state_diff carries a rollback_plan.
    review = base_packet(
        terminal_class="with_state_diff",
        write_intent_class="user_data_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
            "before_snapshot": {"v": 1},
            "after_proposed_snapshot": {"v": 2},
            "rollback_plan": {"steps": [{"kind": "undo_write", "target": "row-1"}]},
        },
        capability_token={"authorizes_write": True},
        grader_composition={
            "roster": ["x"],
            "threshold_profile": "p",
            "consistency": {"pass_power_estimate": 0.98, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    verdicts = run_all_x1_gates(review)
    decision = aggregate_decision(verdicts, review)
    assert decision.disposition is V6Disposition.COMMIT_REQUEST
    commit_packet = build_x3c_commit_request(review, decision)
    # Override rollback_plan since the X3C builder reads it from state_diff.
    commit_packet.rollback_plan = {"steps": [{"kind": "undo_write", "target": "row-1"}]}

    # Wire a refresher that always fails, plus a rollback executor.
    backends = default_backends()
    rollback_handler = NoopRollbackHandler()
    backends.rollback_executor = SequentialRollbackExecutor({"undo_write": rollback_handler})

    class FailingRefresher:
        def refresh(self, *, commit_request_id, l4_alias):
            del commit_request_id, l4_alias
            raise RuntimeError("read-surface refresh failed")

    backends.refresher = FailingRefresher()

    receipt = process_commit_request(commit_packet, backends)
    assert receipt.outcome is UwgOutcome.COMMIT_REJECTED
    assert receipt.rollback["outcome"] == RollbackOutcome.EXECUTED.value
    assert receipt.rollback["executed"] == ["undo_write"]
    assert len(rollback_handler.calls) == 1
