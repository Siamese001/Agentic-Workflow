#!/usr/bin/env python3
"""Identify dead code using ADG snapshot signals."""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List


def parse_adg_snapshot(snapshot_path: str) -> Dict:
    """Parse ADG snapshot for dead code signals."""
    with open(snapshot_path, "r") as f:
        return json.load(f)


def find_unused_imports(file_path: Path) -> List[Dict]:
    """Find potentially unused imports in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        # Collect all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )

        # Simple heuristic: if import name never appears in the rest of the file
        # This is a basic check - full analysis would need symbol resolution
        unused = []
        for imp in imports:
            import_name = imp["alias"] if imp["alias"] else imp["name"]
            if import_name == "*":
                continue  # Can't determine usage for star imports

            # Check if the imported name appears in the code
            pattern = r"\b" + re.escape(import_name) + r"\b"
            matches = re.findall(pattern, content)

            # Subtract the import statement itself
            if len(matches) <= 1:
                unused.append(imp)

        return unused
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return [{"error": str(e)}]


def find_duplicate_methods(file_path: Path) -> List[Dict]:
    """Find potentially duplicate methods in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        # Collect all function definitions with signatures
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                sig = f"{node.name}_{len(node.args.args)}"
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "signature": sig,
                    }
                )

        # Find duplicates by signature
        seen = {}
        duplicates = []
        for func in functions:
            if func["signature"] in seen:
                duplicates.append(
                    {
                        "function": func["name"],
                        "line": func["line"],
                        "duplicate_of": seen[func["signature"]],
                    }
                )
            else:
                seen[func["signature"]] = func["name"]

        return duplicates
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return [{"error": str(e)}]


def analyze_dead_code(target_dir: str, snapshot_path: str) -> Dict:
    """Analyze dead code in target directory."""
    results = {
        "target_dir": target_dir,
        "adg_signals": {},
        "file_analysis": {},
        "summary": {
            "files_analyzed": 0,
            "unused_imports": 0,
            "duplicate_methods": 0,
        },
    }

    # Parse ADG snapshot
    snapshot = parse_adg_snapshot(snapshot_path)
    results["adg_signals"] = {
        "unused_imports": snapshot.get("graph_plane_counts", {}).get("unused_import", 0),
        "dead_imports": snapshot.get("graph_plane_counts", {}).get("dead_imports", 0),
        "unreachable_after_raise": snapshot.get("graph_plane_counts", {}).get("unreachable_after_raise", 0),
        "duplicate_method": snapshot.get("graph_plane_counts", {}).get("duplicate_method", 0),
    }

    # Analyze Python files in target directory
    root = Path(target_dir)
    py_files = list(root.rglob("*.py"))

    for py_file in py_files:
        if "__pycache__" in str(py_file):
            continue

        relative_path = str(py_file.relative_to(root.parent))

        unused_imports = find_unused_imports(py_file)
        duplicate_methods = find_duplicate_methods(py_file)

        if unused_imports or duplicate_methods:
            results["file_analysis"][relative_path] = {
                "unused_imports": unused_imports,
                "duplicate_methods": duplicate_methods,
            }

            results["summary"]["unused_imports"] += len(unused_imports)
            results["summary"]["duplicate_methods"] += len(duplicate_methods)

        results["summary"]["files_analyzed"] += 1

    return results


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python dead_code_detector.py <target_dir> <adg_snapshot> [output_file]")
        sys.exit(1)

    target_dir = sys.argv[1]
    snapshot_path = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Analyzing dead code in: {target_dir}")
    print(f"Using ADG snapshot: {snapshot_path}")
    print("=" * 70)

    results = analyze_dead_code(target_dir, snapshot_path)

    print("\nADG Dead Code Signals:")
    print(f"  Unused imports: {results['adg_signals']['unused_imports']}")
    print(f"  Dead imports: {results['adg_signals']['dead_imports']}")
    print(f"  Unreachable after raise: {results['adg_signals']['unreachable_after_raise']}")
    print(f"  Duplicate methods: {results['adg_signals']['duplicate_method']}")

    print("\nFile Analysis Summary:")
    print(f"  Files analyzed: {results['summary']['files_analyzed']}")
    print(f"  Files with issues: {len(results['file_analysis'])}")
    print(f"  Potential unused imports: {results['summary']['unused_imports']}")
    print(f"  Potential duplicate methods: {results['summary']['duplicate_methods']}")

    if results["file_analysis"]:
        print("\nFiles with dead code issues:")
        for file_path, issues in results["file_analysis"].items():
            print(f"  {file_path}:")
            if issues["unused_imports"]:
                for imp in issues["unused_imports"]:
                    if "error" not in imp:
                        print(
                            f"    - Unused import at line {imp['line']}: {imp.get('name', imp.get('module', ''))}"
                        )
            if issues["duplicate_methods"]:
                for dup in issues["duplicate_methods"]:
                    print(f"    - Duplicate method '{dup['function']}' at line {dup['line']}")

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nDetailed report saved to: {output_file}")


if __name__ == "__main__":
    main()
