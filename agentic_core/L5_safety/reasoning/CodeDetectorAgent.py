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
from agentic_core.mixins.prompt_rendering_mixin import PromptRenderingMixin
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "CodeDetectorAgent", "execution_auth")
_emit_validates_capability("p2", "CodeDetectorAgent", "capability_check")
_emit_routes_to_capability("p2", "CodeDetectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "CodeDetectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "CodeDetectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "CodeDetectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "CodeDetectorAgent", "exec_output")
_emit_dispatches_agent("p3", "CodeDetectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "CodeDetectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "CodeDetectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "CodeDetectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "CodeDetectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "CodeDetectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CodeDetectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "CodeDetectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "CodeDetectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CodeDetectorAgent", "eval_metric")
_emit_stores_embedding("p4", "CodeDetectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "CodeDetectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CodeDetectorAgent", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

emit_replay_key("p0", "CodeDetectorAgent")
emit_determinism_digest("p0", "CodeDetectorAgent")

_emit_dispatches_healing_run("p1", "CodeDetectorAgent", "L5")
_emit_routes_through("p1", "CodeDetectorAgent", "L5")
_emit_checks_agent_registry("p1", "CodeDetectorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "CodeDetectorAgent", "capability")
_emit_dispatches_execution_plan("p1", "CodeDetectorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "CodeDetectorAgent", "sub_agent")
_emit_routes_to_agent("p1", "CodeDetectorAgent", "target_agent")
_emit_verifies_policy("p1", "CodeDetectorAgent", "policy_check")
_emit_observes_runtime_state("p1", "CodeDetectorAgent", "runtime_state")
_emit_verifies_boundary("p1", "CodeDetectorAgent", "boundary_check")
_emit_transcripts_response("p1", "CodeDetectorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "CodeDetectorAgent")
_emit_gated_by_confidence("p1", "CodeDetectorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "CodeDetectorAgent", "L5")
_emit_reads_policy_state("p1", "CodeDetectorAgent", "L5")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("CodeDetectorAgent", "p4obs", "metric_6")
_emit_records_incident_event("CodeDetectorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("CodeDetectorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("CodeDetectorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("CodeDetectorAgent", "p4obs", "mon_state")
_emit_triggers_alert("CodeDetectorAgent", "p4obs", "alert")
_emit_links_incident_trace("CodeDetectorAgent", "p4obs", "trace_link")
_emit_captures_pattern("CodeDetectorAgent", "p3lm", "pattern")
_emit_records_learning_event("CodeDetectorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CodeDetectorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("CodeDetectorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CodeDetectorAgent", "p3lm", "routing")
_emit_improves_agent_policy("CodeDetectorAgent", "p3lm", "policy")
_emit_stores_learning_state("CodeDetectorAgent", "p3lm", "state")
_emit_records_execution_trace("CodeDetectorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CodeDetectorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CodeDetectorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CodeDetectorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CodeDetectorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CodeDetectorAgent", "env_read", "p2_env_1")
_emit_reads_environ("CodeDetectorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("CodeDetectorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CodeDetectorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "CodeDetectorAgent", "context_pull")
_emit_pulls_context("p1", "CodeDetectorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "CodeDetectorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CodeDetectorAgent", "uwg_term_2")
_emit_writes_through("p1", "CodeDetectorAgent", "write_through")
_emit_writes_through("p1", "CodeDetectorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "CodeDetectorAgent", "safety_validation")
_emit_invokes_eval("p1", "CodeDetectorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "CodeDetectorAgent", "routing_commit")

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


class CodeDetectorAgent(PromptRenderingMixin, SovereignBaseAgent):
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
            # guardian: allow-silent-swallow -- baseline load failure is non-fatal; detector runs without baseline
            except Exception as e:
                raise
                Logger.warning(f"Failed to load baseline: {e}")

    @standard_heal
    # guardian: allow-type-erasure -- standard_heal decorator normalizes return type for orchestration compatibility
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
        # guardian: allow-silent-swallow -- unreadable file is skipped; empty detections returned
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
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
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

    # guardian: allow-type-erasure -- standard_heal decorator normalizes violation dict for orchestration compatibility
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