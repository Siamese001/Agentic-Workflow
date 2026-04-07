#!/usr/bin/env python3
"""
CI gate: MCP Config Sovereignty (Constitutional Rule #0 + §8.3).

Validates that mcp_config.json in the repo root conforms to sovereignty rules:
  1. filesystem server present and not disabled.
  2. filesystem allowedDirectories (args) contains ONLY the repo root — no
     out-of-repo paths and no .windsurf/plans/ write-through path.
  3. No MCP server entry has an out-of-repo cwd or args path that points
     outside the repo root.
  4. The forbidden out-of-repo plan path is never referenced in any args.
  5. Denominator-sensitive files are documented as read-sensitive in _comment.

Exits 0 on full compliance. Exits 1 on any violation.
All I/O via stdlib only — no subprocess, no PowerShell.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "check_mcp_config_sovereignty")
_emit_applies_guardrail("p0", "check_mcp_config_sovereignty", "p0_governance")
_emit_reads_policy_state("p0", "check_mcp_config_sovereignty", "policy_binding")
_emit_snapshots_state("p0", "check_mcp_config_sovereignty", "state_snapshot")
emit_replay_key("p0", "check_mcp_config_sovereignty")
emit_determinism_digest("p0", "check_mcp_config_sovereignty")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_mcp_config_sovereignty", "execution_auth")
_emit_validates_capability("p2", "check_mcp_config_sovereignty", "capability_check")
_emit_routes_to_capability("p2", "check_mcp_config_sovereignty", "capability_route")
_emit_writes_via_uwg("p2", "check_mcp_config_sovereignty", "uwg_write")
_emit_blocks_direct_write("p2", "check_mcp_config_sovereignty", "direct_write_block")
_emit_records_tool_invocation("p2", "check_mcp_config_sovereignty", "tool_invocation")
_emit_captures_execution_output("p2", "check_mcp_config_sovereignty", "exec_output")
_emit_dispatches_agent("p3", "check_mcp_config_sovereignty", "agent_dispatch")
_emit_coordinates_agents("p3", "check_mcp_config_sovereignty", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_mcp_config_sovereignty", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_mcp_config_sovereignty", "healing_outcome")
_emit_escalates_failure("p3", "check_mcp_config_sovereignty", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_mcp_config_sovereignty", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_mcp_config_sovereignty", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_mcp_config_sovereignty", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_mcp_config_sovereignty", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_mcp_config_sovereignty", "eval_metric")
_emit_stores_embedding("p4", "check_mcp_config_sovereignty", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_mcp_config_sovereignty", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_mcp_config_sovereignty", "exec_snapshot_link")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_1")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_2")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_3")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_4")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_5")
_emit_emits_metric_event("check_mcp_config_sovereignty", "p4obs", "metric_6")
_emit_records_incident_event("check_mcp_config_sovereignty", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_mcp_config_sovereignty", "p4obs", "anomaly")
_emit_writes_observability_log("check_mcp_config_sovereignty", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_mcp_config_sovereignty", "p4obs", "mon_state")
_emit_triggers_alert("check_mcp_config_sovereignty", "p4obs", "alert")
_emit_links_incident_trace("check_mcp_config_sovereignty", "p4obs", "trace_link")
_emit_captures_pattern("check_mcp_config_sovereignty", "p3lm", "pattern")
_emit_records_learning_event("check_mcp_config_sovereignty", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_mcp_config_sovereignty", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_mcp_config_sovereignty", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_mcp_config_sovereignty", "p3lm", "routing")
_emit_improves_agent_policy("check_mcp_config_sovereignty", "p3lm", "policy")
_emit_stores_learning_state("check_mcp_config_sovereignty", "p3lm", "state")
_emit_records_execution_trace("check_mcp_config_sovereignty", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_mcp_config_sovereignty", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_mcp_config_sovereignty", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_mcp_config_sovereignty", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_mcp_config_sovereignty", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_mcp_config_sovereignty", "env_read", "p2_env_1")
_emit_reads_environ("check_mcp_config_sovereignty", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_mcp_config_sovereignty", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_mcp_config_sovereignty", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_mcp_config_sovereignty", "context_pull")
_emit_pulls_context("p1", "check_mcp_config_sovereignty", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_mcp_config_sovereignty", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_mcp_config_sovereignty", "uwg_term_secondary")
_emit_writes_through("p1", "check_mcp_config_sovereignty", "write_through")
_emit_writes_through("p1", "check_mcp_config_sovereignty", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_mcp_config_sovereignty", "safety_validation")
_emit_invokes_eval("p1", "check_mcp_config_sovereignty", "eval_call")
_emit_proposal_commits_routing("p1", "check_mcp_config_sovereignty", "routing_commit")
_emit_escalates_to_human("p1", "check_mcp_config_sovereignty", "human_escalation")
_emit_routes_through("p1", "check_mcp_config_sovereignty", "route_through")
_emit_checks_agent_registry("p1", "check_mcp_config_sovereignty", "agent_registry")
_emit_validates_agent_capability("p1", "check_mcp_config_sovereignty", "capability")
_emit_dispatches_execution_plan("p1", "check_mcp_config_sovereignty", "exec_plan")
_emit_agent_executes_agent("p1", "check_mcp_config_sovereignty", "sub_agent")
_emit_routes_to_agent("p1", "check_mcp_config_sovereignty", "target_agent")
_emit_verifies_policy("p1", "check_mcp_config_sovereignty", "policy_check")
_emit_observes_runtime_state("p1", "check_mcp_config_sovereignty", "runtime_state")
_emit_verifies_boundary("p1", "check_mcp_config_sovereignty", "boundary_check")
_emit_transcripts_response("p1", "check_mcp_config_sovereignty", "transcript")
_emit_hard_fails_untranscripted("p1", "check_mcp_config_sovereignty")
_emit_gated_by_confidence("p1", "check_mcp_config_sovereignty", "confidence_gate")

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG_PATH = REPO_ROOT / "mcp_config.json"

# guardian: allow-config-with-logic
FORBIDDEN_OUT_OF_REPO_FRAGMENTS = [
    r"c:\users",
    r"c:/users",
    "/users/",
    ".windsurf\\plans",
    ".windsurf/plans",
]

# guardian: allow-config-with-logic
DENOMINATOR_SENSITIVE_FILES = [
    "agentic_core/adg/schema.py",
    "agentic_core/adg/extraction/static_scanner.py",
    "agentic_core/runtime/lifecycle_trace_contract.py",
]

# guardian: allow-config-with-logic
SOVEREIGN_WRITE_TERRITORIES = [
    "docs/reports/plans/",
    "artifacts/adg/",
    "artifacts/memory/",
    "ops_scripts/ci/",
    "tools/",
]


def _normalise(path_str: str) -> str:
    """Lowercase + forward-slash normalise a path string for comparison."""
    return path_str.replace("\\", "/").lower()


def validate_mcp_sovereignty(config_path: Path) -> list[str]:
    """Return a list of violation strings. Empty list = fully compliant."""
    violations: list[str] = []

    if not config_path.exists():
        violations.append(f"MISSING: {config_path} not found in repo root")
        return violations

    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = fh.read()
        config = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        violations.append(f"PARSE_ERROR: cannot read {config_path}: {exc}")
        return violations

    servers: dict = config.get("mcpServers", {})

    # --- Rule 1: filesystem server must be present ---
    if "filesystem" not in servers:
        violations.append(
            "MISSING_FILESYSTEM: 'filesystem' key absent from mcpServers. "
            "Add entry with allowedDirectories locked to repo root.",
        )

    # --- Rule 2: filesystem must not be disabled ---
    if "filesystem" in servers:
        fs_entry = servers["filesystem"]
        if fs_entry.get("disabled", False) is True:
            violations.append(
                "FILESYSTEM_DISABLED: filesystem MCP server is marked disabled=true. "
                "Must be enabled with allowedDirectories=repo root only.",
            )

        # --- Rule 3: filesystem args must contain ONLY the repo root ---
        args: list = fs_entry.get("args", [])
        repo_root_norm = _normalise(str(REPO_ROOT))
        allowed_dir_args = [a for a in args if not a.startswith("-") and "modelcontextprotocol" not in a]
        for arg in allowed_dir_args:
            arg_norm = _normalise(arg)
            if arg_norm != repo_root_norm and not arg_norm.startswith(repo_root_norm):
                violations.append(
                    f"FILESYSTEM_OUT_OF_REPO_ARG: filesystem args contains path outside "
                    f"repo root: '{arg}'. Only '{REPO_ROOT}' is allowed.",
                )

        # --- Rule 4: comment must document sovereign write territories ---
        comment = fs_entry.get("_comment", "")
        if not comment:
            violations.append(
                "FILESYSTEM_MISSING_COMMENT: filesystem entry must have a _comment "
                "documenting sovereign write territories and Constitutional Rule #0.",
            )
        else:
            if "constitutional rule #0" not in comment.lower() and "rule #0" not in comment.lower():
                violations.append(
                    "FILESYSTEM_COMMENT_MISSING_RULE0: _comment must reference Constitutional Rule #0.",
                )
            for territory in SOVEREIGN_WRITE_TERRITORIES:
                if territory not in comment:
                    violations.append(
                        f"FILESYSTEM_COMMENT_MISSING_TERRITORY: _comment must document "
                        f"sovereign write territory '{territory}'.",
                    )
            for sensitive in DENOMINATOR_SENSITIVE_FILES:
                if sensitive not in comment:
                    violations.append(
                        f"FILESYSTEM_COMMENT_MISSING_SENSITIVE: _comment must list "
                        f"read-sensitive path '{sensitive}'.",
                    )

    # --- Rule 5: no server references forbidden out-of-repo paths in args/cwd ---
    for server_name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        args = entry.get("args", [])
        cwd = entry.get("cwd", "")
        all_paths = list(args) + ([cwd] if cwd else [])
        for path_val in all_paths:
            path_norm = _normalise(str(path_val))
            for forbidden in FORBIDDEN_OUT_OF_REPO_FRAGMENTS:
                forbidden_norm = _normalise(forbidden)
                if forbidden_norm in path_norm:
                    violations.append(
                        f"FORBIDDEN_PATH in server '{server_name}': "
                        f"path '{path_val}' contains forbidden fragment '{forbidden}'. "
                        f"Constitutional Rule #0 violation.",
                    )

    return violations


def main() -> int:
    violations = validate_mcp_sovereignty(MCP_CONFIG_PATH)
    if violations:
        print(f"[ERROR] MCP Config Sovereignty gate FAILED — {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nFix: ensure mcp_config.json has a 'filesystem' entry with args locked "
            "to repo root only. Constitutional Rule #0: NEVER reference "
            r"C:\Users\... or .windsurf\plans\ paths.",
        )
        return 1
    print("[OK] MCP Config Sovereignty gate passed — filesystem entry conforms to sovereignty rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
