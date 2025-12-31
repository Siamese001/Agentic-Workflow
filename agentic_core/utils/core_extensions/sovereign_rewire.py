import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
from typing import Any
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
rewire_rules: Any = [('from agentic_core\\.utils import', 'from agentic_core.utils.P1_core import'), ('from agentic_core\\.memory import', 'from agentic_core.memory.P1_core import')]

def rewire_synapses() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] STARTING GLOBAL SYNAPTIC REWIRE...')
    fixed_count: Any = 0
    for py_file in ROOT.rglob('*.py'):
        if 'sovereign_rewire' in py_file.name:
            continue
        try:
            content: Any = py_file.read_text(encoding='utf-8')
            original: Any = content
            for pattern, replacement in REWIRE_RULES:
                content: Any = re.sub(pattern, replacement, content)
            if 'P1_core' in str(py_file):
                content: Any = content.replace('from ..', 'from agentic_core.')
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f'  [✓] Rewired: {py_file.relative_to(ROOT)}')
                fixed_count += 1
        except Exception as e:
            print(f'  [!] Failed {py_file.name}: {e}')
    print(f'\n[OK] REWIRE COMPLETE. {fixed_count} files reconnected to the Sovereign Brain.')
if __name__ == '__main__':
    rewire_synapses()
