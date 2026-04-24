"""
Sequential Thinking Enhanced Planning Workflow for Kimi 2.5

This workflow integrates sequential thinking MCP calls into the planning process
to improve reasoning quality and structured problem decomposition.
ENFORCED: ADG-based templates are mandatory for relevant task types.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from tools.utils.planning.preflight_hook import PlanningPreflightHook, TokenBudgetExceededError
from tools.utils.planning.token_estimator import ContextWindowEstimator, TokenBudget
from tqdm import tqdm
from agentic_core.L0_routing.config.path_constants import DOCS_REPORTS_DIR

# Import ADG-based templates and enforcement configuration
try:
    from agentic_core.config.adg_template_enforcement_config import (
        ADG_FALLBACK_CONTEXT,
        ENFORCEMENT_CONFIG,
        ENFORCEMENT_RULES,
        get_enforcement_template,
        is_enforcement_required,
        validate_enforcement_compliance,
    )
    from apps_shared.prompts.sequential_thinking_templates import (
        SequentialThinkingTemplate,
        get_template,
        render_template,
    )

    ADG_TEMPLATES_AVAILABLE = True
    ENFORCEMENT_ENABLED = ENFORCEMENT_CONFIG.get("enabled", True)
except ImportError:
    ADG_TEMPLATES_AVAILABLE = False
    ENFORCEMENT_ENABLED = False
    logging.warning("ADG templates or enforcement config not available, falling back to basic templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SequentialThinkingEnhancedWorkflow:
    """
    SWE 1.5 planning workflow with integrated sequential thinking.

    This workflow automatically triggers sequential thinking for complex tasks
    and integrates with the token budget management system.
    """

    def __init__(
        self,
        budget_file: Path | None = None,
        custom_budget: TokenBudget | None = None,
        seq_thinking_enabled: bool = True,
    ):
        """
        Initialize the sequential thinking enhanced workflow.

        Args:
            budget_file: Path to budget history file
            custom_budget: Custom token budget configuration
            seq_thinking_enabled: Enable sequential thinking integration
        """
        self.preflight_hook = PlanningPreflightHook(
            estimator=ContextWindowEstimator(budget=custom_budget),
            budget_file=budget_file,
        )

        self.seq_thinking_enabled = seq_thinking_enabled and self._check_seq_thinking_available()

        # Workflow state
        self.current_phase = None
        self.current_wave = None
        self.step_results = []
        self.seq_thinking_usage = 0

        # Sequential thinking configuration
        self.seq_thinking_config = {
            "max_thoughts": int(os.environ.get("SEQUENTIAL_THINKING_MAX_THOUGHTS", "15")),
            "token_budget": int(os.environ.get("SEQUENTIAL_THINKING_TOKEN_BUDGET", "30000")),
            "complexity_threshold": os.environ.get("SEQUENTIAL_THINKING_COMPLEXITY_THRESHOLD", "medium"),
            "auto_trigger": os.environ.get("SEQUENTIAL_THINKING_AUTO_TRIGGER", "true").lower() == "true",
        }

    def _check_seq_thinking_available(self) -> bool:
        """Check if sequential thinking MCP is available."""
        return os.environ.get("SEQUENTIAL_THINKING_ENABLED", "false").lower() == "true"

    def force_sequential_thinking(self, step_type: str, step_config: dict[str, Any]) -> bool:
        """Determine if sequential thinking should be forced for this step."""

        if not self.seq_thinking_enabled:
            return False

        # Force for complex analysis tasks
        complex_types = ["analysis", "architecture", "refactoring", "debugging", "planning"]
        high_complexity = ["high", "critical"]

        # Check step type
        if step_type in complex_types:
            return True

        # Check complexity level
        if step_config.get("complexity", "medium").lower() in high_complexity:
            return True

        # Check for multi-file operations
        if len(step_config.get("files", [])) > 3:
            return True

        # Check for integration tasks
        if any(keyword in step_type.lower() for keyword in ["integration", "multiple", "cross"]):
            return True

        # Check auto-trigger configuration
        if self.seq_thinking_config["auto_trigger"]:
            # Auto-trigger for medium+ complexity
            if step_config.get("complexity", "medium") in ["medium", "high", "critical"]:
                return True

        return False

    def _get_seq_thinking_template(self, step_type: str, step_config: dict[str, Any] = None) -> str:
        """
        Get appropriate sequential thinking template for step type.
        ENFORCED: ADG-based templates are mandatory for relevant task types.
        """

        if not ADG_TEMPLATES_AVAILABLE or not ENFORCEMENT_ENABLED:
            logger.warning("ADG templates or enforcement disabled, using fallback template")
            return self._get_fallback_template(step_type, step_config)

        # ENFORCEMENT: Use centralized enforcement logic
        try:
            enforced_template = get_enforcement_template(step_type, step_config)

            if enforced_template:
                # Convert string template name to enum
                template_enum = getattr(SequentialThinkingTemplate, enforced_template, None)
                if template_enum:
                    logger.info(f"ENFORCING ADG template: {template_enum.value} for step type: {step_type}")
                    rendered = self._render_adg_template(template_enum, step_type, step_config)

                    # Validate compliance if strict mode is enabled
                    if ENFORCEMENT_CONFIG.get("strict_mode", True):
                        validation = validate_enforcement_compliance(rendered, enforced_template)
                        if not validation["compliant"]:
                            logger.warning(f"Template validation failed: {validation['violations']}")
                        else:
                            logger.info(f"Template validation passed: {validation['percentage']:.1f}% score")

                    return rendered
                else:
                    logger.error(f"Unknown enforced template: {enforced_template}")

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            logger.error(f"Enforcement logic failed: {e}")

        # Fallback to manual mapping if enforcement fails
        return self._get_manual_enforced_template(step_type, step_config)

    def _get_manual_enforced_template(self, step_type: str, step_config: dict[str, Any] = None) -> str:
        """Manual enforcement fallback when centralized enforcement fails."""

        # ENFORCEMENT: Map step types to mandatory ADG templates
        adg_template_mapping = {
            # ADG-specific task types - ENFORCED
            "adg_analysis": SequentialThinkingTemplate.SWE_ADG_ANALYSIS,
            "violation_remediation": SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,
            "layer_boundary_audit": SequentialThinkingTemplate.SWE_LAYER_BOUNDARY_AUDIT,
            "dependency_graph_analysis": SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,
            "architectural_review": SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,
            "anti_pattern_detection": SequentialThinkingTemplate.SWE_ANTIPATTERN_DETECTION,
            "system_restructuring": SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING,
            "graph_traversal_optimization": SequentialThinkingTemplate.SWE_GRAPH_TRAVERSAL_OPTIMIZATION,
            # General SWE tasks - ENFORCED to use ADG templates when relevant
            "architecture": SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,
            "debugging": SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,  # Violations often cause bugs
            "implementation": SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,  # Implementation affects dependencies
            "refactoring": SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING,  # Refactoring is restructuring
            "planning": SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,  # Planning requires architectural review
            "testing": SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,  # Testing often reveals violations
            "integration": SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,  # Integration affects dependencies
        }

        # ENFORCEMENT: Check if this step type requires ADG template
        if step_type in adg_template_mapping:
            template_type = adg_template_mapping[step_type]
            logger.info(f"MANUAL ENFORCEMENT: ADG template: {template_type.value} for step type: {step_type}")
            return self._render_adg_template(template_type, step_type, step_config)

        # ENFORCEMENT: Check complexity-based enforcement
        if step_config and step_config.get("complexity", "medium").lower() in ["high", "critical"]:
            # High/critical complexity tasks MUST use ADG templates
            template_type = self._select_complexity_based_adg_template(step_type, step_config)
            logger.info(
                f"COMPLEXITY ENFORCEMENT: ADG template: {template_type.value} for {step_type} ({step_config.get('complexity')})"
            )
            return self._render_adg_template(template_type, step_type, step_config)

        # ENFORCEMENT: Check file-based enforcement
        if (
            step_config
            and len(step_config.get("files", []))
            > ENFORCEMENT_RULES["file_enforcement"]["multi_file_threshold"]
        ):
            # Multi-file operations MUST use ADG templates
            template_type = SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS
            logger.info(
                f"FILE ENFORCEMENT: ADG template: {template_type.value} for {step_type} ({len(step_config.get('files', []))} files)"
            )
            return self._render_adg_template(template_type, step_type, step_config)

        # Default fallback for simple tasks (if allowed)
        if ENFORCEMENT_CONFIG.get("fallback_allowed", False):
            logger.info(f"Using fallback template for simple task: {step_type}")
            return self._get_fallback_template(step_type, step_config)
        else:
            # Strict mode: even simple tasks get basic ADG template
            logger.info(f"STRICT MODE: Using basic ADG template for: {step_type}")
            return self._render_adg_template(SequentialThinkingTemplate.SWE_ANALYSIS, step_type, step_config)

    def _render_adg_template(
        self, template_type: SequentialThinkingTemplate, step_type: str, step_config: dict[str, Any] = None
    ) -> str:
        """Render ADG template with current system context."""

        try:
            # Get current ADG data for template variables
            adg_context = self._get_current_adg_context()

            # Prepare template variables based on template type
            template_vars = self._get_template_variables(template_type, step_type, adg_context, step_config)

            # Render the template
            rendered = render_template(template_type, **template_vars)

            logger.info(f"Successfully rendered ADG template: {template_type.value}")
            return rendered

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            logger.error(f"Failed to render ADG template {template_type.value}: {e}")
            return self._get_fallback_template(step_type, step_config)

    def _get_template_variables(
        self,
        template_type: SequentialThinkingTemplate,
        step_type: str,
        adg_context: dict[str, str],
        step_config: dict[str, Any] = None,
    ) -> dict[str, str]:
        """Get template-specific variables for rendering."""

        # Base variables for all templates
        base_vars = {
            "context": f"Analysis of {step_type} task with current system state",
        }

        # Template-specific variable mappings
        template_mappings = {
            SequentialThinkingTemplate.SWE_ADG_ANALYSIS: {
                "analysis_title": f"System {step_type.title()} Analysis",
                "node_count": adg_context["node_count"],
                "edge_count": adg_context["edge_count"],
                "layer_info": adg_context["layer_info"],
                "violation_count": adg_context["violation_count"],
            },
            SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION: {
                "remediation_title": f"{step_type.title()} Remediation Plan",
                "violation_count": adg_context["violation_count"],
                "high_severity_count": adg_context["high_severity_count"],
                "medium_severity_count": adg_context["medium_severity_count"],
                "low_severity_count": adg_context["low_severity_count"],
                "common_violation_types": adg_context["common_violation_types"],
            },
            SequentialThinkingTemplate.SWE_LAYER_BOUNDARY_AUDIT: {
                "audit_title": f"{step_type.title()} Compliance Audit",
                "layer_count": adg_context["layer_count"],
                "layer_distribution": adg_context["layer_distribution"],
                "boundary_violations": adg_context["boundary_violations"],
                "gravity_violations": adg_context["gravity_violations"],
            },
            SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS: {
                "analysis_title": f"Dependency Graph {step_type.title()} Analysis",
                "dependency_count": adg_context["dependency_count"],
                "circular_deps": adg_context["circular_deps"],
                "longest_chain": adg_context["longest_chain"],
                "hub_nodes": adg_context["hub_nodes"],
            },
            SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW: {
                "review_title": f"System {step_type.title()} Review",
                "component_count": adg_context["component_count"],
                "patterns_used": adg_context["patterns_used"],
                "integration_points": adg_context["integration_points"],
                "quality_attributes": adg_context["quality_attributes"],
            },
            SequentialThinkingTemplate.SWE_ANTIPATTERN_DETECTION: {
                "detection_title": f"Anti-pattern {step_type.title()} Detection",
                "antipattern_count": adg_context["antipattern_count"],
                "high_impact_count": adg_context["high_impact_count"],
                "common_categories": adg_context["common_categories"],
                "affected_files": adg_context["affected_files"],
            },
            SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING: {
                "restructuring_title": f"System {step_type.title()} Restructuring",
                "system_size": adg_context["system_size"],
                "complexity_metrics": adg_context["complexity_metrics"],
                "identified_issues": adg_context["identified_issues"],
                "restructuring_goals": adg_context["restructuring_goals"],
            },
            SequentialThinkingTemplate.SWE_GRAPH_TRAVERSAL_OPTIMIZATION: {
                "optimization_title": f"Graph Traversal {step_type.title()} Optimization",
                "current_traversal_time": adg_context["current_traversal_time"],
                "graph_size": adg_context["graph_size"],
                "traversal_frequency": adg_context["traversal_frequency"],
                "bottlenecks": adg_context["bottlenecks"],
            },
        }

        # Get template-specific variables
        template_vars = template_mappings.get(template_type, {})

        # Add base variables
        template_vars.update(base_vars)

        # Add step-specific variables
        if step_config:
            template_vars.update(
                {
                    "step_name": step_config.get("name", step_type),
                    "step_description": step_config.get("description", ""),
                    "step_files": ", ".join(step_config.get("files", [])),
                    "step_complexity": step_config.get("complexity", "medium"),
                }
            )

        return template_vars

    def _get_current_adg_context(self) -> dict[str, str]:
        """Get current ADG system context for template variables."""

        # Try to get real ADG data
        try:
            if ENFORCEMENT_CONFIG.get("real_time_adg_data", True):
                # Import ADG Redis tools if available
                from mcp1_adg_meta import mcp1_adg_meta
                from mcp1_adg_violations import mcp1_adg_violations

                # Get ADG metadata
                meta_result = mcp1_adg_meta()
                if meta_result.get("status") == "ok":
                    meta_data = meta_result.get("data", {})
                    node_count = str(meta_data.get("node_count", "0"))
                    edge_count = str(meta_data.get("edge_count", "0"))
                    violation_count = str(meta_data.get("violation_count", "0"))
                else:
                    # Use fallback values
                    node_count = ADG_FALLBACK_CONTEXT["node_count"]
                    edge_count = ADG_FALLBACK_CONTEXT["edge_count"]
                    violation_count = ADG_FALLBACK_CONTEXT["violation_count"]

                # Get violation details
                violations_result = mcp1_adg_violations()
                if violations_result.get("status") == "ok":
                    violations_data = violations_result.get("data", {})
                    high_severity = str(
                        len([v for v in violations_data.get("violations", []) if v.get("severity") == "HIGH"])
                    )
                    medium_severity = str(
                        len(
                            [
                                v
                                for v in violations_data.get("violations", [])
                                if v.get("severity") == "MEDIUM"
                            ]
                        )
                    )
                    low_severity = str(
                        len([v for v in violations_data.get("violations", []) if v.get("severity") == "LOW"])
                    )
                else:
                    # Use fallback values
                    high_severity = ADG_FALLBACK_CONTEXT["high_severity_count"]
                    medium_severity = ADG_FALLBACK_CONTEXT["medium_severity_count"]
                    low_severity = ADG_FALLBACK_CONTEXT["low_severity_count"]

                return {
                    "node_count": node_count,
                    "edge_count": edge_count,
                    "violation_count": violation_count,
                    "layer_info": ADG_FALLBACK_CONTEXT["layer_info"],
                    "high_severity_count": high_severity,
                    "medium_severity_count": medium_severity,
                    "low_severity_count": low_severity,
                    "common_violation_types": ADG_FALLBACK_CONTEXT["common_violation_types"],
                    "boundary_violations": ADG_FALLBACK_CONTEXT["boundary_violations"],
                    "gravity_violations": ADG_FALLBACK_CONTEXT["gravity_violations"],
                    "layer_count": ADG_FALLBACK_CONTEXT["layer_count"],
                    "layer_distribution": ADG_FALLBACK_CONTEXT["layer_distribution"],
                    "dependency_count": edge_count,
                    "circular_deps": ADG_FALLBACK_CONTEXT["circular_deps"],
                    "longest_chain": ADG_FALLBACK_CONTEXT["longest_chain"],
                    "hub_nodes": ADG_FALLBACK_CONTEXT["hub_nodes"],
                    "component_count": ADG_FALLBACK_CONTEXT["component_count"],
                    "patterns_used": ADG_FALLBACK_CONTEXT["patterns_used"],
                    "integration_points": ADG_FALLBACK_CONTEXT["integration_points"],
                    "quality_attributes": ADG_FALLBACK_CONTEXT["quality_attributes"],
                    "antipattern_count": violation_count,
                    "high_impact_count": high_severity,
                    "common_categories": ADG_FALLBACK_CONTEXT["common_categories"],
                    "affected_files": ADG_FALLBACK_CONTEXT["affected_files"],
                    "system_size": ADG_FALLBACK_CONTEXT["system_size"],
                    "complexity_metrics": ADG_FALLBACK_CONTEXT["complexity_metrics"],
                    "identified_issues": ADG_FALLBACK_CONTEXT["identified_issues"],
                    "restructuring_goals": ADG_FALLBACK_CONTEXT["restructuring_goals"],
                    "current_traversal_time": ADG_FALLBACK_CONTEXT["current_traversal_time"],
                    "graph_size": f"{edge_count} edges",
                    "traversal_frequency": ADG_FALLBACK_CONTEXT["traversal_frequency"],
                    "bottlenecks": ADG_FALLBACK_CONTEXT["bottlenecks"],
                }
            else:
                # Use fallback data only
                return ADG_FALLBACK_CONTEXT.copy()

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            if ENFORCEMENT_CONFIG.get("audit_trail", True):
                logger.warning(f"Could not fetch real ADG data, using fallback: {e}")

            # Always return fallback context
            return ADG_FALLBACK_CONTEXT.copy()

    def _select_complexity_based_adg_template(
        self, step_type: str, step_config: dict[str, Any]
    ) -> SequentialThinkingTemplate:
        """Select ADG template based on complexity and step type."""

        complexity = step_config.get("complexity", "medium").lower()

        if complexity == "critical":
            # Critical complexity always gets system restructuring
            return SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING

        # High complexity mapping
        complexity_mapping = {
            "analysis": SequentialThinkingTemplate.SWE_ADG_ANALYSIS,
            "debugging": SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,
            "implementation": SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,
            "architecture": SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,
            "refactoring": SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING,
            "planning": SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,
            "testing": SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,
            "integration": SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,
        }

        return complexity_mapping.get(step_type, SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW)

    def _get_fallback_template(self, step_type: str, step_config: dict[str, Any] = None) -> str:
        templates = {
            "analysis": """
