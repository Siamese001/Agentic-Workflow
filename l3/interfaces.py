"""
L3 interfaces for resume workflow orchestration.

Defines abstract interfaces for resume job alignment coordination.
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
    """Execution modes for resume workflow orchestration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


@dataclass
class L3OrchestrationRequest:
    """Input request for resume workflow orchestration operations."""
    plan_bundle: WorkflowPlanBundle
    execution_context: ExecutionContext
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class L3OrchestrationResult:
    """Output result from resume workflow orchestration operations."""
    success: bool
    status: WorkflowStatus
    results: List[NodeResult]
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None


class L3OrchestratorInterface(ABC):
    """Abstract interface for resume workflow orchestration operations."""
    
    @abstractmethod
    async def orchestrate_workflow(self, request: L3OrchestrationRequest) -> L3OrchestrationResult:
        """Orchestrates resume workflow execution for job alignment."""
        pass
    
    @abstractmethod
    async def create_dag(self, plan: WorkflowPlanBundle) -> tuple[List[DAGNode], List[DAGEdge]]:
        """Creates resume workflow DAG for job alignment processing."""
        pass
    
    @abstractmethod
    async def validate_dag(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> bool:
        """Validates resume workflow DAG structure for job alignment."""
        pass


class L3DAGExecutorInterface(ABC):
    """Interface for resume workflow DAG execution operations."""
    
    @abstractmethod
    async def execute_dag(self, nodes: List[DAGNode], edges: List[DAGEdge], context: ExecutionContext) -> List[NodeResult]:
        """Executes resume workflow DAG for job alignment processing."""
        pass
    
    @abstractmethod
    async def execute_node(self, node: DAGNode, context: ExecutionContext) -> NodeResult:
        """Executes single resume workflow DAG node for job alignment."""
        pass
    
    @abstractmethod
    async def handle_node_failure(self, node: DAGNode, error: Exception, context: ExecutionContext) -> bool:
        """Handles resume workflow node failure for job alignment recovery."""
        pass


class L3ConcurrencyControllerInterface(ABC):
    """Interface for resume workflow concurrency control operations."""
    
    @abstractmethod
    async def schedule_parallel_execution(self, nodes: List[DAGNode], context: ExecutionContext) -> List[NodeResult]:
        """Schedules parallel resume workflow execution for job alignment."""
        pass
    
    @abstractmethod
    async def manage_resource_limits(self, active_executions: List[Awaitable]) -> List[Awaitable]:
        """Manages resource limits for resume workflow concurrent execution."""
        pass
    
    @abstractmethod
    async def resolve_dependencies(self, node: DAGNode, completed_results: List[NodeResult]) -> bool:
        """Checks resume workflow node dependencies for job alignment."""
        pass


class L3ErrorHandlerInterface(ABC):
    """Interface for resume workflow error handling and recovery operations."""
    
    @abstractmethod
    async def handle_execution_error(self, error: Exception, context: ExecutionContext) -> bool:
        """Handles resume workflow execution errors for job alignment."""
        pass
    
    @abstractmethod
    async def attempt_recovery(self, failed_nodes: List[DAGNode], context: ExecutionContext) -> List[NodeResult]:
        """Attempts resume workflow recovery for job alignment processing."""
        pass
    
    @abstractmethod
    async def rollback_execution(self, completed_nodes: List[DAGNode], context: ExecutionContext) -> bool:
        """Rollbacks resume workflow executions for job alignment recovery."""
        pass


class L3ResourceMonitorInterface(ABC):
    """Interface for resume workflow resource monitoring operations."""
    
    @abstractmethod
    async def monitor_resource_usage(self, execution_id: str) -> Dict[str, Any]:
        """Monitors resume workflow resource usage for job alignment."""
        pass
    
    @abstractmethod
    async def enforce_resource_limits(self, limits: Dict[str, Any], current_usage: Dict[str, Any]) -> bool:
        """Enforces resource limits during resume workflow execution."""
        pass
    
    @abstractmethod
    async def optimize_execution_plan(self, nodes: List[DAGNode], resource_constraints: Dict[str, Any]) -> List[DAGNode]:
        """Optimizes resume workflow execution plan for job alignment."""
        pass
