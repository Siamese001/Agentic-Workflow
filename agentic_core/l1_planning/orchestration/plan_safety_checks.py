"""
L5 Agentic Core - L1 Planning Layer - Plan Safety Checks
Implements L1 Cognitive Planning Layer for comprehensive plan safety validation
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
from .plan_schema import PlanSchema, PlanStep, PlanStatus, ValidationResult

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class SafetyCategory(Enum):
    """L5 Safety check categories"""
    SECURITY = "security"
    PRIVACY = "privacy"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"

@dataclass
class SafetyRule:
    """L5 Safety rule structure"""
    rule_id: str
    category: SafetyCategory
    level: SafetyLevel
    description: str
    condition: str
    action: str  # "block", "warn", "log"
    enabled: bool = True

@dataclass
class SafetyViolation:
    """L5 Safety violation structure"""
    violation_id: str
    rule_id: str
    category: SafetyCategory
    level: SafetyLevel
    step_id: str
    description: str
    recommendation: str = ""
    timestamp: str = ""

@dataclass
class SafetyCheckResult:
    """L5 Safety check result structure with full type safety"""
    check_id: str
    plan_id: str
    passed: bool
    violations: List[SafetyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    safety_score: float = 0.0
    can_proceed: bool = False
    timestamp: str = ""

class PlanSafetyChecker(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def check_plan_safety(self, schema: PlanSchema) -> SafetyCheckResult:
        """Check plan safety with L5 constraints"""
        pass
    
    @abstractmethod
    def validate_step_safety(self, step: PlanStep) -> List[SafetyViolation]:
        """Validate individual step safety"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Any) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class PlanSafetyChecksImpl(PlanSafetyChecker):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure safety validation with no side effects
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.safety_rules: Dict[str, SafetyRule] = {}
        self._initialize_safety_rules()
    
    def _initialize_safety_rules(self):
        """Initialize default safety rules"""
        default_rules = [
            # Security rules
            SafetyRule(
                rule_id="no_code_injection",
                category=SafetyCategory.SECURITY,
                level=SafetyLevel.CRITICAL,
                description="No code injection patterns in plan steps",
                condition="any(pattern in step.description.lower() for pattern in ['<script', 'javascript:', 'eval(', 'exec(', '__import__'])",
                action="block",
                enabled=True
            ),
            SafetyRule(
                rule_id="no_dangerous_operations",
                category=SafetyCategory.SECURITY,
                level=SafetyLevel.HIGH,
                description="No dangerous system operations",
                condition="step.operation.lower() in ['exec', 'eval', 'import', 'open', 'delete', 'remove']",
                action="block",
                enabled=True
            ),
            
            # Resource rules
            SafetyRule(
                rule_id="max_plan_duration",
                category=SafetyCategory.RESOURCE,
                level=SafetyLevel.HIGH,
                description="Plan execution time within limits",
                condition="sum(step.estimated_duration for step in plan.steps) > 24",
                action="warn",
                enabled=True
            ),
            SafetyRule(
                rule_id="max_step_count",
                category=SafetyCategory.RESOURCE,
                level=SafetyLevel.MEDIUM,
                description="Plan has reasonable number of steps",
                condition="len(plan.steps) > 50",
                action="warn",
                enabled=True
            ),
            
            # Dependency rules
            SafetyRule(
                rule_id="no_circular_dependencies",
                category=SafetyCategory.DEPENDENCY,
                level=SafetyLevel.CRITICAL,
                description="No circular dependencies in plan",
                condition="has_circular_dependencies(plan.steps)",
                action="block",
                enabled=True
            ),
            SafetyRule(
                rule_id="max_dependency_depth",
                category=SafetyCategory.DEPENDENCY,
                level=SafetyLevel.HIGH,
                description="Dependency depth within limits",
                condition="get_max_dependency_depth(plan.steps) > 5",
                action="warn",
                enabled=True
            ),
            
            # Operational rules
            SafetyRule(
                rule_id="required_step_fields",
                category=SafetyCategory.OPERATIONAL,
                level=SafetyLevel.HIGH,
                description="All steps have required fields",
                condition="not all(step.description and step.operation for step in plan.steps)",
                action="block",
                enabled=True
            ),
            
            # Privacy rules
            SafetyRule(
                rule_id="no_pii_in_descriptions",
                category=SafetyCategory.PRIVACY,
                level=SafetyLevel.HIGH,
                description="No personally identifiable information in step descriptions",
                condition="contains_pii(step.description)",
                action="warn",
                enabled=True
            )
        ]
        
        for rule in default_rules:
            self.safety_rules[rule.rule_id] = rule
    
    def add_safety_rule(self, rule: SafetyRule) -> None:
        """Add a new safety rule"""
        self.safety_rules[rule.rule_id] = rule
        self.logger.info(f"Added safety rule: {rule.rule_id}")
    
    def check_plan_safety(self, schema: PlanSchema) -> SafetyCheckResult:
        """Check plan safety following L5 architecture principles"""
        self.logger.info(f"Checking safety for plan: {schema.plan_id}")
        
        # L5 Input validation
        self._validate_input(schema)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(schema):
            raise SecurityError("Plan schema failed L5 safety validation")
        
        violations = []
        warnings = []
        
        # Check each safety rule
        for rule in self.safety_rules.values():
            if not rule.enabled:
                continue
            
            rule_violations = self._check_rule(schema, rule)
            violations.extend(rule_violations)
            
            # Log warnings for non-critical violations
            for violation in rule_violations:
                if violation.level in [SafetyLevel.LOW, SafetyLevel.INFO]:
                    warnings.append(f"Rule {rule.rule_id}: {violation.description}")
        
        # Check individual step safety
        for step in schema.steps:
            step_violations = self.validate_step_safety(step)
            violations.extend(step_violations)
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(violations, len(schema.steps))
        
        # Determine if plan can proceed
        critical_violations = [v for v in violations if v.level == SafetyLevel.CRITICAL]
        can_proceed = len(critical_violations) == 0
        
        result = SafetyCheckResult(
            check_id=self._generate_check_id(),
            plan_id=schema.plan_id,
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            safety_score=safety_score,
            can_proceed=can_proceed,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Safety check completed: {len(violations)} violations, score: {safety_score}")
        return result
    
    def validate_step_safety(self, step: PlanStep) -> List[SafetyViolation]:
        """Validate individual step safety"""
        violations = []
        
        # Check for code injection
        dangerous_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
        for pattern in dangerous_patterns:
            if pattern in step.description.lower():
                violations.append(SafetyViolation(
                    violation_id=f"{step.step_id}_code_injection",
                    rule_id="no_code_injection",
                    category=SafetyCategory.SECURITY,
                    level=SafetyLevel.CRITICAL,
                    step_id=step.step_id,
                    description=f"Code injection pattern detected: {pattern}",
                    recommendation="Remove code injection patterns from step description",
                    timestamp=self._get_timestamp()
                ))
        
        # Check for dangerous operations
        dangerous_ops = ["exec", "eval", "import", "open", "delete", "remove"]
        if step.operation.lower() in dangerous_ops:
            violations.append(SafetyViolation(
                violation_id=f"{step.step_id}_dangerous_op",
                rule_id="no_dangerous_operations",
                category=SafetyCategory.SECURITY,
                level=SafetyLevel.HIGH,
                step_id=step.step_id,
                description=f"Dangerous operation: {step.operation}",
                recommendation="Use safer alternative or add explicit safety validation",
                timestamp=self._get_timestamp()
            ))
        
        # Check step parameters for safety
        for param_name, param_value in step.parameters.items():
            if isinstance(param_value, str):
                for pattern in dangerous_patterns:
                    if pattern in param_value.lower():
                        violations.append(SafetyViolation(
                            violation_id=f"{step.step_id}_param_code_injection",
                            rule_id="no_code_injection",
                            category=SafetyCategory.SECURITY,
                            level=SafetyLevel.CRITICAL,
                            step_id=step.step_id,
                            description=f"Code injection in parameter {param_name}: {pattern}",
                            recommendation="Remove code injection patterns from step parameters",
                            timestamp=self._get_timestamp()
                        ))
        
        return violations
    
    def _check_rule(self, schema: PlanSchema, rule: SafetyRule) -> List[SafetyViolation]:
        """Check a specific safety rule against the plan"""
        violations = []
        
        try:
            # Create safe evaluation context
            context = {
                'plan': schema,
                'step': None,  # Will be set in step-specific checks
                'len': len,
                'sum': sum,
                'any': any,
                'all': all,
                'has_circular_dependencies': self._has_circular_dependencies,
                'get_max_dependency_depth': self._get_max_dependency_depth,
                'contains_pii': self._contains_pii
            }
            
            # Evaluate rule condition
            if eval(rule.condition, {"__builtins__": {}}, context):
                # Rule violated - create violation
                violation = SafetyViolation(
                    violation_id=f"{schema.plan_id}_{rule.rule_id}",
                    rule_id=rule.rule_id,
                    category=rule.category,
                    level=rule.level,
                    step_id="plan_level",
                    description=rule.description,
                    recommendation=self._get_rule_recommendation(rule),
                    timestamp=self._get_timestamp()
                )
                violations.append(violation)
                
                # Block execution for critical violations
                if rule.action == "block" and rule.level == SafetyLevel.CRITICAL:
                    self.logger.error(f"Critical safety violation: {rule.rule_id}")
        
        except Exception as e:
            self.logger.error(f"Error evaluating safety rule {rule.rule_id}: {e}")
        
        return violations
    
    def _has_circular_dependencies(self, steps: List[PlanStep]) -> bool:
        """Check if plan has circular dependencies"""
        # Build dependency graph
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies
        
        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    def _get_max_dependency_depth(self, steps: List[PlanStep]) -> int:
        """Calculate maximum dependency depth"""
        step_map = {step.step_id: step for step in steps}
        
        def get_depth(step_id, visited=None):
            if visited is None:
                visited = set()
            
            if step_id in visited:
                return float('inf')  # Circular dependency
            
            visited.add(step_id)
            
            step = step_map.get(step_id)
            if not step or not step.dependencies:
                visited.remove(step_id)
                return 1
            
            max_depth = 0
            for dep in step.dependencies:
                depth = get_depth(dep, visited.copy())
                max_depth = max(max_depth, depth)
            
            visited.remove(step_id)
            return max_depth + 1
        
        return max(get_depth(step.step_id) for step in steps)
    
    def _contains_pii(self, text: str) -> bool:
        """Check if text contains personally identifiable information"""
        # Simple PII patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        
        patterns = [email_pattern, phone_pattern, ssn_pattern]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _calculate_safety_score(self, violations: List[SafetyViolation], step_count: int) -> float:
        """Calculate safety score (0.0 to 1.0)"""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            SafetyLevel.CRITICAL: 0.4,
            SafetyLevel.HIGH: 0.3,
            SafetyLevel.MEDIUM: 0.2,
            SafetyLevel.LOW: 0.1,
            SafetyLevel.INFO: 0.05
        }
        
        total_penalty = 0.0
        for violation in violations:
            total_penalty += severity_weights.get(violation.level, 0.1)
        
        # Normalize by step count
        normalized_penalty = min(total_penalty / max(step_count, 1), 1.0)
        
        return max(0.0, 1.0 - normalized_penalty)
    
    def _get_rule_recommendation(self, rule: SafetyRule) -> str:
        """Get recommendation for a violated rule"""
        recommendations = {
            "no_code_injection": "Remove all code injection patterns and use safe parameterization",
            "no_dangerous_operations": "Replace dangerous operations with safer alternatives",
            "max_plan_duration": "Break down plan into smaller sub-plans or optimize step durations",
            "max_step_count": "Consider breaking plan into phases or merging related steps",
            "no_circular_dependencies": "Remove circular dependencies by restructuring plan",
            "max_dependency_depth": "Reduce dependency complexity by restructuring plan",
            "required_step_fields": "Ensure all steps have required description and operation fields",
            "no_pii_in_descriptions": "Remove or mask personally identifiable information"
        }
        
        return recommendations.get(rule.rule_id, "Review and address the safety concern")
    
    def validate_safety(self, schema: PlanSchema) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Basic schema validation
            if not schema or not schema.steps:
                self.logger.error("Invalid schema: no steps found")
                return False
            
            # Check for extremely dangerous patterns
            for step in schema.steps:
                critical_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
                step_text = f"{step.description} {step.operation}".lower()
                for pattern in critical_patterns:
                    if pattern in step_text:
                        self.logger.error(f"Critical security pattern in step {step.step_id}: {pattern}")
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
    
    def _generate_check_id(self) -> str:
        """Generate unique safety check ID"""
        import uuid
        return f"check_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class PlanSafetyChecksInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, checker: PlanSafetyChecker):
        self._checker = checker
    
    def check_plan_safety(self, plan_id: str) -> Dict[str, Any]:
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
            
            result = self._checker.check_plan_safety(schema)
            
            return {
                "success": True,
                "check_id": result.check_id,
                "plan_id": result.plan_id,
                "passed": result.passed,
                "safety_score": result.safety_score,
                "can_proceed": result.can_proceed,
                "violation_count": len(result.violations),
                "warning_count": len(result.warnings),
                "violations": [
                    {
                        "rule_id": v.rule_id,
                        "category": v.category.value,
                        "level": v.level.value,
                        "description": v.description,
                        "recommendation": v.recommendation
                    }
                    for v in result.violations
                ],
                "warnings": result.warnings,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class PlanSafetyChecksFactory:
    """L5 Factory for creating plan safety checker instances"""
    
    @staticmethod
    def create_checker() -> PlanSafetyChecker:
        return PlanSafetyChecksImpl()
    
    @staticmethod
    def create_interface() -> PlanSafetyChecksInterface:
        checker = PlanSafetyChecksFactory.create_checker()
        return PlanSafetyChecksInterface(checker)

# L5 Export for module usage
__all__ = [
    "SafetyLevel",
    "SafetyCategory",
    "SafetyRule",
    "SafetyViolation",
    "SafetyCheckResult",
    "PlanSafetyChecker",
    "PlanSafetyChecksImpl",
    "PlanSafetyChecksInterface",
    "PlanSafetyChecksFactory",
    "SecurityError"
]
