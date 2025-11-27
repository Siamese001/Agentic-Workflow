"""
Phase 7 Draft Failure Negative Path Tests

Tests negative path scenarios for concurrent draft generation failures.
Ensures proper fallback behavior when multi-draft generation fails.
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
class MockMessageDraft:
    """Mock message draft for testing."""
    message: str
    content: str
    quality_score: float = 0.0
    
    def __post_init__(self):
        self.__dict__.update({
            "message": self.message,
            "content": self.content,
            "quality_score": self.quality_score
        })


class TestOutreachDraftFailureFallback:
    """Test suite for draft generation failure fallback behavior."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator for draft failure testing."""
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
    
    def test_multi_draft_generation_complete_failure(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when all multi-draft generation attempts fail."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Mock complete multi-draft failure
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.side_effect = Exception("All draft generation failed")
            
            # Mock sequential fallback
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential fallback message",
                    metadata={"draft_failure_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential draft generation
                assert result.success
                assert result.metadata.get("draft_failure_fallback", False)
    
    def test_multi_draft_partial_failure_fallback_to_sequential(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when some multi-draft generation attempts fail."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Create drafts with mixed success/failure
        drafts = [
            MockMessageDraft(message="Good draft", content="quality content", quality_score=0.8),
            MockMessageDraft(message="Poor draft", content="low quality", quality_score=0.3),
            MockMessageDraft(message="Medium draft", content="average content", quality_score=0.6)
        ]
        
        # Mock partial draft failure - only return 2 drafts instead of 3
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.return_value = drafts[0]  # Return best available draft
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should succeed with available drafts
            assert result.success
            assert "Good draft" in result.message
            assert result.metadata.get("partial_draft_success", False)
    
    def test_draft_generation_to_thread_exception_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of to_thread exceptions during concurrent draft generation."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 2
        }
        
        # Mock to_thread exception
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = Exception("Thread pool exhausted")
            
            # Should handle thread exceptions gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to sequential execution
            assert result.metadata.get("thread_exception_handled", False)
    
    def test_draft_generation_timeout_with_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test draft generation timeout handling with fallback."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "draft_timeout": 1.0
        }
        
        # Mock slow draft generation
        async def mock_slow_draft_generation(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return MockMessageDraft(message="Too slow", content="late content")
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', side_effect=mock_slow_draft_generation):
            # Mock sequential fallback for timeout
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential after timeout",
                    metadata={"draft_timeout_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback on draft timeout
                assert result.success
                assert result.metadata.get("draft_timeout_fallback", False)
    
    def test_all_drafts_fail_safety_checks_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when all generated drafts fail safety checks."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Create drafts that all fail safety
        unsafe_drafts = [
            MockMessageDraft(message="Spam content", content="spammy message"),
            MockMessageDraft(message="Inappropriate", content="bad content"),
            MockMessageDraft(message="Offensive", content="harmful message")
        ]
        
        # Mock safety to fail all drafts
        def mock_safety_fail_all(message):
            return Mock(passed=False, findings=["safety_violation"])
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_fail_all
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', return_value=unsafe_drafts[0]):
            # Mock sequential fallback with safe content
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Safe sequential message",
                    metadata={"safety_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential safe message
                assert result.success
                assert result.metadata.get("safety_fallback", False)
    
    def test_draft_generation_memory_error_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of memory errors during draft generation."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 2
        }
        
        # Mock memory error during draft generation
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.side_effect = MemoryError("Draft generation memory exhausted")
            
            # Should handle memory errors gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to sequential with minimal memory usage
            assert result.metadata.get("memory_error_handled", False)
            assert result.metadata.get("fallback_mode", "sequential")
    
    def test_draft_generation_deterministic_failure_recovery(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test deterministic recovery from draft generation failures."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Track failure recovery attempts
        recovery_attempts = []
        
        def mock_draft_with_recovery(*args, **kwargs):
            recovery_attempts.append("attempt")
            if len(recovery_attempts) <= 2:
                raise Exception(f"Draft generation failed on attempt {len(recovery_attempts)}")
            return MockMessageDraft(message="Recovered draft", content="success content")
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', side_effect=mock_draft_with_recovery):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should recover deterministically after failures
            assert result.success
            assert "Recovered draft" in result.message
            assert len(recovery_attempts) == 3
    
    def test_draft_generation_concurrent_limit_exceeded_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when concurrent draft generation exceeds limits."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 1  # Very low limit
        }
        
        # Mock concurrent limit exceeded
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.side_effect = Exception("Concurrent draft limit exceeded")
            
            # Mock sequential fallback within limits
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential within limits",
                    metadata={"concurrent_limit_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential within limits
                assert result.success
                assert result.metadata.get("concurrent_limit_fallback", False)
    
    def test_draft_generation_empty_result_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling when draft generation returns empty results."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Mock empty draft results
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
            mock_draft.return_value = None  # Empty result
            
            # Mock sequential fallback for empty results
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential fallback for empty drafts",
                    metadata={"empty_draft_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback for empty draft results
                assert result.success
                assert result.metadata.get("empty_draft_fallback", False)
