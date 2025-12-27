"""Stub for canon_validator module."""

class CanonValidator:
    """Stub for canon validation."""
    def __init__(self, *args, **kwargs):
        self.rules = []
    
    def validate(self, target) -> bool:
        return True
    
    def get_violations(self):
        return []
