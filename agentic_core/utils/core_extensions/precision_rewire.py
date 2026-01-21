from __future__ import annotations

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path('C:/Git/Agentic-Workflow')
rewire_map: Any = [('agentic_core\\.agents', 'agentic_core.L2_execution.tool_registry'), ('agentic_core\\.tools', 'agentic_core.L2_execution.P2_tools'), ('agentic_core\\.interfaces', 'agentic_core.L1_cognition.P1_interfaces'), ('agentic_core\\.domain', 'agentic_core.L1_cognition.P2_domain'), ('agentic_core\\.L1_cognition\\.action_registry_modules', 'agentic_core.L1_cognition.P1_sensing.action_registry_modules'), ('agentic_core\\.state', 'agentic_core.L4_state.S1_store'), ('agentic_core\\.infra', 'agentic_core.L3_orchestration.S3_vitality'), ('agentic_core\\.security', 'agentic_core.L5_safety.P4_security'), ('from apps_rg\\.L3_orchestration\\.l5_autonomous_orchestrator import WorkflowSnapshot', '')]

def rewire_synapses() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] STARTING GLOBAL SYNAPTIC REWIRE...')
    rewired_count: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(ROOT):
        if 'legacy_code' in str(py_file) or 'data' in str(py_file):
            continue
        try:
            with open(py_file, encoding='utf-8') as f:
                content: Any = f.read()
            original_content: Any = content
            for pattern, replacement in REWIRE_MAP:
                content: Any = re.sub(pattern, replacement, content)
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  [✓] Rewired: {py_file.relative_to(ROOT)}')
                rewired_count += 1
        except Exception as e:
            print(f'  [!] Failed {py_file.name}: {e}')
    print(f'\n[OK] REWIRE COMPLETE. {rewired_count} files aligned with the Sovereign Map.')
if __name__ == '__main__':
    rewire_synapses()
