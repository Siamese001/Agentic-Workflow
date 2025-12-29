# SovereignPromptRenderer - L3 Orchestration Layer (Prompt Assembly)
# Territory: agentic_core/prompt_governance/rendering
# Canon Key 1 - Prompt templates & governance

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

from agentic_core.runtime.shared_runtime.void_compliance import validate_file_location

class SovereignPromptRenderer:
    """
    Sovereign renderer for instructional prompt templates.

    Responsibilities (per blueprint Section 8):
    - Load templates exclusively from prompt_governance/templates
    - Perform safe Jinja2 rendering with strict variable scoping
    - Enforce sovereignty: no inline prompt strings > 50 lines outside this layer
    - Provide typed context injection for downstream agents
    """

    # Anchored to the hard-coded Git root established in previous hardening steps
    TEMPLATE_ROOT = Path(r"C:\Git\Agentic-Workflow\agentic_core\prompt_governance\templates")

    def __init__(self):
        if not self.TEMPLATE_ROOT.exists():
            os.makedirs(self.TEMPLATE_ROOT, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(self.TEMPLATE_ROOT)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined
        )

    def render(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a sovereign instructional prompt with metadata traceability.
        """
        context = context or {}
        metadata = metadata or {}

        # Inject sovereign metadata for L4 Ledger traceability
        full_context = {
            **context,
            "_sovereign_metadata": {
                "renderer": self.__class__.__name__,
                "template": template_name,
                "root": str(self.TEMPLATE_ROOT),
                **metadata,
            }
        }

        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**full_context)
            return rendered.strip() + "\n"
        except Exception as e:
            raise RuntimeError(f"[PROMPT RENDERING FAILURE] Template '{template_name}': {e}")

    @staticmethod
    def list_available_templates() -> list[str]:
        """Utility for introspection and MCP routing."""
        root = SovereignPromptRenderer.TEMPLATE_ROOT
        return [
            p.relative_to(root).as_posix()
            for p in root.rglob("*.jinja")
            if p.is_file()
        ]

# Factory for downstream dependency injection
def get_sovereign_prompt_renderer() -> SovereignPromptRenderer:
    return SovereignPromptRenderer()
