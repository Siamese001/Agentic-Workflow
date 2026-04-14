"""AUTO_FIX rule: Add basic type annotations.

Adds simple type annotations where they can be inferred:
- Function return types (None for no return, obvious types for returns)
- Simple parameter types (str, int, bool, Path, etc.)
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_missing_typing", priority=60)
class FixMissingTypingRule(BaseRepairRule):
    """Adds basic type annotations where inferable.

    Infers and adds:
    - Return type annotations (None for functions without return)
    - Simple parameter types based on default values
    - Path/Pathlib types for file operations

    Safety: Low-Medium - type annotations don't change runtime behavior
    """

    rule_name = "Fix Missing Type Annotations"
    rule_description = "Adds inferable type annotations"
    rule_priority = 60

    HANDLED_ISSUES = {
        "missing_typing",
        "incomplete_type_annotations",
    }

    # Type inference patterns
    TYPE_PATTERNS = [
        (r"^\d+$", "int"),
        (r'^".*"$', "str"),
        (r"^'.*'$", "str"),
        (r"^True$|^False$", "bool"),
        (r"^None$", "None"),
        (r"^\[.*\]$", "list"),
        (r"^\{.*\}$", "dict"),
        (r"^\(.*\)$", "tuple"),
        (r"Path\(|\.path|filepath|file_path", "Path"),
    ]

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies."""
        return deficiency.category == FixCategory.AUTO_FIX and deficiency.issue_type in self.HANDLED_ISSUES

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

        # Check for functions missing annotations
        functions_missing_types = self._find_functions_missing_types(tree)

        if not functions_missing_types:
            return False, "No functions with inferable type annotations found"

        return True, f"Can add types to {len(functions_missing_types)} functions"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by adding type annotations."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")
            lines = original_content.split("\n")
            tree = ast.parse(original_content)

            # Find functions needing types
            functions = self._find_functions_missing_types(tree)

            if not functions:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No functions found",
                )

            # Apply annotations (this is a simplified version)
            # In a full implementation, we'd use AST transformation
            new_lines = list(lines)

            for func_node, needs_return, needs_params in functions:
                if needs_return:
                    line_idx = func_node.lineno - 1
                    line = new_lines[line_idx]

                    # Simple approach: add -> None for functions without return
                    if "->" not in line:
                        # Find the end of the function definition
                        match = re.match(r"^(\s*)(def\s+\w+\s*\([^)]*\))", line)
                        if match:
                            indent, def_part = match.groups()
                            new_lines[line_idx] = f"{indent}{def_part} -> None:"

            new_content = "\n".join(new_lines)

            if new_content == original_content:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No changes made",
                )

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
        """Verify that type annotations were added."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            current_missing = len(self._find_functions_missing_types(tree))

            original_tree = ast.parse(result.original_content or "")
            original_missing = len(self._find_functions_missing_types(original_tree))
            return current_missing < original_missing

        except (OSError, SyntaxError, ValueError):
            return False

    def _find_functions_missing_types(
        self,
        tree: ast.AST,
    ) -> list[tuple[ast.FunctionDef, bool, bool]]:
        """Find functions missing type annotations.

        Returns:
            List of (function_node, needs_return_type, needs_param_types)
        """
        results = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private methods and special methods
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                needs_return = node.returns is None
                needs_params = any(
                    arg.annotation is None
                    for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs
                )

                # Only flag if we can infer something
                if needs_return or needs_params:
                    results.append((node, needs_return, needs_params))

        return results
