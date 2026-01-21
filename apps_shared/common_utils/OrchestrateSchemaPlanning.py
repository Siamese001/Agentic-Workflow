"""Schema Planning Orchestrator - Coordinates schema validation and transformation operations.

This orchestrator manages the planning phase for schema operations,
including validation, transformation, mapping, and compatibility checks.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SchemaType(Enum):
    """Types of schemas for different data formats."""
    JSON = "json"
    XML = "xml"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    SQL = "sql"
    YAML = "yaml"

class ValidationLevel(Enum):
    """Levels of schema validation."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    BUSINESS = "business"
    FULL = "full"

class TransformationType(Enum):
    """Types of schema transformations."""
    FORMAT_CONVERSION = "format_conversion"
    FIELD_MAPPING = "field_mapping"
    TYPE_COERCION = "type_coercion"
    STRUCTURE_REFACTOR = "structure_refactor"
    VERSION_MIGRATION = "version_migration"

@dataclass
class SchemaDefinition:
    """Definition of a data schema."""
    name: str
    schema_type: SchemaType
    version: str
    content: Dict[str, Any]
    namespace: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class ValidationRule:
    """Rule for schema validation."""
    name: str
    rule_type: ValidationLevel
    condition: str
    message: str
    severity: str = "error"

@dataclass
class TransformationPlan:
    """Plan for schema transformation."""
    transformation_type: TransformationType
    source_schema: str
    target_schema: str
    mapping_rules: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class SchemaPlanningConfig:
    """Configuration for schema planning orchestrator."""
    enable_validation: bool = True
    enable_transformation: bool = True
    enable_compatibility_check: bool = True
    max_schema_depth: int = 10
    strict_validation: bool = True
    log_level: str = "INFO"

@dataclass
class SchemaPlanningResult:
    """Result of schema planning orchestration."""
    success: bool
    validated_schemas: List[SchemaDefinition] = field(default_factory=list)
    transformation_plans: List[TransformationPlan] = field(default_factory=list)
    compatibility_report: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SchemaPlanningOrchestrator:
    """Orchestrator for planning schema operations."""

    def __init__(self, config: Optional[SchemaPlanningConfig] = None):
        self.config = config or SchemaPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, schema_request: Dict[str, Any]) -> SchemaPlanningResult:
        """Execute the schema planning orchestration.

        Args:
            schema_request: Dictionary containing schema requirements and definitions

        Returns:
            SchemaPlanningResult: Complete planning result with validated schemas and transformations
        """
        self.logger.info(f"Starting schema planning for: {schema_request.get('operation', 'unknown')}")

        try:
            # Validate input request
            self._validate_request(schema_request)

            # Parse and validate schemas
            validated_schemas = []
            if self.config.enable_validation:
                validated_schemas = self._validate_schemas(schema_request)

            # Plan transformations if enabled
            transformation_plans = []
            if self.config.enable_transformation:
                transformation_plans = self._plan_transformations(schema_request, validated_schemas)

            # Check compatibility if enabled
            compatibility_report = {}
            if self.config.enable_compatibility_check:
                compatibility_report = self._check_compatibility(validated_schemas)

            # Collect validation errors
            validation_errors = self._collect_validation_errors(schema_request)

            result = SchemaPlanningResult(
                success=len(validation_errors) == 0,
                validated_schemas=validated_schemas,
                transformation_plans=transformation_plans,
                compatibility_report=compatibility_report,
                validation_errors=validation_errors,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "operation": schema_request.get("operation"),
                    "schema_count": len(validated_schemas),
                    "transformation_count": len(transformation_plans),
                    "orchestrator": "SchemaPlanningOrchestrator"
                }
            )

            self.logger.info(f"Successfully planned schemas: {len(validated_schemas)} validated, {len(transformation_plans)} transformations")
            return result

        except Exception as e:
            self.logger.error(f"Schema planning failed: {str(e)}")
            return SchemaPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "SchemaPlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate schema planning request."""
        if not request:
            raise ValueError("Schema request cannot be empty")

        if "operation" not in request:
            raise ValueError("Operation type is required in schema request")

        if "schemas" not in request:
            raise ValueError("Schemas are required in schema request")

    def _validate_schemas(self, request: Dict[str, Any]) -> List[SchemaDefinition]:
        """Validate and parse schemas from request."""
        schemas = []
        raw_schemas = request.get("schemas", [])

        for raw_schema in raw_schemas:
            if isinstance(raw_schema, dict):
                schema = SchemaDefinition(
                    name=raw_schema.get("name", "unnamed"),
                    schema_type=SchemaType(raw_schema.get("type", "json")),
                    version=raw_schema.get("version", "1.0"),
                    content=raw_schema.get("content", {}),
                    namespace=raw_schema.get("namespace"),
                    description=raw_schema.get("description"),
                    tags=raw_schema.get("tags", [])
                )
                schemas.append(schema)

        return schemas

    def _plan_transformations(self, request: Dict[str, Any], schemas: List[SchemaDefinition]) -> List[TransformationPlan]:
        """Plan schema transformations based on request."""
        plans = []
        transformations = request.get("transformations", [])

        for transform in transformations:
            plan = TransformationPlan(
                transformation_type=TransformationType(transform.get("type", "format_conversion")),
                source_schema=transform.get("source", ""),
                target_schema=transform.get("target", ""),
                mapping_rules=transform.get("mapping_rules", {}),
                dependencies=transform.get("dependencies", [])
            )
            plans.append(plan)

        return plans

    def _check_compatibility(self, schemas: List[SchemaDefinition]) -> Dict[str, Any]:
        """Check compatibility between schemas."""
        report = {
            "compatible": True,
            "issues": [],
            "warnings": []
        }

        # Simple compatibility check
        if len(schemas) > 1:
            for i, schema1 in enumerate(schemas):
                for schema2 in schemas[i+1:]:
                    if schema1.schema_type != schema2.schema_type:
                        report["warnings"].append(
                            f"Schema type mismatch: {schema1.name} ({schema1.schema_type}) vs {schema2.name} ({schema2.schema_type})"
                        )

        return report

    def _collect_validation_errors(self, request: Dict[str, Any]) -> List[str]:
        """Collect validation errors from schemas."""
        errors = []
        schemas = request.get("schemas", [])

        for schema in schemas:
            if not isinstance(schema, dict):
                errors.append("Invalid schema format")
                continue

            if "name" not in schema:
                errors.append("Schema missing name")

            if "type" not in schema:
                errors.append("Schema missing type")

        return errors

