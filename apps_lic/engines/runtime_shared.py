"""
Runtime Shared Schemas (Phase 2C Residuals)
==========================================
This module serves as the centralized repository for residual models
discovered during the Phase 2C sweep. These models are critical for
the LLM response cycle, RAG state management, and workflow checkpoints.

Note: 'Residual' prefixes are maintained to prevent collisions with
legacy Phase 1 models during the final migration.
"""


# ==========================================
# Messaging & Communication
# ==========================================


class MessageType(str, Enum):
    """Message types for agent communication."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ResidualAgentMessage:
    """Message in agent conversation (Residual Phase 2C)."""

    role: MessageType
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] | None = None


# ==========================================
# LLM Response & Feedback
# ==========================================


@dataclass
class LLMResponse:
    """Standard LLM response format."""

    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class AgentResponse:
    """Response from agent execution containing a residual message."""

    message: ResidualAgentMessage
    success: bool
    error: str | None = None
    usage: dict[str, int] | None = None
    metadata: dict[str, Any] | None = None


# ==========================================
# Validation & Configuration
# ==========================================


class ResidualValidationResult(BaseModel):
    """Validation result for data or operations (Residual Phase 2C)."""

    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


class ReasoningConfig(BaseModel):
    """Configuration for reasoning operations."""

    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: list[str] | None = None


# ==========================================
# Workflow & Runtime Status
# ==========================================


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
    SKIP = "skip"


class ValidationSeverity(str, Enum):
    """Severity of validation issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CircuitState(str, Enum):
    """Circuit breaker state for fault tolerance."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class WorkflowCheckpoint:
    """Checkpoint in workflow execution."""

    hop_id: str
    status: HopStatus
    data: dict[str, Any]
    timestamp: str
    metadata: dict[str, Any] | None = None


# ==========================================
# Specialized Analysis & Retrieval
# ==========================================


@dataclass
class ThematicAnalysis:
    """Analysis of thematic content."""

    theme: str
    confidence: float
    keywords: list[str]
    sentiment: str | None = None


@dataclass
class RAGState:
    """State of RAG (Retrieval-Augmented Generation) operations."""

    query: str
    retrieved_docs: list[dict[str, Any]]
    context: str
    response: str | None = None
    metadata: dict[str, Any] | None = None
