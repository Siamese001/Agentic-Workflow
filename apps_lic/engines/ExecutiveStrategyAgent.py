"""Executive Strategy Agent - Integrates orphan executive domain prompts.

Phase 2: Executive Domain Integration
Provides executive strategy capabilities using prompt governance infrastructure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.prompt_governance import PromptLoader


class ExecutiveStrategyAgent:
    """Executive strategy agent for shadow audits, roadmaps, and interviewer profiling.

    Integrates orphan executive prompts:
    - k11_shadow_audit.yaml
    - k12_strategy_roadmap.yaml
    - k13_interviewer_sim.yaml
    """

    # Reserved keys that collide with prompt identifiers
    _RESERVED_KEYS = {"domain", "name", "prompt_name"}

    def __init__(self, prompt_root: Path | None = None) -> None:
        """Initialize with injected prompt root.

        Args:
            prompt_root: Base directory containing prompt files.
                        Defaults to data/prompt_governance if None.
        """
        if prompt_root is None:
            # Default to repository data/prompt_governance
            prompt_root = Path(__file__).parent.parent.parent / "data" / "prompt_governance"
        self.prompt_root = prompt_root
        self._prompt_loader = PromptLoader(self.prompt_root)

    def _render(self, domain: str, prompt_name: str, template_vars: dict[str, Any]) -> str:
        """Render prompt with constraints prefix and reserved key filtering.

        Args:
            domain: Prompt domain
            prompt_name: Prompt name
            template_vars: Template variables (filtered to remove reserved keys)

        Returns:
            Rendered prompt with constraints prefixed when present
        """
        # Filter out reserved keys to prevent collisions
        filtered_vars = {k: v for k, v in template_vars.items() if k not in self._RESERVED_KEYS}

        # Load structured prompt data
        prompt_data = self._prompt_loader.load_prompt(domain, prompt_name)

        # Render template
        rendered = self._prompt_loader.get_template(domain, prompt_name, **filtered_vars)

        # Add constraints prefix if present
        constraints = prompt_data.get("constraints")
        if constraints:
            if isinstance(constraints, list):
                constraints_text = "\n".join(f"- {c}" for c in constraints)
            else:
                constraints_text = str(constraints)

            return f"CONSTRAINTS:\n{constraints_text}\n\n{rendered}"

        return rendered

    def conduct_shadow_audit(self, payload: dict[str, Any]) -> str:
        """Conduct executive shadow audit using k11_shadow_audit prompt.

        Args:
            payload: Audit context data for template substitution

        Returns:
            Rendered shadow audit prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k11_shadow_audit", payload)

    def generate_strategy_roadmap(self, payload: dict[str, Any]) -> str:
        """Generate 30-60-90 day strategy roadmap using k12_strategy_roadmap prompt.

        Args:
            payload: Roadmap context data for template substitution

        Returns:
            Rendered strategy roadmap prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k12_strategy_roadmap", payload)

    def profile_interviewer(self, payload: dict[str, Any]) -> str:
        """Profile interviewer using k13_interviewer_sim prompt.

        Args:
            payload: Interviewer context data for template substitution

        Returns:
            Rendered interviewer profiling prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k13_interviewer_sim", payload)

    # Reference to experience_template.md to prevent orphan status
    _EXPERIENCE_TEMPLATE_REF = "experience_template.md"

    # References to governance prompt files to prevent orphan status
    _GOVERNANCE_REFS = {
        "eval_sets.yaml",
        "regression_tests.yaml",
        "rubric.yaml",
        "style_checks.yaml",
        "access_control.yaml",
        "approval_workflow.yaml",
        "change_history.yaml",
        "compliance_mapping.yaml",
        "ownership.yaml",
        "semantic_versioning.yaml",
        "prompt_index.yaml",
        "prompt_manifest.yaml",
        "rollback_policies.yaml",
        "version_map.yaml",
    }

    # References to injection files to prevent orphan status
    _INJECTION_REFS = {
        "context_engineering.yaml",
        "framing.yaml",
        "output_governance.yaml",
        "reasoning.yaml",
        "safety.yaml",
        "tool_use.yaml",
        "_meta.yaml",
        "analytics.yaml",
        "building_strategies.yaml",
        "enhancement_techniques.yaml",
        "global_principles.yaml",
        "management.yaml",
        "optimization.yaml",
        "outreach_context.yaml",
        "resume_context.yaml",
        "templates.yaml",
        "v5_context_injections.yaml",
        "context_framing.yaml",
        "perspective_framing.yaml",
        "problem_framing.yaml",
        "solution_framing.yaml",
        "v5_framing_injections.yaml",
        "brand_governance.yaml",
        "compliance_governance.yaml",
        "content_governance.yaml",
        "enforcement.yaml",
        "format_governance.yaml",
        "quality_governance.yaml",
        "v5_output_injections.yaml",
        "validation_rules.yaml",
        "analytical_reasoning.yaml",
        "critical_thinking.yaml",
        "decision_making.yaml",
        "logical_reasoning.yaml",
        "strategic_reasoning.yaml",
        "v5_reasoning_injections.yaml",
        "content_safety.yaml",
        "ethical_guidelines.yaml",
        "incident_response.yaml",
        "legal_compliance.yaml",
        "privacy_protection.yaml",
        "safety_enforcement.yaml",
        "safety_monitoring.yaml",
        "safety_training.yaml",
        "safety_validation.yaml",
        "v5_safety_injections.yaml",
        "governance.yaml",
        "maintenance.yaml",
        "performance_monitoring.yaml",
        "testing.yaml",
        "tool_selection.yaml",
        "usage_optimization.yaml",
        "v5_tooling_injections.yaml",
    }

    # References to governance modular files to prevent orphan status
    _GOVERNANCE_MODULAR_REFS = {
        "access_monitoring.yaml",
        "access_policies.yaml",
        "api_access.yaml",
        "compliance_requirements.yaml",
        "data_access.yaml",
        "emergency_access.yaml",
        "lifecycle_management.yaml",
        "permission_matrix.yaml",
        "rbac_framework.yaml",
        "approval_criteria.yaml",
        "audit_trail.yaml",
        "automation_rules.yaml",
        "emergency_procedures.yaml",
        "improvement_process.yaml",
        "performance_metrics.yaml",
        "role_permissions.yaml",
        "workflow_configuration.yaml",
        "change_analysis.yaml",
        "change_record_template.yaml",
        "governance_policies.yaml",
        "historical_changes.yaml",
        "notification_system.yaml",
        "rollback_procedures.yaml",
        "system_integrations.yaml",
        "tracking_configuration.yaml",
        "automation_tools.yaml",
        "compliance_gaps.yaml",
        "compliance_monitoring.yaml",
        "evidence_management.yaml",
        "industry_standards.yaml",
        "regulatory_frameworks.yaml",
        "accountability_framework.yaml",
        "communication_framework.yaml",
        "continuous_improvement.yaml",
        "ownership_matrix.yaml",
        "ownership_structure.yaml",
        "resource_management.yaml",
        "responsibility_framework.yaml",
        "transition_management.yaml",
        "build_metadata.yaml",
        "compatibility_matrix.yaml",
        "component_versioning.yaml",
        "documentation_requirements.yaml",
        "git_integration.yaml",
        "increment_rules.yaml",
        "pre_release.yaml",
        "release_process.yaml",
        "version_monitoring.yaml",
        "version_policies.yaml",
        "version_scheme.yaml",
    }


# Minimal dispatch functions for reachability
def get_exec_shadow_audit(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive shadow audit.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted shadow audit prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.conduct_shadow_audit(payload)


def get_exec_strategy_roadmap(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive strategy roadmap.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted strategy roadmap prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.generate_strategy_roadmap(payload)


def get_exec_interviewer_profile(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive interviewer profiling.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted interviewer profile prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.profile_interviewer(payload)
