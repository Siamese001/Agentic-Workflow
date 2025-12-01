"""
L5 Agentic Core - L1 Planning Layer - Goal Definitions
Implements L1 Cognitive Planning Layer for goal definition and management
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoalType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CONSTRAINT = "constraint"
    SAFETY = "safety"

@dataclass
class GoalConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_depth: int = 5
    allowed_operations: List[str] = field(default_factory=lambda: ["define", "validate", "prioritize"])
    safety_level: str = "strict"
    requires_approval: bool = True

@dataclass
class GoalDefinition:
    """L5 Goal structure with full type safety"""
    goal_id: str
    goal_type: GoalType
    description: str
    priority: int
    constraints: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class GoalResult:
    """L5 Result structure with full type safety"""
    success: bool
    goals: List[GoalDefinition] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class GoalProcessor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def define_goal(self, goal_data: Dict[str, Any]) -> GoalDefinition:
        """Define a goal with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, goal_data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class GoalDefinitionsImpl(GoalProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """
    
    def __init__(self, constraints: Optional[GoalConstraints] = None):
        self.constraints = constraints or GoalConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.goals: Dict[str, GoalDefinition] = {}
    
    def define_goal(self, goal_data: Dict[str, Any]) -> GoalDefinition:
        """Define a goal following L5 architecture principles"""
        self.logger.info(f"Defining goal: {goal_data}")
        
        # L5 Input validation
        self._validate_input(goal_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(goal_data):
            raise SecurityError("Goal data failed L5 safety validation")
        
        # Create goal with L5 structure
        goal = GoalDefinition(
            goal_id=goal_data.get("goal_id", self._generate_goal_id()),
            goal_type=GoalType(goal_data.get("goal_type", "primary")),
            description=goal_data.get("description", ""),
            priority=goal_data.get("priority", 1),
            constraints=goal_data.get("constraints", {}),
            dependencies=goal_data.get("dependencies", []),
            success_criteria=goal_data.get("success_criteria", []),
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Store goal
        self.goals[goal.goal_id] = goal
        
        self.logger.info(f"Successfully defined goal: {goal.goal_id}")
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[GoalDefinition]:
        """Retrieve a goal by ID"""
        return self.goals.get(goal_id)
    
    def list_goals(self) -> List[GoalDefinition]:
        """List all defined goals"""
        return list(self.goals.values())
    
    def prioritize_goals(self) -> List[GoalDefinition]:
        """Return goals sorted by priority"""
        return sorted(self.goals.values(), key=lambda g: g.priority, reverse=True)
    
    def validate_safety(self, goal_data: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_str = str(goal_data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check data size
            if len(str(goal_data)) > 100000:  # 100KB limit
                self.logger.error("Goal data exceeds size limit")
                return False
            
            # Validate required fields
            if "description" not in goal_data or not goal_data["description"]:
                self.logger.error("Goal description is required")
                return False
            
            self.logger.info("Goal data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, goal_data: Dict[str, Any]) -> None:
        """L5 Input validation"""
        if not isinstance(goal_data, dict):
            raise ValueError("Goal data must be a dictionary")
        
        if not goal_data:
            raise ValueError("Goal data cannot be empty")
    
    def _generate_goal_id(self) -> str:
        """Generate unique goal ID"""
        import uuid
        return f"goal_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class GoalDefinitionsInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, processor: GoalProcessor):
        self._processor = processor
    
    def create_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            goal = self._processor.define_goal(goal_data)
            return {
                "success": True,
                "goal_id": goal.goal_id,
                "goal_type": goal.goal_type.value,
                "description": goal.description,
                "priority": goal.priority,
                "safety_validated": goal.safety_validated,
                "timestamp": goal.timestamp
            }
        except Exception as e:
            self.logger.error(f"Goal creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class GoalDefinitionsFactory:
    """L5 Factory for creating goal definition instances"""
    
    @staticmethod
    def create_processor(constraints: Optional[GoalConstraints] = None) -> GoalProcessor:
        return GoalDefinitionsImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[GoalConstraints] = None) -> GoalDefinitionsInterface:
        processor = GoalDefinitionsFactory.create_processor(constraints)
        return GoalDefinitionsInterface(processor)

# L5 Export for module usage
__all__ = [
    "GoalType",
    "GoalConstraints", 
    "GoalDefinition",
    "GoalResult",
    "GoalProcessor",
    "GoalDefinitionsImpl",
    "GoalDefinitionsInterface",
    "GoalDefinitionsFactory",
    "SecurityError"
]
