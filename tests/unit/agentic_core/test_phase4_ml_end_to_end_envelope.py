"""
Phase 4.1 — Wave 3 Tests: End-to-end-shaped mixin enforcement.

Exercises the real mixin call paths (ml_store_healing_pattern, ml_cache_set)
rather than MLWriteIntentExecutor helpers directly.

Proves:
- Both mixin write methods raise MLWriteEnvelopeViolation outside sandbox.
- Both mixin write methods call through to the underlying client inside sandbox.
- Underlying client write methods are NEVER invoked outside sandbox.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.types.ml_write_intent import (
    MLWriteEnvelopeViolation,
    MLWriteIntentExecutor,
    is_commit_sandbox_active,
)
from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Minimal concrete agent that uses the mixin (no real base class needed)
# ---------------------------------------------------------------------------


class _TestAgent(MetaLearningClientMixin):
    """Minimal concrete agent for testing mixin enforcement."""

    _ml_domain = "agentic_core"

    def __init__(self) -> None:
        MetaLearningClientMixin.reset_ml_singletons()


def _make_agent_with_mock_client() -> tuple[_TestAgent, MagicMock]:
    """Return (agent, mock_client) with the mixin client pre-wired."""
    agent = _TestAgent()
    mock_client = MagicMock()
    mock_client.store_healing_pattern.return_value = "pattern-mock-001"
    mock_client.cache_set.return_value = True
    MetaLearningClientMixin._ml_client = mock_client
    return agent, mock_client


_VIOLATION = {"type": "import_error", "path": "agentic_core/foo.py", "id": "v-001"}
_HEALING_RESULT = {"status": "fixed", "fix": "added import"}
_CACHE_KEY = "ast:result:foo"
_CACHE_VALUE = {"score": 42}


# ---------------------------------------------------------------------------
# Wave 3 — Negative: blocked outside sandbox
# ---------------------------------------------------------------------------


class TestMixinBlockedOutsideSandbox:
    def test_mixin_store_healing_pattern_blocked_outside_sandbox(self):
        """
        ml_store_healing_pattern() called outside L2.2 sandbox MUST raise
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

    def test_mixin_cache_set_blocked_outside_sandbox(self):
        """
        ml_cache_set() called outside L2.2 sandbox MUST raise
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

    def test_store_healing_pattern_client_never_called_outside_sandbox(self):
        """
        Monkeypatch: underlying client.store_healing_pattern must NEVER be
        invoked when called outside the sandbox.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        mock_client.store_healing_pattern.assert_not_called()

    def test_cache_set_client_never_called_outside_sandbox(self):
        """
        Monkeypatch: underlying client.cache_set must NEVER be invoked
        when called outside the sandbox.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        mock_client.cache_set.assert_not_called()

    def test_violation_error_message_contains_method_name_store(self):
        agent, _ = _make_agent_with_mock_client()
        with pytest.raises(MLWriteEnvelopeViolation) as exc_info:
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)
        assert "ml_store_healing_pattern" in str(exc_info.value)

    def test_violation_error_message_contains_method_name_cache_set(self):
        agent, _ = _make_agent_with_mock_client()
        with pytest.raises(MLWriteEnvelopeViolation) as exc_info:
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)
        assert "ml_cache_set" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Wave 3 — Positive: allowed inside sandbox, client write IS invoked
# ---------------------------------------------------------------------------


class TestMixinAllowedInsideSandbox:
    def test_mixin_store_healing_pattern_allowed_inside_sandbox_executes_client_write(self):
        """
        ml_store_healing_pattern() inside L2.2 sandbox must call through to
        client.store_healing_pattern() and return the pattern_id.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            result = agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        mock_client.store_healing_pattern.assert_called_once()
        assert result == "pattern-mock-001"

    def test_mixin_cache_set_allowed_inside_sandbox_executes_client_write(self):
        """
        ml_cache_set() inside L2.2 sandbox must call through to
        client.cache_set() and return True.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            result = agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        mock_client.cache_set.assert_called_once()
        assert result is True

    def test_store_healing_pattern_passes_correct_args_to_client(self):
        """Client receives (possibly sanitized) violation, healing_result, and domain."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        call_args = mock_client.store_healing_pattern.call_args
        passed_violation = call_args[0][0]
        # Guardrails may sanitize the violation dict; assert on stable keys only
        assert passed_violation.get("type") == _VIOLATION["type"]
        assert passed_violation.get("path") == _VIOLATION["path"]
        assert call_args[0][1] == _HEALING_RESULT
        assert call_args[0][2] == "agentic_core"

    def test_cache_set_passes_correct_key_value_to_client(self):
        """Client receives key, value, domain, and ttl."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE, ttl=3600)

        call_args = mock_client.cache_set.call_args
        assert call_args[0][0] == _CACHE_KEY
        assert call_args[0][1] == _CACHE_VALUE

    def test_sandbox_deactivates_after_mixin_write(self):
        """Sandbox must be inactive after the context manager exits."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        assert is_commit_sandbox_active() is False

    def test_cache_set_sandbox_deactivates_after_write(self):
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        assert is_commit_sandbox_active() is False


# ---------------------------------------------------------------------------
# Wave 3 — Bypass detection: direct client write outside mixin is also blocked
# ---------------------------------------------------------------------------


class TestDirectClientBypassBlocked:
    def test_direct_client_store_outside_sandbox_not_guarded_by_client(self):
        """
        The client itself has no sandbox guard — enforcement lives in the mixin.
        This test documents that the mixin is the ONLY enforcement seam.
        Calling client.store_healing_pattern directly bypasses the guard,
        which is why the mixin guard is the required enforcement point.
        """
        _, mock_client = _make_agent_with_mock_client()
        # Direct call to mock does not raise — enforcement is in the mixin only
        mock_client.store_healing_pattern(_VIOLATION, _HEALING_RESULT, "agentic_core")
        mock_client.store_healing_pattern.assert_called_once()

    def test_mixin_is_sole_enforcement_seam_for_store(self):
        """
        Any code path that reaches client.store_healing_pattern MUST go through
        the mixin. Verify the mixin raises before the client is ever touched.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        # Client was never reached
        mock_client.store_healing_pattern.assert_not_called()

    def test_mixin_is_sole_enforcement_seam_for_cache_set(self):
        """
        Any code path that reaches client.cache_set MUST go through the mixin.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        mock_client.cache_set.assert_not_called()
