from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
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
apps: Any = [ROOT / APPS_RG_DIR, ROOT / APPS_LIC_DIR, ROOT / APPS_SHARED_DIR]
rewire_map: Any = [('from agentic_core\\.utils\\.', 'from agentic_core.utils.P1_core.')]

def rebuild_bridges() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] REBUILDING APP-TO-CORE BRIDGES...')
    fixed_count: Any = 0
    for app_dir in APPS:
        if not app_dir.exists():
            continue
        for py_file in app_dir.rglob('*.py'):
            try:
                content: Any = py_file.read_text(encoding='utf-8')
                original: Any = content
                for pattern, sub in REWIRE_MAP:
                    content: Any = re.sub(pattern, sub, content)
                if content != original:
                    py_file.write_text(content, encoding='utf-8')
                    print(f'  [✓] Bridged: {py_file.relative_to(ROOT)}')
                    fixed_count += 1
            except Exception as e:
                print(f'  [!] Failed {py_file.name}: {e}')
    print(f'\n[OK] BRIDGES REBUILT. {fixed_count} app-side files synced with the Sovereign Core.')
if __name__ == '__main__':
    rebuild_bridges()
