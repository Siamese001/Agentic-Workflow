"""Schema Planning API - Factory and convenience functions.

This module provides high-level API functions for creating orchestrators
and executing schema planning operations.
"""

from typing import Dict, List, Optional, Any
from .schema_orchestrator import SchemaPlanningOrchestrator
from .schema_planning_models import SchemaPlanningConfig

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

def plan_schema_operations(
    operation: str,
    schemas: List[Dict[str, Any]],
    transformations: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan schema operations from simple parameters."""
    request = {
        "operation": operation,
        "schemas": schemas,
        "transformations": transformations or []
    }
    
    orchestrator_config = SchemaPlanningConfig(**config) if config else None
    orchestrator = SchemaPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
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
