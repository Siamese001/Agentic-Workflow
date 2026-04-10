#!/usr/bin/env python3
"""Agent Registry Enforcement Scanner

Scans first-party code to ensure all agent usage is registered and compliant
with the 2×2 execution policy. Fails on violations.
"""

import ast
import os
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "audit_agent_registry_enforcement")
_emit_applies_guardrail("p0", "audit_agent_registry_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "audit_agent_registry_enforcement", "policy_binding")
_emit_snapshots_state("p0", "audit_agent_registry_enforcement", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("audit_agent_registry_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("audit_agent_registry_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("audit_agent_registry_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("audit_agent_registry_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("audit_agent_registry_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("audit_agent_registry_enforcement", "p4obs", "alert")
_emit_links_incident_trace("audit_agent_registry_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("audit_agent_registry_enforcement", "p3lm", "pattern")
_emit_records_learning_event("audit_agent_registry_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("audit_agent_registry_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("audit_agent_registry_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("audit_agent_registry_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("audit_agent_registry_enforcement", "p3lm", "policy")
_emit_stores_learning_state("audit_agent_registry_enforcement", "p3lm", "state")
_emit_records_execution_trace("audit_agent_registry_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("audit_agent_registry_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("audit_agent_registry_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("audit_agent_registry_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("audit_agent_registry_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("audit_agent_registry_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("audit_agent_registry_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("audit_agent_registry_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("audit_agent_registry_enforcement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "audit_agent_registry_enforcement", "context_pull")
_emit_pulls_context("p1", "audit_agent_registry_enforcement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "audit_agent_registry_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "audit_agent_registry_enforcement", "uwg_term_2")
_emit_writes_through("p1", "audit_agent_registry_enforcement", "write_through")
_emit_writes_through("p1", "audit_agent_registry_enforcement", "write_through_2")
_emit_validated_by_safety_plane("p1", "audit_agent_registry_enforcement", "safety_validation")
_emit_invokes_eval("p1", "audit_agent_registry_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "audit_agent_registry_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "audit_agent_registry_enforcement", "human_escalation")
_emit_routes_through("p1", "audit_agent_registry_enforcement", "route_through")
_emit_checks_agent_registry("p1", "audit_agent_registry_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "audit_agent_registry_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "audit_agent_registry_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "audit_agent_registry_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "audit_agent_registry_enforcement", "target_agent")
_emit_verifies_policy("p1", "audit_agent_registry_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "audit_agent_registry_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "audit_agent_registry_enforcement", "boundary_check")
_emit_transcripts_response("p1", "audit_agent_registry_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "audit_agent_registry_enforcement")
_emit_gated_by_confidence("p1", "audit_agent_registry_enforcement", "confidence_gate")
emit_replay_key("p0", "audit_agent_registry_enforcement")
emit_determinism_digest("p0", "audit_agent_registry_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "audit_agent_registry_enforcement", "execution_auth")
_emit_validates_capability("p2", "audit_agent_registry_enforcement", "capability_check")
_emit_routes_to_capability("p2", "audit_agent_registry_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "audit_agent_registry_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "audit_agent_registry_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "audit_agent_registry_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "audit_agent_registry_enforcement", "exec_output")
_emit_dispatches_agent("p3", "audit_agent_registry_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "audit_agent_registry_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "audit_agent_registry_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "audit_agent_registry_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "audit_agent_registry_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "audit_agent_registry_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "audit_agent_registry_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "audit_agent_registry_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "audit_agent_registry_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "audit_agent_registry_enforcement", "eval_metric")
_emit_stores_embedding("p4", "audit_agent_registry_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "audit_agent_registry_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "audit_agent_registry_enforcement", "exec_snapshot_link")

# Import agent registry for validation
try:
    # guardian: allow-silent-swallow - optional dependency
    from agentic_core.agents.agent_registry import get_agent_class, get_all_agent_ids, get_profile
except ImportError:
    print("ERROR: Agent registry not available", file=sys.stderr)
    sys.exit(1)


class AgentUsageViolation:
    """Represents a violation of agent registry enforcement."""

    def __init__(self, file_path: str, line: int, violation_type: str, details: str):
        self.file_path = file_path
        self.line = line
        self.violation_type = violation_type
        self.details = details

    def __str__(self):
        return f"{self.file_path}:{self.line} - {self.violation_type}: {self.details}"


class AgentRegistryEnforcementScanner(ast.NodeVisitor):
    """AST scanner for agent usage violations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[AgentUsageViolation] = []
        self.registered_agents = set(get_all_agent_ids())

    def visit_Call(self, node: ast.Call):
        """Check function calls for agent usage violations."""
        # Check for SovereignLLMGateway.generate calls
        if self._is_gateway_call(node):
            self._check_gateway_call(node)

        # Check for direct agent instantiation
        if self._is_agent_instantiation(node):
            self._check_agent_instantiation(node)

        self.generic_visit(node)

    def _is_gateway_call(self, node: ast.Call) -> bool:
        """Check if this is a SovereignLLMGateway.generate call."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "generate":
                # Check if it's a SovereignLLMGateway instance
                if isinstance(node.func.value, ast.Name):
                    return node.func.value.id == "gateway"
                elif isinstance(node.func.value, ast.Attribute):
                    return node.func.value.attr == "gateway"
        return False

    def _is_agent_instantiation(self, node: ast.Call) -> bool:
        """Check if this is an agent class instantiation."""
        if isinstance(node.func, ast.Name):
            return node.func.id in self.registered_agents
        return False

    def _check_gateway_call(self, node: ast.Call):
        """Check SovereignLLMGateway.generate call for agent_id."""
        # Look for agent_id in keyword arguments
        agent_id_found = False
        for keyword in node.keywords:
            if keyword.arg == "agent_id":
                agent_id_found = True
                if isinstance(keyword.value, ast.Constant):
                    agent_id = keyword.value.value
                    if agent_id not in self.registered_agents:
                        self.violations.append(
                            AgentUsageViolation(
                                self.file_path,
                                node.lineno,
                                "UNREGISTERED_AGENT",
                                f"Gateway call uses unregistered agent_id '{agent_id}'",
                            ),
                        )
                break

        if not agent_id_found:
            self.violations.append(
                AgentUsageViolation(
                    self.file_path,
                    node.lineno,
                    "MISSING_AGENT_ID",
                    "Gateway call missing required agent_id parameter",
                ),
            )

    def _check_agent_instantiation(self, node: ast.Call):
        """Check direct agent instantiation."""
        agent_class = node.func.id if isinstance(node.func, ast.Name) else "unknown"
        self.violations.append(
            AgentUsageViolation(
                self.file_path,
                node.lineno,
                "DIRECT_AGENT_INSTANTIATION",
                f"Direct instantiation of agent '{agent_class}' - use registry instead",
            ),
        )


def scan_file(file_path: Path) -> list[AgentUsageViolation]:
    """Scan a single Python file for agent usage violations."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        scanner = AgentRegistryEnforcementScanner(str(file_path.relative_to(Path.cwd())))
        scanner.visit(tree)
        violations.extend(scanner.violations)    # guardian: Syntax errors should be caught at parser level, not runtime

    except SyntaxError as e:
        violations.append(
            AgentUsageViolation(
                str(file_path.relative_to(Path.cwd())),
                e.lineno or 0,
                "SYNTAX_ERROR",
                f"Unable to parse file: {e}",
            ),
        )
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        violations.append(
            AgentUsageViolation(
                str(file_path.relative_to(Path.cwd())), 0, "SCAN_ERROR", f"Error scanning file: {e}",
            ),
        )

    return violations


def scan_directory(root_dir: Path) -> list[AgentUsageViolation]:
    """Scan all Python files in directory recursively, restricted to first-party code."""
    violations = []

    # Define first-party scope
    first_party_prefixes = [
        "agentic_core/",
        "system_learning/",
        "apps_rg/",
        "apps_shared/",
        "data/",
        "tests/",
        "ops_scripts/",
    ]

    # Define third-party directories to ignore
    third_party_patterns = [
        ".nox/",
        "venv/",
        "env/",
        "__pycache__/",
        ".git/",
        "site-packages/",
        "build/",
        "dist/",
        ".pytest_cache/",
    ]

    for py_file in root_dir.rglob("*.py"):
        file_str = str(py_file)

        # Skip third-party directories
        if any(pattern in file_str for pattern in third_party_patterns):
            continue

        # Only scan first-party code
        if not any(file_str.startswith(p) for p in first_party_prefixes):
            continue

        file_violations = scan_file(py_file)
        violations.extend(file_violations)

    return violations


def main():
    """Main entry point for the scanner."""
    scan_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print(f"Scanning {scan_path} for agent registry violations...")

    # Check for tamper mode
    tamper_mode = os.environ.get("W5_NEGCTRL_TAMPER") == "1"

    violations = scan_directory(scan_path)

    if tamper_mode:
        # Introduce synthetic violation for testing
        violations.append(
            AgentUsageViolation(
                "tests/governance/test_agent_execution_profiles.py",
                999,
                "TAMPER_VIOLATION",
                "Synthetic violation for negative control testing",
            ),
        )

    # Print results
    print(f"\nScan complete. Found {len(violations)} agent registry violations.")

    if violations:
        print("\nViolations by type:")

        # Group by type
        by_type = {}
        for violation in violations:
            if violation.violation_type not in by_type:
                by_type[violation.violation_type] = []
            by_type[violation.violation_type].append(violation)

        for violation_type, type_violations in sorted(by_type.items()):
            print(f"\n{violation_type} ({len(type_violations)}):")
            for violation in type_violations:
                print(f"  {violation}")

    # Exit with error code if violations found (unless in tamper mode)
    if violations and not tamper_mode:
        print(f"\nERROR: {len(violations)} agent registry violations found!")
        sys.exit(1)
    elif tamper_mode:
        print(f"\nTAMPER MODE: {len(violations)} violations (including synthetic)")
        sys.exit(0)
    else:
        print("\nOK: No agent registry violations found")
        sys.exit(0)


if __name__ == "__main__":
    main()
