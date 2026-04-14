"""AUTO_FIX rule: Remove unused imports.

Detects and removes confirmed unused imports from Python files.
Uses AST analysis to verify imports are truly unused.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_unused_imports", priority=40)
class FixUnusedImportsRule(BaseRepairRule):
    """Removes confirmed unused imports from Python files.

    Uses AST analysis to:
    1. Find all import statements
    2. Check if imported names are used in the module
    3. Remove imports that are not referenced anywhere

    Safety: Medium - only removes confirmed unused imports
    """

    rule_name = "Fix Unused Imports"
    rule_description = "Removes confirmed unused import statements"
    rule_priority = 40

    HANDLED_ISSUES = {
        "unused_import",
        "dead_import",
    }

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

        # Check for unused imports
        unused = self._find_unused_imports(tree)

        if not unused:
            return False, "No unused imports found"

        return True, f"Can remove {len(unused)} unused imports"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by removing unused imports."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")
            lines = original_content.split("\n")
            tree = ast.parse(original_content)

            # Find unused imports
            unused = self._find_unused_imports(tree)

            if not unused:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No unused imports found",
                )

            # Calculate line numbers to remove
            lines_to_remove = set()
            for node in unused:
                if hasattr(node, "lineno"):
                    # AST lines are 1-indexed, our lines list is 0-indexed
                    lines_to_remove.add(node.lineno - 1)

            # Build new content with lines removed
            new_lines = []
            for i, line in enumerate(lines):
                if i not in lines_to_remove:
                    new_lines.append(line)

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
        """Verify that unused imports were removed."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Check no unused imports remain
            unused = self._find_unused_imports(tree)
            return len(unused) == 0

        except (OSError, SyntaxError):
            return False

    def _find_unused_imports(self, tree: ast.AST) -> list[ast.AST]:
        """Find unused import statements in AST.

        Returns:
            List of AST nodes for unused import statements
        """
        # Collect imported names grouped by AST node so partially used imports are preserved.
        imports_by_node: dict[ast.AST, set[str]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names: set[str] = set()
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    names.add(name.split(".")[0])
                imports_by_node[node] = names
            elif isinstance(node, ast.ImportFrom):
                names = {alias.asname if alias.asname else alias.name for alias in node.names}
                imports_by_node[node] = names

        # Collect all used names
        used_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Load, ast.Store)):
                    used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For x.y, add x to used names
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        # Only remove a statement when every imported alias in that statement is unused.
        removable_nodes: list[ast.AST] = []
        for node, imported in imports_by_node.items():
            public_imports = {name for name in imported if not name.startswith("_")}
            if public_imports and public_imports.isdisjoint(used_names):
                removable_nodes.append(node)

        return removable_nodes
