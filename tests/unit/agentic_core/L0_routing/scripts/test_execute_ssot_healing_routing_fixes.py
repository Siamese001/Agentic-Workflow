"""
Tests for healing routing bug fixes in execute_ssot.py.

Covers:
1. RuntimeError/OSError/TimeoutError now caught in Qwen except clause
2. SSOT model ID constants used (no os.getenv leaks)
3. Gemini enable_llm boundary condition fixed (conf == 0.50 uses <=)
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestQwenExceptionHandling:
    """Test that Qwen failures are properly caught and default to declined (not approved)."""

    def test_qwen_runtime_error_caught_and_defaults_to_declined(self):
        """When Qwen subprocess raises RuntimeError, should catch it and default qwen_approved=False."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        # Mock the Qwen arbiter to raise RuntimeError (subprocess failure)
        def mock_arbiter(*args, **kwargs):
            raise RuntimeError("vLLM subprocess failed: exit code 1")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            # Create a mock confidence score that routes to QWEN tier (0.50 < conf <= 0.80)
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            mock_routing = MagicMock()
            mock_routing.tier = MagicMock()
            mock_routing.tier.value = "QWEN"
            mock_routing.score = 50
            mock_routing.gate_applied = "test_gate"

            # Call should_proceed_with_healing which internally routes to Qwen
            # Since Qwen raises RuntimeError, it should be caught and default to declined
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # After the fix: RuntimeError is caught, qwen_approved defaults to False
            # The Qwen tier then declines and returns False
            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason

    def test_qwen_timeout_error_caught(self):
        """When Qwen subprocess times out, should catch TimeoutError and default to declined."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        def mock_arbiter(*args, **kwargs):
            raise TimeoutError("Qwen subprocess timed out")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason

    def test_qwen_os_error_caught(self):
        """When Qwen subprocess raises OSError (WSL not available), should catch and decline."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        def mock_arbiter(*args, **kwargs):
            raise OSError("WSL not found")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason


class TestSSOTModelIDConstants:
    """Test that model IDs come from SSOT constants, not os.getenv()."""

    def test_qwen_model_id_from_ssot_constant(self):
        """Qwen model ID should come from healing_tier_config.QWEN_14B_MODEL_ID, not os.getenv."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        # Clear any env vars that might interfere
        old_env = os.environ.get("QWEN_14B_MODEL")
        if old_env:
            del os.environ["QWEN_14B_MODEL"]

        try:
            engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

            mock_confidence = MagicMock()
            mock_confidence.value = 0.65  # Routes to QWEN tier
            mock_confidence.reasoning = "test"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Check that decision_data uses the SSOT constant, not env var
            # The model ID should be from healing_tier_config.QWEN_14B_MODEL_ID
            assert len(engine.decisions_made) > 0
            decision = engine.decisions_made[-1]
            # Should be the SSOT constant value, not the env var fallback
            assert decision["model"] == "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"

        finally:
            if old_env:
                os.environ["QWEN_14B_MODEL"] = old_env

    def test_gemini_model_id_from_ssot_constant(self):
        """Gemini model ID should be hardcoded 'gemini-2.5-pro', not os.getenv."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        old_env = os.environ.get("GEMINI_MODEL")
        if old_env:
            del os.environ["GEMINI_MODEL"]

        try:
            engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

            mock_confidence = MagicMock()
            mock_confidence.value = 0.40  # Routes to GEMINI tier (conf <= 0.50)
            mock_confidence.reasoning = "test"

            # enable_llm=False will block Gemini, but we can check the decision_data model field
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Check decision_data
            assert len(engine.decisions_made) > 0
            decision = engine.decisions_made[-1]
            # Should be the hardcoded SSOT value
            assert decision["model"] == "gemini-2.5-pro"

        finally:
            if old_env:
                os.environ["GEMINI_MODEL"] = old_env


class TestGeminiEnableLLMBoundary:
    """Test that Gemini enable_llm guard uses <= instead of < at conf == 0.50."""

    def test_gemini_boundary_conf_exactly_050_blocked_when_llm_disabled(self):
        """When conf == 0.50 exactly and enable_llm=False, should block (not fall through)."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.50  # Exactly on the boundary
        mock_confidence.reasoning = "test"

        approved, reason = engine.should_proceed_with_healing(
            mock_confidence,
            agent_name="test_agent",
            territory="test_territory",
        )

        # Should be blocked because enable_llm=False and conf <= 0.50
        assert approved is False
        assert "Manual Review Required" in reason or "LLM disabled" in reason

    def test_gemini_boundary_conf_049_blocked_when_llm_disabled(self):
        """When conf == 0.49 and enable_llm=False, should also block."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.49
        mock_confidence.reasoning = "test"

        approved, reason = engine.should_proceed_with_healing(
            mock_confidence,
            agent_name="test_agent",
            territory="test_territory",
        )

        assert approved is False
        assert "Manual Review Required" in reason or "LLM disabled" in reason

    def test_gemini_boundary_conf_051_not_blocked_when_llm_disabled(self):
        """When conf == 0.51 (above threshold) and enable_llm=False, routes to QWEN (not Gemini)."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.51  # Just above QWEN lower bound
        mock_confidence.reasoning = "test"

        # Mock Qwen to decline so we can verify it was routed there
        def mock_arbiter(*args, **kwargs):
            return {"decision": False, "reason": "Qwen declined"}

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Should route to QWEN tier, not Gemini
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason
            # Should NOT have "Manual Review Required"
            assert "Manual Review Required" not in reason


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
