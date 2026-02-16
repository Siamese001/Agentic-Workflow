"""Wave 8.1: Governance test for heal LLM seam invocation.

Tests that when HEAL_POLICY_MODEL_ESCALATION is enabled and DEFAULT_HEAL_LLM_CALLER is set:
- HealLlmRequest is constructed with correct fields
- Seam is invoked exactly once
- Logging confirms invocation
- Default-off behavior unchanged
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L5_safety.types.heal_llm_seam import HealLlmRequest
from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier
from agentic_core.utils.decorators_util import standard_heal

pytestmark = pytest.mark.governance


class DummyHealer:
    """Dummy agent with @standard_heal decorated heal_repository."""

    @standard_heal
    def heal_repository(self, **kwargs):
        """Capture kwargs for assertion."""
        self._captured_kwargs = kwargs
        return {"status": "PASS", "violations_found": 0}


def test_heal_llm_seam_default_off():
    """When flag unset, seam not invoked."""
    with patch.dict(os.environ, {}, clear=False):
        if "HEAL_POLICY_MODEL_ESCALATION" in os.environ:
            del os.environ["HEAL_POLICY_MODEL_ESCALATION"]

        mock_caller = MagicMock(return_value="ok")
        with patch(
            "agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER",
            mock_caller,
        ):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True, execute=False)

            assert result["status"] == "PASS"
            mock_caller.assert_not_called()


def test_heal_llm_seam_enabled_no_caller():
    """When enabled but caller is None, seam not invoked."""

    def mock_router(tier: ReasoningTier) -> str:
        return "local_low"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch("agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER", None):
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                assert result["status"] == "PASS"


def test_heal_llm_seam_enabled_with_caller():
    """When enabled + caller set + routed model, seam invoked with correct request."""
    from agentic_core.L5_safety.types.heal_policy_types import (
        ReasoningTier,
    )

    def mock_router(tier: ReasoningTier) -> str:
        return "local_high"

    captured_request = None

    def mock_caller(request: HealLlmRequest) -> str:
        nonlocal captured_request
        captured_request = request
        return "ok"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch(
                "agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER",
                mock_caller,
            ):
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                assert result["status"] == "PASS"
                assert captured_request is not None
                assert captured_request.prompt == "heal_policy_probe"
                assert captured_request.model_id == "local_high"
                assert captured_request.metadata == {"source": "standard_heal"}


def test_heal_llm_seam_logging():
    """When seam invoked, llm_probe log emitted."""

    def mock_router(tier: ReasoningTier) -> str:
        return "local_high"

    def mock_caller(request: HealLlmRequest) -> str:
        return "ok"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch(
                "agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER",
                mock_caller,
            ):
                with patch("agentic_core.utils.decorators_util.Logger") as mock_logger:
                    healer = DummyHealer()
                    result = healer.heal_repository(dry_run=True, execute=False)

                    assert result["status"] == "PASS"

                    # Check that llm_probe log was emitted
                    debug_calls = list(mock_logger.debug.call_args_list)
                    llm_probe_logs = [call for call in debug_calls if "llm_probe=CALLED" in str(call)]
                    assert len(llm_probe_logs) == 1, "Expected exactly one llm_probe log"
                    assert "local_high" in str(llm_probe_logs[0])


def test_heal_llm_seam_no_routed_model():
    """When routed_model_id is None, seam not invoked."""

    def mock_router(tier: ReasoningTier) -> str | None:
        return None

    mock_caller = MagicMock(return_value="ok")
    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch(
                "agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER",
                mock_caller,
            ):
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                assert result["status"] == "PASS"
                mock_caller.assert_not_called()


def test_heal_llm_seam_output_unchanged():
    """Seam invocation does not change heal_repository output."""

    def mock_router(tier: ReasoningTier) -> str:
        return "local_high"

    def mock_caller(request: HealLlmRequest) -> str:
        return "ok"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch(
                "agentic_core.utils.decorators_util.DEFAULT_HEAL_LLM_CALLER",
                mock_caller,
            ):
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                # Verify canonical fields are present and unchanged
                assert result["status"] == "PASS"
                assert result["violations_found"] == 0
                assert "execution_time_ms" in result
                assert isinstance(result["execution_time_ms"], float)
