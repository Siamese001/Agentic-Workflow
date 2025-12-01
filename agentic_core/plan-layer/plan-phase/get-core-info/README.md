# L1 Cognitive Planning - Get Core Info Phase

**Comprehensive layer information gathering and processing system with L5 safety and fail-closed architecture**

## Overview

The Get Core Info phase implements a complete L1 Cognitive Planning system for gathering, analyzing, and validating layer information. This phase orchestrates three subsystems in a cohesive workflow:

1. **General (Understand Request)**: Parse registry intent, extract layer parameters, build core queries
2. **Specific (Analyze/Validate Layer)**: Analyze requirements, extract dependencies, generate layer IDs, map interfaces, validate compatibility and specifications
3. **Utility (Prepare/Validate Information)**: Format registry context, prepare core payloads, validate all aspects of the layer

## Architecture

```
get-core-info/
├── general/understand-request/          # Request understanding subsystem
│   ├── build_core_query.py             # Core query building
│   ├── extract_layer_parameters.py     # Parameter extraction
│   ├── parse_registry_intent.py        # Intent parsing
│   └── __init__.py                      # Module exports
├── specific/                            # Layer analysis subsystem
│   ├── analyze_layer_requirements.py   # Requirements analysis
│   ├── extract_layer_dependencies.py   # Dependency extraction
│   ├── generate_layer_id.py            # Layer ID generation
│   ├── map_layer_interfaces.py         # Interface mapping
│   ├── validate_layer_compatibility.py # Compatibility validation
│   ├── validate_layer_spec.py          # Specification validation
│   └── __init__.py                      # Module exports
├── utility/                             # Information processing subsystem
│   ├── prepare-information/             # Information preparation
│   │   ├── format_registry_context.py  # Context formatting
│   │   ├── prepare_core_payload.py     # Payload preparation
│   │   ├── prepare_information_orchestrator.py  # Preparation orchestration
│   │   ├── prepare_information_registry.py     # Dynamic preparer registry
│   │   ├── prepare_information_metrics.py      # Metrics collection
│   │   ├── integration_tests.py        # Integration tests
│   │   └── __init__.py                  # Module exports
│   ├── validate-information/            # Information validation
│   │   ├── validate_layer_*.py         # 9 comprehensive validators
│   │   ├── validation_orchestrator.py  # Validation orchestration
│   │   ├── validation_registry.py      # Dynamic validator registry
│   │   ├── validation_metrics.py       # Metrics collection
│   │   ├── integration_tests.py        # Integration tests
│   │   └── __init__.py                  # Module exports
│   └── __init__.py                      # Utility exports
├── get_core_info_orchestrator.py        # Top-level orchestrator
├── integration_tests.py                 # End-to-end integration tests
├── __init__.py                          # Complete module exports
└── README.md                            # This documentation
```

## Key Features

### 🏗️ **Comprehensive Architecture**
- **3 Subsystems**: General, Specific, Utility with 17 total components
- **Top-level Orchestrator**: Coordinates all subsystems with workflow management
- **Dynamic Registries**: Component discovery and registration for extensibility
- **Metrics Collection**: Production monitoring and health tracking

### 🔒 **L5 Safety Implementation**
- **Fail-Closed Architecture**: System defaults to safe state on failure
- **Input Sanitization**: Comprehensive validation of all inputs
- **Safety Policies**: Configurable safety constraints and limits
- **Error Handling**: Graceful degradation and fallback mechanisms

### 📊 **Phase Completion Tracking**
- **Phase Status Monitoring**: Real-time tracking of phase execution
- **Component-Level Validation**: Granular completion status tracking
- **Phase 2 Keys Validation**: `phase_2_keys = TRUE` when all phases complete successfully
- **Rollback Capabilities**: Ability to rollback to previous phases on failure

### 🚀 **Execution Modes**
- **Full Workflow**: Execute all phases sequentially (general → specific → utility)
- **Individual Phases**: Execute specific phases only
- **Custom Selection**: Execute selected phases in custom order
- **Parallel/Sequential**: Flexible execution strategies

## Quick Start

### Basic Usage

