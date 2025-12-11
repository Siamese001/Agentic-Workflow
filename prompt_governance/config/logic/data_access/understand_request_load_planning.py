"""Prompt Governance Config Request Understanding Load Planner - Plans configuration loading for prompt governance.

This planner manages the loading phase for understanding prompt governance configuration requests,
including policy parsing, rule validation, and constraint extraction.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Types of prompt governance configurations."""
    POLICY = "policy"
    RULE = "rule"
    CONSTRAINT = "constraint"
    TEMPLATE = "template"
    VALIDATION = "validation"
    GUARDRAIL = "guardrail"


class ConfigScope(Enum):
    """Scopes for configuration."""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    TEAM = "team"
    USER = "user"
    PROMPT = "prompt"


class ValidationLevel(Enum):
    """Validation levels for configurations."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
    DISABLED = "disabled"


@dataclass
class PolicyDefinition:
    """Definition of a policy configuration."""
    name: str
    version: str
    description: str
    rules: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    scope: ConfigScope = ConfigScope.GLOBAL
    enabled: bool = True
    priority: int = 0


@dataclass
class RuleDefinition:
    """Definition of a rule configuration."""
    id: str
    name: str
    type: str
    condition: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    category: str = "general"


@dataclass
class ConstraintDefinition:
    """Definition of a constraint configuration."""
    name: str
    field: str
    operator: str
    value: Any
    message: Optional[str] = None
    validation_level: ValidationLevel = ValidationLevel.MODERATE


@dataclass
class TemplateDefinition:
    """Definition of a template configuration."""
    id: str
    name: str
    template_type: str
    content: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceLoadPlan:
    """Complete plan for governance configuration loading."""
    id: str
    name: str
    config_type: ConfigType
    scope: ConfigScope
    policies: List[PolicyDefinition] = field(default_factory=list)
    rules: List[RuleDefinition] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    templates: List[TemplateDefinition] = field(default_factory=list)
    validation_level: ValidationLevel = ValidationLevel.MODERATE
    enable_caching: bool = True
    cache_ttl: int = 600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceLoadConfig:
    """Configuration for governance load planning."""
    enable_policies: bool = True
    enable_rules: bool = True
    enable_constraints: bool = True
    enable_templates: bool = True
    max_configs_per_plan: int = 100
    default_validation_level: str = "moderate"
    log_level: str = "INFO"


@dataclass
class GovernanceLoadResult:
    """Result of governance load planning."""
    success: bool
    load_plan: Optional[GovernanceLoadPlan] = None
    config_count: int = 0
    rule_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class GovernanceLoadPlanner:
    """Planner for governance configuration loading operations."""

    def __init__(self, config: Optional[GovernanceLoadConfig] = None):
        self.config = config or GovernanceLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> GovernanceLoadResult:
        """Plan governance configuration loading operations.
        
        Args:
            load_request: Dictionary containing load requirements and configurations
            
        Returns:
            GovernanceLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting governance load planning for: {load_request.get('plan_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(load_request)
            
            # Parse config type
            config_type = self._parse_config_type(load_request)
            
            # Parse scope
            scope = self._parse_scope(load_request)
            
            # Parse policies if enabled
            policies = (
                self._parse_policies(load_request) 
                if self.config.enable_policies else []
            )
            
            # Parse rules if enabled
            rules = (
                self._parse_rules(load_request) 
                if self.config.enable_rules else []
            )
            
            # Parse constraints if enabled
            constraints = (
                self._parse_constraints(load_request) 
                if self.config.enable_constraints else []
            )
            
            # Parse templates if enabled
            templates = (
                self._parse_templates(load_request) 
                if self.config.enable_templates else []
            )
            
            # Parse validation level
            validation_level = self._parse_validation_level(load_request)
            
            # Create load plan
            load_plan = self._create_load_plan(
                load_request, config_type, scope,
                policies, rules, constraints, templates, validation_level
            )
            
            # Count configurations
            config_count = len(policies) + len(rules) + len(constraints) + len(templates)
            rule_count = sum(len(p.rules) for p in policies) + len(rules)
            
            # Estimate load time
            load_time = self._estimate_load_time(load_plan)
            
            # Estimate memory usage
            memory_estimate = self._estimate_memory_usage(load_plan)
            
            result = GovernanceLoadResult(
                success=True,
                load_plan=load_plan,
                config_count=config_count,
                rule_count=rule_count,
                load_time_estimate=load_time,
                memory_estimate=memory_estimate,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "config_type": config_type.value,
                    "scope": scope.value,
                    "planner": "GovernanceLoadPlanner"
                }
            )
            
            self.logger.info(
                f"Successfully planned governance load: "
                f"{config_count} configurations, {rule_count} rules"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Governance load planning failed: {str(e)}")
            return GovernanceLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "GovernanceLoadPlanner"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate governance load planning request."""
        if not request:
            raise ValueError("Governance load planning request cannot be empty")
        
        if "plan_name" not in request:
            raise ValueError("Plan name is required in governance load planning request")
        
        if "config_type" not in request:
            raise ValueError("Config type is required in governance load planning request")

    def _parse_config_type(self, request: Dict[str, Any]) -> ConfigType:
        """Parse config type from request."""
        type_mapping = {
            "policy": ConfigType.POLICY,
            "rule": ConfigType.RULE,
            "constraint": ConfigType.CONSTRAINT,
            "template": ConfigType.TEMPLATE,
            "validation": ConfigType.VALIDATION,
            "guardrail": ConfigType.GUARDRAIL
        }
        
        config_type_str = request.get("config_type", "policy")
        return type_mapping.get(config_type_str, ConfigType.POLICY)

    def _parse_scope(self, request: Dict[str, Any]) -> ConfigScope:
        """Parse scope from request."""
        scope_mapping = {
            "global": ConfigScope.GLOBAL,
            "organization": ConfigScope.ORGANIZATION,
            "project": ConfigScope.PROJECT,
            "team": ConfigScope.TEAM,
            "user": ConfigScope.USER,
            "prompt": ConfigScope.PROMPT
        }
        
        scope_str = request.get("scope", "global")
        return scope_mapping.get(scope_str, ConfigScope.GLOBAL)

    def _parse_validation_level(self, request: Dict[str, Any]) -> ValidationLevel:
        """Parse validation level from request."""
        level_mapping = {
            "strict": ValidationLevel.STRICT,
            "moderate": ValidationLevel.MODERATE,
            "lenient": ValidationLevel.LENIENT,
            "disabled": ValidationLevel.DISABLED
        }
        
        level_str = request.get("validation_level", self.config.default_validation_level)
        return level_mapping.get(level_str, ValidationLevel.MODERATE)

    def _parse_policies(self, request: Dict[str, Any]) -> List[PolicyDefinition]:
        """Parse policies from request."""
        policies = []
        raw_policies = request.get("policies", [])
        
        for raw_policy in raw_policies:
            if isinstance(raw_policy, dict):
                # Parse scope if present
                scope = ConfigScope.GLOBAL
                if "scope" in raw_policy:
                    scope_mapping = {
                        "global": ConfigScope.GLOBAL,
                        "organization": ConfigScope.ORGANIZATION,
                        "project": ConfigScope.PROJECT,
                        "team": ConfigScope.TEAM,
                        "user": ConfigScope.USER,
                        "prompt": ConfigScope.PROMPT
                    }
                    scope = scope_mapping.get(
                        raw_policy.get("scope"),
                        ConfigScope.GLOBAL
                    )
                
                policy = PolicyDefinition(
                    name=raw_policy.get("name", "unnamed"),
                    version=raw_policy.get("version", "1.0"),
                    description=raw_policy.get("description", ""),
                    rules=raw_policy.get("rules", []),
                    constraints=raw_policy.get("constraints", {}),
                    scope=scope,
                    enabled=raw_policy.get("enabled", True),
                    priority=raw_policy.get("priority", 0)
                )
                policies.append(policy)
        
        # Validate policy count
        if len(policies) > self.config.max_configs_per_plan:
            raise ValueError(
                f"Number of policies ({len(policies)}) exceeds maximum "
                f"({self.config.max_configs_per_plan})"
            )
        
        return policies

    def _parse_rules(self, request: Dict[str, Any]) -> List[RuleDefinition]:
        """Parse rules from request."""
        rules = []
        raw_rules = request.get("rules", [])
        
        for raw_rule in raw_rules:
            if isinstance(raw_rule, dict):
                rule = RuleDefinition(
                    id=raw_rule.get("id", "unnamed"),
                    name=raw_rule.get("name", "unnamed"),
                    type=raw_rule.get("type", "validation"),
                    condition=raw_rule.get("condition", ""),
                    action=raw_rule.get("action", "warn"),
                    parameters=raw_rule.get("parameters", {}),
                    severity=raw_rule.get("severity", "medium"),
                    category=raw_rule.get("category", "general")
                )
                rules.append(rule)
        
        # Validate rule count
        if len(rules) > self.config.max_configs_per_plan:
            raise ValueError(
                f"Number of rules ({len(rules)}) exceeds maximum "
                f"({self.config.max_configs_per_plan})"
            )
        
        return rules

    def _parse_constraints(self, request: Dict[str, Any]) -> List[ConstraintDefinition]:
        """Parse constraints from request."""
        constraints = []
        raw_constraints = request.get("constraints", [])
        
        for raw_constraint in raw_constraints:
            if isinstance(raw_constraint, dict):
                # Parse validation level if present
                validation_level = ValidationLevel.MODERATE
                if "validation_level" in raw_constraint:
                    level_mapping = {
                        "strict": ValidationLevel.STRICT,
                        "moderate": ValidationLevel.MODERATE,
                        "lenient": ValidationLevel.LENIENT,
                        "disabled": ValidationLevel.DISABLED
                    }
                    validation_level = level_mapping.get(
                        raw_constraint.get("validation_level"),
                        ValidationLevel.MODERATE
                    )
                
                constraint = ConstraintDefinition(
                    name=raw_constraint.get("name", "unnamed"),
                    field=raw_constraint.get("field", ""),
                    operator=raw_constraint.get("operator", "equals"),
                    value=raw_constraint.get("value"),
                    message=raw_constraint.get("message"),
                    validation_level=validation_level
                )
                constraints.append(constraint)
        
        # Validate constraint count
        if len(constraints) > self.config.max_configs_per_plan:
            raise ValueError(
                f"Number of constraints ({len(constraints)}) exceeds maximum "
                f"({self.config.max_configs_per_plan})"
            )
        
        return constraints

    def _parse_templates(self, request: Dict[str, Any]) -> List[TemplateDefinition]:
        """Parse templates from request."""
        templates = []
        raw_templates = request.get("templates", [])
        
        for raw_template in raw_templates:
            if isinstance(raw_template, dict):
                template = TemplateDefinition(
                    id=raw_template.get("id", "unnamed"),
                    name=raw_template.get("name", "unnamed"),
                    template_type=raw_template.get("template_type", "prompt"),
                    content=raw_template.get("content", ""),
                    variables=raw_template.get("variables", []),
                    metadata=raw_template.get("metadata", {})
                )
                templates.append(template)
        
        # Validate template count
        if len(templates) > self.config.max_configs_per_plan:
            raise ValueError(
                f"Number of templates ({len(templates)}) exceeds maximum "
                f"({self.config.max_configs_per_plan})"
            )
        
        return templates

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        config_type: ConfigType,
        scope: ConfigScope,
        policies: List[PolicyDefinition],
        rules: List[RuleDefinition],
        constraints: List[ConstraintDefinition],
        templates: List[TemplateDefinition],
        validation_level: ValidationLevel
    ) -> GovernanceLoadPlan:
        """Create governance load plan from parsed components."""
        return GovernanceLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            config_type=config_type,
            scope=scope,
            policies=policies,
            rules=rules,
            constraints=constraints,
            templates=templates,
            validation_level=validation_level,
            enable_caching=request.get("enable_caching", True),
            cache_ttl=request.get("cache_ttl", 600),
            metadata=request.get("metadata", {})
        )

    def _estimate_load_time(self, plan: GovernanceLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 10  # Base setup time
        
        # Add time per configuration
        config_time = (
            len(plan.policies) * 0.5 +
            len(plan.rules) * 0.2 +
            len(plan.constraints) * 0.1 +
            len(plan.templates) * 0.3
        )
        
        # Add validation time
        validation_multiplier = {
            ValidationLevel.STRICT: 2.0,
            ValidationLevel.MODERATE: 1.0,
            ValidationLevel.LENIENT: 0.5,
            ValidationLevel.DISABLED: 0.1
        }
        
        validation_time = config_time * validation_multiplier.get(
            plan.validation_level, 1.0
        )
        
        total_time = base_time + config_time + validation_time
        
        return int(total_time)

    def _estimate_memory_usage(self, plan: GovernanceLoadPlan) -> int:
        """Estimate memory usage in MB."""
        # Base memory usage
        base_memory = 20  # 20MB base
        
        # Memory for configurations (assume 1KB per config)
        config_memory = (
            len(plan.policies) * 1024 +
            len(plan.rules) * 512 +
            len(plan.constraints) * 256 +
            len(plan.templates) * 2048
        )
        
        # Memory for validation based on level
        validation_multiplier = {
            ValidationLevel.STRICT: 3.0,
            ValidationLevel.MODERATE: 2.0,
            ValidationLevel.LENIENT: 1.5,
            ValidationLevel.DISABLED: 1.0
        }
        
        total_memory_bytes = (
            base_memory * 1024 * 1024 + 
            config_memory * validation_multiplier.get(plan.validation_level, 2.0)
        )
        
        return total_memory_bytes // (1024 * 1024)  # Convert to MB


# Factory function for easy instantiation
def create_governance_load_planner(
    enable_policies: bool = True,
    enable_rules: bool = True,
    enable_constraints: bool = True,
    enable_templates: bool = True,
    **kwargs
) -> GovernanceLoadPlanner:
    """Create a configured governance load planner."""
    config = GovernanceLoadConfig(
        enable_policies=enable_policies,
        enable_rules=enable_rules,
        enable_constraints=enable_constraints,
        enable_templates=enable_templates,
        **kwargs
    )
    return GovernanceLoadPlanner(config)


# Convenience function for direct usage
def plan_governance_load(
    plan_name: str,
    config_type: str,
    scope: str = "global",
    policies: Optional[List[Dict[str, Any]]] = None,
    rules: Optional[List[Dict[str, Any]]] = None,
    constraints: Optional[List[Dict[str, Any]]] = None,
    templates: Optional[List[Dict[str, Any]]] = None,
    validation_level: str = "moderate",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan governance configuration load from simple parameters.
    
    Args:
        plan_name: Name of the load plan
        config_type: Type of governance configuration
        scope: Scope of the configuration
        policies: Optional list of policy definitions
        rules: Optional list of rule definitions
        constraints: Optional list of constraint definitions
        templates: Optional list of template definitions
        validation_level: Level of validation to apply
        config: Optional planner configuration overrides
        
    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "config_type": config_type,
        "scope": scope,
        "policies": policies or [],
        "rules": rules or [],
        "constraints": constraints or [],
        "templates": templates or [],
        "validation_level": validation_level
    }
    
    # Create planner and execute
    planner_config = GovernanceLoadConfig(**config) if config else None
    planner = GovernanceLoadPlanner(planner_config)
    result = planner.plan_load(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "config_type": result.load_plan.config_type.value,
            "scope": result.load_plan.scope.value,
            "policies": [
                {
                    "name": p.name,
                    "version": p.version,
                    "description": p.description,
                    "rules": p.rules,
                    "constraints": p.constraints,
                    "scope": p.scope.value,
                    "enabled": p.enabled,
                    "priority": p.priority
                }
                for p in result.load_plan.policies
            ],
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "type": r.type,
                    "condition": r.condition,
                    "action": r.action,
                    "parameters": r.parameters,
                    "severity": r.severity,
                    "category": r.category
                }
                for r in result.load_plan.rules
            ],
            "constraints": [
                {
                    "name": c.name,
                    "field": c.field,
                    "operator": c.operator,
                    "value": c.value,
                    "message": c.message,
                    "validation_level": c.validation_level.value
                }
                for c in result.load_plan.constraints
            ],
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "template_type": t.template_type,
                    "content": t.content,
                    "variables": t.variables,
                    "metadata": t.metadata
                }
                for t in result.load_plan.templates
            ],
            "validation_level": result.load_plan.validation_level.value,
            "enable_caching": result.load_plan.enable_caching,
            "cache_ttl": result.load_plan.cache_ttl,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "config_count": result.config_count,
        "rule_count": result.rule_count,
        "load_time_estimate": result.load_time_estimate,
        "memory_estimate": result.memory_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }