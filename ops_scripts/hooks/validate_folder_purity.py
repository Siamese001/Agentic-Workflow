#!/usr/bin/env python3
"""
Folder Purity Validation Hook for Pre-commit.

Blocks commits that violate architectural folder placement rules:
- Agent files must be in reasoning/ folders
- _types files must be in types/ folders and contain only type definitions
- Engine/Executor files must be in engines/ folders (with exceptions)

Uses baseline subtraction to allow pre-existing violations while preventing new ones.
"""

import argparse
import ast
import re
import sys
from pathlib import Path


# Transient / non-source directories excluded from all scans.
_EXCLUDE_DIRS = {
    "__pycache__", ".git", ".venv", "venv",
    ".pytest_cache", ".pytest_tmp", ".mypy_cache", ".ruff_cache",
    ".coverage", "dist", "build", ".tox", ".nox",
    "node_modules", "archives", ".backup", "_quarantine",
    "tests",
}


def _is_excluded(path: Path) -> bool:
    """Return True if any path component is in the exclusion set."""
    return bool(set(path.parts) & _EXCLUDE_DIRS)


def check_agent_placement():
    """Check that Agent files are in reasoning/ folders only."""
    violations = []

    # Only scan project directories
    project_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

    for py_file in sorted(Path(".").rglob("*.py")):
        if _is_excluded(py_file):
            continue

        # Skip if not in a project directory
        if not any(project_dir in py_file.parts for project_dir in project_dirs):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")

            # Check if file contains an Agent class
            if re.search(r"class\s+\w*Agent\w*\s*\(", content):
                rel_path = str(py_file).replace("\\", "/")

                # Check if Agent is in wrong folder
                if "/engines/" in rel_path:
                    violations.append(f"X Agent in engines/: {rel_path}")
                elif "/types/" in rel_path:
                    violations.append(f"X Agent in types/: {rel_path}")
                elif "/utils/" in rel_path:
                    violations.append(f"X Agent in utils/: {rel_path}")
                elif "/validators/" in rel_path:
                    violations.append(f"X Agent in validators/: {rel_path}")
                elif "/config/" in rel_path:
                    violations.append(f"X Agent in config/: {rel_path}")
                elif "/reasoning/" not in rel_path:
                    violations.append(f"X Agent not in reasoning/: {rel_path}")

        except (UnicodeDecodeError, OSError):
            continue

    return violations


def check_types_purity():
    """Check that _types files contain only type definitions."""
    violations = []

    # Only scan project directories
    project_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

    for py_file in sorted(Path(".").rglob("*_types.py")):
        if _is_excluded(py_file):
            continue

        # Skip if not in a project directory
        if not any(project_dir in py_file.parts for project_dir in project_dirs):
            continue

        try:
            rel_path = str(py_file).replace("\\", "/")

            # Check if types file is in wrong folder
            if "/engines/" in rel_path:
                violations.append(f"X Types file in engines/: {rel_path}")
                continue  # Skip content check for misplaced files

            content = py_file.read_text(encoding="utf-8")

            try:
                tree = ast.parse(content)

                # Check for implementation classes
                impl_classes = []
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.ClassDef):
                        if not is_type_class(node):
                            impl_classes.append(node.name)

                if impl_classes:
                    violations.append(f"X {rel_path}: Implementation classes: {impl_classes}")

                # Check for functions
                functions = []
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(node.name)

                if functions:
                    violations.append(f"X {rel_path}: Functions: {functions}")

            except SyntaxError as e:
                violations.append(f"X {rel_path}: Syntax error: {e}")

        except (UnicodeDecodeError, OSError):
            continue

    return violations


def check_engine_placement():
    """Check that Engine/Executor files are properly placed.

    Unified rule: Executors belong in engines/ — same logic for
    agentic_core and apps_*.
    """
    violations = []

    # Only scan project directories
    project_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

    for py_file in sorted(Path(".").rglob("*Executor.py")):
        if _is_excluded(py_file):
            continue

        rel_path = str(py_file).replace("\\", "/")

        # Skip non-project directories
        if not any(part in py_file.parts for part in project_dirs):
            continue

        # Unified rule: Executors must be in engines/
        if "/engines/" not in rel_path:
            violations.append(f"X {rel_path}: Executor must be in engines/")

    return violations


def is_type_class(node):
    """Check if a class is a pure type definition."""
    class_name = node.name

    # Protocol classes are types
    if class_name.endswith("Protocol"):
        return True

    # Exception/Error classes are types
    if class_name.endswith(("Exception", "Error")):
        return True

    # Check for dataclass decorator
    has_dataclass = any(
        (isinstance(dec, ast.Name) and dec.id == "dataclass")
        or (isinstance(dec, ast.Attribute) and dec.attr == "dataclass")
        for dec in node.decorator_list
    )

    if has_dataclass:
        # Check if it only has simple methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name not in ("__init__", "__post_init__"):
                    # Check if method has complex logic
                    if len(item.body) > 1 or not isinstance(item.body[0], ast.Pass):
                        if not (
                            item.body
                            and isinstance(item.body[0], ast.Return)
                            and isinstance(item.body[0].value, ast.Constant)
                        ):
                            return False
        return True

    return False


def load_baseline(baseline_file: Path) -> set[str]:
    """Load baseline violations from file."""
    if not baseline_file.exists():
        return set()

    try:
        return set(baseline_file.read_text(encoding="utf-8").strip().split("\n"))
    except (UnicodeDecodeError, OSError):
        return set()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate folder purity rules")
    parser.add_argument("--check-agents-only", action="store_true", help="Only check agent placement")
    parser.add_argument("--check-types-only", action="store_true", help="Only check types purity")
    args = parser.parse_args()

    print("Running Folder Purity Validation...")

    all_violations = []

    # Check agent placement
    if not args.check_types_only:
        agent_violations = check_agent_placement()
        all_violations.extend(agent_violations)

    # Check types purity
    if not args.check_agents_only:
        types_violations = check_types_purity()
        all_violations.extend(types_violations)

    # Check engine placement (only in full mode)
    if not args.check_agents_only and not args.check_types_only:
        engine_violations = check_engine_placement()
        all_violations.extend(engine_violations)

    # Sort violations for deterministic output
    all_violations = sorted(all_violations)

    # Load baseline and subtract
    baseline_file = Path(__file__).parent / "folder_purity_baseline.txt"
    baseline = load_baseline(baseline_file)

    # Calculate new violations
    new_violations = [v for v in all_violations if v not in baseline]

    if new_violations:
        print(f"\nFOLDER PURITY VIOLATIONS DETECTED ({len(new_violations)} NEW):")
        print()

        for violation in new_violations:
            print(f"  {violation}")

        print("\nRequired Actions:")
        print("  • Move Agent files to reasoning/ folders")
        print("  • Move _types files to types/ folders")
        print("  • Split mixed _types files (implementation -> engines/)")
        print("  • Remove functions from _types files")
        print("  • Place apps_* Executors in engines/ folders")

        print("\nFor help, see: docs/architecture/adr-001-folder-purity.md")
        print("\nCommit blocked. Fix violations and try again.")
        return 1
    else:
        print("All folder purity checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
