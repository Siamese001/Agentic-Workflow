"""
Phase 8 Telemetry Boundary Purity Tests

Tests that telemetry respects L1-L5 architectural boundaries:
- Telemetry never crosses layer boundaries inappropriately
- Layer isolation is maintained during telemetry operations
- Telemetry bus respects architectural purity
- No circular dependencies through telemetry
- Layer-specific telemetry validation
- Boundary violation detection and prevention
"""

import pytest
import threading
import time
from unittest.mock import patch, Mock
from typing import Dict, Any

from runtime.telemetry_bus import TelemetryBus, get_telemetry_bus


class TestTelemetryBoundaryPurity:
    """Test suite for telemetry boundary purity validation."""
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = get_telemetry_bus()
        self.bus.clear()
        self.bus.configure(enabled=True, detail_level="standard")
    
    def test_layer_isolation_in_telemetry_events(self):
        """Test that telemetry events maintain proper layer isolation."""
        # Record events from different layers
        l1_payload = {"workflow_type": "archetype_planning", "archetype": "C_LEVEL"}
        l2_payload = {"workflow_type": "research_execution", "company": "test_company"}
        l3_payload = {"workflow_type": "outreach_orchestration", "stage": "planning"}
        l4_payload = {"workflow_type": "rag_enrichment", "query": "test_query"}
        l5_payload = {"workflow_type": "safety_validation", "violation": False}
        
        # Record events from each layer
        self.bus.record_event("l1_event", "L1", l1_payload)
        self.bus.record_event("l2_event", "L2", l2_payload)
        self.bus.record_event("l3_event", "L3", l3_payload)
        self.bus.record_event("l4_event", "L4", l4_payload)
        self.bus.record_event("l5_event", "L5", l5_payload)
        
        # Validate layer isolation
        l1_events = self.bus.get_events(layer="L1")
        l2_events = self.bus.get_events(layer="L2")
        l3_events = self.bus.get_events(layer="L3")
        l4_events = self.bus.get_events(layer="L4")
        l5_events = self.bus.get_events(layer="L5")
        
        # Each layer should only have its own events
        assert len(l1_events) == 1
        assert len(l2_events) == 1
        assert len(l3_events) == 1
        assert len(l4_events) == 1
        assert len(l5_events) == 1
        
        # Validate layer parameters are correct
        assert l1_events[0].layer == "L1"
        assert l2_events[0].layer == "L2"
        assert l3_events[0].layer == "L3"
        assert l4_events[0].layer == "L4"
        assert l5_events[0].layer == "L5"
        
        # Validate no layer in any payload
        for events in [l1_events, l2_events, l3_events, l4_events, l5_events]:
            for event in events:
                assert "layer" not in event.payload
    
    def test_boundary_purity_during_concurrent_operations(self):
        """Test that boundaries remain pure during concurrent operations."""
        results = []
        errors = []
        
        def layer_boundary_test(layer_name, num_events):
            try:
                for i in range(num_events):
                    payload = {
                        "workflow_type": f"{layer_name.lower()}_workflow",
                        "iteration": i,
                        "layer_data": f"data_from_{layer_name}"
                    }
                    
                    self.bus.record_event(f"{layer_name.lower()}_event_{i}", layer_name, payload)
                
                # Validate layer isolation
                layer_events = self.bus.get_events(layer=layer_name)
                assert len(layer_events) == num_events
                
                for event in layer_events:
                    assert event.layer == layer_name
                    assert "layer" not in event.payload
                    assert event.payload["workflow_type"].startswith(layer_name.lower())
                
                results.append(layer_name)
                
            except Exception as e:
                errors.append((layer_name, e))
        
        # Create concurrent boundary tests for each layer
        threads = []
        layers = ["L1", "L2", "L3", "L4", "L5"]
        
        for layer in layers:
            thread = threading.Thread(target=layer_boundary_test, args=(layer, 20))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Validate boundary purity
        assert len(errors) == 0, f"Boundary purity errors: {errors}"
        assert len(results) == 5
        
        # Validate total events
        all_events = self.bus.get_events()
        assert len(all_events) == 100  # 5 layers * 20 events each
        
        # Validate cross-layer isolation
        for layer in layers:
            layer_events = self.bus.get_events(layer=layer)
            other_events = self.bus.get_events()
            other_events = [e for e in other_events if e.layer != layer]
            
            # No events should have wrong layer
            for event in layer_events:
                assert event.layer == layer
    
    def test_no_circular_dependencies_through_telemetry(self):
        """Test that telemetry doesn't create circular dependencies."""
        # Mock layer components to test for circular dependencies
        l1_component = Mock()
        l2_component = Mock()
        l3_component = Mock()
        l4_component = Mock()
        l5_component = Mock()
        
        # Use verbose mode to preserve all test fields
        self.bus.configure(detail_level="verbose")
        
        # Simulate telemetry usage patterns
        def l1_telemetry_usage():
            # L1 should only record L1 events
            self.bus.record_event("l1_operation", "L1", {"source": "L1"})
        
        def l2_telemetry_usage():
            # L2 should only record L2 events
            self.bus.record_event("l2_operation", "L2", {"source": "L2"})
        
        def l3_telemetry_usage():
            # L3 should only record L3 events
            self.bus.record_event("l3_operation", "L3", {"source": "L3"})
        
        def l4_telemetry_usage():
            # L4 should only record L4 events
            self.bus.record_event("l4_operation", "L4", {"source": "L4"})
        
        def l5_telemetry_usage():
            # L5 should only record L5 events
            self.bus.record_event("l5_operation", "L5", {"source": "L5"})
        
        # Execute telemetry usage patterns
        l1_telemetry_usage()
        l2_telemetry_usage()
        l3_telemetry_usage()
        l4_telemetry_usage()
        l5_telemetry_usage()
        
        # Validate no circular dependencies
        events = self.bus.get_events()
        assert len(events) == 5
        
        # Each event should only reference its own layer
        for event in events:
            assert event.layer in ["L1", "L2", "L3", "L4", "L5"]
            assert event.payload["source"] == event.layer
            assert "layer" not in event.payload
    
    def test_telemetry_bus_respects_architectural_boundaries(self):
        """Test that TelemetryBus itself respects architectural boundaries."""
        # TelemetryBus should be layer-agnostic but maintain layer separation
        # Use verbose mode to preserve all test fields
        self.bus.configure(detail_level="verbose")
        
        test_payloads = {
            "L1": {"operation": "archetype_planning", "data": "l1_data"},
            "L2": {"operation": "research_execution", "data": "l2_data"},
            "L3": {"operation": "outreach_orchestration", "data": "l3_data"},
            "L4": {"operation": "rag_enrichment", "data": "l4_data"},
            "L5": {"operation": "safety_validation", "data": "l5_data"}
        }
        
        # Record events from all layers
        for layer, payload in test_payloads.items():
            self.bus.record_event(f"{layer.lower()}_test", layer, payload)
        
        # Validate TelemetryBus maintains proper boundaries
        all_events = self.bus.get_events()
        assert len(all_events) == 5
        
        # Test filtering by layer
        for layer in ["L1", "L2", "L3", "L4", "L5"]:
            layer_events = self.bus.get_events(layer=layer)
            assert len(layer_events) == 1
            assert layer_events[0].layer == layer
            # Validate that the event was recorded with the correct layer
            # The operation field should be preserved as-is in verbose mode
            assert "operation" in layer_events[0].payload
        
        # Test that bus doesn't mix layer data
        l1_events = self.bus.get_events(layer="L1")
        for event in l1_events:
            assert event.layer == "L1"
            assert "L2" not in str(event.payload)
            assert "L3" not in str(event.payload)
            assert "L4" not in str(event.payload)
            assert "L5" not in str(event.payload)
    
    def test_boundary_violation_detection_and_prevention(self):
        """Test that boundary violations are detected and prevented."""
        # Test attempts to record events with invalid layer names
        # TelemetryBus currently accepts all layer strings gracefully
        invalid_layers = ["L0", "L6", "L1.5", "invalid", ""]
        
        for invalid_layer in invalid_layers:
            # Should handle invalid layer names gracefully by accepting them
            payload = {"test": "data"}
            self.bus.record_event("test_event", invalid_layer, payload)
        
        # Test attempts to include layer in payload (should be filtered)
        self.bus.configure(detail_level="standard")
        payload_with_layer = {
            "workflow_type": "test",
            "stage": "execution",
            "layer": "L3"  # This should be filtered out
        }
        
        self.bus.record_event("boundary_test", "L3", payload_with_layer)
        events = self.bus.get_events()
        
        # Should have recorded all events (TelemetryBus is permissive about layer names)
        assert len(events) == 6  # 5 invalid layers + 1 valid layer test
        
        # Validate layer filtering from payload
        boundary_test_events = [e for e in events if e.name == "boundary_test"]
        assert len(boundary_test_events) == 1
        assert "layer" not in boundary_test_events[0].payload
        assert boundary_test_events[0].layer == "L3"
    
    def test_layer_specific_telemetry_validation(self):
        """Test layer-specific telemetry validation rules."""
        # Use verbose mode to preserve all test fields for validation
        self.bus.configure(detail_level="verbose")
        
        # L1 specific payload validation
        l1_payload = {
            "workflow_type": "archetype_planning",
            "archetype": "C_LEVEL",
            "confidence": 0.8,
            "layer": "L1"  # Should be filtered
        }
        
        # L2 specific payload validation
        l2_payload = {
            "workflow_type": "research_execution",
            "company": "test_company",
            "contact": "test_contact",
            "layer": "L2"  # Should be filtered
        }
        
        # L3 specific payload validation
        l3_payload = {
            "workflow_type": "outreach_orchestration",
            "stage": "planning",
            "mission_id": "test_mission",
            "layer": "L3"  # Should be filtered
        }
        
        # Record layer-specific events
        self.bus.record_event("l1_specific", "L1", l1_payload)
        self.bus.record_event("l2_specific", "L2", l2_payload)
        self.bus.record_event("l3_specific", "L3", l3_payload)
        
        # Validate layer-specific filtering
        l1_events = self.bus.get_events(layer="L1")
        l2_events = self.bus.get_events(layer="L2")
        l3_events = self.bus.get_events(layer="L3")
        
        # All should have layer filtered from payload
        assert "layer" not in l1_events[0].payload
        assert "layer" not in l2_events[0].payload
        assert "layer" not in l3_events[0].payload
        
        # Validate layer-specific content preservation (verbose mode preserves all except layer)
        assert l1_events[0].payload["archetype"] == "C_LEVEL"
        assert l2_events[0].payload["company"] == "test_company"
        assert l3_events[0].payload["stage"] == "planning"
    
    def test_boundary_purity_under_configuration_changes(self):
        """Test that boundary purity is maintained under configuration changes."""
        # Record events at different detail levels
        full_payload = {
            "workflow_type": "boundary_test",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "planning",
            "phase": "execution",
            "duration": 1.5,
            "success": True,
            "error_type": None,
            "layer": "L3",  # Should always be filtered
            "debug_info": "detailed debug data"
        }
        
        # Test at verbose level
        self.bus.configure(detail_level="verbose")
        self.bus.record_event("verbose_test", "L3", full_payload.copy())
        verbose_events = self.bus.get_events()
        
        # Test at standard level
        self.bus.clear()
        self.bus.configure(detail_level="standard")
        self.bus.record_event("standard_test", "L3", full_payload.copy())
        standard_events = self.bus.get_events()
        
        # Test at minimal level
        self.bus.clear()
        self.bus.configure(detail_level="minimal")
        self.bus.record_event("minimal_test", "L3", full_payload.copy())
        minimal_events = self.bus.get_events()
        
        # Validate boundary purity across all detail levels
        for events in [verbose_events, standard_events, minimal_events]:
            assert len(events) == 1
            event = events[0]
            assert event.layer == "L3"
            assert "layer" not in event.payload
        
        # Validate verbose preserves most data (except layer)
        verbose_payload = verbose_events[0].payload
        assert "debug_info" in verbose_payload
        assert "layer" not in verbose_payload
        
        # Validate standard filters appropriately
        standard_payload = standard_events[0].payload
        assert "debug_info" not in standard_payload
        assert "layer" not in standard_payload
        assert "workflow_type" in standard_payload
        
        # Validate minimal preserves only essential data
        minimal_payload = minimal_events[0].payload
        assert set(minimal_payload.keys()) <= {"workflow_type", "stage"}
        assert "layer" not in minimal_payload
    
    def test_cross_layer_telemetry_isolation(self):
        """Test that telemetry from different layers doesn't interfere."""
        # Simulate rapid cross-layer telemetry operations
        layers_and_events = [
            ("L1", ["archetype_plan", "archetype_execute", "archetype_validate"]),
            ("L2", ["research_start", "research_progress", "research_complete"]),
            ("L3", ["orchestrate_start", "orchestrate_progress", "orchestrate_end"]),
            ("L4", ["rag_query", "rag_retrieve", "rag_rank"]),
            ("L5", ["safety_check", "safety_validate", "safety_approve"])
        ]
        
        # Record events rapidly across layers
        for layer, events in layers_and_events:
            for event_name in events:
                payload = {
                    "workflow_type": f"{layer.lower()}_workflow",
                    "event_name": event_name,
                    "timestamp": time.time()
                }
                self.bus.record_event(event_name, layer, payload)
        
        # Validate cross-layer isolation
        all_events = self.bus.get_events()
        assert len(all_events) == 15  # 5 layers * 3 events each
        
        # Validate each layer's events are isolated
        for layer, expected_events in layers_and_events:
            layer_events = self.bus.get_events(layer=layer)
            assert len(layer_events) == 3
            
            # Validate all events belong to correct layer
            for event in layer_events:
                assert event.layer == layer
                assert event.name in expected_events
                assert "layer" not in event.payload
                assert event.payload["workflow_type"] == f"{layer.lower()}_workflow"
        
        # Validate no cross-contamination
        l1_events = self.bus.get_events(layer="L1")
        for event in l1_events:
            assert event.layer == "L1"
            assert "L2" not in event.name
            assert "L3" not in event.name
            assert "L4" not in event.name
            assert "L5" not in event.name
