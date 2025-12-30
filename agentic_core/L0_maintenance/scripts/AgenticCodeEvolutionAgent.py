import json
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Any
from agentic_core.prompt_governance.rendering.sovereign_prompt_renderer import get_sovereign_prompt_renderer

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class AgenticCodeEvolutionAgent:
    """
    Sovereign agent that evolves the codebase by learning from repeated healing patterns.

    Responsibilities:
    - Analyze mission report logs for recurring fix types.
    - Propose and generate new specialized atomic healer agents via LLM.
    - Physically register new healers in the L2 tool_registry.
    """
    EVOLUTION_PROMPT: Any = '\nYou are the sovereign code evolution architect. \n\nRecurring violation pattern detected in mission telemetry:\n- Violation type: {{ violation_type }}\n- Frequency: {{ file_count }} instances\n- Recent Examples: {{ examples | join("\\n") }}\n\nTask: Propose and implement a new specialized Atomic Healer Agent.\n\nRequirements:\n- Class Name: {{ suggested_name }}Agent\n- Territory: agentic_core/L2_execution/tool_registry/{{ suggested_file }}\n- Interface: Implements \'async def heal_violation(self, file_path: Path, ctx)\'\n- Logic: Performs single-file surgery to fix the detected pattern.\n\nOutput EXACTLY this JSON:\n{\n  "agent_name": "StringName",\n  "filename": "snake_case_name.py",\n  "purpose": "Brief description of behavior",\n  "code": "Full Python implementation of the agent class",\n  "expected_impact": "Reduction of specific Canon Key violations"\n}\n'

    async def execute(self, ctx: Any) -> None:
        """
        Phase 3 Monitor — executes autonomous evolution if surgery is enabled.
        """
        if not getattr(ctx, 'RUN_SPRAWL_SURGERY', False):
            return
        if not hasattr(ctx, 'engine') or ctx.engine is None:
            return
        pattern: Any = self._detect_evolution_pattern(ctx)
        if not pattern:
            return
        print(f"\n[*] AGENTIC CODE EVOLUTION: Pattern detected! Proposing healer for: {pattern['type']}")
        renderer: Any = get_sovereign_prompt_renderer()
        evolution_context: Any = {'violation_type': pattern['type'], 'file_count': pattern['count'], 'examples': pattern['examples'][:3], 'suggested_name': pattern['type'].replace(' ', '').replace('-', '').replace('_', ''), 'suggested_file': pattern['type'].lower().replace(' ', '_').replace('-', '_') + '_agent.py'}
        instruction: Any = renderer.render(template_name='code_healing.jinja', context={'code_block': self.EVOLUTION_PROMPT, 'violations': [pattern['type']]})
        full_prompt: Any = instruction.format(**evolution_context)
        try:
            proposal_raw: Any = await ctx.engine.resilient_mutation(file_path='code_evolution_proposal', code=full_prompt, task='Generate new specialized healer agent', round_num=1, fission_active=False)
            proposal: Any = json.loads(proposal_raw)
            tool_dir: Any = Path(ctx.project_root) / 'agentic_core' / 'L2_execution' / 'tool_registry'
            tool_dir.mkdir(parents=True, exist_ok=True)
            new_file_path: Any = tool_dir / proposal['filename']
            if new_file_path.exists():
                return
            new_file_path.write_text(proposal['code'], encoding='utf-8')
            print(f"    [EVOLVED] Created new specialized healer: {proposal['filename']}")
            print(f"    Purpose: {proposal['purpose']}")
            if hasattr(ctx, 'audit_log'):
                ctx.audit_log.record(file_name=proposal['filename'], action='AGENT_SPAWNED', source='AgenticCodeEvolutionAgent', destination='L2_execution/tool_registry', reason=f"Learning from {pattern['count']} instances of {pattern['type']}")
            ctx.report(self.__class__.__name__, 0, True, f"Autonomous Evolution: Spawned {proposal['agent_name']}")
        except Exception as e:
            print(f'    [!] Code evolution failed: {e}')
            ctx.report(self.__class__.__name__, 0, False, f'Evolution failure: {str(e)}')

    def _detect_evolution_pattern(self, ctx: Any) -> Optional[Dict[str, Any]]:
        """
        Simulated pattern detection using mission telemetry.
        Scans the current report for recurring violation messages.
        """
        report_entries = getattr(ctx.report, 'entries', [])
        if not report_entries:
            return None
        messages = [e.get('msg', '') for e in report_entries if e.get('msg')]
        counter = Counter(messages)
        most_common = counter.most_common(1)
        if most_common and most_common[0][1] > 5:
            msg, count = most_common[0]
            return {'type': msg.split(':')[0] if ':' in msg else msg, 'count': count, 'examples': [msg]}
        return None

def get_agentic_code_evolution_agent() -> Any:
    """Brief description of functionality and purpose."""
    return AgenticCodeEvolutionAgent()
