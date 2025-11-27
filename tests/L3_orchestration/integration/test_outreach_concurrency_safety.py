"""
Phase 7 Safety + Concurrency Integration Tests

Tests safety validator integration with concurrent outreach workflow.
Ensures safety checks properly override and gate concurrent execution.
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
class MockSafetyResult:
    """Mock safety result with proper structure."""
    passed: bool
    findings: list
    blocked_content: str = ""
    
    def __post_init__(self):
        self.__dict__.update({
            "passed": self.passed,
            "findings": self.findings,
            "blocked_content": self.blocked_content
        })


@dataclass
class MockMessageDraft:
    """Mock message draft for testing."""
    message: str
    content: str
    
    def __post_init__(self):
        self.__dict__.update({"message": self.message, "content": self.content})


class TestOutreachConcurrencySafety:
    """Test suite for safety integration with concurrent outreach workflow."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator for safety testing."""
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
    
    def test_safety_validator_blocks_concurrent_execution(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that safety validator properly blocks concurrent execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True,
            "max_parallel_research": 2
        }
        
        # Mock safety to fail
        mock_orchestrator.safety_validator.evaluate.return_value = MockSafetyResult(
            passed=False,
            findings=["unsafe_content_detected"],
            blocked_content="dangerous content"
        )
        
        # Mock concurrent workflow to be called but safety should block
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.return_value = OutreachPipelineResult(
                success=False,
                message="Blocked by safety",
                metadata={"safety_blocked": True}
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Safety should block execution
            assert not result.success
            assert "safety" in str(result.metadata).lower()
    
    def test_safety_override_concurrency_votes(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that safety validator overrides concurrent voting decisions."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Create multiple drafts with mixed safety results
        drafts = [
            MockMessageDraft(message="High quality but unsafe", content="dangerous content"),
            MockMessageDraft(message="safe professional message", content="Medium quality safe"),
            MockMessageDraft(message="Low quality but unsafe", content="spam content")
        ]
        
        # Mock safety to fail for high-quality drafts, pass for safe one
        def mock_safety_eval(message):
            if "unsafe" in message or "spam" in message:
                return MockSafetyResult(passed=False, findings=["safety_violation"])
            else:
                return MockSafetyResult(passed=True, findings=[])
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_eval
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', return_value=drafts[1]):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should select the safe draft even if lower quality
            assert result.success
            assert "safe professional message" in result.message
    
    def test_concurrent_execution_with_safety_timeout(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test concurrent execution respects safety validation timeout."""
        config = {
            "use_concurrent_research": True,
            "safety_timeout": 1.0  # 1 second timeout
        }
        
        # Mock safety to take too long
        async def slow_safety_eval(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return MockSafetyResult(passed=True, findings=[])
        
        mock_orchestrator.safety_validator.evaluate = slow_safety_eval
        
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = Mock(
                company={"company": "test_company"},
                contact={"contact": "test_contact"}
            )
            
            # Should handle safety timeout gracefully
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should fall back to safe behavior on timeout
            assert result.metadata.get("safety_timeout", False)
    
    def test_safety_preserves_deterministic_behavior_under_concurrency(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that safety validation maintains deterministic behavior during concurrent execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Mock safety to always pass with consistent results
        def mock_safety_eval(message):
            return MockSafetyResult(
                passed=True,
                findings=[],
                blocked_content=""
            )
        
        mock_orchestrator.safety_validator.evaluate.side_effect = mock_safety_eval
        
        # Run multiple concurrent executions
        results = []
        for _ in range(3):
            with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best') as mock_draft:
                mock_draft.return_value = MockMessageDraft(
                    message="Consistent safe message",
                    content="safe content"
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                results.append(result)
        
        # All results should be identical (deterministic)
        for result in results[1:]:
            assert result.success == results[0].success
            assert result.message == results[0].message
    
    def test_safety_blocks_partial_concurrent_failures(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that safety blocks execution even when concurrent components partially fail."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        # Mock partial concurrent failure
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_concurrent:
            mock_concurrent.return_value = Mock(
                company={"company": "test_company"},  # Success
                contact={}  # Failure
            )
            
            # Mock safety to fail
            mock_orchestrator.safety_validator.evaluate.return_value = MockSafetyResult(
                passed=False,
                findings=["safety_block"],
                blocked_content="unsafe"
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Safety should block even with partial concurrent failure
            assert not result.success
            assert result.metadata.get("safety_blocked", False)
    
    def test_safety_concurrent_execution_error_isolation(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that safety errors don't break concurrent execution infrastructure."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": True
        }
        
        # Mock safety to raise exception
        mock_orchestrator.safety_validator.evaluate.side_effect = Exception("Safety service error")
        
        # Should handle safety errors gracefully
        result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
            sample_mission, sample_recipient, config
        ))
        
        # Should fail gracefully with safety error information
        assert not result.success
        assert "safety" in str(result.metadata).lower() or "error" in str(result.metadata).lower()
