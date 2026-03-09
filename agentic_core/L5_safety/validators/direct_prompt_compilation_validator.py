"""
Direct Prompt Compilation Anti-Pattern Detector

Detects prompt strings being assembled outside the AirlockAssembler
(the designated Assembly Stage).  Direct f-string / concatenation /
str.join / format() construction of final prompts bypasses:
  - deterministic composition and manifest hashing
  - authority ordering (S0 > I0 > D0 > C0 > U0)
  - injection scanning

Pattern Detection:
- f-strings that reference known prompt-slot names (s0_, i0_, d0_, c0_, u0_)
  outside the canonical assembly_stage module
- BinOp string concatenation ("+") involving prompt-slot variables
- str.join() / str.format() calls on prompt-slot variables
"""

from __future__ import annotations

import ast
from pathlib import Path

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_PROMPT_SLOT_PREFIXES = ("s0_", "i0_", "d0_", "c0_", "u0_")
_ASSEMBLY_MODULE_STEMS = {"assembly_stage", "airlock_assembler"}
_WHITELIST_COMMENT = "# guardian: allow-direct-prompt-compilation"


def _is_prompt_slot_name(name: str) -> bool:
    """Return True if the name looks like a prompt slot variable."""
    return any(name.startswith(p) for p in _PROMPT_SLOT_PREFIXES)


def _names_in_node(node: ast.expr) -> list[str]:
    """Collect all Name and Attribute identifiers referenced in an expression."""
    names: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.append(child.id)
        elif isinstance(child, ast.Attribute):
            names.append(child.attr)
    return names


class DirectPromptCompilationDetector(AntiPatternDetector):
    """
    Detects direct prompt string construction outside the Assembly Stage.

    All final prompt strings MUST be composed via AirlockAssembler.
    Any f-string / concatenation / join involving prompt-slot variables
    outside assembly_stage.py is a governance violation.
    """

    WHITELIST_COMMENT = _WHITELIST_COMMENT

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect direct prompt compilation patterns."""
        if self._is_assembly_module(file_path):
            return []

        violations: list[AntiPatternViolation] = []
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            source_lines = []

        for node in ast.walk(tree):
            v = self._check_node(node, file_path, source_lines)
            if v:
                violations.append(v)

        return violations

    # ------------------------------------------------------------------
    # node-level checks
    # ------------------------------------------------------------------

    def _check_node(
        self,
        node: ast.AST,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            return None
        if self._is_whitelisted_line(source_lines, lineno):
            return None

        # f-string containing prompt-slot references
        if isinstance(node, ast.JoinedStr):
            slot_names = []
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and _is_prompt_slot_name(child.id):
                    slot_names.append(child.id)
            if slot_names:
                return AntiPatternViolation(
                    file_path=file_path,
                    line_number=lineno,
                    category=self.category,
                    message=(
                        f"Direct prompt compilation: f-string references prompt-slot "
                        f"variable(s) {slot_names!r} outside Assembly Stage"
                    ),
                    evidence=self._get_source_line(file_path, lineno),
                    severity="error",
                    suggested_fix=(
                        "Pass slot values to AirlockAssembler.assemble() instead of "
                        "concatenating them manually."
                    ),
                )

        # BinOp string + involving prompt-slot names
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            names = _names_in_node(node.left) + _names_in_node(node.right)
            slot_names = [n for n in names if _is_prompt_slot_name(n)]
            if slot_names:
                return AntiPatternViolation(
                    file_path=file_path,
                    line_number=lineno,
                    category=self.category,
                    message=(
                        f"Direct prompt compilation: string concatenation (+) references "
                        f"prompt-slot variable(s) {slot_names!r} outside Assembly Stage"
                    ),
                    evidence=self._get_source_line(file_path, lineno),
                    severity="error",
                    suggested_fix=("Use AirlockAssembler.assemble() for all prompt slot composition."),
                )

        # str.join() / str.format() on prompt-slot variables
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("join", "format"):
                all_names: list[str] = []
                for arg in node.args:
                    all_names.extend(_names_in_node(arg))
                for kw in node.keywords:
                    if kw.value:
                        all_names.extend(_names_in_node(kw.value))
                # Also check the object being called on
                all_names.extend(_names_in_node(node.func.value))
                slot_names = [n for n in all_names if _is_prompt_slot_name(n)]
                if slot_names:
                    return AntiPatternViolation(
                        file_path=file_path,
                        line_number=lineno,
                        category=self.category,
                        message=(
                            f"Direct prompt compilation: str.{node.func.attr}() references "
                            f"prompt-slot variable(s) {slot_names!r} outside Assembly Stage"
                        ),
                        evidence=self._get_source_line(file_path, lineno),
                        severity="error",
                        suggested_fix=("Use AirlockAssembler.assemble() for all prompt slot composition."),
                    )

        return None

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _is_assembly_module(self, file_path: Path) -> bool:
        """Return True if this file IS the canonical assembly module (allowlisted)."""
        return file_path.stem in _ASSEMBLY_MODULE_STEMS

    def _is_whitelisted_line(self, source_lines: list[str], lineno: int) -> bool:
        for check_line in (lineno - 1, lineno - 2):
            if 0 <= check_line < len(source_lines):
                if _WHITELIST_COMMENT in source_lines[check_line]:
                    return True
        return False


__all__ = ["DirectPromptCompilationDetector"]
