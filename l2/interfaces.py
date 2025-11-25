"""L2 Interfaces - Execution Layer

This module defines abstract interfaces for all L2 execution operations.
All L2 implementations must inherit from these interfaces.

Layer: L2 (Execution)
Responsibilities:
- Tool execution and API calls
- LLM model invocation
- Data retrieval and processing
- External service interactions

Non-responsibilities:
- Planning (L1)
- Orchestration (L3)
- State management (L4)
- Safety/policy decisions (L5)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass

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


@dataclass
class L2ExecutionRequest:
    """Input request for L2 execution operations."""
    plan_id: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L2ExecutionResult:
    """Output result from L2 execution operations."""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None


class L2ExecutorInterface(ABC):
    """Abstract interface for all L2 execution operations."""
    
    @abstractmethod
    async def execute(self, request: L2ExecutionRequest) -> L2ExecutionResult:
        """Execute a planned operation."""
        pass
    
    @abstractmethod
    async def validate_request(self, request: L2ExecutionRequest) -> bool:
        """Validate execution request before processing."""
        pass


class L2LLMExecutorInterface(L2ExecutorInterface):
    """Interface for LLM model execution operations."""
    
    @abstractmethod
    async def invoke_llm(self, request: LLMRequest) -> LLMResponse:
        """Invoke an LLM model with the given request."""
        pass
    
    @abstractmethod
    async def validate_llm_request(self, request: LLMRequest) -> bool:
        """Validate LLM request parameters."""
        pass


class L2StrategyExecutorInterface(L2LLMExecutorInterface):
    """Interface for strategy execution operations."""
    
    @abstractmethod
    async def execute_strategy(self, request: L2ExecutionRequest) -> StrategyResult:
        """Execute strategy planning result."""
        pass


class L2DraftingExecutorInterface(L2LLMExecutorInterface):
    """Interface for drafting execution operations."""
    
    @abstractmethod
    async def execute_drafting(self, request: L2ExecutionRequest) -> DraftingResult:
        """Execute content drafting."""
        pass


class L2QAExecutorInterface(L2LLMExecutorInterface):
    """Interface for QA execution operations."""
    
    @abstractmethod
    async def execute_qa(self, request: L2ExecutionRequest) -> QAResult:
        """Execute quality assurance evaluation."""
        pass


class L2SafetyExecutorInterface(L2LLMExecutorInterface):
    """Interface for safety execution operations."""
    
    @abstractmethod
    async def execute_safety(self, request: L2ExecutionRequest) -> SafetyResult:
        """Execute safety evaluation."""
        pass


class L2RetrievalExecutorInterface(L2ExecutorInterface):
    """Interface for retrieval operations."""
    
    @abstractmethod
    async def retrieve(self, query: str, context: Dict[str, Any]) -> RAGResult:
        """Retrieve relevant documents/information."""
        pass
    
    @abstractmethod
    async def hybrid_search(self, query: str, filters: Dict[str, Any]) -> List[Evidence]:
        """Perform hybrid vector + keyword search."""
        pass


class L2ToolExecutorInterface(L2ExecutorInterface):
    """Interface for generic tool execution operations."""
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> L2ExecutionResult:
        """Execute a specific tool with given parameters."""
        pass
    
    @abstractmethod
    async def list_available_tools(self) -> List[str]:
        """List all available tools for this executor."""
        pass
