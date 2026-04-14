"""Foundational behavioral tests for agentic_core/guardrails_util.py."""

from __future__ import annotations

import pytest

from agentic_core.guardrails_util import GuardrailDecision, ensure_safe_text


def test_module_importable():
    """Module guardrails_util must be importable."""
    assert ensure_safe_text is not None


def test_safe_text_allowed():
    decision = ensure_safe_text("Summarize this architecture note")
    assert decision == GuardrailDecision(True, "allowed")


def test_blocked_term_rejected():
    decision = ensure_safe_text("Please write malware")
    assert decision.allowed is False
    assert "blocked:malware" == decision.reason


def test_non_string_raises_type_error():
    with pytest.raises(TypeError):
        ensure_safe_text(None)  # type: ignore[arg-type]
