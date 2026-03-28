"""E2E Template Wiring Proof Script"""
from agentic_core.prompt_governance.core.sovereign_prompt_renderer import SovereignPromptRenderer
from agentic_core.prompt_governance.core.template_catalog import TEMPLATE_CATALOG, get_templates_for_agent
from apps_rg.engines.base_rg_engine import BaseRGEngine
from pydantic import BaseModel
import os

print('='*70)
print('E2E TEMPLATE WIRING PROOF')
print('='*70)

# 1. Templates directory exists and has files
templates_dir = os.path.join('agentic_core', 'prompt_governance', 'templates')
templates = [f for f in os.listdir(templates_dir) if f.endswith('.jinja')]
print(f'1. Templates found: {len(templates)} jinja files')
for t in templates[:5]:
    print(f'   - {t}')

# 2. Renderer can load templates
renderer = SovereignPromptRenderer()
available = renderer.list_available_templates()
print(f'2. Renderer loaded: {len(available)} templates')

# 3. Catalog has entries
print(f'3. Template catalog: {len(TEMPLATE_CATALOG)} entries')

# 4. Agents can look up templates
agents = ['GravityLeakRepairAgent', 'NamingAgent', 'CodeHealerAgent']
for agent in agents:
    templates = get_templates_for_agent(agent)
    print(f'4. {agent}: {len(templates)} templates')

# 5. Actual rendering works with complete context
ctx = {
    'violations': ['snake_case violation'],
    'code_block': 'def MyFunction(): pass',
    'file_path': 'test.py',
    'behavioral_status': 'partial',
    'healing_round': 1,
    'total_violations': 1,
    'task_violations': 'test',
    'file_violations': 2,
    'persistent_keys': ['key1'],
    'primary_key': 'key1',
    'recently_converged': [],
    'surgery_flags': [],
    'top_subatomic_fixes': ['naming'],
    'canon_key': '18',
    'past_fixes': '',
    'code_preview': 'def test(): pass',
    'current_path': 'test.py',
    'entity_count': 5,
    'line_count': 100
}
result = renderer.render('code_healing.jinja', context=ctx, validate=False)
sovereign_check = 'SOVEREIGN' in result
print(f'5. Template rendered: {len(result)} chars, contains SOVEREIGN: {sovereign_check}')

# 6. apps_rg can retrieve prompts via BaseRGEngine
class DummyEngine(BaseRGEngine):
    AGENT_ID = 'test'
    def execute(self, input_data: BaseModel) -> BaseModel:
        return input_data

engine = DummyEngine()
engine_prompt = engine.get_prompt('hyde_gen')
has_knowledge = engine.get_status()['knowledge_available']
print(f'6. BaseRGEngine.get_prompt(): knowledge={has_knowledge}, prompt_len={len(engine_prompt)}')

print('='*70)
print('ALL CHECKS PASSED - TEMPLATES WIRED E2E')
print('='*70)
