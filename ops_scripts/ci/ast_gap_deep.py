"""Deep gap analysis: per-layer breakdown for agentic_core, SSOT coverage."""

import ast
import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
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


def get_all_source_modules():
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
                    "layer": _extract_layer(rel, target),
                }
            except SyntaxError as e:
                modules[mod_name] = {
                    "path": rel,
                    "target": target,
                    "syntax_error": str(e),
                    "layer": _extract_layer(rel, target),
                }
    return modules


def _extract_layer(rel_path, target):
    parts = rel_path.split("/")
    if target == AGENTIC_CORE_DIR and len(parts) > 1:
        sub = parts[1]
        if sub.startswith("L"):
            return sub
        return sub
    if target in (APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR) and len(parts) > 1:
        return parts[1]
    if target == SYSTEM_LEARNING_DIR and len(parts) > 1:
        return parts[1]
    return target


def build_test_import_index():
    """Map module name prefix -> set of test files."""
    index = {}
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
                        _add_to_index(index, alias.name, rel)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        _add_to_index(index, node.module, rel)
        except SyntaxError:
            pass
    return index


def _add_to_index(index, module_name, test_path):
    index.setdefault(module_name, set()).add(test_path)
    # Also add parent packages
    parts = module_name.split(".")
    for depth in range(1, len(parts)):
        prefix = ".".join(parts[:depth])
        index.setdefault(prefix, set()).add(test_path)


def find_covering_tests(mod_name, index):
    parts = mod_name.split(".")
    covering = set()
    for depth in range(1, len(parts) + 1):
        prefix = ".".join(parts[:depth])
        if prefix in index:
            covering.update(index[prefix])
    return covering


def main():
    print("Building module index...")
    modules = get_all_source_modules()
    print("Building test import index...")
    test_index = build_test_import_index()

    # Layer-level aggregation
    layer_stats = {}
    uncovered = []
    covered = []

    for mod_name, info in modules.items():
        if "syntax_error" in info:
            continue
        layer = info.get("layer", "unknown")
        target = info["target"]
        layer_key = target + "/" + layer
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
        layer_stats[layer_key]["n_classes"] += info["n_classes"]
        layer_stats[layer_key]["n_funcs"] += info["n_funcs"]

        # Skip empty __init__ files
        path = info["path"]
        if path.endswith("__init__.py") and info["n_classes"] == 0 and info["n_funcs"] == 0:
            layer_stats[layer_key]["covered"] += 1
            continue

        tests = find_covering_tests(mod_name, test_index)
        if tests:
            layer_stats[layer_key]["covered"] += 1
            covered.append({"mod": mod_name, "path": path, "n_tests": len(tests)})
        else:
            layer_stats[layer_key]["uncovered"] += 1
            layer_stats[layer_key]["uncovered_paths"].append(path)
            n_sym = info["n_classes"] + info["n_funcs"]
            sev = "CRITICAL" if n_sym > 3 else ("HIGH" if n_sym > 0 else "LOW")
            uncovered.append(
                {
                    "mod": mod_name,
                    "path": path,
                    "target": target,
                    "layer": layer,
                    "n_classes": info["n_classes"],
                    "n_funcs": info["n_funcs"],
                    "top_classes": info["top_classes"],
                    "top_funcs": info["top_funcs"],
                    "severity": sev,
                }
            )

    print()
    print("=" * 70)
    print("LAYER-LEVEL COVERAGE BREAKDOWN")
    print("=" * 70)
    print("  " + "Layer".ljust(50) + "Files  Cov  Uncov  Classes  Funcs")
    for layer_key in sorted(layer_stats.keys()):
        s = layer_stats[layer_key]
        cov_pct = int(100 * s["covered"] / s["files"]) if s["files"] > 0 else 0
        line = (
            "  "
            + layer_key.ljust(50)
            + str(s["files"]).rjust(5)
            + str(s["covered"]).rjust(5)
            + str(s["uncovered"]).rjust(6)
            + str(s["n_classes"]).rjust(9)
            + str(s["n_funcs"]).rjust(7)
            + "  "
            + str(cov_pct)
            + "%"
        )
        flag = "  <<< ZERO COVERAGE" if s["covered"] == 0 and s["files"] > 0 else ""
        print(line + flag)

    print()
    print("=" * 70)
    print("UNCOVERED MODULES BY SEVERITY")
    print("=" * 70)
    by_sev = {}
    for u in uncovered:
        by_sev.setdefault(u["severity"], []).append(u)

    for sev in ["CRITICAL", "HIGH", "LOW"]:
        items = by_sev.get(sev, [])
        print()
        print("--- " + sev + " (" + str(len(items)) + " modules) ---")
        for item in sorted(items, key=lambda x: x["path"]):
            print("  [" + item["target"] + "/" + item["layer"] + "] " + item["path"])
            print("    classes: " + str(item["top_classes"]))
            print("    funcs:   " + str(item["top_funcs"]))

    print()
    print("=" * 70)
    print("GUARDIAN COVERAGE (tests/guardian -> what layers)")
    print("=" * 70)
    guardian_dir = ROOT / TESTS_DIR / "guardian"
    guardian_module_hits = {}
    for f in sorted(guardian_dir.rglob("test_*.py")):
        if "__pycache__" in str(f):
            continue
        rel = f.relative_to(ROOT).as_posix()
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
                            guardian_module_hits.setdefault(imp, set()).add(rel)
        except SyntaxError:
            pass

    print("  Guardian tests cover these source modules:")
    for mod in sorted(guardian_module_hits.keys()):
        print("    " + mod + " (" + str(len(guardian_module_hits[mod])) + " guardian files)")

    print()
    print("=" * 70)
    print("ZERO-COVERAGE LAYERS (entire layer has no tests)")
    print("=" * 70)
    for layer_key in sorted(layer_stats.keys()):
        s = layer_stats[layer_key]
        real_files = s["files"]
        if s["covered"] == 0 and real_files > 0:
            print("  ZERO: " + layer_key + " (" + str(real_files) + " files)")

    print()
    print("=" * 70)
    print("SUMMARY TOTALS")
    print("=" * 70)
    total_files = sum(s["files"] for s in layer_stats.values())
    total_cov = sum(s["covered"] for s in layer_stats.values())
    total_uncov = sum(s["uncovered"] for s in layer_stats.values())
    print("  Total source files: " + str(total_files))
    print("  Covered: " + str(total_cov))
    print("  Uncovered: " + str(total_uncov))
    print("  Overall coverage: " + str(int(100 * total_cov / total_files if total_files > 0 else 0)) + "%")
    print()
    print("  CRITICAL uncovered: " + str(len(by_sev.get("CRITICAL", []))))
    print("  HIGH uncovered:     " + str(len(by_sev.get("HIGH", []))))
    print("  LOW uncovered:      " + str(len(by_sev.get("LOW", []))))

    # Save full results
    out = {
        "layer_stats": {k: {**v, "uncovered_paths": v["uncovered_paths"]} for k, v in layer_stats.items()},
        "uncovered": uncovered,
        "guardian_module_hits": {k: sorted(v) for k, v in guardian_module_hits.items()},
        "summary": {
            "total_files": total_files,
            "covered": total_cov,
            "uncovered": total_uncov,
        },
    }
    out_path = ROOT / OPS_SCRIPTS_DIR / "ci" / "ast_gap_deep_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print()
    print("Full JSON: " + str(out_path))


if __name__ == "__main__":
    main()
