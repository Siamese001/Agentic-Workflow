from __future__ import annotations

"""ASTEnforcementMixin — Ultra L5 Mixin for AST Enforcement (Jan 01, 2026)

Add to validators/enforcers for precise AST analysis (no regex).
- Detect snake_case classes, aliases, etc.
- Use in _ast_audit override
- Maximizes AST opportunities across all validators
"""


import ast
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
)


class ASTEnforcementMixin:
    """Mixin for sovereign AST enforcement.

    Provides precise AST-based code analysis capabilities for validators
    and enforcers. Eliminates regex fragility with proper syntax tree parsing.
    """

    def _ast_audit_file(self, content: str) -> dict:
        """Ultra AST audit mixin — precise class/alias detection.

        Args:
            content: Python source code to analyze

        Returns:
            Dict with counts: {
                "snake_classes": int,
                "aliases": int,
                "pascal_classes": int,
                "enums": int,
                "dataclasses": int
            }
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "snake_classes": 0,
                "aliases": 0,
                "pascal_classes": 0,
                "enums": 0,
                "dataclasses": 0,
                "syntax_error": True,
            }

        # Count snake_case classes (lowercase or contains underscore)
        snake_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and (node.name[0].islower() or "_" in node.name)
        )

        # Count PascalCase classes (proper naming)
        pascal_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name[0].isupper() and "_" not in node.name
        )

        # Count Enum classes
        enum_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(isinstance(base, ast.Name) and base.id == "Enum" for base in node.bases)
        )

        # Count dataclasses (via decorator)
        dataclass_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(
                (isinstance(dec, ast.Name) and dec.id == "dataclass")
                or (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Name)
                    and dec.func.id == "dataclass"
                )
                for dec in node.decorator_list
            )
        )

        # Count backward-compatibility aliases (PascalCase = snake_case)
        # Using AST for precision: Assign nodes with single target
        alias_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Name):
                    # PascalCase target = snake_case value
                    if target.id[0].isupper() and node.value.id[0].islower():
                        alias_count += 1

        return {
            "snake_classes": snake_count,
            "aliases": alias_count,
            "pascal_classes": pascal_count,
            "enums": enum_count,
            "dataclasses": dataclass_count,
            "syntax_error": False,
        }

    def _ast_audit_repo(self, repo_root: Path, target_prefixes: list[str] | None = None) -> dict:
        """Audit entire repository for snake_case violations.

        Args:
            repo_root: Root directory to scan
            target_prefixes: List of directory prefixes to include (e.g., [AGENTIC_CORE_DIR, "apps_"])

        Returns:
            Dict with aggregated results and file list
        """
        if target_prefixes is None:
            target_prefixes = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]

        files_with_violations = []
        total_snake = 0
        total_aliases = 0
        total_pascal = 0

        # Phase 4: Use ssot_discovery instead of rglob for performance
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        all_files = get_python_files(repo_root)

        for path in all_files:
            # Filter by target prefixes
            if not any(prefix in str(path) for prefix in target_prefixes):
                continue

            try:
                content = path.read_text(encoding="utf-8")
                audit = self._ast_audit_file(content)

                if audit["snake_classes"] or audit["aliases"]:
                    files_with_violations.append(
                        {
                            "path": str(path),
                            "snake_classes": audit["snake_classes"],
                            "aliases": audit["aliases"],
                            "pascal_classes": audit["pascal_classes"],
                        },
                    )
                    total_snake += audit["snake_classes"]
                    total_aliases += audit["aliases"]

                total_pascal += audit["pascal_classes"]

            except (UnicodeDecodeError, PermissionError):
                continue

        return {
            "files": files_with_violations,
            "total_snake_classes": total_snake,
            "total_aliases": total_aliases,
            "total_pascal_classes": total_pascal,
            "violation_count": len(files_with_violations),
            "summary": f"{len(files_with_violations)} files | {total_snake} snake_classes | {total_aliases} aliases",
        }

    def _extract_class_names(self, content: str) -> list[str]:
        """Extract all class names from Python source.

        Args:
            content: Python source code

        Returns:
            List of class names
        """
        try:
            tree = ast.parse(content)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except SyntaxError:
            return []

    def _is_snake_case_class(self, class_name: str) -> bool:
        """Check if class name is snake_case (Violation).

        Args:
            class_name: Name to check

        Returns:
            True if snake_case, False if PascalCase
        """
        return class_name[0].islower() or "_" in class_name
