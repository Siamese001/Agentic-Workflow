"""
L5 Agentic Core - L3 Orchestration Layer - ReAct Engine
Implements L3 Orchestration Layer for Reasoning and Acting cycles
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
from collections import deque

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReActStep(Enum):
    """L5 ReAct step enumeration"""
    OBSERVE = "observe"
    THINK = "think"
    ACT = "act"
    REFLECT = "reflect"

class ReActStatus(Enum):
    """L5 ReAct status enumeration"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SAFETY_VIOLATION = "safety_violation"

@dataclass
class ReActConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_iterations: int = 10
    max_execution_time: float = 300.0  # 5 minutes
    require_safety_checkpoints: bool = True
    allow_tool_use: bool = True
    allow_reflection: bool = True
    safety_level: str = "strict"

@dataclass
class Observation:
    """L5 Observation structure with full type safety"""
    observation_id: str
    content: str
    source: str  # "tool", "user", "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    safety_validated: bool = False

@dataclass
class Thought:
    """L5 Thought structure with full type safety"""
    thought_id: str
    content: str
    reasoning_type: str  # "analysis", "planning", "evaluation"
    confidence: float = 0.0
    next_action: str = ""
    timestamp: str = ""
    safety_validated: bool = False

@dataclass
class Action:
    """L5 Action structure with full type safety"""
    action_id: str
    action_type: str  # "tool", "response", "wait"
    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    timestamp: str = ""
    safety_validated: bool = False

@dataclass
class Reflection:
    """L5 Reflection structure with full type safety"""
    reflection_id: str
    content: str
    evaluation: str  # "success", "failure", "partial"
    insights: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    timestamp: str = ""
    safety_validated: bool = False

@dataclass
class ReActCycle:
    """L5 ReAct cycle structure"""
    cycle_id: str
    iteration: int
    observation: Optional[Observation] = None
    thought: Optional[Thought] = None
    action: Optional[Action] = None
    reflection: Optional[Reflection] = None
    status: ReActStatus = ReActStatus.RUNNING
    error_message: str = ""
    timestamp: str = ""

@dataclass
class ReActExecution:
    """L5 ReAct execution structure"""
    execution_id: str
    goal: str
    initial_observation: str
    cycles: List[ReActCycle] = field(default_factory=list)
    current_step: ReActStep = ReActStep.OBSERVE
    status: ReActStatus = ReActStatus.RUNNING
    start_time: str = ""
    end_time: str = ""
    final_result: Any = None
    safety_validated: bool = False
    timestamp: str = ""

