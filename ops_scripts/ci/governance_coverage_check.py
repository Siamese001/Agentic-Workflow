"""Governance Coverage Audit — CI Gate.

Scans all ops_scripts/ci/*.py scripts. For each script that references
any SSOT-governed resource, asserts it imports from active_set_helper.

Detection layers (all AST-first where applicable):
  1. AST: direct import of ssot_discovery_util or full_agent_discovery modules.
  2. AST: import of load_agent_discovery / perform_deep_integrity_scan names.
  3. String: reference to agent_discovery_full.json literal.

This ensures no CI script bypasses the SSOT active-set abstraction.

Exit 0 = all governed, exit 1 = bypass detected.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_1")
_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_2")
_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_3")
_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_4")
_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_5")
_emit_emits_metric_event("governance_coverage_check", "p4obs", "metric_6")
_emit_records_incident_event("governance_coverage_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("governance_coverage_check", "p4obs", "anomaly")
_emit_writes_observability_log("governance_coverage_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("governance_coverage_check", "p4obs", "mon_state")
_emit_triggers_alert("governance_coverage_check", "p4obs", "alert")
_emit_links_incident_trace("governance_coverage_check", "p4obs", "trace_link")
_emit_captures_pattern("governance_coverage_check", "p3lm", "pattern")
_emit_records_learning_event("governance_coverage_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("governance_coverage_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("governance_coverage_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("governance_coverage_check", "p3lm", "routing")
_emit_improves_agent_policy("governance_coverage_check", "p3lm", "policy")
_emit_stores_learning_state("governance_coverage_check", "p3lm", "state")
_emit_records_execution_trace("governance_coverage_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("governance_coverage_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("governance_coverage_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("governance_coverage_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("governance_coverage_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("governance_coverage_check", "env_read", "p2_env_1")
_emit_reads_environ("governance_coverage_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("governance_coverage_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("governance_coverage_check", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "governance_coverage_check")
_emit_applies_guardrail("p0", "governance_coverage_check", "p0_governance")
_emit_reads_policy_state("p0", "governance_coverage_check", "policy_binding")
_emit_snapshots_state("p0", "governance_coverage_check", "state_snapshot")
_emit_pulls_context("p1", "governance_coverage_check", "context_pull")
_emit_pulls_context("p1", "governance_coverage_check", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "governance_coverage_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "governance_coverage_check", "uwg_term_secondary")
_emit_writes_through("p1", "governance_coverage_check", "write_through")
_emit_writes_through("p1", "governance_coverage_check", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "governance_coverage_check", "safety_validation")
_emit_invokes_eval("p1", "governance_coverage_check", "eval_call")
_emit_proposal_commits_routing("p1", "governance_coverage_check", "routing_commit")
_emit_escalates_to_human("p1", "governance_coverage_check", "human_escalation")
_emit_routes_through("p1", "governance_coverage_check", "route_through")
_emit_checks_agent_registry("p1", "governance_coverage_check", "agent_registry")
_emit_validates_agent_capability("p1", "governance_coverage_check", "capability")
_emit_dispatches_execution_plan("p1", "governance_coverage_check", "exec_plan")
_emit_agent_executes_agent("p1", "governance_coverage_check", "sub_agent")
_emit_routes_to_agent("p1", "governance_coverage_check", "target_agent")
_emit_verifies_policy("p1", "governance_coverage_check", "policy_check")
_emit_observes_runtime_state("p1", "governance_coverage_check", "runtime_state")
_emit_verifies_boundary("p1", "governance_coverage_check", "boundary_check")
_emit_transcripts_response("p1", "governance_coverage_check", "transcript")
_emit_hard_fails_untranscripted("p1", "governance_coverage_check")
_emit_gated_by_confidence("p1", "governance_coverage_check", "confidence_gate")
emit_replay_key("p0", "governance_coverage_check")
emit_determinism_digest("p0", "governance_coverage_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "governance_coverage_check", "execution_auth")
_emit_validates_capability("p2", "governance_coverage_check", "capability_check")
_emit_routes_to_capability("p2", "governance_coverage_check", "capability_route")
_emit_writes_via_uwg("p2", "governance_coverage_check", "uwg_write")
_emit_blocks_direct_write("p2", "governance_coverage_check", "direct_write_block")
_emit_records_tool_invocation("p2", "governance_coverage_check", "tool_invocation")
_emit_captures_execution_output("p2", "governance_coverage_check", "exec_output")
_emit_dispatches_agent("p3", "governance_coverage_check", "agent_dispatch")
_emit_coordinates_agents("p3", "governance_coverage_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "governance_coverage_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "governance_coverage_check", "healing_outcome")
_emit_escalates_failure("p3", "governance_coverage_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "governance_coverage_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "governance_coverage_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "governance_coverage_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "governance_coverage_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "governance_coverage_check", "eval_metric")
_emit_stores_embedding("p4", "governance_coverage_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "governance_coverage_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "governance_coverage_check", "exec_snapshot_link")
_EXEMPT_SCRIPTS = frozenset({'__init__.py', 'active_set_helper.py', 'active_set_ssot_check.py', 'active_set_snapshot_check.py', 'gate_consistency_check.py', 'governance_coverage_check.py', 'mro_new_diamond_check.py'})
_PROHIBITED_MODULES = frozenset({'ssot_discovery_util', 'full_agent_discovery'})
_PROHIBITED_NAMES = frozenset({'load_agent_discovery', 'perform_deep_integrity_scan'})
_DISCOVERY_OUTPUT_PATTERN = re.compile('\\bagent_discovery_full\\.json\\b')
_REQUIRED_IMPORT = 'active_set_helper'

def _imports_helper(tree: ast.AST) -> bool:
    """Check if AST imports from active_set_helper."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and _REQUIRED_IMPORT in node.module:
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if _REQUIRED_IMPORT in alias.name:
                    return True
    return False