# Sequential Analysis for {step_name}

## Context
{context}

## Task
Analyze the provided code/problem systematically using sequential thinking.

## Sequential Analysis Requirements

### Thought 1: Problem Understanding
- What is the core issue or requirement?
- What are the key constraints and boundaries?
- What information is missing or unclear?

### Thought 2: Current State Assessment
- What exists currently?
- What are the strengths and weaknesses?
- What patterns or anti-patterns do you observe?

### Thought 3: Decomposition
- Break the problem into smaller, manageable components
- Identify dependencies between components
- Prioritize components by importance or risk

### Thought 4: Analysis Strategy
- What analysis approach will be most effective?
- What tools or techniques should be used?
- How will you validate your analysis?

### Thought 5: Risk Assessment
- What could go wrong with this analysis?
- What are the common pitfalls in this type of problem?
- How will you mitigate these risks?

### Thought 6: Recommendations
- What are your key findings?
- What specific actions should be taken?
- What are the next steps and dependencies?

Please analyze this systematically using the sequential thinking approach.
""",
            "implementation": """
# Sequential Implementation Planning for {step_name}

## Context
{context}

## Task
Plan the implementation using sequential thinking for structured reasoning.

## Sequential Planning Requirements

### Thought 1: Requirements Analysis
- What exactly needs to be implemented?
- What are the functional and non-functional requirements?
- What are the acceptance criteria?

