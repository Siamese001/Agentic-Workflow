"""
Silent Swallower Anti-Pattern Detector

Detects try/except blocks that catch generic exceptions and suppress
them without proper handling (raising, returning failure status).

Pattern Detection:
- except Exception: with only pass, print(), or logger calls
- except Exception as e: without raise or return False/None
- Bare except: clauses
"""

import ast
from pathlib import Path

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)


class SilentSwallowerDetector(AntiPatternDetector):
    """
    Detects exception handlers that silently swallow errors.

    These patterns prevent proper error propagation and cause
    downstream agents to operate on failed state.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-silent-swallow"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files (test files, debug scripts)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "debug_*.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.SILENT_SWALLOWER

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect silent swallower patterns in the AST."""
        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                violation = self._check_except_handler(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_except_handler(
        self,
        node: ast.ExceptHandler,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if an except handler is a silent swallower."""

        # Check for whitelist comment on previous line
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check if catching generic Exception or bare except
        is_generic_exception = False
        exception_name = "Exception"

        if node.type is None:
            # Bare except:
            is_generic_exception = True
            exception_name = "(bare except)"
        elif isinstance(node.type, ast.Name):
            if node.type.id in ("Exception", "BaseException"):
                is_generic_exception = True
                exception_name = node.type.id
        elif isinstance(node.type, ast.Tuple):
            # Check if Exception is in the tuple
            for elt in node.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                    is_generic_exception = True
                    exception_name = elt.id
                    break

        if not is_generic_exception:
            return None

        # Check handler body for proper error handling
        has_raise = False
        has_return = False
        has_proper_handling = False

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Raise):
                has_raise = True
                has_proper_handling = True
            elif isinstance(stmt, ast.Return):
                # Check if returning False, None, or error dict
                has_return = True
                if isinstance(stmt.value, ast.Constant | ast.NameConstant):
                    if stmt.value.value in (False, None):
                        has_proper_handling = True
                elif isinstance(stmt.value, ast.Dict):
                    # Check for error dict pattern
                    for key in stmt.value.keys:
                        if isinstance(key, ast.Constant) and key.value in (
                            "error",
                            "status",
                            "success",
                        ):
                            has_proper_handling = True
                            break

        # If no proper handling, this is a silent swallower
        if not has_proper_handling:
            # Get the source line for evidence
            evidence = self._get_source_line(file_path, node.lineno)

            return AntiPatternViolation(
                file_path=file_path,
                line_number=node.lineno,
                category=self.category,
                message=f"Silent exception swallower: catches {exception_name} without raise or proper return",
                evidence=evidence,
                severity="error" if exception_name == "(bare except)" else "warning",
                suggested_fix=self._generate_fix_suggestion(node, exception_name),
                metadata={
                    "exception_type": exception_name,
                    "has_raise": has_raise,
                    "has_return": has_return,
                },
            )

        return None

    def _generate_fix_suggestion(self, node: ast.ExceptHandler, exception_name: str) -> str:
        """Generate a fix suggestion for the violation."""
        var_name = node.name or "e"

        if exception_name == "(bare except)":
            return f"""Replace bare except with specific exception handling:
    except Exception as {var_name}:
        logger.error(f"Error: {{{var_name}}}")
        raise  # Re-raise to propagate error"""

        return f"""Add proper error handling:
    except {exception_name} as {var_name}:
        logger.error(f"Error: {{{var_name}}}")
        raise  # Or: return {{"success": False, "error": str({var_name})}}"""


__all__ = ["SilentSwallowerDetector"]
