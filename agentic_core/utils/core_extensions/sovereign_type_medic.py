from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
from typing import Any

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR
type_fixes: Any = [(':\\s*STR\\b', ': str'), (':\\s*FLOAT\\b', ': float'), (':\\s*BOOL\\b', ': bool'), ('->\\s*STR\\b', '-> str'), ('->\\s*FLOAT\\b', '-> float'), ('->\\s*BOOL\\b', '-> bool')]
import_alignments: Any = []

def run_type_medic() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] SOVEREIGN TYPE MEDIC: Initiating Clean Sweep...')
    modified_files: Any = 0
    for py_file in CORE.rglob('*.py'):
        if py_file.name == '__init__.py' or 'legacy' in str(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            original: Any = content
            for pattern, sub in TYPE_FIXES:
                content: Any = re.sub(pattern, sub, content)
            for pattern, sub in IMPORT_ALIGNMENTS:
                content: Any = re.sub(pattern, sub, content)
            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  [✓] Healed: {py_file.relative_to(CORE)}')
                modified_files += 1
        except Exception as e:
            print(f'  [!] Failed to treat {py_file.name}: {e}')
    print(f'\n[OK] MEDIC COMPLETE. {modified_files} files sanitized.')
    print("    [!] NEXT: Run 'python mission_start.py' to verify the full chain.")
if __name__ == '__main__':
    run_type_medic()
