"""W5 tests for v7 6D engines: rollout_receipt_generator + bus_u_publisher."""

from __future__ import annotations

import pytest

from system_learning.engines.bus_u_publisher import (
    ActivationPolicy,
    AliasActivator,
    BusUPublisher,
)
from system_learning.engines.rollout_receipt_generator import (
    RollbackHandle,
    RollbackHandleValidator,
    RolloutReceiptGenerator,
)
from system_learning.engines.v7_kpi_board import UnifiedKPIBoard, V7KPIName


def _make_handle(reachable=True, **overrides):
    base = dict(
        handle_id="h1",
        target_surface="L4:prompt_v2",
        previous_version_pointer="prompt_v2@1.0.0",
        new_version_pointer="prompt_v2@1.0.1",
        revert_diff="-new\n+old",
        verified_reachable=reachable,
        verification_notes="ok",
    )
    base.update(overrides)
    return RollbackHandle(**base)


# ---- rollback_handle_validator -------------------------------------------


def test_validator_accepts_valid_handle():
    v = RollbackHandleValidator()
    ok, _ = v.validate(_make_handle())
    assert ok is True


def test_validator_rejects_empty_handle_id():
    v = RollbackHandleValidator()
    ok, note = v.validate(_make_handle(handle_id=""))
    assert ok is False and "handle_id" in note


def test_validator_rejects_empty_revert_diff():
    v = RollbackHandleValidator()
    ok, note = v.validate(_make_handle(revert_diff=""))
    assert ok is False and "revert_diff" in note


def test_validator_rejects_identical_pointers():
    v = RollbackHandleValidator()
    ok, note = v.validate(_make_handle(
        previous_version_pointer="x",
        new_version_pointer="x",
    ))
    assert ok is False and "identical" in note


# ---- rollout_receipt_generator -------------------------------------------


def _gen_args(**overrides):
    base = dict(
        proposal_id="p1", target_surface="L4:prompt",
        content_hash="ch1", policy_hash="ph1",
        signer_identity="alice@org",
        previous_version_pointer="prompt@1",
        new_version_pointer="prompt@2",
        revert_diff="-x\n+y",
    )
    base.update(overrides)
    return base


def test_generator_produces_receipt_with_reachable_handle():
    g = RolloutReceiptGenerator()
    r = g.generate(**_gen_args())
    assert r.rollback_handle.verified_reachable is True


def test_generator_marks_handle_unreachable_on_empty_revert_diff():
    g = RolloutReceiptGenerator()
    r = g.generate(**_gen_args(revert_diff=""))
    assert r.rollback_handle.verified_reachable is False


def test_generator_publishes_rollback_reachability_kpi():
    g = RolloutReceiptGenerator()
    board = UnifiedKPIBoard()
    g.generate(**_gen_args())
    g.generate(**_gen_args(previous_version_pointer="x", new_version_pointer="x"))
    g.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.ROLLBACK_REACHABILITY)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(0.5)


def test_receipt_id_stable_across_generations():
    g = RolloutReceiptGenerator()
    a = g.generate(**_gen_args())
    b = g.generate(**_gen_args())
    assert a.receipt_id == b.receipt_id


# ---- alias_activator -----------------------------------------------------


def test_alias_activator_plans_swap_at_next_run_start():
    plan = AliasActivator.plan_swap(
        target_surface="L4:rubric",
        previous_version_pointer="rubric@1",
        new_version_pointer="rubric@2",
    )
    assert plan["swap_at"] == "next_run_start"
    assert plan["from"] == "rubric@1"
    assert plan["to"] == "rubric@2"


# ---- bus_u_publisher -----------------------------------------------------


def test_bus_u_publish_succeeds_for_reachable_handle():
    g = RolloutReceiptGenerator()
    receipt = g.generate(**_gen_args())
    pub = BusUPublisher()
    out = pub.publish(receipt=receipt)
    assert out.activate_at == "next_run_start"
    assert out.activation_policy is ActivationPolicy.NEXT_RUN_START


def test_bus_u_rejects_unreachable_rollback():
    g = RolloutReceiptGenerator()
    bad = g.generate(**_gen_args(revert_diff=""))
    pub = BusUPublisher()
    with pytest.raises(ValueError, match="rollback"):
        pub.publish(receipt=bad)


def test_bus_u_rejects_invalid_activation_policy():
    g = RolloutReceiptGenerator()
    receipt = g.generate(**_gen_args())
    pub = BusUPublisher()
    with pytest.raises(ValueError, match="future-run-only"):
        pub.publish(receipt=receipt, activation_policy="immediate")


def test_bus_u_publishes_correctness_kpi():
    g = RolloutReceiptGenerator()
    pub = BusUPublisher()
    board = UnifiedKPIBoard()
    receipt = g.generate(**_gen_args())
    pub.publish(receipt=receipt)
    pub.publish(receipt=receipt, activation_policy="next_run_start_canary",
                canary_scope="10%")
    pub.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.BUS_U_ACTIVATION_CORRECTNESS)  # type: ignore[arg-type]
    assert sample.value == 1.0


def test_bus_u_correctness_drops_when_invalid_attempted():
    g = RolloutReceiptGenerator()
    pub = BusUPublisher()
    board = UnifiedKPIBoard()
    receipt = g.generate(**_gen_args())
    pub.publish(receipt=receipt)
    with pytest.raises(ValueError):
        pub.publish(receipt=receipt, activation_policy="immediate")
    pub.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.BUS_U_ACTIVATION_CORRECTNESS)  # type: ignore[arg-type]
    # 1 successful out of 2 attempts (the rejected attempt still counted)
    assert sample.value == pytest.approx(0.5)
