import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import subprocess
from pathlib import Path
from typing import Any

def wake_the_brain() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] MISSION START: FINAL SOVEREIGN VALIDATION')
    cmd: Any = ['python', 'canon_validator_agentic_v2.py', '--target', 'agentic_core', '--mode', 'comprehensive', '--heal', 'true']
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
