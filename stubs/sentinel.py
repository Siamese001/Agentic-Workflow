"""
Sentinel Stub - Runtime Anomaly Detection

PURPOSE:
    Stub implementation for runtime anomaly detection.
    Provides metric monitoring and alert management for testing.

STATUS: Active - Used for testing monitoring
PLANNED: Full implementation with statistical anomaly detection
"""


class Sentinel:
    """Stub for runtime anomaly detection."""
    def __init__(self): 
        self.alerts = []
        self.status = "monitoring"
        self.metrics = {}

    def monitor(self, metric: str, value: float):
        self.metrics[metric] = value

    def raise_alert(self, message: str, level: str = "info"):
        alert = {
            "message": message,
            "level": level,
            "timestamp": "2025-12-27T12:00:00Z"
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self):
        return self.alerts
