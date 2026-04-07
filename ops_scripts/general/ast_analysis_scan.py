"""AST analysis scan: pinecone refs, semantic cache, shim classification."""
import ast
import json
from pathlib import Path

ROOT = Path('c:/Git/Agentic-Workflow')
SSOT_DIRS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR, 'tools/evidence', OPS_SCRIPTS_DIR]

def parse_file(py_file):
    try:
        src = py_file.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(src, filename=str(py_file))
        return (src, tree)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        print(f'SYNTAX_ERR: {py_file.relative_to(ROOT).as_posix()}: {e}')
        return (None, None)

def get_imports(tree):
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or '')
    return imports

def scan_pinecone(rel, src, tree, imports):
    hits = [i for i in imports if 'pinecone' in i.lower()]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if 'pinecone' in node.value.lower():
                hits.append('literal:' + node.value[:60])
        elif isinstance(node, ast.Attribute):
            if 'pinecone' in (node.attr or '').lower():
                hits.append('attr:' + node.attr)
    if hits:
        return {'file': rel, 'refs': list(dict.fromkeys(hits))[:10]}
    return None

def scan_semantic_cache(rel, src, tree, imports):
    hits = [i for i in imports if 'cache' in i.lower() or 'semantic' in i.lower()]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value.lower()
            if 'semantic_cache' in v or 'semanticcache' in v:
                hits.append('literal:' + node.value[:60])
        elif isinstance(node, ast.Name):
            if 'semantic_cache' in node.id.lower():
                hits.append('name:' + node.id)
        elif isinstance(node, ast.Attribute):
            if 'semantic_cache' in (node.attr or '').lower():
                hits.append('attr:' + node.attr)
    if hits:
        return {'file': rel, 'refs': list(dict.fromkeys(hits))[:8]}
    return None

def classify_shim(rel, tree):
    body = tree.body
    has_func = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for n in body)
    has_import = any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in body)
    if has_func or not has_import:
        return None
    if len(body) > 20:
        return None
    all_assigns = [n for n in body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__all__' for t in n.targets)]
    stmt_types = [type(n).__name__ for n in body]
    is_pure_shim = all(t in ('Expr', 'Import', 'ImportFrom', 'Assign') for t in stmt_types)
    return {'file': rel, 'body_count': len(body), 'has_all': bool(all_assigns), 'is_pure_shim': is_pure_shim, 'stmt_types': stmt_types}
pinecone_refs = []
semantic_cache_refs = []
shim_files = []
for ssot_dir in SSOT_DIRS:
    scan_root = ROOT / ssot_dir
    if not scan_root.exists():
        continue
    for py_file in sorted(scan_root.rglob('*.py')):
        if '.git' in py_file.parts:
            continue
        rel = py_file.relative_to(ROOT).as_posix()
        src, tree = parse_file(py_file)
        if tree is None:
            continue
        imports = get_imports(tree)
        r = scan_pinecone(rel, src, tree, imports)
        if r:
            pinecone_refs.append(r)
        r = scan_semantic_cache(rel, src, tree, imports)
        if r:
            semantic_cache_refs.append(r)
        r = classify_shim(rel, tree)
        if r:
            shim_files.append(r)
print('=== PINECONE REFS (SSOT DIRS) ===')
for item in pinecone_refs:
    print(f"  {item['file']}")
    for ref in item['refs']:
        print(f'    - {ref}')
print(f'TOTAL_PINECONE_FILES: {len(pinecone_refs)}')
print()
print('=== SEMANTIC CACHE REFS (SSOT DIRS) ===')
for item in semantic_cache_refs[:30]:
    print(f"  {item['file']}")
    for ref in item['refs']:
        print(f'    - {ref}')
print(f'TOTAL_CACHE_FILES: {len(semantic_cache_refs)}')
print()
pure_shims = [s for s in shim_files if s['is_pure_shim'] and s['has_all']]
shims_missing_all = [s for s in shim_files if s['is_pure_shim'] and (not s['has_all'])]
impure_shims = [s for s in shim_files if not s['is_pure_shim']]
print('=== PURE SHIMS (imports + __all__ only) ===')
for s in pure_shims:
    print(f"  {s['file']}  body={s['body_count']}")
print(f'TOTAL_PURE_SHIMS: {len(pure_shims)}')
print()
print('=== SHIMS MISSING __all__ ===')
for s in shims_missing_all:
    print(f"  {s['file']}  body={s['body_count']}  stmts={s['stmt_types']}")
print(f'TOTAL_SHIMS_MISSING_ALL: {len(shims_missing_all)}')
print()
print('=== IMPURE SHIM CANDIDATES (no functions but has extra logic) ===')
for s in impure_shims:
    print(f"  {s['file']}  body={s['body_count']}  stmts={s['stmt_types']}")
print(f'TOTAL_IMPURE: {len(impure_shims)}')
