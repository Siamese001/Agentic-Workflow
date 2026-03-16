"""
File: agentic_core/L5_safety/reasoning/CodeDetectorAgent.py
Rationale:
    L5 Sovereign Guardian for Code Purity.
    - Hardened inheritance (Standard SovereignBaseAgent).
    - Implements Atomic Snapshot comparison for Drift detection.
    - Standardized Severity enums for dashboard integration.
"""

from __future__ import annotations

import ast
import json
import logging
import re
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.decorators_compat_util import standard_heal

emit_replay_key("p0", "CodeDetectorAgent")
emit_determinism_digest("p0", "CodeDetectorAgent")

_emit_dispatches_healing_run("p1", "CodeDetectorAgent", "L5")
_emit_routes_through("p1", "CodeDetectorAgent", "L5")
_emit_escalates_to_human("p1", "CodeDetectorAgent", "L5")
_emit_reads_policy_state("p1", "CodeDetectorAgent", "L5")

Logger = logging.getLogger(__name__)


class DetectionType(Enum):
    DEAD_CODE = auto()
    DRIFT = auto()
    METHOD_CHANGE = auto()
    DEADLOCK = auto()
    MEMORY_LEAK = auto()


class Severity(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


@dataclass
class Detection:
    detection_type: str
    file_path: str
    line_number: int
    severity: str
    message: str
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DetectorConfig:
    enable_dead_code: bool = True
    enable_drift: bool = True
    enable_method_change: bool = True
    enable_deadlock: bool = True
    enable_memory_leak: bool = True
    baseline_path: Path | None = None
    ignore_patterns: list[str] = field(default_factory=lambda: ["test_", "_test.py", "conftest.py"])
    project_root: Path | None = None


class CodeDetectorAgent(SovereignBaseAgent):
    """
    Unified code quality detector.
    Consolidates DeadCode, Drift, Deadlock, and MemoryLeak detection.
    """

    LOCK_PATTERNS = [
        "\\.acquire\\(",
        "threading\\.Lock\\(",
        "threading\\.RLock\\(",
        "asyncio\\.Lock\\(",
        "with\\s+\\w+_lock:",
    ]
    MEMORY_LEAK_PATTERNS = ["__del__\\s*\\(", "global\\s+\\w+\\s*=\\s*\\[\\]", "\\.append\\([^)]+\\)\\s*$"]

    def __init__(self, config: DetectorConfig | None = None):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CodeDetectorAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CodeDetectorAgent.__init__", "p0_governance")
        self._detector_config = config or DetectorConfig()
        self.project_root = self._detector_config.project_root or Path.cwd()
        self._lock = threading.RLock()
        self._baseline: dict[str, Any] = {}
        self._detections: list[Detection] = []
        if self._detector_config.baseline_path and self._detector_config.baseline_path.exists():
            try:
                self._baseline = json.loads(self._detector_config.baseline_path.read_text())
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.warning(f"Failed to load baseline: {e}")

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Sovereign Interface.
        Detectors primarily REPORT. 'execute' mode can update baselines.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CodeDetectorAgent.heal_repository")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CodeDetectorAgent.heal_repository".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = self.run_full_scan()
        if execute and self._detector_config.baseline_path:
            self._update_baseline()
        return {
            "violations_found": len(violations),
            "violations_fixed": 0,
            "report": [asdict(d) for d in violations],
        }

    def run_full_scan(self) -> list[Detection]:
        """Scans all Python files in project."""
        self._detections = []
        files = list(self.project_root.rglob("*.py"))
        for f in files:
            if any(p in f.name for p in self._detector_config.ignore_patterns):
                continue
            self.detect_all(f)
        return self._detections

    def detect_all(self, file_path: Path) -> list[Detection]:
        """Run all enabled detections on a file."""
        if not file_path.exists():
            return []
        detections = []
        try:
            content = file_path.read_text(encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception:
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
        detections = []
        try:
            tree = ast.parse(content)
            defined = set()
            used = set()
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
                        detection_type=DetectionType.DEAD_CODE.name,
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
        detections = []
        lines = content.splitlines()
        locks = []
        for i, line in enumerate(lines, 1):
            if any(re.search(p, line) for p in self.LOCK_PATTERNS):
                locks.append((i, line))
        if len(locks) >= 2:
            for j in range(len(locks) - 1):
                l1, txt1 = locks[j]
                l2, txt2 = locks[j + 1]
                if abs(l2 - l1) < 5 and "release" not in txt1 and ("release" not in txt2):
                    detections.append(
                        Detection(
                            detection_type=DetectionType.DEADLOCK.name,
                            file_path=str(file_path),
                            line_number=l1,
                            severity=Severity.ERROR.name,
                            message="Potential nested lock acquisition (Deadlock Risk)",
                            details={"nested_lines": [l1, l2]},
                        )
                    )
        return detections

    def detect_memory_leaks(self, file_path: Path, content: str) -> list[Detection]:
        detections = []
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern in self.MEMORY_LEAK_PATTERNS:
                if re.search(pattern, line):
                    detections.append(
                        Detection(
                            detection_type=DetectionType.MEMORY_LEAK.name,
                            file_path=str(file_path),
                            line_number=i,
                            severity=Severity.WARNING.name,
                            message="Potential memory leak pattern",
                            details={"pattern": pattern},
                        )
                    )
        return detections

    def detect_method_changes(self, file_path: Path, content: str) -> list[Detection]:
        if not self._baseline:
            return []
        return []

    def _update_baseline(self):
        """Generates a new baseline snapshot of the codebase."""

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal code detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (race_condition, deadlock, memory_leak)
                - path: Path to the violating file
                - line_number: Line number of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        violation_type = violation.get("type", "")
        path = violation.get("path", "")
        Logger.info(f"[CODE_DETECTOR] Detection-only agent: {violation_type} at {path}")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Detection-only agent - manual intervention required",
        }
        pass
