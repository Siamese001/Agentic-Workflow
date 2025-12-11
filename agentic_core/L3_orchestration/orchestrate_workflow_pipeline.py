# Ownership: agentic_core / L3_orchestration
# -*- coding: utf-8 -*-
"""Workflow Pipeline Orchestrator - Coordinates multi-stage workflow execution and management.

This orchestrator manages the planning phase for workflow operations,
including stage definition, dependency management, and pipeline optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Types of pipeline stages."""
    INPUT = "input"
    PROCESSING = "processing"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    OUTPUT = "output"
    CLEANUP = "cleanup"


class ExecutionMode(Enum):
    """Pipeline execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCH = "batch"
    STREAMING = "streaming"


class StageStatus(Enum):
    """Status of pipeline stages."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStageDefinition:
    """Definition of a pipeline stage."""
    id: str
    name: str
    stage_type: PipelineStage
    handler: str  # Function or module name
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    condition: Optional[str] = None


@dataclass
class PipelineFlow:
    """Definition of pipeline flow."""
    stages: List[PipelineStageDefinition]
    execution_mode: ExecutionMode
    error_handling: str = "stop"  # stop, continue, retry
    checkpoint_frequency: int = 0
    rollback_on_failure: bool = False


@dataclass
class WorkflowPipelineConfig:
    """Configuration for workflow pipeline orchestrator."""
    enable_checkpoints: bool = True
    enable_parallel_stages: bool = True
    enable_streaming: bool = False
    max_concurrent_stages: int = 5
    default_timeout: int = 300
    log_level: str = "INFO"


