"""Triple-check: which of the 63 scanner-flagged violations are truly module-level."""

import json
from pathlib import Path

data = json.loads(Path("violation_audit.json").read_text())

LAYER_PREFIX_MAP = {
    "agentic_core/L0_routing": "L0",
    "agentic_core/L1_cognition": "L1",
    "agentic_core/L2_execution": "L2",
    "agentic_core/L3_orchestration": "L3",
    "agentic_core/L4_state": "L4",
    "agentic_core/L5_safety": "L5",
    "agentic_core/L6_observability": "L6",
    "agentic_core/utils": "L_SHARED",
    "agentic_core/seams": "L_SHARED",
    "agentic_core/embeddings": "L_SHARED",
    "agentic_core/base_agents": "L_SHARED",
    "agentic_core/evaluation": "L_SHARED",
    "agentic_core/patterns": "L_SHARED",
    "agentic_core/config": "L_SHARED",
    "agentic_core/mixins": "L_SHARED",
    "agentic_core/agents": "L_SHARED",
    "agentic_core/cache": "L_SHARED",
    "agentic_core/interfaces": "L_SHARED",
    "agentic_core/runtime": "L_RUNTIME",
    "agentic_core/prompt_governance": "L_PG",
    "agentic_core/adg": "L_TOOLS",
    "system_learning": "L_SL",
    "apps_shared": "L_APP",
    "apps_rg": "L_APP",
    "apps_lic": "L_APP",
}

ALLOWED = {
    ("L1", "L0"),
    ("L2", "L1"),
    ("L2", "L0"),
    ("L3", "L2"),
    ("L3", "L1"),
    ("L3", "L0"),
    ("L4", "L3"),
    ("L4", "L2"),
    ("L4", "L1"),
    ("L4", "L0"),
    ("L5", "L4"),
    ("L5", "L3"),
    ("L5", "L2"),
    ("L5", "L1"),
    ("L5", "L0"),
    ("L6", "L5"),
    ("L6", "L4"),
    ("L6", "L3"),
    ("L6", "L2"),
    ("L6", "L1"),
    ("L6", "L0"),
    ("L0", "L_SHARED"),
    ("L1", "L_SHARED"),
    ("L2", "L_SHARED"),
    ("L3", "L_SHARED"),
    ("L4", "L_SHARED"),
    ("L5", "L_SHARED"),
    ("L6", "L_SHARED"),
    ("L3", "L_RUNTIME"),
    ("L4", "L_RUNTIME"),
    ("L5", "L_RUNTIME"),
    ("L6", "L_RUNTIME"),
    ("L1", "L_RUNTIME"),
    ("L2", "L5"),
    ("L1", "L_PG"),
    ("L2", "L_PG"),
    ("L3", "L_PG"),
    ("L4", "L_PG"),
    ("L5", "L_PG"),
    ("L6", "L_PG"),
    ("L4", "L_TOOLS"),
    ("L_SL", "L2"),
    ("L_SL", "L1"),
    ("L_SL", "L0"),
    ("L_SL", "L_SHARED"),
    ("L_SL", "L5"),
    ("L_TOOLS", "L5"),
    ("L_TOOLS", "L4"),
    ("L_TOOLS", "L3"),
    ("L_TOOLS", "L2"),
    ("L_TOOLS", "L1"),
    ("L_TOOLS", "L0"),
    ("L_TOOLS", "L_SHARED"),
    ("L_TOOLS", "L_SL"),
    ("L_RUNTIME", "L0"),
    ("L_RUNTIME", "L1"),
    ("L_RUNTIME", "L2"),
    ("L_RUNTIME", "L3"),
    ("L_RUNTIME", "L4"),
    ("L_RUNTIME", "L5"),
    ("L_RUNTIME", "L_SHARED"),
    ("L_PG", "L0"),
    ("L_PG", "L1"),
    ("L_PG", "L2"),
    ("L_PG", "L_RUNTIME"),
    ("L_PG", "L4"),
    ("L_SHARED", "L0"),
    ("L_SHARED", "L_RUNTIME"),
    ("L_SHARED", "L5"),
    ("L_SHARED", "L2"),
    ("L_SHARED", "L1"),
    ("L_SHARED", "L_APP"),
    ("L_SHARED", "L_SHARED"),
    ("L_APP", "L6"),
    ("L_APP", "L5"),
    ("L_APP", "L4"),
    ("L_APP", "L3"),
    ("L_APP", "L2"),
    ("L_APP", "L1"),
    ("L_APP", "L0"),
    ("L_APP", "L_SHARED"),
    ("L_APP", "L_SL"),
    ("L_OPS", "L5"),
    ("L_OPS", "L4"),
    ("L_OPS", "L3"),
    ("L_OPS", "L2"),
    ("L_OPS", "L1"),
    ("L_OPS", "L0"),
    ("L_OPS", "L_SHARED"),
    ("L_OPS", "L_TOOLS"),
    ("L_OPS", "L_SL"),
    ("L_OPS", "L_APP"),
    ("L_OPS", "L_RUNTIME"),
}

