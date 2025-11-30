"""L3 Orchestration Engine - Robust Implementation

Coordinates workflow orchestration for both resume and outreach pipelines.
This layer provides robust orchestration capabilities with proper state management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime

# Re-export robust implementations from engines
from agentic_core.outreach_engine.l3_orchestration.orchestrators.lic_orchestrator import (
    LICOrchestrator,
    RecipientProfile,
    LICPipelineResult,
)  # noqa: F401
from agentic_core.outreach_engine.l3_orchestration.orchestrators.lic_outreach_orchestrator import (
    OutreachOrchestrator,
)  # noqa: F401
from agentic_core.resume_engine.l3_orchestration.orchestrators.rg_kg_retrieval_orchestrator import (
    ResumeKGOrchestrator,
)  # noqa: F401

# Import L2 execution for coordination
from ..l2_execution import ExecutionEngine, ExecutionPlan, ExecutionResult

class OrchestrationStatus(str, Enum):
    """Orchestration status for workflow tracking."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowType(str, Enum):
    """Types of workflows supported."""
    RESUME_GENERATION = "resume_generation"
    OUTREACH_PERSONALIZED = "outreach_personalized"
    OUTREACH_BULK = "outreach_bulk"
    HYBRID_WORKFLOW = "hybrid_workflow"

