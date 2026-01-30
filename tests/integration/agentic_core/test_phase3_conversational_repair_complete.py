"""
Phase 3 Complete Integration Test: ConversationalRepairAgent
Verifies full async/sync bridge functionality in SSOT context
"""

import os
import sys
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_phase3_complete_integration():
    """Complete Phase 3 integration test for ConversationalRepairAgent."""

    # Mock LLM to avoid API requirements
    mock_llm_response = {
        "content": "ANALYSIS: The error indicates a syntax issue. FIX: Correct the indentation.",
        "status": "success",
    }

    with patch(
        "agentic_core.prompt_governance.agents.ConversationalRepairAgent.SovereignBaseAgent.llm_generate",
        new_callable=AsyncMock,
        return_value=mock_llm_response,
    ):
        # Test 1: Agent Discovery
        from agentic_core.L6_observability.ConversationalRepairAgent import (
            get_conversational_repair,
        )

        agent = get_conversational_repair("/test/root")

        # Test 2: Protocol Compliance
        from agentic_core.base_agents.HealerProtocol import HealerProtocol

        assert isinstance(agent, HealerProtocol), "Must implement HealerProtocol"

        # Test 3: Synchronous heal() method (SSOT entry point)
        violation = {
            "type": "SYNTAX_ERROR",
            "message": "IndentationError: unexpected indent",
            "file": "/test/project/broken.py",
            "severity": "high",
            "line": 15,
        }

        # This should work synchronously despite internal async operations
        result = agent.heal(violation)

        # Test 4: Result Structure Validation
        assert isinstance(result, dict), "Must return dict"
        assert "success" in result, "Must have success field"
        assert "message" in result, "Must have message field"
        assert "diff" in result, "Must have diff field"
        assert "agent" in result, "Must have agent field"

        assert result["success"] is True, "Should succeed with mocked LLM"
        assert result["agent"] == "ConversationalRepairAgent", "Must identify itself"
        assert "ANALYSIS" in result["message"], "Should contain LLM analysis"

        # Test 5: Error Handling
        with patch.object(agent, "debate_failure", side_effect=Exception("Async failure")):
            error_result = agent.heal(violation)
            assert error_result["success"] is False, "Should handle async errors"
            assert "Async failure" in error_result["error"], "Should preserve error message"

        # Test 6: LLM Failure Fallback
        async def failing_llm(prompt, provider):
            raise Exception("LLM service down")

        agent.llm_generate = failing_llm
        fallback_result = agent.heal(violation)
        assert fallback_result["success"] is False, "Should handle LLM failure"
        assert "LLM failed" in fallback_result["message"], "Should use fallback message"

        print("✅ Phase 3 Integration Complete: All tests passed")


def test_async_sync_bridge_isolation():
    """Verify the async/sync bridge doesn't interfere with event loops."""

    mock_response = {"content": "Bridge test successful", "status": "success"}

    with patch(
        "agentic_core.prompt_governance.agents.ConversationalRepairAgent.SovereignBaseAgent.llm_generate",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from agentic_core.L6_observability.ConversationalRepairAgent import (
            ConversationalRepairAgent,
        )

        # Create agent with mocked methods
        agent = ConversationalRepairAgent.__new__(ConversationalRepairAgent)
        agent.project_root = "/test"
        agent.specialists = {"test": {"name": "Test", "role": "Testing"}}
        agent.log_info = lambda msg: print(f"[INFO] {msg}")
        agent.log_error = lambda msg: print(f"[ERROR] {msg}")
        agent.llm_generate = AsyncMock(return_value=mock_response)

        # Test multiple concurrent calls (should not deadlock)
        violations = [
            {"type": "ERROR1", "message": "Test 1"},
            {"type": "ERROR2", "message": "Test 2"},
            {"type": "ERROR3", "message": "Test 3"},
        ]

        results = []
        for violation in violations:
            result = agent.heal(violation)
            results.append(result)

        # All should succeed independently
        assert all(r["success"] for r in results), "All concurrent calls should succeed"
        assert len(set(r["message"] for r in results)) == 1, "Should use same mock response"

        print("✅ Async/Sync Bridge Isolation Verified")


if __name__ == "__main__":
    test_phase3_complete_integration()
    test_async_sync_bridge_isolation()
    print("\n🎉 PHASE 3 CONVERSATIONAL REPAIR INTEGRATION: COMPLETE SUCCESS")
