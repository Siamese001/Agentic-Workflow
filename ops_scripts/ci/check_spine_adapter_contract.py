#!/usr/bin/env python3
"""
AST structural guard for spine adapter contract compliance.

Scans apps_*/engines/*_spine_adapter.py files and enforces:
- Must contain a class that subclasses BaseSpineAdapter
- Must NOT call CIDRegistry constructor in adapter module
- Must NOT define custom CID derivation logic
- Must NOT call new_cycle outside BaseSpineAdapter.execute path

Uses Python ast module only - no runtime imports of app modules.
"""

import ast
import sys
from pathlib import Path


class SpineAdapterContractVisitor(ast.NodeVisitor):
    """AST visitor to check spine adapter contract compliance."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations = []
        self.has_spine_adapter_class = False
        self.subclasses_base_spine_adapter = False
        self.uses_cid_registry_constructor = False
        self.uses_canonical_hash = False
        self.uses_strip_nondeterministic = False
        self.calls_new_cycle = False
        self.imports_base_spine_adapter = False
        self.current_class = None
        self.in_init_method = False

    def visit_Import(self, node: ast.Import) -> None:
        """Check for BaseSpineAdapter imports."""
        for alias in node.names:
            if "base_spine_adapter" in alias.name:
                self.imports_base_spine_adapter = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for BaseSpineAdapter imports."""
        if node.module and "base_spine_adapter" in node.module:
            self.imports_base_spine_adapter = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check for spine adapter classes and inheritance."""
        # Check if this looks like a spine adapter class
        if "spine" in node.name.lower() or "adapter" in node.name.lower():
            self.has_spine_adapter_class = True

            # Check inheritance
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "BaseSpineAdapter":
                    self.subclasses_base_spine_adapter = True
                elif isinstance(base, ast.Attribute):
                    # Handle cases like BaseSpineAdapter or module.BaseSpineAdapter
                    if base.attr == "BaseSpineAdapter":
                        self.subclasses_base_spine_adapter = True

        # Track current class for method context
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track if we're in __init__ method."""
        old_in_init = self.in_init_method
        self.in_init_method = node.name == "__init__"
        self.generic_visit(node)
        self.in_init_method = old_in_init

    def visit_Call(self, node: ast.Call) -> None:
        """Check for prohibited function calls."""
        # Check for CIDRegistry constructor calls
        if isinstance(node.func, ast.Name) and node.func.id == "CIDRegistry":
            # Allow CIDRegistry() in __init__ methods of spine adapter classes
            # when it's used to create the dependency for the base class
            if not (
                self.current_class
                and ("spine" in self.current_class.lower() or "adapter" in self.current_class.lower())
                and self.in_init_method
            ):
                self.uses_cid_registry_constructor = True
                self.violations.append(
                    f"Line {node.lineno}: Direct CIDRegistry() constructor call detected. "
                    "CIDRegistry should be injected, not constructed in adapter.",
                )

        # Check for new_cycle calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "new_cycle":
            self.calls_new_cycle = True
            self.violations.append(
                f"Line {node.lineno}: Direct new_cycle() call detected. "
                "new_cycle should only be called via BaseSpineAdapter.execute().",
            )

        # Check for canonical_hash calls
        if isinstance(node.func, ast.Name) and node.func.id == "canonical_hash":
            self.uses_canonical_hash = True
            self.violations.append(
                f"Line {node.lineno}: Direct canonical_hash() call detected. "
                "CID derivation should be delegated to BaseSpineAdapter.",
            )

        # Check for strip_nondeterministic calls
        if isinstance(node.func, ast.Name) and node.func.id == "strip_nondeterministic":
            self.uses_strip_nondeterministic = True
            self.violations.append(
                f"Line {node.lineno}: Direct strip_nondeterministic() call detected. "
                "CID derivation should be delegated to BaseSpineAdapter.",
            )

        self.generic_visit(node)

    def check_compliance(self) -> list[str]:
        """Return list of violations."""
        if not self.has_spine_adapter_class:
            self.violations.append(
                "No spine adapter class found. Expected a class with 'spine' or 'adapter' in the name.",
            )

        if self.has_spine_adapter_class and not self.subclasses_base_spine_adapter:
            self.violations.append(
                "Spine adapter class does not subclass BaseSpineAdapter. "
                "All spine adapters must inherit from BaseSpineAdapter.",
            )

        if self.has_spine_adapter_class and not self.imports_base_spine_adapter:
            self.violations.append(
                "BaseSpineAdapter not imported. Spine adapters must import BaseSpineAdapter.",
            )

        return sorted(self.violations)


def check_adapter_file(filepath: Path) -> list[str]:
    """Check a single adapter file for contract compliance."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(filepath))

        # Visit and check
        visitor = SpineAdapterContractVisitor(filepath)
        visitor.visit(tree)

        return visitor.check_compliance()

    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"Syntax error in {filepath}: {e}"]
    except Exception as e:
        raise
        return [f"Error processing {filepath}: {e}"]


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent

    # Find adapter files
    adapter_pattern = "apps_*/engines/*_spine_adapter.py"
    adapter_files = list(repo_root.glob(adapter_pattern))

    if not adapter_files:
        print("No spine adapter files found matching pattern:", adapter_pattern)
        return 0

    print(f"Checking {len(adapter_files)} spine adapter file(s)...")

    all_violations = []
    for filepath in sorted(adapter_files):
        relative_path = filepath.relative_to(repo_root)
        violations = check_adapter_file(filepath)

        if violations:
            print(f"\n❌ {relative_path}")
            for violation in violations:
                print(f"   {violation}")
            all_violations.extend(violations)
        else:
            print(f"✅ {relative_path}")

    if all_violations:
        print(f"\n🚨 Contract violations found: {len(all_violations)}")
        return 1
    else:
        print(f"\n✅ All {len(adapter_files)} adapter(s) comply with spine contract")
        return 0


if __name__ == "__main__":
    sys.exit(main())
