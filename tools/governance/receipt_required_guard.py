#!/usr/bin/env python3
"""
receipt_required_guard.py - Pre-run command hook for boundary-sensitive changes.

Blocks broad implementation commands after agentic_core boundary-sensitive 
edits unless a boundary receipt exists.

Exit codes:
  0 - Allow (receipt exists or not boundary-sensitive)
  2 - Block (receipt required but missing)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional

# Configuration
REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
BOUNDARY_RECEIPTS_DIR = GOVERNANCE_DIR / "boundary_receipts"

# Commands that are always allowed (read-only)
READONLY_COMMANDS = {
    'python -m pytest', 'pytest',
    'python -m unittest', 'unittest',
    'git status', 'git log', 'git diff', 'git show',
    'ls', 'dir', 'cat', 'type', 'head', 'tail',
    'grep', 'rg', 'find', 'fd',
    'python -c "print', 'python -c "import',
    'curl http://localhost:8000',  # Health checks
    'docker ps', 'docker logs',
}

# Commands that trigger receipt requirement
IMPLEMENTATION_COMMANDS = {
    'git commit',
    'git push',
    'git merge',
    'git rebase',
    'python -m apps_',
    'python apps_',
    'python -m agentic_core',
    'python agentic_core',
    'run_command',
    'edit_file',
    'multi_edit',
    'write_to_file',
}

# File patterns that are boundary-sensitive
BOUNDARY_SENSITIVE_PATTERNS = [
    r'agentic_core/.*\.py$',
    r'agentic_core/.*\.yaml$',
    r'agentic_core/.*\.json$',
]


def is_readonly_command(command: str) -> bool:
    """Check if command is read-only."""
    cmd_lower = command.lower()
    for readonly in READONLY_COMMANDS:
        if readonly in cmd_lower:
            return True
    return False


def is_implementation_command(command: str) -> bool:
    """Check if command is an implementation command."""
    cmd_lower = command.lower()
    for impl in IMPLEMENTATION_COMMANDS:
        if impl in cmd_lower:
            return True
    return False


def get_recently_modified_files(minutes: int = 30) -> List[str]:
    """Get files modified in the last N minutes."""
    # Check environment variable set by Windsurf or other tools
    windsurf_files = os.environ.get('WINDSURF_FILES', '')
    if windsurf_files:
        return [f.strip() for f in windsurf_files.split(',') if f.strip()]
    
    # Check for recent modifications via git
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'diff', '--name-only', f'--since="{minutes} minutes ago"'],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except Exception:
        pass
    
    return []


def is_boundary_sensitive(filepath: str) -> bool:
    """Check if file is boundary-sensitive (in agentic_core)."""
    if 'agentic_core' not in filepath:
        return False
    
    for pattern in BOUNDARY_SENSITIVE_PATTERNS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return True
    
    return False


def has_boundary_receipt(filepath: str) -> bool:
    """Check if boundary receipt exists for file."""
    if not BOUNDARY_RECEIPTS_DIR.exists():
        return False
    
    # Look for receipts that cover this file
    for receipt_file in BOUNDARY_RECEIPTS_DIR.glob("*.json"):
        try:
            with open(receipt_file, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
                
                # Check if file is in changed_files
                changed_files = receipt.get('changed_files', [])
                if isinstance(changed_files, list):
                    if filepath in changed_files:
                        return True
                
                # Check if file is in files_created or files_modified
                files_created = receipt.get('files_created', [])
                files_modified = receipt.get('files_modified', [])
                
                for file_list in [files_created, files_modified]:
                    if isinstance(file_list, list):
                        for item in file_list:
                            if isinstance(item, str) and filepath in item:
                                return True
                            if isinstance(item, dict) and item.get('path', '').endswith(filepath):
                                return True
        except (json.JSONDecodeError, IOError):
            continue
    
    return False


def get_pending_boundary_files() -> List[Dict]:
    """Get boundary-sensitive files that need receipts."""
    modified = get_recently_modified_files()
    
    boundary_files = []
    for filepath in modified:
        if is_boundary_sensitive(filepath):
            has_receipt = has_boundary_receipt(filepath)
            boundary_files.append({
                "file": filepath,
                "boundary_sensitive": True,
                "receipt_exists": has_receipt,
                "receipt_required": not has_receipt
            })
    
    return boundary_files


def main():
    """Main entry point."""
    # Get command from arguments or environment
    command = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else os.environ.get('WINDSURF_COMMAND', '')
    
    output = {
        "guard": "receipt_required_guard",
        "command": command,
        "timestamp": str(Path(__file__).stat().st_mtime),
    }
    
    # If no command or read-only, allow
    if not command or is_readonly_command(command):
        output["result"] = "ALLOW"
        output["reason"] = "Read-only command"
        print(json.dumps(output, indent=2))
        sys.exit(0)
    
    # Check if this is an implementation command
    if not is_implementation_command(command):
        output["result"] = "ALLOW"
        output["reason"] = "Not an implementation command"
        print(json.dumps(output, indent=2))
        sys.exit(0)
    
    # Get boundary-sensitive files
    boundary_files = get_pending_boundary_files()
    
    files_needing_receipt = [f for f in boundary_files if f['receipt_required']]
    
    output["boundary_files_checked"] = len(boundary_files)
    output["files_needing_receipt"] = len(files_needing_receipt)
    output["boundary_files"] = boundary_files
    
    if files_needing_receipt:
        output["result"] = "BLOCK"
        output["reason"] = f"{len(files_needing_receipt)} boundary-sensitive files lack receipts"
        
        print(json.dumps(output, indent=2))
        print("\n" + "="*60)
        print("RECEIPT REQUIRED")
        print("="*60)
        print(f"\nCommand: {command}")
        print("\nBoundary-sensitive files modified:")
        for f in files_needing_receipt:
            print(f"  - {f['file']}")
        print("\nThese files require a boundary receipt before implementation commands.")
        print("\nTo create a receipt, run:")
        print("  /core-boundary-audit")
        print("\nOr create manually at:")
        print(f"  {BOUNDARY_RECEIPTS_DIR}/<timestamp>_<audit_id>.json")
        print("\nTo bypass (not recommended):")
        print("  RECEIPT_REQUIRED_BYPASS=1 <command>")
        print("="*60)
        sys.exit(2)
    
    # Allow - all boundary files have receipts or no boundary files
    output["result"] = "ALLOW"
    output["reason"] = "All boundary-sensitive files have receipts"
    
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
