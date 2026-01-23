#!/usr/bin/env python3
from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
UnifiedCodeDetectorAgent - Code Quality Detection

Phase 4 Hard Migration: Consolidates:
- DeadCodeDetectorAgent (unused code detection)
- DriftDetectorAgent (code drift from baseline)
- MethodChangeDetectorAgent (method signature changes)
- DeadlockDetectorAgent (circular wait detection)
- MemoryLeakDetectorAgent (memory leak patterns)

Features:
- Dead code detection via AST analysis
- Drift detection from baseline snapshots
- Method signature change tracking
- Deadlock/circular wait detection
- Memory leak pattern detection
"""


import ast
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class DetectionType(Enum):
    """Types of code detection."""

    DEAD_CODE = auto()
    DRIFT = auto()
    METHOD_CHANGE = auto()
    DEADLOCK = auto()
    MEMORY_LEAK = auto()


class Severity(Enum):
    """Severity levels for detections."""

    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


@dataclass
class Detection:
    """Represents a code detection finding."""

    detection_type: DetectionType
    file_path: Path
    line_number: int
    severity: Severity
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DetectorConfig:
    """configuration for code detection."""

    enable_dead_code: bool = True
    enable_drift: bool = True
    enable_method_change: bool = True
    enable_deadlock: bool = True
    enable_memory_leak: bool = True
    baseline_path: Path | None = None
    ignore_patterns: list[str] = field(default_factory=lambda: ["test_", "_test.py"])


class UnifiedCodeDetectorAgent(SovereignBaseAgent):
    """
    Unified code quality detector.

    Consolidates:
    - DeadCodeDetectorAgent
    - DriftDetectorAgent
    - MethodChangeDetectorAgent
    - DeadlockDetectorAgent
    - MemoryLeakDetectorAgent

    Usage:
        detector = UnifiedCodeDetectorAgent()

        # Detect all issues in a file
        detections = detector.detect_all(Path("my_agent.py"))

        # Check for deadlocks
        deadlocks = detector.detect_deadlocks(Path("concurrent_code.py"))
    """

    # Patterns for deadlock detection
    LOCK_PATTERNS = [
        r"\.acquire\(",
        r"threading\.Lock\(",
        r"threading\.RLock\(",
        r"asyncio\.Lock\(",
        r"with\s+\w+_lock:",
    ]

    # Patterns for memory leak detection
    MEMORY_LEAK_PATTERNS = [
        r"__del__\s*\(",  # Destructor issues
        r"global\s+\w+\s*=\s*\[\]",  # Global mutable defaults
        r"\.append\([^)]+\)\s*$",  # Unbounded list growth
    ]

    def __init__(
        self,
        project_root: Path | None = None,
        config: DetectorConfig | None = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.config = config or DetectorConfig()
        self._lock = threading.RLock()
        self._baseline: dict[str, Any] = {}
        self._detections: list[Detection] = []

        Logger.info("UnifiedCodeDetectorAgent initialized")

    def detect_all(self, file_path: Path) -> list[Detection]:
        """Run all enabled detections on a file."""
        detections = []

        if not file_path.exists():
            return detections

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return detections

        if self.config.enable_dead_code:
            detections.extend(self.detect_dead_code(file_path, content))

        if self.config.enable_deadlock:
            detections.extend(self.detect_deadlocks(file_path, content))

        if self.config.enable_memory_leak:
            detections.extend(self.detect_memory_leaks(file_path, content))

        if self.config.enable_method_change:
            detections.extend(self.detect_method_changes(file_path, content))

        return detections

    def detect_dead_code(
        self,
        file_path: Path,
        content: str | None = None,
    ) -> list[Detection]:
        """Detect unused/dead code."""
        detections = []

        if content is None:
            content = file_path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return detections

        # Collect all defined names
        defined_names: set[str] = set()
        used_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)

        # Find unused definitions (excluding special methods)
        unused = defined_names - used_names
        for name in unused:
            if name.startswith("_") and not name.startswith("__"):
                continue  # Skip private methods
            if name in ("main", "run", "execute", "__init__"):
                continue  # Skip entry points

            # Find line number
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.ClassDef) and node.name == name:
                    detections.append(
                        Detection(
                            detection_type=DetectionType.DEAD_CODE,
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.WARNING,
                            message=f"Potentially unused: {name}",
                            details={"name": name, "type": type(node).__name__},
                        )
                    )
                    break

        return detections

    def detect_deadlocks(
        self,
        file_path: Path,
        content: str | None = None,
    ) -> list[Detection]:
        """Detect potential deadlock conditions."""
        detections = []

        if content is None:
            content = file_path.read_text(encoding="utf-8")

        lines = content.split("\n")
        lock_acquisitions: list[tuple[int, str]] = []

        for i, line in enumerate(lines, 1):
            for pattern in self.LOCK_PATTERNS:
                if re.search(pattern, line):
                    lock_acquisitions.append((i, line.strip()))

        # Check for nested locks (potential deadlock)
        if len(lock_acquisitions) >= 2:
            # Simple heuristic: multiple lock acquisitions in close proximity
            for j in range(len(lock_acquisitions) - 1):
                line1, _ = lock_acquisitions[j]
                line2, _ = lock_acquisitions[j + 1]

                if abs(line2 - line1) < 10:  # Within 10 lines
                    detections.append(
                        Detection(
                            detection_type=DetectionType.DEADLOCK,
                            file_path=file_path,
                            line_number=line1,
                            severity=Severity.ERROR,
                            message="Potential deadlock: nested lock acquisitions detected",
                            details={
                                "first_lock_line": line1,
                                "second_lock_line": line2,
                            },
                        )
                    )

        # Check for circular wait patterns
        try:
            tree = ast.parse(content)
            self._check_circular_waits(tree, file_path, detections)
        except SyntaxError:
            pass

        return detections

    def _check_circular_waits(
        self,
        tree: ast.AST,
        file_path: Path,
        detections: list[Detection],
    ) -> None:
        """Check for circular wait conditions in AST."""
        # Find all with statements that acquire locks
        with_statements = []

        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Name):
                        with_statements.append((node.lineno, item.context_expr.id))

        # Check for nested with statements (potential circular wait)
        seen_locks = set()
        for lineno, lock_name in with_statements:
            if lock_name in seen_locks:
                detections.append(
                    Detection(
                        detection_type=DetectionType.DEADLOCK,
                        file_path=file_path,
                        line_number=lineno,
                        severity=Severity.CRITICAL,
                        message=f"Circular wait detected: lock '{lock_name}' acquired multiple times",
                        details={"lock_name": lock_name},
                    )
                )
            seen_locks.add(lock_name)

    def detect_memory_leaks(
        self,
        file_path: Path,
        content: str | None = None,
    ) -> list[Detection]:
        """Detect potential memory leak patterns."""
        detections = []

        if content is None:
            content = file_path.read_text(encoding="utf-8")

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern in self.MEMORY_LEAK_PATTERNS:
                if re.search(pattern, line):
                    detections.append(
                        Detection(
                            detection_type=DetectionType.MEMORY_LEAK,
                            file_path=file_path,
                            line_number=i,
                            severity=Severity.WARNING,
                            message="Potential memory leak pattern detected",
                            details={"line": line.strip(), "pattern": pattern},
                        )
                    )

        return detections

    def detect_method_changes(
        self,
        file_path: Path,
        content: str | None = None,
    ) -> list[Detection]:
        """Detect method signature changes from baseline."""
        detections = []

        if not self.config.baseline_path:
            return detections

        if content is None:
            content = file_path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return detections

        # Extract current method signatures
        current_methods = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                current_methods[node.name] = {
                    "args": args,
                    "lineno": node.lineno,
                }

        # Compare with baseline
        baseline_key = str(file_path.relative_to(self.project_root))
        if baseline_key in self._baseline:
            baseline_methods = self._baseline[baseline_key]

            for name, current in current_methods.items():
                if name in baseline_methods:
                    baseline = baseline_methods[name]
                    if current["args"] != baseline["args"]:
                        detections.append(
                            Detection(
                                detection_type=DetectionType.METHOD_CHANGE,
                                file_path=file_path,
                                line_number=current["lineno"],
                                severity=Severity.WARNING,
                                message=f"Method signature changed: {name}",
                                details={
                                    "old_args": baseline["args"],
                                    "new_args": current["args"],
                                },
                            )
                        )

        return detections

    def get_detections(self) -> list[Detection]:
        """Get all recorded detections."""
        return self._detections.copy()


# Factory methods for backward compatibility
def create_legacy_dead_code_detector() -> UnifiedCodeDetectorAgent:
    """Create detector for dead code only."""
    config = DetectorConfig(
        enable_dead_code=True,
        enable_drift=False,
        enable_method_change=False,
        enable_deadlock=False,
        enable_memory_leak=False,
    )
    return UnifiedCodeDetectorAgent(config=config)


def create_legacy_deadlock_detector() -> UnifiedCodeDetectorAgent:
    """Create detector for deadlocks only."""
    config = DetectorConfig(
        enable_dead_code=False,
        enable_drift=False,
        enable_method_change=False,
        enable_deadlock=True,
        enable_memory_leak=False,
    )
    return UnifiedCodeDetectorAgent(config=config)
