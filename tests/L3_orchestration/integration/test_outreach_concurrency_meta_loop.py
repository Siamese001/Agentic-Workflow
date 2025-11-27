"""
Phase 7 Meta-loop + Concurrency Integration Tests

Tests meta-loop fallback behavior with concurrent outreach workflow.
Ensures meta-loop properly handles concurrent execution failures and provides
deterministic fallback sequences.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any
from dataclasses import dataclass

from l3.outreach_orchestrator import OutreachOrchestrator, OutreachPipelineResult
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile


@dataclass
class MockMetaLoopState:
    """Mock meta-loop state for testing."""
    attempt_count: int
    fallback_triggered: bool
    last_error: str = ""
    
    def __post_init__(self):
        self.__dict__.update({
            "attempt_count": self.attempt_count,
            "fallback_triggered": self.fallback_triggered,
            "last_error": self.last_error
        })


class TestOutreachConcurrencyMetaLoop:
    """Test suite for meta-loop integration with concurrent outreach workflow."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator for meta-loop testing."""
        mock_archetype_planner = Mock()
        mock_research_planner = Mock()
        mock_message_planner = Mock()
        mock_company_executor = Mock()
        mock_contact_executor = Mock()
        mock_message_executor = Mock()
        mock_state_manager = Mock()
        mock_safety_validator = Mock()
        
        orchestrator = OutreachOrchestrator(
            archetype_planner=mock_archetype_planner,
            research_planner=mock_research_planner,
            message_planner=mock_message_planner,
            company_executor=mock_company_executor,
            contact_executor=mock_contact_executor,
            message_executor=mock_message_executor,
            state_manager=mock_state_manager,
            safety_validator=mock_safety_validator
        )
        
        # Setup default mock behaviors
        mock_archetype_planner.plan_archetype_influence.return_value = ArchetypeContext(
            archetype=ArchetypeType.C_LEVEL,
            confidence=0.8
        )
        
        mock_research_planner.plan_research.return_value = {"query": "test"}
        
        mock_company_executor.search_company_context.return_value = Mock(
            company="test_company",
            size="large"
        )
        
        mock_contact_executor.search_contact_profile.return_value = Mock(
            contact="test_contact",
            level="senior"
        )
        
        mock_message_planner.create_message_plan.return_value = Mock(
            template="test_template"
        )
        
        mock_message_executor.generate_message.return_value = Mock(
            message="Test message",
            content="Test message"
        )
        
        mock_safety_validator.evaluate.return_value = Mock(
            passed=True,
            findings=[]
        )
        
        return orchestrator
    
    @pytest.fixture
    def sample_mission(self):
        """Create sample outreach mission."""
        return OutreachMission(
            objective="networking",
            target_role="Software Engineer",
            target_company="Tech Corp",
            value_proposition="Collaboration opportunity"
        )
    
    @pytest.fixture
    def sample_recipient(self):
        """Create sample recipient profile."""
        return RecipientProfile(
            name="John Doe",
            title="Engineering Manager",
            company="Tech Corp",
            industry="Technology",
            seniority="Senior",
            department="Engineering",
            skills=["Python", "Leadership", "System Design"],
            recent_activity=["Hiring", "Product Launch"],
            metadata={"location": "San Francisco"}
        )
    
    def test_meta_loop_handles_concurrent_execution_failure(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that meta-loop properly handles concurrent execution failures."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "meta_loop_enabled": True,
            "max_attempts": 3
        }
        
        # Mock concurrent execution to fail
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.side_effect = [
                Exception("Concurrent execution failed"),
                OutreachPipelineResult(
                    success=True,
                    message="Fallback success",
                    metadata={"fallback_used": True}
                )
            ]
            
            # Mock sequential fallback
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential fallback success",
                    metadata={"meta_loop_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should succeed via meta-loop fallback
                assert result.success
                assert result.metadata.get("meta_loop_fallback", False)
    
    def test_meta_loop_preserves_deterministic_fallback_sequence(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that meta-loop fallback sequence is deterministic under concurrent failures."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True,
            "meta_loop_enabled": True,
            "max_attempts": 3
        }
        
        # Track execution order
        execution_order = []
        
        def mock_concurrent_with_tracking(*args, **kwargs):
            execution_order.append("concurrent")
            raise Exception("Concurrent failed")
        
        def mock_sequential_with_tracking(*args, **kwargs):
            execution_order.append("sequential")
            return OutreachPipelineResult(
                success=True,
                message="Sequential success",
                metadata={"deterministic_fallback": True}
            )
        
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async', side_effect=mock_concurrent_with_tracking):
            with patch.object(mock_orchestrator, '_execute_workflow_phases', side_effect=mock_sequential_with_tracking):
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should follow deterministic sequence: concurrent -> sequential
                assert execution_order == ["concurrent", "sequential"]
                assert result.success
                assert result.metadata.get("deterministic_fallback", False)
    
    def test_meta_loop_respects_concurrency_limits_during_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that meta-loop respects concurrency limits during fallback execution."""
        config = {
            "use_concurrent_research": True,
            "max_parallel_research": 1,
            "meta_loop_enabled": True,
            "max_attempts": 2
        }
        
        # Mock concurrent execution to exceed limits
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = Exception("Parallel limit exceeded")
            
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential within limits",
                    metadata={"parallel_limit_respected": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential within limits
                assert result.success
                assert result.metadata.get("parallel_limit_respected", False)
    
    def test_meta_loop_handles_partial_concurrent_research_failure(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test meta-loop behavior when concurrent research partially fails."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "meta_loop_enabled": True
        }
        
        # Mock partial concurrent failure
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = Mock(
                company={"company": "test_company"},  # Success
                contact={}  # Failure
            )
            
            # Meta-loop should handle partial failure gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should succeed with available research
            assert result.success
            assert result.metadata.get("partial_concurrent_handled", False)
    
    def test_meta_loop_concurrent_draft_failure_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test meta-loop fallback when concurrent multi-draft generation fails."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3,
            "meta_loop_enabled": True
        }
        
        # Mock multi-draft concurrent failure
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.side_effect = Exception("Concurrent draft generation failed")
            
            # Mock sequential draft fallback
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential draft success",
                    metadata={"draft_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential draft generation
                assert result.success
                assert result.metadata.get("draft_fallback", False)
    
    def test_meta_loop_concurrent_execution_state_persistence(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that meta-loop maintains state persistence across concurrent execution attempts."""
        config = {
            "use_concurrent_research": True,
            "meta_loop_enabled": True,
            "max_attempts": 3
        }
        
        # Mock state tracking
        meta_loop_state = MockMetaLoopState(attempt_count=0, fallback_triggered=False)
        
        def mock_concurrent_with_state(*args, **kwargs):
            meta_loop_state.attempt_count += 1
            if meta_loop_state.attempt_count < 2:
                raise Exception(f"Attempt {meta_loop_state.attempt_count} failed")
            return OutreachPipelineResult(
                success=True,
                message="Success after retries",
                metadata={"attempts": meta_loop_state.attempt_count}
            )
        
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async', side_effect=mock_concurrent_with_state):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should track attempts across meta-loop execution
            assert result.success
            assert result.metadata.get("attempts", 0) == 2
    
    def test_meta_loop_concurrent_safety_integration(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test meta-loop integration with safety validation during concurrent execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True,
            "meta_loop_enabled": True,
            "max_attempts": 2
        }
        
        # Mock safety to fail on first attempt, pass on second
        safety_attempts = [False, True]
        safety_call_count = 0
        
        def mock_safety_with_retry(*args, **kwargs):
            nonlocal safety_call_count
            safety_call_count += 1
            return Mock(
                passed=safety_attempts[min(safety_call_count - 1, len(safety_attempts) - 1)],
                findings=[] if safety_attempts[min(safety_call_count - 1, len(safety_attempts) - 1)] else ["safety_issue"]
            )
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_with_retry
        
        # Mock concurrent execution to succeed
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.return_value = OutreachPipelineResult(
                success=True,
                message="Concurrent success",
                metadata={"concurrent_executed": True}
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should succeed after safety retry via meta-loop
            assert result.success
            assert safety_call_count >= 1
    
    def test_meta_loop_concurrent_timeout_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test meta-loop handling of concurrent execution timeouts."""
        config = {
            "use_concurrent_research": True,
            "concurrent_timeout": 1.0,
            "meta_loop_enabled": True
        }
        
        # Mock concurrent execution to timeout
        async def mock_concurrent_timeout(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return OutreachPipelineResult(success=True, message="Too late")
        
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async', side_effect=mock_concurrent_timeout):
            # Mock sequential fallback for timeout
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential after timeout",
                    metadata={"timeout_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential on timeout
                assert result.success
                assert result.metadata.get("timeout_fallback", False)