@dataclass
class WorkflowPipelineResult:
    """Result of workflow pipeline orchestration."""
    success: bool
    pipeline_flow: Optional[PipelineFlow] = None
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    stage_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_duration: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowPipelineOrchestrator:
    """Orchestrator for planning workflow pipeline operations."""

    def __init__(self, config: Optional[WorkflowPipelineConfig] = None):
        self.config = config or WorkflowPipelineConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, pipeline_request: Dict[str, Any]) -> WorkflowPipelineResult:
        """Execute the workflow pipeline orchestration.
        
        Args:
            pipeline_request: Dictionary containing pipeline requirements and stages
            
        Returns:
            WorkflowPipelineResult: Complete planning result with pipeline flow and execution plan
        """
        self.logger.info(f"Starting workflow pipeline planning for: {pipeline_request.get('pipeline_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(pipeline_request)
            
            # Parse pipeline stages
            stages = self._parse_pipeline_stages(pipeline_request)
            
            # Create pipeline flow
            pipeline_flow = self._create_pipeline_flow(pipeline_request, stages)
            
            # Generate execution plan
            execution_plan = self._generate_execution_plan(pipeline_flow)
            
            # Build stage dependencies
            stage_dependencies = self._build_stage_dependencies(stages)
            
            # Estimate duration
            estimated_duration = self._estimate_pipeline_duration(pipeline_flow)
            
            result = WorkflowPipelineResult(
                success=True,
                pipeline_flow=pipeline_flow,
                execution_plan=execution_plan,
                stage_dependencies=stage_dependencies,
                estimated_duration=estimated_duration,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "pipeline_name": pipeline_request.get("pipeline_name"),
                    "stage_count": len(stages),
                    "orchestrator": "WorkflowPipelineOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned workflow pipeline: {len(stages)} stages, {estimated_duration}s estimated")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow pipeline planning failed: {str(e)}")
            return WorkflowPipelineResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "WorkflowPipelineOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate workflow pipeline request."""
        if not request:
            raise ValueError("Pipeline request cannot be empty")
        
        if "pipeline_name" not in request:
            raise ValueError("Pipeline name is required in pipeline request")
        
        if "stages" not in request:
            raise ValueError("Stages are required in pipeline request")

    def _parse_pipeline_stages(self, request: Dict[str, Any]) -> List[PipelineStageDefinition]:
        """Parse pipeline stages from request."""
        stages = []
        raw_stages = request.get("stages", [])
        
        for raw_stage in raw_stages:
            if isinstance(raw_stage, dict):
                # Map strings to enums
                stage_mapping = {
                    "input": PipelineStage.INPUT,
                    "processing": PipelineStage.PROCESSING,
                    "transformation": PipelineStage.TRANSFORMATION,
                    "validation": PipelineStage.VALIDATION,
                    "output": PipelineStage.OUTPUT,
                    "cleanup": PipelineStage.CLEANUP
                }
                
                stage = PipelineStageDefinition(
                    id=raw_stage.get("id", f"stage_{len(stages)}"),
                    name=raw_stage.get("name", "unnamed"),
                    stage_type=stage_mapping.get(
                        raw_stage.get("stage_type", "processing"),
                        PipelineStage.PROCESSING
                    ),
                    handler=raw_stage.get("handler", ""),
                    parameters=raw_stage.get("parameters", {}),
                    dependencies=raw_stage.get("dependencies", []),
                    retry_count=raw_stage.get("retry_count", 0),
                    max_retries=raw_stage.get("max_retries", 3),
                    timeout=raw_stage.get("timeout", self.config.default_timeout),
                    condition=raw_stage.get("condition")
                )
                stages.append(stage)
        
        return stages

    def _create_pipeline_flow(
        self, 
        request: Dict[str, Any], 
        stages: List[PipelineStageDefinition]
    ) -> PipelineFlow:
        """Create pipeline flow from request and stages."""
        # Map strings to enums
        execution_mapping = {
            "sequential": ExecutionMode.SEQUENTIAL,
            "parallel": ExecutionMode.PARALLEL,
            "batch": ExecutionMode.BATCH,
            "streaming": ExecutionMode.STREAMING
        }
        
        execution_mode = execution_mapping.get(
            request.get("execution_mode", "sequential"),
            ExecutionMode.SEQUENTIAL
        )
        
        return PipelineFlow(
            stages=stages,
            execution_mode=execution_mode,
            error_handling=request.get("error_handling", "stop"),
            checkpoint_frequency=request.get("checkpoint_frequency", 0),
            rollback_on_failure=request.get("rollback_on_failure", False)
        )

    def _generate_execution_plan(self, flow: PipelineFlow) -> Dict[str, Any]:
        """Generate execution plan from pipeline flow."""
        plan = {
            "execution_order": [],
            "parallel_groups": [],
            "checkpoints": [],
            "rollback_points": []
        }
        
        if flow.execution_mode == ExecutionMode.SEQUENTIAL:
            plan["execution_order"] = [stage.id for stage in flow.stages]
        elif flow.execution_mode == ExecutionMode.PARALLEL:
            # Group stages by dependencies
            plan["parallel_groups"] = self._group_stages_by_dependencies(flow.stages)
        elif flow.execution_mode == ExecutionMode.BATCH:
            # Create batches based on checkpoint frequency
            if flow.checkpoint_frequency > 0:
                for i in range(0, len(flow.stages), flow.checkpoint_frequency):
                    batch = flow.stages[i:i + flow.checkpoint_frequency]
                    plan["execution_order"].extend([s.id for s in batch])
                    plan["checkpoints"].append(batch[-1].id)
        
        # Add rollback points if enabled
        if flow.rollback_on_failure:
            plan["rollback_points"] = [stage.id for stage in flow.stages if stage.stage_type == PipelineStage.VALIDATION]
        
        return plan

    def _group_stages_by_dependencies(self, stages: List[PipelineStageDefinition]) -> List[List[str]]:
        """Group stages into parallel execution groups based on dependencies."""
        groups = []
        remaining = stages[:]
        
        while remaining:
            # Find stages with no unmet dependencies
            ready = []
            for stage in remaining:
                deps_met = all(
                    dep not in [s.id for s in remaining]
                    for dep in stage.dependencies
                )
                if deps_met:
                    ready.append(stage.id)
            
            if not ready:
                raise ValueError("Circular dependency detected in pipeline stages")
            
            groups.append(ready)
            remaining = [s for s in remaining if s.id not in ready]
        
        return groups

    def _build_stage_dependencies(self, stages: List[PipelineStageDefinition]) -> Dict[str, List[str]]:
        """Build dependency map for all stages."""
        dependencies = {}
        
        for stage in stages:
            dependencies[stage.id] = stage.dependencies
        
        return dependencies

    def _estimate_pipeline_duration(self, flow: PipelineFlow) -> int:
        """Estimate total pipeline duration."""
        if flow.execution_mode == ExecutionMode.SEQUENTIAL:
            return sum(stage.timeout for stage in flow.stages)
        elif flow.execution_mode == ExecutionMode.PARALLEL:
            # Find critical path
            critical_path = self._find_critical_path(flow.stages)
            return sum(
                next(s.timeout for s in flow.stages if s.id == stage_id)
                for stage_id in critical_path
            )
        else:
            # Rough estimate for batch/streaming
            return sum(stage.timeout for stage in flow.stages) // 2

    def _find_critical_path(self, stages: List[PipelineStageDefinition]) -> List[str]:
        """Find critical path through parallel stages."""
        # Simple implementation: return the longest chain
        visited = set()
        critical_path = []
        
        def dfs(stage_id: str, path: List[str]):
            if stage_id in visited:
                return
            
            visited.add(stage_id)
            path.append(stage_id)
            
            # Find dependent stages
            dependents = [
                s.id for s in stages 
                if stage_id in s.dependencies
            ]
            
            if not dependents:
                nonlocal critical_path
                if len(path) > len(critical_path):
                    critical_path = path[:]
            else:
                for dep in dependents:
                    dfs(dep, path[:])
        
        # Start from stages with no dependencies
        for stage in stages:
            if not stage.dependencies:
                dfs(stage.id, [])
        
        return critical_path


# Factory function for easy instantiation
def create_workflow_pipeline_orchestrator(
    enable_checkpoints: bool = True,
    enable_parallel_stages: bool = True,
    **kwargs
) -> WorkflowPipelineOrchestrator:
    """Create a configured workflow pipeline orchestrator."""
    config = WorkflowPipelineConfig(
        enable_checkpoints=enable_checkpoints,
        enable_parallel_stages=enable_parallel_stages,
        **kwargs
    )
    return WorkflowPipelineOrchestrator(config)


# Convenience function for direct usage
def orchestrate_workflow_pipeline(
    pipeline_name: str,
    stages: List[Dict[str, Any]],
    execution_mode: str = "sequential",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan workflow pipeline from simple parameters.
    
    Args:
        pipeline_name: Name of the pipeline
        stages: List of pipeline stage definitions
        execution_mode: Execution mode (sequential, parallel, batch, streaming)
        config: Optional orchestrator configuration overrides
        
    Returns:
        Dict: Planning result with pipeline flow and execution plan
    """
    # Build request
    request = {
        "pipeline_name": pipeline_name,
        "stages": stages,
        "execution_mode": execution_mode
    }
    
    # Create orchestrator and execute
    orchestrator_config = WorkflowPipelineConfig(**config) if config else None
    orchestrator = WorkflowPipelineOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "pipeline_flow": {
            "stages": [
                {
                    "id": s.id,
                    "name": s.name,
                    "stage_type": s.stage_type.value,
                    "handler": s.handler,
                    "parameters": s.parameters,
                    "dependencies": s.dependencies,
                    "retry_count": s.retry_count,
                    "max_retries": s.max_retries,
                    "timeout": s.timeout,
                    "condition": s.condition
                }
                for s in result.pipeline_flow.stages
            ],
            "execution_mode": result.pipeline_flow.execution_mode.value,
            "error_handling": result.pipeline_flow.error_handling,
            "checkpoint_frequency": result.pipeline_flow.checkpoint_frequency,
            "rollback_on_failure": result.pipeline_flow.rollback_on_failure
        } if result.pipeline_flow else None,
        "execution_plan": result.execution_plan,
        "stage_dependencies": result.stage_dependencies,
        "estimated_duration": result.estimated_duration,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


def get_orchestrate_workflow_pipeline_config() -> Dict[str, object]:
    """Get configuration for orchestrate_workflow_pipeline."""
    return {"enabled": True, "version": "2.0"}