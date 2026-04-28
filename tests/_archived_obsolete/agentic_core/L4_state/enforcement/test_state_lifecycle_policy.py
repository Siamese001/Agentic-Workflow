"""Tests for StateLifecyclePolicy - state transition policy."""
import pytest
from agentic_core.L4_state.enforcement.state_lifecycle_policy import StateLifecyclePolicy


class TestStateLifecyclePolicy:
    def test_init(self):
        p = StateLifecyclePolicy()
        assert p is not None

    def test_valid_transition(self):
        p = StateLifecyclePolicy()
        assert p.is_valid_transition("draft", "active") is True

    def test_invalid_transition(self):
        p = StateLifecyclePolicy()
        assert p.is_valid_transition("archived", "draft") is False

    def test_apply_valid_transition(self):
        p = StateLifecyclePolicy()
        new_state = p.apply_transition("draft", "active")
        assert new_state == "active"

    def test_apply_invalid_transition_raises(self):
        p = StateLifecyclePolicy()
        with pytest.raises(ValueError):
            p.apply_transition("archived", "draft")

    def test_get_allowed_transitions(self):
        p = StateLifecyclePolicy()
        allowed = p.get_allowed_transitions("draft")
        assert isinstance(allowed, list)

    def test_terminal_state(self):
        p = StateLifecyclePolicy()
        assert p.is_terminal("archived") is True
        assert p.is_terminal("active") is False

    def test_register_custom_transition(self):
        p = StateLifecyclePolicy()
        p.register_transition("custom_a", "custom_b")
        assert p.is_valid_transition("custom_a", "custom_b") is True
