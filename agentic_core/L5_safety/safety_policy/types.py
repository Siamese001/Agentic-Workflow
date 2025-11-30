# Safety policy types
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional

class Severity(str, Enum):
    """Severity levels for safety violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Verdict(str, Enum):
    """Safety verdict types"""
    SAFE = "safe"
    WARNING = "warning"
    VIOLATION = "violation"
    BLOCK = "block"

@dataclass
class SafetyContext:
    """Context for safety evaluation"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation_type: str = ""
    content: str = ""
    domain: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
