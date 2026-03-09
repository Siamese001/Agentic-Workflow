"""AST-based gap analysis: scans source modules and test coverage."""

import ast
import json
import sys
from pathlib import Path

ROOT = Path("c:/Git/Agentic-Workflow")
SOURCE_TARGETS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "system_learning",
    "L6_observability",
]
TEST_ROOT = ROOT / "tests"


def scan_source():
    results = {}
    for target in SOURCE_TARGETS:
        tpath = ROOT / target
        if not tpath.exists():
            results[target] = []
            continue
        modules = []
        for f in sorted(tpath.rglob("*.py")):
            rel = f.relative_to(ROOT).as_posix()
            if "__pycache__" in rel:
                continue
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
                top_classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
                top_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                all_classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                all_funcs = [
                    n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                modules.append(
                    {
                        "path": rel,
                        "top_classes": top_classes,
                        "top_funcs": top_funcs,
                        "n_classes": len(all_classes),
                        "n_funcs": len(all_funcs),
                    }
                )
            except SyntaxError as e:
                modules.append({"path": rel, "syntax_error": str(e)})
        results[target] = modules
    return results


def scan_tests():
    test_map = {}
    for f in sorted(TEST_ROOT.rglob("test_*.py")):
        rel = f.relative_to(ROOT).as_posix()
        if "__pycache__" in rel:
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            test_funcs = [
                n.name
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
            ]
            test_map[rel] = {
                "imports": sorted(set(imports)),
                "test_count": len(test_funcs),
            }
        except SyntaxError as e:
            test_map[rel] = {"syntax_error": str(e)}
    return test_map


def build_coverage_index(test_map):
    """Map source module prefix -> list of test files that import it."""
    coverage = {}
    for test_path, info in test_map.items():
        if "imports" not in info:
            continue
        for imp in info["imports"]:
            for target in SOURCE_TARGETS:
                if imp.startswith(target):
                    coverage.setdefault(imp, []).append(test_path)
    return coverage


def compute_gaps(source_results, coverage_index):
    gaps = []
    for target, modules in source_results.items():
        for mod in modules:
            if "syntax_error" in mod:
                gaps.append(
                    {
                        "path": mod["path"],
                        "target": target,
                        "severity": "SYNTAX_ERROR",
                        "reason": mod["syntax_error"],
                        "tests": [],
                    }
                )
                continue
            path = mod["path"]
            # Build importable module name from path
            mod_name = path.replace("/", ".").removesuffix(".py")
            # Also try parent packages
            parts = mod_name.split(".")
            covering_tests = set()
            # Match any prefix level
            for depth in range(1, len(parts) + 1):
                prefix = ".".join(parts[:depth])
                if prefix in coverage_index:
                    covering_tests.update(coverage_index[prefix])
            # Skip __init__ files with no classes/funcs
            if path.endswith("__init__.py") and mod["n_classes"] == 0 and mod["n_funcs"] == 0:
                continue
            n_cls = mod["n_classes"]
            n_fn = mod["n_funcs"]
            if not covering_tests:
                severity = "CRITICAL" if (n_cls + n_fn) > 3 else "HIGH" if (n_cls + n_fn) > 0 else "LOW"
                gaps.append(
                    {
                        "path": path,
                        "target": target,
                        "severity": severity,
                        "n_classes": n_cls,
                        "n_funcs": n_fn,
                        "top_classes": mod["top_classes"],
                        "reason": "NO_TEST_COVERAGE",
                        "tests": [],
                    }
                )
            else:
                gaps.append(
                    {
                        "path": path,
                        "target": target,
                        "severity": "COVERED",
                        "n_classes": n_cls,
                        "n_funcs": n_fn,
                        "top_classes": mod["top_classes"],
                        "reason": "covered",
                        "tests": sorted(covering_tests),
                    }
                )
    return gaps


def main():
    print("Scanning source modules...")
    source_results = scan_source()

    print("Scanning test files...")
    test_map = scan_tests()

    print("Building coverage index...")
    coverage_index = build_coverage_index(test_map)

    print("Computing gaps...")
    gaps = compute_gaps(source_results, coverage_index)

    # Summary
    by_sev = {}
    for g in gaps:
        by_sev.setdefault(g["severity"], []).append(g)

    print("\n=== SUMMARY ===")
    for sev in ["CRITICAL", "HIGH", "LOW", "SYNTAX_ERROR", "COVERED"]:
        items = by_sev.get(sev, [])
        print(f"  {sev}: {len(items)}")

    # Per-target breakdown
    print("\n=== PER-TARGET MODULE COUNTS ===")
    for target, modules in source_results.items():
        good = [m for m in modules if "syntax_error" not in m]
        n_cls = sum(m.get("n_classes", 0) for m in good)
        n_fn = sum(m.get("n_funcs", 0) for m in good)
        print(f"  {target}: {len(good)} files, {n_cls} classes, {n_fn} funcs")

    print("\n=== CRITICAL GAPS (no tests, >3 symbols) ===")
    for g in sorted(by_sev.get("CRITICAL", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  classes={g['n_classes']} funcs={g['n_funcs']}  top={g['top_classes']}")

    print("\n=== HIGH GAPS (no tests, 1-3 symbols) ===")
    for g in sorted(by_sev.get("HIGH", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  classes={g['n_classes']} funcs={g['n_funcs']}  top={g['top_classes']}")

    print("\n=== COVERED MODULES ===")
    for g in sorted(by_sev.get("COVERED", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  ({len(g['tests'])} test files)")

    # Save full JSON for report writing
    output = {
        "source_summary": {
            t: {
                "files": len([m for m in mods if "syntax_error" not in m]),
                "n_classes": sum(m.get("n_classes", 0) for m in mods if "syntax_error" not in m),
                "n_funcs": sum(m.get("n_funcs", 0) for m in mods if "syntax_error" not in m),
                "syntax_errors": [m for m in mods if "syntax_error" in m],
            }
            for t, mods in source_results.items()
        },
        "test_summary": {
            "total_test_files": len(test_map),
            "total_test_funcs": sum(
                v.get("test_count", 0) for v in test_map.values() if "syntax_error" not in v
            ),
            "syntax_errors": [p for p, v in test_map.items() if "syntax_error" in v],
        },
        "coverage_gaps": [g for g in gaps if g["severity"] != "COVERED"],
        "covered": [g for g in gaps if g["severity"] == "COVERED"],
    }
    out_path = ROOT / "ops_scripts" / "ci" / "ast_gap_results.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nFull results written to: {out_path}")
    return output


if __name__ == "__main__":
    main()
