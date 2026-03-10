from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Nervous System module."""
from agentic_core.L3_orchestration.engines.reflex_layer_pattern import ReflexLayer


# NAMING FIXED: NervousSystem → NervousSystem
class NervousSystem:
    """Nervous System orchestration."""

    def __init__(self):
        self.ReflexLayer = ReflexLayer()
        self.reflexes = {}
        self.missions = []

    def register_reflex(self, trigger: str, action: callable):
        self.reflexes[trigger] = action
        return self.ReflexLayer.register_reflex(trigger, action)

    def trigger_reflex(self, event: str):
        return self.ReflexLayer.trigger_reflex(event)

    def get_status(self):
        return self.ReflexLayer.get_status()


__all__ = ["NervousSystem", "ReflexLayer"]
