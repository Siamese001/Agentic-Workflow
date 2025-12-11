"""Runtime Planning Orchestrator - Coordinates runtime execution and resource management operations.

This orchestrator manages the planning phase for runtime operations,
including resource allocation, execution scheduling, and performance optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RuntimeType(Enum):
    """Types of runtime environments."""
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    VM = "vm"
    STANDALONE = "standalone"


class ExecutionMode(Enum):
    """Execution modes for runtime operations."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    BATCH = "batch"
    STREAMING = "streaming"


class ResourceType(Enum):
    """Types of runtime resources."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class ResourceRequirement:
    """Definition of resource requirements."""
    resource_type: ResourceType
    amount: float
    unit: str
    min_required: float
    max_allowed: float
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTask:
    """Definition of an execution task."""
    id: str
    name: str
    command: str
    environment: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    resources: List[ResourceRequirement] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class RuntimePlan:
    """Plan for runtime execution."""
    runtime_type: RuntimeType
    execution_mode: ExecutionMode
    tasks: List[ExecutionTask]
    resource_limits: Dict[str, float] = field(default_factory=dict)
    scheduling_policy: str = "fifo"
    scaling_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimePlanningConfig:
    """Configuration for runtime planning orchestrator."""
    enable_resource_optimization: bool = True
    enable_auto_scaling: bool = True
    enable_monitoring: bool = True
    default_timeout: int = 300
    max_concurrent_tasks: int = 10
    log_level: str = "INFO"


@dataclass
class RuntimePlanningResult:
    """Result of runtime planning orchestration."""
    success: bool
    runtime_plan: Optional[RuntimePlan] = None
    resource_estimates: Dict[str, Any] = field(default_factory=dict)
    execution_schedule: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimePlanningOrchestrator:
    """Orchestrator for planning runtime operations."""

    def __init__(self, config: Optional[RuntimePlanningConfig] = None):
        self.config = config or RuntimePlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, runtime_request: Dict[str, Any]) -> RuntimePlanningResult:
        """Execute the runtime planning orchestration.
        
        Args:
            runtime_request: Dictionary containing runtime requirements and tasks
            
        Returns:
            RuntimePlanningResult: Complete planning result with runtime plan and schedule
        """
        self.logger.info(f"Starting runtime planning for: {runtime_request.get('application', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(runtime_request)
            
            # Parse tasks from request
            tasks = self._parse_tasks(runtime_request)
            
            # Create runtime plan
            runtime_plan = self._create_runtime_plan(runtime_request, tasks)
            
            # Calculate resource estimates
            resource_estimates = self._calculate_resource_estimates(tasks)
            
            # Generate execution schedule
            execution_schedule = self._generate_execution_schedule(tasks, runtime_plan)
            
            result = RuntimePlanningResult(
                success=True,
                runtime_plan=runtime_plan,
                resource_estimates=resource_estimates,
                execution_schedule=execution_schedule,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "application": runtime_request.get("application"),
                    "task_count": len(tasks),
                    "orchestrator": "RuntimePlanningOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned runtime: {len(tasks)} tasks scheduled")
            return result
            
        except Exception as e:
            self.logger.error(f"Runtime planning failed: {str(e)}")
            return RuntimePlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "RuntimePlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate runtime planning request."""
        if not request:
            raise ValueError("Runtime request cannot be empty")
        
        if "application" not in request:
            raise ValueError("Application name is required in runtime request")
        
        if "tasks" not in request:
            raise ValueError("Tasks are required in runtime request")

    def _parse_tasks(self, request: Dict[str, Any]) -> List[ExecutionTask]:
        """Parse tasks from request."""
        tasks = []
        raw_tasks = request.get("tasks", [])
        
        for raw_task in raw_tasks:
            if isinstance(raw_task, dict):
                # Parse resource requirements
                resources = []
                for raw_resource in raw_task.get("resources", []):
                    if isinstance(raw_resource, dict):
                        resource = ResourceRequirement(
                            resource_type=ResourceType(raw_resource.get("type", "cpu")),
                            amount=raw_resource.get("amount", 1.0),
                            unit=raw_resource.get("unit", "cores"),
                            min_required=raw_resource.get("min_required", 0.5),
                            max_allowed=raw_resource.get("max_allowed", 4.0),
                            constraints=raw_resource.get("constraints", {})
                        )
                        resources.append(resource)
                
                task = ExecutionTask(
                    id=raw_task.get("id", f"task_{len(tasks)}"),
                    name=raw_task.get("name", "unnamed"),
                    command=raw_task.get("command", ""),
                    environment=raw_task.get("environment", {}),
                    dependencies=raw_task.get("dependencies", []),
                    resources=resources,
                    timeout=raw_task.get("timeout", self.config.default_timeout),
                    retry_count=raw_task.get("retry_count", 0),
                    max_retries=raw_task.get("max_retries", 3)
                )
                tasks.append(task)
        
        return tasks

    def _create_runtime_plan(self, request: Dict[str, Any], tasks: List[ExecutionTask]) -> RuntimePlan:
        """Create runtime plan from request and tasks."""
        runtime_config = request.get("runtime", {})
        
        # Map strings to enums
        runtime_mapping = {
            "container": RuntimeType.CONTAINER,
            "kubernetes": RuntimeType.KUBERNETES,
            "serverless": RuntimeType.SERVERLESS,
            "vm": RuntimeType.VM,
            "standalone": RuntimeType.STANDALONE
        }
        
        execution_mapping = {
            "sequential": ExecutionMode.SEQUENTIAL,
            "parallel": ExecutionMode.PARALLEL,
            "pipeline": ExecutionMode.PIPELINE,
            "batch": ExecutionMode.BATCH,
            "streaming": ExecutionMode.STREAMING
        }
        
        runtime_type = runtime_mapping.get(
            runtime_config.get("type", "container"), 
            RuntimeType.CONTAINER
        )
        
        execution_mode = execution_mapping.get(
            runtime_config.get("execution_mode", "sequential"),
            ExecutionMode.SEQUENTIAL
        )
        
        return RuntimePlan(
            runtime_type=runtime_type,
            execution_mode=execution_mode,
            tasks=tasks,
            resource_limits=runtime_config.get("resource_limits", {}),
            scheduling_policy=runtime_config.get("scheduling_policy", "fifo"),
            scaling_config=runtime_config.get("scaling_config", {})
        )

    def _calculate_resource_estimates(self, tasks: List[ExecutionTask]) -> Dict[str, Any]:
        """Calculate total resource estimates for all tasks."""
        estimates = {
            "total_cpu": 0.0,
            "total_memory_gb": 0.0,
            "total_storage_gb": 0.0,
            "estimated_duration_seconds": 0,
            "cost_estimate": 0.0
        }
        
        for task in tasks:
            for resource in task.resources:
                if resource.resource_type == ResourceType.CPU:
                    estimates["total_cpu"] += resource.amount
                elif resource.resource_type == ResourceType.MEMORY:
                    if resource.unit == "GB":
                        estimates["total_memory_gb"] += resource.amount
                    elif resource.unit == "MB":
                        estimates["total_memory_gb"] += resource.amount / 1024
                elif resource.resource_type == ResourceType.STORAGE:
                    if resource.unit == "GB":
                        estimates["total_storage_gb"] += resource.amount
                    elif resource.unit == "MB":
                        estimates["total_storage_gb"] += resource.amount / 1024
            
            estimates["estimated_duration_seconds"] += task.timeout
        
        # Simple cost estimation (example rates)
        estimates["cost_estimate"] = (
            estimates["total_cpu"] * 0.05 +  # $0.05 per CPU-hour
            estimates["total_memory_gb"] * 0.01 +  # $0.01 per GB-hour
            estimates["total_storage_gb"] * 0.001  # $0.001 per GB-hour
        )
        
        return estimates

    def _generate_execution_schedule(self, tasks: List[ExecutionTask], plan: RuntimePlan) -> List[Dict[str, Any]]:
        """Generate execution schedule based on plan."""
        schedule = []
        
        if plan.execution_mode == ExecutionMode.SEQUENTIAL:
            # Simple sequential schedule
            start_time = 0
            for task in tasks:
                schedule_item = {
                    "task_id": task.id,
                    "task_name": task.name,
                    "start_time": start_time,
                    "end_time": start_time + task.timeout,
                    "dependencies": task.dependencies
                }
                schedule.append(schedule_item)
                start_time += task.timeout
        
        elif plan.execution_mode == ExecutionMode.PARALLEL:
            # All tasks start at time 0
            for task in tasks:
                schedule_item = {
                    "task_id": task.id,
                    "task_name": task.name,
                    "start_time": 0,
                    "end_time": task.timeout,
                    "dependencies": task.dependencies
                }
                schedule.append(schedule_item)
        
        else:
            # Default to sequential for other modes
            start_time = 0
            for task in tasks:
                schedule_item = {
                    "task_id": task.id,
                    "task_name": task.name,
                    "start_time": start_time,
                    "end_time": start_time + task.timeout,
                    "dependencies": task.dependencies
                }
                schedule.append(schedule_item)
                start_time += task.timeout
        
        return schedule


