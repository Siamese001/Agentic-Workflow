"""
Unit tests for TelemetryRecorder - L0 Maintenance zombie healing.
Phase 7: Zombie Healing - 100% coverage test suite
"""
import pytest
import logging
from agentic_core.L0_maintenance.logs.telemetry_recorder import TelemetryRecorder, TraceEvent


class TestTraceEvent:
    """Test suite for TraceEvent class."""
    
    def test_trace_event_initialization(self):
        """Test TraceEvent initializes with all required fields."""
        event = TraceEvent(
            trace_id="trace-123",
            span_id="span-456",
            ROLE="agent",
            event_type="execution",
            PAYLOAD={"key": "value"},
            TIMESTAMP=1234567890
        )
        
        assert event.data["trace_id"] == "trace-123"
        assert event.data["span_id"] == "span-456"
        assert event.data["role"] == "agent"
        assert event.data["type"] == "execution"
        assert event.data["payload"] == {"key": "value"}
        assert event.data["time"] == 1234567890
    
    def test_trace_event_data_structure(self):
        """Test TraceEvent data dictionary structure."""
        event = TraceEvent("t1", "s1", "test", "start", {}, 0)
        
        assert isinstance(event.data, dict)
        assert len(event.data) == 6
        assert all(key in event.data for key in ["trace_id", "span_id", "role", "type", "payload", "time"])
    
    def test_trace_event_with_empty_payload(self):
        """Test TraceEvent with empty payload."""
        event = TraceEvent("t1", "s1", "agent", "event", {}, 12345)
        
        assert event.data["payload"] == {}
    
    def test_trace_event_with_complex_payload(self):
        """Test TraceEvent with complex nested payload."""
        complex_payload = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "string": "test"
        }
        event = TraceEvent("t1", "s1", "agent", "complex", complex_payload, 0)
        
        assert event.data["payload"] == complex_payload


class TestTelemetryRecorder:
    """Test suite for TelemetryRecorder class."""
    
    def test_initialization_with_config(self):
        """Test TelemetryRecorder initializes with config."""
        config = {"log_level": "INFO", "output": "stdout"}
        recorder = TelemetryRecorder(config)
        
        assert recorder.config == config
    
    def test_initialization_with_empty_config(self):
        """Test TelemetryRecorder with empty config."""
        recorder = TelemetryRecorder({})
        
        assert recorder.config == {}
    
    def test_record_event(self, caplog):
        """Test recording a trace event logs correctly."""
        config = {"enabled": True}
        recorder = TelemetryRecorder(config)
        
        event = TraceEvent(
            trace_id="test-trace",
            span_id="test-span",
            ROLE="test-agent",
            event_type="test-event",
            PAYLOAD={"test": "data"},
            TIMESTAMP=1234567890
        )
        
        with caplog.at_level(logging.INFO):
            recorder.record(event)
        
        # Verify log message was created
        assert len(caplog.records) > 0
        assert "test-event" in caplog.text
        assert "test-span" in caplog.text
    
    def test_record_multiple_events(self, caplog):
        """Test recording multiple events."""
        recorder = TelemetryRecorder({"enabled": True})
        
        events = [
            TraceEvent("t1", "s1", "agent1", "start", {}, 1000),
            TraceEvent("t2", "s2", "agent2", "process", {}, 2000),
            TraceEvent("t3", "s3", "agent3", "end", {}, 3000)
        ]
        
        with caplog.at_level(logging.INFO):
            for event in events:
                recorder.record(event)
        
        # Verify all events were logged
        assert len(caplog.records) >= 3
        assert "start" in caplog.text
        assert "process" in caplog.text
        assert "end" in caplog.text
    
    def test_record_with_different_roles(self, caplog):
        """Test recording events with different roles."""
        recorder = TelemetryRecorder({})
        
        roles = ["validator", "healer", "orchestrator"]
        
        with caplog.at_level(logging.INFO):
            for role in roles:
                event = TraceEvent("t1", f"span-{role}", role, "action", {}, 0)
                recorder.record(event)
        
        # Verify all roles were logged
        for role in roles:
            assert f"span-{role}" in caplog.text
    
    def test_config_persistence(self):
        """Test config is accessible after initialization."""
        config = {"redis_url": "redis://localhost", "batch_size": 100}
        recorder = TelemetryRecorder(config)
        
        assert recorder.config["redis_url"] == "redis://localhost"
        assert recorder.config["batch_size"] == 100
    
    def test_record_event_with_special_characters(self, caplog):
        """Test recording events with special characters in payload."""
        recorder = TelemetryRecorder({})
        
        event = TraceEvent(
            "t1", "s1", "agent",
            "special-event",
            {"message": "Test with 'quotes' and \"double quotes\""},
            0
        )
        
        with caplog.at_level(logging.INFO):
            recorder.record(event)
        
        assert "special-event" in caplog.text
