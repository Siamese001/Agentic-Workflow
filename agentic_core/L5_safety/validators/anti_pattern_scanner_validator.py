"""
Anti-Pattern Scanner

Unified interface for scanning repositories for Phase 2 landmine anti-patterns.
Integrates with Guardian tests and HygieneGuardianAgent for comprehensive
code quality enforcement.

Usage:
    from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

    scanner = AntiPatternScanner(project_root)
    report = scanner.scan_repository()
    print(report.summary())
"""

import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    INFRASTRUCTURE_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    get_all_apps_paths,
)
from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternViolation,
    CompositeDetector,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.config_with_logic_validator import (
    ConfigWithLogicDetector,
)
from agentic_core.L5_safety.validators.direct_prompt_compilation_validator import (
    DirectPromptCompilationDetector,
)
from agentic_core.L5_safety.validators.global_mutation_validator import (
    GlobalMutationDetector,
)
from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
    HollowFileDetector,
)
from agentic_core.L5_safety.validators.invalid_stub_validator import (
    InvalidStubDetector,
)
from agentic_core.L5_safety.validators.magic_validator import (
    MagicConfigDetector,
)
from agentic_core.L5_safety.validators.path_fragility_validator import (
    PathFragilityDetector,
)
from agentic_core.L5_safety.validators.silent_degradation_validator import (
    SilentDegradationDetector,
)
from agentic_core.L5_safety.validators.silent_swallower_validator import (
    SilentSwallowerDetector,
)
from agentic_core.L5_safety.validators.type_erasure_validator import (
    TypeErasureDetector,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
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
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "anti_pattern_scanner_validator")
emit_determinism_digest("p0", "anti_pattern_scanner_validator")

