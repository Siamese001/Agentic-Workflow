"""
L5 Agentic Core - L1 Planning Layer - Plan Optimizer
Implements L1 Cognitive Planning Layer for plan optimization and efficiency improvements
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
from .plan_schema import PlanSchema, PlanStep, PlanStatus, ValidationResult

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    TIME_OPTIMIZATION = "time_optimization"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    DEPENDENCY_OPTIMIZATION = "dependency_optimization"
    PARALLEL_OPTIMIZATION = "parallel_optimization"
    SAFETY_OPTIMIZATION = "safety_optimization"

class OptimizationLevel(Enum):
    """L5 Optimization intensity levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CRITICAL = "critical"

@dataclass
class OptimizationConstraints:
    """L5 Safety constraints for optimization"""
    max_parallel_steps: int = 5
    max_optimization_passes: int = 10
    preserve_safety: bool = True
    require_validation: bool = True
    safety_level: str = "strict"

@dataclass
class OptimizationMetric:
    """L5 Optimization metric structure"""
    metric_name: str
    before_value: float
    after_value: float
    improvement_percentage: float
    timestamp: str = ""

@dataclass
class OptimizationResult:
    """L5 Optimization result structure with full type safety"""
    optimization_id: str
    strategy: OptimizationStrategy
    original_schema: PlanSchema
    optimized_schema: PlanSchema
    metrics: List[OptimizationMetric] = field(default_factory=list)
    applied_changes: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class PlanOptimizer(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def optimize_plan(self, schema: PlanSchema, strategy: OptimizationStrategy) -> OptimizationResult:
        """Optimize plan with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_optimization(self, original: PlanSchema, optimized: PlanSchema) -> ValidationResult:
        """Validate optimization results"""
        pass
    
    @abstractmethod
    def validate_safety(self, schema: PlanSchema) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class PlanOptimizerImpl(PlanOptimizer):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure plan optimization with no side effects
    """
    
    def __init__(self, constraints: Optional[OptimizationConstraints] = None):
        self.constraints = constraints or OptimizationConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def optimize_plan(self, schema: PlanSchema, strategy: OptimizationStrategy) -> OptimizationResult:
        """Optimize plan following L5 architecture principles"""
        self.logger.info(f"Optimizing plan {schema.plan_id} with strategy: {strategy}")
        
        # L5 Input validation
        self._validate_input(schema)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(schema):
            raise SecurityError("Plan schema failed L5 safety validation")
        
        # Create a deep copy for optimization
        optimized_schema = self._deep_copy_schema(schema)
        applied_changes = []
        metrics = []
        
        # Apply optimization strategy
        if strategy == OptimizationStrategy.TIME_OPTIMIZATION:
            changes, time_metrics = self._optimize_time(optimized_schema)
            applied_changes.extend(changes)
            metrics.extend(time_metrics)
        
        elif strategy == OptimizationStrategy.DEPENDENCY_OPTIMIZATION:
            changes, dep_metrics = self._optimize_dependencies(optimized_schema)
            applied_changes.extend(changes)
            metrics.extend(dep_metrics)
        
        elif strategy == OptimizationStrategy.PARALLEL_OPTIMIZATION:
            changes, parallel_metrics = self._optimize_parallel(optimized_schema)
            applied_changes.extend(changes)
            metrics.extend(parallel_metrics)
        
        elif strategy == OptimizationStrategy.SAFETY_OPTIMIZATION:
            changes, safety_metrics = self._optimize_safety(optimized_schema)
            applied_changes.extend(changes)
            metrics.extend(safety_metrics)
        
        elif strategy == OptimizationStrategy.RESOURCE_OPTIMIZATION:
            changes, resource_metrics = self._optimize_resources(optimized_schema)
            applied_changes.extend(changes)
            metrics.extend(resource_metrics)
        
        # Validate optimized schema
        validation_result = self.validate_optimization(schema, optimized_schema)
        if not validation_result.valid:
            raise ValueError(f"Optimization validation failed: {validation_result.errors}")
        
        # Create optimization result
        result = OptimizationResult(
            optimization_id=self._generate_optimization_id(),
            strategy=strategy,
            original_schema=schema,
            optimized_schema=optimized_schema,
            metrics=metrics,
            applied_changes=applied_changes,
            safety_validated=validation_result.safety_validated,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Plan optimization completed: {len(applied_changes)} changes applied")
        return result
    
    def _optimize_time(self, schema: PlanSchema) -> Tuple[List[str], List[OptimizationMetric]]:
        """Optimize for execution time"""
        changes = []
        metrics = []
        
        # Calculate original total duration
        original_duration = sum(step.estimated_duration for step in schema.steps)
        
        # Optimize step ordering based on dependencies
        optimized_steps = self._topological_sort(schema.steps)
        
        # Merge consecutive steps with no dependencies
        merged_steps = []
        i = 0
        while i < len(optimized_steps):
            current_step = optimized_steps[i]
            
            # Check if next step can be merged
            if (i + 1 < len(optimized_steps) and 
                not optimized_steps[i + 1].dependencies and
                not current_step.dependencies and
                current_step.operation == optimized_steps[i + 1].operation):
                
                # Merge steps
                merged_step = PlanStep(
                    step_id=f"merged_{current_step.step_id}_{optimized_steps[i + 1].step_id}",
                    step_number=current_step.step_number,
                    description=f"Merged: {current_step.description} + {optimized_steps[i + 1].description}",
                    operation=current_step.operation,
                    parameters={**current_step.parameters, **optimized_steps[i + 1].parameters},
                    dependencies=current_step.dependencies,
                    estimated_duration=current_step.estimated_duration + optimized_steps[i + 1].estimated_duration * 0.8,  # 20% efficiency gain
                    status=current_step.status,
                    safety_validated=current_step.safety_validated,
                    timestamp=self._get_timestamp()
                )
                merged_steps.append(merged_step)
                changes.append(f"Merged steps {current_step.step_id} and {optimized_steps[i + 1].step_id}")
                i += 2
            else:
                merged_steps.append(current_step)
                i += 1
        
        schema.steps = merged_steps
        
        # Calculate optimized duration
        optimized_duration = sum(step.estimated_duration for step in schema.steps)
        
        # Create metric
        improvement = ((original_duration - optimized_duration) / original_duration) * 100 if original_duration > 0 else 0
        metrics.append(OptimizationMetric(
            metric_name="total_execution_time",
            before_value=original_duration,
            after_value=optimized_duration,
            improvement_percentage=improvement,
            timestamp=self._get_timestamp()
        ))
        
        return changes, metrics
    
    def _optimize_dependencies(self, schema: PlanSchema) -> Tuple[List[str], List[OptimizationMetric]]:
        """Optimize step dependencies"""
        changes = []
        metrics = []
        
        # Remove redundant dependencies
        original_deps = sum(len(step.dependencies) for step in schema.steps)
        
        for step in schema.steps:
            # Remove self-dependencies
            if step.step_id in step.dependencies:
                step.dependencies.remove(step.step_id)
                changes.append(f"Removed self-dependency from step {step.step_id}")
            
            # Remove transitive dependencies (if A depends on B and B depends on C, A doesn't need to depend on C)
            to_remove = set()
            for dep in step.dependencies:
                dep_step = next((s for s in schema.steps if s.step_id == dep), None)
                if dep_step:
                    for transitive_dep in dep_step.dependencies:
                        if transitive_dep in step.dependencies:
                            to_remove.add(transitive_dep)
            
            for dep in to_remove:
                step.dependencies.remove(dep)
                changes.append(f"Removed transitive dependency {dep} from step {step.step_id}")
        
        optimized_deps = sum(len(step.dependencies for step in schema.steps))
        
        # Create metric
        improvement = ((original_deps - optimized_deps) / original_deps) * 100 if original_deps > 0 else 0
        metrics.append(OptimizationMetric(
            metric_name="dependency_count",
            before_value=original_deps,
            after_value=optimized_deps,
            improvement_percentage=improvement,
            timestamp=self._get_timestamp()
        ))
        
        return changes, metrics
    
    def _optimize_parallel(self, schema: PlanSchema) -> Tuple[List[str], List[OptimizationMetric]]:
        """Optimize for parallel execution"""
        changes = []
        metrics = []
        
        # Identify steps that can run in parallel
        parallel_groups = self._identify_parallel_groups(schema.steps)
        
        original_sequential_time = sum(step.estimated_duration for step in schema.steps)
        parallel_time = 0
        
        for group in parallel_groups:
            if len(group) > 1:
                # Steps in this group can run in parallel
                group_time = max(step.estimated_duration for step in group)
                parallel_time += group_time
                changes.append(f"Identified parallel group of {len(group)} steps")
            else:
                # Single step runs sequentially
                parallel_time += group[0].estimated_duration
        
        # Create metric
        improvement = ((original_sequential_time - parallel_time) / original_sequential_time) * 100 if original_sequential_time > 0 else 0
        metrics.append(OptimizationMetric(
            metric_name="parallel_execution_time",
            before_value=original_sequential_time,
            after_value=parallel_time,
            improvement_percentage=improvement,
            timestamp=self._get_timestamp()
        ))
        
        return changes, metrics
    
    def _optimize_safety(self, schema: PlanSchema) -> Tuple[List[str], List[OptimizationMetric]]:
        """Optimize for safety and security"""
        changes = []
        metrics = []
        
        # Add safety checks to critical steps
        safety_checks_added = 0
        for step in schema.steps:
            if step.operation.lower() in ["execute", "process", "transform"]:
                # Add safety validation parameter
                if "validate_safety" not in step.parameters:
                    step.parameters["validate_safety"] = True
                    safety_checks_added += 1
                    changes.append(f"Added safety check to step {step.step_id}")
        
        # Create metric
        metrics.append(OptimizationMetric(
            metric_name="safety_checks",
            before_value=0,
            after_value=safety_checks_added,
            improvement_percentage=100.0 if safety_checks_added > 0 else 0.0,
            timestamp=self._get_timestamp()
        ))
        
        return changes, metrics
    
    def _optimize_resources(self, schema: PlanSchema) -> Tuple[List[str], List[OptimizationMetric]]:
        """Optimize for resource usage"""
        changes = []
        metrics = []
        
        # Add resource constraints to steps
        resource_constraints_added = 0
        for step in schema.steps:
            if "max_memory" not in step.parameters:
                step.parameters["max_memory"] = "1GB"
                resource_constraints_added += 1
                changes.append(f"Added memory constraint to step {step.step_id}")
            
            if "max_cpu" not in step.parameters:
                step.parameters["max_cpu"] = "80%"
                resource_constraints_added += 1
                changes.append(f"Added CPU constraint to step {step.step_id}")
        
        # Create metric
        metrics.append(OptimizationMetric(
            metric_name="resource_constraints",
            before_value=0,
            after_value=resource_constraints_added,
            improvement_percentage=100.0 if resource_constraints_added > 0 else 0.0,
            timestamp=self._get_timestamp()
        ))
        
        return changes, metrics
    
    def _topological_sort(self, steps: List[PlanStep]) -> List[PlanStep]:
        """Sort steps topologically based on dependencies"""
        # Create a mapping of step_id to step
        step_map = {step.step_id: step for step in steps}
        
        # Build adjacency list
        in_degree = {step.step_id: 0 for step in steps}
        for step in steps:
            for dep in step.dependencies:
                if dep in in_degree:
                    in_degree[step.step_id] += 1
        
        # Queue for nodes with no dependencies
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current_id = queue.pop(0)
            result.append(step_map[current_id])
            
            # Reduce in-degree for dependent steps
            for step in steps:
                if current_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step.step_id)
        
        return result
    
    def _identify_parallel_groups(self, steps: List[PlanStep]) -> List[List[PlanStep]]:
        """Identify groups of steps that can run in parallel"""
        # Simple implementation: steps with no dependencies can run in parallel
        no_deps = [step for step in steps if not step.dependencies]
        with_deps = [step for step in steps if step.dependencies]
        
        groups = []
        if no_deps:
            groups.append(no_deps)
        
        # Add each step with dependencies as its own group for now
        for step in with_deps:
            groups.append([step])
        
        return groups
    
    def validate_optimization(self, original: PlanSchema, optimized: PlanSchema) -> ValidationResult:
        """Validate optimization results"""
        errors = []
        warnings = []
        
        # Check that optimization didn't break core functionality
        if len(optimized.steps) == 0:
            errors.append("Optimized plan has no steps")
        
        # Check that all original step operations are preserved
        original_ops = {step.operation for step in original.steps}
        optimized_ops = {step.operation for step in optimized.steps}
        
        missing_ops = original_ops - optimized_ops
        if missing_ops:
            warnings.append(f"Operations removed during optimization: {missing_ops}")
        
        # Safety validation
        safety_validated = self.validate_safety(optimized)
        if not safety_validated:
            errors.append("Optimized plan failed safety validation")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            safety_validated=safety_validated,
            timestamp=self._get_timestamp()
        )
    
    def validate_safety(self, schema: PlanSchema) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous operations
            dangerous_ops = ["exec", "eval", "import", "open", "file"]
            for step in schema.steps:
                if step.operation.lower() in dangerous_ops:
                    # Only allow if safety validation is explicitly enabled
                    if not step.parameters.get("validate_safety", False):
                        self.logger.error(f"Dangerous operation without safety validation: {step.operation}")
                        return False
            
            # Check for too many parallel steps (resource exhaustion risk)
            parallel_groups = self._identify_parallel_groups(schema.steps)
            for group in parallel_groups:
                if len(group) > self.constraints.max_parallel_steps:
                    self.logger.error(f"Too many parallel steps: {len(group)} > {self.constraints.max_parallel_steps}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, schema: PlanSchema) -> None:
        """L5 Input validation"""
        if not isinstance(schema, PlanSchema):
            raise ValueError("Input must be a PlanSchema")
        
        if not schema.steps:
            raise ValueError("Plan schema must have at least one step")
    
    def _deep_copy_schema(self, schema: PlanSchema) -> PlanSchema:
        """Create a deep copy of the schema"""
        import copy
        return copy.deepcopy(schema)
    
    def _generate_optimization_id(self) -> str:
        """Generate unique optimization ID"""
        import uuid
        return f"opt_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class PlanOptimizerInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, optimizer: PlanOptimizer):
        self._optimizer = optimizer
    
    def optimize_plan(self, plan_id: str, strategy: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            from .plan_schema import PlanSchemaFactory
            processor = PlanSchemaFactory.create_processor()
            schema = processor.get_schema(plan_id)
            
            if not schema:
                return {
                    "success": False,
                    "error": "Plan not found",
                    "safety_validated": False
                }
            
            optimization_strategy = OptimizationStrategy(strategy)
            result = self._optimizer.optimize_plan(schema, optimization_strategy)
            
            return {
                "success": True,
                "optimization_id": result.optimization_id,
                "strategy": result.strategy.value,
                "changes_applied": len(result.applied_changes),
                "improvements": {m.metric_name: m.improvement_percentage for m in result.metrics},
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Plan optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class PlanOptimizerFactory:
    """L5 Factory for creating plan optimizer instances"""
    
    @staticmethod
    def create_optimizer(constraints: Optional[OptimizationConstraints] = None) -> PlanOptimizer:
        return PlanOptimizerImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[OptimizationConstraints] = None) -> PlanOptimizerInterface:
        optimizer = PlanOptimizerFactory.create_optimizer(constraints)
        return PlanOptimizerInterface(optimizer)

# L5 Export for module usage
__all__ = [
    "OptimizationStrategy",
    "OptimizationLevel",
    "OptimizationConstraints",
    "OptimizationMetric",
    "OptimizationResult",
    "PlanOptimizer",
    "PlanOptimizerImpl",
    "PlanOptimizerInterface",
    "PlanOptimizerFactory",
    "SecurityError"
]
