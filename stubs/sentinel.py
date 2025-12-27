class Sentinel:
    """Stub for runtime anomaly detection."""
    def __init__(self): self.alerts = []
    def monitor(self, metric: str, value: float): pass
    def raise_alert(self, msg: str): self.alerts.append(msg)
