"""
Template Loader

Loads templates by category, detects slot codes from filenames,
and provides template content for slot assembly.
"""

import re
from pathlib import Path
from string import Template as StringTemplate
from typing import Any

try:
    import jinja2

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

from agentic_core.L2_execution.reasoning import (
    AuthoritySlot,
)  # guardian: allow-layer-violation -- L1 module uses L2 type/utility; intentional cross-layer dependency in cognition layer

from .categories import (
    CategoryRegistryEntry,
    CategoryTemplate,
    PromptCategory,
    PromptCategoryRegistry,
    get_default_template_path,
)


class TemplateLoadError(Exception):
    """Raised when template loading fails."""

    pass


class TemplateLoader:
    """
    Loads prompt templates by category or slot code.

    Supports both Jinja2 and string.Template formats.
    Detects category from filename prefix (S0_, I0_, D0_, C0_, U0_).
    """

    SLOT_PREFIX_PATTERN = re.compile(r"^([SDICU]0)_(.+)$")

    def __init__(self, template_dir: Path | None = None) -> None:
        if template_dir is None:
            # Default to package templates directory
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = Path(template_dir)
        self.registry = PromptCategoryRegistry()
        self._jinja_env: Any | None = None

        if JINJA2_AVAILABLE and self.template_dir.exists():
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(self.template_dir)),
                autoescape=False,
            )

    def load_template_file(self, path: Path) -> str:
        """Load template content from file."""
        if not path.exists():
            raise TemplateLoadError(f"Template file not found: {path}")
        return path.read_text(encoding="utf-8")

    def detect_category_from_filename(self, filename: str) -> PromptCategory | None:
        """
        Detect prompt category from filename prefix.

        Format: {S0|I0|D0|C0|U0}_{category_snake}.{ext}
        Examples:
        - S0_system_state.j2 -> PromptCategory.SYSTEM_STATE
        - I0_instructional.j2 -> PromptCategory.INSTRUCTIONAL
        - D0_injections.j2 -> PromptCategory.INJECTIONS
        """
        # Remove extension
        base = Path(filename).stem

        # Match slot prefix
        match = self.SLOT_PREFIX_PATTERN.match(base)
        if not match:
            return None

        slot_code, category_snake = match.groups()

        # Map category_snake to PromptCategory
        name_map = {
            "user_prompt": PromptCategory.USER_PROMPT,
            "instructional": PromptCategory.INSTRUCTIONAL,
            "injections": PromptCategory.INJECTIONS,
            "exemplars": PromptCategory.EXEMPLARS,
            "dependency": PromptCategory.DEPENDENCY,
            "meta_cognitive": PromptCategory.META_COGNITIVE,
            "synthesis": PromptCategory.SYNTHESIS,
            "system_state": PromptCategory.SYSTEM_STATE,
            "healing_proposal": PromptCategory.HEALING_PROPOSAL,
        }

        return name_map.get(category_snake.lower())

    def load_category_template(
        self,
        category: PromptCategory,
        custom_path: Path | None = None,
        **variables: Any,
    ) -> CategoryTemplate:
        """
        Load template for a specific category.

        Args:
            category: The prompt category
            custom_path: Optional custom template path
            **variables: Template variables for rendering

        Returns:
            CategoryTemplate with loaded content
        """
        # Determine template path
        if custom_path:
            template_path = custom_path
        else:
            default_path = get_default_template_path(category)
            template_path = self.template_dir / default_path

        # Load content
        if template_path.exists():
            content = self.load_template_file(template_path)
        else:
            # Use default content if file doesn't exist
            content = self._get_default_content(category)

        # Render template with variables
        rendered = self._render_template(content, variables)

        # Create CategoryTemplate
        return CategoryTemplate(
            category=category,
            template_id=f"{category.slot_code}_{category.name.lower()}",
            template_path=str(template_path.relative_to(self.template_dir)) if template_path.exists() else "",
            required_variables=self._extract_variables(content),
        )

    def load_all_templates(self) -> PromptCategoryRegistry:
        """Load all templates from template directory."""
        if not self.template_dir.exists():
            return self.registry

        for file_path in self.template_dir.glob("*.j2"):
            category = self.detect_category_from_filename(file_path.name)
            if category:
                template = self.load_category_template(category, file_path)
                entry = CategoryRegistryEntry(
                    category=category,
                    template=template,
                    loaded_content=self.load_template_file(file_path),
                )
                self.registry.register(entry)

        return self.registry

    def to_authority_slot(
        self,
        category: PromptCategory,
        variables: dict[str, Any],
        source_layer: str = "L4",
    ) -> AuthoritySlot:
        """
        Load template and convert directly to AuthoritySlot.

        Args:
            category: Prompt category
            variables: Template variables
            source_layer: Layer that provided this slot

        Returns:
            AuthoritySlot ready for assembly
        """
        template = self.load_category_template(category, **variables)
        return template.to_slot(template.loaded_content or "", source_layer)

    def _render_template(self, content: str, variables: dict[str, Any]) -> str:
        """Render template with variables."""
        if JINJA2_AVAILABLE and self._jinja_env:
            try:
                template = self._jinja_env.from_string(content)
                return template.render(**variables)
            except jinja2.TemplateError as e:
                # Fall back to string.Template
                import logging

                logging.getLogger(__name__).debug("loader: Exception swallowed at L182: %s", e)

        # Use string.Template as fallback
        return StringTemplate(content).safe_substitute(variables)

    def _extract_variables(self, content: str) -> list[str]:
        """Extract variable names from template content."""
        variables = set()

        # Jinja2 style: {{ var }} or {{ var|filter }}
        jinja_pattern = re.compile(r"\{\{\s*(\w+)")
        for match in jinja_pattern.finditer(content):
            variables.add(match.group(1))

        # String.Template style: $var or ${var}
        string_pattern = re.compile(r"\$\{?(\w+)\}?")
        for match in string_pattern.finditer(content):
            variables.add(match.group(1))

        return sorted(variables)

    def _get_default_content(self, category: PromptCategory) -> str:
        """Get default template content for a category."""
        defaults = {
            PromptCategory.SYSTEM_STATE: "System state: ABSOLUTE rules apply.",
            PromptCategory.INSTRUCTIONAL: "Identity: Governed capabilities.",
            PromptCategory.INJECTIONS: "Constraints: BINDING fences.",
            PromptCategory.EXEMPLARS: "Example: {{ example_input }} -> {{ example_output }}",
            PromptCategory.DEPENDENCY: "Context: {{ context_data }}",
            PromptCategory.META_COGNITIVE: "Think through: {{ reasoning_task }}",
            PromptCategory.SYNTHESIS: "Synthesize: {{ telemetry_data }}",
            PromptCategory.USER_PROMPT: "{{ user_intent }}",
            PromptCategory.HEALING_PROPOSAL: "Healing proposal: {{ correction_plan }}",
        }
        return defaults.get(category, "")


class TemplateLoaderFactory:
    """Factory for creating TemplateLoader instances."""

    @staticmethod
    def create(template_dir: Path | None = None) -> TemplateLoader:
        """Create a new TemplateLoader."""
        return TemplateLoader(template_dir)

    @staticmethod
    def create_with_registry(
        template_dir: Path | None = None,
    ) -> tuple[TemplateLoader, PromptCategoryRegistry]:
        """Create a TemplateLoader and load all templates into registry."""
        loader = TemplateLoader(template_dir)
        registry = loader.load_all_templates()
        return loader, registry
