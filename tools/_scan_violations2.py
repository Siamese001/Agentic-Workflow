"""Targeted scan: L_SHARED violations only, plus TYPE_CHECKING false positives."""
import sys, ast
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ops_scripts.ci.validate_layer_violations import analyze_file, ALLOWED_EDGES, get_layer_from_path
from ops_scripts.ci.ast_layer_sovereignty_scanner import (
    _EXCLUDE_DIRS, _extract_imported_modules, _layer_prefix_of, _LAYER_RULES,
)
from agentic_core.L0_routing.config.path_constants import get_validated_project_root

repo_root = get_validated_project_root()

# 1. L_SHARED violations from validate_layer_violations
print("=== L_SHARED violations (validate_layer_violations) ===")
shared_v = []
for py_file in sorted(repo_root.rglob("agentic_core/**/*.py")):
    if any(part in _EXCLUDE_DIRS for part in py_file.parts):
        continue
    vs = analyze_file(py_file, repo_root)
    for v in vs:
        if "L_SHARED" in v["edge"]:
            shared_v.append(v)

for v in shared_v:
    rel = str(Path(v["file"]).relative_to(repo_root))
    print(f"  {v['edge']:30s}  {rel}:{v['line']}  import={v['import']}")
print(f"Total L_SHARED: {len(shared_v)}")

# 2. TYPE_CHECKING false positives — ast_layer_sovereignty_scanner uses flat ast.walk
#    so it sees imports inside `if TYPE_CHECKING:` blocks.
#    Show which files have TYPE_CHECKING-guarded L5/L6 imports the old scanner would flag.
print("\n=== TYPE_CHECKING false positives (ast_layer_sovereignty_scanner raw walk) ===")
tc_files = [
    repo_root / "agentic_core/agents/adg_backed_registry.py",
    repo_root / "agentic_core/cache/graph_aware_cache.py",
]
for fp in tc_files:
    if not fp.exists():
        print(f"  NOT FOUND: {fp}")
        continue
    source = fp.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = _extract_imported_modules(tree)
    layer = _layer_prefix_of(fp)
    print(f"  {fp.relative_to(repo_root)}  (layer={layer})")
    if layer and layer in _LAYER_RULES:
        forbidden = _LAYER_RULES[layer]
        for lineno, mod in imports:
            for fbp in forbidden:
                if mod == fbp or mod.startswith(fbp + "."):
                    print(f"    FALSE POSITIVE line {lineno}: {mod}")
