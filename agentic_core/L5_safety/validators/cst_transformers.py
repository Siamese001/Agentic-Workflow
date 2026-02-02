"""
CST Transformers - Concrete LibCST transformations for surgical healing.

Provides specific transformers for different types of code modifications
while preserving comments, whitespace, and formatting.
"""

from __future__ import annotations

import libcst as cst
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ImportTarget:
    """Target for import removal operations."""

    line_number: int
    module_name: Optional[str] = None  # For specific module targeting
    name: Optional[str] = None  # For specific name targeting in from-imports


class SurgicalImportRemover(cst.CSTTransformer):
    """
    CST transformer that removes specific imports while preserving formatting.

    Uses a string-based approach to identify and remove imports by name.
    """

    def __init__(self, targets: List[ImportTarget]):
        """
        Initialize with import removal targets.

        Args:
            targets: List of imports to remove
        """
        self.targets = targets
        self.target_lines = {t.line_number for t in targets}
        self.target_names = {t.name for t in targets if t.name}
        self.modifications_made = 0
        self.lines = None
        self.current_line = 0

    def on_visit(self, node: cst.CSTNode) -> bool:
        """Initialize line tracking."""
        if isinstance(node, cst.Module):
            # Store the original source lines for reference
            self.lines = node.code.split("\n")
        return True

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """Handle Import nodes by checking if they match our targets."""
        # Check if this import matches our targets
        for alias in updated_node.names:
            name = alias.asname.value if alias.asname else alias.name.value
            if name in self.target_names:
                # Remove the entire import statement
                self.modifications_made += 1
                return cst.RemoveFromParent()

        return updated_node

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        """
        Handle ImportFrom nodes (e.g., `from os import path`, `from x import a, b`).

        Supports both full line removal and partial name removal.
        """
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node

        # Check if this import line is targeted
        line_targeted = original_node.position.line in self.target_lines

        # Check if module is targeted
        module_targeted = original_node.module and original_node.module.value in self.target_modules

        if not (line_targeted or module_targeted):
            return updated_node

        # Find names to remove
        names_to_remove = set()
        for alias in original_node.names:
            name = alias.asname or alias.name
            if name in self.target_names:
                names_to_remove.add(name)

        if not names_to_remove:
            # No specific names to remove, check if we should remove entire line
            if line_targeted and not self.target_names:
                self.modifications_made += 1
                return cst.RemoveFromParent()
            return updated_node

        # Filter out the names to remove
        remaining_names = []
        for alias in original_node.names:
            name = alias.asname or alias.name
            if name not in names_to_remove:
                remaining_names.append(alias)

        if not remaining_names:
            # All names removed, remove the entire import
            self.modifications_made += 1
            return cst.RemoveFromParent()

        # Some names remain, update the import with remaining names
        new_node = updated_node.with_changes(names=remaining_names)
        self.modifications_made += 1
        return new_node

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        """
        Handle SimpleStatementLine to remove empty import statements.

        This catches cases where we removed all names from a multi-line import
        and need to clean up the empty statement.
        """
        # Check if this line only contains an empty import statement
        if len(updated_node.body) == 0:
            # Check if original line was targeted
            if (
                hasattr(original_node, "position")
                and original_node.position
                and original_node.position.line in self.target_lines
            ):
                self.modifications_made += 1
                return cst.RemoveFromParent()

        return updated_node


