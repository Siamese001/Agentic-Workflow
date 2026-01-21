"""
CanonASTValidator - Base class for AST-based code validation.

Provides the foundation for all AST validators in the L1 cognition layer.
Handles TYPE_CHECKING block detection, violation reporting, and file parsing.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CanonASTValidator(ast.NodeVisitor):
    """
    Base class for AST-based code validators.

    Features:
    - Automatic TYPE_CHECKING block detection (skips validation inside)
    - Standardized violation reporting with line/column context
    - File parsing utilities
    - Integration with HealerMixin chain

    Subclasses should override visit_* methods to implement specific checks.
    """

    violations: list[dict[str, Any]] = field(default_factory=list)
    in_type_checking: bool = False
    current_file: Path | None = None

    def __post_init__(self) -> None:
        """Initialize the validator."""
        if self.violations is None:
            self.violations = []

    def visit_If(self, node: ast.If) -> Any:
        """
        Detect TYPE_CHECKING blocks and set flag.

        TYPE_CHECKING blocks are used for type hints that shouldn't be
        evaluated at runtime. We skip validation inside these blocks.
        """
        is_type_checking = False

        # Check for: if TYPE_CHECKING:
        if isinstance(node.test, ast.Name) and node.test.id == 'TYPE_CHECKING':
            is_type_checking = True

        # Check for: if typing.TYPE_CHECKING:
        elif isinstance(node.test, ast.Attribute):
            if (isinstance(node.test.value, ast.Name) and
                node.test.value.id == 'typing' and
                node.test.attr == 'TYPE_CHECKING'):
                is_type_checking = True

        if is_type_checking:
            # Save state, set flag, visit body, restore state
            old_state = self.in_type_checking
            self.in_type_checking = True
            for child in node.body:
                self.visit(child)
            self.in_type_checking = old_state
            # Visit else clause with normal state
            for child in node.orelse:
                self.visit(child)
        else:
            self.generic_visit(node)

        return None

    def report(self, message: str, node: ast.AST) -> None:
        """
        Report a violation with standardized format.

        Args:
            message: Description of the violation
            node: AST node where violation occurred
        """
        violation = {
            'type': 'AST_VIOLATION',
            'message': message,
            'lineno': getattr(node, 'lineno', 0),
            'col_offset': getattr(node, 'col_offset', 0),
            'agent': self.__class__.__name__,
            'file': str(self.current_file) if self.current_file else None,
        }
        self.violations.append(violation)

    def add_violation(self, violation: dict[str, Any]) -> None:
        """
        Add a pre-formatted violation dict.

        Args:
            violation: Violation dictionary with type, message, lineno, etc.
        """
        self.violations.append(violation)

    def validate(self, source: str, file_path: Path | None = None) -> list[dict[str, Any]]:
        """
        Validate source code and return violations.

        Args:
            source: Python source code to validate
            file_path: Optional path for error reporting

        Returns:
            List of violation dictionaries
        """
        self.violations = []
        self.current_file = file_path
        self.in_type_checking = False

        try:
            tree = ast.parse(source)
            self.visit(tree)
        except SyntaxError as e:
            self.violations.append({
                'type': 'SYNTAX_ERROR',
                'message': f'Syntax error: {e}',
                'lineno': e.lineno or 0,
                'col_offset': e.offset or 0,
                'agent': self.__class__.__name__,
                'file': str(file_path) if file_path else None,
            })

        return self.violations

    def validate_file(self, file_path: Path) -> list[dict[str, Any]]:
        """
        Validate a file and return violations.

        Args:
            file_path: Path to Python file

        Returns:
            List of violation dictionaries
        """
        try:
            source = file_path.read_text(encoding='utf-8')
            return self.validate(source, file_path)
        except Exception as e:
            return [{
                'type': 'FILE_ERROR',
                'message': f'Could not read file: {e}',
                'lineno': 0,
                'col_offset': 0,
                'agent': self.__class__.__name__,
                'file': str(file_path),
            }]

    def get_violations(self) -> list[dict[str, Any]]:
        """Return all collected violations."""
        return self.violations

    def clear_violations(self) -> None:
        """Clear all collected violations."""
        self.violations = []


def parse_and_validate(
    file_path: Path,
    content: str,
    key_id: int,
    validator_class: type[CanonASTValidator]
) -> list[dict[str, Any]]:
    """
    Parse content and validate using specified validator class.

    Args:
        file_path: Path for error reporting
        content: Python source code
        key_id: Canon key ID for this validation
        validator_class: Validator class to use

    Returns:
        List of violations with key_id added
    """
    validator = validator_class()
    violations = validator.validate(content, file_path)

    # Add key_id to each violation
    for v in violations:
        v['key_id'] = key_id

    return violations
