"""Shared data models for runtime components.


logger = logging.getLogger(__name__)
Provides common data structures used across the runtime shared modules.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

@dataclass
class LLMResponse:
    """Standard LLM response format."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageType(str, Enum):
    """Message types for agent communication."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

@dataclass
class AgentMessage:
    """Message in agent conversation."""
    role: MessageType
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse:
    """Response from agent execution."""
    message: AgentMessage
    success: bool
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    """Validation result for data or operations."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}

class ReasoningConfig(BaseModel):
    """Configuration for reasoning operations."""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None

class HopStatus(str, Enum):
    """Status of hop execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GateDecision(str, Enum):
    """Decision from validation gate."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

class ValidationSeverity(str, Enum):
    """Severity of validation issue."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class WorkflowCheckpoint:
    """Checkpoint in workflow execution."""
    hop_id: str
    status: HopStatus
    data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ThematicAnalysis:
    """Analysis of thematic content."""
    theme: str
    confidence: float
    keywords: List[str]
    sentiment: Optional[str] = None

@dataclass
class RAGState:
    """State of RAG operations."""
    query: str
    retrieved_docs: List[Dict[str, Any]]
    context: str
    response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CircuitState(str, Enum):
    """Circuit breaker state."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# Exception classes
class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""
    pass

class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""
    pass

class ValidationError(AgenticWorkflowError):
    """Validation error."""
    pass

class APIError(AgenticWorkflowError):
    """API-related error."""
    pass

class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open."""
    pass
