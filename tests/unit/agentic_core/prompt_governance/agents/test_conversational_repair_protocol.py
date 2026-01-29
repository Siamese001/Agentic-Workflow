"""
Test Suite for ConversationalRepairAgent Protocol Compliance
Phase 3 Integration Verification
"""

from unittest.mock import AsyncMock, patch

import pytest

from agentic_core.prompt_governance.agents.ConversationalRepairAgent import (
    ConversationalRepairAgent,
)


class MockSovereignBaseAgent:
    """Mock base for isolation."""

    def __init__(self, project_root=None):
        self.project_root = project_root

    def log_info(self, msg):
        print(f"[INFO] {msg}")

    def log_error(self, msg):
        print(f"[ERROR] {msg}")

    async def llm_generate(self, prompt, provider):
        return {"content": "Mocked LLM Response", "status": "success"}


@pytest.fixture
def repair_agent():
    # Create agent with mocked base class methods
    agent = ConversationalRepairAgent.__new__(ConversationalRepairAgent)
    agent.project_root = None
    agent.specialists = {
        "sherlock": {"name": "Sherlock", "role": "Root Cause Analysis"},
        "safety": {"name": "SafetyInspectorAgent", "role": "Security Review"},
        "dependency": {"name": "DependencySentinelAgent", "role": "Import Analysis"},
        "architecture": {"name": "ArchitectureGovernor", "role": "Architecture Compliance"},
    }
    agent.log_info = lambda msg: print(f"[INFO] {msg}")
    agent.log_error = lambda msg: print(f"[ERROR] {msg}")
    agent.llm_generate = AsyncMock(
        return_value={"content": "Mocked LLM Response", "status": "success"}
    )
    return agent


def test_heal_method_exists(repair_agent):
    """Verify strictly required heal() method exists."""
    assert hasattr(repair_agent, "heal"), "Agent must implement heal() for SSOT"
    assert callable(repair_agent.heal)


def test_heal_synchronous_execution(repair_agent):
    """Verify heal() creates a loop and returns synchronously."""
    violation = {"type": "SYNTAX_ERROR", "message": "Unexpected indent", "file": "test.py"}

    result = repair_agent.heal(violation)

    assert result["success"] is True
    assert result["message"] == "Mocked LLM Response"
    assert result["agent"] == "ConversationalRepairAgent"


def test_heal_handles_exceptions(repair_agent):
    """Verify robust error handling in the bridge."""
    # Force debate_failure to raise
    with patch.object(repair_agent, "debate_failure", side_effect=Exception("Async Boom")):
        violation = {"type": "TEST"}
        result = repair_agent.heal(violation)

        assert result["success"] is False
        assert "Async Boom" in result["error"]


def test_specialist_initialization(repair_agent):
    """Verify specialists are loaded."""
    assert "sherlock" in repair_agent.specialists
    assert "safety" in repair_agent.specialists
    assert repair_agent.specialists["sherlock"]["role"] == "Root Cause Analysis"


def test_heal_llm_failure_fallback(repair_agent):
    """Verify graceful fallback when LLM fails."""

    # Mock llm_generate to raise exception
    async def failing_llm(prompt, provider):
        raise Exception("LLM service unavailable")

    repair_agent.llm_generate = failing_llm

    violation = {"type": "TEST_ERROR", "message": "Test message"}
    result = repair_agent.heal(violation)

    assert result["success"] is False
    assert "LLM failed" in result["message"]


def test_heal_context_mapping(repair_agent):
    """Verify violation dict is properly mapped to context."""
    violation = {
        "type": "IMPORT_ERROR",
        "message": "Module not found",
        "file": "/path/to/file.py",
        "severity": "high",
    }

    # Mock debate_failure to capture context
    captured_context = {}

    async def capture_context(context):
        captured_context.update(context)
        return {"success": True, "consensus_reasoning": "OK", "consensus_code": "code"}

    with patch.object(repair_agent, "debate_failure", side_effect=capture_context):
        repair_agent.heal(violation)

    assert captured_context["violation_type"] == "IMPORT_ERROR"
    assert captured_context["error"] == "Module not found"
    assert captured_context["file"] == "/path/to/file.py"
    assert captured_context["severity"] == "high"


def test_get_conversational_repair_singleton():
    """Verify singleton pattern works with project_root parameter."""
    # Reset singleton
    import agentic_core.prompt_governance.agents.ConversationalRepairAgent as cra_module

    cra_module._conversational_repair = None

    # Mock the constructor to avoid real initialization
    with patch.object(cra_module.ConversationalRepairAgent, "__init__", return_value=None):
        agent1 = cra_module.get_conversational_repair("/test/root")
        agent2 = cra_module.get_conversational_repair("/test/root")

        assert agent1 is agent2  # Same instance


@pytest.mark.asyncio
async def test_debate_failure_async_method(repair_agent):
    """Verify the async debate_failure method works correctly."""
    context = {"error": "Test error", "file": "test.py", "violation_type": "SYNTAX_ERROR"}

    result = await repair_agent.debate_failure(context)

    assert result["success"] is True
    assert result["consensus_reasoning"] == "Mocked LLM Response"
    assert result["consensus_code"] == "# Fixed code via Sovereign LLM"
