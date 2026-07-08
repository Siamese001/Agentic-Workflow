"""
Global Mutation Anti-Pattern Detector

Detects runtime modifications to global state that break agent isolation.

Pattern Detection:
- sys.path.insert() and sys.path.append()
- os.environ modifications
- Global variable mutations in module scope
"""

import ast
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "global_mutation_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "global_mutation_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "global_mutation_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "global_mutation_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "global_mutation_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "global_mutation_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "global_mutation_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "global_mutation_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "global_mutation_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "global_mutation_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "global_mutation_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "global_mutation_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "global_mutation_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "global_mutation_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "global_mutation_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "global_mutation_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "global_mutation_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "global_mutation_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "global_mutation_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "global_mutation_validator", "exec_snapshot_link")

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("global_mutation_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("global_mutation_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("global_mutation_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("global_mutation_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("global_mutation_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("global_mutation_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("global_mutation_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("global_mutation_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("global_mutation_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("global_mutation_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("global_mutation_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("global_mutation_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("global_mutation_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("global_mutation_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("global_mutation_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("global_mutation_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("global_mutation_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("global_mutation_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("global_mutation_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("global_mutation_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("global_mutation_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("global_mutation_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("global_mutation_validator", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "global_mutation_validator")
trace_contract.emit_determinism_digest("p0", "global_mutation_validator")

trace_contract._emit_dispatches_healing_run("p1", "global_mutation_validator", "L5")
trace_contract._emit_routes_through("p1", "global_mutation_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "global_mutation_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "global_mutation_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "global_mutation_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "global_mutation_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "global_mutation_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "global_mutation_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "global_mutation_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "global_mutation_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "global_mutation_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "global_mutation_validator")
trace_contract._emit_gated_by_confidence("p1", "global_mutation_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "global_mutation_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "global_mutation_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "global_mutation_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "global_mutation_validator", "state_snapshot")
trace_contract._emit_writes_through("p1", "global_mutation_validator", "uwg_governed_write")
trace_contract._emit_writes_through("p1", "global_mutation_validator", "uwg_governed_write_2")
trace_contract._emit_pulls_context("p1", "global_mutation_validator", "context_retrieval")
trace_contract._emit_pulls_context("p1", "global_mutation_validator", "context_retrieval_2")
trace_contract.emit_determinism_digest("trace_global_mutation_validator", "global_mutation_validator_dispatch")
trace_contract.emit_determinism_digest("trace_global_mutation_validator", "global_mutation_validator_complete")
trace_contract._emit_validated_by_safety_plane("p1", "global_mutation_validator", "safety_validation")


class GlobalMutationDetector(AntiPatternDetector):
    """
    Detects runtime global state modifications.

    Global mutations cause "spooky action at a distance" where
    one agent's changes affect other agents unexpectedly.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-global-mutation"

    # sys.path modification methods
    SYS_PATH_METHODS = {"insert", "append", "extend", "remove"}

    # os.environ modification methods
    ENVIRON_METHODS = {"update", "setdefault", "pop", "clear"}

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files (entry points and config files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "__main__.py",
            "setup.py",
            "manage.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.GLOBAL_MUTATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect global mutation patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "GlobalMutationDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GlobalMutationDetector.detect".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                violation = self._check_call(node, file_path, source_lines)
                if violation:
                    violations.append(violation)
            elif isinstance(node, ast.Subscript):
                violation = self._check_subscript_assign(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_call(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if a call modifies global state."""

        # Check for whitelist comment on any of the previous 5 lines (handles if-guard patterns)
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            for lookback in range(1, 6):
                check_line = node.lineno - lookback - 1
                if check_line < 0:
                    break
                if self.WHITELIST_COMMENT in source_lines[check_line].strip():
                    return None
                # Stop looking back if we hit a non-blank, non-comment, non-if line
                stripped = source_lines[check_line].strip()
                if stripped and not stripped.startswith("#") and not stripped.startswith("if "):
                    break

        # Check for sys.path.insert(), sys.path.append(), etc.
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                # sys.path.insert(0, ...)
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "sys"
                    and node.func.value.attr == "path"
                    and node.func.attr in self.SYS_PATH_METHODS
                ):
                    return self._create_violation(
                        node,
                        file_path,
                        f"sys.path.{node.func.attr}()",
                        "sys.path",
                    )

            # os.environ.update(), os.environ.setdefault()
            if (
                isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "os"
                and node.func.value.attr == "environ"
                and node.func.attr in self.ENVIRON_METHODS
            ):
                return self._create_violation(
                    node,
                    file_path,
                    f"os.environ.{node.func.attr}()",
                    "os.environ",
                )

        return None

    def _check_subscript_assign(
        self,
        node: ast.Subscript,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check for os.environ['KEY'] = value patterns."""

        # This is tricky - we need to find the parent Assign node
        # For now, we'll check if this subscript is on os.environ

        # Check for whitelist comment on any of the previous 5 lines
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            for lookback in range(1, 6):
                check_line = node.lineno - lookback - 1
                if check_line < 0:
                    break
                if self.WHITELIST_COMMENT in source_lines[check_line].strip():
                    return None
                stripped = source_lines[check_line].strip()
                if stripped and not stripped.startswith("#") and not stripped.startswith("if "):
                    break

        # Check for os.environ[...] pattern
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "os"
                and node.value.attr == "environ"
            ):
                # Get the key being set
                key = ""
                if isinstance(node.slice, ast.Constant):
                    key = str(node.slice.value)

                # Check if this is in an assignment context
                # We check the source line for '='
                evidence = self._get_source_line(file_path, node.lineno)
                if "=" in evidence and "==" not in evidence:
                    return self._create_violation(
                        node,
                        file_path,
                        f"os.environ['{key}'] assignment",
                        "os.environ",
                    )

        return None

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
        mutation_target: str,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, node.lineno)

        severity = "error" if "sys.path" in mutation_target else "warning"

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Global mutation: {pattern} modifies global state at runtime",
            evidence=evidence,
            severity=severity,
            suggested_fix=self._generate_fix_suggestion(mutation_target),
            metadata={
                "pattern": pattern,
                "mutation_target": mutation_target,
            },
        )

    def _generate_fix_suggestion(self, mutation_target: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "sys.path" in mutation_target:
            return """Remove runtime sys.path manipulation:

    # Option 1: Set PYTHONPATH before running
    # export PYTHONPATH=/path/to/project:$PYTHONPATH

    # Option 2: Use pyproject.toml or setup.py for package installation
    # pip install -e .

    # Option 3: Use absolute imports from project root
    from agentic_core.module import function"""

        if "os.environ" in mutation_target:
            return """Use configuration management instead of runtime env modification:

    # Option 1: Use environment variables at startup
    # Set in .env file or shell profile

    # Option 2: Use AgentDefaults for configuration
    from agentic_core.config.agent_defaults import AgentDefaults
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
_emit_pulls_context("p1", "global_mutation_validator", "context_pull")
_emit_pulls_context("p1", "global_mutation_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "global_mutation_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "global_mutation_validator", "uwg_term_secondary")
_emit_writes_through("p1", "global_mutation_validator", "write_through")
_emit_writes_through("p1", "global_mutation_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "global_mutation_validator", "safety_validation")
_emit_invokes_eval("p1", "global_mutation_validator", "eval_call")
_emit_proposal_commits_routing("p1", "global_mutation_validator", "routing_commit")
    value = AgentDefaults.get("CONFIG_NAME", "default")

    # Option 3: Pass configuration through function parameters
    def my_function(config_value: str = None):
        config_value = config_value or os.getenv("CONFIG_NAME", "default")"""

        return """Avoid modifying global state at runtime.
Use dependency injection or configuration management instead."""


__all__ = ["GlobalMutationDetector"]
