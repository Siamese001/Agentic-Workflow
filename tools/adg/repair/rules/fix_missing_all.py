"""AUTO_FIX rule: Add missing __all__ exports.

Detects modules with exports but no __all__ declaration and
auto-generates __all__ from detected exports.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_missing_all", priority=10)
class FixMissingAllRule(BaseRepairRule):
    """Adds missing __all__ declarations to modules.

    This rule:
    1. Detects modules with exports but no __all__
    2. Generates __all__ from class/function definitions
    3. Inserts __all__ at the appropriate location in the file

    Safety: High - __all__ is additive only, doesn't change behavior
    """

    rule_name = "Fix Missing __all__"
    rule_description = "Adds missing __all__ exports to Python modules"
    rule_priority = 10  # High priority - simple, safe fix

    # Issue types this rule can handle
    HANDLED_ISSUES = {
        "missing_all",
        "unknown_layer_inferrable",
        "unknown_layer_not_inferrable",
    }

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies to the deficiency.

        Matches deficiencies related to module structure.
        """
        return deficiency.category == FixCategory.AUTO_FIX and deficiency.issue_type in self.HANDLED_ISSUES

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if the fix can be safely applied.

        For __all__ addition:
        - File must exist and be readable/writable
        - File must not already have __all__
        - File must be a Python module
        """
        file_path = deficiency.file_path

        if file_path == "ADG_METADATA":
            return False, "Cannot fix ADG metadata files"

        if not file_path.endswith(".py"):
            return False, "Not a Python file"

        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Cannot read file: {e}"

        # Check if __all__ already exists
        if "__all__" in content:
            return False, "__all__ already defined in module"

        # Try to parse as Python
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return False, f"Syntax error in file: {e}"

        return True, "Can add __all__"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by adding __all__ to the module.

        Args:
            deficiency: The deficiency to fix

        Returns:
            FixResult with details
        """
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")
            tree = ast.parse(original_content)

            # Extract exports from the AST
            exports = self._extract_exports(tree)

            if not exports:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No exports found in module",
                )

            # Generate __all__ line
            all_declaration = self._generate_all_declaration(exports)

            # Find insertion point (after imports, before first definition)
            insertion_point = self._find_insertion_point(original_content, tree)

            # Insert __all__
            new_content = (
                original_content[:insertion_point] + all_declaration + original_content[insertion_point:]
            )

            # Write the fixed content
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
        """Verify that __all__ was added correctly."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
            # Check __all__ exists and is valid Python
            if "__all__" not in content:
                return False

            tree = ast.parse(content)

            # Find __all__ assignment
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            return True

            return False

        except (OSError, SyntaxError):
            return False

    def _extract_exports(self, tree: ast.AST) -> list[str]:
        """Extract public exports from AST.

        Returns list of names that should be in __all__.
        """
        exports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Skip private classes (starting with _)
                if not node.name.startswith("_"):
                    exports.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                # Skip private functions
                if not node.name.startswith("_"):
                    exports.append(node.name)
            elif isinstance(node, ast.Assign):
                # Module-level constants (UPPERCASE)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper() and not target.id.startswith("_"):
                            exports.append(target.id)

        # Remove duplicates and sort
        return sorted(set(exports))

    def _generate_all_declaration(self, exports: list[str]) -> str:
        """Generate the __all__ declaration string."""
        lines = ["__all__ = ["]
        for export in exports:
            lines.append(f'    "{export}",')
        lines.append("]")
        lines.append("")
        return "\n".join(lines)

    def _find_insertion_point(self, content: str, tree: ast.AST) -> int:
        """Find the best insertion point for __all__.

        Insert after imports but before first definition.
        """
        # Find the end of all imports
        last_import_end = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Get the line number of this import
                line_num = node.end_lineno or node.lineno
                # Calculate position (1-indexed to 0-indexed)
                pos = self._get_line_start(content, line_num)
                if pos > last_import_end:
                    last_import_end = pos

        if last_import_end > 0:
            return last_import_end

        # If no imports, find first non-comment line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Found first non-empty, non-comment line
                return sum(len(l) + 1 for l in lines[:i])

        # Fallback: end of file
        return len(content)

    def _get_line_start(self, content: str, line_num: int) -> int:
        """Get the byte position at the start of a line."""
        lines = content.split("\n")
        pos = 0
        for i in range(min(line_num, len(lines))):
            pos += len(lines[i]) + 1  # +1 for newline
        return pos
