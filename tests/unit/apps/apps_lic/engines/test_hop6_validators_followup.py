"""Smoke tests for HOP6 validators wired in 2026-05-01 follow-up.

Tests the three new check methods directly via instance binding rather
than running the full HOP6 _process flow (which requires a fully
configured ImmutableStagingBuffer + TraceRegistry + agent_specs that
are out of scope for this unit layer). The integration test surface for
the full HOP6 lives in tests/integration/apps_lic/.

The point of this file is to lock the contract:
    * each check method returns a dict with rule_id/severity/passed/message
    * each delegates to its corresponding validator module
    * archetype passes through correctly
"""

from __future__ import annotations

import pytest

from apps_lic.engines.HOP6ValidationAgent import HOP6ValidationAgent


def _bound_method(name: str):
    """Pull a method off HOP6 without instantiating the dataclass.

    HOP6ValidationAgent inherits LICAgentBase which has heavy
    initialisation. Since the new check methods only consume their
    arguments (not self.config or instance state), unbinding them via
    ``__func__`` lets us call them with a stub self.
    """
    return getattr(HOP6ValidationAgent, name)


class _StubSelf:
    """Minimal stub for self when calling unbound check methods."""


_stub = _StubSelf()


class TestCheckArchetypeLength:
    def test_valid_short_message(self) -> None:
        check = _bound_method("_check_archetype_length")
        result = check(_stub, "Worth a quick chat?", "EXECUTIVE")
        assert result["rule_id"] == "LIC-E020"
        assert result["severity"] == "HIGH"
        assert result["passed"] is True
        assert "OK" in result["message"]

    def test_invalid_long_message(self) -> None:
        check = _bound_method("_check_archetype_length")
        long_text = "x" * 1000
        result = check(_stub, long_text, "EXECUTIVE")
        assert result["passed"] is False
        assert "exceeds" in result["message"].lower()


class TestCheckQuestionEnding:
    def test_executive_with_question(self) -> None:
        check = _bound_method("_check_question_ending")
        result = check(_stub, "Worth a quick chat?", "EXECUTIVE")
        assert result["rule_id"] == "LIC-E021"
        assert result["severity"] == "HIGH"
        assert result["passed"] is True

    def test_executive_without_question_fails(self) -> None:
        check = _bound_method("_check_question_ending")
        result = check(_stub, "Let me know your thoughts.", "EXECUTIVE")
        assert result["passed"] is False
        assert result["severity"] == "HIGH"

    def test_recruiter_without_question_passes_soft(self) -> None:
        check = _bound_method("_check_question_ending")
        result = check(_stub, "Open to discussing a role.", "RECRUITER")
        assert result["passed"] is True
        assert result["severity"] == "MEDIUM"


class TestCheckSpamTriggers:
    def test_clean_message_passes(self) -> None:
        check = _bound_method("_check_spam_triggers")
        result = check(_stub, "Saw the recent product launch — impressive work.")
        assert result["rule_id"] == "LIC-E022"
        assert result["passed"] is True
        assert result["severity"] == "LOW"

    def test_pushy_cta_hard_rejects(self) -> None:
        check = _bound_method("_check_spam_triggers")
        result = check(_stub, "Act now! Book a call on calendly.")
        assert result["passed"] is False
        assert result["severity"] == "HIGH"

    def test_corporate_cliche_soft_flags(self) -> None:
        check = _bound_method("_check_spam_triggers")
        result = check(_stub, "Let's circle back on synergies.")
        # Medium severity → soft (passed=True, severity=MEDIUM).
        assert result["passed"] is True
        assert result["severity"] == "MEDIUM"

    def test_false_urgency_hard_rejects(self) -> None:
        check = _bound_method("_check_spam_triggers")
        result = check(_stub, "Last chance — deadline approaching!")
        assert result["passed"] is False
        assert result["severity"] == "HIGH"
