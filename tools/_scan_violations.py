"""One-shot violation scan using both scanners."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ops_scripts.ci.ast_layer_sovereignty_scanner import (
    _EXCLUDE_DIRS,
    _APPS_PREFIXES,
    _L_LAYER_PREFIX,
    _LAYER_RULES,
    _extract_imported_modules,
    _layer_prefix_of,
)
from ops_scripts.ci.validate_layer_violations import analyze_file
from agentic_core.L0_routing.config.path_constants import get_validated_project_root

repo_root = get_validated_project_root()

# --- validate_layer_violations scan (catches L_SHARED etc.) ---
print("=== validate_layer_violations results ===")
vv_violations = []
for py_file in sorted(repo_root.rglob("agentic_core/**/*.py")):
    if any(part in _EXCLUDE_DIRS for part in py_file.parts):
        continue
    vs = analyze_file(py_file, repo_root)
    vv_violations.extend(vs)

for v in vv_violations:
    rel = str(Path(v["file"]).relative_to(repo_root))
    print(f"  {v['edge']:25s}  {rel}:{v['line']}")
print(f"Total: {len(vv_violations)}")

# --- ast_layer_sovereignty_scanner (catches L3->L5 etc.) ---
print("\n=== ast_layer_sovereignty_scanner results ===")
ast_violations = []
for py_file in sorted(repo_root.rglob("agentic_core/**/*.py")):
    if any(part in _EXCLUDE_DIRS for part in py_file.parts):
        continue
    source_layer = _layer_prefix_of(py_file)
    if source_layer is None:
        continue
    try:
        import ast
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError:
        continue
    imports = _extract_imported_modules(tree)
    if source_layer in _LAYER_RULES:
        forbidden = _LAYER_RULES[source_layer]
        for lineno, mod in imports:
            for fp in forbidden:
                if mod == fp or mod.startswith(fp + "."):
                    rel = str(py_file.relative_to(repo_root))
                    ast_violations.append(f"  {source_layer} -> {mod}  {rel}:{lineno}")

for v in ast_violations:
    print(v)
print(f"Total: {len(ast_violations)}")
