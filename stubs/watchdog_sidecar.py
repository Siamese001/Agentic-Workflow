"""
Watchdog Sidecar Stub - Process Monitoring

PURPOSE:
    Stub implementation for watchdog sidecar monitoring.
    Provides health checks and alert management for testing.

STATUS: Active - Used for testing process monitoring
PLANNED: Full implementation with process supervision
"""

class WatchdogSidecar:
    """Stub for watchdog sidecar monitoring."""
    def __init__(self):
        self.status = "monitoring"
        self.alerts = []
    
    def start(self):
        self.status = "active"
        return True
    
    def stop(self):
        self.status = "stopped"
        return True
    
    def check_health(self) -> dict:
        return {"status": self.status, "healthy": True}
    
    def raise_alert(self, message: str):
        self.alerts.append(message)
