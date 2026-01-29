"""
Integration Test: ConversationalRepairAgent in SSOT Pipeline
Phase 3 Verification - End-to-end testing
"""
import pytest
from unittest.mock import patch, AsyncMock
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_conversational_repair_in_ssot_registry():
    """Verify ConversationalRepairAgent can be loaded and called via SSOT system."""
    
    # Mock the LLM functionality to avoid API key requirements
    mock_llm_response = {"content": "Test repair response", "status": "success"}
    
    with patch('agentic_core.prompt_governance.agents.ConversationalRepairAgent.SovereignBaseAgent.llm_generate', 
               new_callable=AsyncMock, return_value=mock_llm_response):
        
        # Import after patching to ensure mock is applied
        from agentic_core.prompt_governance.agents.ConversationalRepairAgent import get_conversational_repair
        
        # Get agent instance
        agent = get_conversational_repair("/test/project")
        
        # Verify agent has heal method
        assert hasattr(agent, "heal"), "Agent must have heal method for SSOT"
        
        # Test heal method with a sample violation
        violation = {
            "type": "SYNTAX_ERROR",
            "message": "Indentation error in test file",
            "file": "test_file.py",
            "severity": "medium"
        }
        
        result = agent.heal(violation)
        
        # Verify the result structure matches SSOT expectations
        assert "success" in result, "Result must have success field"
        assert "message" in result, "Result must have message field"
        assert "agent" in result, "Result must have agent field"
        assert result["agent"] == "ConversationalRepairAgent"
        assert result["success"] is True

def test_conversational_repair_protocol_compliance():
    """Verify the agent implements HealerProtocol correctly."""
    
    from agentic_core.base_agents.HealerProtocol import HealerProtocol
    
    # Mock the LLM functionality
    mock_llm_response = {"content": "Test response", "status": "success"}
    
    with patch('agentic_core.prompt_governance.agents.ConversationalRepairAgent.SovereignBaseAgent.llm_generate',
               new_callable=AsyncMock, return_value=mock_llm_response):
        
        from agentic_core.prompt_governance.agents.ConversationalRepairAgent import ConversationalRepairAgent
        
        # Create agent instance directly for protocol testing
        agent = ConversationalRepairAgent.__new__(ConversationalRepairAgent)
        agent.project_root = "/test"
        agent.specialists = {
            "sherlock": {"name": "Sherlock", "role": "Root Cause Analysis"},
            "safety": {"name": "SafetyInspectorAgent", "role": "Security Review"},
            "dependency": {"name": "DependencySentinelAgent", "role": "Import Analysis"},
            "architecture": {"name": "ArchitectureGovernor", "role": "Architecture Compliance"},
        }
        agent.log_info = lambda msg: print(f"[INFO] {msg}")
        agent.log_error = lambda msg: print(f"[ERROR] {msg}")
        agent.llm_generate = AsyncMock(return_value=mock_llm_response)
        
        # Verify protocol compliance
        assert isinstance(agent, HealerProtocol), "Agent must implement HealerProtocol"
        assert hasattr(agent, "heal"), "Agent must have heal method"
        assert callable(agent.heal), "heal must be callable"
        
        # Test method signature
        violation = {"type": "TEST", "message": "Test message"}
        result = agent.heal(violation)
        
        # Verify return structure
        assert isinstance(result, dict), "heal must return dict"
        assert "success" in result, "Result must contain success field"
