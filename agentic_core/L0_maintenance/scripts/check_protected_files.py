"""
Gatekeeper Protection: Block commits that modify protected files

This script prevents accidental modifications to critical infrastructure files
like ArchivalGatekeeper.py unless an explicit override is present in the commit message.

PROTECTED FILES:
    - agentic_core/L5_safety/core/ArchivalGatekeeper.py (The Executioner)
    - agentic_core/L5_safety/validators/decorators.py (The Normalizer)

OVERRIDE:
    Include '#gatekeeper-override' in your commit message to bypass protection.

USAGE:
    python scripts/maintenance/check_protected_files.py

EXIT CODES:
    0 - No protected files modified OR override present
    1 - Protected files modified without override
"""
from pathlib import Path
import subprocess
import sys
PROTECTED_FILES = ['agentic_core/L5_safety/core/ArchivalGatekeeper.py', 'agentic_core/L5_safety/validators/decorators.py']
OVERRIDE_FLAG = '#gatekeeper-override'

def get_staged_files() -> list[str]:
    """Get list of files staged for commit."""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, check=True)
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []

def get_commit_message() -> str:
    """Get the commit message if available."""
    try:
        commit_msg_file = Path('.git/COMMIT_EDITMSG')
        if commit_msg_file.exists():
            return commit_msg_file.read_text()
        return ''
    except Exception:
        return ''

def main():
    """TODO: Add documentation for main."""
    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)
    modified_protected = []
    for protected in PROTECTED_FILES:
        protected_path = Path(protected).as_posix()
        for staged in staged_files:
            staged_path = Path(staged).as_posix()
            if staged_path == protected_path or staged_path.endswith(protected_path):
                modified_protected.append(protected)
                break
    if not modified_protected:
        sys.exit(0)
    commit_message = get_commit_message()
    if OVERRIDE_FLAG in commit_message:
        for f in modified_protected:
            pass
        sys.exit(0)
    for f in modified_protected:
        pass
    sys.exit(1)
if __name__ == '__main__':
    main()