STDLIB = {
    "__future__",
    "logging",
    "json",
    "sys",
    "os",
    "uuid",
    "time",
    "typing",
    "dataclasses",
    "enum",
    "pathlib",
    "asyncio",
    "hashlib",
    "threading",
    "shutil",
    "abc",
    "copy",
    "re",
    "io",
    "functools",
    "itertools",
    "collections",
    "warnings",
    "contextlib",
    "weakref",
    "inspect",
    "traceback",
    "subprocess",
    "tempfile",
    "socket",
    "http",
    "math",
    "random",
    "string",
    "struct",
    "datetime",
    "gc",
    "operator",
}

THIRD_PARTY = {
    "flask",
    "werkzeug",
    "requests",
    "pydantic",
    "numpy",
    "pandas",
    "chromadb",
    "watchdog",
    "websockets",
    "git",
    "yaml",
    "toml",
    "attrs",
    "cattrs",
    "click",
    "fastapi",
    "uvicorn",
    "starlette",
}


def get_layer(mod):
    imp_path = mod.replace(".", "/")
    for prefix, layer in sorted(LAYER_PREFIX_MAP.items(), key=lambda x: -len(x[0])):
        if imp_path.startswith(prefix):
            return layer
    return None


def get_file_layer(fpath):
    for prefix, layer in sorted(LAYER_PREFIX_MAP.items(), key=lambda x: -len(x[0])):
        if fpath.startswith(prefix):
            return layer
    return None


print("CONFIRMED MODULE-LEVEL VIOLATIONS (depth=0, not TYPE_CHECKING):")
print("=" * 70)

real = []
for entry in data:
    if "imports" not in entry:
        continue
    fpath = entry["file"]
    file_layer = get_file_layer(fpath)
    if not file_layer:
        continue
    for imp in entry["imports"]:
        if imp["depth"] != 0 or imp["in_type_checking"]:
            continue
        for mod in imp["modules"]:
            root = mod.split(".")[0]
            if root in STDLIB or root in THIRD_PARTY:
                continue
            imp_layer = get_layer(mod)
            if not imp_layer or imp_layer == file_layer:
                continue
            if (file_layer, imp_layer) not in ALLOWED:
                real.append(
                    {
                        "edge": f"{file_layer}->{imp_layer}",
                        "file": fpath,
                        "line": imp["line"],
                        "import": mod,
                        "code": imp["context"],
                    }
                )

# Group by edge
from collections import defaultdict

by_edge = defaultdict(list)
for v in real:
    by_edge[v["edge"]].append(v)

for edge, items in sorted(by_edge.items()):
    print(f"\n[{edge}] ({len(items)} violations)")
    for v in items:
        print(f"  {v['file']}:{v['line']}")
        print(f"    {v['code']}")

print(f"\nTOTAL CONFIRMED REAL VIOLATIONS: {len(real)}")
