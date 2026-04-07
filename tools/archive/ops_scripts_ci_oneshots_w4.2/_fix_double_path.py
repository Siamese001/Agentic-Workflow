"""
Fix double-pathing: AGENTIC_CORE_DIR / L*_DIR -> L*_DIR
The L*_DIR constants already contain 'agentic_core/' prefix,
so AGENTIC_CORE_DIR / L*_DIR creates an invalid double path.

Also add any missing imports detected by the audit.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYER_DIRS = {'L0_ROUTING_DIR', 'L1_COGNITION_DIR', 'L2_EXECUTION_DIR', 'L3_ORCHESTRATION_DIR', 'L4_STATE_DIR', 'L5_SAFETY_DIR', 'L6_OBSERVABILITY_DIR'}
ALL_CONSTANTS = {'AGENTIC_CORE_DIR', 'APPS_LIC_DIR', 'APPS_RG_DIR', 'APPS_SHARED_DIR', 'SYSTEM_LEARNING_DIR', 'TOOLS_DIR', 'TESTS_DIR', 'OPS_SCRIPTS_DIR', 'L0_ROUTING_DIR', 'L1_COGNITION_DIR', 'L2_EXECUTION_DIR', 'L3_ORCHESTRATION_DIR', 'L4_STATE_DIR', 'L5_SAFETY_DIR', 'L6_OBSERVABILITY_DIR', 'ARCHIVES_DIR'}
IMPORT_BLOCK_RE = re.compile('from agentic_core\\.L0_routing\\.config\\.path_constants import \\(([^)]*)\\)', re.DOTALL)

def get_imported_constants(src: str) -> set[str]:
    imported = set()
    m = IMPORT_BLOCK_RE.search(src)
    if m:
        imported.update(re.findall('\\b([A-Z_]{3,})\\b', m.group(1)))
    return imported & ALL_CONSTANTS

def add_missing_to_import(src: str, missing: set[str]) -> str:
    m = IMPORT_BLOCK_RE.search(src)
    if not m:
        return src
    body = m.group(1)
    existing = set(re.findall('\\b([A-Z_]{3,})\\b', body))
    truly_missing = missing - existing
    if not truly_missing:
        return src
    stripped_body = body.rstrip().rstrip(',')
    new_body = stripped_body + ',\n    ' + ',\n    '.join(sorted(truly_missing)) + ','
    new_block = 'from agentic_core.L0_routing.config.path_constants import (' + new_body + '\n)'
    return src.replace(m.group(0), new_block)

def fix_double_paths(src: str) -> tuple[str, list[str]]:
    """
    Replace all AGENTIC_CORE_DIR / L*_DIR patterns with just L*_DIR.
    Handles both direct and chained path expressions.
    """
    fixes = []
    for layer_const in LAYER_DIRS:
        # guardian: allow-path-string
        pattern = re.compile('\\bAGENTIC_CORE_DIR\\s*/\\s*' + re.escape(layer_const) + '\\b')
        if pattern.search(src):
            src = pattern.sub(layer_const, src)
            fixes.append(f'AGENTIC_CORE_DIR / {layer_const} -> {layer_const}')
    return (src, fixes)

def process_file(filepath: Path) -> tuple[bool, list[str]]:
    src = filepath.read_text(encoding='utf-8')
    original = src
    all_fixes = []
    src, path_fixes = fix_double_paths(src)
    all_fixes.extend(path_fixes)
    try:
        tree = ast.parse(src)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, ['SyntaxError after double-path fix'])
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ALL_CONSTANTS:
            used.add(node.id)
    imported = get_imported_constants(src)
    missing = (used & ALL_CONSTANTS) - imported
    if missing:
        src = add_missing_to_import(src, missing)
        all_fixes.append(f'Added missing imports: {sorted(missing)}')
    try:
        ast.parse(src)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, [f'SyntaxError after fix: {e}'])
    if src != original:
        filepath.write_text(src, encoding='utf-8')
        return (True, all_fixes)
    return (True, [])

def main():
    tests_dir = ROOT / TESTS_DIR
    all_test_files = list(tests_dir.rglob('*.py'))
    fixed = 0
    errors = []
    for f in sorted(all_test_files):
        if '__pycache__' in str(f):
            continue
        ok, fixes = process_file(f)
        if not ok:
            errors.append((str(f.relative_to(ROOT)), fixes))
            print(f'ERROR: {f.relative_to(ROOT)}: {fixes}')
        elif fixes:
            fixed += 1
            rel = str(f.relative_to(ROOT))
            for fix in fixes:
                print(f'FIXED: {rel}: {fix}')
    print(f'\nDone: {fixed} files fixed, {len(errors)} errors.')
    for f, e in errors:
        print(f'  ERROR {f}: {e}')
if __name__ == '__main__':
    main()
