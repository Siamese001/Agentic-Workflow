"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging

from agentic_core.config.core.injection_layer_config import InjectionLayer, InstructionalPattern
from agentic_core.config.core.yaml_injection_loader import YamlValidationError

logger = logging.getLogger(__name__)


def get_instructional_injections() -> list[InstructionalPattern]:
    """Get instructional injection patterns from YAML or markdown fallback.

    Returns:
        List of InstructionalPattern objects.
    """
    try:
        # Try YAML loader first
        from agentic_core.config.core.yaml_injection_loader import get_yaml_loader

        yaml_loader = get_yaml_loader()
        all_patterns = yaml_loader.load_all_patterns()

        # Convert to flat list
        patterns = []
        for layer_patterns in all_patterns.values():
            patterns.extend(layer_patterns)

        logger.info(f"Loaded {len(patterns)} instructional patterns from YAML")
        return patterns

    except ImportError as e:
        logger.warning(f"YAML loader not available, falling back to markdown: {e}")
        return _get_markdown_injections()
    except FileNotFoundError as e:
        logger.warning(f"YAML corpus not found, falling back to markdown: {e}")
        return _get_markdown_injections()
    except YamlValidationError as e:
        logger.warning(f"YAML validation failed, falling back to markdown: {e}")
        return _get_markdown_injections()
    # Any other exception should propagate
    raise


def get_required_injections() -> list[InstructionalPattern]:
    """Get required instructional injection patterns.

    Returns:
        List of required InstructionalPattern objects.
        Deterministic rule:
        1. If any patterns have required=True, return only those
        2. If no patterns have required=True, return all FRAMING layer patterns
    """
    all_patterns = get_instructional_injections()

    # Check for explicitly required patterns
    required_patterns = [pattern for pattern in all_patterns if pattern.required]

    if required_patterns:
        # Found explicitly required patterns
        logger.info(f"Identified {len(required_patterns)} explicitly required instructional patterns")
        return required_patterns
    else:
        # No explicitly required patterns - fallback to FRAMING layer deterministically
        framing_patterns = [pattern for pattern in all_patterns if pattern.layer == InjectionLayer.FRAMING]
        logger.info(f"No explicit required patterns found; using FRAMING layer fallback: {len(framing_patterns)} patterns")
        return framing_patterns