```python
from agentic_core.plan_layer.plan_phase.get_core_info import (
    GetCoreInfoOrchestrator,
    GetCoreInfoRequest,
    ExecutionMode,
    create_get_core_info_orchestrator
)

# Create orchestrator with all subsystems
orchestrator = create_get_core_info_orchestrator(
    # General subsystem components
    core_query_builder=create_core_query_builder(),
    layer_parameter_extractor=create_layer_parameter_extractor(),
    registry_intent_parser=create_registry_intent_parser(),
    
    # Specific subsystem components
    layer_requirements_analyzer=create_layer_requirements_analyzer(),
    layer_dependency_extractor=create_layer_dependency_extractor(),
    layer_id_generator=create_layer_id_generator(),
    layer_interface_mapper=create_layer_interface_mapper(),
    layer_compatibility_validator=create_layer_compatibility_validator(),
    layer_spec_validator=create_layer_spec_validator(),
    
    # Utility subsystem components
    prepare_information_orchestrator=create_prepare_information_orchestrator(...),
    layer_validation_orchestrator=create_validation_orchestrator(...)
)

# Execute full workflow
request = GetCoreInfoRequest(
    layer_name="my_layer",
    layer_spec={
        "name": "my_layer",
        "version": "1.0.0",
        "type": "service",
        # ... complete layer specification
    },
    execution_mode=ExecutionMode.FULL_WORKFLOW,
    context={"environment": "production"}
)

response = await orchestrator.orchestrate_get_core_info(request)

# Check phase completion
if response.phase_2_keys:
    print("✅ All phases completed successfully!")
    print(f"Overall score: {response.overall_score}")
else:
    print("❌ Some phases failed")
    print(f"Failed phases: {[r.phase_name for r in response.phase_results if not r.is_successful]}")
```

### Individual Phase Execution

```python
# Execute only validation phase
validation_request = GetCoreInfoRequest(
    layer_name="my_layer",
    layer_spec=layer_spec,
    execution_mode=ExecutionMode.UTILITY_ONLY,
    context={"validation_only": True}
)

validation_response = await orchestrator.orchestrate_get_core_info(validation_request)
```

## Phase 2 Keys Validation

The system implements a comprehensive phase completion tracking mechanism that validates when all phases have completed successfully.

### Phase Completion Criteria

**General Phase Requirements:**
- ✅ Core Query Builder completed successfully
- ✅ Layer Parameter Extractor completed successfully  
- ✅ Registry Intent Parser completed successfully

**Specific Phase Requirements:**
- ✅ Layer Requirements Analyzer completed successfully
- ✅ Layer Dependency Extractor completed successfully
- ✅ Layer ID Generator completed successfully
- ✅ Layer Interface Mapper completed successfully
- ✅ Layer Compatibility Validator completed successfully
- ✅ Layer Spec Validator completed successfully

**Utility Phase Requirements:**
- ✅ Prepare Information Orchestrator completed successfully
- ✅ Layer Validation Orchestrator completed successfully

### Phase 2 Keys Status

```python
# Check phase completion status
completion_status = response.phase_completion_status
# Returns: {"general": True, "specific": True, "utility": True}

# Check phase 2 keys
phase_2_keys = response.phase_2_keys
# Returns: True when all phases complete successfully
```

## Subsystem Details

### General Subsystem (Understand Request)

The general subsystem handles request understanding and parsing:

```python
from agentic_core.plan_layer.plan_phase.get_core_info.general import (
    CoreQueryBuilder,
    LayerParameterExtractor,
    RegistryIntentParser
)

# Build core queries
query_builder = create_core_query_builder()
core_query = await query_builder.build_core_query(query_request)

# Extract layer parameters
param_extractor = create_layer_parameter_extractor()
parameters = await param_extractor.extract_parameters(param_request)

# Parse registry intent
intent_parser = create_registry_intent_parser()
intent = await intent_parser.parse_registry_intent(intent_request)
```

### Specific Subsystem (Layer Analysis)

The specific subsystem performs detailed layer analysis:

```python
from agentic_core.plan_layer.plan_phase.get_core_info.specific import (
    LayerRequirementsAnalyzer,
    LayerDependencyExtractor,
    LayerIdGenerator,
    LayerInterfaceMapper,
    LayerCompatibilityValidator,
    LayerSpecValidator
)

# Analyze requirements
requirements_analyzer = create_layer_requirements_analyzer()
requirements = await requirements_analyzer.analyze_requirements(req_request)

# Extract dependencies
dependency_extractor = create_layer_dependency_extractor()
dependencies = await dependency_extractor.extract_dependencies(dep_request)

# Generate layer ID
id_generator = create_layer_id_generator()
layer_id = await id_generator.generate_layer_id(id_request)

# Map interfaces
interface_mapper = create_layer_interface_mapper()
interfaces = await interface_mapper.map_interfaces(interface_request)

# Validate compatibility
compatibility_validator = create_layer_compatibility_validator()
compatibility = await compatibility_validator.validate_compatibility(comp_request)

# Validate specification
spec_validator = create_layer_spec_validator()
spec_validation = await spec_validator.validate_spec(spec_request)
```

