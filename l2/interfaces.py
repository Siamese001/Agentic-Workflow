"""L2 Interfaces for resume processing execution layer.

Defines abstract interfaces for L2 execution operations to ensure
consistent resume improvement and job alignment workflows.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar

from core.models.models import (
    StrategyResult,
    DraftingResult,
    QAResult,
    SafetyResult,
    RAGResult,
    Evidence,
    LLMRequest,
    LLMResponse,
)

T = TypeVar('T')


@dataclass
class L2ExecutionRequest:
    """
    Input request for L2 resume processing execution operations.

    Ensures structured input for consistent resume improvement workflows.
    """
    plan_id: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L2ExecutionResult:
    """
    Output result from L2 resume processing execution operations.

    Provides structured output for resume enhancement and job alignment.
    """
    success: bool
    data: Any
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None
    
    @classmethod
    def success_result(cls, data: T, message: str = "Execution completed successfully") -> L2ExecutionResult:
        """Create a successful result"""
        return cls(
            success=True,
            data=data,
            metadata={"message": message}
        )
    
    @classmethod
    def failure_result(cls, message: str, error_code: Optional[str] = None) -> L2ExecutionResult:
        """Create a failure result"""
        return cls(
            success=False,
            data=None,
            metadata={"message": message, "error_code": error_code},
            errors=[message] if message else None
        )
    
    @classmethod
    def timeout_result(cls, message: str = "Execution timed out") -> L2ExecutionResult:
        """Create a timeout result"""
        return cls(
            success=False,
            data=None,
            metadata={"message": message, "error_code": "TIMEOUT"},
            errors=[message]
        )


class L2ExecutorInterface(ABC):
    """
    Abstract interface for L2 resume processing execution operations.

    Ensures consistent execution patterns for resume improvement workflows.
    """
    
    @abstractmethod
    async def execute(self, request: L2ExecutionRequest) -> L2ExecutionResult:
        """Executes planned resume processing operation."""
        pass
    
    @abstractmethod
    async def validate_request(self, request: L2ExecutionRequest) -> bool:
        """Validates resume processing execution request."""
        pass


class L2LLMExecutorInterface(L2ExecutorInterface):
    """
    Interface for LLM model execution in resume processing.

    Ensures consistent LLM invocation for resume improvement workflows.
    """
    
    @abstractmethod
    async def invoke_llm(self, request: LLMRequest) -> LLMResponse:
        """Invokes LLM model for resume processing operations."""
        pass
    
    @abstractmethod
    async def validate_llm_request(self, request: LLMRequest) -> bool:
        """Validates LLM request parameters for resume processing."""
        pass


class L2StrategyExecutorInterface(L2LLMExecutorInterface):
    """
    Interface for resume strategy execution operations.

    Ensures consistent strategy execution for resume job alignment.
    """
    
    @abstractmethod
    async def execute_strategy(self, request: L2ExecutionRequest) -> StrategyResult:
        """Executes resume strategy planning result for job alignment."""
        pass


class L2DraftingExecutorInterface(L2LLMExecutorInterface):
    """
    Interface for resume drafting execution operations.

    Ensures consistent drafting for resume improvement workflows.
    """
    
    @abstractmethod
    async def execute_drafting(self, request: L2ExecutionRequest) -> DraftingResult:
        """Executes resume content drafting for job alignment."""
        pass


class L2QAExecutorInterface(L2LLMExecutorInterface):
    """
    Interface for resume QA execution operations.

    Ensures consistent quality assurance for resume improvement.
    """
    
    @abstractmethod
    async def execute_qa(self, request: L2ExecutionRequest) -> QAResult:
        """Executes resume quality assurance evaluation for job alignment."""
        pass


class L2SafetyExecutorInterface(L2LLMExecutorInterface):
    """
    Interface for resume safety execution operations.

    Ensures consistent safety validation for resume processing workflows.
    """
    
    @abstractmethod
    async def execute_safety(self, request: L2ExecutionRequest) -> SafetyResult:
        """Executes resume safety evaluation for job alignment compliance."""
        pass


class L2RetrievalExecutorInterface(L2ExecutorInterface):
    """
    Interface for resume retrieval operations.

    Ensures consistent data retrieval for resume improvement workflows.
    """
    
    @abstractmethod
    async def retrieve(self, query: str, context: Dict[str, Any]) -> RAGResult:
        """Retrieves relevant resume documents for job alignment."""
        pass
    
    @abstractmethod
    async def hybrid_search(self, query: str, filters: Dict[str, Any]) -> List[Evidence]:
        """Performs hybrid search for resume enhancement data."""
        pass


class L2ToolExecutorInterface(L2ExecutorInterface):
    """
    Interface for generic resume processing tool execution operations.

    Ensures consistent tool execution for resume improvement workflows.
    """
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> L2ExecutionResult:
        """Executes resume processing tool with given parameters."""
        pass
    
    @abstractmethod
    async def list_available_tools(self) -> List[str]:
        """Lists all available resume processing tools."""
        pass


# =============================================================================
# Tool Injection Defense (ID 7) - L2 Boundary Validation
# =============================================================================

@dataclass
class ToolOutputValidationResult:
    """
    Result of tool output validation for resume processing injection defense.

    Ensures secure tool execution for resume improvement workflows.
    """
    
    is_safe: bool
    original_output: Any
    sanitized_output: Optional[Any] = None
    detected_threats: Optional[List[str]] = None
    confidence: float = 1.0


class L2ToolOutputValidatorInterface(ABC):
    """
    Interface for validating resume processing tool outputs at L2 boundary.

    Defends against injection attacks by validating all tool outputs
    for secure resume improvement workflows.
    """
    
    @abstractmethod
    def validate_tool_output(self, tool_name: str, output: Any) -> ToolOutputValidationResult:
        """
        Validates resume processing tool output for injection attacks.

        Ensures secure execution for resume improvement workflows.
        """
        pass
    
    @abstractmethod
    def sanitize_output(self, output: Any) -> Any:
        """
        Sanitizes tool output by removing malicious content.

        Protects resume processing workflows from security threats.
        """
        pass
    
    @abstractmethod
    def detect_injection_patterns(self, content: str) -> List[str]:
        """
        Detects injection patterns in resume processing tool outputs.

        Identifies threats to protect resume improvement workflows.
        """
        pass
