"""
Render templates for prompt governance.

This module provides template rendering functionality for generating
prompts from templates with variable substitution.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateVariable:
    """Definition of a template variable."""

    name: str
    description: str
    required: bool = True
    default_value: Optional[str] = None


@dataclass
class PromptTemplate:
    """Definition of a prompt template."""

    template_id: str
    name: str
    content: str
    variables: List[TemplateVariable] = field(default_factory=list)


@dataclass
class RenderResult:
    """Result from rendering a template."""

    success: bool
    rendered_content: str
    missing_variables: List[str]
    message: str


class TemplateRenderer:
    """Renderer for prompt templates."""

    def __init__(self) -> None:
        """Initialize the template renderer."""
        self._templates: Dict[str, PromptTemplate] = {}

    def register_template(self, template: PromptTemplate) -> None:
        """Register a prompt template."""
        self._templates[template.template_id] = template

    def render(
        self,
        template_id: str,
        context: Dict[str, str],
    ) -> RenderResult:
        """Render a template with the given context."""
        template = self._templates.get(template_id)
        if template is None:
            return RenderResult(
                success=False,
                rendered_content="",
                missing_variables=[],
                message=f"Template not found: {template_id}",
            )

        missing: List[str] = []
        rendered = template.content

        for var in template.variables:
            if var.name in context:
                rendered = rendered.replace(f"{{{var.name}}}", context[var.name])
            elif var.default_value is not None:
                rendered = rendered.replace(f"{{{var.name}}}", var.default_value)
            elif var.required:
                missing.append(var.name)

        if missing:
            return RenderResult(
                success=False,
                rendered_content=rendered,
                missing_variables=missing,
                message=f"Missing required variables: {missing}",
            )

        return RenderResult(
            success=True,
            rendered_content=rendered,
            missing_variables=[],
            message="Template rendered successfully",
        )

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self) -> List[str]:
        """List all registered template IDs."""
        return list(self._templates.keys())


def create_template_renderer() -> TemplateRenderer:
    """Factory function to create a template renderer."""
    return TemplateRenderer()


def render_template(
    template: PromptTemplate,
    context: Dict[str, str],
) -> RenderResult:
    """Render a single template with the given context."""
    renderer = TemplateRenderer()
    renderer.register_template(template)
    return renderer.render(template.template_id, context)
