from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

# Import for semantic deduplication awareness
from agentic_core.prompt_governance.version_registry.PromptRegistry import get_prompt_registry, DuplicatePromptError

# [PHASE 20] DEPRECATION: void_compliance.py removed - using LocationAgent
def validate_file_location(file_path, project_root):
    """Bridge to LocationAgent."""
    from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
    return LocationAgent(project_root).validate_file_location(file_path)

class SovereignPromptRenderer:
    """
    Sovereign renderer for instructional prompt templates.

    Responsibilities (per blueprint Section 8):
    - Load templates exclusively from prompt_governance/templates
    - Perform safe Jinja2 rendering with strict variable scoping
    - Enforce sovereignty: no inline prompt strings > 50 lines outside this layer
    - Provide typed context injection for downstream agents
    """
    TEMPLATE_ROOT: Any = Path('C:\\Git\\Agentic-Workflow\\agentic_core\\prompt_governance\\templates')

    def __init__(self):
        if not self.TEMPLATE_ROOT.exists():
            os.makedirs(self.TEMPLATE_ROOT, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(str(self.TEMPLATE_ROOT)), autoescape=select_autoescape(['html', 'xml']), trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True, undefined=StrictUndefined)

    def render(self, template_name: str, context: Optional[Dict[str, Any]]=None, metadata: Optional[Dict[str, Any]]=None) -> str:
        """
        Render a standard sovereign instructional prompt.
        """
        context: Any = context or {}
        metadata: Any = metadata or {}
        full_context: Any = {**context, '_sovereign_metadata': {'renderer': self.__class__.__name__, 'template': template_name, 'root': str(self.TEMPLATE_ROOT), **metadata}}
        try:
            template: Any = self.env.get_template(template_name)
            rendered: Any = template.render(**full_context)
            return rendered.strip() + '\n'
        except Exception as e:
            raise RuntimeError(f"[PROMPT RENDERING FAILURE] Template '{template_name}': {e}")

    def render_tagentic(self, base_template: str, fragments: List[str], context: Optional[Dict[str, Any]]=None) -> str:
        """
        Tag-based agentic composition: combine meta-prompt + instructional fragments.
        Provides clear architectural cues for high-precision CoT.
        """
        context: Any = context or {}
        try:
            base: Any = self.env.get_template(f'../meta_prompts/{base_template}').render(**context)
        except Exception as e:
            raise RuntimeError(f'[META-PROMPT FAILURE] {base_template}: {e}')
        assembled: Any = [base]
        for frag in fragments:
            try:
                fragment_text: Any = self.env.get_template(frag).render(**context)
                assembled.append(f'\n<INSTRUCTIONAL_FRAGMENT:{frag}>\n{fragment_text}\n</INSTRUCTIONAL_FRAGMENT>')
            except Exception:
                continue
        return '\n'.join(assembled)

    @staticmethod
    def list_available_templates() -> list[str]:
        """Utility for introspection and MCP routing."""
        root: Any = SovereignPromptRenderer.TEMPLATE_ROOT
        return [p.relative_to(root).as_posix() for p in root.rglob('*.jinja') if p.is_file()]

def get_sovereign_prompt_renderer() -> SovereignPromptRenderer:
    """Brief description of functionality and purpose."""
    return SovereignPromptRenderer()
