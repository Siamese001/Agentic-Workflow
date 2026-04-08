"""AUTO_FIX rule: Add placeholder docstrings.

Adds placeholder docstrings to modules, classes, and functions
that are missing documentation.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_docstring_placeholder", priority=70)
class FixDocstringPlaceholderRule(BaseRepairRule):
    """Adds placeholder docstrings to undocumented code elements.

    Adds docstrings to:
    - Modules without module docstrings
    - Public classes without docstrings
    - Public functions without docstrings

    Safety: High - docstrings don't affect runtime behavior
    """

    rule_name = "Fix Missing Docstrings"
    rule_description = "Adds placeholder docstrings to modules, classes, and functions"
    rule_priority = 70

    HANDLED_ISSUES = {
        "missing_docstring",
        "missing_module_docstring",
    }

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies."""
        return (
            deficiency.category == FixCategory.AUTO_FIX
            and deficiency.issue_type in self.HANDLED_ISSUES
        )

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if fix can be applied."""
        file_path = deficiency.file_path

        if file_path == "ADG_METADATA":
            return False, "Cannot fix ADG metadata"

        if not file_path.endswith(".py"):
            return False, "Not a Python file"

        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Cannot read file: {e}"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        # Check for missing docstrings
        missing = self._find_missing_docstrings(tree)

        if not missing:
            return False, "No missing docstrings found"

        return True, f"Can add {len(missing)} docstrings"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by adding placeholder docstrings."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")
            lines = original_content.split("\n")
            tree = ast.parse(original_content)

            # Find missing docstrings
            missing = self._find_missing_docstrings(tree)

            if not missing:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No missing docstrings found",
                )

            # Add docstrings (simplified approach)
            new_lines = list(lines)

            for node, element_type in missing:
                line_idx = node.lineno - 1
                indent = self._get_indent(new_lines[line_idx])

                # Generate appropriate docstring
                if element_type == "module":
                    docstring = f'{indent}"""{node.get("name", "Module")}."""\n'
                elif element_type == "class":
                    docstring = f'{indent}\'\'\'{node.name}.\'\'\'\n'
                else:  # function
                    docstring = f'{indent}\'\'\'{node.name}().\'\'\'\n'

                # Insert after the definition line
                insert_idx = line_idx + 1
                new_lines.insert(insert_idx, docstring.rstrip())

            new_content = "\n".join(new_lines)
            path.write_text(new_content, encoding="utf-8")

            return FixResult(
                deficiency_id=deficiency.id,
                success=True,
                original_content=original_content,
                new_content=new_content,
            )

        except (OSError, SyntaxError, ValueError) as e:
            return FixResult(
                deficiency_id=deficiency.id,
                success=False,
                error_message=str(e),
            )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify that docstrings were added."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Check fewer missing docstrings
            missing = self._find_missing_docstrings(tree)
            return len(missing) == 0

        except (OSError, SyntaxError):
            return False

    def _find_missing_docstrings(self, tree: ast.AST) -> list[tuple[ast.AST, str]]:
        """Find code elements missing docstrings.

        Returns:
            List of (node, type) tuples where type is 'module', 'class', or 'function'
        """
        missing = []

        # Check for module docstring
        has_module_docstring = False
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    has_module_docstring = True
                    break

        if not has_module_docstring:
            missing.append((tree, "module"))

        # Check classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Skip private classes
                if node.name.startswith("_"):
                    continue

                # Check if has docstring
                if not self._has_docstring(node):
                    missing.append((node, "class"))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private functions and special methods
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                # Check if has docstring
                if not self._has_docstring(node):
                    missing.append((node, "function"))

        return missing

    def _has_docstring(self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if a node has a docstring."""
        if not node.body:
            return False

        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            return isinstance(first.value.value, str)

        return False

    def _get_indent(self, line: str) -> str:
        """Get the indentation of a line."""
        stripped = line.lstrip()
        if stripped:
            return line[: len(line) - len(stripped)]
        return ""
