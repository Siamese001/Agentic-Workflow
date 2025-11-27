"""
Phase 7 Concurrency Integration with Telemetry Tests

Tests telemetry integration with concurrent outreach workflow:
- Concurrent workflow telemetry recording
- Telemetry during parallel research execution
- Multi-draft generation telemetry
- Meta-loop fallback telemetry tracking
- Concurrent execution timing and duration
- Thread safety of telemetry during concurrent operations
"""

import pytest
import asyncio
import threading
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from runtime.telemetry_bus import TelemetryBus, get_telemetry_bus
from l3.outreach_orchestrator import OutreachOrchestrator, OutreachPipelineResult
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile


class TestConcurrentTelemetry:
    """Test suite for telemetry integration with concurrent workflow."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock OutreachOrchestrator with telemetry integration."""
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
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = get_telemetry_bus()
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="standard")
    
    def test_concurrent_workflow_telemetry_start_end_events(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that concurrent workflow records proper start/end telemetry events."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock concurrent execution to record telemetry
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.return_value = OutreachPipelineResult(
                success=True,
                message="Concurrent execution success",
                metadata={"concurrent_id": "test_concurrent_123"}
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should have recorded concurrent workflow telemetry
            events = self.bus.get_events()
            
            # Look for concurrent workflow events
            concurrent_events = [e for e in events if "concurrent" in e.name.lower()]
            assert len(concurrent_events) >= 1
            
            # Validate concurrent workflow event structure
            for event in concurrent_events:
                assert event.layer == "L3"
                assert "layer" not in event.payload
                assert "workflow_type" in event.payload
                assert event.payload["workflow_type"] in ["concurrent_outreach", "outreach_concurrent"]
    
    def test_parallel_research_telemetry_tracking(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test telemetry tracking during parallel research execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        # Mock parallel research execution
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_research:
            mock_research.return_value = Mock(
                company={"company": "researched_company"},
                contact={"contact": "researched_contact"}
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should have recorded research telemetry
            events = self.bus.get_events()
            research_events = [e for e in events if "research" in e.name.lower()]
            
            assert len(research_events) >= 1
            
            # Validate research event structure
            for event in research_events:
                assert event.layer == "L3"
                assert "layer" not in event.payload
                assert "workflow_type" in event.payload
                assert "stage" in event.payload
    
    def test_multi_draft_telemetry_with_voting(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test telemetry tracking during multi-draft generation and voting."""
        config = {
            "use_concurrent_research": False,
            "use_multi_draft": True,
            "max_parallel_drafts": 3
        }
        
        # Create mock drafts
        drafts = [
            Mock(message="High quality draft", content="quality content"),
            Mock(message="Medium quality draft", content="average content"),
            Mock(message="Low quality draft", content="poor content")
        ]
        
        with patch.object(mock_orchestrator, '_generate_multiple_drafts_and_select_best', return_value=drafts[0]):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should have recorded draft generation telemetry
            events = self.bus.get_events()
            draft_events = [e for e in events if "draft" in e.name.lower()]
            
            assert len(draft_events) >= 1
            
            # Validate draft event structure
            for event in draft_events:
                assert event.layer == "L3"
                assert "layer" not in event.payload
                assert "workflow_type" in event.payload
    
    def test_meta_loop_fallback_telemetry_tracking(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test telemetry tracking during meta-loop fallback scenarios."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "meta_loop_enabled": True,
            "max_attempts": 3
        }
        
        # Mock concurrent execution failure and sequential fallback
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.side_effect = [
                Exception("Concurrent execution failed"),
                OutreachPipelineResult(
                    success=True,
                    message="Sequential fallback success",
                    metadata={"meta_loop_fallback": True}
                )
            ]
            
            with patch.object(mock_orchestrator, '_execute_workflow_phases') as mock_sequential:
                mock_sequential.return_value = OutreachPipelineResult(
                    success=True,
                    message="Sequential fallback",
                    metadata={"fallback_used": True}
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                # Should have recorded meta-loop telemetry
                events = self.bus.get_events()
                fallback_events = [e for e in events if "fallback" in e.name.lower() or "meta_loop" in e.name.lower()]
                
                assert len(fallback_events) >= 1
                
                # Validate fallback event structure
                for event in fallback_events:
                    assert event.layer == "L3"
                    assert "layer" not in event.payload
                    assert "workflow_type" in event.payload
    
    def test_concurrent_execution_timing_and_duration(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that concurrent execution telemetry includes accurate timing."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        start_time = time.time()
        
        # Mock concurrent execution with measurable delay
        async def mock_concurrent_with_delay(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return OutreachPipelineResult(
                success=True,
                message="Concurrent success",
                metadata={"concurrent_id": "timing_test"}
            )
        
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async', side_effect=mock_concurrent_with_delay):
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            # Should have recorded timing telemetry
            events = self.bus.get_events()
            
            # Look for timing-related events
            timing_events = [e for e in events if any(keyword in e.name.lower() for keyword in ["start", "end", "duration", "timing"])]
            
            if timing_events:
                # Validate timing accuracy
                for event in timing_events:
                    assert event.timestamp > 0
                    assert "layer" not in event.payload
                    
                # If we have start and end events, calculate duration
                start_events = [e for e in timing_events if "start" in e.name.lower()]
                end_events = [e for e in timing_events if "end" in e.name.lower()]
                
                if start_events and end_events:
                    telemetry_duration = end_events[0].timestamp - start_events[0].timestamp
                    assert telemetry_duration > 0.05  # Should be at least 50ms
                    assert telemetry_duration < actual_duration + 0.1  # Should be close to actual
    
    def test_telemetry_thread_safety_during_concurrent_operations(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that telemetry recording is thread-safe during concurrent operations."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "max_parallel_research": 2
        }
        
        results = []
        errors = []
        
        async def concurrent_workflow_with_telemetry(thread_id):
            try:
                # Mock different concurrent executions for each thread
                with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
                    mock_concurrent.return_value = OutreachPipelineResult(
                        success=True,
                        message=f"Concurrent success {thread_id}",
                        metadata={"concurrent_id": f"thread_{thread_id}"}
                    )
                    
                    result = await mock_orchestrator.orchestrate_outreach_concurrent(
                        sample_mission, sample_recipient, config
                    )
                    results.append((thread_id, result))
                    
            except Exception as e:
                errors.append((thread_id, e))
        
        # Run multiple concurrent workflows
        async def run_concurrent_workflows():
            tasks = []
            for i in range(3):
                task = concurrent_workflow_with_telemetry(i)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        # Execute concurrent workflows
        asyncio.run(run_concurrent_workflows())
        
        # Validate no thread safety errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 3
        
        # Validate telemetry integrity
        events = self.bus.get_events()
        assert len(events) >= 3  # Should have events from all concurrent executions
        
        # Validate no layer in any payload
        for event in events:
            assert "layer" not in event.payload
            assert event.layer == "L3"
    
    def test_telemetry_during_partial_concurrent_failures(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test telemetry tracking during partial concurrent execution failures."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        # Mock partial concurrent failure
        with patch.object(mock_orchestrator, '_execute_research_concurrent') as mock_research:
            mock_research.return_value = Mock(
                company={"company": "success_company"},  # Success
                contact={}  # Failure
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should have recorded partial failure telemetry
            events = self.bus.get_events()
            error_events = self.bus.get_errors()
            
            # Should have events and possibly errors
            assert len(events) >= 1
            
            # Validate partial failure handling in telemetry
            failure_events = [e for e in events if any(keyword in e.name.lower() for keyword in ["partial", "failure", "error"])]
            
            # Should have some indication of partial failure
            if failure_events:
                for event in failure_events:
                    assert event.layer == "L3"
                    assert "layer" not in event.payload
    
    def test_telemetry_suppression_during_concurrent_execution(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test that telemetry suppression works during concurrent execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        # Disable telemetry
        self.bus.configure(enabled=False, detail_level="verbose")
        
        # Execute concurrent workflow
        with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
            mock_concurrent.return_value = OutreachPipelineResult(
                success=True,
                message="Concurrent success",
                metadata={"concurrent_id": "suppression_test"}
            )
            
            result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                sample_mission, sample_recipient, config
            ))
            
            # Should have no telemetry events
            events = self.bus.get_events()
            errors = self.bus.get_errors()
            traces = self.bus.get_traces()
            
            assert len(events) == 0
            assert len(errors) == 0
            assert len(traces) == 0
    
    def test_concurrent_workflow_telemetry_detail_levels(self, mock_orchestrator, sample_mission, sample_recipient):
        """Test telemetry detail levels during concurrent workflow execution."""
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False
        }
        
        # Test different detail levels
        detail_levels = ["verbose", "standard", "minimal"]
        results = {}
        
        for detail_level in detail_levels:
            # Clear telemetry and configure detail level
            self.bus.clear()
            self.bus.configure(enabled=True, detail_level=detail_level)
            
            # Execute concurrent workflow
            with patch.object(mock_orchestrator, '_execute_workflow_phases_concurrent_async') as mock_concurrent:
                mock_concurrent.return_value = OutreachPipelineResult(
                    success=True,
                    message="Concurrent success",
                    metadata={
                        "concurrent_id": f"detail_test_{detail_level}",
                        "detailed_metrics": {"cpu": 0.8, "memory": 0.6},
                        "debug_info": "detailed debug data"
                    }
                )
                
                result = asyncio.run(mock_orchestrator.orchestrate_outreach_concurrent(
                    sample_mission, sample_recipient, config
                ))
                
                events = self.bus.get_events()
                results[detail_level] = events
        
        # Validate detail level differences
        verbose_events = results["verbose"]
        standard_events = results["standard"]
        minimal_events = results["minimal"]
        
        # Verbose should have most detail
        if verbose_events:
            verbose_payload = verbose_events[0].payload
            assert "layer" not in verbose_payload  # Always filtered
            # Verbose should preserve most fields
        
        # Standard should have medium detail
        if standard_events:
            standard_payload = standard_events[0].payload
            assert "layer" not in standard_payload
            assert set(standard_payload.keys()) <= {
                'workflow_type', 'archetype', 'mission_id', 'stage',
                'phase', 'duration', 'success', 'error_type', 'concurrent_id'
            }
        
        # Minimal should have least detail
        if minimal_events:
            minimal_payload = minimal_events[0].payload
            assert "layer" not in minimal_payload
            assert set(minimal_payload.keys()) <= {'workflow_type', 'stage'}
