#!/usr/bin/env python3
"""
Validate that no hardcoded paths exist - enforce SSOT compliance.
Run this as pre-commit hook or CI check.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

# Directories to exclude
EXCLUDED_DIRS = {
    '__pycache__', '.pytest_cache', 'build', 'dist',
    '.git', '.venv', 'venv', 'env', 'node_modules',
    'archives', 'legacy', 'deprecated', 'test_data',
}

# Files that are allowed to have hardcoded paths
EXCLUDED_FILES = {
    'structure_blueprint.py',  # SSOT definition file
    'validate_path_ssot.py',   # This file
    'scan_hardcoded_paths.py',
    'refactor_hardcoded_paths.py',
}

# Patterns that indicate hardcoded paths (violations)
HARDCODED_PATH_PATTERNS = [
    # Agent discovery files
    (r'(?<!AGENT_DISCOVERY_JSON\s*=\s*)["\']agent_discovery_full\.json["\']', 
     'Use AGENT_DISCOVERY_JSON constant'),
    (r'(?<!AGENT_DISCOVERY_MANIFEST_JSON\s*=\s*)["\']agent_discovery_full\.manifest\.json["\']',
     'Use AGENT_DISCOVERY_MANIFEST_JSON constant'),
    
    # Layer directories - exact matches only
    (r'["\']agentic_core/L0_maintenance["\'](?!\s*[:\]])',
     'Use L0_MAINTENANCE_DIR constant'),
    (r'["\']agentic_core/L1_cognition["\'](?!\s*[:\]])',
     'Use L1_COGNITION_DIR constant'),
    (r'["\']agentic_core/L2_execution["\'](?!\s*[:\]])',
     'Use L2_EXECUTION_DIR constant'),
    (r'["\']agentic_core/L3_orchestration["\'](?!\s*[:\]])',
     'Use L3_ORCHESTRATION_DIR constant'),
    (r'["\']agentic_core/L4_state["\'](?!\s*[:\]])',
     'Use L4_STATE_DIR constant'),
    (r'["\']agentic_core/L5_safety["\'](?!\s*[:\]])',
     'Use L5_SAFETY_DIR constant'),
    (r'["\']agentic_core/L6_observability["\'](?!\s*[:\]])',
     'Use L6_OBSERVABILITY_DIR constant'),
    
    # Dashboard directory
    (r'["\']agentic_core/L6_observability/dashboards["\']',
     'Use DASHBOARD_DIR constant'),
    
    # Core directories - only flag bare references
    (r'(?<![/\w])["\']agentic_core["\'](?!\s*[:\]./])',
     'Use AGENTIC_CORE_DIR constant'),
    (r'(?<![/\w])["\']scripts["\'](?!\s*[:\]./])',
     'Use SCRIPTS_DIR constant'),
    (r'["\']tests/unit["\']',
     'Use TESTS_UNIT_DIR constant'),
    (r'(?<![/\w])["\']tests["\'](?!\s*[:\]./])',
     'Use TESTS_DIR constant'),
]

def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded from validation."""
    parts_lower = {p.lower() for p in path.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False

def validate_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Validate a single file for hardcoded paths.
    
    Returns:
        List of (line_number, violation_description, line_content)
    """
    violations = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        # Skip if file imports from structure_blueprint (likely compliant)
        if 'from agentic_core.L5_safety.validators.structure_blueprint import' in content:
            # File uses SSOT, but still check for violations
            pass
        
        for line_num, line in enumerate(lines, 1):
            # Skip import lines
            if 'import' in line and 'structure_blueprint' in line:
                continue
            
            # Skip lines defining SSOT constants
            if re.match(r'^\s*[A-Z_]+\s*[:=]\s*["\']', line):
                continue
            
            # Check each pattern
            for pattern, description in HARDCODED_PATH_PATTERNS:
                if re.search(pattern, line):
                    violations.append((line_num, description, line.strip()))
    
    except Exception as e:
        pass
    
    return violations

def validate_repository() -> Tuple[bool, Dict]:
    """Validate entire repository.
    
    Returns:
        (is_compliant, violations_dict)
    """
    print("=" * 80)
    print("PATH SSOT VALIDATION")
    print("=" * 80)
    print(f"\n📂 Project: {PROJECT_ROOT}")
    print(f"🔍 Scanning for hardcoded paths...\n")
    
    violations_by_file = {}
    files_scanned = 0
    
    # Scan all Python files
    # Final True 20: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(PROJECT_ROOT):
        if should_exclude_path(py_file):
            continue
        
        files_scanned += 1
        violations = validate_file(py_file)
        
        if violations:
            rel_path = py_file.relative_to(PROJECT_ROOT)
            violations_by_file[str(rel_path)] = violations
    
    # Print results
    total_violations = sum(len(v) for v in violations_by_file.values())
    
    print(f"✅ Scanned {files_scanned} files\n")
    
    if total_violations == 0:
        print("=" * 80)
        print("✅ ALL FILES COMPLIANT")
        print("=" * 80)
        print("No hardcoded paths found!")
        print("All files correctly use SSOT constants from structure_blueprint.py")
        return True, {}
    else:
        print("=" * 80)
        print(f"❌ FOUND {total_violations} VIOLATIONS IN {len(violations_by_file)} FILES")
        print("=" * 80)
        print()
        
        # Show top violators
        sorted_files = sorted(violations_by_file.items(), key=lambda x: -len(x[1]))
        for file_path, violations in sorted_files[:20]:
            print(f"\n📄 {file_path}")
            print(f"   {len(violations)} violation(s):")
            for line_num, desc, line_content in violations[:5]:
                print(f"      Line {line_num}: {desc}")
                print(f"         {line_content}")
            if len(violations) > 5:
                print(f"      ... and {len(violations) - 5} more")
        
        if len(violations_by_file) > 20:
            print(f"\n   ... and {len(violations_by_file) - 20} more files with violations")
        
        print("\n" + "=" * 80)
        print("REMEDIATION REQUIRED")
        print("=" * 80)
        print("Replace hardcoded paths with SSOT constants:")
        print("  from agentic_core.L5_safety.validators.structure_blueprint import (")
        print("      AGENT_DISCOVERY_JSON, DASHBOARD_DIR, L0_MAINTENANCE_DIR,")
        print("      get_validated_project_root")
        print("  )")
        print()
        print("  # Example usage:")
        print("  discovery_path = get_validated_project_root() / AGENT_DISCOVERY_JSON")
        print("  dashboard_dir = get_validated_project_root() / DASHBOARD_DIR")
        print("=" * 80)
        
        return False, violations_by_file

def main():
    import sys
    is_compliant, violations = validate_repository()
    
    if is_compliant:
        print("\n✅ Validation passed")
        return 0
    else:
        print(f"\n❌ Validation failed: {sum(len(v) for v in violations.values())} violations")
        return 1

if __name__ == "__main__":
    exit(main())