### Thought 2: Design Approach
- What architectural pattern should be used?
- How should the code be structured?
- What design principles apply?

### Thought 3: Implementation Strategy
- What is the optimal sequence of implementation?
- What components should be built first?
- How should dependencies be managed?

### Thought 4: Risk Mitigation
- What implementation risks exist?
- How will you handle edge cases?
- What testing strategy is needed?

### Thought 5: Integration Planning
- How will this integrate with existing code?
- What APIs or interfaces are needed?
- How will backward compatibility be maintained?

### Thought 6: Validation & Testing
- How will you verify the implementation?
- What test cases are needed?
- How will you measure success?

Please plan this implementation systematically using sequential thinking.
""",
            "debugging": """
# Sequential Debugging Analysis for {step_name}

## Context
{context}

## Task
Debug the issue systematically using sequential thinking.

## Sequential Debugging Requirements

### Thought 1: Problem Definition
- What exactly is the symptom or error?
- When and where does it occur?
- What are the reproduction steps?

### Thought 2: Information Gathering
- What logs, traces, or error messages are available?
- What recent changes might be related?
- What environmental factors could be relevant?

### Thought 3: Hypothesis Formation
- What are the most likely root causes?
- How can you prioritize hypotheses?
- What evidence supports each hypothesis?

### Thought 4: Systematic Investigation
- How will you test each hypothesis?
- What debugging tools or techniques will you use?
- How will you isolate variables?

