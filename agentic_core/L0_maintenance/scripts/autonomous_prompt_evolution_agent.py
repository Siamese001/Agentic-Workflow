import json
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from agentic_core.prompt_governance.rendering.sovereign_prompt_renderer import get_sovereign_prompt_renderer
from agentic_core.prompt_governance.version_registry.prompt_registry import get_prompt_registry

class autonomous_prompt_evolution_agent:
    """
    Sovereign agent for autonomous evolution of prompt templates.

    Responsibilities (per Master Constitution):
    - Detect evolution needs based on validation drift.
    - Propose v2+ Jinja templates using SubAtomic LLM reasoning.
    - Physically write versioned artifacts to prompt_governance zones.
    - Register new versions in the version_registry for active deployment.
    """
    EVOLUTION_PROMPT: Any = '\nYou are a sovereign prompt engineer evolving Canon Key 1 templates.\n\nCurrent template performance issues:\n{% for issue in issues %}\n- {{ issue }}\n{% endfor %}\n\nTask: Evolve the template to v2+ while preserving sovereignty, Jinja syntax, and tagged structure.\n\nOutput EXACTLY this JSON format:\n{\n  "proposed_version": "v2",\n  "improved_template": "full Jinja content here",\n  "change_rationale": "sovereign justification",\n  "expected_impact": "specific metric improvement"\n}\n\nOriginal Template to Evolve:\n{{ current_template }}\n'

    async def execute(self, ctx: Any) -> None:
        """
        Phase 3 Monitor / Escalation entry point.
        """
        if not hasattr(ctx, 'engine') or ctx.engine is None:
            return
        trigger: Any = self._detect_evolution_need(ctx)
        if not trigger:
            return
        print(f"\n[*] AUTONOMOUS PROMPT EVOLUTION: Self-correcting {trigger['template']}")
        renderer: Any = get_sovereign_prompt_renderer()
        registry: Any = get_prompt_registry()
        template_path: Any = Path(trigger['path'])
        try:
            current_content: Any = template_path.read_text(encoding='utf-8')
        except Exception:
            return
        evolution_input: Any = renderer.render(template_name='code_healing.jinja', context={'code_block': self.EVOLUTION_PROMPT, 'violations': trigger['issues'], 'current_template': current_content})
        try:
            proposal_raw: Any = await ctx.engine.resilient_mutation(file_path=str(template_path.name), code=evolution_input, task='Evolve sovereign prompt template', round_num=1, fission_active=False)
            proposal: Any = json.loads(proposal_raw)
            new_version: Any = proposal.get('proposed_version', 'v2')
            new_content: Any = proposal['improved_template']
            new_file_name: Any = f'{template_path.stem}_{new_version}{template_path.suffix}'
            new_path: Any = template_path.parent / new_file_name
            new_path.write_text(new_content, encoding='utf-8')
            registry.register_prompt(template_name=template_path.name, version=new_version, purpose=proposal.get('change_rationale', 'Autonomous drift repair'), active=True)
            print(f'    [EVOLVED] {template_path.name} -> {new_version}')
            if hasattr(ctx, 'audit_log'):
                ctx.audit_log.record(file_name=template_path.name, action='AUTONOMOUS_PROMPT_EVOLUTION', source='v1', destination=new_version, reason=proposal.get('change_rationale'))
            ctx.report(self.__class__.__name__, 0, True, f'Evolved {template_path.name} to {new_version}')
        except Exception as e:
            print(f'    [!] Evolution failed: {e}')
            ctx.report(self.__class__.__name__, 0, False, f'Evolution failure: {str(e)}')

    def _detect_evolution_need(self, ctx: Any) -> Optional[Dict[str, Any]]:
        """
        Heuristic trigger: evaluates context for prompt validation failures.
        """
        if getattr(ctx, 'prompt_validation_issues', None):
            return {'template': 'reasoning_chain.jinja', 'path': Path(ctx.project_root) / 'agentic_core/prompt_governance/templates/reasoning_chain.jinja', 'issues': ctx.prompt_validation_issues}
        return None

def get_autonomous_prompt_evolution_agent() -> Any:
    """Brief description of functionality and purpose."""
    return AutonomousPromptEvolutionAgent()
