"""
Utility Silent Swallower Validator

Enhanced silent swallower detection for utility/ops scripts with context-aware
classification and governance path enforcement.

Implements Windsurf Hardening Response requirements:
- Zero tolerance for governance/CI script silent failures
- Retry-with-reraise pattern detection
- Utility script classification by operational category
- Failure signal emission requirements
"""

import ast
import logging
import re
from pathlib import Path

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace

logger = logging.getLogger(__name__)


class UtilityScriptClassifier:
    """Classifies utility scripts by operational category."""

    # Paths that are governance-critical (zero tolerance for silent failures)
    GOVERNANCE_PATHS = {
        "ops_scripts/ci",
        "ops_scripts/maintenance",
        "ops_scripts/root_scripts",
        "tests/guardian",
        "tests/governance",
        "tests/integration",
        "tests/performance",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/static_checks",
    }

    # Diagnostic paths (must emit failure signals)
    DIAGNOSTIC_PATHS = {
        "tools/evidence",
        "tools/semantic_gap_analyzer.py",
        "tools/dep_graph_db.py",
        "ops_scripts/general",
    }

    # Local dev paths (allowed with annotation)
    LOCAL_DEV_PATHS = {
        "ops_scripts/dev_tools",
        "scripts",
        "_debug",
        "_test",
        "_temp",
    }

    @classmethod
    def classify_script(cls, file_path: Path) -> str:
        """Classify a script by its operational category."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "UtilityScriptClassifier.classify_script")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:UtilityScriptClassifier.classify_script".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Normalize to forward slashes for cross-platform comparison
        path_str = file_path.as_posix()

        # Check for governance-critical paths
        if any(gov_path in path_str for gov_path in cls.GOVERNANCE_PATHS):
            return "GOVERNANCE_CRITICAL"

        # Check for diagnostic paths
        if any(diag_path in path_str for diag_path in cls.DIAGNOSTIC_PATHS):
            return "DIAGNOSTIC_ONLY"

        # Check for local dev paths
        if any(dev_path in path_str for dev_path in cls.LOCAL_DEV_PATHS):
            return "LOCAL_DEV_ONLY"

        # Default to governance-critical for safety
        return "GOVERNANCE_CRITICAL"


class RetryPatternDetector:
    """Detects retry-with-reraise patterns that are compliant."""

    def __init__(self):
        self.retry_patterns = [
            # Pattern: for attempt in range(max_attempts): try: ... except: if attempt == max_attempts-1: raise
            r"for\s+\w+\s+in\s+range\([^)]+\):\s*try:.*?except\s+[^:]+:\s*if\s+\w+\s*==\s*[^-]+\s*-\s*1:\s*raise",
            # Pattern: if attempt < max_attempts: ... else: raise
            r"if\s+\w+\s*<\s*[^:]+:.*?else:\s*raise",
            # Pattern: if attempt == max_attempts: raise
            r"if\s+\w+\s*==\s*[^:]+:\s*raise",
        ]

    def is_compliant_retry(self, node: ast.Try, source_lines: list[str]) -> bool:
        """Check if this try-except is part of a compliant retry pattern."""
        try:
            # Get the source line range for this try node
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                start_line = max(0, node.lineno - 5)  # Look at context
                end_line = min(len(source_lines), node.end_lineno + 5)
                context = "\n".join(source_lines[start_line:end_line])

                # Check for retry patterns
                for pattern in self.retry_patterns:
                    if re.search(pattern, context, re.DOTALL | re.MULTILINE):
                        return True

            return False
        except Exception:
            raise
            return False


class UtilitySilentSwallowerDetector(AntiPatternDetector):
    """Enhanced silent swallower detector for utility scripts."""

    def __init__(self, project_root: Path = None):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.classifier = UtilityScriptClassifier()
        self.retry_detector = RetryPatternDetector()
        self.guardian_annotations: set[str] = set()

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.SILENT_SWALLOWER

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect utility silent swallower violations in the given AST."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "UtilitySilentSwallowerDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:UtilitySilentSwallowerDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        try:
            # Read source lines for context
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                source_lines = f.readlines()

            # Classify script
            script_category = self.classifier.classify_script(file_path)

            # Scan for silent swallowers
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    violation = self._check_try_except(node, file_path, source_lines, script_category)
                    if violation:
                        violations.append(violation)

        except Exception as e:
            raise
            logger.warning(f"Error scanning {file_path}: {e}")

        return violations

    def _check_try_except(
        self, node: ast.Try, file_path: Path, source_lines: list[str], script_category: str
    ) -> AntiPatternViolation | None:
        """Check a try-except node for silent swallower violations."""

        for handler in node.handlers:
            # Check if this catches Exception broadly
            if self._is_broad_exception(handler):
                # Check for guardian annotation
                if self._has_guardian_annotation(handler, source_lines):
                    continue

                # Check if this is a compliant retry pattern
                if self.retry_detector.is_compliant_retry(node, source_lines):
                    continue

                # Check if this re-raises the exception
                if self._has_reraise(handler):
                    continue

                # Determine violation based on script category
                if script_category == "GOVERNANCE_CRITICAL":
                    return self._create_violation(
                        file_path,
                        handler,
                        "GOVERNANCE_CRITICAL silent failure - zero tolerance",
                        EnforcementLevel.HARD_BLOCK,
                    )
                elif script_category == "DIAGNOSTIC_ONLY":
                    if not self._has_failure_signal(handler):
                        return self._create_violation(
                            file_path,
                            handler,
                            "DIAGNOSTIC script without failure signal",
                            EnforcementLevel.WARNING,
                        )
                elif script_category == "LOCAL_DEV_ONLY":
                    return self._create_violation(
                        file_path,
                        handler,
                        "LOCAL_DEV script requires guardian annotation",
                        EnforcementLevel.SOFT_BLOCK,
                    )

        return None

    def _is_broad_exception(self, handler: ast.ExceptHandler) -> bool:
        """Check if handler catches Exception broadly."""
        if handler.type is None:
            return True  # bare except

        if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
            return True

        return False

    def _has_guardian_annotation(self, handler: ast.ExceptHandler, source_lines: list[str]) -> bool:
        """Check if handler has guardian annotation (hyphens or underscores accepted)."""
        try:
            # Check the line of the except handler
            line_idx = handler.lineno - 1
            if 0 <= line_idx < len(source_lines):
                line = source_lines[line_idx]
                if (
                    "guardian: allow-silent-swallower" in line
                    or "guardian: allow-silent_swallower" in line
                    or "guardian: allow_silent_swallower" in line
                ):
                    return True
            
            # Check the line before the except handler
            line_idx = handler.lineno - 2
            if 0 <= line_idx < len(source_lines):
                line = source_lines[line_idx]
                if (
                    "guardian: allow-silent-swallower" in line
                    or "guardian: allow-silent_swallower" in line
                    or "guardian: allow_silent_swallower" in line
                ):
                    return True
        except (IndexError, TypeError):
            pass
        return False

    def _has_reraise(self, handler: ast.ExceptHandler) -> bool:
        """Check if handler re-raises the exception."""
        for node in ast.walk(handler):
            if isinstance(node, ast.Raise):
                # Check if it's a bare raise or raise from
                if node.exc is None or isinstance(node.exc, ast.Name):
                    return True
        return False

    def _has_failure_signal(self, handler: ast.ExceptHandler) -> bool:
        """Check if handler emits a failure signal."""
        for node in ast.walk(handler):
            if isinstance(node, ast.Call):
                # Check for logging calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["error", "exception", "critical", "warning"]:
                        return True

                # Check for sys.exit
                if isinstance(node.func, ast.Attribute):
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "sys"
                        and node.func.attr == "exit"
                    ):
                        return True

        return False

    def _create_violation(
        self, file_path: Path, handler: ast.ExceptHandler, message: str, enforcement_level: EnforcementLevel
    ) -> AntiPatternViolation:
        """Create an anti-pattern violation."""
        severity = "error" if enforcement_level == EnforcementLevel.HARD_BLOCK else "warning"
        return AntiPatternViolation(
            file_path=file_path,
            line_number=handler.lineno,
            category=self.category,
            message=message,
            evidence=f"Silent exception handler at line {handler.lineno}",
            severity=severity,
            suggested_fix="Add proper error handling with re-raise or failure signal",
        )
