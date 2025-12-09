"""L3 Interfaces - Orchestration Layer

This module defines abstract interfaces for all L3 orchestration operations.
All L3 implementations must inherit from these interfaces.

Layer: L3 (Orchestration)
Responsibilities:
- DAG construction and execution
- Workflow coordination
- Concurrency control
- Error handling and recovery
- Resource management

Non-responsibilities:
- Planning (L1)
- Tool execution (L2)
- State mutation (L4)
- Safety/policy decisions (L5)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from core.models.models import (
    WorkflowPlanBundle,
    ExecutionContext,
    L2ResultBundle,
    WorkflowStatus,
    NodeResult,
    DAGNode,
    DAGEdge,
)


class ExecutionMode(Enum):
    """Execution modes for orchestration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


@dataclass
class L3OrchestrationRequest:
    """Input request for L3 orchestration operations."""
    plan_bundle: WorkflowPlanBundle
    execution_context: ExecutionContext
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L3OrchestrationResult:
    """Output result from L3 orchestration operations."""
    success: bool
    status: WorkflowStatus
    results: List[NodeResult]
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None


class L3OrchestratorInterface(ABC):
    """Abstract interface for all L3 orchestration operations."""
    
    @abstractmethod
    async def orchestrate_workflow(self, request: L3OrchestrationRequest) -> L3OrchestrationResult:
        """Orchestrate the execution of a complete workflow."""
        pass
    
    @abstractmethod
    async def create_dag(self, plan: WorkflowPlanBundle) -> tuple[List[DAGNode], List[DAGEdge]]:
        """Create a DAG from a workflow plan."""
        pass
    
    @abstractmethod
    async def validate_dag(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> bool:
        """Validate DAG structure and dependencies."""
        pass


class L3DAGExecutorInterface(ABC):
    """Interface for DAG execution operations."""
    
    @abstractmethod
    async def execute_dag(self, nodes: List[DAGNode], edges: List[DAGEdge], context: ExecutionContext) -> List[NodeResult]:
        """Execute a DAG with given context."""
        pass
    
    @abstractmethod
    async def execute_node(self, node: DAGNode, context: ExecutionContext) -> NodeResult:
        """Execute a single DAG node."""
        pass
    
    @abstractmethod
    async def handle_node_failure(self, node: DAGNode, error: Exception, context: ExecutionContext) -> bool:
        """Handle node execution failure with retry/recovery logic."""
        pass


class L3ConcurrencyControllerInterface(ABC):
    """Interface for concurrency control operations."""
    
    @abstractmethod
    async def schedule_parallel_execution(self, nodes: List[DAGNode], context: ExecutionContext) -> List[NodeResult]:
        """Schedule and execute nodes in parallel."""
        pass
    
    @abstractmethod
    async def manage_resource_limits(self, active_executions: List[Awaitable]) -> List[Awaitable]:
        """Manage resource limits for concurrent executions."""
        pass
    
    @abstractmethod
    async def resolve_dependencies(self, node: DAGNode, completed_results: List[NodeResult]) -> bool:
        """Check if node dependencies are satisfied."""
        pass


class L3ErrorHandlerInterface(ABC):
    """Interface for error handling and recovery operations."""
    
    @abstractmethod
    async def handle_execution_error(self, error: Exception, context: ExecutionContext) -> bool:
        """Handle workflow-level execution errors."""
        pass
    
    @abstractmethod
    async def attempt_recovery(self, failed_nodes: List[DAGNode], context: ExecutionContext) -> List[NodeResult]:
        """Attempt to recover from failed executions."""
        pass
    
    @abstractmethod
    async def rollback_execution(self, completed_nodes: List[DAGNode], context: ExecutionContext) -> bool:
        """Rollback completed executions if needed."""
        pass


class L3ResourceMonitorInterface(ABC):
    """Interface for resource monitoring operations."""
    
    @abstractmethod
    async def monitor_resource_usage(self, execution_id: str) -> Dict[str, Any]:
        """Monitor resource usage for an execution."""
        pass
    
    @abstractmethod
    async def enforce_resource_limits(self, limits: Dict[str, Any], current_usage: Dict[str, Any]) -> bool:
        """Enforce resource limits during execution."""
        pass
    
    @abstractmethod
    async def optimize_execution_plan(self, nodes: List[DAGNode], resource_constraints: Dict[str, Any]) -> List[DAGNode]:
        """Optimize execution plan based on resource constraints."""
        pass
