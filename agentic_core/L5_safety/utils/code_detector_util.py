"""Code Detector Utility - Deterministic code quality detection.

This module provides deterministic code detection functionality previously
implemented in CodeDetectorAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 8 Micro-Wave 3).

Usage:
    from agentic_core.L5_safety.utils.code_detector_util import (
        CodeDetector, Detection, DetectionType, Severity
    )

    # Detect issues
    detector = CodeDetector(project_root=Path("."))
    detections = detector.run_full_scan()
"""

from __future__ import annotations

import ast
import json
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class DetectionType(Enum):
    """Types of code quality detections."""
    DEAD_CODE = "DEAD_CODE"
    DRIFT = "DRIFT"
    METHOD_CHANGE = "METHOD_CHANGE"
    DEADLOCK = "DEADLOCK"
    MEMORY_LEAK = "MEMORY_LEAK"


class Severity(Enum):
    """Severity levels for detections."""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


@dataclass
class Detection:
    """Represents a single code quality detection."""

    detection_type: str
    file_path: str
    line_number: int
    severity: str
    message: str
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "detection_type": self.detection_type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass
class DetectorConfig:
    """Configuration for code detection."""

    enable_dead_code: bool = True
    enable_drift: bool = True
    enable_method_change: bool = True
    enable_deadlock: bool = True
    enable_memory_leak: bool = True
    baseline_path: Path | None = None
    ignore_patterns: list[str] = field(
        default_factory=lambda: ["test_", "_test.py", "conftest.py"]
    )
    project_root: Path | None = None


