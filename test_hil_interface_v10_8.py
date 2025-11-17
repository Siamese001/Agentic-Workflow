from copy import deepcopy

from hil_interface import apply_hil_feedback


def test_apply_hil_feedback_does_not_mutate():
    original_state = {"a": 1, "nested": {"b": 2}}
    snapshot = deepcopy(original_state)

    updated = apply_hil_feedback(original_state, {"comment": "looks good"})

    assert original_state == snapshot
    assert updated is not original_state


def test_apply_hil_feedback_deterministic():
    state = {"foo": "bar"}
    feedback = {"note": "check"}

    first = apply_hil_feedback(state, feedback)
    second = apply_hil_feedback(state, feedback)

    assert first == second
    assert first["hil_feedback"] == feedback


def test_apply_hil_feedback_sets_key():
    state = {}
    feedback = {"decision": "approve"}

    updated = apply_hil_feedback(state, feedback)

    assert "hil_feedback" in updated
    assert updated["hil_feedback"] == feedback