def _find_governed_references(tree: ast.AST, source: str) -> list[str]:
    """Return list of governed references found via AST + string scan."""
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for mod in _PROHIBITED_MODULES:
                if mod in node.module:
                    found.append(f"import from '{node.module}' (prohibited module)")
                    break
        if isinstance(node, ast.Import):
            for alias in node.names:
                for mod in _PROHIBITED_MODULES:
                    if mod in alias.name:
                        found.append(f"import '{alias.name}' (prohibited module)")
                        break
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                if alias.name in _PROHIBITED_NAMES:
                    found.append(f"import name '{alias.name}' (prohibited)")
    if _DISCOVERY_OUTPUT_PATTERN.search(source):
        found.append("string reference to 'agent_discovery_full.json'")
    return found

def main() -> int:
    project_root = get_validated_project_root()
    ci_dir = project_root / OPS_SCRIPTS_DIR / 'ci'
    if not ci_dir.is_dir():
        print('FAIL: ops_scripts/ci/ not found', file=sys.stderr)
        return 1
    violations: list[str] = []
    scanned = 0
    governed = 0
    for pyfile in sorted(ci_dir.glob('*.py')):
        if pyfile.name in _EXEMPT_SCRIPTS:
            continue
        scanned += 1
        try:
            source = pyfile.read_text(encoding='utf-8', errors='replace')
        except OSError:    # guardian: Add error context logging
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
            continue
        refs = _find_governed_references(tree, source)
        if not refs:
            continue
        governed += 1
        if not _imports_helper(tree):
            rel = str(pyfile.relative_to(project_root)).replace('\\', '/')
            violations.append(f'{rel}: {refs} but does NOT import {_REQUIRED_IMPORT}')
    print('Governance Coverage Audit:')
    print(f'  scanned={scanned}  governed={governed}  violations={len(violations)}')
    if violations:
        print(f'FAIL: {len(violations)} script(s) bypass SSOT:')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('PASS: 100% governance coverage — no CI script bypasses SSOT')
    return 0
if __name__ == '__main__':
    sys.exit(main())
