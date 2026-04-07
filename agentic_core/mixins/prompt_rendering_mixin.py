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

from typing import Any

# Import TemplateCategory at module level since it's used in class definition
from agentic_core.prompt_governance.core.template_catalog import TemplateCategory


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
        self, category: TemplateCategory = TemplateCategory.INSTRUCTIONAL,
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
                    f"Assign one via TEMPLATE_CATALOG or pass template_name explicitly.",
                )
            template_name = entry.template_name

        return self.render_template(template_name, context=context, validate=False)