class SurgicalDocstringInserter(cst.CSTTransformer):
    """
    CST transformer that inserts docstrings while preserving formatting.

    Inserts docstrings at the beginning of class or function bodies.
    """

    def __init__(self, targets: List[ImportTarget]):
        """
        Initialize with docstring insertion targets.

        Args:
            targets: List of locations where docstrings should be inserted
        """
        self.targets = targets
        self.target_lines = {t.line_number for t in targets}
        self.modifications_made = 0

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Insert docstring into class if targeted."""
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node

        if original_node.position.line in self.target_lines:
            # Check if class already has a docstring
            if (
                len(updated_node.body.body) > 0
                and isinstance(updated_node.body.body[0], cst.SimpleStatementLine)
                and len(updated_node.body.body[0].body) > 0
                and isinstance(updated_node.body.body[0].body[0], cst.Expr)
                and isinstance(updated_node.body.body[0].body[0].value, cst.SimpleString)
            ):
                # Already has docstring
                return updated_node

            # Insert docstring as first statement
            docstring = cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.SimpleString(value='"""TODO: Add class docstring"""'))]
            )

            new_body = [docstring] + list(updated_node.body.body)
            new_module_body = cst.Module(body=new_body)

            new_node = updated_node.with_changes(body=new_module_body)
            self.modifications_made += 1
            return new_node

        return updated_node

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Insert docstring into function if targeted."""
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node

        if original_node.position.line in self.target_lines:
            # Check if function already has a docstring
            if (
                len(updated_node.body.body) > 0
                and isinstance(updated_node.body.body[0], cst.SimpleStatementLine)
                and len(updated_node.body.body[0].body) > 0
                and isinstance(updated_node.body.body[0].body[0], cst.Expr)
                and isinstance(updated_node.body.body[0].body[0].value, cst.SimpleString)
            ):
                # Already has docstring
                return updated_node

            # Insert docstring as first statement
            docstring = cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.SimpleString(value='"""TODO: Add function docstring"""'))]
            )

            new_body = [docstring] + list(updated_node.body.body)
            new_module_body = cst.Module(body=new_body)

            new_node = updated_node.with_changes(body=new_module_body)
            self.modifications_made += 1
            return new_node

        return updated_node


class SurgicalBareExceptFixer(cst.CSTTransformer):
    """
    CST transformer that fixes bare except clauses.

    Converts `except:` to `except Exception:` while preserving formatting.
    """

    def __init__(self, targets: List[ImportTarget]):
        """
        Initialize with bare except fix targets.

        Args:
            targets: List of locations where bare except should be fixed
        """
        self.targets = targets
        self.target_lines = {t.line_number for t in targets}
        self.modifications_made = 0

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        """Fix bare except clauses."""
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node

        if original_node.position.line in self.target_lines and original_node.type is None:
            # This is a bare except clause, fix it
            exception_type = cst.Name(value="Exception")
            new_node = updated_node.with_changes(type=exception_type)
            self.modifications_made += 1
            return new_node

        return updated_node


def create_import_remover(violations) -> Optional[SurgicalImportRemover]:
    """
    Factory function to create import remover from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalImportRemover instance or None if no import violations
    """
    import_targets = []

    for violation in violations:
        if violation.constraint_type == "unused_import" and violation.fix_type == "delete":
            if violation.target_coordinate:
                # Extract module name from message if possible
                module_name = None
                if violation.message and "Unused import:" in violation.message:
                    module_name = violation.message.split("Unused import:")[-1].strip()

                target = ImportTarget(
                    line_number=violation.target_coordinate.line,
                    module_name=module_name,
                    name=module_name,  # Use same name for both
                )
                import_targets.append(target)

    if import_targets:
        return SurgicalImportRemover(import_targets)
    return None


def create_docstring_inserter(violations) -> Optional[SurgicalDocstringInserter]:
    """
    Factory function to create docstring inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalDocstringInserter instance or None if no docstring violations
    """
    docstring_targets = []

    for violation in violations:
        if violation.constraint_type == "missing_docstring" and violation.fix_type == "insert":
            if violation.target_coordinate:
                target = ImportTarget(
                    line_number=violation.target_coordinate.line,
                )
                docstring_targets.append(target)

    if docstring_targets:
        return SurgicalDocstringInserter(docstring_targets)
    return None


def create_bare_except_fixer(violations) -> Optional[SurgicalBareExceptFixer]:
    """
    Factory function to create bare except fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalBareExceptFixer instance or None if no bare except violations
    """
    except_targets = []

    for violation in violations:
        if violation.constraint_type == "bare_except" and violation.fix_type == "replace":
            if violation.target_coordinate:
                target = ImportTarget(
                    line_number=violation.target_coordinate.line,
                )
                except_targets.append(target)

    if except_targets:
        return SurgicalBareExceptFixer(except_targets)
    return None