### Utility Subsystem (Information Processing)

The utility subsystem handles information preparation and validation:

#### Prepare Information

```python
from agentic_core.plan_layer.plan_phase.get_core_info.utility.prepare_information import (
    PrepareInformationOrchestrator,
    PreparationType,
    PreparationMode
)

# Create prepare orchestrator
prepare_orchestrator = create_prepare_information_orchestrator(
    context_formatter=create_registry_context_formatter(),
    payload_preparer=create_core_payload_preparer()
)

# Execute preparation
prepare_request = PrepareInformationRequest(
    layer_name="my_layer",
    layer_spec=layer_spec,
    preparation_types=[PreparationType.ALL],
    preparation_mode=PreparationMode.SEQUENTIAL
)

prepare_response = await prepare_orchestrator.orchestrate_preparations(prepare_request)
```

#### Validate Information

```python
from agentic_core.plan_layer.plan_phase.get_core_info.utility.validate_information import (
    LayerValidationOrchestrator,
    ValidationType,
    OrchestrationMode
)

# Create validation orchestrator
validation_orchestrator = create_validation_orchestrator(
    dependencies_validator=create_layer_dependencies_validator(),
    interfaces_validator=create_layer_interfaces_validator(),
    # ... all other validators
)

# Execute validation
validation_request = OrchestratorRequest(
    layer_name="my_layer",
    layer_spec=layer_spec,
    validation_types=[ValidationType.ALL],
    orchestration_mode=OrchestrationMode.PARALLEL_WITH_DEPENDENCIES
)

validation_response = await validation_orchestrator.orchestrate_validations(validation_request)
```

## Configuration and Safety

### Safety Policies

Configure safety policies for each subsystem:

```python
from agentic_core.plan_layer.plan_phase.get_core_info import GetCoreInfoSafetyPolicy

# Create custom safety policy
safety_policy = GetCoreInfoSafetyPolicy(
    max_execution_time_seconds=600,
    require_phase_validation=True,
    enable_timeout_protection=True,
    fail_closed=True
)

# Apply to orchestrator
orchestrator = create_get_core_info_orchestrator(
    # ... components
    safety_policy=safety_policy
)
```

### Metrics Collection

Enable comprehensive metrics collection:

```python
from agentic_core.plan_layer.plan_phase.get_core_info.utility.validate_information import (
    create_prometheus_metrics_collector,
    get_global_metrics_collector
)

# Configure Prometheus metrics
prometheus_collector = create_prometheus_metrics_collector(
    prefix="get_core_info_system"
)

# Set as global collector
set_global_metrics_collector(prometheus_collector)

# Monitor health
health_monitor = get_global_health_monitor()
health_status = await health_monitor.get_health_status()
```

## Error Handling and Rollback

### Comprehensive Error Handling

```python
try:
    response = await orchestrator.orchestrate_get_core_info(request)
except SafetyError as e:
    print(f"Safety policy violation: {e}")
except GetCoreInfoOrchestrationError as e:
    print(f"Orchestration error: {e}")
```

### Rollback Functionality

```python
# Enable rollback in request
request = GetCoreInfoRequest(
    layer_name="my_layer",
    layer_spec=layer_spec,
    execution_mode=ExecutionMode.FULL_WORKFLOW,
    enable_rollback=True
)

response = await orchestrator.orchestrate_get_core_info(request)

# Access rollback data if needed
if response.rollback_data:
    general_data = response.rollback_data.get("general", {})
    specific_data = response.rollback_data.get("specific", {})
    utility_data = response.rollback_data.get("utility", {})
```

## Testing

### Running Integration Tests

```bash
# Run all integration tests
python -m pytest integration_tests.py -v

# Run specific test categories
python -m pytest integration_tests.py::TestGetCoreInfoOrchestrator -v
python -m pytest integration_tests.py::TestPhase2KeysValidation -v
python -m pytest integration_tests.py::TestEndToEndWorkflow -v
```

### Verification Script

```python
# Quick verification that phase_2_keys = TRUE works
from agentic_core.plan_layer.plan_phase.get_core_info.integration_tests import (
    verify_phase_2_keys_implementation
)

# Verify implementation
success = await verify_phase_2_keys_implementation()
if success:
    print("✅ phase_2_keys = TRUE implementation verified!")
```

## Performance Optimization

### Parallel Execution

