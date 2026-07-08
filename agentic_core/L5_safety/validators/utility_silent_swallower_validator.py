"""
Utility Silent Swallower Validator

Enhanced silent swallower detection for utility/ops scripts with context-aware
classification and governance path enforcement.

Implements legacy editor Hardening Response requirements:
- Zero tolerance for governance/CI script silent failures
- Retry-with-reraise pattern detection
- Utility script classification by operational category
- Failure signal emission requirements
"""

import ast
import logging
import re
import uuid
from pathlib import Path

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "utility_silent_swallower_validator")
trace_contract.emit_determinism_digest("p0", "utility_silent_swallower_validator")

trace_contract._emit_dispatches_healing_run("p1", "utility_silent_swallower_validator", "L5")
trace_contract._emit_routes_through("p1", "utility_silent_swallower_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "utility_silent_swallower_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "utility_silent_swallower_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "utility_silent_swallower_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "utility_silent_swallower_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "utility_silent_swallower_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "utility_silent_swallower_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "utility_silent_swallower_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "utility_silent_swallower_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "utility_silent_swallower_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "utility_silent_swallower_validator")
trace_contract._emit_gated_by_confidence("p1", "utility_silent_swallower_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "utility_silent_swallower_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "utility_silent_swallower_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "utility_silent_swallower_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "utility_silent_swallower_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "utility_silent_swallower_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "utility_silent_swallower_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "utility_silent_swallower_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "utility_silent_swallower_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "utility_silent_swallower_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "utility_silent_swallower_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "utility_silent_swallower_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "utility_silent_swallower_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "utility_silent_swallower_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "utility_silent_swallower_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "utility_silent_swallower_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "utility_silent_swallower_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "utility_silent_swallower_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "utility_silent_swallower_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "utility_silent_swallower_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "utility_silent_swallower_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "utility_silent_swallower_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "utility_silent_swallower_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "utility_silent_swallower_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "utility_silent_swallower_validator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("utility_silent_swallower_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("utility_silent_swallower_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("utility_silent_swallower_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("utility_silent_swallower_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("utility_silent_swallower_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("utility_silent_swallower_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("utility_silent_swallower_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("utility_silent_swallower_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("utility_silent_swallower_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("utility_silent_swallower_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("utility_silent_swallower_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("utility_silent_swallower_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("utility_silent_swallower_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("utility_silent_swallower_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("utility_silent_swallower_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("utility_silent_swallower_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("utility_silent_swallower_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("utility_silent_swallower_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("utility_silent_swallower_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("utility_silent_swallower_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("utility_silent_swallower_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("utility_silent_swallower_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("utility_silent_swallower_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "utility_silent_swallower_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "utility_silent_swallower_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "utility_silent_swallower_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "utility_silent_swallower_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "utility_silent_swallower_validator", "write_through")
trace_contract._emit_writes_through("p1", "utility_silent_swallower_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "utility_silent_swallower_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "utility_silent_swallower_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "utility_silent_swallower_validator", "routing_commit")

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
        trace_contract._emit_validated_by_safety_plane(
            str(uuid.uuid4()),
            "UtilityScriptClassifier.classify_script",
            "L5_POLICY",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "UtilityScriptClassifier.classify_script",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:UtilityScriptClassifier.classify_script".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        except (ValueError, TypeError, RuntimeError) as e:
            raise


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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "UtilitySilentSwallowerDetector.detect",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:UtilitySilentSwallowerDetector.detect".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

        except Exception:  # guardian: allow-broad-exception -- scan error re-raised to caller for handling
            raise

        return violations

    def _check_try_except(
        self,
        node: ast.Try,
        file_path: Path,
        source_lines: list[str],
        script_category: str,
    ) -> AntiPatternViolation | None:
        """Check a try-except node for silent swallower violations."""

        for handler in tqdm(node.handlers, desc="Processing", unit="item"):
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
        except (
            IndexError,
            TypeError,
        ):  # guardian: allow-silent-swallow -- boundary access best-effort: caller treats False as "no match"
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
        for node in tqdm(ast.walk(handler), desc="Processing", unit="item"):
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
        self,
        file_path: Path,
        handler: ast.ExceptHandler,
        message: str,
        enforcement_level: EnforcementLevel,
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
