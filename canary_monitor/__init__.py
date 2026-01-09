"""
Canary Monitor - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class CanaryMonitor:
    """Monitor for canary deployments."""
    def __init__(self):
        self._metrics = {}
    
    def record(self, metric: str, value: Any) -> None:
        self._metrics[metric] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()


__all__ = ['CanaryMonitor']
