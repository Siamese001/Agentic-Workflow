"""
ADG Tombstone Detector

Detects tombstone modules in Python packages - files that exist but are not
re-exported in __init__.py. This catches architectural violations where
deprecated or dead code remains in the codebase.

Usage:
    python tools/adg/detect_tombstone_modules.py <package_path> [--report]

Examples:
    # Default: Interactive heal mode (executes real actions with HITL)
    python tools/adg/detect_tombstone_modules.py agentic_core/L4_state/cache

    # Report-only mode (CI-friendly, no actions)
    python tools/adg/detect_tombstone_modules.py agentic_core/L4_state/cache --report
    python tools/adg/detect_tombstone_modules.py agentic_core/L4_state/cache -r

Interactive Heal Mode (default):
    - Walks through each problematic file individually
    - Presents options for each file (archive/delete/keep/mark tombstone)
    - EXECUTES REAL ACTIONS (archives files, deletes files, modifies __init__.py)
    - Perfect for architectural decision-making with human oversight
    - Creates tools/archive/ if it doesn't exist
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def extract_public_symbols(module_path: Path) -> Set[str]:
    """Extract public symbols (non-underscore) from a Python module."""
    try:
        with open(module_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(module_path))

        public_symbols = set()

        for node in ast.walk(tree):
            # Function definitions
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                public_symbols.add(node.name)
            # Class definitions
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                public_symbols.add(node.name)
            # Variable assignments at module level
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        public_symbols.add(target.id)

        return public_symbols
    except Exception:
        return set()


def is_tombstone_file(module_path: Path) -> bool:
    """Check if a module is marked as a tombstone in its docstring."""
    try:
        with open(module_path, "r", encoding="utf-8") as f:
            first_lines = [f.readline() for _ in range(10)]

        docstring = "".join(first_lines)
        return "TOMBSTONED" in docstring or "tombstoned" in docstring
    except Exception:
        return False


def get_init_imports(init_path: Path) -> Set[str]:
    """Extract module names imported in __init__.py."""
    try:
        with open(init_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(init_path))

        imported_modules = set()

        for node in ast.walk(tree):
            # from .module import ...
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get the relative module name
                    module_name = node.module.split(".")[-1]
                    imported_modules.add(module_name)

        return imported_modules
    except Exception:
        return set()


def scan_package(package_path: Path) -> Dict[str, List[Path]]:
    """Scan a package directory and categorize modules."""
    if not package_path.exists() or not package_path.is_dir():
        print(f"Error: {package_path} is not a valid directory")
        sys.exit(1)

    init_path = package_path / "__init__.py"
    if not init_path.exists():
        print(f"Error: {package_path} is not a Python package (no __init__.py)")
        sys.exit(1)

    # Get all .py files in the package (excluding __init__.py)
    py_files = [f for f in package_path.glob("*.py") if f.name != "__init__.py"]

    # Get modules imported in __init__.py
    imported_modules = get_init_imports(init_path)

    # Categorize modules
    categories = {
        "imported": [],
        "tombstone_not_imported": [],
        "no_public_symbols_not_imported": [],
        "unimported_with_symbols": [],
    }

    for py_file in py_files:
        module_name = py_file.stem

        if module_name in imported_modules:
            categories["imported"].append(py_file)
            continue

        # Not imported - check why
        is_tombstone = is_tombstone_file(py_file)
        public_symbols = extract_public_symbols(py_file)

        if is_tombstone:
            categories["tombstone_not_imported"].append(py_file)
        elif not public_symbols:
            categories["no_public_symbols_not_imported"].append(py_file)
        else:
            categories["unimported_with_symbols"].append(py_file)

    return categories


def print_report(package_path: Path, categories: Dict[str, List[Path]]) -> int:
    """Print a detailed report and return exit code."""
    print(f"\n{'=' * 70}")
    print(f"Tombstone Detection Report: {package_path}")
    print(f"{'=' * 70}\n")

    total_files = sum(len(files) for files in categories.values())

    # Imported modules (good)
    if categories["imported"]:
        print(f"✓ Imported modules ({len(categories['imported'])}):")
        for f in sorted(categories["imported"]):
            print(f"  - {f.name}")
        print()

    # Tombstone files not imported (expected but should be archived)
    if categories["tombstone_not_imported"]:
        print(f"⚠ TOMBSTONE files not imported ({len(categories['tombstone_not_imported'])}):")
        print("  These files are marked as TOMBSTONED but still exist in the package.")
        for f in sorted(categories["tombstone_not_imported"]):
            print(f"  - {f.name}")
        print()

    # Files with no public symbols not imported (suspicious)
    if categories["no_public_symbols_not_imported"]:
        print(
            f"⚠ Files with no public symbols not imported ({len(categories['no_public_symbols_not_imported'])}):"
        )
        print("  These files have no exportable symbols and are not imported.")
        for f in sorted(categories["no_public_symbols_not_imported"]):
            print(f"  - {f.name}")
        print()

    # Unimported files with public symbols (potential bug)
    if categories["unimported_with_symbols"]:
        print(f"✗ Files with public symbols NOT imported ({len(categories['unimported_with_symbols'])}):")
        print("  These files have exportable symbols but are not in __init__.py.")
        for f in sorted(categories["unimported_with_symbols"]):
            symbols = extract_public_symbols(f)
            print(f"  - {f.name} (symbols: {', '.join(sorted(symbols))})")
        print()

    # Summary
    print(f"{'=' * 70}")
    print("Summary:")
    print(f"  Total modules: {total_files}")
    print(f"  Imported: {len(categories['imported'])}")
    print(f"  Tombstone not imported: {len(categories['tombstone_not_imported'])}")
    print(f"  No symbols not imported: {len(categories['no_public_symbols_not_imported'])}")
    print(f"  Unimported with symbols: {len(categories['unimported_with_symbols'])}")
    print(f"{'=' * 70}\n")

    # Exit code: 0 if clean, 1 if tombstones found, 2 if unimported with symbols
    if categories["unimported_with_symbols"]:
        return 2
    elif categories["tombstone_not_imported"] or categories["no_public_symbols_not_imported"]:
        return 1
    else:
        return 0


def interactive_fix_session(package_path: Path, categories: Dict[str, List[Path]]) -> None:
    """Interactive HITL session to guide fixes."""
    print(f"\n{'=' * 70}")
    print("INTERACTIVE FIX SESSION")
    print("⚠️  ACTIONS WILL BE EXECUTED - NO DRY RUN")
    print(f"{'=' * 70}\n")

    init_path = package_path / "__init__.py"
    archive_dir = Path("tools/archive")
    archive_dir.mkdir(exist_ok=True)

    actions_taken = []

    # Handle tombstone files
    if categories["tombstone_not_imported"]:
        print(f"🪦 TOMBSTONE FILES ({len(categories['tombstone_not_imported'])}):")
        for i, f in enumerate(sorted(categories["tombstone_not_imported"]), 1):
            print(f"\n  [{i}] {f.name}")
            print(f"      Path: {f}")
            print("      Marked as TOMBSTONED in docstring")

            print(f"\n      Options for {f.name}:")
            print("        A) Archive to tools/archive/")
            print("        D) Delete permanently")
            print("        K) Keep as-is (no action)")
            print("        S) Skip this file")

            choice = input("\n      Your choice [A/D/K/S]: ").strip().upper()

            if choice == "A":
                archive_path = archive_dir / f.name
                f.rename(archive_path)
                print(f"      ✓ Moved {f.name} to {archive_path}")
                actions_taken.append(f"Archived {f.name} to {archive_path}")
            elif choice == "D":
                f.unlink()
                print(f"      ✓ Deleted {f.name}")
                actions_taken.append(f"Deleted {f.name}")
            elif choice == "K":
                print(f"      → Keeping {f.name} as-is")
            elif choice == "S":
                print(f"      → Skipping {f.name}")
            else:
                print(f"      → Invalid choice, skipping {f.name}")

    # Handle files with no public symbols
    if categories["no_public_symbols_not_imported"]:
        print(f"\n\n❓ FILES WITH NO PUBLIC SYMBOLS ({len(categories['no_public_symbols_not_imported'])}):")
        for i, f in enumerate(sorted(categories["no_public_symbols_not_imported"]), 1):
            print(f"\n  [{i}] {f.name}")
            print(f"      Path: {f}")
            print("      No exportable functions or classes found")

            print(f"\n      Options for {f.name}:")
            print("        A) Add to __init__.py (if it should be exported)")
            print("        R) Archive to tools/archive/")
            print("        D) Delete permanently")
            print("        K) Keep as-is (no action)")
            print("        S) Skip this file")

            choice = input("\n      Your choice [A/R/D/K/S]: ").strip().upper()

            if choice == "A":
                # Add import to __init__.py
                with open(init_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Add import statement
                import_line = (
                    f"from agentic_core.{package_path.as_posix().replace('/', '.')}.{f.stem} import (\n"
                )
                content = content.replace("\n", f"\n{import_line}\n", 1)

                with open(init_path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"      ✓ Added import for {f.stem} to __init__.py")
                actions_taken.append(f"Added import for {f.stem} to __init__.py")
            elif choice == "R":
                archive_path = archive_dir / f.name
                f.rename(archive_path)
                print(f"      ✓ Moved {f.name} to {archive_path}")
                actions_taken.append(f"Archived {f.name} to {archive_path}")
            elif choice == "D":
                f.unlink()
                print(f"      ✓ Deleted {f.name}")
                actions_taken.append(f"Deleted {f.name}")
            elif choice == "K":
                print(f"      → Keeping {f.name} as-is")
            elif choice == "S":
                print(f"      → Skipping {f.name}")
            else:
                print(f"      → Invalid choice, skipping {f.name}")

    # Handle files with public symbols not imported
    if categories["unimported_with_symbols"]:
        print(f"\n\n⚠ FILES WITH PUBLIC SYMBOLS NOT IMPORTED ({len(categories['unimported_with_symbols'])}):")
        for i, f in enumerate(sorted(categories["unimported_with_symbols"]), 1):
            symbols = extract_public_symbols(f)
            print(f"\n  [{i}] {f.name}")
            print(f"      Path: {f}")
            print(f"      Public symbols: {', '.join(sorted(symbols))}")

            print(f"\n      Options for {f.name}:")
            print("        A) Add to __init__.py (export these symbols)")
            print("        M) Mark as tombstone (add TOMBSTONED docstring)")
            print("        R) Archive to tools/archive/")
            print("        D) Delete permanently")
            print("        K) Keep as-is (no action)")
            print("        S) Skip this file")

            choice = input("\n      Your choice [A/M/R/D/K/S]: ").strip().upper()

            if choice == "A":
                # Add import to __init__.py with symbols
                with open(init_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Add import statement with specific symbols
                symbols_list = ",\n    ".join(sorted(symbols))
                import_line = f"from agentic_core.{package_path.as_posix().replace('/', '.')}.{f.stem} import (\n    {symbols_list},\n)\n"
                content = content.replace("\n", f"\n{import_line}\n", 1)

                with open(init_path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"      ✓ Added import for {f.stem} to __init__.py")
                print(f"      ✓ Exporting symbols: {', '.join(sorted(symbols))}")
                actions_taken.append(f"Added import for {f.stem} to __init__.py with symbols")
            elif choice == "M":
                # Add TOMBSTONED docstring
                with open(f, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                # Insert TOMBSTONED docstring after opening quotes
                if lines[0].startswith('"""') or lines[0].startswith("'''"):
                    lines.insert(1, "TOMBSTONED - Deprecated module. Do not import.\n\n")
                else:
                    lines.insert(0, '"""\nTOMBSTONED - Deprecated module. Do not import.\n"""\n\n')

                with open(f, "w", encoding="utf-8") as file:
                    file.writelines(lines)
                print(f"      ✓ Added TOMBSTONED docstring to {f.name}")
                actions_taken.append(f"Marked {f.name} as tombstone")
            elif choice == "R":
                archive_path = archive_dir / f.name
                f.rename(archive_path)
                print(f"      ✓ Moved {f.name} to {archive_path}")
                actions_taken.append(f"Archived {f.name} to {archive_path}")
            elif choice == "D":
                f.unlink()
                print(f"      ✓ Deleted {f.name}")
                actions_taken.append(f"Deleted {f.name}")
            elif choice == "K":
                print(f"      → Keeping {f.name} as-is")
            elif choice == "S":
                print(f"      → Skipping {f.name}")
            else:
                print(f"      → Invalid choice, skipping {f.name}")

    print(f"\n{'=' * 70}")
    print("INTERACTIVE SESSION COMPLETE")
    if actions_taken:
        print(f"Actions taken ({len(actions_taken)}):")
        for action in actions_taken:
            print(f"  - {action}")
    else:
        print("No actions taken.")
    print(f"{'=' * 70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_tombstone_modules.py <package_path> [--report]")
        print("Example: python detect_tombstone_modules.py agentic_core/L4_state/cache")
        print("         python detect_tombstone_modules.py agentic_core/L4_state/cache --report")
        sys.exit(1)

    package_path = Path(sys.argv[1])
    report_only = "--report" in sys.argv or "-r" in sys.argv

    categories = scan_package(package_path)
    exit_code = print_report(package_path, categories)

    # Default to interactive heal mode unless --report flag is set
    if not report_only:
        if exit_code == 0:
            print("No issues found - nothing to heal.")
        else:
            interactive_fix_session(package_path, categories)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
