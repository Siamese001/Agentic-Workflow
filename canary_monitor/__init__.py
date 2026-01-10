"""
Canary Monitor - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional

# Constants for test compatibility
CANARY_FILE_PATH = "/tmp/secrets_canary.txt"
TERMINATE_PID_PATH = "/tmp/agent.pid"


def run_canary_monitor(*args, **kwargs) -> Dict[str, Any]:
    """Run the canary monitor."""
    return {"status": "ok", "canaries": []}


class CanaryMonitor:
    """Monitor for canary deployments."""
    
    def __init__(self):
        self._canaries = {}
        self._running = False
    
    def register(self, name: str, check: callable) -> None:
        self._canaries[name] = check
    
    def check_all(self) -> Dict[str, bool]:
        return {name: check() for name, check in self._canaries.items()}
    
    def stop(self) -> None:
        """Stop the monitor."""
        self._running = False


__all__ = ['CanaryMonitor', 'run_canary_monitor', 'CANARY_FILE_PATH', 'TERMINATE_PID_PATH']
