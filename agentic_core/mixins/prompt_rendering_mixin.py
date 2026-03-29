"""
PromptRenderingMixin — Wires agents to the Jinja2 prompt governance system.

Provides agents with:
1. render_template() — Renders assigned Jinja templates via SovereignPromptRenderer
2. get_assigned_templates() — Discovers templates assigned to this agent via template_catalog
3. build_healing_prompt() — Renders the agent's primary template with healing context

This mixin bridges the gap between agents and the prompt governance system.
Without it, agents construct prompts as raw strings, bypassing template governance,
schema validation, and the D0 injection fence.
"""

from __future__ import annotations

import logging
from typing import Any

# Lazy imports to avoid L_SHARED->L_PG gravity violations
def _get_prompt_renderer():
    from agentic_core.prompt_governance.core.sovereign_prompt_renderer import (
        SovereignPromptRenderer,
    )
    return SovereignPromptRenderer

def _get_template_catalog():
    from agentic_core.prompt_governance.core.template_catalog import (
        TEMPLATE_CATALOG,
        TemplateCatalogEntry,
        TemplateCategory,
        TemplateStatus,
    )
    return TEMPLATE_CATALOG, TemplateCatalogEntry, TemplateCategory, TemplateStatus

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)


class PromptRenderingMixin:
    """Mixin that wires any agent into the Jinja2 prompt governance system.

    Usage:
        class MyAgent(PromptRenderingMixin, SovereignBaseAgent):
            def heal_repository(self, ...):
                prompt = self.render_template(
                    "code_healing.jinja",
                    context={"violations": violations, "code_block": code},
                )
                return self.llm_call(prompt)
    """

    _prompt_renderer: SovereignPromptRenderer | None = None
    _assigned_templates: list[TemplateCatalogEntry] | None = None

    @property
    def prompt_renderer(self) -> SovereignPromptRenderer:
        """Lazy-initialize the sovereign prompt renderer."""
        if self._prompt_renderer is None:
            self._prompt_renderer = SovereignPromptRenderer()
        return self._prompt_renderer

    def get_assigned_templates(self) -> list[TemplateCatalogEntry]:
        """Discover templates assigned to this agent class via template_catalog.

        Returns:
            List of TemplateCatalogEntry for templates assigned to this agent.
        """
        if self._assigned_templates is not None:
            return self._assigned_templates

        agent_name = type(self).__name__
        self._assigned_templates = [
            entry
            for entry in TEMPLATE_CATALOG
            if agent_name in entry.consumer_agents and entry.status == TemplateStatus.ACTIVE
        ]
        return self._assigned_templates

    def get_primary_template(
        self, category: TemplateCategory = TemplateCategory.INSTRUCTIONAL
    ) -> TemplateCatalogEntry | None:
        """Get the first assigned template of a given category.

        Args:
            category: Template category to filter by.

        Returns:
            The first matching TemplateCatalogEntry, or None.
        """
        for entry in self.get_assigned_templates():
            if entry.category == category:
                return entry
        return None

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> str:
        """Render a Jinja template through the sovereign prompt renderer.

        Args:
            template_name: Template filename (e.g. "code_healing.jinja")
            context: Template variables dict
            validate: Whether to validate context against template schema

        Returns:
            Rendered prompt string

        Raises:
            RuntimeError: If template rendering fails
        """
        agent_name = type(self).__name__
        logger.debug("Agent %s rendering template %s", agent_name, template_name)
        return self.prompt_renderer.render(
            template_name=template_name,
            context=context,
            validate=validate,
        )

    def build_healing_prompt(
        self,
        context: dict[str, Any],
        template_name: str | None = None,
    ) -> str:
        """Build a healing prompt using this agent's assigned template.

        If template_name is not provided, uses the primary INSTRUCTIONAL template
        from the template_catalog.

        Args:
            context: Template variables for rendering
            template_name: Override template name (optional)

        Returns:
            Rendered healing prompt string

        Raises:
            ValueError: If no template is assigned to this agent
            RuntimeError: If rendering fails
        """
        if template_name is None:
            entry = self.get_primary_template()
            if entry is None:
                agent_name = type(self).__name__
                raise ValueError(
                    f"No INSTRUCTIONAL template assigned to {agent_name} in template_catalog. "
                    f"Assign one via TEMPLATE_CATALOG or pass template_name explicitly."
                )
            template_name = entry.template_name

        return self.render_template(template_name, context=context, validate=False)
