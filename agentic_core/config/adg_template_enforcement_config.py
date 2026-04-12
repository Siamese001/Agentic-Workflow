"""
ADG Template Enforcement Configuration
Mandatory enforcement of ADG-based templates in SWE model
"""

# ADG Template Enforcement Rules
ENFORCEMENT_RULES = {
    # Direct ADG task types - ALWAYS ENFORCED
    "direct_adg_tasks": {
        "adg_analysis": "SWE_ADG_ANALYSIS",
        "violation_remediation": "SWE_VIOLATION_REMEDIATION",
        "layer_boundary_audit": "SWE_LAYER_BOUNDARY_AUDIT",
        "dependency_graph_analysis": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
        "architectural_review": "SWE_ARCHITECTURAL_REVIEW",
        "anti_pattern_detection": "SWE_ANTIPATTERN_DETECTION",
        "system_restructuring": "SWE_SYSTEM_RESTRUCTURING",
        "graph_traversal_optimization": "SWE_GRAPH_TRAVERSAL_OPTIMIZATION",
    },
    # General SWE tasks - ENFORCED when relevant
    "swe_task_mapping": {
        "architecture": "SWE_ARCHITECTURAL_REVIEW",
        "debugging": "SWE_VIOLATION_REMEDIATION",
        "implementation": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
        "refactoring": "SWE_SYSTEM_RESTRUCTURING",
        "planning": "SWE_ARCHITECTURAL_REVIEW",
        "testing": "SWE_VIOLATION_REMEDIATION",
        "integration": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
    },
    # Complexity-based enforcement - MANDATORY
    "complexity_enforcement": {
        "critical": "SWE_SYSTEM_RESTRUCTURING",
        "high": {
            "analysis": "SWE_ADG_ANALYSIS",
            "debugging": "SWE_VIOLATION_REMEDIATION",
            "implementation": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
            "architecture": "SWE_ARCHITECTURAL_REVIEW",
            "refactoring": "SWE_SYSTEM_RESTRUCTURING",
            "planning": "SWE_ARCHITECTURAL_REVIEW",
            "testing": "SWE_VIOLATION_REMEDIATION",
            "integration": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
        },
    },
    # File-based enforcement - MANDATORY
    "file_enforcement": {
        "multi_file_threshold": 5,  # Files > threshold MUST use ADG templates
        "template": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
    },
}

# Enforcement Configuration
ENFORCEMENT_CONFIG = {
    "enabled": True,
    "strict_mode": True,  # If True, non-compliant tasks will fail
    "fallback_allowed": False,  # If True, fallback templates allowed for simple tasks
    "logging_level": "INFO",
    "audit_trail": True,  # Track all enforcement decisions
    "auto_trigger": True,  # Auto-trigger for medium+ complexity
    "real_time_adg_data": True,  # Use real ADG Redis data when available
}

# ADG Context Data (fallback when Redis not available)
ADG_FALLBACK_CONTEXT = {
    "node_count": "10,432",
    "edge_count": "681,161",
    "violation_count": "5,301",
    "layer_info": "L0: 7,220 nodes, L1: 4,362 nodes, L2-L6: 2,850 nodes",
    "high_severity_count": "1,200",
    "medium_severity_count": "2,800",
    "low_severity_count": "1,301",
    "common_violation_types": "except:Exception, for_retry, CURRENT_PHASE, except:bare",
    "boundary_violations": "17",
    "gravity_violations": "17",
    "layer_count": "7",
    "layer_distribution": "L0: 69.2%, L1: 41.8%, L2: 14.4%, L3: 7.7%, L4: 1.9%, L5: 1.4%, L6: 1.9%",
    "dependency_count": "681,161",
    "circular_deps": "0",
    "longest_chain": "15",
    "hub_nodes": "42",
    "component_count": "156",
    "patterns_used": "Layered Architecture, Dependency Injection, Event-Driven",
    "integration_points": "45",
    "quality_attributes": "Performance, Scalability, Maintainability, Security",
    "antipattern_count": "5,301",
    "high_impact_count": "1,200",
    "common_categories": "Exception Handling, Retry Logic, State Management",
    "affected_files": "234",
    "system_size": "Large-scale enterprise system",
    "complexity_metrics": "Cyclomatic Complexity: 8.5 avg, Coupling: 12.3 avg",
    "identified_issues": "Layer violations, Exception handling anti-patterns, Circular dependencies",
    "restructuring_goals": "Improve layer compliance, Reduce technical debt, Enhance maintainability",
    "current_traversal_time": "2.3s average",
    "graph_size": "681,161 edges",
    "traversal_frequency": "100+ queries/hour",
    "bottlenecks": "Layer boundary queries, Violation filtering, Graph traversal",
}

