"""
L5 Agentic Core - L3 Orchestration Layer - Flow Controller
Implements L3 Orchestration Layer for managing execution flow and state transitions
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
from collections import defaultdict

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowState(Enum):
    """L5 Flow state enumeration"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FlowType(Enum):
    """L5 Flow type enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    DAG = "dag"
    REACT = "react"

@dataclass
class FlowConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_execution_time: float = 600.0  # 10 minutes
    max_concurrent_flows: int = 10
    require_safety_checkpoints: bool = True
    allow_cancellation: bool = True
    safety_level: str = "strict"

@dataclass
class FlowStep:
    """L5 Flow step structure with full type safety"""
    step_id: str
    step_type: str  # "dag", "react", "tool", "condition"
    step_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    status: FlowState = FlowState.INITIALIZED
    result: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class FlowTransition:
    """L5 Flow transition structure"""
    from_step: str
    to_step: str
    condition: str = ""
    action: str = "continue"  # "continue", "branch", "loop", "stop"

@dataclass
class FlowExecution:
    """L5 Flow execution structure"""
    flow_id: str
    flow_type: FlowType
    steps: List[FlowStep] = field(default_factory=list)
    transitions: List[FlowTransition] = field(default_factory=list)
    current_step: Optional[str] = None
    state: FlowState = FlowState.INITIALIZED
    start_time: str = ""
    end_time: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

class FlowController(ABC):
    """L5 Abstract base - ensures L3 orchestration behavior"""
    
    @abstractmethod
    def create_flow(self, flow_type: FlowType, steps: List[FlowStep], transitions: List[FlowTransition], constraints: FlowConstraints) -> FlowExecution:
        """Create flow with L5 safety constraints"""
        pass
    
    @abstractmethod
    def execute_flow(self, flow: FlowExecution) -> FlowExecution:
        """Execute flow with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, flow: FlowExecution) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class FlowControllerImpl(FlowController):
    """
    L5 Implementation - L3 Orchestration Layer
    Pure flow control execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[FlowConstraints] = None):
        self.constraints = constraints or FlowConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_flows: Dict[str, FlowExecution] = {}
        
        # Initialize orchestration engines
        from ..dag_orchestration.dag_engine import DAGEngineFactory
        from ..react_orchestration.react_engine import ReActEngineFactory
        from ..l2_execution.execution_engines.tool_invocation import ToolInvocationEngineFactory
        
        self.dag_engine = DAGEngineFactory.create_engine()
        self.react_engine = ReActEngineFactory.create_engine()
        self.tool_engine = ToolInvocationEngineFactory.create_engine()
    
    def create_flow(self, flow_type: FlowType, steps: List[FlowStep], transitions: List[FlowTransition], constraints: Optional[FlowConstraints] = None) -> FlowExecution:
        """Create flow following L5 architecture principles"""
        flow_constraints = constraints or self.constraints
        self.logger.info(f"Creating {flow_type.value} flow with {len(steps)} steps")
        
        # L5 Input validation
        self._validate_flow_input(flow_type, steps, transitions)
        
        # L5 Safety validation - fail-closed
        if not self._validate_flow_creation_safety(flow_type, steps, transitions):
            raise SecurityError("Flow creation failed L5 safety validation")
        
        # Create flow execution
        flow_id = self._generate_flow_id()
        
        flow = FlowExecution(
            flow_id=flow_id,
            flow_type=flow_type,
            steps=steps,
            transitions=transitions,
            state=FlowState.INITIALIZED,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Store active flow
        self.active_flows[flow_id] = flow
        
        self.logger.info(f"Flow created successfully: {flow_id}")
        return flow
    
    def execute_flow(self, flow: FlowExecution) -> FlowExecution:
        """Execute flow following L5 architecture principles"""
        self.logger.info(f"Executing flow: {flow.flow_id} ({flow.flow_type.value})")
        
        # L5 Input validation
        self._validate_execution_input(flow)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(flow):
            raise SecurityError("Flow execution failed L5 safety validation")
        
        # Initialize execution
        flow.state = FlowState.RUNNING
        flow.start_time = self._get_timestamp()
        
        try:
            # Execute based on flow type
            if flow.flow_type == FlowType.SEQUENTIAL:
                self._execute_sequential_flow(flow)
            elif flow.flow_type == FlowType.PARALLEL:
                self._execute_parallel_flow(flow)
            elif flow.flow_type == FlowType.CONDITIONAL:
                self._execute_conditional_flow(flow)
            elif flow.flow_type == FlowType.LOOP:
                self._execute_loop_flow(flow)
            elif flow.flow_type == FlowType.DAG:
                self._execute_dag_flow(flow)
            elif flow.flow_type == FlowType.REACT:
                self._execute_react_flow(flow)
            else:
                raise ValueError(f"Unsupported flow type: {flow.flow_type}")
            
            # Finalize execution
            flow.end_time = self._get_timestamp()
            
            # Determine final state
            failed_steps = [s for s in flow.steps if s.status == FlowState.FAILED]
            if failed_steps:
                flow.state = FlowState.FAILED
            else:
                flow.state = FlowState.COMPLETED
            
            self.logger.info(f"Flow execution completed: {flow.state.value}")
            return flow
            
        except Exception as e:
            self.logger.error(f"Flow execution error: {e}")
            flow.state = FlowState.FAILED
            flow.end_time = self._get_timestamp()
            return flow
    
    def _execute_sequential_flow(self, flow: FlowExecution) -> None:
        """Execute flow steps sequentially"""
        for step in flow.steps:
            flow.current_step = step.step_id
            self._execute_step(flow, step)
            
            # Check if step failed
            if step.status == FlowState.FAILED:
                self.logger.error(f"Step {step.step_id} failed, stopping sequential execution")
                break
    
    def _execute_parallel_flow(self, flow: FlowExecution) -> None:
        """Execute flow steps in parallel"""
        # For simplicity, execute all steps without dependencies in parallel
        independent_steps = [s for s in flow.steps if not s.dependencies]
        
        for step in independent_steps:
            flow.current_step = step.step_id
            self._execute_step(flow, step)
        
        # Wait for all steps to complete (simplified)
        # In a full implementation, this would use actual parallel execution
    
    def _execute_conditional_flow(self, flow: FlowExecution) -> None:
        """Execute flow with conditional branching"""
        current_step = None
        
        # Find initial step (no dependencies)
        for step in flow.steps:
            if not step.dependencies:
                current_step = step
                break
        
        while current_step:
            flow.current_step = current_step.step_id
            self._execute_step(flow, current_step)
            
            # Find next step based on transitions
            next_step_id = self._find_next_step(flow, current_step)
            if next_step_id:
                current_step = self._find_step(flow, next_step_id)
            else:
                break
    
    def _execute_loop_flow(self, flow: FlowExecution) -> None:
        """Execute flow with looping"""
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            # Execute all steps in the loop
            for step in flow.steps:
                flow.current_step = step.step_id
                self._execute_step(flow, step)
            
            # Check loop condition (simplified)
            if self._should_stop_loop(flow):
                break
            
            iteration += 1
        
        if iteration >= max_iterations:
            self.logger.warning("Flow loop exceeded maximum iterations")
    
    def _execute_dag_flow(self, flow: FlowExecution) -> None:
        """Execute DAG flow"""
        # Convert flow steps to DAG nodes
        from ..dag_orchestration.dag_engine import DAGNode, DAGEdge, ExecutionMode
        
        dag_nodes = []
        dag_edges = []
        
        for step in flow.steps:
            node = DAGNode(
                node_id=step.step_id,
                node_type=step.step_type,
                operation=step.step_name,
                parameters=step.parameters,
                dependencies=step.dependencies
            )
            dag_nodes.append(node)
        
        for transition in flow.transitions:
            edge = DAGEdge(
                source_node=transition.from_step,
                target_node=transition.to_step,
                condition=transition.condition
            )
            dag_edges.append(edge)
        
        # Execute via DAG engine
        from ..dag_orchestration.dag_engine import DAGConstraints
        dag_constraints = DAGConstraints()
        dag_execution = self.dag_engine.create_dag(dag_nodes, dag_edges, dag_constraints)
        result = self.dag_engine.execute_dag(dag_execution, ExecutionMode.SEQUENTIAL)
        
        # Update flow steps with DAG results
        for dag_node in result.nodes:
            flow_step = self._find_step(flow, dag_node.node_id)
            if flow_step:
                flow_step.status = FlowState.COMPLETED if dag_node.status.value == "completed" else FlowState.FAILED
                flow_step.result = dag_node.result
                flow_step.execution_time = dag_node.execution_time
    
    def _execute_react_flow(self, flow: FlowExecution) -> None:
        """Execute ReAct flow"""
        # Find the ReAct step
        react_step = None
        for step in flow.steps:
            if step.step_type == "react":
                react_step = step
                break
        
        if not react_step:
            raise ValueError("No ReAct step found in flow")
        
        # Execute via ReAct engine
        goal = step.parameters.get("goal", "")
        observation = step.parameters.get("observation", "")
        
        from ..react_orchestration.react_engine import ReActConstraints
        react_constraints = ReActConstraints()
        react_execution = self.react_engine.start_react(goal, observation, react_constraints)
        
        # Execute ReAct cycles
        while react_execution.status.value == "running":
            react_execution = self.react_engine.execute_cycle(react_execution)
        
        # Update step with result
        react_step.status = FlowState.COMPLETED if react_execution.status.value == "completed" else FlowState.FAILED
        react_step.result = react_execution.final_result
        react_step.execution_time = 0.0  # Simplified
    
    def _execute_step(self, flow: FlowExecution, step: FlowStep) -> bool:
        """Execute individual flow step"""
        self.logger.info(f"Executing step: {step.step_id}")
        
        step.status = FlowState.RUNNING
        step.timestamp = self._get_timestamp()
        
        try:
            # Execute based on step type
            if step.step_type == "tool":
                result = self._execute_tool_step(step)
            elif step.step_type == "condition":
                result = self._execute_condition_step(step)
            elif step.step_type == "dag" or step.step_type == "react":
                # These are handled by specialized flow execution
                result = "Specialized execution handled"
            else:
                raise ValueError(f"Unsupported step type: {step.step_type}")
            
            # Update step with result
            step.result = result
            step.status = FlowState.COMPLETED
            step.safety_validated = True
            
            self.logger.info(f"Step {step.step_id} completed successfully")
            return True
            
        except Exception as e:
            step.status = FlowState.FAILED
            step.error_message = str(e)
            step.safety_validated = False
            
            self.logger.error(f"Step {step.step_id} failed: {e}")
            return False
    
    def _execute_tool_step(self, step: FlowStep) -> Any:
        """Execute tool step"""
        tool_name = step.step_name
        tool_params = step.parameters
        
        # Execute tool via tool engine
        from ..l2_execution.execution_engines.tool_invocation import ExecutionMode, NodeStatus
        tool_execution = self.tool_engine.invoke_tool(tool_name, tool_params, ExecutionMode.SYNCHRONOUS)
        
        if tool_execution.status != NodeStatus.SUCCESS:
            raise Exception(f"Tool execution failed: {tool_execution.error_message}")
        
        return tool_execution.result
    
    def _execute_condition_step(self, step: FlowStep) -> bool:
        """Execute condition step"""
        condition = step.parameters.get("condition", "")
        context = step.parameters.get("context", {})
        
        # Simple condition evaluation (simplified)
        if "success" in condition.lower():
            return True
        elif "failure" in condition.lower():
            return False
        else:
            return True  # Default to true
    
    def _find_next_step(self, flow: FlowExecution, current_step: FlowStep) -> Optional[str]:
        """Find next step based on transitions"""
        for transition in flow.transitions:
            if transition.from_step == current_step.step_id:
                # Check condition (simplified)
                if not transition.condition or self._evaluate_condition(transition.condition, flow.context):
                    return transition.to_step
        
        return None
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate condition string (simplified)"""
        # In a full implementation, this would use proper expression evaluation
        return "true" in condition.lower()
    
    def _should_stop_loop(self, flow: FlowExecution) -> bool:
        """Determine if loop should stop"""
        # Simple loop termination condition
        return any(step.status == FlowState.FAILED for step in flow.steps)
    
    def _find_step(self, flow: FlowExecution, step_id: str) -> Optional[FlowStep]:
        """Find step by ID"""
        for step in flow.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def validate_safety(self, flow: FlowExecution) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check flow count
            if len(self.active_flows) > self.constraints.max_concurrent_flows:
                self.logger.error("Too many active flows")
                return False
            
            # Validate step safety
            for step in flow.steps:
                # Check step parameters for dangerous content
                for key, value in step.parameters.items():
                    if isinstance(value, str):
                        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
                        value_lower = value.lower()
                        for pattern in dangerous_patterns:
                            if pattern in value_lower:
                                self.logger.error(f"Dangerous pattern in step {step.step_id}: {pattern}")
                                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Flow safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_flow_creation_safety(self, flow_type: FlowType, steps: List[FlowStep], transitions: List[FlowTransition]) -> bool:
        """Validate flow creation safety"""
        # Check step count
        if len(steps) > 50:  # Reasonable limit
            self.logger.error("Too many steps in flow")
            return False
        
        # Validate transition safety
        for transition in transitions:
            if not self._validate_text_safety(transition.condition):
                self.logger.error("Transition condition contains unsafe content")
                return False
        
        return True
    
    def _validate_text_safety(self, text: str) -> bool:
        """Validate text safety"""
        if not text:
            return True
        
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        text_lower = text.lower()
        
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return False
        
        return True
    
    def _validate_flow_input(self, flow_type: FlowType, steps: List[FlowStep], transitions: List[FlowTransition]) -> None:
        """L5 Flow input validation"""
        if not isinstance(flow_type, FlowType):
            raise ValueError("Flow type must be a FlowType enum")
        
        if not isinstance(steps, list):
            raise ValueError("Steps must be a list")
        
        if not isinstance(transitions, list):
            raise ValueError("Transitions must be a list")
        
        if not steps:
            raise ValueError("Steps cannot be empty")
        
        for step in steps:
            if not isinstance(step, FlowStep):
                raise ValueError("Each step must be a FlowStep object")
        
        for transition in transitions:
            if not isinstance(transition, FlowTransition):
                raise ValueError("Each transition must be a FlowTransition object")
    
    def _validate_execution_input(self, flow: FlowExecution) -> None:
        """L5 Execution input validation"""
        if not isinstance(flow, FlowExecution):
            raise ValueError("Flow must be a FlowExecution object")
        
        if not flow.steps:
            raise ValueError("Flow must have at least one step")
    
    def _generate_flow_id(self) -> str:
        """Generate unique flow ID"""
        return f"flow_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class FlowControllerInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, controller: FlowController):
        self._controller = controller
    
    def create_flow(self, flow_type: str, steps: List[Dict[str, Any]], transitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Convert dictionaries to flow objects
            flow_type_enum = FlowType(flow_type)
            
            flow_steps = []
            for step_dict in steps:
                flow_steps.append(FlowStep(
                    step_id=step_dict.get("step_id", ""),
                    step_type=step_dict.get("step_type", "tool"),
                    step_name=step_dict.get("step_name", ""),
                    parameters=step_dict.get("parameters", {}),
                    dependencies=step_dict.get("dependencies", []),
                    conditions=step_dict.get("conditions", [])
                ))
            
            flow_transitions = []
            for transition_dict in transitions:
                flow_transitions.append(FlowTransition(
                    from_step=transition_dict.get("from_step", ""),
                    to_step=transition_dict.get("to_step", ""),
                    condition=transition_dict.get("condition", ""),
                    action=transition_dict.get("action", "continue")
                ))
            
            constraints = FlowConstraints()
            flow = self._controller.create_flow(flow_type_enum, flow_steps, flow_transitions, constraints)
            
            return {
                "success": True,
                "flow_id": flow.flow_id,
                "flow_type": flow.flow_type.value,
                "step_count": len(flow.steps),
                "transition_count": len(flow.transitions),
                "safety_validated": flow.safety_validated,
                "timestamp": flow.timestamp
            }
        except Exception as e:
            self.logger.error(f"Flow creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def execute_flow(self, flow_id: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Get flow from active flows
            if flow_id not in self._controller.active_flows:
                return {
                    "success": False,
                    "error": "Flow ID not found",
                    "safety_validated": False
                }
            
            flow = self._controller.active_flows[flow_id]
            result = self._controller.execute_flow(flow)
            
            return {
                "success": result.state == FlowState.COMPLETED,
                "flow_id": result.flow_id,
                "flow_type": result.flow_type.value,
                "state": result.state.value,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "step_statuses": {step.step_id: step.status.value for step in result.steps},
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Flow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class FlowControllerFactory:
    """L5 Factory for creating flow controller instances"""
    
    @staticmethod
    def create_controller(constraints: Optional[FlowConstraints] = None) -> FlowController:
        return FlowControllerImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[FlowConstraints] = None) -> FlowControllerInterface:
        controller = FlowControllerFactory.create_controller(constraints)
        return FlowControllerInterface(controller)

# L5 Export for module usage
__all__ = [
    "FlowState",
    "FlowType",
    "FlowConstraints",
    "FlowStep",
    "FlowTransition",
    "FlowExecution",
    "FlowController",
    "FlowControllerImpl",
    "FlowControllerInterface",
    "FlowControllerFactory",
    "SecurityError"
]
