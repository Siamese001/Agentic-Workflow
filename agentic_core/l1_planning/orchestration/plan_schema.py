"""
L5 Agentic Core - L1 Planning Layer - Plan Schema
Implements L1 Cognitive Planning Layer for plan schema validation and management
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PlanComplexity(Enum):
    """L5 Plan complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"

@dataclass
class PlanConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_steps: int = 50
    max_depth: int = 5
    max_duration_hours: float = 24.0
    allowed_operations: List[str] = field(default_factory=lambda: ["plan", "validate", "execute"])
    safety_level: str = "strict"
    requires_approval: bool = True

@dataclass
class PlanStep:
    """L5 Plan step structure with full type safety"""
    step_id: str
    step_number: int
    description: str
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    status: PlanStatus = PlanStatus.DRAFT
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class PlanSchema:
    """L5 Plan schema structure with full type safety"""
    plan_id: str
    name: str
    description: str
    complexity: PlanComplexity
    steps: List[PlanStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: PlanConstraints = field(default_factory=PlanConstraints)
    status: PlanStatus = PlanStatus.DRAFT
    safety_validated: bool = False
    created_at: str = ""
    updated_at: str = ""

@dataclass
class ValidationResult:
    """L5 Validation result structure"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

class PlanSchemaProcessor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def create_plan_schema(self, plan_data: Dict[str, Any]) -> PlanSchema:
        """Create a plan schema with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_schema(self, schema: PlanSchema) -> ValidationResult:
        """Validate plan schema with L5 safety"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class PlanSchemaImpl(PlanSchemaProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure plan schema management with no side effects
    """
    
    def __init__(self, constraints: Optional[PlanConstraints] = None):
        self.constraints = constraints or PlanConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schemas: Dict[str, PlanSchema] = {}
    
    def create_plan_schema(self, plan_data: Dict[str, Any]) -> PlanSchema:
        """Create a plan schema following L5 architecture principles"""
        self.logger.info(f"Creating plan schema: {plan_data}")
        
        # L5 Input validation
        self._validate_input(plan_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(plan_data):
            raise SecurityError("Plan data failed L5 safety validation")
        
        # Create plan steps
        steps = []
        step_data_list = plan_data.get("steps", [])
        
        for i, step_data in enumerate(step_data_list):
            step = PlanStep(
                step_id=step_data.get("step_id", f"step_{i+1}"),
                step_number=i + 1,
                description=step_data.get("description", ""),
                operation=step_data.get("operation", "execute"),
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", []),
                estimated_duration=step_data.get("estimated_duration", 0.0),
                status=PlanStatus(step_data.get("status", "draft")),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
            steps.append(step)
        
        # Create plan schema with L5 structure
        schema = PlanSchema(
            plan_id=plan_data.get("plan_id", self._generate_plan_id()),
            name=plan_data.get("name", ""),
            description=plan_data.get("description", ""),
            complexity=PlanComplexity(plan_data.get("complexity", "moderate")),
            steps=steps,
            metadata=plan_data.get("metadata", {}),
            constraints=PlanConstraints(**plan_data.get("constraints", {})),
            status=PlanStatus(plan_data.get("status", "draft")),
            safety_validated=False,
            created_at=self._get_timestamp(),
            updated_at=self._get_timestamp()
        )
        
        # Validate the schema
        validation_result = self.validate_schema(schema)
        if not validation_result.valid:
            raise ValueError(f"Invalid plan schema: {validation_result.errors}")
        
        schema.safety_validated = validation_result.safety_validated
        
        # Store schema
        self.schemas[schema.plan_id] = schema
        
        self.logger.info(f"Successfully created plan schema: {schema.plan_id}")
        return schema
    
    def validate_schema(self, schema: PlanSchema) -> ValidationResult:
        """Validate plan schema following L5 principles"""
        self.logger.info(f"Validating plan schema: {schema.plan_id}")
        
        errors = []
        warnings = []
        
        # Basic validation
        if not schema.name:
            errors.append("Plan name is required")
        
        if not schema.description:
            errors.append("Plan description is required")
        
        if not schema.steps:
            errors.append("Plan must have at least one step")
        
        # Step validation
        step_numbers = set()
        for step in schema.steps:
            if step.step_number in step_numbers:
                errors.append(f"Duplicate step number: {step.step_number}")
            step_numbers.add(step.step_number)
            
            if not step.description:
                errors.append(f"Step {step.step_number} description is required")
            
            if step.estimated_duration < 0:
                errors.append(f"Step {step.step_number} duration cannot be negative")
        
        # Constraint validation
        if len(schema.steps) > schema.constraints.max_steps:
            errors.append(f"Plan exceeds maximum steps: {len(schema.steps)} > {schema.constraints.max_steps}")
        
        total_duration = sum(step.estimated_duration for step in schema.steps)
        if total_duration > schema.constraints.max_duration_hours:
            errors.append(f"Plan exceeds maximum duration: {total_duration} > {schema.constraints.max_duration_hours}")
        
        # Dependency validation
        all_step_ids = {step.step_id for step in schema.steps}
        for step in schema.steps:
            for dep in step.dependencies:
                if dep not in all_step_ids:
                    errors.append(f"Step {step.step_id} depends on non-existent step: {dep}")
        
        # Safety validation
        safety_validated = self._validate_schema_safety(schema)
        if not safety_validated:
            errors.append("Schema failed safety validation")
        
        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            safety_validated=safety_validated,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Schema validation completed: {len(errors)} errors, {len(warnings)} warnings")
        return result
    
    def get_schema(self, plan_id: str) -> Optional[PlanSchema]:
        """Retrieve a plan schema by ID"""
        return self.schemas.get(plan_id)
    
    def list_schemas(self) -> List[PlanSchema]:
        """List all plan schemas"""
        return list(self.schemas.values())
    
    def update_schema(self, plan_id: str, updates: Dict[str, Any]) -> PlanSchema:
        """Update an existing plan schema"""
        if plan_id not in self.schemas:
            raise ValueError(f"Plan schema not found: {plan_id}")
        
        schema = self.schemas[plan_id]
        
        # Apply updates
        if "name" in updates:
            schema.name = updates["name"]
        if "description" in updates:
            schema.description = updates["description"]
        if "status" in updates:
            schema.status = PlanStatus(updates["status"])
        
        schema.updated_at = self._get_timestamp()
        
        # Re-validate
        validation_result = self.validate_schema(schema)
        if not validation_result.valid:
            raise ValueError(f"Invalid updated schema: {validation_result.errors}")
        
        self.logger.info(f"Updated plan schema: {plan_id}")
        return schema
    
    def validate_safety(self, plan_data: Dict[str, Any]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_str = str(plan_data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check data size
            if len(str(plan_data)) > 1000000:  # 1MB limit
                self.logger.error("Plan data exceeds size limit")
                return False
            
            # Validate required fields
            if "name" not in plan_data or not plan_data["name"]:
                self.logger.error("Plan name is required")
                return False
            
            self.logger.info("Plan data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_schema_safety(self, schema: PlanSchema) -> bool:
        """Validate schema-specific safety rules"""
        try:
            # Check for suspicious operations
            suspicious_ops = ["exec", "eval", "import", "open", "file"]
            for step in schema.steps:
                if step.operation.lower() in suspicious_ops:
                    self.logger.warning(f"Suspicious operation in step {step.step_id}: {step.operation}")
                    return False
            
            # Check for too many dependencies (potential circular dependency)
            for step in schema.steps:
                if len(step.dependencies) > 10:
                    self.logger.warning(f"Step {step.step_id} has too many dependencies: {len(step.dependencies)}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Schema safety validation error: {e}")
            return False
    
    def _validate_input(self, plan_data: Dict[str, Any]) -> None:
        """L5 Input validation"""
        if not isinstance(plan_data, dict):
            raise ValueError("Plan data must be a dictionary")
        
        if not plan_data:
            raise ValueError("Plan data cannot be empty")
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID"""
        import uuid
        return f"plan_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class PlanSchemaInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, processor: PlanSchemaProcessor):
        self._processor = processor
    
    def create_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            schema = self._processor.create_plan_schema(plan_data)
            return {
                "success": True,
                "plan_id": schema.plan_id,
                "name": schema.name,
                "complexity": schema.complexity.value,
                "step_count": len(schema.steps),
                "safety_validated": schema.safety_validated,
                "created_at": schema.created_at
            }
        except Exception as e:
            self.logger.error(f"Plan creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def validate_plan(self, plan_id: str) -> Dict[str, Any]:
        """L5 Interface method - validates plan safely"""
        try:
            schema = self._processor.get_schema(plan_id)
            if not schema:
                return {
                    "success": False,
                    "error": "Plan not found",
                    "safety_validated": False
                }
            
            result = self._processor.validate_schema(schema)
            return {
                "success": result.valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Plan validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class PlanSchemaFactory:
    """L5 Factory for creating plan schema instances"""
    
    @staticmethod
    def create_processor(constraints: Optional[PlanConstraints] = None) -> PlanSchemaProcessor:
        return PlanSchemaImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[PlanConstraints] = None) -> PlanSchemaInterface:
        processor = PlanSchemaFactory.create_processor(constraints)
        return PlanSchemaInterface(processor)

# L5 Export for module usage
__all__ = [
    "PlanStatus",
    "PlanComplexity",
    "PlanConstraints",
    "PlanStep",
    "PlanSchema",
    "ValidationResult",
    "PlanSchemaProcessor",
    "PlanSchemaImpl",
    "PlanSchemaInterface",
    "PlanSchemaFactory",
    "SecurityError"
]
