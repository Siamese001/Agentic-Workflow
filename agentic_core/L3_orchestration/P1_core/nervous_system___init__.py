"""Nervous System module."""
from .reflex_layer import ReflexLayer

class NervousSystem:
    """Nervous System orchestration."""
    
    def __init__(self):
        self.reflex_layer = ReflexLayer()
        self.reflexes = {}
        self.missions = []
    
    def register_reflex(self, trigger: str, action: callable):
        self.reflexes[trigger] = action
        return self.reflex_layer.register_reflex(trigger, action)
    
    def trigger_reflex(self, event: str):
        return self.reflex_layer.trigger_reflex(event)
    
    def get_status(self):
        return self.reflex_layer.get_status()

__all__ = ['NervousSystem', 'ReflexLayer']