```python
# Use parallel execution for better performance
request = GetCoreInfoRequest(
    layer_name="my_layer",
    layer_spec=layer_spec,
    execution_mode=ExecutionMode.FULL_WORKFLOW,
    execution_options={
        "parallel_execution": True,
        "max_concurrent_components": 4
    }
)
```

### Caching

```python
# Enable component caching for better performance
from agentic_core.plan_layer.plan_phase.get_core_info.utility.validate_information import (
    get_validation_registry
)

registry = get_validation_registry()
await registry.clear_cache()  # Clear existing cache
# Components will be cached automatically on first use
```

## Production Deployment

### Environment Configuration

```python
# Production configuration
production_config = {
    "safety_level": "high",
    "timeout_seconds": 300,
    "enable_metrics": True,
    "enable_health_monitoring": True,
    "fail_closed": True
}

request = GetCoreInfoRequest(
    layer_name="production_layer",
    layer_spec=layer_spec,
    execution_mode=ExecutionMode.FULL_WORKFLOW,
    context={"production": True, **production_config}
)
```

### Monitoring and Health Checks

```python
# Monitor system health
health_monitor = get_global_health_monitor()
health_status = await health_monitor.get_health_status()

if not health_status.healthy:
    print(f"System unhealthy: {health_status.status_message}")
    print(f"Recent success rate: {health_status.recent_success_rate}%")
    print(f"Error rate: {health_status.error_rate}%")
```

## Troubleshooting

### Common Issues

1. **phase_2_keys = FALSE**
   - Check that all required components completed successfully
   - Verify layer specification contains all required fields
   - Check component-specific error messages

2. **Timeout Errors**
   - Increase timeout_seconds in request
   - Check system resource utilization
   - Consider using parallel execution mode

3. **Safety Policy Violations**
   - Review safety policy configuration
   - Check input validation requirements
   - Verify execution mode is allowed

### Debug Information

```python
# Enable detailed logging
import logging
logging.getLogger("agentic_core.plan_layer.plan_phase.get_core_info").setLevel(logging.DEBUG)

# Check detailed phase results
for result in response.phase_results:
    print(f"Phase: {result.phase_name}")
    print(f"Status: {result.status}")
    print(f"Score: {result.score}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
```

## Contributing

### Adding New Components

1. Create component class implementing appropriate interface
2. Add factory function for component creation
3. Register component in relevant registry
4. Update phase completion criteria if needed
5. Add integration tests

### Example: Adding New Validator

```python
# 1. Create validator class
class CustomValidator(LayerValidatorInterface):
    async def validate_layer(self, request):
        # Implementation
        pass

# 2. Add factory function
def create_custom_validator():
    return CustomValidator()

# 3. Register in validation registry
from agentic_core.plan_layer.plan_phase.get_core_info.utility.validate_information import (
    register_custom_validator
)

await register_custom_validator(
    validator_type=ValidationType.CUSTOM,
    validator_class=CustomValidator,
    factory_function=create_custom_validator
)
```

## API Reference

### Core Classes

- **GetCoreInfoOrchestrator**: Top-level orchestration
- **GetCoreInfoRequest**: Unified request format
- **GetCoreInfoResponse**: Unified response format
- **ExecutionMode**: Execution mode enumeration
- **PhaseStatus**: Phase status tracking

### Factory Functions

- **create_get_core_info_orchestrator()**: Create orchestrator instance
- **create_core_query_builder()**: Create query builder
- **create_layer_parameter_extractor()**: Create parameter extractor
- **create_registry_intent_parser()**: Create intent parser
- **create_layer_requirements_analyzer()**: Create requirements analyzer
- **create_layer_dependency_extractor()**: Create dependency extractor
- **create_layer_id_generator()**: Create layer ID generator
- **create_layer_interface_mapper()**: Create interface mapper
- **create_layer_compatibility_validator()**: Create compatibility validator
- **create_layer_spec_validator()**: Create spec validator
- **create_prepare_information_orchestrator()**: Create preparation orchestrator
- **create_validation_orchestrator()**: Create validation orchestrator

### Safety and Monitoring

- **GetCoreInfoSafetyPolicy**: Safety policy configuration
- **PhaseCompletionChecker**: Phase completion validation
- **MetricsCollectorInterface**: Metrics collection interface
- **HealthMonitor**: System health monitoring

## Version Information

- **Version**: 1.0.0
- **Author**: L1 Cognitive Planning Team
- **Description**: Comprehensive layer information gathering and processing system
- **Phase Completion**: phase_2_keys = TRUE when all subsystems complete successfully

## License

This implementation follows L5 safety principles and fail-closed architecture guidelines. All components are designed for production use with comprehensive error handling, monitoring, and validation capabilities.
