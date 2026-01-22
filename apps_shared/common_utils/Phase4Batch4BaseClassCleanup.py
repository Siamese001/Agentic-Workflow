"""
Phase 4 Batch 4: Base Class Cleanup (The MRO Fix) - Hardened AST Version

Remove redundant mixin inheritance from classes that inherit from SovereignBaseAgent.

SovereignBaseAgent already includes:
- HealerMixin
- MCPHardenedMixin
- SubatomicTestingMixin

This script:
1. Uses AST to find classes inheriting from SovereignBaseAgent
2. Removes redundant mixin inheritance
3. Removes unused mixin imports
4. Self-verifies syntax before writing
"""


import argparse
import ast
import re

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "SovereignBaseAgent.py",
    "infrastructure_mixin.py",
    "healer_mixin.py",
    "mcp_hardened_mixin.py",
    "subatomic_testing_mixin.py",
    "conftest.py",
}

# Directories to exclude
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "void_violations",
    "node_modules",
    ".venv",
    "venv",
}

# Redundant mixins that are already in SovereignBaseAgent
REDUNDANT_MIXINS = {"HealerMixin", "MCPHardenedMixin", "SubatomicTestingMixin"}


def find_python_files(root: Path) -> list[Path]:
    """Find all Python files, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


class BaseClassVisitor(ast.NodeVisitor):
    """AST visitor to find classes with redundant mixin inheritance."""

    def __init__(self):
        self.last_import_line = 0
        self.classes_with_redundant_mixins: list[
            tuple[int, str, list[str]]
        ] = []  # (line, class_name, redundant_bases)
        self.mixin_imports: dict = {}  # mixin_name -> (line, module)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track mixin import statements."""
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)

        for alias in node.names:
            if alias.name in REDUNDANT_MIXINS:
                self.mixin_imports[alias.name] = (node.lineno, node.module)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Track import statements."""
        self.last_import_line = max(self.last_import_line, node.end_lineno or node.lineno)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Find classes with redundant mixin inheritance."""
        base_names = []
        has_sovereign_base = False
        redundant_bases = []

        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
                if base.id == "SovereignBaseAgent":
                    has_sovereign_base = True
                elif base.id in REDUNDANT_MIXINS:
                    redundant_bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
                if base.attr == "SovereignBaseAgent":
                    has_sovereign_base = True
                elif base.attr in REDUNDANT_MIXINS:
                    redundant_bases.append(base.attr)

        if has_sovereign_base and redundant_bases:
            self.classes_with_redundant_mixins.append((node.lineno, node.name, redundant_bases))

        self.generic_visit(node)


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.

    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "classes_cleaned": 0,
        "imports_removed": 0,
        "skipped": False,
        "reason": None,
    }

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result

    # Quick check for SovereignBaseAgent
    if "SovereignBaseAgent" not in content:
        result["skipped"] = True
        result["reason"] = "No SovereignBaseAgent"
        return result

    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"Pre-existing syntax error: {e}"
        return result

    visitor = BaseClassVisitor()
    visitor.visit(tree)

    # Skip if no redundant mixins found
    if not visitor.classes_with_redundant_mixins:
        result["skipped"] = True
        result["reason"] = "No redundant mixins"
        return result

    # Perform text-based replacements (safer than AST manipulation)
    modified_content = content

    for line_no, class_name, redundant_bases in visitor.classes_with_redundant_mixins:
        for mixin in redundant_bases:
            # Remove mixin from class definition
            # Pattern: class Foo(SovereignBaseAgent, HealerMixin, ...):
            # or: class Foo(HealerMixin, SovereignBaseAgent, ...):
            patterns = [
                (rf",\s*{mixin}", ""),  # Remove ", HealerMixin"
                (rf"{mixin}\s*,\s*", ""),  # Remove "HealerMixin, "
            ]

            for pattern, replacement in patterns:
                modified_content = re.sub(pattern, replacement, modified_content)

            result["classes_cleaned"] += 1

    # Remove unused mixin imports
    for mixin, (import_line, module) in visitor.mixin_imports.items():
        # Check if mixin is still used in the modified content
        if mixin not in modified_content.split("class ")[0]:  # Only check before class definitions
            # Try to remove the import line
            # This is conservative - only removes if it's a single import
            single_import_pattern = rf"^from\s+\S+\s+import\s+{mixin}\s*$"
            if re.search(single_import_pattern, modified_content, re.MULTILINE):
                modified_content = re.sub(
                    single_import_pattern + r"\n?", "", modified_content, flags=re.MULTILINE
                )
                result["imports_removed"] += 1

    # Skip if no actual changes
    if modified_content == content:
        result["skipped"] = True
        result["reason"] = "No changes needed"
        return result

    # Final Safety Check
    try:
        ast.parse(modified_content)
    except SyntaxError as e:
        result["skipped"] = True
        result["reason"] = f"SAFETY ABORT: Generated invalid syntax: {e}"
        return result

    # Write
    if not dry_run:
        try:
            file_path.write_text(modified_content, encoding="utf-8")
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 4: Base Class Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually modify files")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return

    root = Path(__file__).parent.parent / "agentic_core"
    if not root.exists():
        print(f"Error: agentic_core directory not found at {root}")
        return

    print(f"{'[DRY RUN]' if args.dry_run else '[EXECUTE]'} Phase 4 Batch 4: Base Class Cleanup")
    print(f"Scanning: {root}")
    print("-" * 60)

    files = find_python_files(root)
    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "classes_cleaned": 0,
        "imports_removed": 0,
        "files_skipped": 0,
    }

    for file_path in files:
        result = process_file(file_path, dry_run=args.dry_run)
        stats["files_processed"] += 1

        if result["skipped"]:
            stats["files_skipped"] += 1
            if "No redundant" not in str(result["reason"]) and "No SovereignBaseAgent" not in str(
                result["reason"]
            ):
                print(f"  [SKIP] {file_path.name}: {result['reason']}")
            continue

        if result["classes_cleaned"] > 0:
            stats["files_modified"] += 1
            stats["classes_cleaned"] += result["classes_cleaned"]
            stats["imports_removed"] += result["imports_removed"]

            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if args.dry_run else '[MODIFIED]'} {rel_path}")
            print(f"    - Cleaned {result['classes_cleaned']} class(es)")
            if result["imports_removed"]:
                print(f"    - Removed {result['imports_removed']} import(s)")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed:   {stats['files_processed']}")
    print(f"  Files modified:    {stats['files_modified']}")
    print(f"  Classes cleaned:   {stats['classes_cleaned']}")
    print(f"  Imports removed:   {stats['imports_removed']}")
    print(f"  Files skipped:     {stats['files_skipped']}")


if __name__ == "__main__":
    main()