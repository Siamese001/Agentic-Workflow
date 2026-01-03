from __future__ import annotations

from collections import defaultdict
import threading
from typing import Dict

# PHASE 6: SSOT atomic counter store for dashboard metrics
# Thread-safe, in-memory defaultdict with granular layer + subterritory tracking


class LayerActivationCounters:
    """
    SSOT atomic counter store for dashboard metrics.
    Thread-safe, in-memory defaultdict.
    Granular: layer + optional subterritory.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.counters: Dict[str, int] = defaultdict(int)
            self.sub_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
            self._initialized = True

    def increment(self, layer: str, subterritory: str | None = None) -> None:
        """Atomic increment — called on every layer entry."""
        with self._lock:
            self.counters[layer] += 1
            if subterritory:
                self.sub_counters[layer][subterritory] += 1

    def get_counts(self) -> Dict[str, int]:
        """Get layer-level counts only."""
        return dict(self.counters)

    def get_all(self) -> Dict:
        """Get all counts including subterritory granularity."""
        return {
            "layer_counts": dict(self.counters),
            "sub_counts": {k: dict(v) for k, v in self.sub_counters.items()}
        }

    def reset(self) -> None:
        """Reset all counters."""
        with self._lock:
            self.counters.clear()
            self.sub_counters.clear()


# Global singleton access
counters = LayerActivationCounters()

# Legacy API for backward compatibility
layer_activation_counts = {
    "L0_maintenance": 0,
    "L1_cognition": 0,
    "L2_execution": 0,
    "L3_orchestration": 0,
    "L4_state": 0,
    "L5_safety": 0,
    "config": 0,
    "schemas": 0,
    "prompt_governance": 0,
    "observability": 0,
    "utils": 0,
    "apps_rg": 0,
    "apps_lic": 0,
    "apps_shared": 0
}

def increment_layer_activation(layer: str):
    """Increment activation count for a given layer (legacy API)."""
    if layer in layer_activation_counts:
        layer_activation_counts[layer] += 1
    else:
        layer_activation_counts[layer] = 1
    # Also increment in new SSOT counter
    counters.increment(layer)

def get_layer_counts() -> dict:
    """Get current layer activation counts (legacy API)."""
    return layer_activation_counts.copy()

def reset_layer_counts():
    """Reset all layer activation counts to zero (legacy API)."""
    for layer in layer_activation_counts:
        layer_activation_counts[layer] = 0
    counters.reset()

# Dashboard hook (existing /api/metrics uses this)
def export_for_dashboard() -> Dict:
    """Export counters for dashboard metrics endpoint."""
    return counters.get_all()
