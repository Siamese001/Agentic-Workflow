from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "ast_enforcement_mixin")
_emit_applies_guardrail("p0", "ast_enforcement_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ast_enforcement_mixin", "policy_binding")
_emit_snapshots_state("p0", "ast_enforcement_mixin", "state_snapshot")
emit_replay_key("p0", "ast_enforcement_mixin")
emit_determinism_digest("p0", "ast_enforcement_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"ASTEnforcementMixin — Ultra L5 Mixin for AST Enforcement (Jan 01, 2026)\n\nAdd to validators/enforcers for precise AST analysis (no regex).\n- Detect snake_case classes, aliases, etc.\n- Use in _ast_audit override\n- Maximizes AST opportunities across all validators\n"
import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


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
        snake_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and (node.name[0].islower() or "_" in node.name)
        )
        pascal_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name[0].isupper() and ("_" not in node.name)
        )
        enum_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(isinstance(base, ast.Name) and base.id == "Enum" for base in node.bases)
        )
        dataclass_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(
                isinstance(dec, ast.Name)
                and dec.id == "dataclass"
                or (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Name)
                    and (dec.func.id == "dataclass")
                )
                for dec in node.decorator_list
            )
        )
        alias_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Name):
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
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        all_files = get_python_files(repo_root)
        for path in all_files:
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
                        }
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