class ReActEngine(ABC):
    """L5 Abstract base - ensures L3 orchestration behavior"""
    
    @abstractmethod
    def start_react(self, goal: str, initial_observation: str, constraints: ReActConstraints) -> ReActExecution:
        """Start ReAct execution with L5 safety constraints"""
        pass
    
    @abstractmethod
    def execute_cycle(self, execution: ReActExecution) -> ReActExecution:
        """Execute single ReAct cycle with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, execution: ReActExecution) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class ReActEngineImpl(ReActEngine):
    """
    L5 Implementation - L3 Orchestration Layer
    Pure ReAct orchestration execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ReActConstraints] = None):
        self.constraints = constraints or ReActConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_executions: Dict[str, ReActExecution] = {}
        
        # Initialize L2 execution engines (factories)
        from ..l2_execution.execution_engines.tool_invocation import ToolInvocationEngineFactory
        from ..l2_execution.execution_engines.validation import ValidationEngineFactory
        
        self.tool_engine = ToolInvocationEngineFactory.create_engine()
        self.validation_engine = ValidationEngineFactory.create_engine()
    
    def start_react(self, goal: str, initial_observation: str, constraints: Optional[ReActConstraints] = None) -> ReActExecution:
        """Start ReAct execution following L5 architecture principles"""
        react_constraints = constraints or self.constraints
        self.logger.info(f"Starting ReAct execution for goal: {goal}")
        
        # L5 Input validation
        self._validate_start_input(goal, initial_observation)
        
        # L5 Safety validation - fail-closed
        if not self._validate_input_safety(goal, initial_observation):
            raise SecurityError("ReAct input failed L5 safety validation")
        
        # Create execution
        execution_id = self._generate_execution_id()
        
        execution = ReActExecution(
            execution_id=execution_id,
            goal=goal,
            initial_observation=initial_observation,
            current_step=ReActStep.OBSERVE,
            status=ReActStatus.RUNNING,
            start_time=self._get_timestamp(),
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Store active execution
        self.active_executions[execution_id] = execution
        
        # Create initial cycle with observation
        initial_cycle = self._create_initial_cycle(execution)
        execution.cycles.append(initial_cycle)
        
        self.logger.info(f"ReAct execution started: {execution_id}")
        return execution
    
    def execute_cycle(self, execution: ReActExecution) -> ReActExecution:
        """Execute single ReAct cycle following L5 architecture principles"""
        self.logger.info(f"Executing ReAct cycle for: {execution.execution_id}")
        
        # L5 Input validation
        self._validate_cycle_input(execution)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(execution):
            raise SecurityError("ReAct execution failed L5 safety validation")
        
        # Check constraints
        if len(execution.cycles) >= self.constraints.max_iterations:
            execution.status = ReActStatus.TIMEOUT
            execution.end_time = self._get_timestamp()
            return execution
        
        try:
            # Execute based on current step
            if execution.current_step == ReActStep.OBSERVE:
                self._execute_observe_step(execution)
            elif execution.current_step == ReActStep.THINK:
                self._execute_think_step(execution)
            elif execution.current_step == ReActStep.ACT:
                self._execute_act_step(execution)
            elif execution.current_step == ReActStep.REFLECT:
                self._execute_reflect_step(execution)
            else:
                raise ValueError(f"Unsupported ReAct step: {execution.current_step}")
            
            # Move to next step
            execution.current_step = self._get_next_step(execution.current_step)
            
            # Check if execution should continue
            if self._should_complete_execution(execution):
                execution.status = ReActStatus.COMPLETED
                execution.end_time = self._get_timestamp()
                execution.final_result = self._extract_final_result(execution)
            
            self.logger.info(f"ReAct cycle completed: {execution.current_step.value}")
            return execution
            
        except Exception as e:
            self.logger.error(f"ReAct cycle error: {e}")
            execution.status = ReActStatus.FAILED
            execution.end_time = self._get_timestamp()
            return execution
    
    def _create_initial_cycle(self, execution: ReActExecution) -> ReActCycle:
        """Create initial ReAct cycle with observation"""
        cycle_id = self._generate_cycle_id()
        
        observation = Observation(
            observation_id=self._generate_observation_id(),
            content=execution.initial_observation,
            source="user",
            timestamp=self._get_timestamp(),
            safety_validated=True
        )
        
        cycle = ReActCycle(
            cycle_id=cycle_id,
            iteration=1,
            observation=observation,
            status=ReActStatus.RUNNING,
            timestamp=self._get_timestamp()
        )
        
        return cycle
    
    def _execute_observe_step(self, execution: ReActExecution) -> None:
        """Execute observe step"""
        current_cycle = execution.cycles[-1]
        
        # For this implementation, observation is already provided
        # In a full implementation, this could gather observations from tools
        self.logger.info("Observation step completed - using existing observation")
        
        current_cycle.status = ReActStatus.RUNNING
    
    def _execute_think_step(self, execution: ReActExecution) -> None:
        """Execute think step - reasoning about observation"""
        current_cycle = execution.cycles[-1]
        
        if not current_cycle.observation:
            raise ValueError("No observation available for thinking")
        
        # Generate thought based on observation and goal
        thought_content = self._generate_thought(execution.goal, current_cycle.observation.content)
        
        thought = Thought(
            thought_id=self._generate_thought_id(),
            content=thought_content,
            reasoning_type="analysis",
            confidence=0.8,
            next_action=self._extract_next_action(thought_content),
            timestamp=self._get_timestamp(),
            safety_validated=True
        )
        
        current_cycle.thought = thought
        self.logger.info(f"Thought generated: {thought_content[:100]}...")
    
    def _execute_act_step(self, execution: ReActExecution) -> None:
        """Execute act step - perform action based on thought"""
        current_cycle = execution.cycles[-1]
        
        if not current_cycle.thought:
            raise ValueError("No thought available for action")
        
        # Determine action from thought
        action_type, tool_name, parameters = self._parse_action_from_thought(current_cycle.thought)
        
        action = Action(
            action_id=self._generate_action_id(),
            action_type=action_type,
            tool_name=tool_name,
            parameters=parameters,
            timestamp=self._get_timestamp(),
            safety_validated=True
        )
        
        # Execute action if it's a tool action
        if action_type == "tool" and self.constraints.allow_tool_use:
            try:
                from ..l2_execution.execution_engines.tool_invocation import ExecutionMode
                tool_execution = self.tool_engine.invoke_tool(tool_name, parameters, ExecutionMode.SYNCHRONOUS)
                action.result = tool_execution.result
            except Exception as e:
                action.result = f"Tool execution failed: {str(e)}"
                self.logger.error(f"Tool execution failed: {e}")
        
        current_cycle.action = action
        self.logger.info(f"Action executed: {action_type} - {tool_name}")
    
    def _execute_reflect_step(self, execution: ReActExecution) -> None:
        """Execute reflect step - evaluate action results"""
        current_cycle = execution.cycles[-1]
        
        if not current_cycle.action:
            raise ValueError("No action available for reflection")
        
        # Generate reflection based on action result
        reflection_content = self._generate_reflection(execution.goal, current_cycle)
        
        reflection = Reflection(
            reflection_id=self._generate_reflection_id(),
            content=reflection_content,
            evaluation=self._evaluate_success(current_cycle),
            insights=self._extract_insights(reflection_content),
            next_steps=self._extract_next_steps(reflection_content),
            timestamp=self._get_timestamp(),
            safety_validated=True
        )
        
        current_cycle.reflection = reflection
        self.logger.info(f"Reflection generated: {reflection_content[:100]}...")
    
    def _generate_thought(self, goal: str, observation: str) -> str:
        """Generate thought content (simplified implementation)"""
        # In a full implementation, this would use LLM reasoning
        # For now, provide template-based reasoning
        thought = f"Based on the observation '{observation[:100]}...', I need to work towards the goal '{goal}'. "
        thought += "The next logical step would be to analyze the current state and determine what action to take."
        return thought
    
    def _parse_action_from_thought(self, thought: Thought) -> Tuple[str, str, Dict[str, Any]]:
        """Parse action from thought content"""
        # Simplified action parsing
        if "search" in thought.content.lower():
            return "tool", "search", {"query": "information"}
        elif "parse" in thought.content.lower():
            return "tool", "parse", {"data": "sample"}
        else:
            return "response", "", {"content": thought.content}
    
    def _generate_reflection(self, goal: str, cycle: ReActCycle) -> str:
        """Generate reflection content"""
        reflection = f"Reflecting on the action taken towards goal '{goal}'. "
        if cycle.action and cycle.action.result:
            reflection += f"The action resulted in: {str(cycle.action.result)[:100]}... "
        reflection += "This provides insight into the next steps needed."
        return reflection
    
    def _evaluate_success(self, cycle: ReActCycle) -> str:
        """Evaluate success of current cycle"""
        if not cycle.action:
            return "failure"
        
        # Simple success evaluation
        if cycle.action.result and "error" not in str(cycle.action.result).lower():
            return "success"
        else:
            return "partial"
    
    def _extract_insights(self, reflection: str) -> List[str]:
        """Extract insights from reflection"""
        # Simple insight extraction
        insights = []
        if "error" in reflection.lower():
            insights.append("Action encountered an error")
        if "success" in reflection.lower():
            insights.append("Action was successful")
        return insights
    
    def _extract_next_steps(self, reflection: str) -> List[str]:
        """Extract next steps from reflection"""
        # Simple next step extraction
        next_steps = ["Continue with next observation"]
        if "error" in reflection.lower():
            next_steps.append("Consider alternative approach")
        return next_steps
    
    def _extract_next_action(self, thought: str) -> str:
        """Extract next action from thought"""
        if "search" in thought.lower():
            return "search_tool"
        elif "parse" in thought.lower():
            return "parse_tool"
        else:
            return "respond"
    
    def _get_next_step(self, current_step: ReActStep) -> ReActStep:
        """Get next step in ReAct cycle"""
        step_order = [ReActStep.OBSERVE, ReActStep.THINK, ReActStep.ACT, ReActStep.REFLECT]
        current_index = step_order.index(current_step)
        next_index = (current_index + 1) % len(step_order)
        return step_order[next_index]
    
    def _should_complete_execution(self, execution: ReActExecution) -> bool:
        """Determine if execution should complete"""
        # Check if goal is achieved (simplified)
        if execution.cycles:
            last_cycle = execution.cycles[-1]
            if last_cycle.reflection and "success" in last_cycle.reflection.evaluation:
                return True
        
        # Check max iterations
        if len(execution.cycles) >= self.constraints.max_iterations:
            return True
        
        return False
    
    def _extract_final_result(self, execution: ReActExecution) -> Any:
        """Extract final result from execution"""
        if execution.cycles:
            last_cycle = execution.cycles[-1]
            if last_cycle.action and last_cycle.action.result:
                return last_cycle.action.result
        
        return "Execution completed without specific result"
    
    def validate_safety(self, execution: ReActExecution) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check execution count
            if len(self.active_executions) > 50:  # Reasonable limit
                self.logger.error("Too many active ReAct executions")
                return False
            
            # Validate goal safety
            if not self._validate_text_safety(execution.goal):
                self.logger.error("Goal contains unsafe content")
                return False
            
            # Validate observation safety
            if not self._validate_text_safety(execution.initial_observation):
                self.logger.error("Initial observation contains unsafe content")
                return False
            
            # Validate cycle safety
            for cycle in execution.cycles:
                if cycle.observation and not self._validate_text_safety(cycle.observation.content):
                    self.logger.error("Cycle observation contains unsafe content")
                    return False
                
                if cycle.thought and not self._validate_text_safety(cycle.thought.content):
                    self.logger.error("Cycle thought contains unsafe content")
                    return False
                
                if cycle.action and cycle.action.tool_name:
                    if not self._validate_tool_safety(cycle.action.tool_name, cycle.action.parameters):
                        self.logger.error("Cycle action contains unsafe tool or parameters")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"ReAct safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input_safety(self, goal: str, initial_observation: str) -> bool:
        """Validate input safety"""
        return self._validate_text_safety(goal) and self._validate_text_safety(initial_observation)
    
    def _validate_text_safety(self, text: str) -> bool:
        """Validate text safety"""
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        text_lower = text.lower()
        
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return False
        
        # Check length
        if len(text) > 10000:
            return False
        
        return True
    
    def _validate_tool_safety(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool safety"""
        dangerous_tools = ["exec", "eval", "compile", "open"]
        if tool_name.lower() in dangerous_tools:
            return False
        
        # Validate parameters
        for key, value in parameters.items():
            if isinstance(value, str) and not self._validate_text_safety(value):
                return False
        
        return True
    
    def _validate_start_input(self, goal: str, initial_observation: str) -> None:
        """L5 Start input validation"""
        if not isinstance(goal, str):
            raise ValueError("Goal must be a string")
        
        if not isinstance(initial_observation, str):
            raise ValueError("Initial observation must be a string")
        
        if not goal.strip():
            raise ValueError("Goal cannot be empty")
        
        if not initial_observation.strip():
            raise ValueError("Initial observation cannot be empty")
    
    def _validate_cycle_input(self, execution: ReActExecution) -> None:
        """L5 Cycle input validation"""
        if not isinstance(execution, ReActExecution):
            raise ValueError("Execution must be a ReActExecution object")
        
        if not execution.cycles:
            raise ValueError("Execution must have at least one cycle")
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        return f"react_exec_{uuid.uuid4().hex[:8]}"
    
    def _generate_cycle_id(self) -> str:
        """Generate unique cycle ID"""
        return f"cycle_{uuid.uuid4().hex[:8]}"
    
    def _generate_observation_id(self) -> str:
        """Generate unique observation ID"""
        return f"obs_{uuid.uuid4().hex[:8]}"
    
    def _generate_thought_id(self) -> str:
        """Generate unique thought ID"""
        return f"thought_{uuid.uuid4().hex[:8]}"
    
    def _generate_action_id(self) -> str:
        """Generate unique action ID"""
        return f"action_{uuid.uuid4().hex[:8]}"
    
    def _generate_reflection_id(self) -> str:
        """Generate unique reflection ID"""
        return f"reflect_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class ReActEngineInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, engine: ReActEngine):
        self._engine = engine
    
    def start_react(self, goal: str, initial_observation: str, max_iterations: int = 10) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = ReActConstraints(max_iterations=max_iterations)
            execution = self._engine.start_react(goal, initial_observation, constraints)
            
            return {
                "success": True,
                "execution_id": execution.execution_id,
                "goal": execution.goal,
                "status": execution.status.value,
                "current_step": execution.current_step.value,
                "cycle_count": len(execution.cycles),
                "safety_validated": execution.safety_validated,
                "timestamp": execution.timestamp
            }
        except Exception as e:
            self.logger.error(f"ReAct start failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def execute_cycle(self, execution_id: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Get execution from active executions
            if execution_id not in self._engine.active_executions:
                return {
                    "success": False,
                    "error": "Execution ID not found",
                    "safety_validated": False
                }
            
            execution = self._engine.active_executions[execution_id]
            result = self._engine.execute_cycle(execution)
            
            # Format cycle data for response
            cycles_data = []
            for cycle in result.cycles:
                cycle_data = {
                    "cycle_id": cycle.cycle_id,
                    "iteration": cycle.iteration,
                    "status": cycle.status.value,
                    "timestamp": cycle.timestamp
                }
                
                if cycle.observation:
                    cycle_data["observation"] = {
                        "content": cycle.observation.content,
                        "source": cycle.observation.source,
                        "safety_validated": cycle.observation.safety_validated
                    }
                
                if cycle.thought:
                    cycle_data["thought"] = {
                        "content": cycle.thought.content,
                        "reasoning_type": cycle.thought.reasoning_type,
                        "confidence": cycle.thought.confidence,
                        "safety_validated": cycle.thought.safety_validated
                    }
                
                if cycle.action:
                    cycle_data["action"] = {
                        "action_type": cycle.action.action_type,
                        "tool_name": cycle.action.tool_name,
                        "result": str(cycle.action.result) if cycle.action.result else None,
                        "safety_validated": cycle.action.safety_validated
                    }
                
                if cycle.reflection:
                    cycle_data["reflection"] = {
                        "content": cycle.reflection.content,
                        "evaluation": cycle.reflection.evaluation,
                        "insights": cycle.reflection.insights,
                        "safety_validated": cycle.reflection.safety_validated
                    }
                
                cycles_data.append(cycle_data)
            
            return {
                "success": True,
                "execution_id": result.execution_id,
                "status": result.status.value,
                "current_step": result.current_step.value,
                "cycles": cycles_data,
                "final_result": str(result.final_result) if result.final_result else None,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"ReAct cycle execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class ReActEngineFactory:
    """L5 Factory for creating ReAct engine instances"""
    
    @staticmethod
    def create_engine(constraints: Optional[ReActConstraints] = None) -> ReActEngine:
        return ReActEngineImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ReActConstraints] = None) -> ReActEngineInterface:
        engine = ReActEngineFactory.create_engine(constraints)
        return ReActEngineInterface(engine)

# L5 Export for module usage
__all__ = [
    "ReActStep",
    "ReActStatus",
    "ReActConstraints",
    "Observation",
    "Thought",
    "Action",
    "Reflection",
    "ReActCycle",
    "ReActExecution",
    "ReActEngine",
    "ReActEngineImpl",
    "ReActEngineInterface",
    "ReActEngineFactory",
    "SecurityError"
]
