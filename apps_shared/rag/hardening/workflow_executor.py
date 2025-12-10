"""
runtime/shared/transaction_manager.py
Transaction Manager with Rollback Support

Ported from legacy resume gen Job_Workflow_v61.27.json
Implements transactional workflow execution with:
  - Dependency graph management
  - Checkpoint creation and restoration
  - Rollback on failure
  - Execution trace logging
"""


import copy
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Tuple, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# ENUMERATIONS
# =============================================================================

class TransactionState(Enum):
    """States for a transaction."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMMITTED = auto()
    ROLLED_BACK = auto()
    FAILED = auto()


class StepState(Enum):
    """States for a workflow step."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    SKIPPED = "SKIPPED"


class ExecutionTraceLevel(Enum):
    """Levels for execution trace logging."""
    MINIMAL = auto()
    STANDARD = auto()
    VERBOSE = auto()
    DEBUG = auto()


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Checkpoint:
    """A checkpoint capturing state at a point in time."""
    checkpoint_id: str
    step_id: str
    state: Dict[str, object]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    hash: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.hash is None:
            self.hash = self._compute_hash()
            
    def _compute_hash(self) -> str:
        """Compute hash of checkpoint state."""
        content = json.dumps(self.state, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "step_id": self.step_id,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "metadata": self.metadata,
            "state_keys": list(self.state.keys()),
        }


@dataclass
class StepResult:
    """Result from executing a workflow step."""
    step_id: str
    state: StepState
    output: Optional[object] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    checkpoint: Optional[Checkpoint] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "state": self.state.value,
            "has_output": self.output is not None,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "checkpoint_id": self.checkpoint.checkpoint_id if self.checkpoint else None,
            "timestamp": self.timestamp,
        }


@dataclass
class ExecutionTrace:
    """Trace entry for execution logging."""
    trace_id: str
    step_id: str
    action: str
    details: Dict[str, object]
    level: ExecutionTraceLevel
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "step_id": self.step_id,
            "action": self.action,
            "details": self.details,
            "level": self.level.name,
            "timestamp": self.timestamp,
        }