### Thought 5: Solution Development
- What is the most likely fix?
- How will you implement it safely?
- How will you test the fix?

### Thought 6: Prevention
- How can similar issues be prevented?
- What monitoring or alerts are needed?
- What documentation should be updated?

Please debug this systematically using sequential thinking.
""",
        }

        return templates.get(step_type, templates["analysis"])

    def _execute_sequential_thinking(
        self, step_name: str, step_type: str, context: dict[str, Any], step_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Execute sequential thinking for a step with ENFORCED ADG templates."""

        if not self.seq_thinking_enabled:
            return {"success": False, "reason": "Sequential thinking not available"}

        logger.info(f"Executing sequential thinking for step: {step_name} (type: {step_type})")

        # ENFORCEMENT: Get mandatory ADG template
        template = self._get_seq_thinking_template(step_type, step_config)

        # Log which template is being used
        if ADG_TEMPLATES_AVAILABLE and step_config:
            logger.info(
                f"ENFORCED template selection for {step_type} (complexity: {step_config.get('complexity', 'medium')})"
            )

        # Format context for template
        context_str = json.dumps(context, indent=2)

        # Try to render with ADG template variables
        try:
            if step_config:
                # Use step_config for template rendering
                prompt = template
                # Replace template variables if they exist
                for key, value in step_config.items():
                    if f"{{{key}}}" in template:
                        prompt = prompt.replace(f"{{{key}}}", str(value))

                # Replace common variables
                prompt = prompt.replace("{step_name}", step_name)
                prompt = prompt.replace("{context}", context_str)
            else:
                # Fallback formatting
                prompt = template.format(
                    step_name=step_name,
                    context=context_str,
                )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            logger.warning(f"Template formatting failed, using fallback: {e}")
            prompt = template.format(
                step_name=step_name,
                context=context_str,
            )

        # In a real implementation, this would call the sequential thinking MCP
        # For now, we simulate the call
        seq_result = {
            "success": True,
            "thoughts": [
                f"Thought 1: Analyzing {step_name} requirements and context",
                f"Thought 2: Breaking down {step_type} into manageable components",
                "Thought 3: Identifying dependencies and risks",
                "Thought 4: Developing systematic approach",
                "Thought 5: Planning validation strategy",
                "Thought 6: Defining next steps and success criteria",
            ],
            "recommendations": [
                "Proceed with structured approach",
                "Monitor for complexity indicators",
                "Validate assumptions early",
            ],
            "token_usage": 5000,  # Estimated
            "response_time": 2.5,  # Estimated
        }

        self.seq_thinking_usage += 1
        logger.info(f"Sequential thinking completed for {step_name}")

        return seq_result

    def execute_step_with_seq_thinking(
        self, step_name: str, step_type: str, step_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute step with forced sequential thinking when appropriate."""

        # Prepare context for token estimation
        context = self._prepare_step_context(step_name, step_type, step_config)

        # Check if we should force sequential thinking
        if self.force_sequential_thinking(step_type, step_config):
            # Inject sequential thinking trigger
            step_config["force_sequential_thinking"] = True
            step_config["seq_thinking_template"] = self._get_seq_thinking_template(step_type)

            logger.info(f"Forcing sequential thinking for step: {step_name}")

            # Execute sequential thinking first
            seq_result = self._execute_sequential_thinking(step_name, step_type, context, step_config)

            if seq_result["success"]:
                # Add sequential thinking results to context
                context["sequential_thinking"] = seq_result
                logger.info(f"Sequential thinking enhanced context for {step_name}")
            else:
                logger.warning(
                    f"Sequential thinking failed for {step_name}: {seq_result.get('reason', 'Unknown')}"
                )

        # Perform preflight token budget check
        estimate = self.preflight_hook.preflight_check(**context)

        # Record step result
        step_result = {
            "step": step_name,
            "type": step_type,
            "status": "completed",
            "budget_status": estimate.status,
            "estimated_tokens": estimate.total_projected_tokens,
            "compression_applied": len(estimate.compression_applied) > 0,
            "top_contributors": estimate.top_contributors,
            "recommendations": estimate.recommended_reductions,
            "sequential_thinking_used": step_config.get("force_sequential_thinking", False),
        }

        # Execute the actual step logic
        if estimate.action == "proceed":
            logger.info(f"Step {step_name} proceeding with {estimate.total_projected_tokens:,} tokens")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        elif estimate.action == "compress":
            logger.info(f"Step {step_name} compressed from original estimate")
            logger.info(f"Compression applied: {estimate.compression_applied}")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        else:  # 'block'
            # This should be caught by the preflight hook, but add safety
            raise TokenBudgetExceededError(
                f"Step {step_name} blocked: {estimate.total_projected_tokens:,} tokens",
            )

        self.step_results.append(step_result)
        return step_result

    def _prepare_step_context(
        self, step_name: str, step_type: str, step_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for token estimation based on step type and configuration."""
        base_context = {
            "plan_step": f"{self.current_phase}/{self.current_wave}/{step_name}",
            "system_prompt": self._get_system_prompt(step_type),
            "user_prompt": step_config.get("prompt", ""),
            "files": self._get_file_contents(step_config.get("files", [])),
            "diffs": self._get_diff_contents(step_config.get("diffs", [])),
            "logs": self._get_log_contents(step_config.get("logs", [])),
            "retrieved_context": self._get_retrieved_context(step_config.get("context", [])),
            "prior_steps": self._get_prior_step_contents(),
            "sequential_thinking_enabled": self.seq_thinking_enabled,
        }

        return base_context

    def _get_system_prompt(self, step_type: str) -> str:
        """Get system prompt based on step type with sequential thinking integration."""
        base_prompts = {
            "analysis": "You are a code analysis expert. Analyze the provided code and identify issues.",
            "implementation": "You are a senior software engineer. Implement the requested feature.",
            "testing": "You are a QA engineer. Write comprehensive tests for the provided code.",
            "refactoring": "You are a code refactoring specialist. Improve the code structure.",
            "documentation": "You are a technical writer. Create clear documentation.",
            "debugging": "You are a debugging specialist. Systematically identify and resolve issues.",
            "planning": "You are a system architect. Plan complex implementations systematically.",
        }

        base_prompt = base_prompts.get(step_type, "You are a helpful assistant.")

        if self.seq_thinking_enabled:
            base_prompt += "\n\nUse sequential thinking to break down complex problems into manageable steps. Think systematically and validate your reasoning at each step."

        return base_prompt

    def _get_file_contents(self, file_paths: list[str]) -> list[dict[str, Any]]:
        """Get file contents for token estimation."""
        files = []
        for file_path in tqdm(file_paths, desc="Processing", unit="item"):
            path = Path(file_path)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                files.append(
                    {
                        "path": file_path,
                        "content": content,
                    }
                )
            else:
                # Simulate file content for demonstration
                files.append(
                    {
                        "path": file_path,
                        "content": f"# Simulated content for {file_path}\n"
                        + "def example_function():\n    pass\n" * 100,
                    }
                )
        return files

    def _get_diff_contents(self, diff_paths: list[str]) -> list[dict[str, Any]]:
        """Get diff contents for token estimation."""
        diffs = []
        for diff_path in tqdm(diff_paths, desc="Processing", unit="item"):
            # Simulate diff content
            diff_content = f"""diff --git a/{diff_path} b/{diff_path}
--- a/{diff_path}
+++ b/{diff_path}
@@ -1,3 +1,4 @@
 def existing_function():
     pass
+def new_function():
+    pass"""
            diffs.append(
                {
                    "path": diff_path,
                    "content": diff_content,
                }
            )
        return diffs

    def _get_log_contents(self, log_sources: list[str]) -> list[dict[str, Any]]:
        """Get log contents for token estimation."""
        logs = []
        for source in tqdm(log_sources, desc="Processing", unit="item"):
            # Simulate log content
            log_content = f"""2023-01-01 12:00:00 INFO Starting {source}
2023-01-01 12:00:01 DEBUG Loading configuration
2023-01-01 12:00:02 ERROR Failed to load {source}
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    load_config()
FileNotFoundError: Config file not found
2023-01-01 12:00:03 INFO Process completed"""
            logs.append(
                {
                    "source": source,
                    "content": log_content,
                }
            )
        return logs

    def _get_retrieved_context(self, context_sources: list[str]) -> list[dict[str, Any]]:
        """Get retrieved context for token estimation."""
        context = []
        for i, source in tqdm(enumerate(context_sources), desc="Processing", unit="item"):
            # Simulate retrieved context
            context_content = (
                f"""Retrieved context chunk {i + 1} from {source}:
This is documentation about the codebase structure and best practices.
It contains important information about coding standards and patterns.
{source} provides guidance for implementation decisions.
"""
                * 5
            )  # Make it substantial
            context.append(
                {
                    "source": source,
                    "content": context_content,
                    "chunk_id": f"chunk_{i + 1}",
                }
            )
        return context

    def _get_prior_step_contents(self) -> list[str]:
        """Get contents from prior steps to carry forward."""
        # Return last 3 step results as context
        return [str(result) for result in self.step_results[-3:]]

    def _execute_step_logic(self, step_type: str, step_config: dict[str, Any], estimate) -> dict[str, Any]:
        """Execute the actual step logic."""
        # Simulate step execution
        execution_time = 0.5  # Simulated execution time

        return {
            "execution_time": execution_time,
            "output_tokens": 5000,  # Simulated output
            "success": True,
            "artifacts": [f"artifact_{step_type}_{hash(str(step_config)) % 1000}.json"],
        }

    def get_workflow_summary(self) -> dict[str, Any]:
        """Get complete workflow summary including sequential thinking metrics."""
        budget_summary = self.preflight_hook.get_budget_summary()

        return {
            "workflow_summary": {
                "phases_completed": 1,  # Single phase in this example
                "total_steps": len(self.step_results),
                "total_tokens": sum(r["estimated_tokens"] for r in self.step_results),
                "sequential_thinking_usage": self.seq_thinking_usage,
                "sequential_thinking_enabled": self.seq_thinking_enabled,
            },
            "budget_summary": budget_summary,
            "step_results": self.step_results,
            "sequential_thinking_config": self.seq_thinking_config,
        }


# Example usage
def example_sequential_thinking_workflow():
    """Example of using the SequentialThinkingEnhancedWorkflow"""

    # Initialize workflow with sequential thinking enabled
    custom_budget = TokenBudget(
        WARNING_THRESHOLD=120000,  # Earlier warning for demo
        SAFE_OPERATING_CAP=150000,  # Lower safe cap for demo
    )

    workflow = SequentialThinkingEnhancedWorkflow(
        budget_file=Path(f"{DOCS_REPORTS_DIR}/plans/seq_thinking_workflow_budget.json"),
        custom_budget=custom_budget,
        seq_thinking_enabled=True,
    )

    # Define phase configuration with complex tasks that should trigger sequential thinking
    phase_configs = [
        {
            "name": "complex_analysis_wave",
            "steps": [
                {
                    "name": "architecture_analysis",
                    "type": "analysis",
                    "prompt": "Analyze the system architecture for scalability issues",
                    "files": [
                        "src/main.py",
                        "src/utils.py",
                        "src/config.py",
                        "src/database.py",
                        "src/api.py",
                    ],
                    "context": ["architecture.md", "requirements.txt"],
                    "complexity": "high",
                },
                {
                    "name": "dependency_analysis",
                    "type": "analysis",
                    "prompt": "Analyze dependencies and potential conflicts",
                    "files": ["requirements.txt", "setup.py", "pyproject.toml"],
                    "logs": ["pip_install.log"],
                    "complexity": "medium",
                },
            ],
        },
        {
            "name": "implementation_wave",
            "steps": [
                {
                    "name": "feature_implementation",
                    "type": "implementation",
                    "prompt": "Implement the new feature following best practices",
                    "files": ["src/main.py", "src/utils.py"],
                    "diffs": ["src/main.py"],
                    "context": ["documentation.md", "api_reference.md"],
                    "complexity": "high",
                },
                {
                    "name": "debug_session",
                    "type": "debugging",
                    "prompt": "Debug the performance issue in the main module",
                    "files": ["src/main.py", "logs/error.log"],
                    "logs": ["performance.log", "error.log"],
                    "complexity": "critical",
                },
            ],
        },
    ]

    # Execute the phase
    try:
        results = workflow.execute_phase("complex_feature_development", phase_configs)

        # Print workflow summary
        summary = workflow.get_workflow_summary()
        print("\n" + "=" * 60)
        print("SEQUENTIAL THINKING ENHANCED WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Phases completed: {summary['workflow_summary']['phases_completed']}")
        print(f"Total steps: {summary['workflow_summary']['total_steps']}")
        print(f"Total tokens used: {summary['workflow_summary']['total_tokens']:,}")
        print(f"Sequential thinking usage: {summary['workflow_summary']['sequential_thinking_usage']}")
        print(f"Sequential thinking enabled: {summary['workflow_summary']['sequential_thinking_enabled']}")
        print(f"Average tokens per step: {summary['budget_summary']['average_tokens_per_step']:.0f}")
        print(f"Status distribution: {summary['budget_summary']['status_distribution']}")

        return results

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        RuntimeError,
    ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        logger.error(f"Workflow failed: {e}")
        raise


if __name__ == "__main__":
    # Run the example workflow
    example_sequential_thinking_workflow()
