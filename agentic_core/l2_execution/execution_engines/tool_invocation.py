"""
L5 Agentic Core - L2 Execution Layer - Tool Invocation Engine
Implements L2 Pure Execution Layer for safe tool invocation and execution
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import time
import uuid

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    """L5 Tool status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INVALID_TOOL = "invalid_tool"
    INVALID_PARAMETERS = "invalid_parameters"
    SAFETY_VIOLATION = "safety_violation"

class ExecutionMode(Enum):
    """L5 Execution mode enumeration"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    FIRE_AND_FORGET = "fire_and_forget"

@dataclass
class ToolConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_execution_time: float = 30.0
    max_parameter_size: int = 10000  # 10KB
    allowed_tools: List[str] = field(default_factory=list)
    blocked_tools: List[str] = field(default_factory=lambda: ["exec", "eval", "compile", "open"])
    require_validation: bool = True
    safety_level: str = "strict"

@dataclass
class ToolParameter:
    """L5 Tool parameter structure with full type safety"""
    name: str
    value: Any
    type_hint: str = "any"
    required: bool = True
    validated: bool = False

@dataclass
class ToolDefinition:
    """L5 Tool definition structure"""
    tool_id: str
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    function: Optional[Callable] = None
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class ToolExecution:
    """L5 Tool execution structure"""
    execution_id: str
    tool_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    status: ToolStatus = ToolStatus.FAILED
    safety_validated: bool = False
    timestamp: str = ""

class ToolInvocationEngine(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def register_tool(self, tool: ToolDefinition) -> bool:
        """Register a tool with L5 safety constraints"""
        pass
    
    @abstractmethod
    def invoke_tool(self, tool_id: str, parameters: Dict[str, Any], mode: ExecutionMode) -> ToolExecution:
        """Invoke tool with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, tool_id: str, parameters: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class ToolInvocationEngineImpl(ToolInvocationEngine):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure tool invocation execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ToolConstraints] = None):
        self.constraints = constraints or ToolConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.registered_tools: Dict[str, ToolDefinition] = {}
        self.execution_history: List[ToolExecution] = []
    
    def register_tool(self, tool: ToolDefinition) -> bool:
        """Register a tool following L5 architecture principles"""
        self.logger.info(f"Registering tool: {tool.tool_id}")
        
        # L5 Input validation
        self._validate_tool_input(tool)
        
        # L5 Safety validation - fail-closed
        if not self._validate_tool_safety(tool):
            raise SecurityError("Tool failed L5 safety validation")
        
        # Check if tool is blocked
        if tool.tool_id in self.constraints.blocked_tools:
            self.logger.error(f"Tool is blocked: {tool.tool_id}")
            return False
        
        # Check allowed tools list (if specified)
        if (self.constraints.allowed_tools and 
            tool.tool_id not in self.constraints.allowed_tools):
            self.logger.error(f"Tool not in allowed list: {tool.tool_id}")
            return False
        
        # Validate tool function
        if not tool.function or not callable(tool.function):
            self.logger.error("Tool function is not callable")
            return False
        
        # Register the tool
        tool.safety_validated = True
        tool.timestamp = self._get_timestamp()
        self.registered_tools[tool.tool_id] = tool
        
        self.logger.info(f"Tool registered successfully: {tool.tool_id}")
        return True
    
    def invoke_tool(self, tool_id: str, parameters: Dict[str, Any], mode: ExecutionMode) -> ToolExecution:
        """Invoke tool following L5 architecture principles"""
        execution_id = self._generate_execution_id()
        self.logger.info(f"Invoking tool: {tool_id} with mode: {mode.value}")
        
        # L5 Input validation
        self._validate_invocation_input(tool_id, parameters, mode)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(tool_id, parameters):
            raise SecurityError("Tool invocation failed L5 safety validation")
        
        # Check if tool is registered
        if tool_id not in self.registered_tools:
            return ToolExecution(
                execution_id=execution_id,
                tool_id=tool_id,
                status=ToolStatus.INVALID_TOOL,
                error_message="Tool not registered",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        
        tool = self.registered_tools[tool_id]
        
        # Validate parameters
        validation_result = self._validate_parameters(tool, parameters)
        if not validation_result.valid:
            return ToolExecution(
                execution_id=execution_id,
                tool_id=tool_id,
                parameters=parameters,
                status=ToolStatus.INVALID_PARAMETERS,
                error_message=f"Parameter validation failed: {validation_result.error}",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        
        # Execute tool
        execution = self._execute_tool(tool, parameters, mode, execution_id)
        
        # Store in history
        self.execution_history.append(execution)
        
        self.logger.info(f"Tool invocation completed: {execution.status.value}")
        return execution
    
    def _execute_tool(self, tool: ToolDefinition, parameters: Dict[str, Any], mode: ExecutionMode, execution_id: str) -> ToolExecution:
        """Execute the tool with safety constraints"""
        start_time = time.time()
        
        try:
            if mode == ExecutionMode.SYNCHRONOUS:
                # Synchronous execution
                result = tool.function(**parameters)
                execution_time = time.time() - start_time
                
                return ToolExecution(
                    execution_id=execution_id,
                    tool_id=tool.tool_id,
                    parameters=parameters,
                    result=result,
                    execution_time=execution_time,
                    status=ToolStatus.SUCCESS,
                    safety_validated=True,
                    timestamp=self._get_timestamp()
                )
            
            elif mode == ExecutionMode.ASYNCHRONOUS:
                # Asynchronous execution (mock implementation)
                # In production, this would use actual async execution
                result = tool.function(**parameters)
                execution_time = time.time() - start_time
                
                return ToolExecution(
                    execution_id=execution_id,
                    tool_id=tool.tool_id,
                    parameters=parameters,
                    result=result,
                    execution_time=execution_time,
                    status=ToolStatus.SUCCESS,
                    safety_validated=True,
                    timestamp=self._get_timestamp()
                )
            
            elif mode == ExecutionMode.FIRE_AND_FORGET:
                # Fire and forget execution (mock implementation)
                # In production, this would spawn a background task
                try:
                    tool.function(**parameters)
                    execution_time = time.time() - start_time
                    
                    return ToolExecution(
                        execution_id=execution_id,
                        tool_id=tool.tool_id,
                        parameters=parameters,
                        result=None,  # Fire and forget doesn't return results
                        execution_time=execution_time,
                        status=ToolStatus.SUCCESS,
                        safety_validated=True,
                        timestamp=self._get_timestamp()
                    )
                except Exception as e:
                    # Even fire and forget should log errors
                    self.logger.error(f"Fire and forget execution failed: {e}")
                    return ToolExecution(
                        execution_id=execution_id,
                        tool_id=tool.tool_id,
                        parameters=parameters,
                        error_message=str(e),
                        execution_time=time.time() - start_time,
                        status=ToolStatus.FAILED,
                        safety_validated=False,
                        timestamp=self._get_timestamp()
                    )
            
            else:
                raise ValueError(f"Unsupported execution mode: {mode}")
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Tool execution failed: {e}")
            
            return ToolExecution(
                execution_id=execution_id,
                tool_id=tool.tool_id,
                parameters=parameters,
                error_message=str(e),
                execution_time=execution_time,
                status=ToolStatus.FAILED,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _validate_parameters(self, tool: ToolDefinition, parameters: Dict[str, Any]) -> 'ValidationResult':
        """Validate tool parameters"""
        missing_params = []
        invalid_params = []
        
        # Check required parameters
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                missing_params.append(param.name)
        
        # Check parameter types and values
        for param_name, param_value in parameters.items():
            # Find parameter definition
            param_def = next((p for p in tool.parameters if p.name == param_name), None)
            
            if param_def:
                # Basic type validation
                if param_def.type_hint != "any":
                    if not self._validate_parameter_type(param_value, param_def.type_hint):
                        invalid_params.append(f"{param_name}: invalid type")
                
                # Size validation
                if len(str(param_value)) > self.constraints.max_parameter_size:
                    invalid_params.append(f"{param_name}: parameter too large")
        
        if missing_params or invalid_params:
            error_parts = []
            if missing_params:
                error_parts.append(f"Missing: {missing_params}")
            if invalid_params:
                error_parts.append(f"Invalid: {invalid_params}")
            
            return ValidationResult(valid=False, error="; ".join(error_parts))
        
        return ValidationResult(valid=True)
    
    def _validate_parameter_type(self, value: Any, type_hint: str) -> bool:
        """Validate parameter type"""
        type_map = {
            "str": str,
            "int": int,
            "float": (int, float),
            "bool": bool,
            "list": list,
            "dict": dict,
            "any": object
        }
        
        expected_type = type_map.get(type_hint, object)
        return isinstance(value, expected_type)
    
    def validate_safety(self, tool_id: str, parameters: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check tool safety
            if tool_id in self.constraints.blocked_tools:
                self.logger.error(f"Tool is blocked: {tool_id}")
                return False
            
            # Check parameter safety
            for param_name, param_value in parameters.items():
                # Check for dangerous patterns in string parameters
                if isinstance(param_value, str):
                    dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
                    param_lower = param_value.lower()
                    
                    for pattern in dangerous_patterns:
                        if pattern in param_lower:
                            self.logger.error(f"Dangerous pattern in parameter {param_name}: {pattern}")
                            return False
                
                # Check parameter size
                if len(str(param_value)) > self.constraints.max_parameter_size:
                    self.logger.error(f"Parameter {param_name} too large")
                    return False
            
            self.logger.info("Tool invocation passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_tool_safety(self, tool: ToolDefinition) -> bool:
        """Validate tool safety"""
        try:
            # Check tool name
            dangerous_names = ["exec", "eval", "compile", "open", "file", "import"]
            if tool.tool_id.lower() in dangerous_names:
                self.logger.error(f"Dangerous tool name: {tool.tool_id}")
                return False
            
            # Check function name
            if tool.function:
                func_name = getattr(tool.function, '__name__', '')
                if func_name.lower() in dangerous_names:
                    self.logger.error(f"Dangerous function name: {func_name}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tool safety validation error: {e}")
            return False
    
    def _validate_tool_input(self, tool: ToolDefinition) -> None:
        """L5 Tool input validation"""
        if not isinstance(tool, ToolDefinition):
            raise ValueError("Tool must be a ToolDefinition object")
        
        if not tool.tool_id or not tool.tool_id.strip():
            raise ValueError("Tool ID cannot be empty")
        
        if not tool.name or not tool.name.strip():
            raise ValueError("Tool name cannot be empty")
    
    def _validate_invocation_input(self, tool_id: str, parameters: Dict[str, Any], mode: ExecutionMode) -> None:
        """L5 Invocation input validation"""
        if not isinstance(tool_id, str):
            raise ValueError("Tool ID must be a string")
        
        if not tool_id.strip():
            raise ValueError("Tool ID cannot be empty")
        
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary")
        
        if not isinstance(mode, ExecutionMode):
            raise ValueError("Mode must be an ExecutionMode enum")
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        return f"exec_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

@dataclass
class ValidationResult:
    """L5 Validation result structure"""
    valid: bool
    error: str = ""

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class ToolInvocationEngineInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, engine: ToolInvocationEngine):
        self._engine = engine
    
    def invoke_tool(self, tool_id: str, parameters: Dict[str, Any], mode: str = "synchronous") -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            execution_mode = ExecutionMode(mode)
            execution = self._engine.invoke_tool(tool_id, parameters, execution_mode)
            
            return {
                "success": execution.status == ToolStatus.SUCCESS,
                "execution_id": execution.execution_id,
                "tool_id": execution.tool_id,
                "result": str(execution.result) if execution.result is not None else None,
                "execution_time": execution.execution_time,
                "status": execution.status.value,
                "error_message": execution.error_message,
                "safety_validated": execution.safety_validated,
                "timestamp": execution.timestamp
            }
        except Exception as e:
            self.logger.error(f"Tool invocation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class ToolInvocationEngineFactory:
    """L5 Factory for creating tool invocation engine instances"""
    
    @staticmethod
    def create_engine(constraints: Optional[ToolConstraints] = None) -> ToolInvocationEngine:
        return ToolInvocationEngineImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ToolConstraints] = None) -> ToolInvocationEngineInterface:
        engine = ToolInvocationEngineFactory.create_engine(constraints)
        return ToolInvocationEngineInterface(engine)

# L5 Export for module usage
__all__ = [
    "ToolStatus",
    "ExecutionMode",
    "ToolConstraints",
    "ToolParameter",
    "ToolDefinition",
    "ToolExecution",
    "ToolInvocationEngine",
    "ToolInvocationEngineImpl",
    "ToolInvocationEngineInterface",
    "ToolInvocationEngineFactory",
    "ValidationResult",
    "SecurityError"
]
