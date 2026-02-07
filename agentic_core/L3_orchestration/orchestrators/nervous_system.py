from __future__ import annotations

"""Nervous System module."""
from agentic_core.L3_orchestration.patterns.reflex_layer_pattern import ReflexLayer


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
