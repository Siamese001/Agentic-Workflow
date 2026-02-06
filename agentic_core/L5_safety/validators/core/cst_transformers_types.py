"""
CST Transformers - Concrete LibCST transformations for surgical healing.

Provides specific transformers for different types of code modifications
while preserving comments, whitespace, and formatting.
"""

from __future__ import annotations

from dataclasses import dataclass

import libcst as cst


@dataclass
class ImportTarget:
    """Target for import removal operations."""

    line_number: int
    module_name: str | None = None  # For specific module targeting
    name: str | None = None  # For specific name targeting in from-imports


@dataclass
class DocstringTarget:
    """Target for docstring insertion operations."""

    line_number: int
    name: str | None = None  # Class or function name
    node_type: str = "class"  # "class" or "function"
    docstring: str = '"""TODO: Add docstring."""'  # Docstring to insert


@dataclass
class BareExceptTarget:
    """Target for bare except fix operations."""

    line_number: int
    exception_type: str = "Exception"  # Exception type to use


class SurgicalImportRemover(cst.CSTTransformer):
    """
    CST transformer that removes specific imports while preserving formatting.

    Uses a string-based approach to identify and remove imports by name.
    """

    def __init__(self, targets: list[ImportTarget]):
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

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
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
    Uses name-based matching since CST nodes don't have position metadata.
    """

    def __init__(self, targets: list[DocstringTarget]):
        """
        Initialize with docstring insertion targets.

        Args:
            targets: List of DocstringTarget objects specifying where to insert
        """
        self.targets = targets
        self.target_names = {t.name for t in targets if t.name}
        self.target_lines = {t.line_number for t in targets}
        self.target_map = {t.name: t for t in targets if t.name}
        self.modifications_made = 0

    def _has_docstring(self, body: cst.IndentedBlock) -> bool:
        """Check if the body already has a docstring."""
        if len(body.body) == 0:
            return False
        first_stmt = body.body[0]
        if isinstance(first_stmt, cst.SimpleStatementLine):
            if len(first_stmt.body) > 0:
                first_expr = first_stmt.body[0]
                if isinstance(first_expr, cst.Expr):
                    value = first_expr.value
                    if isinstance(value, cst.SimpleString | cst.ConcatenatedString):
                        # Check if it's a docstring (triple-quoted)
                        if isinstance(value, cst.SimpleString):
                            return value.value.startswith(('"""', "'''"))
        return False

    def _create_docstring_stmt(self, docstring: str) -> cst.SimpleStatementLine:
        """Create a docstring statement line."""
        return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=docstring))])

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Insert docstring into class if targeted by name."""
        class_name = updated_node.name.value

        if class_name not in self.target_names:
            return updated_node

        # Check if class already has a docstring
        if self._has_docstring(updated_node.body):
            return updated_node

        # Get the docstring to insert
        target = self.target_map.get(class_name)
        docstring = target.docstring if target else '"""TODO: Add class docstring."""'

        # Create docstring statement
        docstring_stmt = self._create_docstring_stmt(docstring)

        # Build new body with docstring as first statement
        new_body_stmts = [docstring_stmt] + list(updated_node.body.body)
        new_body = updated_node.body.with_changes(body=new_body_stmts)

        self.modifications_made += 1
        return updated_node.with_changes(body=new_body)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Insert docstring into function if targeted by name."""
        func_name = updated_node.name.value

        if func_name not in self.target_names:
            return updated_node

        # Check if function already has a docstring
        if self._has_docstring(updated_node.body):
            return updated_node

        # Get the docstring to insert
        target = self.target_map.get(func_name)
        docstring = target.docstring if target else '"""TODO: Add function docstring."""'

        # Create docstring statement
        docstring_stmt = self._create_docstring_stmt(docstring)

        # Build new body with docstring as first statement
        new_body_stmts = [docstring_stmt] + list(updated_node.body.body)
        new_body = updated_node.body.with_changes(body=new_body_stmts)

        self.modifications_made += 1
        return updated_node.with_changes(body=new_body)


