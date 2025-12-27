"""Stub for canon validator engine."""
from typing import Dict, Any
from enum import Enum

class ExitReason(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"

class P6FixResult:
    def __init__(self, success: bool = True, message: str = ""):
        self.success = success
        self.message = message

class CanonValidatorEngineZLM:
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def validate(self, data: Dict) -> bool:
        return True
    
    def get_violations(self) -> list:
        return []
    
    def run(self) -> ExitReason:
        return ExitReason.SUCCESS
