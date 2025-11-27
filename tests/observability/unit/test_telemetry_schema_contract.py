"""
Phase 8 Telemetry Schema Contract Tests

Tests that ensure telemetry payloads follow the correct schema:
- Layer is always a parameter, never included in payload
- Payload filtering respects detail levels correctly
- Telemetry events maintain consistent structure
- Schema violations are properly detected and handled
"""

import pytest
from unittest.mock import patch
from typing import Dict, Any

from runtime.telemetry_bus import (
    TelemetryBus,
    TelemetryEvent,
    TelemetryError,
    TelemetryTrace,
    get_telemetry_bus
)


class TestTelemetrySchemaContract:
    """Test suite for telemetry schema contract validation."""
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = TelemetryBus()
        self.bus.clear()
    
    def test_layer_is_parameter_not_in_payload_verbose(self):
        """Test that layer is a parameter, not included in payload at verbose level."""
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL", 
            "mission_id": "test_mission",
            "stage": "research",
            "duration": 1.5,
            "layer": "L3"  # This should be filtered out
        }
        
        self.bus.configure(enabled=True, detail_level="verbose")
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        event = events[0]
        # Layer should be in the event parameter, not payload
        assert event.layer == "L3"
        assert "layer" not in event.payload
        assert event.payload["workflow_type"] == "outreach"
        assert event.payload["archetype"] == "C_LEVEL"
    
    def test_layer_is_parameter_not_in_payload_standard(self):
        """Test that layer is filtered out from payload at standard detail level."""
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission", 
            "stage": "research",
            "duration": 1.5,
            "layer": "L3",  # Should be filtered out
            "extra_detail": "should be removed"
        }
        
        self.bus.configure(enabled=True, detail_level="standard")
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        event = events[0]
        # Layer should be parameter, not in payload
        assert event.layer == "L3"
        assert "layer" not in event.payload
        # Only allowed keys should remain
        assert set(event.payload.keys()) <= {
            'workflow_type', 'archetype', 'mission_id', 'stage', 
            'phase', 'duration', 'success', 'error_type'
        }
        assert "extra_detail" not in event.payload
    
    def test_layer_is_parameter_not_in_payload_minimal(self):
        """Test that layer is filtered out from payload at minimal detail level."""
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research", 
            "duration": 1.5,
            "layer": "L3",  # Should be filtered out
            "extra_detail": "should be removed"
        }
        
        self.bus.configure(enabled=True, detail_level="minimal")
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        event = events[0]
        # Layer should be parameter, not in payload
        assert event.layer == "L3"
        assert "layer" not in event.payload
        # Only essential keys should remain
        assert set(event.payload.keys()) <= {'workflow_type', 'stage'}
        assert "archetype" not in event.payload
        assert "mission_id" not in event.payload
        assert "duration" not in event.payload
    
    def test_error_recording_excludes_layer_from_context(self):
        """Test that error recording excludes layer from context payload."""
        context = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "layer": "L3",  # Should be filtered out
            "error_detail": "specific error info"
        }
        
        test_error = Exception("Test error")
        
        self.bus.configure(enabled=True, detail_level="standard")
        self.bus.record_error("phase_failed", "L3", test_error, context)
        
        errors = self.bus.get_errors()
        assert len(errors) == 1
        
        error = errors[0]
        # Layer should be parameter, not in context
        assert error.layer == "L3"
        assert "layer" not in error.context
        assert error.context["workflow_type"] == "outreach"
        assert "error_detail" not in error.context  # Filtered at standard level
    
    def test_trace_recording_preserves_all_data(self):
        """Test that trace recording preserves all data without filtering."""
        trace_data = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "layer": "L3",  # Should be preserved in traces
            "detailed_metrics": {"cpu": 0.8, "memory": 0.6},
            "step_timings": [1.0, 2.0, 1.5]
        }
        
        self.bus.configure(enabled=True, detail_level="minimal")
        self.bus.record_trace(trace_data)
        
        traces = self.bus.get_traces()
        assert len(traces) == 1
        
        trace = traces[0]
        # Traces should preserve all data including layer
        assert trace.trace["workflow_type"] == "outreach"
        assert trace.trace["layer"] == "L3"
        assert "detailed_metrics" in trace.trace
        assert "step_timings" in trace.trace
    
    def test_telemetry_enabled_suppresses_all_events(self):
        """Test that telemetry_enabled=False suppresses all event recording."""
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "stage": "research"
        }
        
        self.bus.configure(enabled=False, detail_level="verbose")
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 0
    
    def test_telemetry_enabled_suppresses_all_errors(self):
        """Test that telemetry_enabled=False suppresses all error recording."""
        test_error = Exception("Test error")
        context = {"workflow_type": "outreach"}
        
        self.bus.configure(enabled=False, detail_level="verbose")
        self.bus.record_error("phase_failed", "L3", test_error, context)
        
        errors = self.bus.get_errors()
        assert len(errors) == 0
    
    def test_telemetry_enabled_suppresses_all_traces(self):
        """Test that telemetry_enabled=False suppresses all trace recording."""
        trace_data = {"workflow_type": "outreach"}
        
        self.bus.configure(enabled=False, detail_level="verbose")
        self.bus.record_trace(trace_data)
        
        traces = self.bus.get_traces()
        assert len(traces) == 0
    
    def test_payload_filtering_respects_detail_levels_consistently(self):
        """Test that payload filtering is consistent across all detail levels."""
        full_payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "phase": "planning",
            "duration": 1.5,
            "success": True,
            "error_type": None,
            "layer": "L3",  # Should always be filtered
            "debug_info": "detailed debug data",
            "metrics": {"cpu": 0.8}
        }
        
        # Test verbose level - should preserve everything except layer
        self.bus.configure(enabled=True, detail_level="verbose")
        self.bus.record_event("test_event", "L3", full_payload.copy())
        verbose_events = self.bus.get_events()
        
        # Test standard level - should preserve only allowed keys
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="standard")
        self.bus.record_event("test_event", "L3", full_payload.copy())
        standard_events = self.bus.get_events()
        
        # Test minimal level - should preserve only essential keys
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="minimal")
        self.bus.record_event("test_event", "L3", full_payload.copy())
        minimal_events = self.bus.get_events()
        
        # Validate filtering consistency
        assert len(verbose_events) == 1
        assert len(standard_events) == 1
        assert len(minimal_events) == 1
        
        # Verbose should have everything except layer
        verbose_payload = verbose_events[0].payload
        assert "layer" not in verbose_payload
        assert "debug_info" in verbose_payload
        assert "metrics" in verbose_payload
        
        # Standard should have only allowed keys
        standard_payload = standard_events[0].payload
        assert "layer" not in standard_payload
        assert "debug_info" not in standard_payload
        assert "metrics" not in standard_payload
        assert "workflow_type" in standard_payload
        
        # Minimal should have only essential keys
        minimal_payload = minimal_events[0].payload
        assert "layer" not in minimal_payload
        assert set(minimal_payload.keys()) == {'workflow_type', 'stage'}
    
    def test_concurrent_workflow_records_start_end_duration(self):
        """Test that concurrent workflow events record start, end, and duration."""
        # Record workflow start
        start_payload = {
            "workflow_type": "concurrent_outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "concurrent_id": "concurrent_123"
        }
        
        self.bus.record_event("workflow_start", "L3", start_payload)
        
        # Simulate workflow execution
        import time
        time.sleep(0.1)
        
        # Record workflow end
        end_payload = {
            "workflow_type": "concurrent_outreach",
            "archetype": "C_LEVEL", 
            "mission_id": "test_mission",
            "stage": "completed",
            "concurrent_id": "concurrent_123",
            "success": True
        }
        
        self.bus.record_event("workflow_end", "L3", end_payload)
        
        events = self.bus.get_events()
        assert len(events) == 2
        
        start_event = events[0]
        end_event = events[1]
        
        # Validate start event
        assert start_event.name == "workflow_start"
        assert start_event.layer == "L3"
        assert start_event.payload["workflow_type"] == "concurrent_outreach"
        assert start_event.payload["concurrent_id"] == "concurrent_123"
        
        # Validate end event
        assert end_event.name == "workflow_end"
        assert end_event.layer == "L3"
        assert end_event.payload["success"] == True
        
        # Validate duration can be calculated
        duration = end_event.timestamp - start_event.timestamp
        assert duration > 0.05  # Should be at least 50ms due to sleep
    
    def test_telemetry_bus_thread_safety_basic(self):
        """Test basic thread safety of telemetry operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def record_events(thread_id):
            try:
                for i in range(10):
                    payload = {
                        "workflow_type": "test",
                        "thread_id": thread_id,
                        "iteration": i,
                        "layer": f"thread_{thread_id}"  # Should be filtered
                    }
                    self.bus.record_event(f"event_{i}", f"L{thread_id}", payload)
                    time.sleep(0.001)  # Small delay to increase contention
                results.append(thread_id)
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=record_events, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Validate results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 5
        
        # Validate all events were recorded
        events = self.bus.get_events()
        assert len(events) == 50  # 5 threads * 10 events each
        
        # Validate no layer in any payload
        for event in events:
            assert "layer" not in event.payload
            assert event.layer.startswith("L")
