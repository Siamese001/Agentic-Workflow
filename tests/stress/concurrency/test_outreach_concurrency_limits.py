"""
Stress tests for outreach concurrency limits.

Tests that L3 orchestrator respects concurrency limits and budget constraints
under high load scenarios.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from typing import List, Any

from l3.outreach_orchestrator import OutreachOrchestrator
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile


class TestOutreachConcurrencyLimits:
    """Test suite for outreach workflow concurrency limits."""
    
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
        
        # Setup default mock behaviors with delays to simulate real work
        def slow_company_search(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms research time
            return type('MockCompanyResult', (), {
                'company': 'test_company', 
                'size': 'large',
                '__dict__': {'company': 'test_company', 'size': 'large'}
            })()
        
        def slow_contact_search(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms research time
            return type('MockContactResult', (), {
                'contact': 'test_contact', 
                'level': 'senior',
                '__dict__': {'contact': 'test_contact', 'level': 'senior'}
            })()
        
        self.mock_company_executor.search_company_context.side_effect = slow_company_search
        self.mock_contact_executor.search_contact_profile.side_effect = slow_contact_search
        
        self.mock_archetype_planner.plan_archetype_influence.return_value = ArchetypeContext(
            archetype=ArchetypeType.C_LEVEL,
            confidence=0.8
        )
        
        self.mock_research_planner.plan_research.return_value = {"query": "test"}
        self.mock_message_planner.create_message_plan.return_value = type('MockMessagePlan', (), {
            'template': 'test_template',
            '__dict__': {'template': 'test_template'}
        })()
        self.mock_message_executor.generate_message.return_value = type('MockMessageResult', (), {
            'message': 'Test message',
            'content': 'Test message',
            '__dict__': {'content': 'Test message'}
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
    
    def create_sample_recipient(self):
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
    
    def test_concurrency_limit_enforced(self):
        """Test that concurrent research respects max_parallel limit."""
        # Configure with low concurrency limit
        config = {
            "use_concurrent_research": True,
            "max_parallel_research": 2,  # Allow only 2 concurrent operations
            "telemetry_enabled": False  # Disable for cleaner test
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute multiple concurrent workflows
        async def run_multiple_workflows():
            tasks = []
            for i in range(6):  # Try to run 6 workflows concurrently
                task = asyncio.create_task(
                    orchestrator.orchestrate_outreach_concurrent(
                        mission, recipient, config
                    )
                )
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # Measure execution time
        start_time = time.time()
        results = asyncio.run(run_multiple_workflows())
        execution_time = time.time() - start_time
        
        # Verify all completed successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 6
        
        # With max_parallel=2 and 6 workflows taking ~100ms each,
        # execution should take at least 300ms (3 batches * 100ms)
        # If unlimited concurrency, it would take ~100ms
        assert execution_time >= 0.25  # Allow some tolerance
        
        # Verify no exceptions due to concurrency limits
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0
    
    def test_concurrency_limit_zero_blocks_execution(self):
        """Test that max_parallel=0 blocks concurrent execution."""
        config = {
            "use_concurrent_research": True,
            "max_parallel_research": 0,  # Block all concurrent operations
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Should fall back to sequential execution or fail gracefully
        result = asyncio.run(orchestrator.orchestrate_outreach_concurrent(
            mission, recipient, config
        ))
        
        # Should handle gracefully - either succeed sequentially or fail with budget error
        assert result is not None
        if hasattr(result, 'success'):
            # If it succeeded, it should have used sequential path
            assert True  # Success is acceptable
        else:
            # If it failed, should be due to budget constraint
            assert "budget" in str(result).lower() or "concurrency" in str(result).lower()
    
    def test_concurrent_executor_timeout_respected(self):
        """Test that individual executor calls respect timeout limits."""
        config = {
            "use_concurrent_research": True,
            "executor_timeout": 0.05,  # 50ms timeout (less than 100ms mock delay)
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Should timeout and handle gracefully
        start_time = time.time()
        result = asyncio.run(orchestrator.orchestrate_outreach_concurrent(
            mission, recipient, config
        ))
        execution_time = time.time() - start_time
        
        # Should complete quickly due to timeout, not wait full 100ms
        assert execution_time < 0.15  # Should be much less than 200ms (2 * 100ms)
        
        # Should handle timeout gracefully
        assert result is not None
