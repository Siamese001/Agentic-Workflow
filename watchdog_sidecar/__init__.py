"""
Watchdog Sidecar - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class WatchdogSidecar:
    """Sidecar for watchdog monitoring."""
    def __init__(self):
        self._watches = {}
    
    def watch(self, name: str, target: Any) -> None:
        self._watches[name] = target
    
    def check(self, name: str) -> bool:
        return name in self._watches
    
    def get_status(self) -> Dict[str, Any]:
        return {name: "active" for name in self._watches}


__all__ = ['WatchdogSidecar']
