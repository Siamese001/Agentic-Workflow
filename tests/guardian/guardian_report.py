"""
Guardian Report Builder
========================
Machine-readable JSON report infrastructure for Zero-Trust Guardian Shield.

This module provides:
1. Structured violation schema
2. Thread-safe report accumulation
3. JSON serialization with timestamps
4. Binary PASS/BLOCK status determination

MANIFESTO COMPLIANCE:
- Static Stasis: No agent code execution
- Binary Output: PASS or BLOCK only
- Machine-Readable: JSON schema output
- Constitutional Lock: structure_blueprint.py enforcement
- No AI Checking AI: Deterministic Python only
"""

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


class GuardianStatus(str, Enum):
    """Binary guardian status - no warnings allowed."""

    PASS = "PASS"
    BLOCK = "BLOCKING"


class ViolationCode(str, Enum):
    """Standardized violation codes for machine parsing."""

    # MRO Violations
    MRO_DIAMOND = "MRO_DIAMOND"
    MRO_ORDER = "MRO_ORDER"
    MRO_DUPLICATE_MIXIN = "MRO_DUPLICATE_MIXIN"

    # Import Violations
    IMPORT_SYNTAX_ERROR = "IMPORT_SYNTAX_ERROR"
    IMPORT_CIRCULAR = "IMPORT_CIRCULAR"
    IMPORT_GHOST = "IMPORT_GHOST"
    IMPORT_LAYER_VIOLATION = "IMPORT_LAYER_VIOLATION"

    # SSOT Violations
    SSOT_TERRITORY = "SSOT_TERRITORY"
    SSOT_BASE_AGENT_LOCATION = "SSOT_BASE_AGENT_LOCATION"
    SSOT_INDEPENDENCE = "SSOT_INDEPENDENCE"
    SSOT_TEST_PLACEMENT = "SSOT_TEST_PLACEMENT"
    SSOT_LAYER_HIERARCHY = "SSOT_LAYER_HIERARCHY"
    SSOT_VOID_COMPLIANCE = "SSOT_VOID_COMPLIANCE"
    SSOT_GHOST_FILE = "SSOT_GHOST_FILE"

    # Subatomic Violations
    SUBATOMIC_MONOLITH = "SUBATOMIC_MONOLITH"
    SUBATOMIC_MIXIN_LIMIT = "SUBATOMIC_MIXIN_LIMIT"
    SUBATOMIC_METHOD_LIMIT = "SUBATOMIC_METHOD_LIMIT"
    SUBATOMIC_NAMING = "SUBATOMIC_NAMING"
    SUBATOMIC_LAYER_ZONING = "SUBATOMIC_LAYER_ZONING"

    # Capability Violations
    CAPABILITY_VIOLATION = "CAPABILITY_VIOLATION"
    MUTATION_VIOLATION = "MUTATION_VIOLATION"

    # Forensic Violations
    FORENSIC_LLM_VALIDATION = "FORENSIC_LLM_VALIDATION"
    FORENSIC_STRUCTURAL = "FORENSIC_STRUCTURAL"
    FORENSIC_INTROSPECTION = "FORENSIC_INTROSPECTION"

    # Constitutional Violations
    CONSTITUTIONAL_BASE_AGENT = "CONSTITUTIONAL_BASE_AGENT"


class FixAction(str, Enum):
    """Recommended fix actions for the Healer."""

    REORDER_INHERITANCE = "REORDER_INHERITANCE"
    REFACTOR_INHERITANCE = "REFACTOR_INHERITANCE"
    REMOVE_DUPLICATE_MIXIN = "REMOVE_DUPLICATE_MIXIN"
    REMOVE_DUPLICATE = "REMOVE_DUPLICATE"
    FIX_SYNTAX = "FIX_SYNTAX"
    BREAK_CYCLE = "BREAK_CYCLE"
    MOVE_FILE = "MOVE_FILE"
    REMOVE_IMPORT = "REMOVE_IMPORT"
    SPLIT_FILE = "SPLIT_FILE"
    REMOVE_MIXIN = "REMOVE_MIXIN"
    REMOVE_METHOD = "REMOVE_METHOD"
    RENAME = "RENAME"
    DELETE = "DELETE"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass
