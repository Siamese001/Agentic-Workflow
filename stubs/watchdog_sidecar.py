"""Stub for watchdog_sidecar module."""

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