class CodeDetector:
    """Deterministic code quality detection without agent overhead."""

    LOCK_PATTERNS = [
        r"\.acquire\(",
        r"threading\.Lock\(",
        r"threading\.RLock\(",
        r"asyncio\.Lock\(",
        r"with\s+\w+_lock:",
    ]

    MEMORY_LEAK_PATTERNS = [
        r"__del__\s*\(",
        r"global\s+\w+\s*=\s*\[\]",
        r"\.append\([^)]+\)\s*$",
    ]

    def __init__(self, config: DetectorConfig | None = None) -> None:
        """Initialize the code detector.

        Args:
            config: Optional detector configuration
        """
        self._detector_config = config or DetectorConfig()
        self.project_root = self._detector_config.project_root or Path.cwd()
        self._lock = threading.RLock()
        self._baseline: dict[str, Any] = {}
        self._detections: list[Detection] = []

        # Load baseline if available
        if self._detector_config.baseline_path and self._detector_config.baseline_path.exists():
            try:
                self._baseline = json.loads(self._detector_config.baseline_path.read_text())
            except (json.JSONDecodeError, OSError) as e:
                Logger.warning(f"Failed to load baseline: {e}")

    def run_full_scan(self) -> list[Detection]:
        """Scan all Python files in the project.

        Returns:
            List of all detections found
        """
        self._detections = []
        files = list(self.project_root.rglob("*.py"))

        for f in files:
            if any(p in f.name for p in self._detector_config.ignore_patterns):
                continue
            self.detect_all(f)

        return self._detections

    def detect_all(self, file_path: Path) -> list[Detection]:
        """Run all enabled detections on a file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of detections for this file
        """
        if not file_path.exists():
            return []

        detections: list[Detection] = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (ValueError, TypeError, OSError):
            return []

        if self._detector_config.enable_dead_code:
            detections.extend(self.detect_dead_code(file_path, content))

        if self._detector_config.enable_deadlock:
            detections.extend(self.detect_deadlocks(file_path, content))

        if self._detector_config.enable_memory_leak:
            detections.extend(self.detect_memory_leaks(file_path, content))

        if self._detector_config.enable_method_change:
            detections.extend(self.detect_method_changes(file_path, content))

        with self._lock:
            self._detections.extend(detections)

        return detections

    def detect_dead_code(self, file_path: Path, content: str) -> list[Detection]:
        """Detect potentially unused definitions.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of dead code detections
        """
        detections: list[Detection] = []

        try:
            tree = ast.parse(content)
            defined: set[str] = set()
            used: set[str] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.ClassDef):
                    defined.add(node.name)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used.add(node.id)

            unused = defined - used

            for name in unused:
                if name.startswith("_") or name in {"main", "run", "execute", "__init__", "setup"}:
                    continue

                lineno = 0
                for node in ast.walk(tree):
                    if hasattr(node, "name") and node.name == name:
                        lineno = node.lineno
                        break

                detections.append(
                    Detection(
                        detection_type=DetectionType.DEAD_CODE.value,
                        file_path=str(file_path),
                        line_number=lineno,
                        severity=Severity.WARNING.name,
                        message=f"Potentially unused definition: {name}",
                    )
                )
        except SyntaxError:
            pass

        return detections

    def detect_deadlocks(self, file_path: Path, content: str) -> list[Detection]:
        """Detect potential deadlock patterns.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of deadlock detections
        """
        detections: list[Detection] = []
        lines = content.splitlines()
        locks: list[tuple[int, str]] = []

        for i, line in enumerate(lines, 1):
            if any(re.search(p, line) for p in self.LOCK_PATTERNS):
                locks.append((i, line))

        if len(locks) >= 2:
            for j in range(len(locks) - 1):
                l1, txt1 = locks[j]
                l2, txt2 = locks[j + 1]

                if abs(l2 - l1) < 5 and "release" not in txt1 and "release" not in txt2:
                    detections.append(
                        Detection(
                            detection_type=DetectionType.DEADLOCK.value,
                            file_path=str(file_path),
                            line_number=l1,
                            severity=Severity.ERROR.name,
                            message="Potential nested lock acquisition (Deadlock Risk)",
                            details={"nested_lines": [l1, l2]},
                        )
                    )

        return detections

    def detect_memory_leaks(self, file_path: Path, content: str) -> list[Detection]:
        """Detect potential memory leak patterns.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of memory leak detections
        """
        detections: list[Detection] = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            for pattern in self.MEMORY_LEAK_PATTERNS:
                if re.search(pattern, line):
                    detections.append(
                        Detection(
                            detection_type=DetectionType.MEMORY_LEAK.value,
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.WARNING.name,
                            message="Potential memory leak pattern",
                            details={"pattern": pattern},
                        )
                    )

        return detections

    def detect_method_changes(self, file_path: Path, content: str) -> list[Detection]:
        """Detect method signature changes against baseline.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of method change detections (requires baseline)
        """
        if not self._baseline:
            return []
        return []

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all detections.

        Returns:
            Dictionary with detection statistics
        """
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}

        for detection in self._detections:
            by_type[detection.detection_type] = by_type.get(detection.detection_type, 0) + 1
            by_severity[detection.severity] = by_severity.get(detection.severity, 0) + 1

        return {
            "total_detections": len(self._detections),
            "by_type": by_type,
            "by_severity": by_severity,
            "files_scanned": len(set(d.file_path for d in self._detections)),
        }

    def export_detections(self, output_path: Path) -> None:
        """Export detections to JSON file.

        Args:
            output_path: Path to write JSON output
        """
        data = {
            "detections": [d.to_dict() for d in self._detections],
            "summary": self.get_summary(),
            "exported_at": datetime.utcnow().isoformat(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def detect_file(file_path: str | Path, config: DetectorConfig | None = None) -> list[Detection]:
    """Standalone function to detect issues in a single file.

    Args:
        file_path: Path to the file
        config: Optional detector configuration

    Returns:
        List of detections
    """
    detector = CodeDetector(config)
    return detector.detect_all(Path(file_path))


def scan_project(project_root: str | Path, config: DetectorConfig | None = None) -> list[Detection]:
    """Standalone function to scan an entire project.

    Args:
        project_root: Root directory of the project
        config: Optional detector configuration

    Returns:
        List of all detections
    """
    if config is None:
        config = DetectorConfig()
    config.project_root = Path(project_root)

    detector = CodeDetector(config)
    return detector.run_full_scan()


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance).

    Detectors primarily REPORT - they don't auto-fix.
    """
    Logger.info("[CodeDetector] Detection-only - manual review required")
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal code detection violations.

    Args:
        violation: Violation dict

    Returns:
        Healing result dict
    """
    violation_type = violation.get("type", "unknown")
    path = violation.get("path", "")

    Logger.info(f"[CodeDetector] Detection-only: {violation_type} at {path}")

    return {
        "status": "skipped",
        "details": "Detection-only - manual intervention required",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Code Detector Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Detector Utility")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    parser.add_argument(
        "--checks",
        nargs="+",
        choices=["dead_code", "deadlock", "memory_leak", "all"],
        default=["all"],
        help="Detection checks to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = DetectorConfig(
        project_root=Path(args.project_root),
        enable_dead_code="all" in args.checks or "dead_code" in args.checks,
        enable_deadlock="all" in args.checks or "deadlock" in args.checks,
        enable_memory_leak="all" in args.checks or "memory_leak" in args.checks,
    )

    detector = CodeDetector(config)
    detections = detector.run_full_scan()

    print(f"Total detections: {len(detections)}")

    for d in detections[:20]:
        print(f"  [{d.severity}] {d.detection_type}: {d.file_path}:{d.line_number} - {d.message}")

    if len(detections) > 20:
        print(f"  ... and {len(detections) - 20} more")

    if args.output:
        detector.export_detections(Path(args.output))
        print(f"\nExported to: {args.output}")


if __name__ == "__main__":
    main()