class Violation:
    """Single violation record with full context."""

    code: str
    file: str
    line: int
    message: str
    fix_action: str
    severity: str = "BLOCKING"
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "fix_action": self.fix_action,
            "severity": self.severity,
            "context": self.context,
        }


@dataclass
class GuardianReport:
    """Complete guardian report with all violations."""

    status: str = GuardianStatus.PASS.value
    timestamp: str = ""
    test_suite: str = ""
    violations: list[Violation] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def add_violation(self, violation: Violation) -> None:
        """Add a violation and update status to BLOCKING."""
        self.violations.append(violation)
        self.status = GuardianStatus.BLOCK.value

        # Update summary counts
        code = violation.code
        self.summary[code] = self.summary.get(code, 0) + 1

    def is_blocking(self) -> bool:
        """Check if report has blocking violations."""
        return len(self.violations) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "timestamp": self.timestamp,
            "test_suite": self.test_suite,
            "violations": [v.to_dict() for v in self.violations],
            "summary": self.summary,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class GuardianReportBuilder:
    """
    Thread-safe report builder for accumulating violations across tests.

    Usage:
        builder = GuardianReportBuilder("test_mro_integrity")
        builder.add_violation(
            code=ViolationCode.MRO_DIAMOND,
            file="path/to/file.py",
            line=10,
            message="Diamond inheritance detected",
            fix_action=FixAction.REORDER_INHERITANCE
        )
        report = builder.build()
    """

    _instance: "GuardianReportBuilder | None" = None
    _lock = threading.Lock()

    def __init__(self, test_suite: str = "guardian"):
        self._report = GuardianReport(test_suite=test_suite)
        self._violations_lock = threading.Lock()

    @classmethod
    def get_instance(cls, test_suite: str = "guardian") -> "GuardianReportBuilder":
        """Get or create singleton instance (thread-safe)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(test_suite)
            return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for new test run."""
        with cls._lock:
            cls._instance = None

    def add_violation(
        self,
        code: ViolationCode | str,
        file: str,
        line: int,
        message: str,
        fix_action: FixAction | str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a violation to the report (thread-safe)."""
        code_str = code.value if isinstance(code, ViolationCode) else code
        action_str = fix_action.value if isinstance(fix_action, FixAction) else fix_action

        violation = Violation(
            code=code_str,
            file=str(file),
            line=line,
            message=message,
            fix_action=action_str,
            context=context or {},
        )

        with self._violations_lock:
            self._report.add_violation(violation)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata on the report."""
        self._report.metadata[key] = value

    def build(self) -> GuardianReport:
        """Build and return the final report."""
        return self._report

    def is_blocking(self) -> bool:
        """Check if any blocking violations exist."""
        return self._report.is_blocking()

    def get_violation_count(self) -> int:
        """Get total violation count."""
        return len(self._report.violations)

    def to_json(self) -> str:
        """Get JSON representation."""
        return self._report.to_json()


def write_guardian_report(
    report: GuardianReport,
    output_path: Path | str | None = None,
) -> Path:
    """
    Write guardian report to JSON file.

    Default location: logs/guardian_report.json
    """
    if output_path is None:
        project_root = Path(__file__).resolve().parents[2]
        output_path = project_root / "logs" / "guardian_report.json"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report.to_json())

    return output_path


def load_guardian_report(path: Path | str) -> GuardianReport:
    """Load a guardian report from JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    violations = [Violation(**v) for v in data.get("violations", [])]

    return GuardianReport(
        status=data.get("status", GuardianStatus.PASS.value),
        timestamp=data.get("timestamp", ""),
        test_suite=data.get("test_suite", ""),
        violations=violations,
        summary=data.get("summary", {}),
        metadata=data.get("metadata", {}),
    )


# Convenience functions for quick violation creation
def violation(
    code: ViolationCode,
    file: str,
    line: int,
    message: str,
    fix_action: FixAction,
    **context: Any,
) -> Violation:
    """Create a violation with minimal boilerplate."""
    return Violation(
        code=code.value,
        file=str(file),
        line=line,
        message=message,
        fix_action=fix_action.value,
        context=context,
    )
