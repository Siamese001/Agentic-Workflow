"""Schema Planning Orchestrator - Main orchestration logic.

This module contains the core orchestrator class that coordinates
schema validation, transformation, and compatibility checking.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

    SchemaPlanningConfig,
    SchemaPlanningResult,
    TransformationPlan,
    TransformationType
)

logger = logging.getLogger(__name__)

class SchemaPlanningOrchestrator:
    """Orchestrator for planning schema operations."""

    def __init__(self, config: Optional[SchemaPlanningConfig] = None):
        self.config = config or SchemaPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, schema_request: Dict[str, Any]) -> SchemaPlanningResult:
        """Execute the schema planning orchestration."""
        self.logger.info(f"Starting schema planning for: {schema_request.get('operation',
            'unknown')}")

        try:
            self._validate_request(schema_request)

            validated_schemas = []
            if self.config.enable_validation:
                validated_schemas = self._validate_schemas(schema_request)

            transformation_plans = []
            if self.config.enable_transformation:
                transformation_plans = self._plan_transformations(schema_request, validated_schemas)

            compatibility_report = {}
            if self.config.enable_compatibility_check:
                compatibility_report = self._check_compatibility(validated_schemas)

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

            self.logger.info(f"Successfully planned schemas: {len(validated_schemas)} validated,
                {len(transformation_plans)} transformations")
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

    def _plan_transformations(self,
        request: Dict[str,
        Any],
        schemas: List[SchemaDefinition]) -> List[TransformationPlan]:
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

        if len(schemas) > 1:
            for i, schema1 in enumerate(schemas):
                for schema2 in schemas[i+1:]:
                    if schema1.schema_type != schema2.schema_type:
                        report["warnings"].append(
                            f"Schema type mismatch: {schema1.name} ({schema1.schema_type}) vs {schem
    a2.name} ({schema2.schema_type})"
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