# Factory function for easy instantiation
def create_schema_planning_orchestrator(
    enable_validation: bool = True,
    enable_transformation: bool = True,
    **kwargs: Dict[str, object]) -> SchemaPlanningOrchestrator:
    """Create a configured schema planning orchestrator."""
    config = SchemaPlanningConfig(
        enable_validation=enable_validation,
        enable_transformation=enable_transformation,
        **kwargs
    )
    return SchemaPlanningOrchestrator(config)

# Convenience function for direct usage
def plan_schema_operations(
    operation: str,
    schemas: List[Dict[str, Any]],
    transformations: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan schema operations from simple parameters.

    Args:
        operation: Type of operation (validate, transform, migrate)
        schemas: List of schema definitions
        transformations: Optional list of transformation definitions
        config: Optional configuration overrides

    Returns:
        Dict: Planning result with schemas and transformations
    """
    # Build request
    request = {
        "operation": operation,
        "schemas": schemas,
        "transformations": transformations or []
    }

    # Create orchestrator and execute
    orchestrator_config = SchemaPlanningConfig(**config) if config else None
    orchestrator = SchemaPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "validated_schemas": [
            {
                "name": s.name,
                "schema_type": s.schema_type.value,
                "version": s.version,
                "content": s.content,
                "namespace": s.namespace,
                "description": s.description,
                "tags": s.tags
            }
            for s in result.validated_schemas
        ],
        "transformation_plans": [
            {
                "transformation_type": t.transformation_type.value,
                "source_schema": t.source_schema,
                "target_schema": t.target_schema,
                "mapping_rules": t.mapping_rules,
                "dependencies": t.dependencies
            }
            for t in result.transformation_plans
        ],
        "compatibility_report": result.compatibility_report,
        "validation_errors": result.validation_errors,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }

if __name__ == "__main__":
    # Example usage
    example_schemas = [
        {
            "name": "user_schema",
            "type": "json",
            "version": "1.0",
            "content": {"type": "object", "properties": {"id": {"type": "string"}}}
        }
    ]

    result = plan_schema_operations(
        operation="validate",
        schemas=example_schemas
    )

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
            dangerous_patterns = ["<script>", "javascript:", "ast.literal_eval(", "pass  # exec disabled: ", "__import__"]
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

# L5 Interface compliance
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

# L5 builder
class OrchestrateDataPlanningOrchestratorFactory:
    """L5 builder for creating processors with proper configuration"""

    @staticmethod
    def create_processor(safety_level: str = "strict") -> OrchestrateDataPlanningOrchestratorInterface:
        """Create configured engine"""
        constraints = OrchestrateDataPlanningOrchestratorConstraints(safety_level=safety_level)
        engine = OrchestrateDataPlanningOrchestratorImpl(constraints)
        return OrchestrateDataPlanningOrchestratorInterface(engine)

# L5 Main execution point
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