# Enforcement Validation Rules
VALIDATION_RULES = {
    "must_contain_adg_context": [
        "node_count",
        "edge_count",
        "violation_count",
        "layer_info",
    ],
    "must_contain_sequential_structure": [
        "### Thought 1:",
        "### Thought 2:",
        "### Thought 3:",
        "### Thought 4:",
        "### Thought 5:",
        "### Thought 6:",
    ],
    "must_contain_real_data": [
        "10,432",
        "681,161",
        "5,301",
    ],
    "forbidden_patterns": [
        "fallback template",
        "basic template",
        "simple analysis",
    ],
}

# Enforcement Metrics
ENFORCEMENT_METRICS = {
    "total_enforcements": 0,
    "successful_enforcements": 0,
    "failed_enforcements": 0,
    "fallback_usage": 0,
    "template_types_used": {},
    "complexity_distribution": {},
    "file_size_distribution": {},
}


def get_enforcement_template(step_type: str, step_config: dict = None) -> str:
    """
    Get the enforced ADG template for a given step type and configuration.

    Args:
        step_type: The type of step being executed
        step_config: Configuration including complexity, files, etc.

    Returns:
        The template type that MUST be used
    """

    # Check direct ADG tasks first (highest precedence)
    if step_type in ENFORCEMENT_RULES["direct_adg_tasks"]:
        return ENFORCEMENT_RULES["direct_adg_tasks"][step_type]

    # Check complexity-based enforcement SECOND (overrides SWE mapping)
    if step_config:
        complexity = step_config.get("complexity", "medium").lower()

        if complexity == "critical":
            return ENFORCEMENT_RULES["complexity_enforcement"]["critical"]

        if complexity == "high" and step_type in ENFORCEMENT_RULES["complexity_enforcement"]["high"]:
            return ENFORCEMENT_RULES["complexity_enforcement"]["high"][step_type]

        # Check file-based enforcement
        file_count = len(step_config.get("files", []))
        if file_count > ENFORCEMENT_RULES["file_enforcement"]["multi_file_threshold"]:
            return ENFORCEMENT_RULES["file_enforcement"]["template"]

    # Check SWE task mapping LAST (lowest precedence)
    if step_type in ENFORCEMENT_RULES["swe_task_mapping"]:
        return ENFORCEMENT_RULES["swe_task_mapping"][step_type]

    # No enforcement required
    return None


def is_enforcement_required(step_type: str, step_config: dict = None) -> bool:
    """
    Check if ADG template enforcement is required for this step.

    Args:
        step_type: The type of step being executed
        step_config: Configuration including complexity, files, etc.

    Returns:
        True if enforcement is required, False otherwise
    """

    template = get_enforcement_template(step_type, step_config)
    return template is not None


