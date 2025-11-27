"""
TelemetryBus - Observability layer for outreach workflow.

Provides structured event capture for L3 and L2 layers without
affecting core behavior. Singleton pattern with in-memory storage.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TelemetryEvent:
    """Structured telemetry event."""
    name: str
    layer: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_type: str = "event"  # "event", "error", "trace"


@dataclass
class TelemetryError:
    """Structured telemetry error."""
    name: str
    layer: str
    error: BaseException
    context: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_type: str = "error"


@dataclass
class TelemetryTrace:
    """Structured telemetry trace."""
    trace: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_type: str = "trace"


class TelemetryBus:
    """Singleton telemetry bus for event capture and observability."""
    
    _instance: Optional['TelemetryBus'] = None
    _class_lock = threading.Lock()  # Class-level lock for singleton pattern
    
    def __new__(cls) -> 'TelemetryBus':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._class_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize telemetry storage."""
        if not hasattr(self, '_initialized'):
            self._events: List[TelemetryEvent] = []
            self._errors: List[TelemetryError] = []
            self._traces: List[TelemetryTrace] = []
            self._enabled: bool = True
            self._detail_level: str = "standard"
            self._lock: threading.RLock = threading.RLock()
            self._initialized = True
    
    def configure(self, enabled: bool = True, detail_level: str = "standard") -> None:
        """Configure telemetry settings."""
        with self._lock:
            self._enabled = enabled
            self._detail_level = detail_level
    
    def record_event(self, name: str, layer: str, payload: Dict[str, Any]) -> None:
        """Record a structured event."""
        if not self._enabled:
            return
        
        with self._lock:
            # Filter payload based on detail level
            filtered_payload = self._filter_payload(payload)
            event = TelemetryEvent(name=name, layer=layer, payload=filtered_payload)
            self._events.append(event)
    
    def record_error(self, name: str, layer: str, error: BaseException, context: Dict[str, Any]) -> None:
        """Record an error event."""
        if not self._enabled:
            return
        
        with self._lock:
            # Filter context based on detail level
            filtered_context = self._filter_payload(context)
            error_event = TelemetryError(
                name=name, 
                layer=layer, 
                error=error, 
                context=filtered_context
            )
            self._errors.append(error_event)
    
    def record_trace(self, trace: Dict[str, Any]) -> None:
        """Record a trace event."""
        if not self._enabled:
            return
        
        with self._lock:
            # Don't filter trace data - traces need all fields for observability
            trace_event = TelemetryTrace(trace=trace.copy())
            self._traces.append(trace_event)
    
    def _filter_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Filter payload based on detail level and remove sensitive data."""
        if self._detail_level == "verbose":
            return payload.copy()
        elif self._detail_level == "standard":
            # Include basic workflow info, exclude detailed metrics
            allowed_keys = {
                'workflow_type', 'archetype', 'mission_id', 'stage', 
                'phase', 'duration', 'success', 'error_type', 'layer'
            }
            return {k: v for k, v in payload.items() if k in allowed_keys}
        else:  # minimal
            # Only include essential identifiers
            allowed_keys = {'workflow_type', 'stage', 'layer'}
            return {k: v for k, v in payload.items() if k in allowed_keys}
    
    def get_events(self, layer: Optional[str] = None, name: Optional[str] = None) -> List[TelemetryEvent]:
        """Get recorded events with optional filtering."""
        with self._lock:
            events = self._events.copy()
        
        if layer:
            events = [e for e in events if e.layer == layer]
        if name:
            events = [e for e in events if e.name == name]
        
        return events
    
    def get_errors(self, layer: Optional[str] = None, name: Optional[str] = None) -> List[TelemetryError]:
        """Get recorded errors with optional filtering."""
        with self._lock:
            errors = self._errors.copy()
        
        if layer:
            errors = [e for e in errors if e.layer == layer]
        if name:
            errors = [e for e in errors if e.name == name]
        
        return errors
    
    def get_traces(self) -> List[TelemetryTrace]:
        """Get recorded traces."""
        with self._lock:
            return self._traces.copy()
    
    def clear(self) -> None:
        """Clear all recorded telemetry data."""
        with self._lock:
            self._events.clear()
            self._errors.clear()
            self._traces.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary statistics."""
        with self._lock:
            # Include layers from both events and errors
            event_layers = set(e.layer for e in self._events)
            error_layers = set(e.layer for e in self._errors)
            all_layers = event_layers.union(error_layers)
            
            return {
                "total_events": len(self._events),
                "total_errors": len(self._errors),
                "total_traces": len(self._traces),
                "enabled": self._enabled,
                "detail_level": self._detail_level,
                "layers": list(all_layers),
                "event_names": list(set(e.name for e in self._events))
            }


# Global singleton instance
_telemetry_bus: Optional[TelemetryBus] = None


def get_telemetry_bus() -> TelemetryBus:
    """Get the global TelemetryBus singleton instance."""
    global _telemetry_bus
    if _telemetry_bus is None:
        _telemetry_bus = TelemetryBus()
    return _telemetry_bus
