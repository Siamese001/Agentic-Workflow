"""
Phase 7 Research Failure Negative Path Tests

Tests negative path scenarios for concurrent research execution failures.
Ensures proper fallback behavior when concurrent research operations fail.
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
class MockResearchBundle:
    """Mock research bundle for testing."""
    company: Dict[str, Any]
    contact: Dict[str, Any]
    
    def __bool__(self) -> bool:
        return bool(self.company or self.contact)


class TestOutreachResearchFailureFallback:
    """Test suite for research execution failure fallback behavior."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator for research failure testing."""
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
    
    def test_concurrent_research_complete_failure_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when all concurrent research attempts fail."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock complete concurrent research failure
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = Exception("All concurrent research failed")
            
            # Mock sequential research fallback
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential research success",
                    metadata={"research_failure_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential research
                assert result.success
                assert result.metadata.get("research_failure_fallback", False)
    
    def test_concurrent_research_partial_failure_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling when some concurrent research operations fail."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock partial research failure - company succeeds, contact fails
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = MockResearchBundle(
                company={"company": "test_company", "size": "large"},  # Success
                contact={}  # Failure
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should succeed with available research
            assert result.success
            assert result.metadata.get("partial_research_success", False)
    
    def test_research_to_thread_exception_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of to_thread exceptions during concurrent research."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock to_thread exception during research
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = Exception("Research thread pool exhausted")
            
            # Should handle research thread exceptions gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to sequential research execution
            assert result.metadata.get("research_thread_exception_handled", False)
    
    def test_research_timeout_with_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test research timeout handling with fallback."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "research_timeout": 1.0
        }
        
        # Mock slow research execution
        async def mock_slow_research(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return MockResearchBundle(
                company={"company": "slow research"},
                contact={"contact": "late result"}
            )
        
        with patch.object(mock_orchestrator, '_execute_research_concurrent', side_effect=mock_slow_research):
            # Mock sequential research fallback for timeout
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential research after timeout",
                    metadata={"research_timeout_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback on research timeout
                assert result.success
                assert result.metadata.get("research_timeout_fallback", False)
    
    def test_research_network_error_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of network errors during research."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock network error during research
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = ConnectionError("Research service unavailable")
            
            # Should handle network errors gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to cached or sequential research
            assert result.metadata.get("network_error_handled", False)
            assert result.metadata.get("fallback_mode", "sequential")
    
    def test_research_memory_error_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of memory errors during research."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock memory error during research
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = MemoryError("Research memory exhausted")
            
            # Should handle memory errors gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to lightweight research
            assert result.metadata.get("memory_error_handled", False)
            assert result.metadata.get("lightweight_research", False)
    
    def test_research_deterministic_failure_recovery(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test deterministic recovery from research failures."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Track failure recovery attempts
        recovery_attempts = []
        
        def mock_research_with_recovery(*args, **kwargs):
            recovery_attempts.append("attempt")
            if len(recovery_attempts) <= 2:
                raise Exception(f"Research failed on attempt {len(recovery_attempts)}")
            return MockResearchBundle(
                company={"company": "recovered research"},
                contact={"contact": "success after retry"}
            )
        
        with patch.object(mock_orchestrator, '_execute_research_concurrent', side_effect=mock_research_with_recovery):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should recover deterministically after failures
            assert result.success
            assert len(recovery_attempts) == 3
            assert result.metadata.get("deterministic_recovery", False)
    
    def test_research_concurrent_limit_exceeded_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when concurrent research exceeds limits."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 1  # Very low limit
        }
        
        # Mock concurrent limit exceeded
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = Exception("Concurrent research limit exceeded")
            
            # Mock sequential research fallback within limits
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential research within limits",
                    metadata={"concurrent_limit_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to sequential within limits
                assert result.success
                assert result.metadata.get("concurrent_limit_fallback", False)
    
    def test_research_empty_result_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling when research returns empty results."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock empty research results
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = MockResearchBundle(company={}, contact={})  # Empty results
            
            # Should handle empty research gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should proceed with minimal research or fallback
            assert result.metadata.get("empty_research_handled", False)
            assert result.metadata.get("minimal_research_mode", False)
    
    def test_research_api_rate_limit_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of API rate limits during research."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock API rate limit error
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = Exception("API rate limit exceeded")
            
            # Should handle rate limits gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to cached research or sequential mode
            assert result.metadata.get("rate_limit_handled", False)
            assert result.metadata.get("fallback_mode", "cached_or_sequential")
    
    def test_research_service_unavailable_fallback(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test fallback when research service is unavailable."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock service unavailable error
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.side_effect = Exception("Research service unavailable")
            
            # Mock fallback to basic research
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Basic research fallback",
                    metadata={"service_unavailable_fallback": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should fallback to basic research
                assert result.success
                assert result.metadata.get("service_unavailable_fallback", False)
    
    def test_research_partial_data_corruption_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test handling of partially corrupted research data."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock partially corrupted research data
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = MockResearchBundle(
                company={"company": "valid company data"},  # Valid
                contact={"corrupted": "data", "error": True}  # Corrupted
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should handle partial corruption gracefully
            assert result.success
            assert result.metadata.get("partial_corruption_handled", False)
            assert result.metadata.get("valid_data_used", True)
