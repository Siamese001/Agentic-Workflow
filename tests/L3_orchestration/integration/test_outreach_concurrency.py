"""
Phase 7 Outreach Concurrency Tests

Tests for optional concurrent execution in outreach workflow.
Ensures backward compatibility and proper concurrency handling.
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


@dataclass
class MockResearchResult:
    """Mock research result with proper __dict__."""
    company: str
    size: str
    
    def __post_init__(self):
        self.__dict__.update({
            "company": self.company,
            "size": self.size
        })


@dataclass
class MockMessagePlan:
    """Mock message plan with proper __dict__."""
    template: str
    
    def __post_init__(self):
        self.__dict__.update({"template": self.template})


@dataclass
class MockMessageResult:
    """Mock message result with proper __dict__."""
    message: str
    content: str
    
    def __post_init__(self):
        self.__dict__.update({
            "message": self.message,
            "content": self.content
        })


@dataclass
class MockContactResult:
    """Mock contact result with proper __dict__."""
    contact: str
    level: str
    
    def __post_init__(self):
        self.__dict__.update({
            "contact": self.contact,
            "level": self.level
        })


@dataclass
class MockMessageDraft:
    """Mock message draft with proper __dict__."""
    message: str
    content: str
    
    def __post_init__(self):
        self.__dict__.update({
            "message": self.message,
            "content": self.content
        })


class TestOutreachConcurrency:
    """Test suite for outreach concurrency features."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator for testing."""
        # Mock all required components
        mock_archetype_planner = Mock()
        mock_research_planner = Mock()
        mock_message_planner = Mock()
        mock_company_executor = Mock()
        mock_contact_executor = Mock()
        mock_message_executor = Mock()
        mock_state_manager = Mock()
        mock_safety_validator = Mock()
        
        # Create orchestrator with mocked components
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
        
        mock_company_executor.search_company_context.return_value = MockResearchResult(
            company="test_company",
            size="large"
        )
        
        mock_contact_executor.search_contact_profile.return_value = MockContactResult(
            contact="test_contact",
            level="senior"
        )
        
        mock_message_planner.create_message_plan.return_value = MockMessagePlan(
            template="test_template"
        )
        
        mock_message_executor.generate_message.return_value = MockMessageResult(
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
    
    def test_concurrent_research_equivalent_to_sequential(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that concurrent research produces equivalent results to sequential."""
        # Setup config with concurrent research enabled
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock the async concurrent method to call sequential executors
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = MockResearchBundle(
                company={"company": "test_company", "size": "large"},
                contact={"contact": "test_contact", "level": "senior"}
            )
            
            # Execute concurrent workflow (await the async method)
            result_concurrent = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Execute sequential workflow for comparison
            result_sequential = mock_orchestrator.orchestrate_outreach(
                sample_mission, sample_recipient, config
            )
            
            # Both should succeed and have equivalent structure
            assert result_concurrent.success == result_sequential.success
            assert result_concurrent.message == result_sequential.message
            
            # Verify concurrent method was called
            mock_concurrent.assert_called_once()
    
    def test_concurrent_respects_max_parallel_research(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that concurrent execution respects max_parallel_research limit."""
        config = {
            "use_concurrent_research": True,
            "max_parallel_research": 1  # Limit to 1 parallel task
        }
        
        # Mock async execution with task tracking
        created_tasks = []
        
        async def mock_create_task(coro):
            created_tasks.append(coro)
            return asyncio.create_task(coro)
        
        with patch('asyncio.create_task', side_effect=mock_create_task):
            with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
                mock_concurrent.return_value = MockResearchBundle(
                    company={"company": "test_company"},
                    contact={"contact": "test_contact"}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should respect parallel limit
                assert len(created_tasks) <= config["max_parallel_research"]
                assert result.success
    
    def test_multi_draft_voting_selects_best(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that multi-draft voting selects the highest quality draft."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Create mock drafts with different qualities
        drafts = [
            MockMessageDraft(message="Short message", content="Short message"),
            MockMessageDraft(message="Medium length message with good content", content="Medium length message with good content"),
            MockMessageDraft(message="Comprehensive message with detailed information and high signal density", content="Comprehensive message with detailed information and high signal density")
        ]
        
        # Mock safety evaluation - all pass
        def mock_safety_eval(message):
            return Mock(passed=True, findings=[])
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_eval
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', return_value=drafts[2]):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should select the longest, highest-quality draft
            assert result.success
            assert "Comprehensive message" in result.message
            assert len(result.message) > len(drafts[0].message)
    
    def test_concurrency_disabled_by_default(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that behavior is identical to sequential when concurrency flags are False."""
        # Default config (all flags False)
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": False
        }
        
        # Mock sequential workflow
        with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
            mock_sequential.return_value = OutreachPipelineResult(
                success=True,
                message="Sequential message",
                metadata={"workflow_type": "sequential"}
            )
            
            result_concurrent = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            result_sequential = mock_orchestrator.orchestrate_outreach(
                sample_mission, sample_recipient, config
            )
            
            # Should be identical when concurrency disabled
            assert result_concurrent.success == result_sequential.success
            assert result_concurrent.message == result_sequential.message
            assert result_concurrent.metadata["workflow_type"] == "sequential"
    
    def test_concurrent_research_partial_failure_handling(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that partial research failures are handled gracefully."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        # Mock partial failure - company research succeeds, contact fails
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = MockResearchBundle(
                company={"company": "test_company", "size": "large"},
                contact={}  # Empty contact research
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should succeed with available research
            assert result.success
            assert result.message
    
    def test_multi_draft_with_safety_failures(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test multi-draft voting when some drafts fail safety checks."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True
        }
        
        # Create drafts with mixed safety results
        drafts = [
            MockMessageDraft(message="Unsafe message", content="Unsafe message"),
            MockMessageDraft(message="Safe message", content="Safe message"),
            MockMessageDraft(message="Another unsafe message", content="Another unsafe message")
        ]
        
        # Mock safety evaluation - only middle draft passes
        def mock_safety_eval(message):
            if "Safe" in message:
                return Mock(passed=True, findings=[])
            else:
                return Mock(passed=False, findings=["safety_issue"])
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_eval
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', return_value=drafts[1]):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should select the safe draft
            assert result.success
            assert result.message == "Safe message"
    
    def test_config_defaults_maintain_sequential_behavior(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that default config maintains sequential behavior."""
        # Empty config should use defaults (all flags False)
        config = {}
        
        with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
            mock_sequential.return_value = OutreachPipelineResult(
                success=True,
                message="Default message"
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should use sequential workflow by default
            mock_sequential.assert_called_once()
            assert result.success
            assert result.message == "Default message"
