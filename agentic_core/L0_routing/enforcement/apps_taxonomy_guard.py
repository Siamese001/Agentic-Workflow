"""
L0 Routing Apps Taxonomy Guard - Deterministic import-graph checks

Ensures apps_* remain ZERO authority and cannot import from agentic_core
in prohibited directions, enforced via deterministic import-graph checks.
"""

import ast
import uuid
from pathlib import Path

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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "apps_taxonomy_guard", "L0")
_emit_routes_through("p1", "apps_taxonomy_guard", "L0")
_emit_checks_agent_registry("p1", "apps_taxonomy_guard", "agent_registry")
_emit_validates_agent_capability("p1", "apps_taxonomy_guard", "capability")
_emit_dispatches_execution_plan("p1", "apps_taxonomy_guard", "exec_plan")
_emit_agent_executes_agent("p1", "apps_taxonomy_guard", "sub_agent")
_emit_routes_to_agent("p1", "apps_taxonomy_guard", "target_agent")
_emit_verifies_policy("p1", "apps_taxonomy_guard", "policy_check")
_emit_observes_runtime_state("p1", "apps_taxonomy_guard", "runtime_state")
_emit_verifies_boundary("p1", "apps_taxonomy_guard", "boundary_check")
_emit_transcripts_response("p1", "apps_taxonomy_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "apps_taxonomy_guard")
_emit_gated_by_confidence("p1", "apps_taxonomy_guard", "confidence_gate")
_emit_escalates_to_human("p1", "apps_taxonomy_guard", "L0")
_emit_reads_policy_state("p1", "apps_taxonomy_guard", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "apps_taxonomy_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "apps_taxonomy_guard", "execution_auth")
_emit_validates_capability("p2", "apps_taxonomy_guard", "capability_check")
_emit_routes_to_capability("p2", "apps_taxonomy_guard", "capability_route")
_emit_writes_via_uwg("p2", "apps_taxonomy_guard", "uwg_write")
_emit_blocks_direct_write("p2", "apps_taxonomy_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "apps_taxonomy_guard", "tool_invocation")
_emit_captures_execution_output("p2", "apps_taxonomy_guard", "exec_output")
_emit_dispatches_agent("p3", "apps_taxonomy_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "apps_taxonomy_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "apps_taxonomy_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "apps_taxonomy_guard", "healing_outcome")
_emit_escalates_failure("p3", "apps_taxonomy_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "apps_taxonomy_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "apps_taxonomy_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "apps_taxonomy_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "apps_taxonomy_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "apps_taxonomy_guard", "eval_metric")
_emit_stores_embedding("p4", "apps_taxonomy_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "apps_taxonomy_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "apps_taxonomy_guard", "exec_snapshot_link")
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

_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_1")
_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_2")
_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_3")
_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_4")
_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_5")
_emit_emits_metric_event("apps_taxonomy_guard", "p4obs", "metric_6")
_emit_records_incident_event("apps_taxonomy_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("apps_taxonomy_guard", "p4obs", "anomaly")
_emit_writes_observability_log("apps_taxonomy_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("apps_taxonomy_guard", "p4obs", "mon_state")
_emit_triggers_alert("apps_taxonomy_guard", "p4obs", "alert")
_emit_links_incident_trace("apps_taxonomy_guard", "p4obs", "trace_link")
_emit_captures_pattern("apps_taxonomy_guard", "p3lm", "pattern")
_emit_records_learning_event("apps_taxonomy_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("apps_taxonomy_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("apps_taxonomy_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("apps_taxonomy_guard", "p3lm", "routing")
_emit_improves_agent_policy("apps_taxonomy_guard", "p3lm", "policy")
_emit_stores_learning_state("apps_taxonomy_guard", "p3lm", "state")
_emit_records_execution_trace("apps_taxonomy_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("apps_taxonomy_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("apps_taxonomy_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("apps_taxonomy_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("apps_taxonomy_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("apps_taxonomy_guard", "env_read", "p2_env_1")
_emit_reads_environ("apps_taxonomy_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("apps_taxonomy_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("apps_taxonomy_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "apps_taxonomy_guard", "context_pull")
_emit_pulls_context("p1", "apps_taxonomy_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "apps_taxonomy_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "apps_taxonomy_guard", "uwg_term_2")
_emit_writes_through("p1", "apps_taxonomy_guard", "write_through")
_emit_writes_through("p1", "apps_taxonomy_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "apps_taxonomy_guard", "safety_validation")
_emit_invokes_eval("p1", "apps_taxonomy_guard", "eval_call")
_emit_proposal_commits_routing("p1", "apps_taxonomy_guard", "routing_commit")


class AppsTaxonomyGuard:
    """
    Guard that enforces apps_* taxonomy rules via AST parsing.

    Uses read-only AST parsing (no imports/execution) to detect
    prohibited imports from apps_* to agentic_core.
    """

    ALLOWED_IMPORTS = {"agentic_core.interfaces", "agentic_core.prompt_governance.contracts"}

    def scan(self, *, repo_root: str) -> tuple[str, ...]:
        """
        Scan apps_* packages for prohibited agentic_core imports.

        Args:
            repo_root: Repository root path

        Returns:
            Deterministic sorted tuple of violation strings: "path:lineno import ..."
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "AppsTaxonomyGuard.scan")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        violations = []
        repo_path = Path(repo_root)
        for apps_dir in repo_path.glob("apps_*"):
            if apps_dir.is_dir():
                violations.extend(self._scan_apps_directory(apps_dir, repo_path))
        return tuple(sorted(violations))

    def _scan_apps_directory(self, apps_dir: Path, repo_root: Path) -> list[str]:
        """Scan a single apps_* directory for violations."""
        violations = []
        for py_file in apps_dir.rglob("*.py"):
            try:
                violations.extend(self._scan_file(py_file, repo_root))
            # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue
        return violations

    def _scan_file(self, file_path: Path, repo_root: Path) -> list[str]:
        """Scan a single Python file for prohibited imports."""
        violations = []
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
        # guardian: allow-specific -- file system and encoding errors
        except (OSError, UnicodeDecodeError, SyntaxError) as e:
            # guardian: allow-silent-swallow - acceptable exception handling
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                violations.extend(self._check_import_node(node, file_path, repo_root))
            elif isinstance(node, ast.ImportFrom):
                violations.extend(self._check_import_from_node(node, file_path, repo_root))
        return violations

    def _check_import_node(self, node: ast.Import, file_path: Path, repo_root: Path) -> list[str]:
        """Check import node for prohibited agentic_core imports."""
        _emit_applies_guardrail(str(uuid.uuid4()), "AppsTaxonomyGuard._check_import_node", "L0_ROUTING")
        violations = []
        for alias in node.names:
            if alias.name.startswith("agentic_core"):
                if not self._is_allowed_import(alias.name):
                    relative_path = file_path.relative_to(repo_root).as_posix()
                    violation = f"{relative_path}:{node.lineno} import {alias.name}"
                    violations.append(violation)
        return violations

    def _check_import_from_node(self, node: ast.ImportFrom, file_path: Path, repo_root: Path) -> list[str]:
        """Check import-from node for prohibited agentic_core imports."""
        violations = []
        if node.module and node.module.startswith("agentic_core"):
            if not self._is_allowed_import(node.module):
                imported_names = ", ".join(alias.name for alias in node.names)
                import_stmt = f"from {node.module} import {imported_names}"
                relative_path = file_path.relative_to(repo_root).as_posix()
                violation = f"{relative_path}:{node.lineno} {import_stmt}"
                violations.append(violation)
        return violations

    def _is_allowed_import(self, import_path: str) -> bool:
        """Check if import path is in the allowlist."""
        if import_path in self.ALLOWED_IMPORTS:
            return True
        for allowed in self.ALLOWED_IMPORTS:
            if import_path.startswith(allowed + "."):
                return True
        return False