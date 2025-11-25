"""Tests for Runtime Core Integration

Tests LLM invocation, sandbox execution, and
workflow orchestration integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.models.models import ExecutionContext, JobInput, ResumeInput
from runtime.runtime_utils import invoke_model, SandboxConfig


class TestLLMInvocation:
    """Test LLM invocation with mock responses."""
    
    def test_mock_invoke_model_strategy_response(self):
        """Test mock LLM response for strategy generation."""
        prompt = "Generate strategy for software engineer role"
        
        # This would normally call the LLM, but we're testing the mock setup
        # in the test runtime that provides predefined responses
        result = invoke_model(prompt, model="test-model")
        
        assert "strategy" in result.lower()
        assert len(result) > 0
    
    def test_mock_invoke_model_drafting_response(self):
        """Test mock LLM response for drafting."""
        prompt = "Draft resume for software engineer"
        
        result = invoke_model(prompt, model="test-model")
        
        assert "draft" in result.lower()
        assert len(result) > 0


class TestSandboxExecution:
    """Test sandbox execution and configuration."""
    
    def test_sandbox_config_creation(self):
        """Test sandbox configuration."""
        config = SandboxConfig(
            timeout=30,
            memory_limit="512MB",
            allow_network=False
        )
        
        assert config.timeout == 30
        assert config.memory_limit == "512MB"
        assert config.allow_network is False
    
    def test_sandbox_execution_mock(self):
        """Test sandbox execution with mock."""
        from runtime.runtime_utils import get_sandbox
        
        config = SandboxConfig(timeout=10)
        sandbox = get_sandbox(config)
        
        # Mock sandbox execution
        result = sandbox.execute("print('test')")
        
        # In real implementation, this would execute in sandbox
        # For tests, we verify the interface exists
        assert hasattr(sandbox, 'execute')


class TestWorkflowOrchestration:
    """Test workflow orchestration integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ctx = ExecutionContext(
            job=JobInput(
                title="Software Engineer",
                role_type="engineering",
                seniority="mid",
                posting_text="Looking for a software engineer"
            ),
            resume=ResumeInput(
                name="John Doe",
                email="john@example.com",
                sections={}
            ),
            user_id="test_user",
        )
    
    @patch('l2.execute_workflow_plans')
    def test_l2_execute_with_mock_llm(self, mock_execute):
        """Test L2 execution with mock LLM responses."""
        from l2 import execute_workflow_plans, L2ResultBundle
        
        # Mock L2 execution to return proper bundle
        mock_strategy = Mock()
        mock_strategy.branches = [Mock(description="Test strategy")]
        
        mock_execute.return_value = L2ResultBundle(
            strategy=mock_strategy,
            rag=Mock(),
            drafting=Mock(),
            qa=Mock(),
            safety=Mock(),
        )
        
        plans = [Mock()]
        result = execute_workflow_plans(plans, self.ctx)
        
        assert isinstance(result, L2ResultBundle)
        assert result.strategy is not None
    
    @patch('l3.orchestrate_execution')
    def test_l3_dag_orchestration(self, mock_orchestrate):
        """Test L3 DAG orchestration."""
        from l3.run_dag import run_dag
        from l2 import L2ResultBundle
        
        # Mock orchestrate execution
        mock_strategy = Mock()
        mock_strategy.branches = [Mock(description="Test strategy branch text")]
        
        mock_orchestrate.return_value = L2ResultBundle(
            strategy=mock_strategy,
            rag=Mock(),
            drafting=Mock(),
            qa=Mock(),
            safety=Mock(),
        )
        
        plans = [Mock()]
        dag = run_dag(plans, self.ctx)
        
        # Verify the final state patch is populated
        assert dag.final_state_patch["strategy_text"] == "Test strategy branch text"
        assert "strategy" in dag.final_state_patch
        assert "rag" in dag.final_state_patch


class TestIntegrationWithAdapters:
    """Test integration with various adapters."""
    
    def test_pinecone_adapter_integration(self):
        """Test Pinecone adapter integration."""
        mock_adapter = Mock()
        mock_adapter.query_by_text.return_value = [
            Mock(id="doc1", score=0.9, metadata={"text": "test"})
        ]
        
        ctx = ExecutionContext(
            job=JobInput(title="Test", role_type="test", seniority="test", posting_text="test"),
            resume=ResumeInput(name="Test", email="test@example.com", sections={}),
            user_id="test_user",
            pinecone_adapter=mock_adapter,
        )
        
        # Test adapter is accessible
        assert ctx.pinecone_adapter is mock_adapter
    
    def test_execution_context_validation(self):
        """Test ExecutionContext validation."""
        # Test with missing required fields
        with pytest.raises(Exception):
            ExecutionContext()  # Should fail without required fields


# Mock LLM responses for testing
MOCK_LLM_RESPONSES = {
    "strategy_generate_branch": "Mock strategy branch text for testing.",
    "drafting_generate_content": "Mock drafted content for testing.",
    "qa_evaluate_quality": "Mock quality assessment for testing.",
    "safety_check_policy": "Mock safety evaluation for testing.",
}


def mock_invoke_model(prompt: str, model: str = "test-model") -> str:
    """Mock invoke_model function for testing."""
    for keyword, response in MOCK_LLM_RESPONSES.items():
        if keyword in prompt.lower():
            return response
    
    return f"Mock response for: {prompt[:50]}..."


# Patch the invoke_model for tests
@pytest.fixture(autouse=True)
def patch_invoke_model():
    """Patch invoke_model for all tests in this module."""
    with patch('runtime.runtime_utils.invoke_model', side_effect=mock_invoke_model):
        yield


if __name__ == "__main__":
    pytest.main([__file__])
