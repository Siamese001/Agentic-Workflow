"""Execution Planning Orchestrator - Coordinates execution workflow and process management operations.

This orchestrator manages the planning phase for execution operations,
including workflow definition, process sequencing, and execution strategy optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionType(Enum):
    """Types of execution workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"
    WORKFLOW = "workflow"


class ExecutionStatus(Enum):
    """Status of execution steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class RetryPolicy(Enum):
    """Retry policies for failed executions."""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CUSTOM = "custom"


@dataclass
class ExecutionStep:
    """Definition of an execution step."""
    id: str
    name: str
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_policy: RetryPolicy = RetryPolicy.NONE
    max_retries: int = 0
    retry_delay: int = 0
    on_failure: str = "stop"  # stop, continue, retry


@dataclass
class ExecutionCondition:
    """Condition for conditional execution."""
    expression: str
    expected_value: Any
    operator: str = "eq"  # eq, ne, gt, lt, gte, lte, in, not_in


@dataclass
class ExecutionBranch:
    """Branch in conditional execution."""
    condition: ExecutionCondition
    steps: List[ExecutionStep]
    else_steps: Optional[List[ExecutionStep]] = None


@dataclass
class ExecutionPlan:
    """Plan for execution workflow."""
    execution_type: ExecutionType
    steps: List[ExecutionStep]
    branches: List[ExecutionBranch] = field(default_factory=list)
    global_timeout: int = 3600
    retry_policy: RetryPolicy = RetryPolicy.NONE
    error_handling: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlanningConfig:
    """Configuration for execution planning orchestrator."""
    enable_parallel_execution: bool = True
    enable_retry_mechanism: bool = True
    enable_timeout_handling: bool = True
    max_concurrent_steps: int = 5
    default_timeout: int = 300
    log_level: str = "INFO"


@dataclass
class ExecutionPlanningResult:
    """Result of execution planning orchestration."""
    success: bool
    execution_plan: Optional[ExecutionPlan] = None
    execution_graph: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: int = 0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionPlanningOrchestrator:
    """Orchestrator for planning execution operations."""

    def __init__(self, config: Optional[ExecutionPlanningConfig] = None):
        self.config = config or ExecutionPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, execution_request: Dict[str, Any]) -> ExecutionPlanningResult:
        """Execute the execution planning orchestration.
        
        Args:
            execution_request: Dictionary containing execution requirements and workflow
            
        Returns:
            ExecutionPlanningResult: Complete planning result with execution plan and graph
        """
        self.logger.info(f"Starting execution planning for: {execution_request.get('workflow_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(execution_request)
            
            # Parse execution steps
            steps = self._parse_execution_steps(execution_request)
            
            # Parse execution branches if conditional
            branches = self._parse_execution_branches(execution_request)
            
            # Create execution plan
            execution_plan = self._create_execution_plan(execution_request, steps, branches)
            
            # Generate execution graph
            execution_graph = self._generate_execution_graph(execution_plan)
            
            # Estimate duration
            estimated_duration = self._estimate_execution_duration(execution_plan)
            
            # Calculate resource requirements
            resource_requirements = self._calculate_resource_requirements(execution_plan)
            
            result = ExecutionPlanningResult(
                success=True,
                execution_plan=execution_plan,
                execution_graph=execution_graph,
                estimated_duration=estimated_duration,
                resource_requirements=resource_requirements,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "workflow_name": execution_request.get("workflow_name"),
                    "step_count": len(steps),
                    "branch_count": len(branches),
                    "orchestrator": "ExecutionPlanningOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned execution: {len(steps)} steps, {estimated_duration}s estimated")
            return result
            
        except Exception as e:
            self.logger.error(f"Execution planning failed: {str(e)}")
            return ExecutionPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "ExecutionPlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate execution planning request."""
        if not request:
            raise ValueError("Execution request cannot be empty")
        
        if "workflow_name" not in request:
            raise ValueError("Workflow name is required in execution request")
        
        if "execution_type" not in request:
            raise ValueError("Execution type is required in execution request")

    def _parse_execution_steps(self, request: Dict[str, Any]) -> List[ExecutionStep]:
        """Parse execution steps from request."""
        steps = []
        raw_steps = request.get("steps", [])
        
        for raw_step in raw_steps:
            if isinstance(raw_step, dict):
                # Map strings to enums
                retry_mapping = {
                    "none": RetryPolicy.NONE,
                    "fixed": RetryPolicy.FIXED,
                    "exponential": RetryPolicy.EXPONENTIAL,
                    "linear": RetryPolicy.LINEAR,
                    "custom": RetryPolicy.CUSTOM
                }
                
                step = ExecutionStep(
                    id=raw_step.get("id", f"step_{len(steps)}"),
                    name=raw_step.get("name", "unnamed"),
                    command=raw_step.get("command", ""),
                    parameters=raw_step.get("parameters", {}),
                    dependencies=raw_step.get("dependencies", []),
                    timeout=raw_step.get("timeout", self.config.default_timeout),
                    retry_policy=retry_mapping.get(
                        raw_step.get("retry_policy", "none"),
                        RetryPolicy.NONE
                    ),
                    max_retries=raw_step.get("max_retries", 0),
                    retry_delay=raw_step.get("retry_delay", 0),
                    on_failure=raw_step.get("on_failure", "stop")
                )
                steps.append(step)
        
        return steps

    def _parse_execution_branches(self, request: Dict[str, Any]) -> List[ExecutionBranch]:
        """Parse execution branches from request."""
        branches = []
        raw_branches = request.get("branches", [])
        
        for raw_branch in raw_branches:
            if isinstance(raw_branch, dict):
                condition = ExecutionCondition(
                    expression=raw_branch.get("condition", {}).get("expression", ""),
                    expected_value=raw_branch.get("condition", {}).get("expected_value"),
                    operator=raw_branch.get("condition", {}).get("operator", "eq")
                )
                
                # Parse branch steps
                branch_steps = []
                for raw_step in raw_branch.get("steps", []):
                    if isinstance(raw_step, dict):
                        step = ExecutionStep(
                            id=raw_step.get("id", f"branch_step_{len(branch_steps)}"),
                            name=raw_step.get("name", "unnamed"),
                            command=raw_step.get("command", ""),
                            parameters=raw_step.get("parameters", {}),
                            dependencies=raw_step.get("dependencies", []),
                            timeout=raw_step.get("timeout", self.config.default_timeout)
                        )
                        branch_steps.append(step)
                
                # Parse else steps if present
                else_steps = None
                if "else_steps" in raw_branch:
                    else_steps = []
                    for raw_step in raw_branch.get("else_steps", []):
                        if isinstance(raw_step, dict):
                            step = ExecutionStep(
                                id=raw_step.get("id", f"else_step_{len(else_steps)}"),
                                name=raw_step.get("name", "unnamed"),
                                command=raw_step.get("command", ""),
                                parameters=raw_step.get("parameters", {}),
                                dependencies=raw_step.get("dependencies", []),
                                timeout=raw_step.get("timeout", self.config.default_timeout)
                            )
                            else_steps.append(step)
                
                branch = ExecutionBranch(
                    condition=condition,
                    steps=branch_steps,
                    else_steps=else_steps
                )
                branches.append(branch)
        
        return branches

    def _create_execution_plan(
        self, 
        request: Dict[str, Any], 
        steps: List[ExecutionStep], 
        branches: List[ExecutionBranch]
    ) -> ExecutionPlan:
        """Create execution plan from request, steps, and branches."""
        # Map strings to enums
        execution_mapping = {
            "sequential": ExecutionType.SEQUENTIAL,
            "parallel": ExecutionType.PARALLEL,
            "conditional": ExecutionType.CONDITIONAL,
            "pipeline": ExecutionType.PIPELINE,
            "workflow": ExecutionType.WORKFLOW
        }
        
        retry_mapping = {
            "none": RetryPolicy.NONE,
            "fixed": RetryPolicy.FIXED,
            "exponential": RetryPolicy.EXPONENTIAL,
            "linear": RetryPolicy.LINEAR,
            "custom": RetryPolicy.CUSTOM
        }
        
        execution_type = execution_mapping.get(
            request.get("execution_type", "sequential"),
            ExecutionType.SEQUENTIAL
        )
        
        return ExecutionPlan(
            execution_type=execution_type,
            steps=steps,
            branches=branches,
            global_timeout=request.get("global_timeout", 3600),
            retry_policy=retry_mapping.get(
                request.get("retry_policy", "none"),
                RetryPolicy.NONE
            ),
            error_handling=request.get("error_handling", {}),
            metadata=request.get("metadata", {})
        )

    def _generate_execution_graph(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Generate execution graph from plan."""
        graph = {
            "nodes": [],
            "edges": [],
            "execution_order": []
        }
        
        # Add nodes for each step
        for step in plan.steps:
            node = {
                "id": step.id,
                "name": step.name,
                "type": "step",
                "command": step.command,
                "timeout": step.timeout
            }
            graph["nodes"].append(node)
        
        # Add edges for dependencies
        for step in plan.steps:
            for dep in step.dependencies:
                edge = {
                    "from": dep,
                    "to": step.id,
                    "type": "dependency"
                }
                graph["edges"].append(edge)
        
        # Determine execution order
        if plan.execution_type == ExecutionType.SEQUENTIAL:
            graph["execution_order"] = [step.id for step in plan.steps]
        elif plan.execution_type == ExecutionType.PARALLEL:
            graph["execution_order"] = [step.id for step in plan.steps]  # All can run in parallel
        else:
            # For complex types, use topological sort based on dependencies
            graph["execution_order"] = self._topological_sort(plan.steps)
        
        return graph

    def _topological_sort(self, steps: List[ExecutionStep]) -> List[str]:
        """Simple topological sort for steps with dependencies."""
        # Build dependency graph
        graph = {step.id: step.dependencies for step in steps}
        visited = set()
        result = []
        
        def visit(node):
            if node not in visited:
                visited.add(node)
                for dep in graph.get(node, []):
                    visit(dep)
                result.append(node)
        
        for step in steps:
            visit(step.id)
        
        return result

    def _estimate_execution_duration(self, plan: ExecutionPlan) -> int:
        """Estimate total execution duration."""
        if plan.execution_type == ExecutionType.SEQUENTIAL:
            # Sum of all step timeouts
            return sum(step.timeout for step in plan.steps)
        elif plan.execution_type == ExecutionType.PARALLEL:
            # Maximum of all step timeouts
            return max((step.timeout for step in plan.steps), default=0)
        else:
            # Complex estimate based on dependencies
            return sum(step.timeout for step in plan.steps) // 2  # Rough estimate

    def _calculate_resource_requirements(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Calculate resource requirements for execution."""
        requirements = {
            "cpu_cores": 1.0,
            "memory_mb": 512,
            "storage_mb": 100,
            "network_bandwidth_mbps": 10
        }
        
        # Adjust based on execution type
        if plan.execution_type == ExecutionType.PARALLEL:
            requirements["cpu_cores"] = min(len(plan.steps), self.config.max_concurrent_steps)
            requirements["memory_mb"] *= min(len(plan.steps), self.config.max_concurrent_steps)
        
        # Add per-step requirements
        for step in plan.steps:
            if "python" in step.command.lower():
                requirements["memory_mb"] += 256
            if "docker" in step.command.lower():
                requirements["cpu_cores"] += 0.5
                requirements["memory_mb"] += 512
        
        return requirements


# Factory function for easy instantiation
def create_execution_planning_orchestrator(
    enable_parallel_execution: bool = True,
    enable_retry_mechanism: bool = True,
    **kwargs
) -> ExecutionPlanningOrchestrator:
    """Create a configured execution planning orchestrator."""
    config = ExecutionPlanningConfig(
        enable_parallel_execution=enable_parallel_execution,
        enable_retry_mechanism=enable_retry_mechanism,
        **kwargs
    )
    return ExecutionPlanningOrchestrator(config)


# Convenience function for direct usage
def plan_execution_workflow(
    workflow_name: str,
    execution_type: str,
    steps: List[Dict[str, Any]],
    branches: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan execution workflow from simple parameters.
    
    Args:
        workflow_name: Name of the workflow
        execution_type: Type of execution (sequential, parallel, conditional)
        steps: List of execution step definitions
        branches: Optional list of conditional branches
        config: Optional orchestrator configuration overrides
        
    Returns:
        Dict: Planning result with execution plan and graph
    """
    # Build request
    request = {
        "workflow_name": workflow_name,
        "execution_type": execution_type,
        "steps": steps,
        "branches": branches or []
    }
    
    # Create orchestrator and execute
    orchestrator_config = ExecutionPlanningConfig(**config) if config else None
    orchestrator = ExecutionPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "execution_plan": {
            "execution_type": result.execution_plan.execution_type.value,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "command": s.command,
                    "parameters": s.parameters,
                    "dependencies": s.dependencies,
                    "timeout": s.timeout,
                    "retry_policy": s.retry_policy.value,
                    "max_retries": s.max_retries,
                    "retry_delay": s.retry_delay,
                    "on_failure": s.on_failure
                }
                for s in result.execution_plan.steps
            ],
            "global_timeout": result.execution_plan.global_timeout,
            "retry_policy": result.execution_plan.retry_policy.value,
            "error_handling": result.execution_plan.error_handling,
            "metadata": result.execution_plan.metadata
        } if result.execution_plan else None,
        "execution_graph": result.execution_graph,
        "estimated_duration": result.estimated_duration,
        "resource_requirements": result.resource_requirements,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


if __name__ == "__main__":
    # Example usage
    example_steps = [
        {
            "id": "step_1",
            "name": "Data Extraction",
            "command": "python extract_data.py",
            "timeout": 300
        },
        {
            "id": "step_2",
            "name": "Data Processing",
            "command": "python process_data.py",
            "dependencies": ["step_1"],
            "timeout": 600
        }
    ]
    
    result = plan_execution_workflow(
        workflow_name="data_pipeline",
        execution_type="sequential",
        steps=example_steps
    )
    print(f"Execution planning result: {result}")