"""L3 Adapter - Wraps UnifiedWorkflowOrchestrator to implement L3OrchestratorInterface

This adapter provides backward compatibility while enforcing strict interface contracts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from l3.interfaces import (
    L3OrchestratorInterface,
    L3DAGExecutorInterface,
    L3OrchestrationRequest,
    L3OrchestrationResult,
    ExecutionMode,
)
from l3.unified_workflow_orchestrator import UnifiedWorkflowOrchestrator
from core.models.models import (
    WorkflowPlanBundle,
    ExecutionContext,
    L2ResultBundle,
    WorkflowStatus,
    NodeResult,
    DAGNode,
    DAGEdge,
)


class UnifiedWorkflowOrchestratorAdapter(L3OrchestratorInterface):
    """Adapter that wraps UnifiedWorkflowOrchestrator to implement L3 interface."""
    
    def __init__(self, wrapped_orchestrator: UnifiedWorkflowOrchestrator):
        self.wrapped_orchestrator = wrapped_orchestrator
    
    async def orchestrate_workflow(self, request: L3OrchestrationRequest) -> L3OrchestrationResult:
        """Orchestrate workflow using wrapped implementation."""
        try:
            # Convert interface request to internal format
            job_data = {
                "mission": request.plan_bundle.mission,
                "plan": request.plan_bundle,
                "context": request.execution_context,
                "mode": request.mode.value,
                "constraints": request.constraints,
            }
            
            # Execute using wrapped orchestrator
            result = self.wrapped_orchestrator.orchestrate_full_workflow(
                job=job_data,
                resume=None,  # TODO: Map from request
                config={}  # TODO: Map from request
            )
            
            # Convert result to interface format
            return L3OrchestrationResult(
                success=result.get("success", False),
                status=WorkflowStatus.COMPLETED if result.get("success") else WorkflowStatus.FAILED,
                results=self._convert_to_node_results(result.get("results", [])),
                metadata=result.get("metadata", {}),
                errors=result.get("errors"),
            )
            
        except Exception as e:
            return L3OrchestrationResult(
                success=False,
                status=WorkflowStatus.FAILED,
                results=[],
                metadata={"error": str(e)},
                errors=[str(e)],
            )
    
    async def create_dag(self, plan: WorkflowPlanBundle) -> tuple[List[DAGNode], List[DAGEdge]]:
        """Create DAG from workflow plan."""
        # Delegate to wrapped orchestrator's DAG creation logic
        # This is a simplified implementation - the actual logic would be in UnifiedWorkflowOrchestrator
        nodes = []
        edges = []
        
        # Create nodes for each step in the plan
        for i, step in enumerate(plan.steps):
            node = DAGNode(
                id=f"node_{i}",
                type=step.step_type,
                parameters=step.parameters,
                dependencies=step.dependencies,
            )
            nodes.append(node)
        
        # Create edges based on dependencies
        for node in nodes:
            for dep_id in node.dependencies:
                edge = DAGEdge(from_node=dep_id, to_node=node.id)
                edges.append(edge)
        
        return nodes, edges
    
    async def validate_dag(self, nodes: List[DAGNode], edges: List[DAGEdge]) -> bool:
        """Validate DAG structure and dependencies."""
        # Basic validation - check for cycles and missing dependencies
        node_ids = {node.id for node in nodes}
        
        # Check all dependencies exist
        for node in nodes:
            for dep_id in node.dependencies:
                if dep_id not in node_ids:
                    return False
        
        # Check for cycles (simplified)
        # In a real implementation, this would use proper cycle detection
        return True
    
    def _convert_to_node_results(self, internal_results: List[Any]) -> List[NodeResult]:
        """Convert internal result format to NodeResult format."""
        node_results = []
        for i, result in enumerate(internal_results):
            node_result = NodeResult(
                node_id=f"node_{i}",
                success=result.get("success", False),
                data=result.get("data"),
                metadata=result.get("metadata", {}),
                error=result.get("error"),
            )
            node_results.append(node_result)
        return node_results