class SurgicalBareExceptFixer(cst.CSTTransformer):
    """
    CST transformer that fixes bare except clauses.

    Converts `except:` to `except Exception:` while preserving formatting.
    Fixes ALL bare except clauses found (no position metadata needed).
    """

    def __init__(self, targets: list[BareExceptTarget] | None = None, fix_all: bool = True):
        """
        Initialize bare except fixer.

        Args:
            targets: Optional list of specific targets (if None, fix all)
            fix_all: If True, fix all bare except clauses found
        """
        self.targets = targets or []
        self.target_lines = {t.line_number for t in self.targets} if self.targets else set()
        self.fix_all = fix_all
        self.modifications_made = 0

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        """Fix bare except clauses."""
        # Check if this is a bare except (no type specified)
        if updated_node.type is not None:
            return updated_node

        # Fix all bare excepts or only targeted ones
        if self.fix_all or (self.target_lines and self._should_fix(original_node)):
            # Convert bare except to except Exception
            # Need to add whitespace after "except" keyword
            exception_type = cst.Name(value="Exception")
            new_node = updated_node.with_changes(
                type=exception_type,
                whitespace_after_except=cst.SimpleWhitespace(" "),
            )
            self.modifications_made += 1
            return new_node

        return updated_node

    def _should_fix(self, node: cst.ExceptHandler) -> bool:
        """Check if this node should be fixed based on targets."""
        # If we have position info, use it
        if hasattr(node, "position") and node.position:
            return node.position.line in self.target_lines
        # Otherwise, fix all if fix_all is True
        return self.fix_all


class SurgicalFutureImportInserter(cst.CSTTransformer):
    """
    CST transformer that inserts __future__ imports at the top of modules.

    Handles proper placement after shebang and module docstrings.
    """

    def __init__(self, future_imports: list[str] | None = None):
        """
        Initialize with future imports to add.

        Args:
            future_imports: List of future imports (e.g., ["annotations"])
        """
        self.future_imports = future_imports or ["annotations"]
        self.modifications_made = 0
        self.has_future_import = False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        """Check if __future__ import already exists."""
        if node.module and isinstance(node.module, cst.Attribute):
            # Handle from __future__.something import ...
            pass
        elif node.module and isinstance(node.module, cst.Name):
            if node.module.value == "__future__":
                self.has_future_import = True
        return True

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Insert __future__ import at the correct position in the module."""
        if self.has_future_import:
            return updated_node

        # Find insertion point (after shebang and docstring)
        insert_idx = 0
        body = list(updated_node.body)

        # Skip shebang comment if present (it's in leading_lines of first statement)
        # Skip module docstring if present
        if body:
            first_stmt = body[0]
            if isinstance(first_stmt, cst.SimpleStatementLine):
                if len(first_stmt.body) > 0:
                    first_expr = first_stmt.body[0]
                    if isinstance(first_expr, cst.Expr):
                        if isinstance(first_expr.value, cst.SimpleString):
                            # This is a module docstring, insert after it
                            insert_idx = 1

        # Create __future__ import statement
        import_names = [cst.ImportAlias(name=cst.Name(value=name)) for name in self.future_imports]
        future_import = cst.SimpleStatementLine(
            body=[
                cst.ImportFrom(
                    module=cst.Name(value="__future__"),
                    names=import_names,
                )
            ],
            trailing_whitespace=cst.TrailingWhitespace(
                whitespace=cst.SimpleWhitespace(value=""),
                comment=None,
                newline=cst.Newline(value=None),
            ),
        )

        # Insert the import
        new_body = body[:insert_idx] + [future_import] + body[insert_idx:]
        self.modifications_made += 1

        return updated_node.with_changes(body=new_body)


class SurgicalTrailingWhitespaceFixer(cst.CSTTransformer):
    """
    CST transformer that removes trailing whitespace from lines.

    Preserves all code structure while cleaning up whitespace.
    """

    def __init__(self):
        """Initialize the trailing whitespace fixer."""
        self.modifications_made = 0

    def leave_TrailingWhitespace(
        self, original_node: cst.TrailingWhitespace, updated_node: cst.TrailingWhitespace
    ) -> cst.TrailingWhitespace:
        """Remove trailing whitespace before newlines."""
        # Check if there's non-empty whitespace before the newline
        if updated_node.whitespace.value.strip() == "" and updated_node.whitespace.value:
            # Has trailing whitespace - remove it
            new_node = updated_node.with_changes(whitespace=cst.SimpleWhitespace(""))
            self.modifications_made += 1
            return new_node
        return updated_node

    def leave_EmptyLine(self, original_node: cst.EmptyLine, updated_node: cst.EmptyLine) -> cst.EmptyLine:
        """Remove trailing whitespace from empty lines."""
        if updated_node.whitespace.value:
            new_node = updated_node.with_changes(whitespace=cst.SimpleWhitespace(""))
            self.modifications_made += 1
            return new_node
        return updated_node


class SurgicalBlankLineNormalizer(cst.CSTTransformer):
    """
    CST transformer that normalizes excessive blank lines.

    Reduces multiple consecutive blank lines to a maximum of 2.
    """

    def __init__(self, max_blank_lines: int = 2):
        """
        Initialize the blank line normalizer.

        Args:
            max_blank_lines: Maximum allowed consecutive blank lines
        """
        self.max_blank_lines = max_blank_lines
        self.modifications_made = 0

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Normalize blank lines in the module body."""
        new_body = []
        consecutive_empty = 0

        for stmt in updated_node.body:
            # Check leading lines for empty lines
            if hasattr(stmt, "leading_lines") and stmt.leading_lines:
                new_leading = []
                for line in stmt.leading_lines:
                    if isinstance(line, cst.EmptyLine):
                        consecutive_empty += 1
                        if consecutive_empty <= self.max_blank_lines:
                            new_leading.append(line)
                        else:
                            self.modifications_made += 1
                    else:
                        consecutive_empty = 0
                        new_leading.append(line)

                if len(new_leading) != len(stmt.leading_lines):
                    stmt = stmt.with_changes(leading_lines=new_leading)

            new_body.append(stmt)
            consecutive_empty = 0  # Reset after non-empty statement

        if self.modifications_made > 0:
            return updated_node.with_changes(body=new_body)
        return updated_node