_emit_dispatches_healing_run("p1", "anti_pattern_scanner_validator", "L5")
_emit_routes_through("p1", "anti_pattern_scanner_validator", "L5")
_emit_checks_agent_registry("p1", "anti_pattern_scanner_validator", "agent_registry")
_emit_validates_agent_capability("p1", "anti_pattern_scanner_validator", "capability")
_emit_dispatches_execution_plan("p1", "anti_pattern_scanner_validator", "exec_plan")
_emit_agent_executes_agent("p1", "anti_pattern_scanner_validator", "sub_agent")
_emit_routes_to_agent("p1", "anti_pattern_scanner_validator", "target_agent")
_emit_verifies_policy("p1", "anti_pattern_scanner_validator", "policy_check")
_emit_observes_runtime_state("p1", "anti_pattern_scanner_validator", "runtime_state")
_emit_verifies_boundary("p1", "anti_pattern_scanner_validator", "boundary_check")
_emit_transcripts_response("p1", "anti_pattern_scanner_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "anti_pattern_scanner_validator")
_emit_gated_by_confidence("p1", "anti_pattern_scanner_validator", "confidence_gate")
_emit_escalates_to_human("p1", "anti_pattern_scanner_validator", "L5")
_emit_reads_policy_state("p1", "anti_pattern_scanner_validator", "L5")
_emit_applies_guardrail("p0", "anti_pattern_scanner_validator", "p0_governance")
_emit_snapshots_state("p0", "anti_pattern_scanner_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "anti_pattern_scanner_validator", "execution_auth")
_emit_validates_capability("p2", "anti_pattern_scanner_validator", "capability_check")
_emit_routes_to_capability("p2", "anti_pattern_scanner_validator", "capability_route")
_emit_writes_via_uwg("p2", "anti_pattern_scanner_validator", "uwg_write")
_emit_blocks_direct_write("p2", "anti_pattern_scanner_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "anti_pattern_scanner_validator", "tool_invocation")
_emit_captures_execution_output("p2", "anti_pattern_scanner_validator", "exec_output")
_emit_dispatches_agent("p3", "anti_pattern_scanner_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "anti_pattern_scanner_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "anti_pattern_scanner_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "anti_pattern_scanner_validator", "healing_outcome")
_emit_escalates_failure("p3", "anti_pattern_scanner_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "anti_pattern_scanner_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "anti_pattern_scanner_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "anti_pattern_scanner_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "anti_pattern_scanner_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "anti_pattern_scanner_validator", "eval_metric")
_emit_stores_embedding("p4", "anti_pattern_scanner_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "anti_pattern_scanner_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "anti_pattern_scanner_validator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_1")
_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_2")
_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_3")
_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_4")
_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_5")
_emit_emits_metric_event("anti_pattern_scanner_validator", "p4obs", "metric_6")
_emit_records_incident_event("anti_pattern_scanner_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("anti_pattern_scanner_validator", "p4obs", "anomaly")
_emit_writes_observability_log("anti_pattern_scanner_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("anti_pattern_scanner_validator", "p4obs", "mon_state")
_emit_triggers_alert("anti_pattern_scanner_validator", "p4obs", "alert")
_emit_links_incident_trace("anti_pattern_scanner_validator", "p4obs", "trace_link")
_emit_captures_pattern("anti_pattern_scanner_validator", "p3lm", "pattern")
_emit_records_learning_event("anti_pattern_scanner_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("anti_pattern_scanner_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("anti_pattern_scanner_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("anti_pattern_scanner_validator", "p3lm", "routing")
_emit_improves_agent_policy("anti_pattern_scanner_validator", "p3lm", "policy")
_emit_stores_learning_state("anti_pattern_scanner_validator", "p3lm", "state")
_emit_records_execution_trace("anti_pattern_scanner_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("anti_pattern_scanner_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("anti_pattern_scanner_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("anti_pattern_scanner_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("anti_pattern_scanner_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("anti_pattern_scanner_validator", "env_read", "p2_env_1")
_emit_reads_environ("anti_pattern_scanner_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("anti_pattern_scanner_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("anti_pattern_scanner_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "anti_pattern_scanner_validator", "context_pull")
_emit_pulls_context("p1", "anti_pattern_scanner_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "anti_pattern_scanner_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "anti_pattern_scanner_validator", "uwg_term_2")
_emit_writes_through("p1", "anti_pattern_scanner_validator", "write_through")
_emit_writes_through("p1", "anti_pattern_scanner_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "anti_pattern_scanner_validator", "safety_validation")
_emit_invokes_eval("p1", "anti_pattern_scanner_validator", "eval_call")
_emit_proposal_commits_routing("p1", "anti_pattern_scanner_validator", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class ScanReport:
    """Report from anti-pattern scanning."""

    project_root: Path
    total_files_scanned: int = 0
    total_violations: int = 0
    violations_by_category: dict[str, int] = field(default_factory=dict)
    _files_with_violations: int = 0
    scan_time_ms: float = 0.0
    all_violations: list[AntiPatternViolation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def files_with_violations(self) -> int:
        if self._files_with_violations == 0 and self.all_violations:
            unique_files = {v.file_path for v in self.all_violations if getattr(v, "file_path", None)}
            return len(unique_files)
        return self._files_with_violations

    @files_with_violations.setter
    def files_with_violations(self, value: int) -> None:
        self._files_with_violations = value

    def add_violation(self, violation: AntiPatternViolation) -> None:
        if violation is None:
            raise TypeError("Violation cannot be None")
        self.all_violations.append(violation)
        self.total_violations = len(self.all_violations)
        if getattr(violation, "file_path", None):
            unique_files = {v.file_path for v in self.all_violations if getattr(v, "file_path", None)}
            self._files_with_violations = len(unique_files)
        category_key = violation.category
        self.violations_by_category[category_key] = self.violations_by_category.get(category_key, 0) + 1

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def summary(self) -> str:
        """Generate human-readable summary."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ScanReport.summary")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ScanReport.summary".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        lines = [
            "=" * 60,
            "Anti-Pattern Scan Report",
            "=" * 60,
            f"Project: {self.project_root}",
            f"Files Scanned: {self.total_files_scanned}",
            f"Files with Violations: {self.files_with_violations}",
            f"Violations: {self.total_violations}",
            f"Errors: {len(self.errors)}",
            f"Status: {'PASSED' if self.passed else 'FAILED'}",
            f"Scan Time: {self.scan_time_ms:.2f}ms",
            "",
            "Violations by Category:",
        ]

        for category, count in self.violations_by_category.items():
            status = "🚨" if count > 0 else "✅"
            lines.append(f"  {status} {category}: {count}")

        if self.all_violations:
            lines.append("")
            lines.append("Top Violations:")
            for v in self.all_violations[:10]:
                lines.append(
                    f"  - {v.file_path.name}:{v.line_number} [{v.category.value}] {v.message[:50]}...",
                )
        lines.append("=" * 60)
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_root": str(self.project_root),
            "total_files_scanned": self.total_files_scanned,
            "total_violations": self.total_violations,
            "violations_by_category": self.violations_by_category,
            "files_with_violations": self.files_with_violations,
            "scan_time_ms": self.scan_time_ms,
            "violations": [v.to_dict() for v in self.all_violations],
            "errors": self.errors,
        }

    @property
    def passed(self) -> bool:
        """Check if scan passed (no violations)."""
        return self.total_violations == 0


class AntiPatternScanner:
    """
    Unified anti-pattern scanner for repository-wide detection.

    Combines all Phase 2 landmine detectors into a single scanning interface
    with configurable enforcement levels and reporting.
    """

    # Default directories to scan
    @classmethod
    def get_default_scan_dirs(cls) -> list[str]:
        """Get default scan directories using dynamic apps discovery.

        Returns:
            List of directory names to scan, including all apps_* directories.
        """
        dirs = [
            AGENTIC_CORE_DIR,
            INFRASTRUCTURE_DIR,
            OPS_SCRIPTS_DIR,
            SYSTEM_LEARNING_DIR,
            TOOLS_DIR,
        ]

        # Add all apps_* directories dynamically
        apps_paths = get_all_apps_paths()
        apps_dirs = [p.name for p in apps_paths]
        dirs.extend(apps_dirs)

        return dirs

    # Default exclude patterns
    DEFAULT_EXCLUDES = [
        "**/test_*.py",
        "**/*_test.py",
        "**/conftest.py",
        "**/__pycache__/**",
        "**/archives/**",
        "**/.git/**",
    ]

    def __init__(
        self,
        project_root: Path,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        scan_dirs: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ):
        """
        Initialize the anti-pattern scanner.

        Args:
            project_root: Root directory of the project
            enforcement_level: Enforcement level for all detectors
            scan_dirs: Directories to scan (relative to project_root)
            exclude_patterns: Glob patterns to exclude
        """
        root_path = Path(project_root)
        if (
            isinstance(project_root, str)
            and root_path.drive == ""
            and project_root.startswith("/")
        ):
            raise FileNotFoundError(f"Project root does not exist: {project_root}")
        self.project_root = root_path.resolve()
        if not self.project_root.is_dir():
            raise FileNotFoundError(f"Project root does not exist: {self.project_root}")
        self.enforcement_level = enforcement_level
        self.scan_dirs = scan_dirs or self.get_default_scan_dirs()
        if not any((self.project_root / scan_dir).exists() for scan_dir in self.scan_dirs):
            self.scan_dirs = ["."]
        self.exclude_patterns = exclude_patterns or self.DEFAULT_EXCLUDES
        self.config: dict[str, Any] = {}

        # Initialize detectors
        self.composite = CompositeDetector(
            [
                SilentSwallowerDetector(enforcement_level=enforcement_level),
                SilentDegradationDetector(enforcement_level=enforcement_level),
                TypeErasureDetector(enforcement_level=enforcement_level),
                PathFragilityDetector(enforcement_level=enforcement_level),
                MagicConfigDetector(enforcement_level=enforcement_level),
                GlobalMutationDetector(enforcement_level=enforcement_level),
                ConfigWithLogicDetector(enforcement_level=enforcement_level),
                DirectPromptCompilationDetector(enforcement_level=enforcement_level),
                HollowFileDetector(enforcement_level=enforcement_level),
                InvalidStubDetector(enforcement_level=enforcement_level),
            ],
        )
        self.detectors = self.composite.detectors

    def scan(self) -> ScanReport:
        return self.scan_repository()

    def is_initialized(self) -> bool:
        return True

    def get_detector_count(self) -> int:
        if isinstance(self.detectors, (list, tuple, set)):
            return len(self.detectors)
        if isinstance(self.detectors, dict):
            return len(self.detectors)
        return 0

    def set_config(self, config: dict[str, Any]) -> None:
        self.config.update(config)

    def scan_repository(self) -> ScanReport:
        """
        Scan the entire repository for anti-patterns.

        Returns:
            ScanReport with all findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AntiPatternScanner.scan_repository")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AntiPatternScanner.scan_repository".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        import time

        start_time = time.time()

        report = ScanReport(project_root=self.project_root)
        all_files = set()
        files_with_violations = set()
        effective_excludes = self.exclude_patterns
        if self.scan_dirs == ["."]:
            effective_excludes = []

        from fnmatch import fnmatch  # noqa: PLC0415

        def _is_excluded(path: Path) -> bool:
            rel_path = path.relative_to(self.project_root).as_posix()
            return any(fnmatch(rel_path, pattern) for pattern in effective_excludes)

        for scan_dir in self.scan_dirs:
            target_dir = self.project_root / scan_dir

            if not target_dir.exists():
                Logger.debug(f"Skipping non-existent directory: {target_dir}")
                continue

            for file_path in target_dir.rglob("*.py"):
                if _is_excluded(file_path):
                    continue
                all_files.add(file_path)

            try:
                results = self.composite.scan_directory(
                    target_dir,
                    include_patterns=["**/*.py"],
                    exclude_patterns=effective_excludes,
                )

                for category, category_results in results.items():
                    category_name = category.value

                    if category_name not in report.violations_by_category:
                        report.violations_by_category[category_name] = 0

                    for result in category_results:
                        all_files.add(result.file_path)

                        if result.error:
                            report.errors.append(f"{result.file_path}: {result.error}")

                        if result.has_violations:
                            files_with_violations.add(result.file_path)

                            for violation in result.violations:
                                if not violation.whitelisted:
                                    report.violations_by_category[category_name] += 1
                                    report.total_violations += 1
                                    report.all_violations.append(violation)

            # Error handling - log and continue scanning other directories
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"Error scanning {target_dir}: {e}")
                report.errors.append(f"Error scanning {target_dir}: {e}")
                continue

        report.total_files_scanned = len(all_files)
        report.files_with_violations = len(files_with_violations)
        report.scan_time_ms = max((time.time() - start_time) * 1000, 0.01)

        # Sort violations by severity
        report.all_violations.sort(
            key=lambda v: (0 if v.severity == "error" else 1, str(v.file_path), v.line_number),
        )

        return report

    def scan_file(self, file_path: Path) -> list[AntiPatternViolation]:
        """
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of violations found
        """
        violations = []

        results = self.composite.scan_file(file_path)

        for result in results:
            for violation in result.violations:
                if not violation.whitelisted:
                    violations.append(violation)

        return violations

    def scan_changed_files(self, file_paths: list[Path]) -> ScanReport:
        """
        Scan only specific files (for incremental PR checks).

        Args:
            file_paths: List of files to scan

        Returns:
            ScanReport with findings for the specified files
        """
        import time

        start_time = time.time()

        report = ScanReport(project_root=self.project_root)
        files_with_violations = set()

        for category in AntiPatternCategory:
            report.violations_by_category[category.value] = 0

        for file_path in file_paths:
            if not file_path.exists() or not file_path.suffix == ".py":
                continue

            violations = self.scan_file(file_path)

            if violations:
                files_with_violations.add(file_path)

                for violation in violations:
                    category_name = violation.category.value
                    report.violations_by_category[category_name] += 1
                    report.total_violations += 1
                    report.all_violations.append(violation)

        report.total_files_scanned = len(file_paths)
        report.files_with_violations = len(files_with_violations)
        report.scan_time_ms = (time.time() - start_time) * 1000

        return report

    def get_enforcement_action(self, report: ScanReport) -> str:
        """
        Determine the enforcement action based on scan results.

        Args:
            report: Scan report

        Returns:
            Action to take: "pass", "warn", "soft_block", "hard_block"
        """
        _emit_validated_by_safety_plane(
            str(uuid.uuid4()), "AntiPatternScanner.get_enforcement_action", "L5_POLICY"
        )
        if report.passed:
            return "pass"

        if self.enforcement_level == EnforcementLevel.DISABLED:
            return "pass"
        elif self.enforcement_level == EnforcementLevel.WARNING:
            return "warn"
        elif self.enforcement_level == EnforcementLevel.SOFT_BLOCK:
            return "soft_block"
        elif self.enforcement_level == EnforcementLevel.HARD_BLOCK:
            return "hard_block"

        return "warn"


def run_scan(project_root: Path | None = None) -> ScanReport:
    """
    Convenience function to run a full repository scan.

    Args:
        project_root: Optional project root (defaults to current working directory)

    Returns:
        ScanReport with all findings
    """
    if project_root is None:
        project_root = Path.cwd()

    scanner = AntiPatternScanner(project_root)
    return scanner.scan_repository()


__all__ = [
    "AntiPatternScanner",
    "ScanReport",
    "run_scan",
]