@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    step_id: str
    name: str
    step_type: str
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    status: OrchestrationStatus = OrchestrationStatus.INITIALIZING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow."""
    workflow_id: str
    name: str
    workflow_type: WorkflowType
    steps: List[WorkflowStep]
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class OrchestrationResult:
    """Result of workflow orchestration."""
    workflow_id: str
    status: OrchestrationStatus
    completed_steps: List[str]
    failed_steps: List[str]
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None

class OrchestrationEngine:
    """
    Core L3 orchestration coordinator with robust implementations.
    
    Manages workflow execution, step dependencies, and state coordination
    between L1 planning and L2 execution layers.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized orchestrators
        self.lic_orchestrator = LICOrchestrator()
        self.outreach_orchestrator = OutreachOrchestrator()
        self.resume_orchestrator = ResumeKGOrchestrator()
        
        # Initialize execution engine
        self.execution_engine = ExecutionEngine()
        
        # State tracking
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_history: List[OrchestrationResult] = []
        self.step_results: Dict[str, Dict[str, Any]] = {}
    
    async def execute_workflow(
        self, 
        workflow: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """
        Execute a complete workflow with step dependency management.
        
        Args:
            workflow: Workflow definition with steps
            context: Execution context
            
        Returns:
            Orchestration result with step outcomes
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.active_workflows[workflow.workflow_id] = workflow
            
            if workflow.workflow_type == WorkflowType.RESUME_GENERATION:
                result = await self._execute_resume_workflow(workflow, context)
            elif workflow.workflow_type == WorkflowType.OUTREACH_PERSONALIZED:
                result = await self._execute_outreach_workflow(workflow, context)
            elif workflow.workflow_type == WorkflowType.OUTREACH_BULK:
                result = await self._execute_bulk_outreach_workflow(workflow, context)
            elif workflow.workflow_type == WorkflowType.HYBRID_WORKFLOW:
                result = await self._execute_hybrid_workflow(workflow, context)
            else:
                raise ValueError(f"Unknown workflow type: {workflow.workflow_type}")
            
            execution_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            result.execution_time_ms = execution_time
            
            self.workflow_history.append(result)
            return result
            
        except Exception as e:
            execution_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            error_result = OrchestrationResult(
                workflow_id=workflow.workflow_id,
                status=OrchestrationStatus.FAILED,
                completed_steps=[],
                failed_steps=[step.step_id for step in workflow.steps],
                results={},
                metadata={"workflow": workflow.config},
                error=str(e),
                execution_time_ms=execution_time
            )
            
            self.workflow_history.append(error_result)
            return error_result
        
        finally:
            self.active_workflows.pop(workflow.workflow_id, None)
    
    async def _execute_resume_workflow(
        self, 
        workflow: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """Execute resume generation workflow."""
        completed_steps = []
        failed_steps = []
        results = {}
        
        # Execute steps in dependency order
        for step in self._resolve_dependencies(workflow.steps):
            try:
                step.status = OrchestrationStatus.RUNNING
                
                if step.step_type == "resume_planning":
                    step_result = await self.resume_orchestrator.plan_resume(step.config, context)
                elif step.step_type == "resume_generation":
                    step_result = await self.resume_orchestrator.generate_resume(step.config, context)
                elif step.step_type == "resume_validation":
                    step_result = await self.resume_orchestrator.validate_resume(step.config, context)
                else:
                    # Use execution engine for generic steps
                    execution_plan = ExecutionPlan(
                        plan_id=f"{workflow.workflow_id}-{step.step_id}",
                        tasks=[step.config],
                        config=step.config
                    )
                    execution_results = await self.execution_engine.execute_plan(execution_plan, context)
                    step_result = execution_results[0].payload if execution_results else {}
                
                step.result = step_result
                step.status = OrchestrationStatus.COMPLETED
                completed_steps.append(step.step_id)
                results[step.step_id] = step_result
                
            except Exception as e:
                step.error = str(e)
                step.status = OrchestrationStatus.FAILED
                failed_steps.append(step.step_id)
                self.logger.error(f"Step {step.step_id} failed: {e}")
        
        overall_status = OrchestrationStatus.COMPLETED if not failed_steps else OrchestrationStatus.FAILED
        
        return OrchestrationResult(
            workflow_id=workflow.workflow_id,
            status=overall_status,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            results=results,
            metadata={"workflow_type": "resume_generation"}
        )
    
    async def _execute_outreach_workflow(
        self, 
        workflow: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """Execute personalized outreach workflow."""
        completed_steps = []
        failed_steps = []
        results = {}
        
        for step in self._resolve_dependencies(workflow.steps):
            try:
                step.status = OrchestrationStatus.RUNNING
                
                if step.step_type == "recipient_research":
                    step_result = await self.lic_orchestrator.research_recipient(step.config, context)
                elif step.step_type == "message_generation":
                    step_result = await self.outreach_orchestrator.generate_message(step.config, context)
                elif step.step_type == "message_validation":
                    step_result = await self.lic_orchestrator.validate_message(step.config, context)
                else:
                    execution_plan = ExecutionPlan(
                        plan_id=f"{workflow.workflow_id}-{step.step_id}",
                        tasks=[step.config],
                        config=step.config
                    )
                    execution_results = await self.execution_engine.execute_plan(execution_plan, context)
                    step_result = execution_results[0].payload if execution_results else {}
                
                step.result = step_result
                step.status = OrchestrationStatus.COMPLETED
                completed_steps.append(step.step_id)
                results[step.step_id] = step_result
                
            except Exception as e:
                step.error = str(e)
                step.status = OrchestrationStatus.FAILED
                failed_steps.append(step.step_id)
                self.logger.error(f"Step {step.step_id} failed: {e}")
        
        overall_status = OrchestrationStatus.COMPLETED if not failed_steps else OrchestrationStatus.FAILED
        
        return OrchestrationResult(
            workflow_id=workflow.workflow_id,
            status=overall_status,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            results=results,
            metadata={"workflow_type": "outreach_personalized"}
        )
    
    async def _execute_bulk_outreach_workflow(
        self, 
        workflow: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """Execute bulk outreach workflow."""
        # Similar to personalized but optimized for volume
        return await self._execute_outreach_workflow(workflow, context)
    
    async def _execute_hybrid_workflow(
        self, 
        workflow: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """Execute hybrid workflow combining resume and outreach."""
        # Execute resume steps first, then outreach
        resume_steps = [s for s in workflow.steps if "resume" in s.step_type]
        outreach_steps = [s for s in workflow.steps if "outreach" in s.step_type]
        
        # Create sub-workflows
        resume_workflow = WorkflowDefinition(
            workflow_id=f"{workflow.workflow_id}-resume",
            name="Resume Sub-workflow",
            workflow_type=WorkflowType.RESUME_GENERATION,
            steps=resume_steps,
            config=workflow.config
        )
        
        outreach_workflow = WorkflowDefinition(
            workflow_id=f"{workflow.workflow_id}-outreach",
            name="Outreach Sub-workflow", 
            workflow_type=WorkflowType.OUTREACH_PERSONALIZED,
            steps=outreach_steps,
            config=workflow.config
        )
        
        # Execute sequentially
        resume_result = await self._execute_resume_workflow(resume_workflow, context)
        
        # Use resume results in outreach context
        enhanced_context = {**context, **resume_result.results}
        outreach_result = await self._execute_outreach_workflow(outreach_workflow, enhanced_context)
        
        # Combine results
        return OrchestrationResult(
            workflow_id=workflow.workflow_id,
            status=OrchestrationStatus.COMPLETED if not (resume_result.failed_steps + outreach_result.failed_steps) else OrchestrationStatus.FAILED,
            completed_steps=resume_result.completed_steps + outreach_result.completed_steps,
            failed_steps=resume_result.failed_steps + outreach_result.failed_steps,
            results={**resume_result.results, **outreach_result.results},
            metadata={"workflow_type": "hybrid_workflow"}
        )
    
    def _resolve_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Resolve step dependencies and return execution order."""
        # Simple topological sort for now
        resolved = []
        remaining = steps.copy()
        
        while remaining:
            # Find steps with no unresolved dependencies
            ready = [
                step for step in remaining
                if all(dep in [s.step_id for s in resolved] for dep in step.dependencies)
            ]
            
            if not ready:
                raise ValueError("Circular dependency detected in workflow steps")
            
            resolved.extend(ready)
            for step in ready:
                remaining.remove(step)
        
        return resolved
    
    def get_workflow_history(self) -> List[OrchestrationResult]:
        """Get the workflow execution history."""
        return self.workflow_history.copy()
    
    def get_active_workflows(self) -> Dict[str, WorkflowDefinition]:
        """Get currently active workflows."""
        return self.active_workflows.copy()

# Global orchestration engine instance
_global_orchestration_engine: Optional[OrchestrationEngine] = None

def get_orchestration_engine(config: Optional[Dict[str, Any]] = None) -> OrchestrationEngine:
    """Get the global orchestration engine instance."""
    global _global_orchestration_engine
    if _global_orchestration_engine is None:
        _global_orchestration_engine = OrchestrationEngine(config)
    return _global_orchestration_engine

def reset_orchestration_engine() -> None:
    """Reset the global orchestration engine instance (for testing)."""
    global _global_orchestration_engine
    _global_orchestration_engine = None

__all__ = [
    "OrchestrationStatus",
    "WorkflowType",
    "WorkflowStep",
    "WorkflowDefinition", 
    "OrchestrationResult",
    "OrchestrationEngine",
    "get_orchestration_engine",
    "reset_orchestration_engine",
]