@dataclass
class StructuralTarget:
    """Target for structural fix operations."""

    line_number: int
    fix_type: str  # "trailing_whitespace", "blank_lines"


@dataclass
class TypeHintTarget:
    """Target for type hint operations."""

    line_number: int
    name: str  # Function or parameter name
    hint_type: str  # "return", "parameter"
    type_annotation: str  # The type annotation to add


class SurgicalTypeHintInserter(cst.CSTTransformer):
    """
    CST transformer that inserts type hints into function signatures.

    Adds return type hints and parameter type hints while preserving formatting.
    """

    def __init__(self, targets: list[TypeHintTarget]):
        """
        Initialize with type hint targets.

        Args:
            targets: List of TypeHintTarget objects specifying hints to add
        """
        self.targets = targets
        self.target_names = {t.name for t in targets}
        self.target_map = {t.name: t for t in targets}
        self.modifications_made = 0

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Add type hints to function if targeted."""
        func_name = updated_node.name.value

        if func_name not in self.target_names:
            return updated_node

        target = self.target_map.get(func_name)
        if not target:
            return updated_node

        # Handle return type hint
        if target.hint_type == "return" and updated_node.returns is None:
            # Parse the type annotation
            try:
                annotation = cst.parse_expression(target.type_annotation)
                new_returns = cst.Annotation(annotation=annotation)
                updated_node = updated_node.with_changes(returns=new_returns)
                self.modifications_made += 1
            except Exception:
                pass  # Skip if annotation parsing fails

        return updated_node


def create_type_hint_inserter(violations) -> SurgicalTypeHintInserter | None:
    """
    Factory function to create type hint inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTypeHintInserter instance or None if no type hint violations
    """
    type_hint_targets = []

    for violation in violations:
        if violation.constraint_type == "missing_type_hint" and violation.fix_type == "insert":
            if violation.target_coordinate:
                # Extract function name and type from message
                name = None
                type_annotation = "Any"
                hint_type = "return"

                if violation.message:
                    import re

                    # Try to extract function name
                    match = re.search(r"[Ff]unction\s+['\"]?(\w+)['\"]?", violation.message)
                    if match:
                        name = match.group(1)

                    # Try to extract type annotation
                    type_match = re.search(r"type[:\s]+['\"]?(\w+)['\"]?", violation.message)
                    if type_match:
                        type_annotation = type_match.group(1)

                if name:
                    target = TypeHintTarget(
                        line_number=violation.target_coordinate.line,
                        name=name,
                        hint_type=hint_type,
                        type_annotation=type_annotation,
                    )
                    type_hint_targets.append(target)

    if type_hint_targets:
        return SurgicalTypeHintInserter(type_hint_targets)
    return None


def create_trailing_whitespace_fixer(violations) -> SurgicalTrailingWhitespaceFixer | None:
    """
    Factory function to create trailing whitespace fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTrailingWhitespaceFixer instance or None if no violations
    """
    for violation in violations:
        if violation.constraint_type == "trailing_whitespace":
            return SurgicalTrailingWhitespaceFixer()
    return None


def create_blank_line_normalizer(violations, max_blank_lines: int = 2) -> SurgicalBlankLineNormalizer | None:
    """
    Factory function to create blank line normalizer from violations.

    Args:
        violations: List of ViolationConstraint objects
        max_blank_lines: Maximum allowed consecutive blank lines

    Returns:
        SurgicalBlankLineNormalizer instance or None if no violations
    """
    for violation in violations:
        if violation.constraint_type == "excessive_blank_lines":
            return SurgicalBlankLineNormalizer(max_blank_lines=max_blank_lines)
    return None


def create_import_remover(violations) -> SurgicalImportRemover | None:
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


def create_docstring_inserter(violations) -> SurgicalDocstringInserter | None:
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
                # Extract name from message if possible
                name = None
                node_type = "class"
                if violation.message:
                    msg_lower = violation.message.lower()
                    if "class" in msg_lower:
                        node_type = "class"
                        # Try to extract class name from patterns like:
                        # "Class MyClass missing docstring"
                        # "Class 'MyClass' missing docstring"
                        import re

                        match = re.search(r"[Cc]lass\s+['\"]?(\w+)['\"]?", violation.message)
                        if match:
                            name = match.group(1)
                    elif "function" in msg_lower or "def " in msg_lower:
                        node_type = "function"
                        # Try to extract function name
                        match = re.search(r"[Ff]unction\s+['\"]?(\w+)['\"]?", violation.message)
                        if match:
                            name = match.group(1)

                target = DocstringTarget(
                    line_number=violation.target_coordinate.line,
                    name=name,
                    node_type=node_type,
                )
                docstring_targets.append(target)

    if docstring_targets:
        return SurgicalDocstringInserter(docstring_targets)
    return None


def create_bare_except_fixer(violations) -> SurgicalBareExceptFixer | None:
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
                target = BareExceptTarget(
                    line_number=violation.target_coordinate.line,
                )
                except_targets.append(target)

    if except_targets:
        # Use fix_all=True since CST nodes don't have reliable position metadata
        return SurgicalBareExceptFixer(targets=except_targets, fix_all=True)
    return None


def create_future_import_inserter(
    violations, future_imports: list[str] | None = None
) -> SurgicalFutureImportInserter | None:
    """
    Factory function to create future import inserter from violations.

    Args:
        violations: List of ViolationConstraint objects
        future_imports: List of future imports to add (default: ["annotations"])

    Returns:
        SurgicalFutureImportInserter instance or None if no future import violations
    """
    for violation in violations:
        if violation.constraint_type == "missing_future_import":
            return SurgicalFutureImportInserter(future_imports=future_imports)

    return None
