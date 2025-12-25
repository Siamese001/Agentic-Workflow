"""Shared data models for runtime components.


LOGGER = logging.getLogger(__name__)
Provides common data structures used across the runtime shared modules.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class LLMResponse:
    """Standard LLM response format."""

    _content: str
    _model: str
    _usage: Optional[Dict[str, int]] = None
    _finish_reason: Optional[str] = None
    _metadata: Optional[Dict[str, Any]] = None


class MessageType(str, Enum):
    """Message types for agent communication."""


@dataclass
class AgentMessage:
    """Message in agent conversation."""

    _role: MessageType
    content: str
    _tool_calls: Optional[List[Dict[str, Any]]] = None
    _tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    """Response from agent execution."""

    _message: AgentMessage
    _success: bool
    _error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None


class ValidationResult(BaseModel):
    """Validation result for data or operations."""

    _is_valid: bool
    _errors: List[str] = []
    _warnings: List[str] = []
    metadata: Dict[str, Any] = {}


class ReasoningConfig(BaseModel):
    """Configuration for reasoning operations."""

    _temperature: float = 0.7
    _max_tokens: int = 1000
    _top_p: float = 0.9
    _frequency_penalty: float = 0.0
    _presence_penalty: float = 0.0
    _stop_sequences: Optional[List[str]] = None


class HopStatus(str, Enum):
    """Status of hop execution."""


class GateDecision(str, Enum):
    """Decision from validation gate."""


class ValidationSeverity(str, Enum):
    """Severity of validation issue."""


@dataclass
class WorkflowCheckpoint:
    """Checkpoint in workflow execution."""

    _hop_id: str
    _status: HopStatus
    _data: Dict[str, Any]
    _timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ThematicAnalysis:
    """Analysis of thematic content."""

    _theme: str
    _confidence: float
    _keywords: List[str]
    _sentiment: Optional[str] = None


@dataclass
class RAGState:
    """State of RAG operations."""

    _query: str
    _retrieved_docs: List[Dict[str, Any]]
    _context: str
    _response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CircuitState(str, Enum):
    """Circuit breaker state."""


# Exception classes
class AgenticWorkflowError(Exception):
    """Base exception for agentic workflow."""


class HopExecutionError(AgenticWorkflowError):
    """Error in hop execution."""


class ValidationError(AgenticWorkflowError):
    """Validation error."""


class APIError(AgenticWorkflowError):
    """API-related error."""


class CircuitBreakerOpenError(AgenticWorkflowError):
    """Circuit breaker is open."""