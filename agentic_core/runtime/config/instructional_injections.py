"""Instructional injections for agentic_core - self-contained implementation.

This module provides instructional injection patterns without depending on apps_shared,
maintaining agentic_core boundary integrity.
"""

import logging
from pathlib import Path
from typing import List

from agentic_core.config.core.injection_layer_config import InstructionalPattern, InjectionLayer

logger = logging.getLogger(__name__)


def get_instructional_injections() -> List[InstructionalPattern]:
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
        
    except Exception as e:
        logger.warning(f"YAML loader failed, falling back to markdown: {e}")
        return _get_markdown_injections()


def get_required_injections() -> List[InstructionalPattern]:
    """Get required instructional injection patterns.
    
    Returns:
        List of required InstructionalPattern objects.
    """
    all_patterns = get_instructional_injections()
    
    # Mark first few patterns as required (simplified logic)
    required_patterns = []
    for i, pattern in enumerate(all_patterns[:5]):  # First 5 as required
        required_patterns.append(pattern)
    
    logger.info(f"Identified {len(required_patterns)} required instructional patterns")
    return required_patterns


def _get_markdown_injections() -> List[InstructionalPattern]:
    """Fallback: Load patterns from markdown corpus.
    
    Returns:
        List of InstructionalPattern objects from markdown.
    """
    patterns = []
    
    # Define the 30 instructional patterns based on v5 structure
    pattern_definitions = [
        # Framing Layer (1-5)
        (1, "cost_latency_targets", InjectionLayer.FRAMING, 
         "Defines cost and latency constraints for the task", 
         "Operate within these constraints: cost_limit={cost_limit}, latency_limit={latency_limit}"),
        (2, "global_goal_state", InjectionLayer.FRAMING,
         "Establishes the overall goal and success criteria",
         "Primary goal: {goal}. Success criteria: {success_criteria}"),
        (3, "scope_boundaries", InjectionLayer.FRAMING,
         "Defines what is in and out of scope",
         "Scope includes: {in_scope}. Exclude: {out_scope}"),
        (4, "success_criteria", InjectionLayer.FRAMING,
         "Specific measurable success criteria",
         "Success when: {criteria}. Measurement: {measurement}"),
        (5, "task_mode_declaration", InjectionLayer.FRAMING,
         "Declares the operational mode and constraints",
         "Mode: {mode}. Constraints: {constraints}"),
        
        # Context Layer (6-10)
        (6, "contextual_background", InjectionLayer.CONTEXT,
         "Provides relevant background context",
         "Context: {background}. Relevant factors: {factors}"),
        (7, "domain_knowledge", InjectionLayer.CONTEXT,
         "Injects domain-specific knowledge",
         "Domain expertise: {knowledge}. Apply to: {domain}"),
        (8, "stakeholder_perspective", InjectionLayer.CONTEXT,
         "Considers stakeholder viewpoints",
         "Stakeholders: {stakeholders}. Perspectives: {perspectives}"),
        (9, "historical_precedent", InjectionLayer.CONTEXT,
         "References relevant historical examples",
         "Precedent: {precedent}. Lessons: {lessons}"),
        (10, "environmental_factors", InjectionLayer.CONTEXT,
          "Accounts for environmental context",
          "Environment: {environment}. Impact: {impact}"),
        
        # Reasoning Layer (11-15)
        (11, "logical_framework", InjectionLayer.REASONING,
          "Establishes logical reasoning framework",
          "Logic: {framework}. Apply steps: {steps}"),
        (12, "analytical_approach", InjectionLayer.REASONING,
          "Specifies analytical methodology",
          "Analysis method: {method}. Steps: {steps}"),
        (13, "critical_thinking", InjectionLayer.REASONING,
          "Applies critical thinking criteria",
          "Critical criteria: {criteria}. Evaluate: {evaluation}"),
        (14, "decision_matrix", InjectionLayer.REASONING,
          "Uses decision matrix for evaluation",
          "Decision factors: {factors}. Weights: {weights}"),
        (15, "hypothesis_testing", InjectionLayer.REASONING,
          "Applies hypothesis testing methodology",
          "Hypothesis: {hypothesis}. Test method: {method}"),
        
        # Tooling Layer (16-20)
        (16, "tool_selection", InjectionLayer.TOOLING,
          "Guides tool selection and usage",
          "Recommended tools: {tools}. Selection criteria: {criteria}"),
        (17, "resource_allocation", InjectionLayer.TOOLING,
          "Optimizes resource allocation",
          "Resources: {resources}. Allocation strategy: {strategy}"),
        (18, "workflow_optimization", InjectionLayer.TOOLING,
          "Optimizes workflow processes",
          "Workflow: {workflow}. Optimization: {optimization}"),
        (19, "automation_opportunities", InjectionLayer.TOOLING,
          "Identifies automation opportunities",
          "Automate: {tasks}. Benefits: {benefits}"),
        (20, "integration_points", InjectionLayer.TOOLING,
          "Identifies system integration points",
          "Integrations: {points}. Interfaces: {interfaces}"),
        
        # Safety Layer (21-25)
        (21, "constitutional_guardrails", InjectionLayer.SAFETY,
          "Applies constitutional constraints",
          "Constraints: {guardrails}. Compliance: {compliance}"),
        (22, "risk_assessment", InjectionLayer.SAFETY,
          "Conducts risk assessment",
          "Risks: {risks}. Mitigation: {mitigation}"),
        (23, "ethical_considerations", InjectionLayer.SAFETY,
          "Incorporates ethical guidelines",
          "Ethics: {principles}. Apply to: {scenarios}"),
        (24, "security_measures", InjectionLayer.SAFETY,
          "Implements security measures",
          "Security: {measures}. Threat model: {threats}"),
        (25, "compliance_requirements", InjectionLayer.SAFETY,
          "Ensures regulatory compliance",
          "Compliance: {requirements}. Standards: {standards}"),
        
        # Output Layer (26-30)
        (26, "output_formatting", InjectionLayer.OUTPUT,
          "Specifies output formatting requirements",
          "Format: {format}. Requirements: {requirements}"),
        (27, "quality_criteria", InjectionLayer.OUTPUT,
          "Defines output quality standards",
          "Quality standards: {criteria}. Validation: {validation}"),
        (28, "delivery_specifications", InjectionLayer.OUTPUT,
          "Specifies delivery requirements",
          "Delivery: {specifications}. Timeline: {timeline}"),
        (29, "stakeholder_communication", InjectionLayer.OUTPUT,
          "Guides stakeholder communication",
          "Communication: {strategy}. Audience: {audience}"),
        (30, "documentation_requirements", InjectionLayer.OUTPUT,
          "Specifies documentation needs",
          "Documentation: {requirements}. Format: {format}"),
    ]
    
    for pattern_id, name, layer, description, template in pattern_definitions:
        pattern = InstructionalPattern(
            id=pattern_id,
            name=name,
            layer=layer,
            description=description,
            template=template,
            enabled=True
        )
        patterns.append(pattern)
    
    logger.info(f"Loaded {len(patterns)} instructional patterns from markdown fallback")
    return patterns
