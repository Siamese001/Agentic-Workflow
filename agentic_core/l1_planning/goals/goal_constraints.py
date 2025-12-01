"""
L5 Agentic Core - L1 Planning Layer - Goal Constraints
Implements L1 Cognitive Planning Layer for goal constraint validation
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    HARD = "hard"  # Must be satisfied
    SOFT = "soft"  # Can be violated with penalty
    SAFETY = "safety"  # Security constraints
    PERFORMANCE = "performance"  # Resource constraints

@dataclass
class ConstraintRule:
    """L5 Constraint rule structure"""
    rule_id: str
    constraint_type: ConstraintType
    condition: str
    penalty: float = 0.0
    description: str = ""
    safety_critical: bool = False

@dataclass
class GoalConstraint:
    """L5 Goal constraint structure with full type safety"""
    constraint_id: str
    goal_id: str
    rule: ConstraintRule
    value: Any
    satisfied: bool = False
    violation_reason: str = ""
    timestamp: str = ""

@dataclass
class ConstraintValidationResult:
    """L5 Result structure with full type safety"""
    success: bool
    constraints: List[GoalConstraint] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class GoalConstraintsProcessor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def validate_constraints(self, goal_data: Dict[str, Any], constraints: List[ConstraintRule]) -> ConstraintValidationResult:
        """Validate constraints with L5 safety"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class GoalConstraintsImpl(GoalConstraintsProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure constraint validation with no side effects
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.constraint_rules: Dict[str, ConstraintRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default constraint rules"""
        default_rules = [
            ConstraintRule(
                rule_id="max_depth",
                constraint_type=ConstraintType.HARD,
                condition="depth <= 5",
                description="Maximum goal depth limit",
                safety_critical=True
            ),
            ConstraintRule(
                rule_id="priority_range",
                constraint_type=ConstraintType.HARD,
                condition="1 <= priority <= 10",
                description="Priority must be between 1 and 10",
                safety_critical=False
            ),
            ConstraintRule(
                rule_id="description_length",
                constraint_type=ConstraintType.SOFT,
                condition="len(description) <= 500",
                penalty=0.1,
                description="Description should be concise",
                safety_critical=False
            ),
            ConstraintRule(
                rule_id="no_code_injection",
                constraint_type=ConstraintType.SAFETY,
                condition="not any(pattern in description.lower() for pattern in ['<script', 'javascript:', 'eval(', 'exec('])",
                description="No code injection in description",
                safety_critical=True
            )
        ]
        
        for rule in default_rules:
            self.constraint_rules[rule.rule_id] = rule
    
    def add_constraint_rule(self, rule: ConstraintRule) -> None:
        """Add a new constraint rule"""
        self.constraint_rules[rule.rule_id] = rule
        self.logger.info(f"Added constraint rule: {rule.rule_id}")
    
    def validate_constraints(self, goal_data: Dict[str, Any], constraints: List[ConstraintRule]) -> ConstraintValidationResult:
        """Validate constraints following L5 architecture principles"""
        self.logger.info(f"Validating constraints for goal: {goal_data.get('goal_id', 'unknown')}")
        
        # L5 Input validation
        self._validate_input(goal_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(goal_data):
            raise SecurityError("Goal data failed L5 safety validation")
        
        validated_constraints = []
        violations = []
        
        # Use provided constraints or default ones
        rules_to_check = constraints or list(self.constraint_rules.values())
        
        for rule in rules_to_check:
            constraint = self._evaluate_rule(goal_data, rule)
            validated_constraints.append(constraint)
            
            if not constraint.satisfied:
                violations.append(constraint.violation_reason)
                
                # Fail immediately on safety critical violations
                if rule.safety_critical:
                    self.logger.error(f"Safety critical constraint violated: {rule.rule_id}")
                    raise SecurityError(f"Safety constraint violated: {constraint.violation_reason}")
        
        result = ConstraintValidationResult(
            success=len(violations) == 0,
            constraints=validated_constraints,
            violations=violations,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Constraint validation completed: {len(violations)} violations")
        return result
    
    def _evaluate_rule(self, goal_data: Dict[str, Any], rule: ConstraintRule) -> GoalConstraint:
        """Evaluate a single constraint rule"""
        try:
            # Create a safe evaluation context
            context = {
                'depth': goal_data.get('depth', 1),
                'priority': goal_data.get('priority', 1),
                'description': goal_data.get('description', ''),
                'len': len,
                'any': any,
                'not': not
            }
            
            # Evaluate condition safely
            satisfied = eval(rule.condition, {"__builtins__": {}}, context)
            
            return GoalConstraint(
                constraint_id=f"{goal_data.get('goal_id', 'unknown')}_{rule.rule_id}",
                goal_id=goal_data.get('goal_id', 'unknown'),
                rule=rule,
                value=goal_data,
                satisfied=satisfied,
                violation_reason="" if satisfied else f"Constraint violated: {rule.condition}",
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return GoalConstraint(
                constraint_id=f"{goal_data.get('goal_id', 'unknown')}_{rule.rule_id}",
                goal_id=goal_data.get('goal_id', 'unknown'),
                rule=rule,
                value=goal_data,
                satisfied=False,
                violation_reason=f"Rule evaluation error: {str(e)}",
                timestamp=self._get_timestamp()
            )
    
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
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class GoalConstraintsInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, processor: GoalConstraintsProcessor):
        self._processor = processor
    
    def validate_goal_constraints(self, goal_data: Dict[str, Any], constraints: Optional[List[ConstraintRule]] = None) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.validate_constraints(goal_data, constraints or [])
            return {
                "success": result.success,
                "constraint_count": len(result.constraints),
                "violation_count": len(result.violations),
                "violations": result.violations,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Constraint validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class GoalConstraintsFactory:
    """L5 Factory for creating goal constraint instances"""
    
    @staticmethod
    def create_processor() -> GoalConstraintsProcessor:
        return GoalConstraintsImpl()
    
    @staticmethod
    def create_interface() -> GoalConstraintsInterface:
        processor = GoalConstraintsFactory.create_processor()
        return GoalConstraintsInterface(processor)

# L5 Export for module usage
__all__ = [
    "ConstraintType",
    "ConstraintRule",
    "GoalConstraint",
    "ConstraintValidationResult",
    "GoalConstraintsProcessor",
    "GoalConstraintsImpl",
    "GoalConstraintsInterface",
    "GoalConstraintsFactory",
    "SecurityError"
]
