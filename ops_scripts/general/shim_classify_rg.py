"""Classify shims in apps_rg/reasoning and across all SSOT dirs."""
import ast
from pathlib import Path


ROOT = Path('c:/Git/Agentic-Workflow')
SSOT_DIRS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]

def classify_file(py_file):
    rel = py_file.relative_to(ROOT).as_posix()
    try:
        src = py_file.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(src)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return None
    body = tree.body
    has_func = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for n in body)
    has_import = any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in body)
    imports = []
    for node in body:
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.append(('Import', a.name, a.asname))
        elif isinstance(node, ast.ImportFrom):
            names = [a.name for a in node.names]
            imports.append(('From', node.module or '', names))
    all_assigns = [n for n in body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__all__' for t in n.targets)]
    all_value = None
    if all_assigns:
        node = all_assigns[0]
        if isinstance(node.value, (ast.List, ast.Tuple)):
            all_value = [elt.s if isinstance(elt, ast.Constant) else '?' for elt in node.value.elts]
    stmt_types = [type(n).__name__ for n in body]
    non_trivial = [t for t in stmt_types if t not in ('Expr', 'Import', 'ImportFrom', 'Assign', 'AnnAssign')]
    is_shim_candidate = has_import and (not has_func) and (len(body) <= 20)
    if not is_shim_candidate:
        return None
    if all_assigns and (not non_trivial):
        shim_type = 'PURE_SHIM'
    elif not all_assigns and (not non_trivial):
        shim_type = 'SHIM_MISSING_ALL'
    elif non_trivial:
        shim_type = 'IMPURE_SHIM'
    else:
        shim_type = 'UNKNOWN'
    return {'file': rel, 'shim_type': shim_type, 'body_count': len(body), 'has_all': bool(all_assigns), 'all_value': all_value, 'non_trivial_stmts': non_trivial, 'imports': imports}
results = []
for ssot_dir in SSOT_DIRS:
    scan_root = ROOT / ssot_dir
    if not scan_root.exists():
        continue
    for py_file in sorted(scan_root.rglob('*.py')):
        if '.git' in py_file.parts:
            continue
        r = classify_file(py_file)
        if r:
            results.append(r)
pure_shims = [r for r in results if r['shim_type'] == 'PURE_SHIM']
missing_all = [r for r in results if r['shim_type'] == 'SHIM_MISSING_ALL']
impure = [r for r in results if r['shim_type'] == 'IMPURE_SHIM']
print('=== PURE SHIMS (intentional re-export, has __all__) ===')
for r in pure_shims:
    exported = r['all_value'] or '?'
    print(f"  {r['file']}  exports={exported}")
print(f'COUNT: {len(pure_shims)}')
print()
print('=== SHIMS MISSING __all__ (re-exports but no explicit export list) ===')
for r in missing_all:
    imp_summary = []
    for imp in r['imports']:
        if imp[0] == 'From':
            imp_summary.append(f'from {imp[1]} import {imp[2]}')
        else:
            imp_summary.append(f'import {imp[1]}')
    print(f"  {r['file']}  body={r['body_count']}")
    for s in imp_summary:
        print(f'    {s}')
print(f'COUNT: {len(missing_all)}')
print()
print('=== IMPURE SHIMS (no funcs/classes but has logic stmts) ===')
for r in impure:
    print(f"  {r['file']}  non_trivial={r['non_trivial_stmts']}  body={r['body_count']}")
print(f'COUNT: {len(impure)}')
print()
print(f'TOTAL_SHIM_CANDIDATES: {len(results)}')
