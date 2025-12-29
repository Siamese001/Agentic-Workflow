"""Nervous System module."""
from .reflex_layer import ReflexLayer

# NAMING FIXED: NervousSystem → nervous_system
class nervous_system:
    """Nervous System orchestration."""
    
    def __init__(self):
        self.reflex_layer = ReflexLayer()
        self.reflexes = {}
        self.missions = []
    
    def register_reflex(self, trigger: str, action: callable):
                    '''Brief description of functionality and purpose.'''
                    
        self.reflexes[trigger] = action
        return self.reflex_layer.register_reflex(trigger, action)
    
    def trigger_reflex(self, event: str):
                    '''Brief description of functionality and purpose.'''
                    
        return self.reflex_layer.trigger_reflex(event)
    
    def get_status(self):
                    '''Brief description of functionality and purpose.'''
                    
        return self.reflex_layer.get_status()

__all__ = ['NervousSystem', 'ReflexLayer']
