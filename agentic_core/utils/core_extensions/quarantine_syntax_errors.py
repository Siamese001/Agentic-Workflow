from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from archives.location_violations.sovereign_index import SovereignIndex
root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / AGENTIC_CORE_DIR
quarantine: Any = ROOT / 'quarantine_syntax_errors'

def quarantine_all_broken() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] QUARANTINE: Scanning for all syntax-broken files...')
    QUARANTINE.mkdir(exist_ok=True)
    quarantined: Any = 0
    for py_file in CORE.rglob('*.py'):
        try:
            content: Any = py_file.read_text(encoding='utf-8')
            ast.parse(content)
        except SyntaxError:
            try:
                dest: Any = QUARANTINE / py_file.name
                counter: Any = 1
                while dest.exists():
                    dest: Any = QUARANTINE / f'{py_file.stem}_{counter}{py_file.suffix}'
                    counter += 1
                shutil.move(str(py_file), str(dest))
                print(f'  [✓] Quarantined: {py_file.relative_to(CORE)}')
                quarantined += 1
            except Exception as e:
                print(f'  [X] Failed to quarantine {py_file.name}: {e}')
        except Exception as e:
            print(f'  [!] Skipped {py_file.name}: {e}')
    print(f'\n[OK] QUARANTINE COMPLETE. {quarantined} broken files isolated.')
    print(f'    Files moved to: {QUARANTINE}')
if __name__ == '__main__':
    quarantine_all_broken()
