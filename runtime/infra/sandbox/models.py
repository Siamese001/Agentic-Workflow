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
    name: str
    vm_id: Optional[str] = None
    timestamp: Optional[str] = None
    ts_ms: Optional[int] = None
    tool_name: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        # Add attributes property for observability compatibility
        if self.details is None:
            self.details = {}
        
        # Create attributes dict that includes vm_id for observability tests
        self.attributes = self.details.copy()
        if self.vm_id:
            self.attributes["vm_id"] = self.vm_id
        if self.tool_name:
            self.attributes["tool_name"] = self.tool_name
        if self.ts_ms:
            self.attributes["ts_ms"] = self.ts_ms
