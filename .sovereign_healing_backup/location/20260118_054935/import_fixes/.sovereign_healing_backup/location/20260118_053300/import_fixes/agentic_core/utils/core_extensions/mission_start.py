from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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

def wake_the_brain() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] MISSION START: FINAL SOVEREIGN VALIDATION')
    cmd: Any = ['python', 'canon_validator_agentic_v2.py', '--target', AGENTIC_CORE_DIR, '--mode', 'comprehensive', '--heal', 'true']
    try:
        process: Any = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode == 0:
            print('\n[SUCCESS] SOVEREIGN CORE IS FULLY FUNCTIONAL.')
        else:
            print(f'\n[!] ALERT: Validator exited with code {process.returncode}.')
    except Exception as e:
        print(f'[ERROR] Could not start validation: {e}')
if __name__ == '__main__':
    wake_the_brain()
