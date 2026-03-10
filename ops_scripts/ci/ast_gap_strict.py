"""
Strict gap analysis: a source module is COVERED only if a test file imports
it by its *exact* dotted module name (or one of its direct children).
Parent-package membership alone does NOT count as coverage.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    get_validated_project_root,
)

ROOT = get_validated_project_root()
SOURCE_TARGETS = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    "L6_observability",
]


# ---------------------------------------------------------------------------
# 1. Collect all source modules
# ---------------------------------------------------------------------------
def collect_source_modules():
    modules = {}
    for target in SOURCE_TARGETS:
        tpath = ROOT / target
        if not tpath.exists():
            continue
        for f in sorted(tpath.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            rel = f.relative_to(ROOT).as_posix()
            mod_name = rel.replace("/", ".").removesuffix(".py")
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
                top_classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
                top_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                all_classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                all_funcs = [
                    n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                modules[mod_name] = {
                    "path": rel,
                    "target": target,
                    "top_classes": top_classes,
                    "top_funcs": top_funcs,
                    "n_classes": len(all_classes),
                    "n_funcs": len(all_funcs),
                    "layer": _layer(rel, target),
                }
            except SyntaxError as e:
                modules[mod_name] = {
                    "path": rel,
                    "target": target,
                    "syntax_error": str(e),
                    "layer": _layer(rel, target),
                }
    return modules


def _layer(rel_path, target):
    parts = rel_path.split("/")
    if len(parts) > 1 and parts[1] != "__init__.py":
        return parts[1]
    return target


# ---------------------------------------------------------------------------
# 2. Build EXACT-match import index: mod_name -> set of test paths
# ---------------------------------------------------------------------------
def build_exact_import_index():
    """Only exact import strings — no parent propagation."""
    index = defaultdict(set)
    test_root = ROOT / TESTS_DIR
    for f in sorted(test_root.rglob("test_*.py")):
        if "__pycache__" in str(f):
            continue
        rel = f.relative_to(ROOT).as_posix()
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        index[alias.name].add(rel)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    index[node.module].add(rel)
                    # Also credit the names imported from the module
                    for alias in node.names:
                        index[node.module + "." + alias.name].add(rel)
        except SyntaxError:
            pass
    return index


# ---------------------------------------------------------------------------
# 3. Determine coverage for a module
# ---------------------------------------------------------------------------
def is_covered(mod_name, index):
    """
    A module is covered if:
      - it is directly imported, OR
      - one of its direct children (depth+1) is imported.
    We do NOT propagate upward — importing agentic_core.L0_routing does NOT
    cover agentic_core.L0_routing.types.foo.
    """
    if mod_name in index:
        return True
    # One level down (direct children only, not deep descendants)
    prefix = mod_name + "."
    return any(k.startswith(prefix) and k.count(".") == mod_name.count(".") + 1 for k in index)


# ---------------------------------------------------------------------------
# 4. Main analysis
# ---------------------------------------------------------------------------
def main():
    print("Collecting source modules...")
    modules = collect_source_modules()
    print("Building exact import index...")
    index = build_exact_import_index()

    # ---- per-layer stats ----
    layer_stats = {}
    uncovered_list = []
    covered_list = []

    for mod_name, info in modules.items():
        layer_key = info["target"] + "/" + info["layer"]
        if layer_key not in layer_stats:
            layer_stats[layer_key] = {
                "files": 0,
                "covered": 0,
                "uncovered": 0,
                "n_classes": 0,
                "n_funcs": 0,
                "uncovered_paths": [],
            }
        layer_stats[layer_key]["files"] += 1

        if "syntax_error" in info:
            layer_stats[layer_key]["uncovered"] += 1
            layer_stats[layer_key]["uncovered_paths"].append(info["path"] + "  [SYNTAX_ERROR]")
            continue

        path = info["path"]
        n_cls = info["n_classes"]
        n_fn = info["n_funcs"]
        layer_stats[layer_key]["n_classes"] += n_cls
        layer_stats[layer_key]["n_funcs"] += n_fn

        # Empty __init__ files don't need dedicated tests
        if path.endswith("__init__.py") and n_cls == 0 and n_fn == 0:
            layer_stats[layer_key]["covered"] += 1
            continue

        covered = is_covered(mod_name, index)
        if covered:
            layer_stats[layer_key]["covered"] += 1
            covered_list.append({"mod": mod_name, "path": path})
        else:
            layer_stats[layer_key]["uncovered"] += 1
            layer_stats[layer_key]["uncovered_paths"].append(path)
            n_sym = n_cls + n_fn
            sev = "CRITICAL" if n_sym > 5 else ("HIGH" if n_sym > 1 else "LOW")
            uncovered_list.append(
                {
                    "mod": mod_name,
                    "path": path,
                    "target": info["target"],
                    "layer": info["layer"],
                    "n_classes": n_cls,
                    "n_funcs": n_fn,
                    "top_classes": info["top_classes"],
                    "top_funcs": info["top_funcs"],
                    "severity": sev,
                }
            )

    # ---- print layer breakdown ----
    print()
    print("=" * 80)
    print("LAYER-LEVEL COVERAGE BREAKDOWN  (strict exact-import matching)")
    print("=" * 80)
    header = "  " + "Layer".ljust(52) + "Files  Cov  Unc  Cls   Fn  Cov%"
    print(header)
    print("  " + "-" * 78)
    for lk in sorted(layer_stats.keys()):
        s = layer_stats[lk]
        pct = int(100 * s["covered"] / s["files"]) if s["files"] > 0 else 0
        flag = "  *** ZERO ***" if s["covered"] == 0 and s["files"] > 0 else ""
        row = (
            "  "
            + lk.ljust(52)
            + str(s["files"]).rjust(5)
            + str(s["covered"]).rjust(5)
            + str(s["uncovered"]).rjust(5)
            + str(s["n_classes"]).rjust(5)
            + str(s["n_funcs"]).rjust(5)
            + str(pct).rjust(5)
            + "%"
            + flag
        )
        print(row)

    # ---- severity breakdown ----
    by_sev = defaultdict(list)
    for u in uncovered_list:
        by_sev[u["severity"]].append(u)

    print()
    print("=" * 80)
    print("UNCOVERED MODULES — CRITICAL (>5 symbols)")
    print("=" * 80)
    for item in sorted(by_sev.get("CRITICAL", []), key=lambda x: x["path"]):
        print("  [" + item["target"] + "/" + item["layer"] + "]  " + item["path"])
        if item["top_classes"]:
            print("      classes: " + str(item["top_classes"]))
        if item["top_funcs"]:
            print("      funcs  : " + str(item["top_funcs"]))

    print()
    print("=" * 80)
    print("UNCOVERED MODULES — HIGH (2-5 symbols)")
    print("=" * 80)
    for item in sorted(by_sev.get("HIGH", []), key=lambda x: x["path"]):
        print("  [" + item["target"] + "/" + item["layer"] + "]  " + item["path"])
        if item["top_classes"]:
            print("      classes: " + str(item["top_classes"]))
        if item["top_funcs"]:
            print("      funcs  : " + str(item["top_funcs"]))

    print()
    print("=" * 80)
    print("UNCOVERED MODULES — LOW (0-1 symbols)")
    print("=" * 80)
    for item in sorted(by_sev.get("LOW", []), key=lambda x: x["path"]):
        print("  [" + item["target"] + "/" + item["layer"] + "]  " + item["path"])

    # ---- guardian layer focus ----
    print()
    print("=" * 80)
    print("GUARDIAN TESTS — LAYER FOCUS (tests/guardian/)")
    print("=" * 80)
    guardian_layers = defaultdict(int)
    guardian_dir = ROOT / TESTS_DIR / "guardian"
    for f in sorted(guardian_dir.rglob("test_*.py")):
        if "__pycache__" in str(f):
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                imp = None
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imp = alias.name
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imp = node.module
                if imp:
                    for tgt in SOURCE_TARGETS:
                        if imp.startswith(tgt):
                            parts = imp.split(".")
                            layer_id = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
                            guardian_layers[layer_id] += 1
        except SyntaxError:
            pass
    for lk in sorted(guardian_layers.keys()):
        print("  " + lk + ": " + str(guardian_layers[lk]) + " import refs")

    # Layers with NO guardian tests
    print()
    print("Layers with NO guardian test coverage:")
    all_layer_roots = set()
    for mod_name in modules:
        parts = mod_name.split(".")
        root2 = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
        all_layer_roots.add(root2)
    for lr in sorted(all_layer_roots):
        if lr not in guardian_layers:
            # Only flag non-trivial ones (not just __init__)
            count = sum(1 for m in modules if m.startswith(lr + ".") or m == lr)
            if count > 2:
                print("  MISSING guardian: " + lr + " (" + str(count) + " modules)")

    # ---- summary ----
    total_f = sum(s["files"] for s in layer_stats.values())
    total_c = sum(s["covered"] for s in layer_stats.values())
    total_u = sum(s["uncovered"] for s in layer_stats.values())
    print()
    print("=" * 80)
    print("TOTALS")
    print("=" * 80)
    print("  Source files scanned  : " + str(total_f))
    print("  Directly covered      : " + str(total_c))
    print("  Uncovered             : " + str(total_u))
    print("  Overall coverage      : " + str(int(100 * total_c / total_f if total_f > 0 else 0)) + "%")
    print("  CRITICAL gaps         : " + str(len(by_sev.get("CRITICAL", []))))
    print("  HIGH gaps             : " + str(len(by_sev.get("HIGH", []))))
    print("  LOW gaps              : " + str(len(by_sev.get("LOW", []))))
    print("  Test files (total)    : " + str(sum(1 for _ in (ROOT / TESTS_DIR).rglob("test_*.py"))))
    print("  Guardian test files   : " + str(sum(1 for _ in guardian_dir.rglob("test_*.py"))))

    # Save JSON
    out_path = ROOT / OPS_SCRIPTS_DIR / "ci" / "ast_gap_strict_results.json"
    out_path.write_text(
        json.dumps(
            {
                "layer_stats": layer_stats,
                "uncovered": uncovered_list,
                "covered_count": len(covered_list),
                "guardian_layer_hits": dict(guardian_layers),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print()
    print("JSON saved: " + str(out_path))


if __name__ == "__main__":
    main()
