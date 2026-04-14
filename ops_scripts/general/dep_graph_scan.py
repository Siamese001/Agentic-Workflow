"""AST-based dependency graph analysis: what exists, what is missing, what would be needed."""

import ast
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)
from tqdm import tqdm


def _resolve_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


ROOT = _resolve_root()
SSOT_DIRS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]


def get_imports(tree):
    deps = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                deps.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                deps.append(node.module)
    return deps


def find_cycles(graph):
    visited = set()
    rec_stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, set()):
            if neighbor not in graph:
                continue
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycles.append(path[cycle_start:] + [neighbor])
        rec_stack.discard(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [node])
    return cycles


LAYER_ORDER = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}


def get_layer(mod):
    for layer_name, rank in LAYER_ORDER.items():
        if layer_name in mod:
            return (rank, layer_name)
    return (-1, None)


def main() -> int:
    import_graph = defaultdict(set)
    module_to_file = {}
    syntax_errors = []

    for d in tqdm(SSOT_DIRS, desc="Processing", unit="item"):
        scan_root = ROOT / d
        if not scan_root.exists():
            continue
        for py in tqdm(sorted(scan_root.rglob("*.py")), desc="Processing", unit="item"):
            if ".git" in py.parts:
                continue
            rel = py.relative_to(ROOT).as_posix()
            mod = rel.replace("/", ".").removesuffix(".py")
            module_to_file[mod] = rel
            try:
                src = py.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except SyntaxError as e:
                syntax_errors.append((rel, str(e)))
                continue
            for dep in get_imports(tree):
                if any(dep.startswith(d.replace("/", ".")) for d in SSOT_DIRS):
                    import_graph[mod].add(dep)

    cycles = find_cycles(import_graph)
    layer_inversions = []
    for mod, deps in import_graph.items():
        src_rank, src_layer = get_layer(mod)
        if src_rank < 0:
            continue
        for dep in deps:
            dep_rank, dep_layer = get_layer(dep)
            if dep_rank < 0:
                continue
            if dep_rank > src_rank:
                layer_inversions.append((mod, src_layer, dep, dep_layer))

    fan_out = {mod: len(deps) for mod, deps in import_graph.items()}
    fan_in = defaultdict(int)
    for mod, deps in import_graph.items():
        for dep in deps:
            fan_in[dep] += 1

    top_fan_in = sorted(fan_in.items(), key=lambda x: x[1], reverse=True)[:20]
    top_fan_out = sorted(fan_out.items(), key=lambda x: x[1], reverse=True)[:15]
    all_imported = set(fan_in.keys())
    orphans = [
        mod
        for mod in module_to_file
        if mod not in all_imported and (not import_graph.get(mod)) and (not mod.endswith("__init__"))
    ]

    print("=== CYCLE DETECTION ===")
    if cycles:
        for c in cycles[:10]:
            print(" CYCLE:", " -> ".join(c))
    else:
        print(" No cycles detected in SSOT dirs")
    print(f"TOTAL_CYCLES: {len(cycles)}")
    print()

    print("=== LAYER INVERSIONS ===")
    for mod, src_layer, dep, dep_layer in layer_inversions[:20]:
        print(f"  INVERSION: {mod} ({src_layer}) -> {dep} ({dep_layer})")
    print(f"TOTAL_INVERSIONS: {len(layer_inversions)}")
    print()

    print("=== TOP FAN-IN (most imported modules = highest-value nodes) ===")
    for mod, count in top_fan_in:
        print(f"  {count:3d}  {mod}")
    print()

    print("=== TOP FAN-OUT (most dependencies = highest coupling) ===")
    for mod, count in top_fan_out:
        print(f"  {count:3d}  {mod}")
    print()

    print(f"TOTAL_MODULES_IN_GRAPH: {len(import_graph)}")
    print(f"TOTAL_UNIQUE_MODULES: {len(module_to_file)}")
    print(f"TOTAL_ORPHANS (no imports/importers): {len(orphans)}")
    print(f"SYNTAX_ERRORS: {len(syntax_errors)}")

    existing_tools = []
    for py in tqdm(ROOT.rglob("*.py"), desc="Processing", unit="item"):
        if ".git" in py.parts:
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        if any(
            kw in src
            for kw in ["import_graph", "dependency_graph", "dep_graph", "cycle_detect", "ImportGraph"]
        ):
            rel = py.relative_to(ROOT).as_posix()
            existing_tools.append(rel)

    print()
    print("=== EXISTING DEP GRAPH TOOLING ===")
    for t in existing_tools[:15]:
        print(" ", t)
    print(f"COUNT: {len(existing_tools)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
