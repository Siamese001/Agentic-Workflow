#!/usr/bin/env python3
"""Run NamingAgent to detect agent file naming violations."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.core_extensions.NamingAgent import NamingAgent

def main():
    agent = NamingAgent(PROJECT_ROOT)
    
    # Directories to scan
    scan_dirs = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']
    
    violations = []
    compliant = 0
    
    for dir_name in scan_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.rglob('*.py'):
            if '__pycache__' in str(py_file) or '__init__.py' == py_file.name:
                continue
            
            is_valid, message = agent.validate_file_naming(py_file)
            
            if not is_valid and 'AGENT FILE NAMING VIOLATION' in message:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                violations.append((str(rel_path), message))
            elif is_valid:
                compliant += 1
    
    print("=" * 70)
    print("AGENT FILE NAMING LAW CHECK")
    print("=" * 70)
    print(f"\nCompliant files: {compliant}")
    print(f"Violations (agent classes in non-*Agent.py files): {len(violations)}")
    print("=" * 70)
    
    if violations:
        print("\nVIOLATIONS:\n")
        for path, msg in sorted(violations)[:50]:
            print(f"  {path}")
            # Extract suggested name from message
            if "Rename file to" in msg:
                suggested = msg.split("Rename file to '")[1].split("'")[0]
                print(f"    → Rename to: {suggested}")
            print()
        
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more violations")
    
    print("=" * 70)
    print(f"TOTAL: {len(violations)} files need renaming to *Agent.py")
    print("=" * 70)

if __name__ == '__main__':
    main()
