"""Schema Planning Orchestrator - Backward compatibility shim.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).
"""

# Re-export all types for backward compatibility
    SchemaType,
    ValidationLevel,
    TransformationType,
    SchemaDefinition,
    ValidationRule
)

    TransformationPlan,
    SchemaPlanningConfig,
    SchemaPlanningResult
)


    create_schema_planning_orchestrator,
    plan_schema_operations
)

    OrchestrateDataPlanningOrchestratorImpl,
    SecurityError,
    OrchestrateDataPlanningOrchestratorInterface,
    OrchestrateDataPlanningOrchestratorFactory,
    orchestrate_data_planning
)

__all__ = [
    'SchemaType',
    'ValidationLevel',
    'TransformationType',
    'SchemaDefinition',
    'ValidationRule',
    'TransformationPlan',
    'SchemaPlanningConfig',
    'SchemaPlanningResult',
    'SchemaPlanningOrchestrator',
    'create_schema_planning_orchestrator',
    'plan_schema_operations',
    'OrchestrateDataPlanningOrchestratorImpl',
    'SecurityError',
    'OrchestrateDataPlanningOrchestratorInterface',
    'OrchestrateDataPlanningOrchestratorFactory',
    'orchestrate_data_planning'
]
