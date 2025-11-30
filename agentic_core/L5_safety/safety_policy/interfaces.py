# Safety policy interfaces
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional

class Verdict(str, Enum):
    """Safety verdict types"""
    SAFE = "safe"
    WARNING = "warning"
    VIOLATION = "violation"
    BLOCK = "block"

@dataclass
class Action:
    """Safety action to take"""
    action_type: str
    severity: str
    message: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
