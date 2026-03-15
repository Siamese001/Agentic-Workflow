"""
Type Erasure Anti-Pattern Detector

Detects functions returning raw `dict` or `Any` types instead of
structured Pydantic models or dataclasses.

Pattern Detection:
- `-> dict:` or `-> dict[str, Any]:` return annotations
- `-> Any:` return annotations
- Missing return type annotations on public methods
"""

import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_emit_applies_guardrail("p0", "type_erasure_validator", "p0_governance")
_emit_snapshots_state("p0", "type_erasure_validator", "state_snapshot")


class TypeErasureDetector(AntiPatternDetector):
    """
    Detects functions with type-erased return types.

    Type erasure causes downstream agents to hallucinate
    non-existent keys and leads to schema drift.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-type-erasure"

    # Allowed dict types with sufficient specificity
    ALLOWED_DICT_TYPES = {
        "dict[str, str]",
        "dict[str, int]",
        "dict[str, float]",
        "dict[str, bool]",
        "dict[str, Path]",
    }

    # Methods to ignore (common utility patterns)
    IGNORED_METHODS = {
        "__init__",
        "__str__",
        "__repr__",
        "__eq__",
        "__hash__",
        "__iter__",
        "__next__",
        "__len__",
        "__getitem__",
        "__setitem__",
        "to_dict",
        "from_dict",
        "as_dict",
    }

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
        check_agent_classes_only: bool = True,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.check_agent_classes_only = check_agent_classes_only

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "*_types.py",  # Type definition files
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.TYPE_ERASURE

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect type erasure patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TypeErasureDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TypeErasureDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            raise
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this is an agent/validator class
                if self.check_agent_classes_only and not self._is_agent_class(node):
                    continue

                # Check methods in the class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        violation = self._check_function(item, file_path, source_lines, node.name)
                        if violation:
                            violations.append(violation)

            # Also check module-level functions if not limiting to agent classes
            elif not self.check_agent_classes_only:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    # Skip if inside a class (already handled above)
                    violation = self._check_function(node, file_path, source_lines, None)
                    if violation:
                        violations.append(violation)

        return violations

    def _is_agent_class(self, node: ast.ClassDef) -> bool:
        """Check if class is an Agent or Validator.

        [REFACTORED 2026-02-08] Aligned with classification kernel:
        - Agent: class name ends with 'Agent' (not just contains)
        - Validator: class name ends with 'Validator' or inherits from Validator
        - Excludes Mixin classes
        """
        name = node.name
        # Exclude Mixins (kernel MIXIN priority)
        if "Mixin" in name:
            return False
        # Agent check (kernel AGENT priority: endswith, not contains)
        if name.endswith("Agent"):
            return True
        # Validator check
        if name.endswith("Validator"):
            return True
        # Check base classes for Agent/Validator inheritance
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name and (base_name.endswith("Agent") or base_name.endswith("Validator")):
                return True
        return False

    def _check_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
        class_name: str | None,
    ) -> AntiPatternViolation | None:
        """Check if a function has type-erased return type."""

        # Skip private methods and ignored methods
        if node.name.startswith("_") and node.name not in ("__call__",):
            if node.name not in self.IGNORED_METHODS:
                return None

        if node.name in self.IGNORED_METHODS:
            return None

        # Check for whitelist comment
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check return annotation
        if node.returns is None:
            # Missing return annotation - less severe
            return None  # Don't flag missing annotations for now

        return_type = self._get_annotation_string(node.returns)

        if return_type is None:
            return None

        # Check for type erasure patterns
        is_type_erasure = False
        severity = "warning"

        if return_type == "dict" or return_type == "Dict":
            is_type_erasure = True
        elif return_type == "Any":
            is_type_erasure = True
            severity = "error"
        elif return_type.startswith("dict[") and return_type not in self.ALLOWED_DICT_TYPES:
            # Check if it's dict[str, Any] or similar
            if "Any" in return_type:
                is_type_erasure = True

        if not is_type_erasure:
            return None

        # Generate evidence
        evidence = self._get_source_line(file_path, node.lineno)

        method_name = f"{class_name}.{node.name}" if class_name else node.name

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Type erasure: {method_name} returns {return_type} instead of structured type",
            evidence=evidence,
            severity=severity,
            suggested_fix=self._generate_fix_suggestion(node.name, return_type),
            metadata={
                "method_name": method_name,
                "return_type": return_type,
                "class_name": class_name,
            },
        )

    def _get_name(self, node: ast.expr) -> str | None:
        """Get the name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _get_annotation_string(self, node: ast.expr) -> str | None:
        """Convert an annotation AST node to string representation."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Subscript):
                base = self._get_annotation_string(node.value)
                if base:
                    # Simplified - just get the base type
                    return f"{base}[...]"
            elif isinstance(node, ast.Attribute):
                return node.attr
            return ast.unparse(node)
        except Exception:
            raise
            return None

    def _generate_fix_suggestion(self, method_name: str, return_type: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "heal" in method_name.lower():
            return """Use HealResult dataclass:
    from agentic_core.runtime.types.heal_result import HealResult, HealStatus

    def heal(self, violation: dict) -> HealResult:
        return HealResult(
            violations_found=1,
            violations_fixed=1,
            status=HealStatus.SUCCESS,
        )"""

        return f"""Replace {return_type} with a structured type:
    from dataclasses import dataclass
import uuid

    @dataclass
    class {method_name.title().replace("_", "")}Result:
        # Define specific fields
        value: str
        status: str

    def {method_name}(self, ...) -> {method_name.title().replace("_", "")}Result:
        ..."""


__all__ = ["TypeErasureDetector"]
