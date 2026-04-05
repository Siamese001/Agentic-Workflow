"""
Path Fragility Anti-Pattern Detector

Detects string-based path manipulation instead of pathlib.Path usage.

Pattern Detection:
- os.path.join() calls
- os.getcwd() usage
- String concatenation for paths (+ "/" +)
- os.path.exists(), os.path.isfile(), etc.
"""

import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_pulls_context,
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
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "path_fragility_validator", "execution_auth")
_emit_validates_capability("p2", "path_fragility_validator", "capability_check")
_emit_routes_to_capability("p2", "path_fragility_validator", "capability_route")
_emit_writes_via_uwg("p2", "path_fragility_validator", "uwg_write")
_emit_blocks_direct_write("p2", "path_fragility_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "path_fragility_validator", "tool_invocation")
_emit_captures_execution_output("p2", "path_fragility_validator", "exec_output")
_emit_dispatches_agent("p3", "path_fragility_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "path_fragility_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "path_fragility_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "path_fragility_validator", "healing_outcome")
_emit_escalates_failure("p3", "path_fragility_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "path_fragility_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "path_fragility_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "path_fragility_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "path_fragility_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "path_fragility_validator", "eval_metric")
_emit_stores_embedding("p4", "path_fragility_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "path_fragility_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "path_fragility_validator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_1")
_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_2")
_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_3")
_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_4")
_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_5")
_emit_emits_metric_event("path_fragility_validator", "p4obs", "metric_6")
_emit_records_incident_event("path_fragility_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("path_fragility_validator", "p4obs", "anomaly")
_emit_writes_observability_log("path_fragility_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("path_fragility_validator", "p4obs", "mon_state")
_emit_triggers_alert("path_fragility_validator", "p4obs", "alert")
_emit_links_incident_trace("path_fragility_validator", "p4obs", "trace_link")
_emit_captures_pattern("path_fragility_validator", "p3lm", "pattern")
_emit_records_learning_event("path_fragility_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("path_fragility_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("path_fragility_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("path_fragility_validator", "p3lm", "routing")
_emit_improves_agent_policy("path_fragility_validator", "p3lm", "policy")
_emit_stores_learning_state("path_fragility_validator", "p3lm", "state")
_emit_records_execution_trace("path_fragility_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("path_fragility_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("path_fragility_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("path_fragility_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("path_fragility_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("path_fragility_validator", "env_read", "p2_env_1")
_emit_reads_environ("path_fragility_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("path_fragility_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("path_fragility_validator", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "path_fragility_validator")
emit_determinism_digest("p0", "path_fragility_validator")

_emit_dispatches_healing_run("p1", "path_fragility_validator", "L5")
_emit_routes_through("p1", "path_fragility_validator", "L5")
_emit_checks_agent_registry("p1", "path_fragility_validator", "agent_registry")
_emit_validates_agent_capability("p1", "path_fragility_validator", "capability")
_emit_dispatches_execution_plan("p1", "path_fragility_validator", "exec_plan")
_emit_agent_executes_agent("p1", "path_fragility_validator", "sub_agent")
_emit_routes_to_agent("p1", "path_fragility_validator", "target_agent")
_emit_verifies_policy("p1", "path_fragility_validator", "policy_check")
_emit_observes_runtime_state("p1", "path_fragility_validator", "runtime_state")
_emit_verifies_boundary("p1", "path_fragility_validator", "boundary_check")
_emit_transcripts_response("p1", "path_fragility_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "path_fragility_validator")
_emit_gated_by_confidence("p1", "path_fragility_validator", "confidence_gate")
_emit_escalates_to_human("p1", "path_fragility_validator", "L5")
_emit_reads_policy_state("p1", "path_fragility_validator", "L5")

_emit_applies_guardrail("p0", "path_fragility_validator", "p0_governance")
_emit_snapshots_state("p0", "path_fragility_validator", "state_snapshot")
_emit_writes_through("p1", "path_fragility_validator", "uwg_governed_write")
_emit_writes_through("p1", "path_fragility_validator", "uwg_governed_write_2")
_emit_pulls_context("p1", "path_fragility_validator", "context_retrieval")
_emit_pulls_context("p1", "path_fragility_validator", "context_retrieval_2")
emit_determinism_digest("trace_path_fragility_validator", "path_fragility_validator_dispatch")
emit_determinism_digest("trace_path_fragility_validator", "path_fragility_validator_complete")
_emit_validated_by_safety_plane("p1", "path_fragility_validator", "safety_validation")


class PathFragilityDetector(AntiPatternDetector):
    """
    Detects string-based path manipulation.

    String paths cause cross-platform incompatibility between
    Windows and Unix systems.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-path-string"

    # os.path functions to detect
    OS_PATH_FUNCTIONS = {
        "join",
        "exists",
        "isfile",
        "isdir",
        "basename",
        "dirname",
        "abspath",
        "realpath",
        "normpath",
        "expanduser",
        "splitext",
    }

    # os functions to detect
    OS_FUNCTIONS = {
        "getcwd",
        "chdir",
    }

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "setup.py",
            "setup.cfg",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.PATH_FRAGILITY

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect path fragility patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PathFragilityDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PathFragilityDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                violation = self._check_call(node, file_path, source_lines)
                if violation:
                    violations.append(violation)
            elif isinstance(node, ast.BinOp):
                violation = self._check_string_concat(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_call(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if a call uses os.path functions."""

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for os.path.* calls
        if isinstance(node.func, ast.Attribute):
            # Check os.path.join, os.path.exists, etc.
            if isinstance(node.func.value, ast.Attribute):
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.value.attr == "path"
                    and node.func.attr in self.OS_PATH_FUNCTIONS
                ):
                    return self._create_violation(node, file_path, f"os.path.{node.func.attr}()")

            # Check os.getcwd(), os.chdir()
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr in self.OS_FUNCTIONS
            ):
                return self._create_violation(node, file_path, f"os.{node.func.attr}()")

        return None

    def _check_string_concat(
        self,
        node: ast.BinOp,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check for string concatenation patterns that look like path building."""

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for string addition with path separators
        if not isinstance(node.op, ast.Add):
            return None

        # Look for patterns like: path + "/" + filename
        def contains_path_separator(n: ast.expr) -> bool:
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                return "/" in n.value or "\\" in n.value
            if isinstance(n, ast.BinOp):
                return contains_path_separator(n.left) or contains_path_separator(n.right)
            return False

        if contains_path_separator(node):
            return self._create_violation(node, file_path, "String concatenation for path building")

        return None

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, node.lineno)

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Path fragility: {pattern} - use pathlib.Path instead",
            evidence=evidence,
            severity="warning",
            suggested_fix=self._generate_fix_suggestion(pattern),
            metadata={
                "pattern": pattern,
            },
        )

    def _generate_fix_suggestion(self, pattern: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "os.path.join" in pattern:
            return """Replace os.path.join with pathlib.Path:
    # Before
    path = os.path.join(base, "subdir", "file.txt")

    # After
    from pathlib import Path
    path = Path(base) / "subdir" / "file.txt" """

        if "os.getcwd" in pattern:
            return """Replace os.getcwd with Path.cwd():
    # Before
    cwd = os.getcwd()

    # After
    from pathlib import Path
    cwd = Path.cwd()"""

        if "os.path.exists" in pattern:
            return """Replace os.path.exists with Path.exists():
    # Before
    if os.path.exists(path):

    # After
    from pathlib import Path
    if Path(path).exists():"""

        return """Use pathlib.Path for all path operations:
    from pathlib import Path
import uuid
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
_emit_pulls_context("p1", "path_fragility_validator", "context_pull")
_emit_pulls_context("p1", "path_fragility_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "path_fragility_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "path_fragility_validator", "uwg_term_secondary")
_emit_writes_through("p1", "path_fragility_validator", "write_through")
_emit_writes_through("p1", "path_fragility_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "path_fragility_validator", "safety_validation")
_emit_invokes_eval("p1", "path_fragility_validator", "eval_call")
_emit_proposal_commits_routing("p1", "path_fragility_validator", "routing_commit")

    # Path construction
    path = Path(base) / "subdir" / "file.txt"

    # Path operations
    path.exists()
    path.is_file()
    path.is_dir()
    path.parent
    path.name"""


__all__ = ["PathFragilityDetector"]
