"""Prompt Governance Config Info Understanding Load Planner - Plans information loading for prompt governance.

This planner manages the loading phase for understanding prompt governance information requests,
including policy analysis, rule extraction, and constraint interpretation.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class InfoType(Enum):
    """Types of information to load."""
    POLICY_INFO = "policy_info"
    RULE_INFO = "rule_info"
    CONSTRAINT_INFO = "constraint_info"
    TEMPLATE_INFO = "template_info"
    VALIDATION_INFO = "validation_info"
    GOVERNANCE_INFO = "governance_info"


class InfoScope(Enum):
    """Scopes for information loading."""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    TEAM = "team"
    USER = "user"
    PROMPT = "prompt"


class ProcessingMode(Enum):
    """Processing modes for information."""
    STRICT = "strict"
    MODERATE = "moderate"
    FAST = "fast"
    DETAILED = "detailed"


@dataclass
class PolicyInfo:
    """Information about a policy."""
    id: str
    name: str
    description: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    scope: InfoScope = InfoScope.GLOBAL
    version: str = "1.0"


@dataclass
class RuleInfo:
    """Information about a rule."""
    id: str
    name: str
    type: str
    description: str
    logic: str
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintInfo:
    """Information about a constraint."""
    id: str
    name: str
    field: str
    condition: str
    rationale: str
    impact: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateInfo:
    """Information about a template."""
    id: str
    name: str
    type: str
    structure: Dict[str, Any]
    guidelines: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceInfoLoadPlan:
    """Complete plan for governance information loading."""
    id: str
    name: str
    info_type: InfoType
    scope: InfoScope
    policies: List[PolicyInfo] = field(default_factory=list)
    rules: List[RuleInfo] = field(default_factory=list)
    constraints: List[ConstraintInfo] = field(default_factory=list)
    templates: List[TemplateInfo] = field(default_factory=list)
    processing_mode: ProcessingMode = ProcessingMode.MODERATE
    enable_caching: bool = True
    cache_ttl: int = 600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceInfoLoadConfig:
    """Configuration for governance info load planning."""
    enable_policies: bool = True
    enable_rules: bool = True
    enable_constraints: bool = True
    enable_templates: bool = True
    max_info_per_plan: int = 100
    default_processing_mode: str = "moderate"
    log_level: str = "INFO"


@dataclass
class GovernanceInfoLoadResult:
    """Result of governance info load planning."""
    success: bool
    load_plan: Optional[GovernanceInfoLoadPlan] = None
    info_count: int = 0
    policy_count: int = 0
    rule_count: int = 0
    constraint_count: int = 0
    template_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class GovernanceInfoLoadPlanner:
    """Planner for governance information loading operations."""

    def __init__(self, config: Optional[GovernanceInfoLoadConfig] = None):
        self.config = config or GovernanceInfoLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> GovernanceInfoLoadResult:
        """Plan governance information loading operations.
        
        Args:
            load_request: Dictionary containing information loading requirements
            
        Returns:
            GovernanceInfoLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting governance info load planning for: {load_request.get('plan_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(load_request)
            
            # Parse info type
            info_type = self._parse_info_type(load_request)
            
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
            
            # Parse processing mode
            processing_mode = self._parse_processing_mode(load_request)
            
            # Create load plan
            load_plan = self._create_load_plan(
                load_request, info_type, scope,
                policies, rules, constraints, templates, processing_mode
            )
            
            # Count items
            info_count = len(policies) + len(rules) + len(constraints) + len(templates)
            policy_count = len(policies)
            rule_count = len(rules)
            constraint_count = len(constraints)
            template_count = len(templates)
            
            # Estimate load time
            load_time = self._estimate_load_time(load_plan)
            
            # Estimate memory usage
            memory_estimate = self._estimate_memory_usage(load_plan)
            
            result = GovernanceInfoLoadResult(
                success=True,
                load_plan=load_plan,
                info_count=info_count,
                policy_count=policy_count,
                rule_count=rule_count,
                constraint_count=constraint_count,
                template_count=template_count,
                load_time_estimate=load_time,
                memory_estimate=memory_estimate,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "info_type": info_type.value,
                    "scope": scope.value,
                    "planner": "GovernanceInfoLoadPlanner"
                }
            )
            
            self.logger.info(
                f"Successfully planned governance info load: "
                f"{info_count} information items"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Governance info load planning failed: {str(e)}")
            return GovernanceInfoLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "GovernanceInfoLoadPlanner"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate governance info load planning request."""
        if not request:
            raise ValueError("Governance info load planning request cannot be empty")
        
        if "plan_name" not in request:
            raise ValueError("Plan name is required in governance info load planning request")
        
        if "info_type" not in request:
            raise ValueError("Info type is required in governance info load planning request")

    def _parse_info_type(self, request: Dict[str, Any]) -> InfoType:
        """Parse info type from request."""
        type_mapping = {
            "policy_info": InfoType.POLICY_INFO,
            "rule_info": InfoType.RULE_INFO,
            "constraint_info": InfoType.CONSTRAINT_INFO,
            "template_info": InfoType.TEMPLATE_INFO,
            "validation_info": InfoType.VALIDATION_INFO,
            "governance_info": InfoType.GOVERNANCE_INFO
        }
        
        info_type_str = request.get("info_type", "policy_info")
        return type_mapping.get(info_type_str, InfoType.POLICY_INFO)

    def _parse_scope(self, request: Dict[str, Any]) -> InfoScope:
        """Parse scope from request."""
        scope_mapping = {
            "global": InfoScope.GLOBAL,
            "organization": InfoScope.ORGANIZATION,
            "project": InfoScope.PROJECT,
            "team": InfoScope.TEAM,
            "user": InfoScope.USER,
            "prompt": InfoScope.PROMPT
        }
        
        scope_str = request.get("scope", "global")
        return scope_mapping.get(scope_str, InfoScope.GLOBAL)

    def _parse_processing_mode(self, request: Dict[str, Any]) -> ProcessingMode:
        """Parse processing mode from request."""
        mode_mapping = {
            "strict": ProcessingMode.STRICT,
            "moderate": ProcessingMode.MODERATE,
            "fast": ProcessingMode.FAST,
            "detailed": ProcessingMode.DETAILED
        }
        
        mode_str = request.get("processing_mode", self.config.default_processing_mode)
        return mode_mapping.get(mode_str, ProcessingMode.MODERATE)

    def _parse_policies(self, request: Dict[str, Any]) -> List[PolicyInfo]:
        """Parse policies from request."""
        policies = []
        raw_policies = request.get("policies", [])
        
        for raw_policy in raw_policies:
            if isinstance(raw_policy, dict):
                # Parse scope if present
                scope = InfoScope.GLOBAL
                if "scope" in raw_policy:
                    scope_mapping = {
                        "global": InfoScope.GLOBAL,
                        "organization": InfoScope.ORGANIZATION,
                        "project": InfoScope.PROJECT,
                        "team": InfoScope.TEAM,
                        "user": InfoScope.USER,
                        "prompt": InfoScope.PROMPT
                    }
                    scope = scope_mapping.get(
                        raw_policy.get("scope"),
                        InfoScope.GLOBAL
                    )
                
                policy = PolicyInfo(
                    id=raw_policy.get("id", "unnamed"),
                    name=raw_policy.get("name", "unnamed"),
                    description=raw_policy.get("description", ""),
                    content=raw_policy.get("content", ""),
                    metadata=raw_policy.get("metadata", {}),
                    scope=scope,
                    version=raw_policy.get("version", "1.0")
                )
                policies.append(policy)
        
        # Validate policy count
        if len(policies) > self.config.max_info_per_plan:
            raise ValueError(
                f"Number of policies ({len(policies)}) exceeds maximum "
                f"({self.config.max_info_per_plan})"
            )
        
        return policies

    def _parse_rules(self, request: Dict[str, Any]) -> List[RuleInfo]:
        """Parse rules from request."""
        rules = []
        raw_rules = request.get("rules", [])
        
        for raw_rule in raw_rules:
            if isinstance(raw_rule, dict):
                rule = RuleInfo(
                    id=raw_rule.get("id", "unnamed"),
                    name=raw_rule.get("name", "unnamed"),
                    type=raw_rule.get("type", "validation"),
                    description=raw_rule.get("description", ""),
                    logic=raw_rule.get("logic", ""),
                    examples=raw_rule.get("examples", []),
                    metadata=raw_rule.get("metadata", {})
                )
                rules.append(rule)
        
        # Validate rule count
        if len(rules) > self.config.max_info_per_plan:
            raise ValueError(
                f"Number of rules ({len(rules)}) exceeds maximum "
                f"({self.config.max_info_per_plan})"
            )
        
        return rules

    def _parse_constraints(self, request: Dict[str, Any]) -> List[ConstraintInfo]:
        """Parse constraints from request."""
        constraints = []
        raw_constraints = request.get("constraints", [])
        
        for raw_constraint in raw_constraints:
            if isinstance(raw_constraint, dict):
                constraint = ConstraintInfo(
                    id=raw_constraint.get("id", "unnamed"),
                    name=raw_constraint.get("name", "unnamed"),
                    field=raw_constraint.get("field", ""),
                    condition=raw_constraint.get("condition", ""),
                    rationale=raw_constraint.get("rationale", ""),
                    impact=raw_constraint.get("impact", ""),
                    metadata=raw_constraint.get("metadata", {})
                )
                constraints.append(constraint)
        
        # Validate constraint count
        if len(constraints) > self.config.max_info_per_plan:
            raise ValueError(
                f"Number of constraints ({len(constraints)}) exceeds maximum "
                f"({self.config.max_info_per_plan})"
            )
        
        return constraints

    def _parse_templates(self, request: Dict[str, Any]) -> List[TemplateInfo]:
        """Parse templates from request."""
        templates = []
        raw_templates = request.get("templates", [])
        
        for raw_template in raw_templates:
            if isinstance(raw_template, dict):
                template = TemplateInfo(
                    id=raw_template.get("id", "unnamed"),
                    name=raw_template.get("name", "unnamed"),
                    type=raw_template.get("type", "prompt"),
                    structure=raw_template.get("structure", {}),
                    guidelines=raw_template.get("guidelines", []),
                    metadata=raw_template.get("metadata", {})
                )
                templates.append(template)
        
        # Validate template count
        if len(templates) > self.config.max_info_per_plan:
            raise ValueError(
                f"Number of templates ({len(templates)}) exceeds maximum "
                f"({self.config.max_info_per_plan})"
            )
        
        return templates

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        info_type: InfoType,
        scope: InfoScope,
        policies: List[PolicyInfo],
        rules: List[RuleInfo],
        constraints: List[ConstraintInfo],
        templates: List[TemplateInfo],
        processing_mode: ProcessingMode
    ) -> GovernanceInfoLoadPlan:
        """Create governance info load plan from parsed components."""
        return GovernanceInfoLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            info_type=info_type,
            scope=scope,
            policies=policies,
            rules=rules,
            constraints=constraints,
            templates=templates,
            processing_mode=processing_mode,
            enable_caching=request.get("enable_caching", True),
            cache_ttl=request.get("cache_ttl", 600),
            metadata=request.get("metadata", {})
        )

    def _estimate_load_time(self, plan: GovernanceInfoLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 5  # Base setup time
        
        # Time per info item
        info_time = (
            len(plan.policies) * 0.5 +
            len(plan.rules) * 0.3 +
            len(plan.constraints) * 0.2 +
            len(plan.templates) * 0.4
        )
        
        # Processing mode multiplier
        mode_multiplier = {
            ProcessingMode.STRICT: 2.0,
            ProcessingMode.MODERATE: 1.0,
            ProcessingMode.FAST: 0.5,
            ProcessingMode.DETAILED: 3.0
        }
        
        processing_time = info_time * mode_multiplier.get(
            plan.processing_mode, 1.0
        )
        
        total_time = base_time + processing_time
        
        return int(total_time)

    def _estimate_memory_usage(self, plan: GovernanceInfoLoadPlan) -> int:
        """Estimate memory usage in MB."""
        # Base memory usage
        base_memory = 20  # 20MB base
        
        # Memory for info items (assume average 2KB per item)
        info_memory = (
            len(plan.policies) * 2048 +
            len(plan.rules) * 1024 +
            len(plan.constraints) * 512 +
            len(plan.templates) * 1536
        )
        
        # Processing mode memory multiplier
        mode_multiplier = {
            ProcessingMode.STRICT: 2.0,
            ProcessingMode.MODERATE: 1.0,
            ProcessingMode.FAST: 0.5,
            ProcessingMode.DETAILED: 3.0
        }
        
        total_memory_bytes = (
            base_memory * 1024 * 1024 + 
            info_memory * mode_multiplier.get(plan.processing_mode, 1.0)
        )
        
        return total_memory_bytes // (1024 * 1024)  # Convert to MB


# Factory function for easy instantiation
def create_governance_info_load_planner(
    enable_policies: bool = True,
    enable_rules: bool = True,
    enable_constraints: bool = True,
    enable_templates: bool = True,
    **kwargs
) -> GovernanceInfoLoadPlanner:
    """Create a configured governance info load planner."""
    config = GovernanceInfoLoadConfig(
        enable_policies=enable_policies,
        enable_rules=enable_rules,
        enable_constraints=enable_constraints,
        enable_templates=enable_templates,
        **kwargs
    )
    return GovernanceInfoLoadPlanner(config)


# Convenience function for direct usage
def plan_governance_info_load(
    plan_name: str,
    info_type: str,
    scope: str = "global",
    policies: Optional[List[Dict[str, Any]]] = None,
    rules: Optional[List[Dict[str, Any]]] = None,
    constraints: Optional[List[Dict[str, Any]]] = None,
    templates: Optional[List[Dict[str, Any]]] = None,
    processing_mode: str = "moderate",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan governance information load from simple parameters.
    
    Args:
        plan_name: Name of the load plan
        info_type: Type of governance information
        scope: Scope of the information
        policies: Optional list of policy information
        rules: Optional list of rule information
        constraints: Optional list of constraint information
        templates: Optional list of template information
        processing_mode: Mode of processing to apply
        config: Optional planner configuration overrides
        
    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "info_type": info_type,
        "scope": scope,
        "policies": policies or [],
        "rules": rules or [],
        "constraints": constraints or [],
        "templates": templates or [],
        "processing_mode": processing_mode
    }
    
    # Create planner and execute
    planner_config = GovernanceInfoLoadConfig(**config) if config else None
    planner = GovernanceInfoLoadPlanner(planner_config)
    result = planner.plan_load(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "info_type": result.load_plan.info_type.value,
            "scope": result.load_plan.scope.value,
            "policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "content": p.content,
                    "metadata": p.metadata,
                    "scope": p.scope.value,
                    "version": p.version
                }
                for p in result.load_plan.policies
            ],
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "type": r.type,
                    "description": r.description,
                    "logic": r.logic,
                    "examples": r.examples,
                    "metadata": r.metadata
                }
                for r in result.load_plan.rules
            ],
            "constraints": [
                {
                    "id": c.id,
                    "name": c.name,
                    "field": c.field,
                    "condition": c.condition,
                    "rationale": c.rationale,
                    "impact": c.impact,
                    "metadata": c.metadata
                }
                for c in result.load_plan.constraints
            ],
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "type": t.type,
                    "structure": t.structure,
                    "guidelines": t.guidelines,
                    "metadata": t.metadata
                }
                for t in result.load_plan.templates
            ],
            "processing_mode": result.load_plan.processing_mode.value,
            "enable_caching": result.load_plan.enable_caching,
            "cache_ttl": result.load_plan.cache_ttl,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "info_count": result.info_count,
        "policy_count": result.policy_count,
        "rule_count": result.rule_count,
        "constraint_count": result.constraint_count,
        "template_count": result.template_count,
        "load_time_estimate": result.load_time_estimate,
        "memory_estimate": result.memory_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }
