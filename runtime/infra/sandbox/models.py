# Sandbox models
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class ToolCallRequest:
    """Request for tool execution in sandbox"""
    tool_name: str
    args: List[str] = None
    env: Dict[str, str] = None
    timeout_s: float = 30.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ToolCallResult:
    """Result from tool execution in sandbox"""
    success: bool = True
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SandboxEvent:
    """Event emitted by sandbox operations"""
    event_type: str
    vm_id: Optional[str] = None
    timestamp: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
