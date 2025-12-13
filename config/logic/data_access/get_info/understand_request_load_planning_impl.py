"""Implementation for understand_request_load_planning."""

from typing import Any, Dict, List, Optional
from .understand_request_load_planning_types import *

class ConfigLoadPlanner:
    """Planner for configuration loading operations."""

    def __init__(self, config: Optional[ConfigLoadConfig]=None):
        self.config = config or ConfigLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> ConfigLoadResult:
        """Plan configuration loading operations.

        Args:
            load_request: Dictionary containing configuration loading requirements

        Returns:
            ConfigLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting config load planning for: {load_request.get('plan_name', 'unknown')}")
        try:
            self._validate_request(load_request)
            config_type = self._parse_config_type(load_request)
            scope = self._parse_scope(load_request)
            sections = self._parse_sections(load_request)
            validation_rules = self._parse_validation_rules(load_request) if self.config.enable_validation else []
            validation_level = self._parse_validation_level(load_request)
            load_plan = self._create_load_plan(load_request, config_type, scope, sections, validation_rules, validation_level)
            parameter_count = sum((len(section.parameters) for section in sections))
            section_count = len(sections)
            validation_rule_count = len(validation_rules)
            load_time = self._estimate_load_time(load_plan)
            memory_estimate = self._estimate_memory_usage(load_plan)
            result = ConfigLoadResult(success=True, load_plan=load_plan, parameter_count=parameter_count, section_count=section_count, validation_rule_count=validation_rule_count, load_time_estimate=load_time, memory_estimate=memory_estimate, metadata={'planned_at': datetime.utcnow().isoformat(), 'plan_name': load_request.get('plan_name'), 'config_type': config_type.value, 'scope': scope.value, 'planner': 'ConfigLoadPlanner'})
            self.logger.info(f'Successfully planned config load: {parameter_count} parameters in {section_count} sections')
            return result
        except Exception as e:
            self.logger.error(f'Config load planning failed: {str(e)}')
            return ConfigLoadResult(success=False, errors=[str(e)], metadata={'failed_at': datetime.utcnow().isoformat(), 'planner': 'ConfigLoadPlanner'})

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate config load planning request."""
        if not request:
            raise ValueError('Config load planning request cannot be empty')
        if 'plan_name' not in request:
            raise ValueError('Plan name is required in config load planning request')
        if 'config_type' not in request:
            raise ValueError('Config type is required in config load planning request')

    def _parse_config_type(self, request: Dict[str, Any]) -> ConfigType:
        """Parse config type from request."""
        type_mapping = {'system_config': ConfigType.SYSTEM_CONFIG, 'app_config': ConfigType.APP_CONFIG, 'user_config': ConfigType.USER_CONFIG, 'env_config': ConfigType.ENV_CONFIG, 'feature_flags': ConfigType.FEATURE_FLAGS, 'security_config': ConfigType.SECURITY_CONFIG}
        config_type_str = request.get('config_type', 'app_config')
        return type_mapping.get(config_type_str, ConfigType.APP_CONFIG)

    def _parse_scope(self, request: Dict[str, Any]) -> ConfigScope:
        """Parse scope from request."""
        scope_mapping = {'global': ConfigScope.GLOBAL, 'organization': ConfigScope.ORGANIZATION, 'project': ConfigScope.PROJECT, 'service': ConfigScope.SERVICE, 'module': ConfigScope.MODULE, 'user': ConfigScope.USER}
        scope_str = request.get('scope', 'project')
        return scope_mapping.get(scope_str, ConfigScope.PROJECT)

    def _parse_validation_level(self, request: Dict[str, Any]) -> ValidationLevel:
        """Parse validation level from request."""
        level_mapping = {'none': ValidationLevel.NONE, 'basic': ValidationLevel.BASIC, 'strict': ValidationLevel.STRICT, 'comprehensive': ValidationLevel.COMPREHENSIVE}
        level_str = request.get('validation_level', self.config.default_validation_level)
        return level_mapping.get(level_str, ValidationLevel.BASIC)

    def _parse_sections(self, request: Dict[str, Any]) -> List[ConfigSection]:
        """Parse sections from request."""
        sections = []
        raw_sections = request.get('sections', [])
        for raw_section in raw_sections:
            if isinstance(raw_section, dict):
                parameters = []
                raw_params = raw_section.get('parameters', [])
                for raw_param in raw_params:
                    if isinstance(raw_param, dict):
                        param = ConfigParameter(key=raw_param.get('key', 'unnamed'), value=raw_param.get('value'), type=raw_param.get('type', 'string'), required=raw_param.get('required', False), default_value=raw_param.get('default_value'), description=raw_param.get('description', ''), validation_rules=raw_param.get('validation_rules', []), metadata=raw_param.get('metadata', {}))
                        parameters.append(param)
                subsections = self._parse_subsections(raw_section.get('subsections', []))
                section = ConfigSection(name=raw_section.get('name', 'unnamed'), parameters=parameters, subsections=subsections, metadata=raw_section.get('metadata', {}))
                sections.append(section)
        total_params = sum((len(s.parameters) for s in sections))
        if total_params > self.config.max_parameters_per_config:
            raise ValueError(f'Number of parameters ({total_params}) exceeds maximum ({self.config.max_parameters_per_config})')
        return sections

    def _parse_subsections(self, raw_subsections: List[Dict[str, Any]]) -> List[ConfigSection]:
        """Parse subsections recursively."""
        subsections = []
        for raw_sub in raw_subsections:
            if isinstance(raw_sub, dict):
                parameters = []
                raw_params = raw_sub.get('parameters', [])
                for raw_param in raw_params:
                    if isinstance(raw_param, dict):
                        param = ConfigParameter(key=raw_param.get('key', 'unnamed'), value=raw_param.get('value'), type=raw_param.get('type', 'string'), required=raw_param.get('required', False), default_value=raw_param.get('default_value'), description=raw_param.get('description', ''), validation_rules=raw_param.get('validation_rules', []), metadata=raw_param.get('metadata', {}))
                        parameters.append(param)
                nested_subsections = self._parse_subsections(raw_sub.get('subsections', []))
                subsection = ConfigSection(name=raw_sub.get('name', 'unnamed'), parameters=parameters, subsections=nested_subsections, metadata=raw_sub.get('metadata', {}))
                subsections.append(subsection)
        return subsections

    def _parse_validation_rules(self, request: Dict[str, Any]) -> List[ValidationRule]:
        """Parse validation rules from request."""
        rules = []
        raw_rules = request.get('validation_rules', [])
        for raw_rule in raw_rules:
            if isinstance(raw_rule, dict):
                rule = ValidationRule(name=raw_rule.get('name', 'unnamed'), type=raw_rule.get('type', 'condition'), condition=raw_rule.get('condition', ''), error_message=raw_rule.get('error_message', ''), severity=raw_rule.get('severity', 'error'), metadata=raw_rule.get('metadata', {}))
                rules.append(rule)
        return rules

    def _create_load_plan(self, request: Dict[str, Any], config_type: ConfigType, scope: ConfigScope, sections: List[ConfigSection], validation_rules: List[ValidationRule], validation_level: ValidationLevel) -> ConfigLoadPlan:
        """Create config load plan from parsed components."""
        return ConfigLoadPlan(id=request.get('plan_id', f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"), name=request.get('plan_name', 'unnamed_plan'), config_type=config_type, scope=scope, sections=sections, validation_rules=validation_rules, validation_level=validation_level, enable_caching=request.get('enable_caching', True), cache_ttl=request.get('cache_ttl', 600), metadata=request.get('metadata', {}))

    def _estimate_load_time(self, plan: ConfigLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 3
        param_count = sum((len(section.parameters) for section in plan.sections))
        param_time = param_count * 0.01
        validation_time = len(plan.validation_rules) * 0.05
        level_multiplier = {ValidationLevel.NONE: 0.5, ValidationLevel.BASIC: 1.0, ValidationLevel.STRICT: 1.5, ValidationLevel.COMPREHENSIVE: 2.0}
        total_time = (base_time + param_time + validation_time) * level_multiplier.get(plan.validation_level, 1.0)
        return int(total_time)

    def _estimate_memory_usage(self, plan: ConfigLoadPlan) -> int:
        """Estimate memory usage in MB."""
        base_memory = 10
        param_count = sum((len(section.parameters) for section in plan.sections))
        param_memory = param_count * 512
        rule_memory = len(plan.validation_rules) * 256
        level_multiplier = {ValidationLevel.NONE: 0.5, ValidationLevel.BASIC: 1.0, ValidationLevel.STRICT: 1.5, ValidationLevel.COMPREHENSIVE: 2.0}
        total_memory_bytes = (base_memory * 1024 * 1024 + param_memory + rule_memory) * level_multiplier.get(plan.validation_level, 1.0)
        return total_memory_bytes // (1024 * 1024)

def create_config_load_planner(enable_validation: bool=True, enable_type_checking: bool=True, enable_default_values: bool=True, **kwargs: object) -> ConfigLoadPlanner:
    """Create a configured config load planner."""
    config = ConfigLoadConfig(enable_validation=enable_validation, enable_type_checking=enable_type_checking, enable_default_values=enable_default_values, **kwargs)
    return ConfigLoadPlanner(config)

def plan_config_load(plan_name: str, config_type: str, scope: str='project', sections: Optional[List[Dict[str, Any]]]=None, validation_rules: Optional[List[Dict[str, Any]]]=None, validation_level: str='basic', config: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    """Plan config load from simple parameters.

    Args:
        plan_name: Name of the load plan
        config_type: Type of configuration
        scope: Scope of the configuration
        sections: Optional list of configuration sections
        validation_rules: Optional list of validation rules
        validation_level: Level of validation to apply
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    request = {'plan_name': plan_name, 'config_type': config_type, 'scope': scope, 'sections': sections or [], 'validation_rules': validation_rules or [], 'validation_level': validation_level}
    planner_config = ConfigLoadConfig(**config) if config else None
    planner = ConfigLoadPlanner(planner_config)
    result = planner.plan_load(request)

    def serialize_section(section: ConfigSection) -> Dict[str, Any]:
        """Serialize a ConfigSection to a dictionary for JSON output."""
        return {'name': section.name, 'parameters': [{'key': p.key, 'value': p.value, 'type': p.type, 'required': p.required, 'default_value': p.default_value, 'description': p.description, 'validation_rules': p.validation_rules, 'metadata': p.metadata} for p in section.parameters], 'subsections': [serialize_section(sub) for sub in section.subsections], 'metadata': section.metadata}
    return {'success': result.success, 'load_plan': {'id': result.load_plan.id, 'name': result.load_plan.name, 'config_type': result.load_plan.config_type.value, 'scope': result.load_plan.scope.value, 'sections': [serialize_section(section) for section in result.load_plan.sections], 'validation_rules': [{'name': r.name, 'type': r.type, 'condition': r.condition, 'error_message': r.error_message, 'severity': r.severity, 'metadata': r.metadata} for r in result.load_plan.validation_rules], 'validation_level': result.load_plan.validation_level.value, 'enable_caching': result.load_plan.enable_caching, 'cache_ttl': result.load_plan.cache_ttl, 'metadata': result.load_plan.metadata} if result.load_plan else None, 'parameter_count': result.parameter_count, 'section_count': result.section_count, 'validation_rule_count': result.validation_rule_count, 'load_time_estimate': result.load_time_estimate, 'memory_estimate': result.memory_estimate, 'warnings': result.warnings, 'errors': result.errors, 'metadata': result.metadata}
