"""End-to-End Workflow Tests

Tests complete workflows from job input to final output,
integrating all layers and components.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from core.models.models import ExecutionContext, JobInput, ResumeInput, WorkflowConfig


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow execution."""
    
    def test_full_workflow_with_all_components(self):
        """Test complete workflow with strategy, RAG, drafting, QA, and safety."""
        ctx = ExecutionContext(
            job=JobInput(
                title="Senior Software Engineer",
                role_type="engineering",
                seniority="senior",
                posting_text="Looking for a senior software engineer with Python experience"
            ),
            resume=ResumeInput(
                name="Jane Doe",
                email="jane@example.com",
                sections={}
            ),
            user_id="test_user",
        )
        
        # Mock all external dependencies
        with patch('l2.execute_workflow_plans') as mock_execute:
            with patch('runtime.runtime_utils.invoke_model') as mock_llm:
                
                # Mock LLM responses
                mock_llm.side_effect = [
                    "Generated strategy for senior software engineer",
                    "Drafted resume content",
                    "QA evaluation passed",
                    "Safety check passed"
                ]
                
                # Mock L2 execution
                from l2 import L2ResultBundle
                mock_strategy = Mock()
                mock_strategy.branches = [Mock(description="Senior engineer strategy")]
                
                mock_execute.return_value = L2ResultBundle(
                    strategy=mock_strategy,
                    rag=Mock(),
                    drafting=Mock(),
                    qa=Mock(),
                    safety=Mock(),
                )
                
                # Execute workflow
                from l3.run_dag import run_dag
                plans = [Mock()]
                result = run_dag(plans, ctx)
                
                # Verify workflow completed
                assert result is not None
                assert result.final_state_patch["strategy_text"] is not None
    
    def test_workflow_with_different_job_types(self):
        """Test workflow with different job types and roles."""
        job_types = [
            ("Data Scientist", "data_science", "senior"),
            ("Product Manager", "product", "mid"),
            ("UX Designer", "design", "junior"),
        ]
        
        for title, role_type, seniority in job_types:
            ctx = ExecutionContext(
                job=JobInput(
                    title=title,
                    role_type=role_type,
                    seniority=seniority,
                    posting_text=f"Looking for a {title}"
                ),
                resume=ResumeInput(
                    name="Test User",
                    email="test@example.com",
                    sections={}
                ),
                user_id="test_user",
            )
            
            # Verify context is properly created
            assert ctx.job.title == title
            assert ctx.job.role_type == role_type
            assert ctx.job.seniority == seniority
    
    def test_workflow_error_handling(self):
        """Test workflow error handling and recovery."""
        ctx = ExecutionContext(
            job=JobInput(title="Test", role_type="test", seniority="mid", posting_text="test"),
            resume=ResumeInput(name="Test", email="test@example.com", sections={}),
            user_id="test_user",
        )
        
        # Test with failing L2 execution
        with patch('l2.execute_workflow_plans') as mock_execute:
            mock_execute.side_effect = Exception("L2 execution failed")
            
            from l3.run_dag import run_dag
            
            with pytest.raises(Exception):
                plans = [Mock()]
                run_dag(plans, ctx)


class TestWorkflowConfiguration:
    """Test workflow configuration and customization."""
    
    def test_workflow_config_customization(self):
        """Test workflow configuration options."""
        config = WorkflowConfig(
            enable_rag=True,
            enable_qa=True,
            enable_safety=True,
            max_drafts=3
        )
        
        assert config.enable_rag is True
        assert config.enable_qa is True
        assert config.enable_safety is True
        assert config.max_drafts == 3
    
    def test_workflow_with_custom_config(self):
        """Test workflow execution with custom configuration."""
        config = WorkflowConfig(
            enable_rag=False,  # Disable RAG for faster execution
            enable_qa=True,
            enable_safety=True,
            max_drafts=1
        )
        
        ctx = ExecutionContext(
            job=JobInput(title="Test", role_type="test", seniority="mid", posting_text="test"),
            resume=ResumeInput(name="Test", email="test@example.com", sections={}),
            user_id="test_user",
            config=config
        )
        
        # Verify config is applied
        assert ctx.config.enable_rag is False
        assert ctx.config.max_drafts == 1


class TestWorkflowPerformance:
    """Test workflow performance and optimization."""
    
    def test_workflow_execution_time(self):
        """Test workflow execution time is reasonable."""
        import time
        
        ctx = ExecutionContext(
            job=JobInput(title="Test", role_type="test", seniority="mid", posting_text="test"),
            resume=ResumeInput(name="Test", email="test@example.com", sections={}),
            user_id="test_user",
        )
        
        with patch('l2.execute_workflow_plans') as mock_execute:
            from l2 import L2ResultBundle
            mock_strategy = Mock()
            mock_strategy.branches = [Mock(description="Test strategy")]
            
            mock_execute.return_value = L2ResultBundle(
                strategy=mock_strategy,
                rag=Mock(),
                drafting=Mock(),
                qa=Mock(),
                safety=Mock(),
            )
            
            start_time = time.time()
            
            from l3.run_dag import run_dag
            plans = [Mock()]
            result = run_dag(plans, ctx)
            
            execution_time = time.time() - start_time
            
            # Should complete in reasonable time (mocked execution)
            assert execution_time < 5.0
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])