def validate_enforcement_compliance(template_content: str, expected_template: str) -> dict:
    """
    Validate that the rendered template complies with enforcement rules.
    Template-specific validation for better accuracy.
    """

    validation_results = {
        "compliant": True,
        "violations": [],
        "score": 0,
        "total_checks": 0,
    }

    # Template-specific validation rules
    template_validation_rules = {
        "SWE_ADG_ANALYSIS": {
            "required_context": ["node_count", "edge_count", "layer_info", "violation_count"],
            "required_data": ["10,432", "681,161", "5,301"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_VIOLATION_REMEDIATION": {
            "required_context": [
                "violation_count",
                "high_severity_count",
                "medium_severity_count",
                "low_severity_count",
            ],
            "required_data": ["5,301", "1,200", "2,800", "1,301"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_ARCHITECTURAL_REVIEW": {
            "required_context": [
                "component_count",
                "patterns_used",
                "integration_points",
                "quality_attributes",
            ],
            "required_data": ["156", "Layered Architecture", "Dependency Injection", "Event-Driven"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_DEPENDENCY_GRAPH_ANALYSIS": {
            "required_context": ["dependency_count", "circular_deps", "longest_chain", "hub_nodes"],
            "required_data": ["681,161", "0", "15", "42"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_LAYER_BOUNDARY_AUDIT": {
            "required_context": [
                "layer_count",
                "layer_distribution",
                "boundary_violations",
                "gravity_violations",
            ],
            "required_data": ["7", "69.2%", "41.8%", "17"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_ANTIPATTERN_DETECTION": {
            "required_context": [
                "antipattern_count",
                "high_impact_count",
                "common_categories",
                "affected_files",
            ],
            "required_data": ["5,301", "1,200", "Exception Handling", "234"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_SYSTEM_RESTRUCTURING": {
            "required_context": [
                "system_size",
                "complexity_metrics",
                "identified_issues",
                "restructuring_goals",
            ],
            "required_data": [
                "Large-scale enterprise",
                "Cyclomatic Complexity",
                "layer violations",
                "technical debt",
            ],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
        "SWE_GRAPH_TRAVERSAL_OPTIMIZATION": {
            "required_context": [
                "current_traversal_time",
                "graph_size",
                "traversal_frequency",
                "bottlenecks",
            ],
            "required_data": ["2.3s", "681,161 edges", "100+ queries", "Layer boundary"],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
    }

    # Get validation rules for this template
    rules = template_validation_rules.get(
        expected_template,
        {
            "required_context": [],
            "required_data": [],
            "required_structure": [
                "### Thought 1:",
                "### Thought 2:",
                "### Thought 3:",
                "### Thought 4:",
                "### Thought 5:",
                "### Thought 6:",
            ],
        },
    )

    # Check sequential structure (required for all templates)
    for required_structure in rules["required_structure"]:
        validation_results["total_checks"] += 1
        if required_structure not in template_content:
            validation_results["compliant"] = False
            validation_results["violations"].append(f"Missing sequential structure: {required_structure}")
        else:
            validation_results["score"] += 1

    # Check template-specific context
    for required_context in rules["required_context"]:
        validation_results["total_checks"] += 1
        if required_context not in template_content:
            validation_results["violations"].append(f"Missing required context: {required_context}")
        else:
            validation_results["score"] += 1

    # Check template-specific data
    for required_data in rules["required_data"]:
        validation_results["total_checks"] += 1
        if required_data not in template_content:
            validation_results["violations"].append(f"Missing required data: {required_data}")
        else:
            validation_results["score"] += 1

    # Check for forbidden patterns
    for forbidden in VALIDATION_RULES["forbidden_patterns"]:
        validation_results["total_checks"] += 1
        if forbidden in template_content.lower():
            validation_results["compliant"] = False
            validation_results["violations"].append(f"Contains forbidden pattern: {forbidden}")
        else:
            validation_results["score"] += 1

    # Calculate percentage
    if validation_results["total_checks"] > 0:
        validation_results["percentage"] = (
            validation_results["score"] / validation_results["total_checks"]
        ) * 100
    else:
        validation_results["percentage"] = 0

    return validation_results


# Export configuration
__all__ = [
    "ENFORCEMENT_RULES",
    "ENFORCEMENT_CONFIG",
    "ADG_FALLBACK_CONTEXT",
    "VALIDATION_RULES",
    "ENFORCEMENT_METRICS",
    "get_enforcement_template",
    "is_enforcement_required",
    "validate_enforcement_compliance",
]