def _get_markdown_injections() -> list[InstructionalPattern]:
    """Fallback: Load patterns from markdown corpus.

    Returns:
        List of InstructionalPattern objects from markdown.
    """
    patterns = []

    # Define the 30 instructional patterns based on v5 structure
    pattern_definitions = [
        # Framing Layer (1-5) - REQUIRED
        (
            1,
            "cost_latency_targets",
            InjectionLayer.FRAMING,
            True,
            "Defines cost and latency constraints for the task",
            "Operate within these constraints: cost_limit={cost_limit}, latency_limit={latency_limit}",
        ),
        (
            2,
            "global_goal_state",
            InjectionLayer.FRAMING,
            True,
            "Establishes the overall goal and success criteria",
            "Primary goal: {goal}. Success criteria: {success_criteria}",
        ),
        (
            3,
            "scope_boundaries",
            InjectionLayer.FRAMING,
            True,
            "Defines what is in and out of scope",
            "Scope includes: {in_scope}. Exclude: {out_scope}",
        ),
        (
            4,
            "success_criteria",
            InjectionLayer.FRAMING,
            True,
            "Specific measurable success criteria",
            "Success when: {criteria}. Measurement: {measurement}",
        ),
        (
            5,
            "task_mode_declaration",
            InjectionLayer.FRAMING,
            True,
            "Declares the operational mode and constraints",
            "Mode: {mode}. Constraints: {constraints}",
        ),
        # Context Layer (6-10) - NOT REQUIRED
        (
            6,
            "contextual_background",
            InjectionLayer.CONTEXT,
            False,
            "Provides relevant background context",
            "Context: {background}. Relevant factors: {factors}",
        ),
        (
            7,
            "domain_knowledge",
            InjectionLayer.CONTEXT,
            False,
            "Injects domain-specific knowledge",
            "Domain expertise: {knowledge}. Apply to: {domain}",
        ),
        (
            8,
            "stakeholder_perspective",
            InjectionLayer.CONTEXT,
            False,
            "Considers stakeholder viewpoints",
            "Stakeholders: {stakeholders}. Perspectives: {perspectives}",
        ),
        (
            9,
            "historical_precedent",
            InjectionLayer.CONTEXT,
            False,
            "References relevant historical examples",
            "Precedent: {precedent}. Lessons: {lessons}",
        ),
        (
            10,
            "environmental_factors",
            InjectionLayer.CONTEXT,
            False,
            "Accounts for environmental context",
            "Environment: {environment}. Impact: {impact}",
        ),
        # Reasoning Layer (11-15) - NOT REQUIRED
        (
            11,
            "logical_framework",
            InjectionLayer.REASONING,
            False,
            "Establishes logical reasoning framework",
            "Logic: {framework}. Apply steps: {steps}",
        ),
        (
            12,
            "analytical_approach",
            InjectionLayer.REASONING,
            False,
            "Specifies analytical methodology",
            "Analysis method: {method}. Steps: {steps}",
        ),
        (
            13,
            "critical_thinking",
            InjectionLayer.REASONING,
            False,
            "Applies critical thinking criteria",
            "Critical criteria: {criteria}. Evaluate: {evaluation}",
        ),
        (
            14,
            "decision_matrix",
            InjectionLayer.REASONING,
            False,
            "Uses decision matrix for evaluation",
            "Decision factors: {factors}. Weights: {weights}",
        ),
        (
            15,
            "hypothesis_testing",
            InjectionLayer.REASONING,
            False,
            "Applies hypothesis testing methodology",
            "Hypothesis: {hypothesis}. Test method: {method}",
        ),
        # Tooling Layer (16-20) - NOT REQUIRED
        (
            16,
            "tool_selection",
            InjectionLayer.TOOLING,
            False,
            "Guides tool selection and usage",
            "Recommended tools: {tools}. Selection criteria: {criteria}",
        ),
        (
            17,
            "resource_allocation",
            InjectionLayer.TOOLING,
            False,
            "Optimizes resource allocation",
            "Resources: {resources}. Allocation strategy: {strategy}",
        ),
        (
            18,
            "workflow_optimization",
            InjectionLayer.TOOLING,
            False,
            "Optimizes workflow processes",
            "Workflow: {workflow}. Optimization: {optimization}",
        ),
        (
            19,
            "automation_opportunities",
            InjectionLayer.TOOLING,
            False,
            "Identifies automation opportunities",
            "Automate: {tasks}. Benefits: {benefits}",
        ),
        (
            20,
            "integration_points",
            InjectionLayer.TOOLING,
            False,
            "Identifies system integration points",
            "Integrations: {points}. Interfaces: {interfaces}",
        ),
        # Safety Layer (21-25) - NOT REQUIRED
        (
            21,
            "constitutional_guardrails",
            InjectionLayer.SAFETY,
            False,
            "Applies constitutional constraints",
            "Constraints: {guardrails}. Compliance: {compliance}",
        ),
        (
            22,
            "risk_assessment",
            InjectionLayer.SAFETY,
            False,
            "Conducts risk assessment",
            "Risks: {risks}. Mitigation: {mitigation}",
        ),
        (
            23,
            "ethical_considerations",
            InjectionLayer.SAFETY,
            False,
            "Incorporates ethical guidelines",
            "Ethics: {principles}. Apply to: {scenarios}",
        ),
        (
            24,
            "security_measures",
            InjectionLayer.SAFETY,
            False,
            "Implements security measures",
            "Security: {measures}. Threat model: {threats}",
        ),
        (
            25,
            "compliance_requirements",
            InjectionLayer.SAFETY,
            False,
            "Ensures regulatory compliance",
            "Compliance: {requirements}. Standards: {standards}",
        ),
        # Output Layer (26-30) - NOT REQUIRED
        (
            26,
            "output_formatting",
            InjectionLayer.OUTPUT,
            False,
            "Specifies output formatting requirements",
            "Format: {format}. Requirements: {requirements}",
        ),
        (
            27,
            "quality_criteria",
            InjectionLayer.OUTPUT,
            False,
            "Defines output quality standards",
            "Quality standards: {criteria}. Validation: {validation}",
        ),
        (
            28,
            "delivery_specifications",
            InjectionLayer.OUTPUT,
            False,
            "Specifies delivery requirements",
            "Delivery: {specifications}. Timeline: {timeline}",
        ),
        (
            29,
            "stakeholder_communication",
            InjectionLayer.OUTPUT,
            False,
            "Guides stakeholder communication",
            "Communication: {strategy}. Audience: {audience}",
        ),
        (
            30,
            "documentation_requirements",
            InjectionLayer.OUTPUT,
            False,
            "Specifies documentation needs",
            "Documentation: {requirements}. Format: {format}",
        ),
    ]

    for pattern_id, name, layer, required, description, template in pattern_definitions:
        pattern = InstructionalPattern(
            id=pattern_id,
            name=name,
            layer=layer,
            description=description,
            template=template,
            enabled=True,
            required=required,
        )
        patterns.append(pattern)

    logger.info(f"Loaded {len(patterns)} instructional patterns from markdown fallback")
    return patterns
