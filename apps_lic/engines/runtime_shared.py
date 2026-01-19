from __future__ import annotations
"""
Runtime Shared Schemas (Phase 2C Residuals)
==========================================
This module serves as the centralized repository for residual models 
discovered during the Phase 2C sweep. These models are critical for 
the LLM response cycle, RAG state management, and workflow checkpoints.

Note: 'Residual' prefixes are maintained to prevent collisions with 
legacy Phase 1 models during the final migration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

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
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ==========================================
# LLM Response & Feedback
# ==========================================

@dataclass
class LLMResponse:
    """Standard LLM response format."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse:
    """Response from agent execution containing a residual message."""
    message: 'ResidualAgentMessage'
    success: bool
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

# ==========================================
# Validation & Configuration
# ==========================================

class ResidualValidationResult(BaseModel):
    """Validation result for data or operations (Residual Phase 2C)."""
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
    data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

# ==========================================
# Specialized Analysis & Retrieval
# ==========================================

@dataclass
class ThematicAnalysis:
    """Analysis of thematic content."""
    theme: str
    confidence: float
    keywords: List[str]
    sentiment: Optional[str] = None

@dataclass
class RAGState:
    """State of RAG (Retrieval-Augmented Generation) operations."""
    query: str
    retrieved_docs: List[Dict[str, Any]]
    context: str
    response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
