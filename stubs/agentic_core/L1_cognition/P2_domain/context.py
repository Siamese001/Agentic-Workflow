"""Stub for validation context."""
from typing import Dict, Any, List

class ValidationContext:
    def __init__(self):
        self.data = {}
        self.errors = []
    
    def add_error(self, error: str):
        self.errors.append(error)
    
    def is_valid(self) -> bool:
        return len(self.errors) == 0
