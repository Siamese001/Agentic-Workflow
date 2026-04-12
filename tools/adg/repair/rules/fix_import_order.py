"""AUTO_FIX rule: Sort imports according to policy.

Reorders imports to follow the project's import ordering policy:
1. Standard library imports
2. Third-party imports
3. Local application imports
"""

from __future__ import annotations

from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_import_order", priority=50)
class FixImportOrderRule(BaseRepairRule):
    """Reorders imports to follow project policy.

    Groups imports into:
    1. Standard library (os, sys, typing, etc.)
    2. Third-party (external dependencies)
    3. Local/project imports

    Safety: Medium - changes import order but not semantics
    """

    rule_name = "Fix Import Order"
    rule_description = "Sorts imports according to project policy"
    rule_priority = 50

    HANDLED_ISSUES = {
        "import_order",
        "unsorted_imports",
    }

    # Standard library modules (common ones)
    STDLIB_MODULES = {
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "collections",
        "concurrent",
        "contextlib",
        "copy",
        "csv",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "functools",
        "glob",
        "hashlib",
        "html",
        "http",
        "importlib",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "multiprocessing",
        "operator",
        "os",
        "pathlib",
        "pickle",
        "platform",
        "random",
        "re",
        "shutil",
        "signal",
        "socket",
        "sqlite3",
        "string",
        "subprocess",
        "sys",
        "tempfile",
        "textwrap",
        "threading",
        "time",
        "traceback",
        "typing",
        "unittest",
        "urllib",
        "uuid",
        "warnings",
        "weakref",
        "xml",
        "zipfile",
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
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Cannot read file: {e}"

        # Check if there are imports that need reordering
        import_blocks = self._extract_import_blocks(content)

        if len(import_blocks) < 2:
            return False, "Not enough imports to reorder"

        # Check if already sorted
        if self._is_sorted(import_blocks):
            return False, "Imports already sorted"

        return True, f"Can sort {len(import_blocks)} import groups"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by sorting imports."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")

            # Extract import blocks
            import_blocks = self._extract_import_blocks(original_content)

            if not import_blocks:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No imports found",
                )

            # Sort the imports
            sorted_imports = self._sort_imports(import_blocks)

            # Reconstruct the file
            new_content = self._reconstruct_with_sorted_imports(
                original_content,
                import_blocks,
                sorted_imports,
            )

            path.write_text(new_content, encoding="utf-8")

            return FixResult(
                deficiency_id=deficiency.id,
                success=True,
                original_content=original_content,
                new_content=new_content,
            )

        except Exception as e:
            return FixResult(
                deficiency_id=deficiency.id,
                success=False,
                error_message=str(e),
            )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify that imports are sorted."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
            import_blocks = self._extract_import_blocks(content)
            return self._is_sorted(import_blocks)
        except Exception:
            return False

    def _extract_import_blocks(self, content: str) -> list[tuple[int, int, str]]:
        """Extract import blocks from content.

        Returns:
            List of (start_line, end_line, text) tuples
        """
        lines = content.split("\n")
        blocks = []

        current_block_start = None
        current_block_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if this is an import line
            if stripped.startswith("import ") or stripped.startswith("from "):
                if current_block_start is None:
                    current_block_start = i
                current_block_lines.append(line)
            elif stripped == "" and current_block_start is not None:
                # Blank line ends import block
                if current_block_lines:
                    block_text = "\n".join(current_block_lines)
                    blocks.append((current_block_start, i, block_text))
                current_block_start = None
                current_block_lines = []
            elif current_block_start is not None:
                # Non-import, non-blank line ends import block
                if current_block_lines:
                    block_text = "\n".join(current_block_lines)
                    blocks.append((current_block_start, i, block_text))
                current_block_start = None
                current_block_lines = []

        # Handle trailing import block
        if current_block_start is not None and current_block_lines:
            block_text = "\n".join(current_block_lines)
            blocks.append((current_block_start, len(lines), block_text))

        return blocks

    def _is_sorted(self, blocks: list[tuple[int, int, str]]) -> bool:
        """Check if imports are already sorted."""
        if len(blocks) < 2:
            return True

        # Check if blocks follow stdlib -> third-party -> local order
        categories = [self._categorize_import_block(b[2]) for b in blocks]

        expected_order = ["stdlib", "third_party", "local"]
        current_idx = 0

        for cat in categories:
            if cat == expected_order[current_idx]:
                continue
            elif current_idx < len(expected_order) - 1 and cat == expected_order[current_idx + 1]:
                current_idx += 1
            else:
                return False

        return True

    def _categorize_import_block(self, block_text: str) -> str:
        """Categorize an import block."""
        lines = block_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("import "):
                module = line.split()[1].split(".")[0]
                if module in self.STDLIB_MODULES:
                    return "stdlib"
                elif module.startswith("tools") or module.startswith("agentic"):
                    return "local"
                else:
                    return "third_party"
            elif line.startswith("from "):
                module = line.split()[1].split(".")[0]
                if module in self.STDLIB_MODULES:
                    return "stdlib"
                elif module.startswith("tools") or module.startswith("agentic"):
                    return "local"
                else:
                    return "third_party"

        return "unknown"

    def _sort_imports(self, blocks: list[tuple[int, int, str]]) -> list[str]:
        """Sort import blocks by category."""
        # Separate by category
        stdlib = []
        third_party = []
        local = []

        for start, end, text in blocks:
            category = self._categorize_import_block(text)
            if category == "stdlib":
                stdlib.append(text)
            elif category == "third_party":
                third_party.append(text)
            elif category == "local":
                local.append(text)

        # Combine in order with blank lines between
        result = []
        if stdlib:
            result.extend(stdlib)
            result.append("")
        if third_party:
            result.extend(third_party)
            result.append("")
        if local:
            result.extend(local)

        return result

    def _reconstruct_with_sorted_imports(
        self,
        original_content: str,
        original_blocks: list[tuple[int, int, str]],
        sorted_imports: list[str],
    ) -> str:
        """Reconstruct file with sorted imports."""
        lines = original_content.split("\n")

        if not original_blocks:
            return original_content

        # Find the span of all import blocks
        first_start = original_blocks[0][0]
        last_end = original_blocks[-1][1]

        # Build new content
        new_lines = lines[:first_start]
        new_lines.extend(sorted_imports)
        new_lines.extend(lines[last_end:])

        return "\n".join(new_lines)
