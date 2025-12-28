#!/usr/bin/env python3
"""
Standalone Key 49 Depth Violation Checker
Scans all Python files for depth > 5 (Key 49: Universal Max 5 Levels From Root)
"""
from pathlib import Path


def check_key_49_depth():
    """Check directory depth violations per Key 49"""
    project_root = Path(__file__).parent.parent.parent  # Repository root (from validator/entry/)
    violations = []
    warnings = []
    
    # Excludes per Key 49 rules - ONLY data, archives, and tests excluded
    excludes = {'.git', '__pycache__', 'data', 'archives', '.venv', 'tests'}
    
    for py_file in project_root.rglob('*.py'):
        # Calculate depth: len(parts) - 1 (excluding root)
        relative_path = py_file.relative_to(project_root)
        depth = len(relative_path.parts)
        
        # [SSOT] Dynamic depth check from structure_blueprint
        import sys
        from pathlib import Path as PathLib

        # Path insert no longer needed - using absolute import
        from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_DEPTH_MAP

        # Check if folder has specific depth requirement
        if relative_path.parts and relative_path.parts[0] in SOVEREIGN_DEPTH_MAP:
            root_folder = relative_path.parts[0]
            required_depth = SOVEREIGN_DEPTH_MAP[root_folder]
            if depth != required_depth:
                violations.append(f"{relative_path} (Invalid depth: {depth} - {root_folder} must be at depth {required_depth})")
            continue
            
        # Skip excluded directories
        if any(exclude in str(py_file) for exclude in excludes):
            continue
            
        if depth > 5:
            violations.append(f"{relative_path} (Invalid depth: {depth})")
        elif depth < 3 and not py_file.name == "__init__.py":  # Files too shallow, but __init__.py can be depth 2
            violations.append(f"{relative_path} (Invalid depth: {depth} - minimum depth is 3)")
    
    # Report results
    print("=" * 70)
    print("KEY 49 DEPTH VIOLATION REPORT")
    print("=" * 70)
    
    if violations:
        print(f"\n[VIOLATIONS] Found {len(violations)} file(s) exceeding depth 5:")
        for v in violations[:20]:  # Show first 20
            print(f"  ✗ {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more violations")
    else:
        print("\n[✓] NO depth violations found - All files at depth ≤ 5")
    
    if warnings:
        print(f"\n[WARNINGS] Found {len(warnings)} file(s) at depth 1:")
        for w in warnings[:10]:
            print(f"  ⚠ {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    
    # Show deepest files
    print(f"\n[DEEPEST FILES] Current maximum depth in repository:")
    all_depths = []
    for py_file in project_root.rglob('*.py'):
        if any(exclude in str(py_file) for exclude in excludes):
            continue
        relative_path = py_file.relative_to(project_root)
        depth = len(relative_path.parts)
        all_depths.append((depth, relative_path))
    
    all_depths.sort(reverse=True)
    max_depth = all_depths[0][0] if all_depths else 0
    deepest = [f for d, f in all_depths if d == max_depth][:5]
    
    print(f"  Maximum depth: {max_depth}")
    for f in deepest:
        print(f"  - {f}")
    
    print("=" * 70)
    return len(violations) == 0

if __name__ == "__main__":
    success = check_key_49_depth()
    exit(0 if success else 1)