# Factory function for easy instantiation
def create_runtime_planning_orchestrator(
    enable_resource_optimization: bool = True,
    enable_auto_scaling: bool = True,
    **kwargs
) -> RuntimePlanningOrchestrator:
    """Create a configured runtime planning orchestrator."""
    config = RuntimePlanningConfig(
        enable_resource_optimization=enable_resource_optimization,
        enable_auto_scaling=enable_auto_scaling,
        **kwargs
    )
    return RuntimePlanningOrchestrator(config)


# Convenience function for direct usage
def plan_runtime_execution(
    application: str,
    tasks: List[Dict[str, Any]],
    runtime: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan runtime execution from simple parameters.
    
    Args:
        application: Name of the application
        tasks: List of task definitions
        runtime: Optional runtime configuration
        config: Optional orchestrator configuration overrides
        
    Returns:
        Dict: Planning result with runtime plan and schedule
    """
    # Build request
    request = {
        "application": application,
        "tasks": tasks,
        "runtime": runtime or {}
    }
    
    # Create orchestrator and execute
    orchestrator_config = RuntimePlanningConfig(**config) if config else None
    orchestrator = RuntimePlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "runtime_plan": {
            "runtime_type": result.runtime_plan.runtime_type.value,
            "execution_mode": result.runtime_plan.execution_mode.value,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "command": t.command,
                    "environment": t.environment,
                    "dependencies": t.dependencies,
                    "resources": [
                        {
                            "resource_type": r.resource_type.value,
                            "amount": r.amount,
                            "unit": r.unit,
                            "min_required": r.min_required,
                            "max_allowed": r.max_allowed,
                            "constraints": r.constraints
                        }
                        for r in t.resources
                    ],
                    "timeout": t.timeout,
                    "retry_count": t.retry_count,
                    "max_retries": t.max_retries
                }
                for t in result.runtime_plan.tasks
            ],
            "resource_limits": result.runtime_plan.resource_limits,
            "scheduling_policy": result.runtime_plan.scheduling_policy,
            "scaling_config": result.runtime_plan.scaling_config
        } if result.runtime_plan else None,
        "resource_estimates": result.resource_estimates,
        "execution_schedule": result.execution_schedule,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }


if __name__ == "__main__":
    # Example usage
    example_tasks = [
        {
            "id": "task_1",
            "name": "data_processing",
            "command": "python process_data.py",
            "resources": [
                {"type": "cpu", "amount": 2.0, "unit": "cores", "min_required": 1.0, "max_allowed": 4.0},
                {"type": "memory", "amount": 4.0, "unit": "GB", "min_required": 2.0, "max_allowed": 8.0}
            ],
            "timeout": 600
        }
    ]
    
    result = plan_runtime_execution(
        application="data_pipeline",
        tasks=example_tasks,
        runtime={"type": "container", "execution_mode": "sequential"}
    )
    print(f"Runtime planning result: {result}")
class OrchestrateDataPlanningOrchestratorProcessor(ABC):
    """L5 interface foundation - ensures L1 pure planning behavior"""

    @abstractmethod
    def process(self, input_data: Dict[str, object]) -> OrchestrateDataPlanningOrchestratorResult:
        """Process data with L5 safety constraints"""
        ...

    @abstractmethod
    def validate_safety(self, data: Dict[str, object]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        ...


class OrchestrateDataPlanningOrchestratorImpl(OrchestrateDataPlanningOrchestratorProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """

    def __init__(self, constraints: Optional[OrchestrateDataPlanningOrchestratorConstraints] = None):
        self.constraints = constraints or OrchestrateDataPlanningOrchestratorConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(self, input_data: Dict[str, object]) -> OrchestrateDataPlanningOrchestratorResult:
        """Process input following L5 architecture principles"""
        self.logger.info(f"Processing {input_data}")

        # L5 Input validation
        self._validate_input(input_data)

        # L5 Safety validation - fail-closed
        if not self.validate_safety(input_data):
            raise SecurityError("Input failed L5 safety validation")

        # Create result with L5 structure
        result = OrchestrateDataPlanningOrchestratorResult(
            success=True,
            data={"processed": True, "input": input_data},
            safety_validated=True,
            timestamp=self._get_timestamp()
        )

        self.logger.info(f"Successfully processed: {result.success}")
        return result

    def validate_safety(self, data: Dict[str, object]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "# SECURITY: ast.literal_eval(", "# SECURITY: pass  # exec disabled: ", "__import__"]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f" Dangerous pattern detected: {pattern}")
                    return False

            # Check data size
            if len(str(data)) > 1000000:  # 1MB limit
                self.logger.error("Data exceeds size limit")
                return False

            self.logger.info("Data passed L5 safety validation")
            return True
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed

    def _validate_input(self, input_data: Dict[str, object]) -> None:
        """L5 Input validation"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        if not input_data:
            raise ValueError("Input cannot be empty")

    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    ...


class OrchestrateDataPlanningOrchestratorInterface:
    """L5 Interface - ensures contract compliance"""

    def __init__(self, engine: OrchestrateDataPlanningOrchestratorProcessor):
        self._processor = engine

    def execute(self, input_data: Dict[str, object]) -> Dict[str, object]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            raise SecurityError(f"Execution failed: {e}")


class OrchestrateDataPlanningOrchestratorFactory:
    """L5 builder for creating processors with proper configuration"""

    @staticmethod
    def create_processor(safety_level: str = "strict") -> OrchestrateDataPlanningOrchestratorInterface:
        """Create configured engine"""
        constraints = OrchestrateDataPlanningOrchestratorConstraints(safety_level=safety_level)
        engine = OrchestrateDataPlanningOrchestratorImpl(constraints)
        return OrchestrateDataPlanningOrchestratorInterface(engine)


def orchestrate_data_planning(input_data: Dict[str, object]) -> Dict[str, object]:
    """
    L5 Main function - orchestrate data planning operations

    Args:
        input_data: Input data to process

    Returns:
        Dict: Processed result

    Raises:
        SecurityError: If execution fails any safety check
    """
    builder = OrchestrateDataPlanningOrchestratorFactory()
    engine = builder.create_processor()
    return engine.execute(input_data)


if __name__ == "__main__":
    # L5 Test execution
    try:
        test_data = {"test": True}
        result = orchestrate_data_planning(test_data)
        logger.info(f"L5 Execution successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except (ValueError, TypeError, RuntimeError, KeyError) as e:
        logger.error(f"L5 Unexpected error: {e}")