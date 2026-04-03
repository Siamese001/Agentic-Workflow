"""CI Gate: Block imports from archives/ in production code.

Rule 12 of .windsurfrules: NO IMPORTS FROM ARCHIVES/ IN PRODUCTION CODE.
The archives/ directory is a backup graveyard — imports from it are FORBIDDEN.
"""

import re
import sys
from pathlib import Path


def find_archives_imports(repo_root: Path) -> list[tuple[str, int, str]]:
    """Find all active imports from archives/ in production code."""
    violations = []
    production_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_eval", "apps_exec", "apps_research", "apps_shared", "system_learning"]
    
    for dir_name in production_dirs:
        dir_path = repo_root / dir_name
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    # Skip comments
                    if re.match(r'^\s*#', line):
                        continue
                    # Skip lines where 'archives' is inside a string (e.g., sed commands)
                    if re.search(r'["\'].*archives.*["\']', line):
                        continue
                    # Match actual imports from archives
                    if re.match(r'^(?:from|import)\s+archives\.', line.strip()):
                        violations.append((str(py_file), i + 1, line.strip()))
            except Exception:
                continue
    
    return violations


def main() -> int:
    """Main entrypoint. Returns 0 if clean, 1 if violations found."""
    repo_root = Path.cwd()
    violations = find_archives_imports(repo_root)
    
    if violations:
        print("ERROR: Found imports from archives/ in production code!")
        print("Rule 12: NO IMPORTS FROM ARCHIVES/ IN PRODUCTION CODE.")
        print(f"Violations: {len(violations)}")
        print()
        for file_path, line, content in violations:
            print(f"  {file_path}:{line}: {content}")
        print()
        print("Fix: Update imports to point to canonical locations in production code.")
        print("The archives/ directory is a backup graveyard — do not import from it.")
        return 1
    
    print("OK: No archives/ imports found in production code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
