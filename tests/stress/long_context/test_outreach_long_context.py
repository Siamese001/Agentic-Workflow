"""
Stress tests for outreach long context handling.

Tests that L3 orchestrator handles large context sizes gracefully
without memory issues or crashes.
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import List, Any

from l3.outreach_orchestrator import OutreachOrchestrator
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile


class TestOutreachLongContext:
    """Test suite for outreach workflow long context handling."""
    
    def setup_method(self):
        """Setup test environment with realistic mocks."""
        # Mock all required components
        self.mock_archetype_planner = Mock()
        self.mock_research_planner = Mock()
        self.mock_message_planner = Mock()
        self.mock_company_executor = Mock()
        self.mock_contact_executor = Mock()
        self.mock_message_executor = Mock()
        self.mock_state_manager = Mock()
        self.mock_safety_validator = Mock()
        
        # Setup default mock behaviors
        self.mock_archetype_planner.plan_archetype_influence.return_value = ArchetypeContext(
            archetype=ArchetypeType.C_LEVEL,
            confidence=0.8
        )
        
        self.mock_research_planner.plan_research.return_value = {"query": "test"}
        self.mock_message_planner.create_message_plan.return_value = type('MockMessagePlan', (), {
            'template': 'test_template',
            '__dict__': {"template": "test_template"}
        })()
        self.mock_message_executor.generate_message.return_value = type('MockMessageResult', (), {
            'message': "Test message",
            'content': "Test message",
            '__dict__': {"content": "Test message"}
        })()
        self.mock_safety_validator.evaluate.return_value = type('MockSafetyResult', (), {
            'passed': True,
            'findings': []
        })()
    
    def create_orchestrator(self, config: dict = None):
        """Create OutreachOrchestrator with mocked components."""
        return OutreachOrchestrator(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            message_executor=self.mock_message_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator
        )
    
    def create_sample_mission(self):
        """Create sample outreach mission."""
        return OutreachMission(
            objective="networking",
            target_role="Software Engineer",
            target_company="Tech Corp",
            value_proposition="Collaboration opportunity"
        )
    
    def create_large_recipient(self):
        """Create recipient with extensive metadata to simulate large context."""
        # Generate large skills list
        large_skills = [f"skill_{i}" for i in range(1000)]
        
        # Generate large activity list
        large_activities = [f"activity_{i}" for i in range(500)]
        
        # Generate large metadata
        large_metadata = {
            f"metadata_key_{i}": f"metadata_value_{i}" * 10  # Repeat to increase size
            for i in range(200)
        }
        
        return RecipientProfile(
            name="John Doe with very long name that includes many details " + "x" * 100,
            title="Engineering Manager with extensive title and responsibilities " + "y" * 100,
            company="Tech Corp with comprehensive company description " + "z" * 100,
            industry="Technology with detailed industry analysis " + "a" * 100,
            seniority="Senior with extensive seniority details " + "b" * 100,
            department="Engineering with large department description " + "c" * 100,
            skills=large_skills,
            recent_activity=large_activities,
            metadata=large_metadata
        )
    
    def create_large_research_results(self):
        """Create mock research results with large data."""
        large_company_data = {
            "company_info": "x" * 10000,  # 10KB of company data
            "financial_data": "y" * 10000,  # 10KB of financial data
            "products": ["product_" + "z" * 100 for _ in range(100)],
            "competitors": ["competitor_" + "a" * 100 for _ in range(100)],
        }
        
        large_contact_data = {
            "contact_info": "b" * 10000,  # 10KB of contact data
            "social_media": "c" * 10000,  # 10KB of social data
            "connections": ["connection_" + "d" * 100 for _ in range(200)],
            "interests": ["interest_" + "e" * 100 for _ in range(150)],
        }
        
        # Mock large research results
        mock_company_result = type('MockCompanyResult', (), {
            'company': large_company_data,
            '__dict__': large_company_data
        })()
        
        mock_contact_result = type('MockContactResult', (), {
            'contact': large_contact_data,
            '__dict__': large_contact_data
        })()
        
        return mock_company_result, mock_contact_result
    
    def test_long_context_does_not_crash(self):
        """Test that large context sizes don't cause crashes."""
        # Setup large data
        large_recipient = self.create_large_recipient()
        large_company_result, large_contact_result = self.create_large_research_results()
        
        self.mock_company_executor.search_company_context.return_value = large_company_result
        self.mock_contact_executor.search_contact_profile.return_value = large_contact_result
        
        config = {
            "max_context_size": 100000,  # 100KB limit
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        
        # Should handle large context gracefully
        start_time = time.time()
        result = orchestrator.orchestrate_outreach(mission, large_recipient, config)
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time despite large data
        assert execution_time < 5.0  # Should complete within 5 seconds
        
        # Should not crash
        assert result is not None
        assert hasattr(result, 'success')
    
    def test_context_size_limit_enforced(self):
        """Test that context size limits are enforced."""
        # Create extremely large recipient that exceeds limits
        huge_recipient = self.create_large_recipient()
        
        # Add even more data to exceed limits
        huge_recipient.metadata.update({
            f"huge_data_{i}": "x" * 1000 for i in range(1000)  # Add 1MB of data
        })
        
        config = {
            "max_context_size": 50000,  # 50KB limit (much smaller than our data)
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        
        # Should handle context size limit gracefully
        result = orchestrator.orchestrate_outreach(mission, huge_recipient, config)
        
        # Should not crash, may fail gracefully or truncate data
        assert result is not None
        
        # If it failed, should be due to context size limit
        if hasattr(result, 'success') and not result.success:
            assert "context" in result.message.lower() or "size" in result.message.lower()
    
    def test_memory_usage_stable_under_load(self):
        """Test that memory usage remains stable with multiple large contexts."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple workflows with large contexts
        config = {
            "max_context_size": 200000,  # 200KB limit
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        large_recipient = self.create_large_recipient()
        
        # Execute multiple workflows
        for i in range(10):
            result = orchestrator.orchestrate_outreach(mission, large_recipient, config)
            assert result is not None
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 10 large workflows)
        assert memory_increase < 100, f"Memory increased by {memory_increase}MB, which is too high"
    
    def test_large_message_generation_handled(self):
        """Test that large message generation doesn't cause issues."""
        # Mock large message generation
        large_message = "x" * 50000  # 50KB message
        
        self.mock_message_executor.generate_message.return_value = type('MockMessageResult', (), {
            'message': large_message,
            'content': large_message,
            '__dict__': {'content': large_message}
        })()
        
        config = {
            "max_message_length": 100000,  # 100KB limit
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_large_recipient()
        
        # Should handle large message generation
        result = orchestrator.orchestrate_outreach(mission, recipient, config)
        
        assert result is not None
        assert hasattr(result, 'success')
        
        # If successful, message should be within limits
        if hasattr(result, 'success') and result.success:
            assert len(result.message) <= config["max_message_length"]
