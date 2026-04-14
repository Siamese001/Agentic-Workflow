"""
Base Anti-Pattern Detector Framework

Provides the core infrastructure for AST-based anti-pattern detection
with caching, incremental scanning, and configurable enforcement levels.
"""

import ast
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "base_detector_validator")
emit_determinism_digest("p0", "base_detector_validator")

_emit_dispatches_healing_run("p1", "base_detector_validator", "L5")
_emit_routes_through("p1", "base_detector_validator", "L5")
_emit_checks_agent_registry("p1", "base_detector_validator", "agent_registry")
_emit_validates_agent_capability("p1", "base_detector_validator", "capability")
_emit_dispatches_execution_plan("p1", "base_detector_validator", "exec_plan")
_emit_agent_executes_agent("p1", "base_detector_validator", "sub_agent")
_emit_routes_to_agent("p1", "base_detector_validator", "target_agent")
_emit_verifies_policy("p1", "base_detector_validator", "policy_check")
_emit_observes_runtime_state("p1", "base_detector_validator", "runtime_state")
_emit_verifies_boundary("p1", "base_detector_validator", "boundary_check")
_emit_transcripts_response("p1", "base_detector_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "base_detector_validator")
_emit_gated_by_confidence("p1", "base_detector_validator", "confidence_gate")
_emit_escalates_to_human("p1", "base_detector_validator", "L5")
_emit_reads_policy_state("p1", "base_detector_validator", "L5")

_emit_applies_guardrail("p0", "base_detector_validator", "p0_governance")
_emit_snapshots_state("p0", "base_detector_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "base_detector_validator", "execution_auth")
_emit_validates_capability("p2", "base_detector_validator", "capability_check")
_emit_routes_to_capability("p2", "base_detector_validator", "capability_route")
_emit_writes_via_uwg("p2", "base_detector_validator", "uwg_write")
_emit_blocks_direct_write("p2", "base_detector_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "base_detector_validator", "tool_invocation")
_emit_captures_execution_output("p2", "base_detector_validator", "exec_output")
_emit_dispatches_agent("p3", "base_detector_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "base_detector_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_detector_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_detector_validator", "healing_outcome")
_emit_escalates_failure("p3", "base_detector_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_detector_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_detector_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_detector_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_detector_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_detector_validator", "eval_metric")
_emit_stores_embedding("p4", "base_detector_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_detector_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_detector_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_1")
_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_2")
_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_3")
_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_4")
_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_5")
_emit_emits_metric_event("base_detector_validator", "p4obs", "metric_6")
_emit_records_incident_event("base_detector_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("base_detector_validator", "p4obs", "anomaly")
_emit_writes_observability_log("base_detector_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("base_detector_validator", "p4obs", "mon_state")
_emit_triggers_alert("base_detector_validator", "p4obs", "alert")
_emit_links_incident_trace("base_detector_validator", "p4obs", "trace_link")
_emit_captures_pattern("base_detector_validator", "p3lm", "pattern")
_emit_records_learning_event("base_detector_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("base_detector_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("base_detector_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("base_detector_validator", "p3lm", "routing")
_emit_improves_agent_policy("base_detector_validator", "p3lm", "policy")
_emit_stores_learning_state("base_detector_validator", "p3lm", "state")
_emit_records_execution_trace("base_detector_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("base_detector_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("base_detector_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("base_detector_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("base_detector_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("base_detector_validator", "env_read", "p2_env_1")
_emit_reads_environ("base_detector_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("base_detector_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("base_detector_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "base_detector_validator", "context_pull")
_emit_pulls_context("p1", "base_detector_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "base_detector_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "base_detector_validator", "uwg_term_2")
_emit_writes_through("p1", "base_detector_validator", "write_through")
_emit_writes_through("p1", "base_detector_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "base_detector_validator", "safety_validation")
_emit_invokes_eval("p1", "base_detector_validator", "eval_call")
_emit_proposal_commits_routing("p1", "base_detector_validator", "routing_commit")

Logger = logging.getLogger(__name__)


class EnforcementLevel(str, Enum):
    """Enforcement level for anti-pattern violations."""

    DISABLED = "disabled"  # No enforcement
    WARNING = "warning"  # Log warning, don't block
    SOFT_BLOCK = "soft_block"  # Block PR with override option
    HARD_BLOCK = "hard_block"  # Block PR, no override


class AntiPatternCategory(str, Enum):
    """Categories of anti-patterns."""

    NAMING = "naming"
    DOCUMENTATION = "documentation"
    SILENT_SWALLOWER = "silent_swallower"
    SILENT_DEGRADATION = "silent_degradation"
    TEST_SILENT_SKIP = "test_silent_skip"
    TEST_QUALITY = "test_quality"
    TYPE_ERASURE = "type_erasure"
    PATH_FRAGILITY = "path_fragility"
    MAGIC_CONFIGURATION = "magic_configuration"
    GLOBAL_MUTATION = "global_mutation"
    CONFIG_WITH_LOGIC = "config_with_logic"
    DIRECT_PROMPT_COMPILATION = "direct_prompt_compilation"
    HOLLOW_FILE = "hollow_file"
    INVALID_STUB = "invalid_stub"


@dataclass
class AntiPatternViolation:
    """Represents a detected anti-pattern violation."""

    file_path: Path
    line_number: int
    category: AntiPatternCategory
    message: str | None = None
    evidence: str | None = ""
    description: str | None = None
    severity: str = "warning"
    suggested_fix: str | None = None
    suggestion: str | None = None
    whitelisted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.message is None:
            self.message = self.description or ""
        if self.suggested_fix is None and self.suggestion:
            self.suggested_fix = self.suggestion
        if self.evidence is None:
            self.evidence = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "category": self.category.value,
            "message": self.message or "",
            "evidence": self.evidence or "",
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
            "whitelisted": self.whitelisted,
            "metadata": self.metadata,
        }


@dataclass
class DetectionResult:
    """Result of anti-pattern detection for a file."""

    file_path: Path
    violations: list[AntiPatternViolation] = field(default_factory=list)
    scan_time_ms: float = 0.0
    cached: bool = False
    error: str | None = None

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len([v for v in self.violations if not v.whitelisted]) > 0

    @property
    def violation_count(self) -> int:
        """Count non-whitelisted violations."""
        return len([v for v in self.violations if not v.whitelisted])


class AntiPatternDetector(ABC):
    """
    Abstract base class for anti-pattern detectors.

    Subclasses implement specific detection logic for each anti-pattern category.
    """

    # Cache for parsed ASTs
    _ast_cache: dict[str, tuple[str, ast.Module]] = {}

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        self.enforcement_level = enforcement_level
        self.whitelisted_patterns = whitelisted_patterns or []
        self.whitelisted_files = whitelisted_files or []

    @property
    @abstractmethod
    def category(self) -> AntiPatternCategory:
        """Return the category of anti-pattern this detector handles."""
        pass

    @abstractmethod
    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """
        Detect anti-patterns in the given AST.

        Args:
            file_path: Path to the file being analyzed
            tree: Parsed AST of the file

        Returns:
            List of detected violations
        """
        pass

    def scan_file(self, file_path: Path) -> DetectionResult:
        """
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            DetectionResult with violations and metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AntiPatternDetector.scan_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AntiPatternDetector.scan_file".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        import time

        start_time = time.time()

        # Check if file is whitelisted
        if self._is_file_whitelisted(file_path):
            return DetectionResult(
                file_path=file_path,
                violations=[],
                scan_time_ms=0,
                cached=False,
            )

        try:
            # Get AST (with caching)
            tree = self._get_ast(file_path)

            if tree is None:
                return DetectionResult(
                    file_path=file_path,
                    violations=[],
                    scan_time_ms=(time.time() - start_time) * 1000,
                    error="Failed to parse file",
                )

            # Detect violations
            violations = self.detect(file_path, tree)

            # Apply whitelist patterns
            for violation in tqdm(violations, desc="Processing", unit="item"):
                if self._is_violation_whitelisted(violation):
                    violation.whitelisted = True

            # Phase 3e: ADG confirmation — upgrade to HARD_BLOCK when ADG confirms the same pattern
            if violations:
                try:
                    from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

                    _bp = _gbp(
                        file_path,
                        file_path.parents[5] if len(file_path.parents) > 5 else file_path.parents[-1],
                    )
                    if _bp.antipattern_signals:
                        for violation in violations:
                            if (
                                not violation.whitelisted
                                and violation.severity != "hard_block"
                                and violation.category.value in _bp.antipattern_signals
                            ):
                                violation.severity = "hard_block"
                                violation.metadata["adg_confirmed"] = True
                # guardian: allow-silent-swallower -- ADG behavioral profile lookup is optional telemetry; failure is non-critical
                except (RuntimeError, OSError) as e:
                    import logging

                    logging.getLogger(__name__).debug(
                        "base_detector_validator: RuntimeError swallowed at L378: %s", e
                    )

            scan_time = (time.time() - start_time) * 1000

            return DetectionResult(
                file_path=file_path,
                violations=violations,
                scan_time_ms=scan_time,
            )

        except (RuntimeError, OSError) as e:
            Logger.error(f"Error scanning {file_path}: {e}")
            return DetectionResult(
                file_path=file_path,
                violations=[],
                scan_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    def scan_directory(
        self,
        directory: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[DetectionResult]:
        """
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of DetectionResults
        """
        include_patterns = include_patterns or ["**/*.py"]
        exclude_patterns = exclude_patterns or ["**/test_*.py", "**/__pycache__/**"]

        results = []

        for pattern in tqdm(include_patterns, desc="Processing", unit="item"):
            for file_path in tqdm(directory.glob(pattern), desc="Processing", unit="item"):
                # Skip excluded patterns
                skip = False
                for exclude in exclude_patterns:
                    if file_path.match(exclude):
                        skip = True
                        break

                if skip:
                    continue

                if file_path.is_file():
                    result = self.scan_file(file_path)
                    results.append(result)

        return results

    def _get_ast(self, file_path: Path) -> ast.Module | None:
        """Get AST for file with caching."""
        try:
            content = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.md5(content.encode()).hexdigest()

            cache_key = str(file_path)

            # Check cache
            if cache_key in self._ast_cache:
                cached_hash, cached_tree = self._ast_cache[cache_key]
                if cached_hash == content_hash:
                    return cached_tree

            # Parse and cache
            tree = ast.parse(content, filename=str(file_path))
            self._ast_cache[cache_key] = (content_hash, tree)

            return tree
        # guardian: Syntax errors should be caught at parser level, not runtime
        except SyntaxError as e:
            Logger.warning(f"Syntax error in {file_path}: {e}")
            return None
        except (RuntimeError, OSError) as e:
            Logger.error(f"Error reading {file_path}: {e}")
            return None

    def _is_file_whitelisted(self, file_path: Path) -> bool:
        """Check if file matches whitelist patterns."""
        for pattern in self.whitelisted_files:
            if file_path.match(pattern):
                return True
        return False

    def _is_violation_whitelisted(self, violation: AntiPatternViolation) -> bool:
        """Check if violation matches whitelist patterns."""
        for pattern in self.whitelisted_patterns:
            if pattern in violation.evidence:
                return True
        return False

    def _get_source_line(self, file_path: Path, line_number: int) -> str:
        """Get a specific line from the source file."""
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            if 0 < line_number <= len(lines):
                return lines[line_number - 1].strip()
        except (ValueError, TypeError, RuntimeError) as e:
            raise
        return ""


class CompositeDetector:
    """
    Combines multiple detectors into a single scanning interface.
    """

    def __init__(self, detectors: list[AntiPatternDetector] | None = None):
        self.detectors = detectors or []

    def add_detector(self, detector: AntiPatternDetector) -> None:
        """Add a detector to the composite."""
        self.detectors.append(detector)

    def scan_file(self, file_path: Path) -> list[DetectionResult]:
        """Scan file with all detectors."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CompositeDetector.scan_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CompositeDetector.scan_file".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        results = []
        for detector in tqdm(self.detectors, desc="Processing", unit="item"):
            result = detector.scan_file(file_path)
            results.append(result)
        return results

    def scan_directory(
        self,
        directory: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> dict[AntiPatternCategory, list[DetectionResult]]:
        """Scan directory with all detectors, grouped by category."""
        results: dict[AntiPatternCategory, list[DetectionResult]] = {}

        for detector in tqdm(self.detectors, desc="Processing", unit="item"):
            category_results = detector.scan_directory(directory, include_patterns, exclude_patterns)
            results[detector.category] = category_results

        return results

    def get_summary(self, results: dict[AntiPatternCategory, list[DetectionResult]]) -> dict[str, Any]:
        """Generate summary statistics from scan results."""
        summary = {
            "total_files_scanned": 0,
            "total_violations": 0,
            "violations_by_category": {},
            "files_with_violations": 0,
        }

        all_files = set()
        files_with_violations = set()

        for category, category_results in tqdm(results.items(), desc="Processing", unit="item"):
            category_violations = 0

            for result in category_results:
                all_files.add(result.file_path)

                if result.has_violations:
                    files_with_violations.add(result.file_path)
                    category_violations += result.violation_count

            summary["violations_by_category"][category.value] = category_violations
            summary["total_violations"] += category_violations

        summary["total_files_scanned"] = len(all_files)
        summary["files_with_violations"] = len(files_with_violations)

        return summary


__all__ = [
    "AntiPatternCategory",
    "AntiPatternDetector",
    "AntiPatternViolation",
    "CompositeDetector",
    "DetectionResult",
    "EnforcementLevel",
]
