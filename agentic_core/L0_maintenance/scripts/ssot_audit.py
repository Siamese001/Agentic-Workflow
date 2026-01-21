"""
SSOT Audit Script - Scans approved folders for SSOT violations
"""
import sys
from pathlib import Path
import json
from collections import defaultdict

# SSOT: Import canonical layer inference (Phase 3 Migration)
# [FIX] Corrected import path (was canonical_truth_1, should be canonical_truth)
from agentic_core.L5_safety.validators.canonical_truth import get_canonical_layer
import ast
import json

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
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
from agentic_core.utils.sovereign_index import SovereignIndex

# Approved folders only
APPROVED_FOLDERS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, SCRIPTS_DIR, TESTS_DIR]
ROOT = Path('.')

# REMOVED: get_layer() function - migrated to canonical_truth.py (Phase 3)
# All layer inference now uses get_canonical_layer() from canonical_truth.py

def find_duplicates():
    """Find duplicate filenames across approved folders."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    files_by_name = defaultdict(list)
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                if py_file.name != '__init__.py':
                    files_by_name[py_file.name].append(str(py_file))

    return {name: paths for name, paths in files_by_name.items() if len(paths) > 1}

def find_gravity_violations():
    """Find upward import violations (higher layer importing from lower layer)."""
    violations = []

    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(ROOT / AGENTIC_CORE_DIR):
        file_layer = get_canonical_layer(py_file)
        if not file_layer or file_layer == 'Unknown':
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    import_path = node.module.replace('.', '/')
                    import_layer = get_canonical_layer(import_path)
                    # SSOT: Use canonical layer order from canonical_truth
                    layer_order = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6}
                    if import_layer and layer_order.get(import_layer, 99) < layer_order.get(file_layer, 0):
                        violations.append({
                            'file': str(py_file),
                            'file_layer': file_layer,
                            'imports': node.module,
                            'import_layer': import_layer
                        })
        except Exception as e:
            pass

    return violations

def find_syntax_errors():
    """Find files with syntax errors."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    errors = []
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append({
                        'file': str(py_file),
                        'line': e.lineno,
                        'message': str(e.msg)
                    })
                except Exception:
                    pass
    return errors

def find_naming_violations():
    """Find files with naming convention violations."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    violations = []
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                name = py_file.stem
                # Check for CamelCase in non-Agent files
                if any(c.isupper() for c in name) and 'Agent' not in name and 'Mixin' not in name:
                    violations.append({
                        'file': str(py_file),
                        'issue': 'CamelCase naming (should be snake_case)'
                    })
                # Check for version suffixes
                if any(suffix in name for suffix in ['_v1', '_v2', '_v3', '_old', '_new', '_backup']):
                    violations.append({
                        'file': str(py_file),
                        'issue': 'Version suffix in filename'
                    })
    return violations

if __name__ == '__main__':
    print("=== SSOT AUDIT REPORT ===\n")

    # Duplicates
    duplicates = find_duplicates()
    print(f"DUPLICATE FILES: {len(duplicates)}")
    for name, paths in sorted(duplicates.items())[:50]:
        print(f"  {name}:")
        for p in paths:
            print(f"    - {p}")

    print(f"\n{'='*50}\n")

    # Gravity violations
    gravity = find_gravity_violations()
    print(f"GRAVITY VIOLATIONS: {len(gravity)}")
    for v in gravity[:30]:
        print(f"  {v['file_layer']} imports {v['import_layer']}: {Path(v['file']).name}")
        print(f"    File: {v['file']}")
        print(f"    Imports: {v['imports']}")

    print(f"\n{'='*50}\n")

    # Syntax errors
    syntax = find_syntax_errors()
    print(f"SYNTAX ERRORS: {len(syntax)}")
    for e in syntax[:30]:
        print(f"  {e['file']}:{e['line']} - {e['message']}")

    print(f"\n{'='*50}\n")

    # Naming violations
    naming = find_naming_violations()
    print(f"NAMING VIOLATIONS: {len(naming)}")
    for v in naming[:30]:
        print(f"  {v['file']}: {v['issue']}")
