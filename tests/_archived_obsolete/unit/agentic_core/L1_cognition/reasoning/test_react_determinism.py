"""Behavioral tests for react_determinism."""

from __future__ import annotations

from agentic_core.react_determinism import stable_react_signature


def test_same_inputs_produce_same_signature():
    left = stable_react_signature("hash-1", ("retrieve", "synthesize"))
    right = stable_react_signature("hash-1", ("retrieve", "synthesize"))
    assert left == right


def test_different_steps_produce_different_signatures():
    left = stable_react_signature("hash-1", ("retrieve",))
    right = stable_react_signature("hash-1", ("retrieve", "act"))
    assert left != right
