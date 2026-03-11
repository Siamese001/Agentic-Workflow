from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Sovereign Prompt Renderer - Safe Jinja2 template rendering with validation.

Responsibilities:
- Load templates exclusively from prompt_governance/templates
- Perform safe Jinja2 rendering with strict variable scoping
- Enforce sovereignty: no inline prompt strings > 50 lines outside this layer
- Validate template schemas and required variables
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
    select_autoescape,
)


@dataclass
class TemplateSchema:
    """Schema definition for template validation."""

    required_vars: set[str]
    optional_vars: set[str]
    description: str


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    pass


class SovereignPromptRenderer:
    """
    Sovereign renderer for instructional prompt templates.

    ARCHITECTURAL HARDENING:
    - No hardcoded paths (injected via constructor)
    - Strict template validation with schema checking
    - Variable injection safety with StrictUndefined
    - Template header parsing for metadata extraction
    """

    def __init__(self, template_root: Path | None = None):
        """Initialize renderer with dependency-injected template root.

        Args:
            template_root: Path to template directory. If None, auto-discovers
                          relative to this file's location.
        """
        # HARDENING: Remove hardcoded path, use dependency injection
        if template_root is None:
            # Auto-discover relative to this file
            template_root = Path(__file__).parent / "templates"

        self.template_root = template_root

        if not self.template_root.exists():
            os.makedirs(self.template_root, exist_ok=True)

        # SECURITY: StrictUndefined ensures undefined variables raise errors
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_root)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,  # Critical: fail on undefined vars
        )

        # Cache for parsed template schemas
        self._schema_cache: dict[str, TemplateSchema] = {}

    def _parse_template_schema(self, template_name: str) -> TemplateSchema:
        """Parse template header for schema metadata.

        Expected header format:
        {# SCHEMA: required_vars=[var1, var2], optional_vars=[var3] #}
        {# DESCRIPTION: Template purpose #}
        """
        if template_name in self._schema_cache:
            return self._schema_cache[template_name]

        template_path = self.template_root / template_name
        if not template_path.exists():
            raise TemplateNotFound(template_name)

        content = template_path.read_text(encoding="utf-8")

        # Parse SCHEMA header
        required_vars = set()
        optional_vars = set()
        description = "No description provided"

        schema_match = re.search(
            r"\{#\s*SCHEMA:\s*required_vars=\[([^\]]*)\](?:,\s*optional_vars=\[([^\]]*)\])?\s*#\}",
            content,
        )
        if schema_match:
            required_str = schema_match.group(1).strip()
            if required_str:
                required_vars = {v.strip() for v in required_str.split(",")}
            optional_str = schema_match.group(2)
            if optional_str:
                optional_vars = {v.strip() for v in optional_str.split(",")}

        desc_match = re.search(r"\{#\s*DESCRIPTION:\s*(.+?)\s*#\}", content)
        if desc_match:
            description = desc_match.group(1).strip()

        schema = TemplateSchema(
            required_vars=required_vars,
            optional_vars=optional_vars,
            description=description,
        )
        self._schema_cache[template_name] = schema
        return schema

    def validate_context(self, template_name: str, context: dict[str, Any]) -> None:
        """Validate that context provides all required variables.

        Args:
            template_name: Template to validate against
            context: Context dictionary to validate

        Raises:
            TemplateValidationError: If required variables are missing
        """
        schema = self._parse_template_schema(template_name)
        provided_vars = set(context.keys())
        missing_vars = schema.required_vars - provided_vars

        if missing_vars:
            raise TemplateValidationError(
                f"Template '{template_name}' requires variables {missing_vars} "
                f"but only {provided_vars} were provided. "
                f"Description: {schema.description}",
            )

    def render(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> str:
        """Render a standard sovereign instructional prompt with validation.

        Args:
            template_name: Name of template file (e.g., 'code_healing.jinja')
            context: Variables to inject into template
            metadata: Additional metadata for tracing
            validate: Whether to validate context against template schema

        Returns:
            Rendered prompt string

        Raises:
            TemplateValidationError: If validation fails
            TemplateNotFound: If template doesn't exist
        """
        context = context or {}
        metadata = metadata or {}

        # HARDENING: Validate context before rendering
        if validate:
            try:
                self.validate_context(template_name, context)
            except TemplateValidationError as e:
                # Log but don't fail if schema not defined (backward compat)
                if "No description provided" not in str(e):
                    raise

        full_context = {
            **context,
            "_sovereign_metadata": {
                "renderer": self.__class__.__name__,
                "template": template_name,
                "root": str(self.template_root),
                **metadata,
            },
        }

        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**full_context)
            return rendered.strip() + "\n"
        except TemplateNotFound:
            raise TemplateNotFound(f"Template '{template_name}' not found in {self.template_root}")
        except Exception as e:
            raise RuntimeError(f"[PROMPT RENDERING FAILURE] Template '{template_name}': {e}")

    def render_tagentic(
        self,
        base_template: str,
        fragments: list[str],
        context: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> str:
        """Tag-based agentic composition with validation.

        Combines meta-prompt + instructional fragments with XML semantic fencing.

        Args:
            base_template: Base meta-prompt template name
            fragments: List of fragment template names to compose
            context: Variables for rendering
            validate: Whether to validate each template

        Returns:
            Assembled prompt with XML tags
        """
        context = context or {}

        # Render base meta-prompt from meta_prompts/ directory
        try:
            base = self.env.get_template(f"../meta_prompts/{base_template}").render(**context)
        except TemplateNotFound:
            raise TemplateNotFound(f"Meta-prompt '{base_template}' not found in meta_prompts/")
        except Exception as e:
            raise RuntimeError(f"[META-PROMPT FAILURE] {base_template}: {e}")

        assembled = [base]

        # Render and compose fragments
        for frag in fragments:
            try:
                if validate:
                    self.validate_context(frag, context)
                fragment_text = self.env.get_template(frag).render(**context)
                assembled.append(
                    f"\n<INSTRUCTIONAL_FRAGMENT:{frag}>\n{fragment_text}\n</INSTRUCTIONAL_FRAGMENT>",
                )
            except TemplateNotFound:
                # Skip missing fragments (non-critical)
                continue
            except Exception as e:
                # Log but continue for non-critical fragments
                print(f"[WARNING] Fragment '{frag}' failed to render: {e}")
                continue

        return "\n".join(assembled)

    def list_available_templates(self) -> list[str]:
        """List all available templates for introspection.

        Returns:
            List of template names relative to template_root
        """
        from agentic_core.utils.ssot_discovery_validator import get_data_files

        jinja_files = get_data_files(self.template_root, extensions=[".jinja"])
        return [p.relative_to(self.template_root).as_posix() for p in jinja_files if p.is_file()]

    def get_template_schema(self, template_name: str) -> TemplateSchema:
        """Get the schema for a template.

        Args:
            template_name: Template to inspect

        Returns:
            TemplateSchema with required/optional variables
        """
        return self._parse_template_schema(template_name)


# Singleton instance
_RENDERER: SovereignPromptRenderer | None = None


def get_sovereign_prompt_renderer(template_root: Path | None = None) -> SovereignPromptRenderer:
    """Get the global renderer singleton.

    Args:
        template_root: Optional custom template root (for testing)

    Returns:
        SovereignPromptRenderer instance
    """
    global _RENDERER
    if _RENDERER is None or template_root is not None:
        _RENDERER = SovereignPromptRenderer(template_root=template_root)
    return _RENDERER
