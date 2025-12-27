"""Stub for canon validator engine."""
from typing import Dict, Any

class CanonValidatorEngine:
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def validate(self, data: Dict) -> bool:
        return True
    
    def get_violations(self) -> list:
        return []
