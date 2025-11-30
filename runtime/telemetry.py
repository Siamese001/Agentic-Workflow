# telemetry - Runtime telemetry system
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class TelemetryLevel(Enum):
    """Telemetry logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class TelemetryEvent:
    """Individual telemetry event"""
    event_type: str
    timestamp: str
    level: TelemetryLevel
    data: Dict[str, Any]
    source: str = "unknown"
    
    def __post_init__(self):
        if isinstance(self.level, str):
            self.level = TelemetryLevel(self.level)

class TelemetryBus:
    """Central telemetry bus for collecting and distributing events"""
    
    def __init__(self):
        self.subscribers: List[Callable[[TelemetryEvent], None]] = []
        self.events: List[TelemetryEvent] = []
        self.errors: List[Dict[str, Any]] = []
        self.traces: List[Dict[str, Any]] = []
        self.enabled = True
    
    def subscribe(self, callback: Callable[[TelemetryEvent], None]) -> str:
        """Subscribe to telemetry events"""
        self.subscribers.append(callback)
        return f"subscriber_{len(self.subscribers)}"
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from telemetry events"""
        # Simple implementation - would need proper tracking in real system
        return True
    
    def publish(self, event: TelemetryEvent) -> bool:
        """Publish a telemetry event"""
        if not self.enabled:
            return False
        
        self.events.append(event)
        
        # Notify subscribers
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception:
                pass  # Don't let subscriber errors break publishing
        
        return True
    
    def create_event(self, event_type: str, data: Dict[str, Any], level: TelemetryLevel = TelemetryLevel.INFO, source: str = "unknown") -> TelemetryEvent:
        """Create a new telemetry event"""
        import datetime
        return TelemetryEvent(
            event_type=event_type,
            timestamp=datetime.datetime.now().isoformat(),
            level=level,
            data=data,
            source=source
        )
    
    def get_events(self, event_type: Optional[str] = None, level: Optional[TelemetryLevel] = None, limit: Optional[int] = None) -> List[TelemetryEvent]:
        """Get filtered telemetry events"""
        filtered_events = self.events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if level:
            filtered_events = [e for e in filtered_events if e.level == level]
        
        if limit:
            filtered_events = filtered_events[-limit:]
        
        return filtered_events
    
    def record_event(self, event_type: str, source: str, data: Dict[str, Any]) -> None:
        """Record a telemetry event"""
        event = self.create_event(event_type, data, TelemetryLevel.INFO, source)
        self.publish(event)
    
    def record_error(self, error_type: str, source: str, exception: Exception, context: Dict[str, Any]) -> None:
        """Record a telemetry error"""
        error_data = {
            "error_type": error_type,
            "exception": str(exception),
            "exception_type": type(exception).__name__,
            "context": context
        }
        self.errors.append({
            "error_type": error_type,
            "source": source,
            "exception": exception,
            "context": context,
            "timestamp": self.create_event("", {}, TelemetryLevel.ERROR, source).timestamp
        })
    
    def record_trace(self, trace_data: Dict[str, Any]) -> None:
        """Record a telemetry trace"""
        import datetime
        trace = {
            "trace_data": trace_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.traces.append(trace)
    
    def get_events(self) -> List[TelemetryEvent]:
        """Get all recorded events"""
        return self.events.copy()
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all recorded errors"""
        return self.errors.copy()
    
    def get_traces(self) -> List[Dict[str, Any]]:
        """Get all recorded traces"""
        return self.traces.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary statistics"""
        return {
            "total_events": len(self.events),
            "total_errors": len(self.errors),
            "total_traces": len(self.traces),
            "enabled": self.enabled,
            "subscribers": len(self.subscribers)
        }
    
    def clear_events(self) -> bool:
        """Clear all stored events"""
        self.events.clear()
        return True
    
    def clear(self) -> None:
        """Clear all stored events (alias for clear_events for test compatibility)"""
        self.events.clear()
        self.errors.clear()
        self.traces.clear()
    
    def enable(self) -> None:
        """Enable telemetry collection"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable telemetry collection"""
        self.enabled = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics"""
        level_counts = {}
        for level in TelemetryLevel:
            level_counts[level.value] = len([e for e in self.events if e.level == level])
        
        return {
            "total_events": len(self.events),
            "subscribers": len(self.subscribers),
            "enabled": self.enabled,
            "level_counts": level_counts
        }

# Global telemetry bus instance
_global_telemetry_bus: Optional[TelemetryBus] = None

def get_telemetry_bus() -> TelemetryBus:
    """Get the global telemetry bus instance"""
    global _global_telemetry_bus
    if _global_telemetry_bus is None:
        _global_telemetry_bus = TelemetryBus()
    return _global_telemetry_bus

def reset_telemetry_bus() -> None:
    """Reset the global telemetry bus (for testing)"""
    global _global_telemetry_bus
    _global_telemetry_bus = None

# Convenience functions
def log_event(event_type: str, data: Dict[str, Any], level: TelemetryLevel = TelemetryLevel.INFO, source: str = "unknown") -> bool:
    """Log a telemetry event using the global bus"""
    bus = get_telemetry_bus()
    event = bus.create_event(event_type, data, level, source)
    return bus.publish(event)

def log_info(event_type: str, data: Dict[str, Any], source: str = "unknown") -> bool:
    """Log an info level telemetry event"""
    return log_event(event_type, data, TelemetryLevel.INFO, source)

def log_warning(event_type: str, data: Dict[str, Any], source: str = "unknown") -> bool:
    """Log a warning level telemetry event"""
    return log_event(event_type, data, TelemetryLevel.WARNING, source)

def log_error(event_type: str, data: Dict[str, Any], source: str = "unknown") -> bool:
    """Log an error level telemetry event"""
    return log_event(event_type, data, TelemetryLevel.ERROR, source)
