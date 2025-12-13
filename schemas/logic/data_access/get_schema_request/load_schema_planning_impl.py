"""Implementation for load_schema_planning."""

from typing import Any, Dict, List, Optional
from .load_schema_planning_types import *

class SchemaLoadPlanner:
    """Planner for schema loading operations."""

    def __init__(self, config: Optional[SchemaLoadConfig]=None):
        self.config = config or SchemaLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> SchemaLoadResult:
        """Plan schema loading operations.

        Args:
            load_request: Dictionary containing schema requirements

        Returns:
            SchemaLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting schema load planning for: {load_request.get('plan_name', 'unknown')}")
        try:
            self._validate_request(load_request)
            schemas = self._parse_schemas(load_request)
            validation_mode = self._parse_validation_mode(load_request)
            validation_rules = self._parse_validation_rules(load_request) if self.config.enable_validation else []
            transforms = self._parse_transforms(load_request) if self.config.enable_transforms else []
            load_plan = self._create_load_plan(load_request, schemas, validation_mode, validation_rules, transforms)
            schema_count = len(schemas)
            dependency_count = sum((len(s.dependencies) for s in schemas))
            validation_rule_count = len(validation_rules)
            transform_count = len(transforms)
            load_time = self._estimate_load_time(load_plan)
            memory_estimate = self._estimate_memory_usage(load_plan)
            result = SchemaLoadResult(success=True, load_plan=load_plan, schema_count=schema_count, dependency_count=dependency_count, validation_rule_count=validation_rule_count, transform_count=transform_count, load_time_estimate=load_time, memory_estimate=memory_estimate, metadata={'planned_at': datetime.utcnow().isoformat(), 'plan_name': load_request.get('plan_name'), 'planner': 'SchemaLoadPlanner'})
            self.logger.info(f'Successfully planned schema load: {schema_count} schemas, {dependency_count} dependencies')
            return result
        except Exception as e:
            self.logger.error(f'Schema load planning failed: {str(e)}')
            return SchemaLoadResult(success=False, errors=[str(e)], metadata={'failed_at': datetime.utcnow().isoformat(), 'planner': 'SchemaLoadPlanner'})

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate schema load planning request."""
        if not request:
            raise ValueError('Schema load planning request cannot be empty')
        if 'plan_name' not in request:
            raise ValueError('Plan name is required in schema load planning request')
        if 'schemas' not in request:
            raise ValueError('Schemas are required in schema load planning request')

    def _parse_schemas(self, request: Dict[str, Any]) -> List[SchemaDefinition]:
        """Parse schemas from request."""
        schemas = []
        raw_schemas = request.get('schemas', [])
        for raw_schema in raw_schemas:
            if isinstance(raw_schema, dict):
                type_mapping = {'json': SchemaType.JSON, 'xml': SchemaType.XML, 'yaml': SchemaType.YAML, 'protobuf': SchemaType.PROTOBUF, 'avro': SchemaType.AVRO, 'openapi': SchemaType.OPENAPI, 'graphql': SchemaType.GRAPHQL}
                schema_type = type_mapping.get(raw_schema.get('type', 'json'), SchemaType.JSON)
                scope = SchemaScope.DATA
                if 'scope' in raw_schema:
                    scope_mapping = {'request': SchemaScope.REQUEST, 'response': SchemaScope.RESPONSE, 'event': SchemaScope.EVENT, 'config': SchemaScope.CONFIG, 'data': SchemaScope.DATA, 'internal': SchemaScope.INTERNAL}
                    scope = scope_mapping.get(raw_schema.get('scope'), SchemaScope.DATA)
                schema = SchemaDefinition(name=raw_schema.get('name', 'unnamed'), type=schema_type, version=raw_schema.get('version', '1.0'), content=raw_schema.get('content', ''), file_path=raw_schema.get('file_path'), url=raw_schema.get('url'), dependencies=raw_schema.get('dependencies', []), scope=scope)
                schemas.append(schema)
        if len(schemas) > self.config.max_schemas_per_plan:
            raise ValueError(f'Number of schemas ({len(schemas)}) exceeds maximum ({self.config.max_schemas_per_plan})')
        total_deps = sum((len(s.dependencies) for s in schemas))
        if total_deps > self.config.max_dependencies:
            raise ValueError(f'Total dependencies ({total_deps}) exceeds maximum ({self.config.max_dependencies})')
        return schemas

    def _parse_validation_mode(self, request: Dict[str, Any]) -> ValidationMode:
        """Parse validation mode from request."""
        mode_mapping = {'strict': ValidationMode.STRICT, 'lenient': ValidationMode.LENIENT, 'syntax_only': ValidationMode.SYNTAX_ONLY, 'disabled': ValidationMode.DISABLED}
        mode_str = request.get('validation_mode', self.config.default_validation_mode)
        return mode_mapping.get(mode_str, ValidationMode.STRICT)

    def _parse_validation_rules(self, request: Dict[str, Any]) -> List[ValidationRule]:
        """Parse validation rules from request."""
        rules = []
        raw_rules = request.get('validation_rules', [])
        for raw_rule in raw_rules:
            if isinstance(raw_rule, dict):
                rule = ValidationRule(name=raw_rule.get('name', 'unnamed'), type=raw_rule.get('type', 'required'), parameters=raw_rule.get('parameters', {}), severity=raw_rule.get('severity', 'error'), message=raw_rule.get('message'))
                rules.append(rule)
        return rules

    def _parse_transforms(self, request: Dict[str, Any]) -> List[SchemaTransform]:
        """Parse transforms from request."""
        transforms = []
        raw_transforms = request.get('transforms', [])
        type_mapping = {'json': SchemaType.JSON, 'xml': SchemaType.XML, 'yaml': SchemaType.YAML, 'protobuf': SchemaType.PROTOBUF, 'avro': SchemaType.AVRO, 'openapi': SchemaType.OPENAPI, 'graphql': SchemaType.GRAPHQL}
        for raw_transform in raw_transforms:
            if isinstance(raw_transform, dict):
                transform = SchemaTransform(source_type=type_mapping.get(raw_transform.get('source_type', 'json'), SchemaType.JSON), target_type=type_mapping.get(raw_transform.get('target_type', 'json'), SchemaType.JSON), transform_function=raw_transform.get('transform_function', ''), parameters=raw_transform.get('parameters', {}))
                transforms.append(transform)
        return transforms

    def _create_load_plan(self, request: Dict[str, Any], schemas: List[SchemaDefinition], validation_mode: ValidationMode, validation_rules: List[ValidationRule], transforms: List[SchemaTransform]) -> SchemaLoadPlan:
        """Create schema load plan from parsed components."""
        return SchemaLoadPlan(id=request.get('plan_id', f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"), name=request.get('plan_name', 'unnamed_plan'), schemas=schemas, validation_mode=validation_mode, validation_rules=validation_rules, transforms=transforms, resolve_dependencies=request.get('resolve_dependencies', True), enable_caching=request.get('enable_caching', True), cache_ttl=request.get('cache_ttl', 3600), metadata=request.get('metadata', {}))

    def _estimate_load_time(self, plan: SchemaLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 5
        schema_time = len(plan.schemas) * 0.5
        validation_multiplier = {ValidationMode.STRICT: 2.0, ValidationMode.LENIENT: 1.0, ValidationMode.SYNTAX_ONLY: 0.5, ValidationMode.DISABLED: 0.1}
        validation_time = len(plan.validation_rules) * 0.2 * validation_multiplier.get(plan.validation_mode, 1.0)
        transform_time = len(plan.transforms) * 1.0
        dep_time = sum((len(s.dependencies) for s in plan.schemas)) * 0.1 if plan.resolve_dependencies else 0
        total_time = base_time + schema_time + validation_time + transform_time + dep_time
        return int(total_time)

    def _estimate_memory_usage(self, plan: SchemaLoadPlan) -> int:
        """Estimate memory usage in MB."""
        base_memory = 30
        schema_memory = len(plan.schemas) * 10 * 1024
        validation_memory = len(plan.validation_rules) * 1024
        transform_memory = len(plan.transforms) * 5 * 1024
        dep_memory = sum((len(s.dependencies) for s in plan.schemas)) * 512 if plan.resolve_dependencies else 0
        total_memory_bytes = base_memory * 1024 * 1024 + schema_memory + validation_memory + transform_memory + dep_memory
        return total_memory_bytes // (1024 * 1024)

def create_schema_load_planner(enable_validation: bool=True, enable_transforms: bool=True, **kwargs: Dict[str, object]) -> SchemaLoadPlanner:
    """Create a configured schema load planner."""
    config = SchemaLoadConfig(enable_validation=enable_validation, enable_transforms=enable_transforms, **kwargs)
    return SchemaLoadPlanner(config)

def plan_schema_load(plan_name: str, schemas: List[Dict[str, Any]], validation_mode: str='strict', validation_rules: Optional[List[Dict[str, Any]]]=None, transforms: Optional[List[Dict[str, Any]]]=None, resolve_dependencies: bool=True, config: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    """Plan schema load from simple parameters.

    Args:
        plan_name: Name of the load plan
        schemas: List of schema definitions
        validation_mode: Mode of validation to apply
        validation_rules: Optional list of validation rules
        transforms: Optional list of schema transforms
        resolve_dependencies: Whether to resolve schema dependencies
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    request = {'plan_name': plan_name, 'schemas': schemas, 'validation_mode': validation_mode, 'validation_rules': validation_rules or [], 'transforms': transforms or [], 'resolve_dependencies': resolve_dependencies}
    planner_config = SchemaLoadConfig(**config) if config else None
    planner = SchemaLoadPlanner(planner_config)
    result = planner.plan_load(request)
    return {'success': result.success, 'load_plan': {'id': result.load_plan.id, 'name': result.load_plan.name, 'schemas': [{'name': s.name, 'type': s.type.value, 'version': s.version, 'file_path': s.file_path, 'url': s.url, 'dependencies': s.dependencies, 'scope': s.scope.value} for s in result.load_plan.schemas], 'validation_mode': result.load_plan.validation_mode.value, 'validation_rules': [{'name': r.name, 'type': r.type, 'parameters': r.parameters, 'severity': r.severity, 'message': r.message} for r in result.load_plan.validation_rules], 'transforms': [{'source_type': t.source_type.value, 'target_type': t.target_type.value, 'transform_function': t.transform_function, 'parameters': t.parameters} for t in result.load_plan.transforms], 'resolve_dependencies': result.load_plan.resolve_dependencies, 'enable_caching': result.load_plan.enable_caching, 'cache_ttl': result.load_plan.cache_ttl, 'metadata': result.load_plan.metadata} if result.load_plan else None, 'schema_count': result.schema_count, 'dependency_count': result.dependency_count, 'validation_rule_count': result.validation_rule_count, 'transform_count': result.transform_count, 'load_time_estimate': result.load_time_estimate, 'memory_estimate': result.memory_estimate, 'warnings': result.warnings, 'errors': result.errors, 'metadata': result.metadata}