@dataclass
class DependencyNode:
    """A node in the dependency graph."""
    step_id: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    state: StepState = StepState.PENDING
    
    def can_execute(self, completed_steps: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return self.dependencies.issubset(completed_steps)


@dataclass
class TransactionConfig:
    """Configuration for the transaction manager."""
    enabled: bool = True
    rollback_on_failure: bool = True
    max_checkpoints: int = 100
    trace_level: ExecutionTraceLevel = ExecutionTraceLevel.VERBOSE
    checkpoint_dir: Optional[str] = None
    auto_checkpoint: bool = True


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================

class DependencyGraph:
    """
    Manages step dependencies for workflow execution.
    
    Ensures steps execute in correct order based on their dependencies.
    """
    
    def __init__(self) -> None:
        self._nodes: Dict[str, DependencyNode] = {}
        
    def add_step(self, step_id: str, dependencies: Optional[List[str]] = None) -> None:
        """Add a step with its dependencies."""
        deps = set(dependencies) if dependencies else set()
        
        if step_id not in self._nodes:
            self._nodes[step_id] = DependencyNode(step_id=step_id, dependencies=deps)
        else:
            self._nodes[step_id].dependencies.update(deps)
            
        # Update dependents for dependency nodes
        for dep_id in deps:
            if dep_id not in self._nodes:
                self._nodes[dep_id] = DependencyNode(step_id=dep_id)
            self._nodes[dep_id].dependents.add(step_id)
            
    def get_execution_order(self) -> List[str]:
        """
        Get topologically sorted execution order.
        
        Returns:
            List of step IDs in execution order
            
        Raises:
            ValueError: If circular dependency detected
        """
        visited: Set[str] = set()
        pending_nodes: Set[str] = set()
        order: List[str] = []
        
        def visit(node_id: str) -> None:
            """Execute visit operation."""
            if node_id in pending_nodes:
                raise ValueError(f"Circular dependency detected involving {node_id}")
            if node_id in visited:
                return
                
            pending_nodes.add(node_id)
            
            node = self._nodes.get(node_id)
            if node:
                for dep_id in node.dependencies:
                    visit(dep_id)
                    
            pending_nodes.remove(node_id)
            visited.add(node_id)
            order.append(node_id)
            
        for node_id in self._nodes:
            if node_id not in visited:
                visit(node_id)
                
        return order
    
    def get_ready_steps(self, completed: Set[str]) -> List[str]:
        """Get steps that are ready to execute."""
        ready = []
        for node_id, node in self._nodes.items():
            if node.state == StepState.PENDING and node.can_execute(completed):
                ready.append(node_id)
        return ready
    
    def mark_completed(self, step_id: str) -> None:
        """Mark a step as completed."""
        if step_id in self._nodes:
            self._nodes[step_id].state = StepState.COMPLETED
            
    def mark_failed(self, step_id: str) -> None:
        """Mark a step as failed."""
        if step_id in self._nodes:
            self._nodes[step_id].state = StepState.FAILED
            
    def get_dependents(self, step_id: str) -> Set[str]:
        """Get all steps that depend on the given step."""
        if step_id in self._nodes:
            return self._nodes[step_id].dependents
        return set()
    
    def get_all_dependents(self, step_id: str) -> Set[str]:
        """Get all transitive dependents of a step."""
        all_deps: Set[str] = set()
        to_process = [step_id]
        
        while to_process:
            current = to_process.pop()
            direct_deps = self.get_dependents(current)
            for dep in direct_deps:
                if dep not in all_deps:
                    all_deps.add(dep)
                    to_process.append(dep)
                    
        return all_deps
    
    @classmethod
    def from_dict(cls, dependency_map: Dict[str, List[str]]) -> DependencyGraph:
        """
        Create dependency graph from dictionary.
        
        Args:
            dependency_map: Dict mapping step_id -> list of dependency step_ids
            
        Returns:
            DependencyGraph instance
        """
        graph = cls()
        for step_id, deps in dependency_map.items():
            graph.add_step(step_id, deps)
        return graph


# =============================================================================
# TRANSACTION MANAGER
# =============================================================================

class TransactionManager:
    """
    Manages transactional workflow execution with rollback support.
    
    Features:
    - Checkpoint creation at each step
    - Rollback to previous checkpoint on failure
    - Dependency-aware execution ordering
    - Detailed execution tracing
    """
    
    def __init__(self, config: Optional[TransactionConfig] = None) -> None:
        self.config = config or TransactionConfig()
        self._state: Dict[str, object] = {}
        self._checkpoints: List[Checkpoint] = []
        self._traces: List[ExecutionTrace] = []
        self._step_results: Dict[str, StepResult] = {}
        self._dependency_graph: Optional[DependencyGraph] = None
        self._transaction_state = TransactionState.PENDING
        self._trace_counter = 0
        
    @property
    def state(self) -> Dict[str, object]:
        """Get current state (deep copy for safety)."""
        return copy.deepcopy(self._state)
    
    @property
    def checkpoints(self) -> List[Checkpoint]:
        """Get list of checkpoints."""
        return list(self._checkpoints)
    
    @property
    def traces(self) -> List[ExecutionTrace]:
        """Get execution traces."""
        return list(self._traces)
    
    def set_dependency_graph(self, graph: DependencyGraph) -> None:
        """Set the dependency graph for execution ordering."""
        self._dependency_graph = graph
        
    def set_dependencies(self, dependency_map: Dict[str, List[str]]) -> None:
        """Set dependencies from a dictionary."""
        self._dependency_graph = DependencyGraph.from_dict(dependency_map)
        
    def begin(self) -> None:
        """Begin a new transaction."""
        if self._transaction_state == TransactionState.IN_PROGRESS:
            raise RuntimeError("Transaction already in progress")
            
        self._transaction_state = TransactionState.IN_PROGRESS
        self._trace("TRANSACTION_BEGIN", {"config": {
            "rollback_on_failure": self.config.rollback_on_failure,
            "trace_level": self.config.trace_level.name,
        }})
        
        # Create initial checkpoint
        if self.config.auto_checkpoint:
            self._create_checkpoint("INITIAL", {})
            
    def commit(self) -> None:
        """Commit the transaction."""
        if self._transaction_state != TransactionState.IN_PROGRESS:
            raise RuntimeError("No transaction in progress")
            
        self._transaction_state = TransactionState.COMMITTED
        self._trace("TRANSACTION_COMMIT", {
            "checkpoints": len(self._checkpoints),
            "steps_completed": len([r for r in self._step_results.values() if r.state == StepState.COMPLETED]),
        })
        
    def rollback(self, to_checkpoint: Optional[str] = None) -> bool:
        """
        Rollback to a previous checkpoint.
        
        Args:
            to_checkpoint: Checkpoint ID to rollback to. If None, rollback to last checkpoint.
            
        Returns:
            True if rollback successful
        """
        if not self._checkpoints:
            self._trace("ROLLBACK_FAILED", {"reason": "No checkpoints available"})
            return False
            
        # Find target checkpoint
        target: Optional[Checkpoint] = None
        
        if to_checkpoint:
            for cp in reversed(self._checkpoints):
                if cp.checkpoint_id == to_checkpoint:
                    target = cp
                    break
        else:
            # Rollback to last checkpoint
            target = self._checkpoints[-1]
            
        if not target:
            self._trace("ROLLBACK_FAILED", {"reason": f"Checkpoint not found: {to_checkpoint}"})
            return False
            
        # Restore state
        self._state = copy.deepcopy(target.state)
        
        # Mark dependent steps as rolled back
        if self._dependency_graph:
            dependents = self._dependency_graph.get_all_dependents(target.step_id)
            for dep_id in dependents:
                if dep_id in self._step_results:
                    self._step_results[dep_id].state = StepState.ROLLED_BACK
                    
        self._transaction_state = TransactionState.ROLLED_BACK
        self._trace("ROLLBACK_SUCCESS", {
            "to_checkpoint": target.checkpoint_id,
            "step_id": target.step_id,
            "state_hash": target.hash,
        })
        
        return True
    
    def execute_step(
        self,
        step_id: str,
        executor: Callable[[Dict[str, object]], Any],
        input_keys: Optional[List[str]] = None,
        output_key: Optional[str] = None,
    ) -> StepResult:
        """
        Execute a workflow step with transaction support.
        
        Args:
            step_id: Unique identifier for the step
            executor: Function that executes the step logic
            input_keys: Keys from state to pass to executor
            output_key: Key to store result in state
            
        Returns:
            StepResult with execution outcome
        """
        import time
        start_time = time.time()
        
        self._trace("STEP_START", {"step_id": step_id, "input_keys": input_keys})
        
        # Check dependencies
        if self._dependency_graph:
            completed = {
                sid for sid, result in self._step_results.items()
                if result.state == StepState.COMPLETED
            }
            node = self._dependency_graph._nodes.get(step_id)
            if node and not node.can_execute(completed):
                missing = node.dependencies - completed
                return StepResult(
                    step_id=step_id,
                    state=StepState.SKIPPED,
                    error=f"Dependencies not met: {missing}",
                    duration_ms=(time.time() - start_time) * 1000,
                )
                
        # Prepare input
        if input_keys:
            step_input = {k: self._state.get(k) for k in input_keys}
        else:
            step_input = copy.deepcopy(self._state)
            
        # Execute
        try:
            output = executor(step_input)
            
            # Store output
            if output_key:
                self._state[output_key] = output
            elif isinstance(output, dict):
                self._state.update(output)
                
            # Create checkpoint
            checkpoint = None
            if self.config.auto_checkpoint:
                checkpoint = self._create_checkpoint(step_id, self._state)
                
            # Mark completed in dependency graph
            if self._dependency_graph:
                self._dependency_graph.mark_completed(step_id)
                
            duration = (time.time() - start_time) * 1000
            result = StepResult(
                step_id=step_id,
                state=StepState.COMPLETED,
                output=output,
                duration_ms=duration,
                checkpoint=checkpoint,
            )
            
            self._step_results[step_id] = result
            self._trace("STEP_COMPLETE", {
                "step_id": step_id,
                "duration_ms": duration,
                "output_key": output_key,
            })
            
            return result
            
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            duration = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            self._trace("STEP_FAILED", {
                "step_id": step_id,
                "error": error_msg,
                "duration_ms": duration,
            })
            
            # Mark failed in dependency graph
            if self._dependency_graph:
                self._dependency_graph.mark_failed(step_id)
                
            result = StepResult(
                step_id=step_id,
                state=StepState.FAILED,
                error=error_msg,
                duration_ms=duration,
            )
            
            self._step_results[step_id] = result
            
            # Auto-rollback if configured
            if self.config.rollback_on_failure:
                self.rollback()
                
            self._transaction_state = TransactionState.FAILED
            return result
    
    def set_state(self, key: str, value: object) -> None:
        """Set a value in the transaction state."""
        self._state[key] = value
        self._trace("STATE_SET", {"key": key}, level=ExecutionTraceLevel.DEBUG)
        
    def get_state(self, key: str, default: object = None) -> object:
        """Get a value from the transaction state."""
        return copy.deepcopy(self._state.get(key, default))
    
    def _create_checkpoint(self, step_id: str, state: Dict[str, object]) -> Checkpoint:
        """Create a checkpoint of current state."""
        checkpoint_id = f"CP_{step_id}_{len(self._checkpoints):04d}"
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            step_id=step_id,
            state=copy.deepcopy(state),
        )
        
        self._checkpoints.append(checkpoint)
        
        # Trim old checkpoints if needed
        if len(self._checkpoints) > self.config.max_checkpoints:
            self._checkpoints = self._checkpoints[-self.config.max_checkpoints:]
            
        self._trace("CHECKPOINT_CREATED", {
            "checkpoint_id": checkpoint_id,
            "step_id": step_id,
            "hash": checkpoint.hash,
        }, level=ExecutionTraceLevel.VERBOSE)
        
        return checkpoint
    
    def _trace(
        self,
        action: str,
        details: Dict[str, object],
        level: ExecutionTraceLevel = ExecutionTraceLevel.STANDARD,
    ) -> None:
        """Add an execution trace entry."""
        if level.value > self.config.trace_level.value:
            return
            
        self._trace_counter += 1
        trace = ExecutionTrace(
            trace_id=f"T_{self._trace_counter:06d}",
            step_id=details.get("step_id", "SYSTEM"),
            action=action,
            details=details,
            level=level,
        )
        
        self._traces.append(trace)
        
        if self.config.trace_level == ExecutionTraceLevel.DEBUG:
            logger.debug(f"[{trace.trace_id}] {action}: {details}")
            
    def get_execution_report(self) -> Dict[str, object]:
        """Generate execution report."""
        return {
            "transaction_state": self._transaction_state.name,
            "steps": {
                "total": len(self._step_results),
                "completed": len([r for r in self._step_results.values() if r.state == StepState.COMPLETED]),
                "failed": len([r for r in self._step_results.values() if r.state == StepState.FAILED]),
                "rolled_back": len([r for r in self._step_results.values() if r.state == StepState.ROLLED_BACK]),
            },
            "checkpoints": len(self._checkpoints),
            "traces": len(self._traces),
            "step_results": [r.to_dict() for r in self._step_results.values()],
        }
    
    def save_traces(self, filepath: str) -> None:
        """Save execution traces to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump({
                "traces": [t.to_dict() for t in self._traces],
                "report": self.get_execution_report(),
            }, f, indent=2)


# =============================================================================
# WORKFLOW EXECUTOR
# =============================================================================

class WorkflowExecutor:
    """
    High-level workflow executor using transaction manager.
    
    Provides a simplified interface for executing multi-step workflows
    with automatic dependency resolution and rollback support.
    """
    
    def __init__(
        self,
        config: Optional[TransactionConfig] = None,
        dependency_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self.transaction = TransactionManager(config)
        self._steps: Dict[str, Callable] = {}
        self._step_configs: Dict[str, Dict[str, object]] = {}
        
        if dependency_map:
            self.transaction.set_dependencies(dependency_map)
            
    def register_step(
        self,
        step_id: str,
        executor: Callable[[Dict[str, object]], Any],
        dependencies: Optional[List[str]] = None,
        input_keys: Optional[List[str]] = None,
        output_key: Optional[str] = None,
    ) -> None:
        """Register a workflow step."""
        self._steps[step_id] = executor
        self._step_configs[step_id] = {
            "input_keys": input_keys,
            "output_key": output_key,
        }
        
        if dependencies and self.transaction._dependency_graph:
            self.transaction._dependency_graph.add_step(step_id, dependencies)
        elif dependencies:
            self.transaction.set_dependencies({step_id: dependencies})
            
    def execute(self, initial_state: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        """
        Execute all registered steps in dependency order.
        
        Args:
            initial_state: Initial state to start with
            
        Returns:
            Final state after execution
        """
        # Initialize state
        if initial_state:
            for key, value in initial_state.items():
                self.transaction.set_state(key, value)
                
        # Begin transaction
        self.transaction.begin()
        
        # Get execution order
        if self.transaction._dependency_graph:
            order = self.transaction._dependency_graph.get_execution_order()
            # Filter to only registered steps
            order = [s for s in order if s in self._steps]
        else:
            order = list(self._steps.keys())
            
        # Execute steps
        for step_id in order:
            executor = self._steps[step_id]
            config = self._step_configs[step_id]
            
            result = self.transaction.execute_step(
                step_id=step_id,
                executor=executor,
                input_keys=config.get("input_keys"),
                output_key=config.get("output_key"),
            )
            
            if result.state == StepState.FAILED:
                logger.error(f"Workflow failed at step {step_id}: {result.error}")
                break
                
        # Commit if successful
        if self.transaction._transaction_state == TransactionState.IN_PROGRESS:
            self.transaction.commit()
            
        return self.transaction.state


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_default_transaction_manager() -> TransactionManager:
    """Create a transaction manager with default configuration."""
    return TransactionManager()


def create_strict_transaction_manager() -> TransactionManager:
    """Create a transaction manager with strict rollback."""
    config = TransactionConfig(
        enabled=True,
        rollback_on_failure=True,
        trace_level=ExecutionTraceLevel.VERBOSE,
        auto_checkpoint=True,
    )
    return TransactionManager(config=config)


def create_workflow_executor(
    dependency_map: Optional[Dict[str, List[str]]] = None,
) -> WorkflowExecutor:
    """Create a workflow executor with optional dependencies."""
    config = TransactionConfig(
        enabled=True,
        rollback_on_failure=True,
        trace_level=ExecutionTraceLevel.STANDARD,
    )
    return WorkflowExecutor(config=config, dependency_map=dependency_map)
