class CanaryMonitor:
    def __init__(self, **kwargs): pass
    def check_health(self) -> bool: return True
    def trigger_alert(self, msg: str): print(f"Stub Alert: {msg}")

def run_canary_monitor(**kwargs):
    """Stub function for running canary monitor."""
    return CanaryMonitor(**kwargs)
