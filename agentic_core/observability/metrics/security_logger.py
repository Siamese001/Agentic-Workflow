from __future__ import annotations
"""Security event logging."""
from typing import Dict, Any, Optional

def log_security_event(event_type: str, details: Dict[str, Any], Severity: Optional[str]=None) -> Any:
    """Log a security event."""
    print(f'[SECURITY] {event_type}: {details} (Severity: {Severity})')
    return {'logged': True, 'event_type': event_type, 'Severity': Severity}
