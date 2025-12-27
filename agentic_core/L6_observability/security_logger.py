"""Security event logging."""
from typing import Dict, Any, Optional

def log_security_event(event_type: str, details: Dict[str, Any], severity: Optional[str] = None):
    """Log a security event."""
    print(f"[SECURITY] {event_type}: {details} (severity: {severity})")
    return {"logged": True, "event_type": event_type, "severity": severity}
