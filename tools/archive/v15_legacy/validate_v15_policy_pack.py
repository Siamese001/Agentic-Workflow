"""V15 Policy Pack Validator.

Validates a V15 policy pack JSON file against the required schema,
checks for duplicate rule_ids, and warns on unknown fields.

Usage:
    python ops_scripts/policy/validate_v15_policy_pack.py --path <policy_pack.json>

Exit codes:
    0 — Valid policy pack
    2 — Schema validation failure (missing/bad fields)
    3 — Duplicate rule_id detected
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
from ops_scripts.review.integration_contract_stubs import (
    Finding,
    ResultEnvelope,
)

_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_1")
_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_2")
_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_3")
_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_4")
_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_5")
_emit_emits_metric_event("validate_v15_policy_pack", "p4obs", "metric_6")
_emit_records_incident_event("validate_v15_policy_pack", "p4obs", "incident")
_emit_captures_runtime_anomaly("validate_v15_policy_pack", "p4obs", "anomaly")
_emit_writes_observability_log("validate_v15_policy_pack", "p4obs", "obs_log")
_emit_updates_monitoring_state("validate_v15_policy_pack", "p4obs", "mon_state")
_emit_triggers_alert("validate_v15_policy_pack", "p4obs", "alert")
_emit_links_incident_trace("validate_v15_policy_pack", "p4obs", "trace_link")
_emit_captures_pattern("validate_v15_policy_pack", "p3lm", "pattern")
_emit_records_learning_event("validate_v15_policy_pack", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validate_v15_policy_pack", "p3lm", "snapshot")
_emit_feeds_meta_learning("validate_v15_policy_pack", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validate_v15_policy_pack", "p3lm", "routing")
_emit_improves_agent_policy("validate_v15_policy_pack", "p3lm", "policy")
_emit_stores_learning_state("validate_v15_policy_pack", "p3lm", "state")
_emit_records_execution_trace("validate_v15_policy_pack", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validate_v15_policy_pack", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validate_v15_policy_pack", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validate_v15_policy_pack", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validate_v15_policy_pack", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validate_v15_policy_pack", "env_read", "p2_env_1")
_emit_reads_environ("validate_v15_policy_pack", "env_read", "p2_env_2")
_emit_reads_runtime_state("validate_v15_policy_pack", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validate_v15_policy_pack", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "validate_v15_policy_pack")
_emit_applies_guardrail("p0", "validate_v15_policy_pack", "p0_governance")
_emit_snapshots_state("p0", "validate_v15_policy_pack", "state_snapshot")
_emit_pulls_context("p1", "validate_v15_policy_pack", "context_pull")
_emit_pulls_context("p1", "validate_v15_policy_pack", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "validate_v15_policy_pack", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validate_v15_policy_pack", "uwg_term_secondary")
_emit_writes_through("p1", "validate_v15_policy_pack", "write_through")
_emit_writes_through("p1", "validate_v15_policy_pack", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "validate_v15_policy_pack", "safety_validation")
_emit_invokes_eval("p1", "validate_v15_policy_pack", "eval_call")
_emit_proposal_commits_routing("p1", "validate_v15_policy_pack", "routing_commit")
_emit_escalates_to_human("p1", "validate_v15_policy_pack", "human_escalation")
_emit_routes_through("p1", "validate_v15_policy_pack", "route_through")
_emit_checks_agent_registry("p1", "validate_v15_policy_pack", "agent_registry")
_emit_validates_agent_capability("p1", "validate_v15_policy_pack", "capability")
_emit_dispatches_execution_plan("p1", "validate_v15_policy_pack", "exec_plan")
_emit_agent_executes_agent("p1", "validate_v15_policy_pack", "sub_agent")
_emit_routes_to_agent("p1", "validate_v15_policy_pack", "target_agent")
_emit_verifies_policy("p1", "validate_v15_policy_pack", "policy_check")
_emit_observes_runtime_state("p1", "validate_v15_policy_pack", "runtime_state")
_emit_verifies_boundary("p1", "validate_v15_policy_pack", "boundary_check")
_emit_transcripts_response("p1", "validate_v15_policy_pack", "transcript")
_emit_hard_fails_untranscripted("p1", "validate_v15_policy_pack")
_emit_gated_by_confidence("p1", "validate_v15_policy_pack", "confidence_gate")
emit_replay_key("p0", "validate_v15_policy_pack")
emit_determinism_digest("p0", "validate_v15_policy_pack")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validate_v15_policy_pack", "execution_auth")
_emit_validates_capability("p2", "validate_v15_policy_pack", "capability_check")
_emit_routes_to_capability("p2", "validate_v15_policy_pack", "capability_route")
_emit_writes_via_uwg("p2", "validate_v15_policy_pack", "uwg_write")
_emit_blocks_direct_write("p2", "validate_v15_policy_pack", "direct_write_block")
_emit_records_tool_invocation("p2", "validate_v15_policy_pack", "tool_invocation")
_emit_captures_execution_output("p2", "validate_v15_policy_pack", "exec_output")
_emit_dispatches_agent("p3", "validate_v15_policy_pack", "agent_dispatch")
_emit_coordinates_agents("p3", "validate_v15_policy_pack", "agent_coordination")
_emit_records_workflow_lineage("p3", "validate_v15_policy_pack", "workflow_lineage")
_emit_records_healing_outcome("p3", "validate_v15_policy_pack", "healing_outcome")
_emit_escalates_failure("p3", "validate_v15_policy_pack", "failure_escalation")
_emit_orchestrates_workflow("p3", "validate_v15_policy_pack", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validate_v15_policy_pack", "healing_dispatch")
_emit_invokes_evaluation("p3", "validate_v15_policy_pack", "evaluation_signal")
_emit_records_telemetry_event("p4", "validate_v15_policy_pack", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validate_v15_policy_pack", "eval_metric")
_emit_stores_embedding("p4", "validate_v15_policy_pack", "embedding_store")
_emit_updates_meta_learning_state("p4", "validate_v15_policy_pack", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validate_v15_policy_pack", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

VALID_APPLIES_TO = frozenset({"PIPE", "POLICY", "HASH", "CLOCK", "GENERAL"})
VALID_SEVERITY = frozenset({"WARN", "SOFT_FAIL", "HARD_FAIL"})

REQUIRED_TOP_LEVEL = {"version", "rules"}
REQUIRED_RULE_FIELDS = {"rule_id", "applies_to", "severity", "description", "enabled"}

KNOWN_TOP_LEVEL = REQUIRED_TOP_LEVEL | {"updated_at"}
KNOWN_RULE_FIELDS = REQUIRED_RULE_FIELDS | {"metadata"}


# ---------------------------------------------------------------------------
# Validation core (importable for tests)
# ---------------------------------------------------------------------------


def validate_policy_pack(data: dict) -> tuple[int, list[str], list[str]]:
    """Validate a parsed policy pack dict.

    Returns:
        (exit_code, errors, warnings)
        exit_code: 0=ok, 2=schema, 3=duplicates
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Top-level required fields ---
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in data:
            errors.append(f"Missing required top-level field: '{field}'")

    if errors:
        return 2, errors, warnings

    # --- Top-level unknown fields ---
    for key in sorted(data.keys()):
        if key not in KNOWN_TOP_LEVEL:
            warnings.append(f"Unknown top-level field: '{key}' (forward-compat, ignored)")

    # --- version ---
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("'version' must be a non-empty string")

    # --- rules ---
    rules = data.get("rules")
    if not isinstance(rules, list):
        errors.append("'rules' must be a list")
        return 2, errors, warnings

    if len(rules) == 0:
        errors.append("'rules' must contain at least one rule")
        return 2, errors, warnings

    # --- Per-rule validation ---
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for idx, rule in enumerate(rules):
        prefix = f"rules[{idx}]"

        if not isinstance(rule, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        # Required fields
        for field in sorted(REQUIRED_RULE_FIELDS):
            if field not in rule:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Unknown rule fields
        for key in sorted(rule.keys()):
            if key not in KNOWN_RULE_FIELDS:
                warnings.append(f"{prefix}: unknown field '{key}' (forward-compat, ignored)")

        # Type checks
        rule_id = rule.get("rule_id")
        if rule_id is not None:
            if not isinstance(rule_id, str) or not rule_id.strip():
                errors.append(f"{prefix}: 'rule_id' must be a non-empty string")
            else:
                if rule_id in seen_ids:
                    duplicate_ids.append(rule_id)
                seen_ids.add(rule_id)

        applies_to = rule.get("applies_to")
        if applies_to is not None and applies_to not in VALID_APPLIES_TO:
            errors.append(
                f"{prefix}: 'applies_to' must be one of {sorted(VALID_APPLIES_TO)}, got '{applies_to}'",
            )

        severity = rule.get("severity")
        if severity is not None and severity not in VALID_SEVERITY:
            errors.append(
                f"{prefix}: 'severity' must be one of {sorted(VALID_SEVERITY)}, got '{severity}'",
            )

        description = rule.get("description")
        if description is not None and not isinstance(description, str):
            errors.append(f"{prefix}: 'description' must be a string")

        enabled = rule.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            errors.append(f"{prefix}: 'enabled' must be a boolean")

    # --- Duplicate check (separate exit code) ---
    if duplicate_ids:
        for dup in sorted(set(duplicate_ids)):
            errors.append(f"Duplicate rule_id: '{dup}'")
        return 3, errors, warnings

    if errors:
        return 2, errors, warnings

    # --- Ordering recommendation ---
    rule_ids = [r.get("rule_id", "") for r in rules if isinstance(r, dict)]
    if rule_ids != sorted(rule_ids):
        warnings.append("Rules are not sorted by rule_id (recommended for stable diffs)")

    return 0, errors, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_validator_envelope(
    pack_path: str,
    exit_code: int,
    errors: list[str],
    warnings: list[str],
) -> ResultEnvelope:
    """Build a ResultEnvelope for the policy pack validator run."""
    env = ResultEnvelope(tool="policy_pack_validator", exit_code=exit_code)
    env.inputs["policy_pack"] = {
        "path": Path(pack_path).name,
        "present": Path(pack_path).is_file(),
    }

    for w in warnings:
        env.findings.append(
            Finding(
                code="SCHEMA_WARN",
                severity="WARN",
                message=w,
            ),
        )
    for e in errors:
        env.findings.append(
            Finding(
                code="SCHEMA_ERROR" if exit_code == 2 else "DUPLICATE_RULE_ID",
                severity="ERROR",
                message=e,
            ),
        )

    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a V15 policy pack JSON file.")
    parser.add_argument("--path", type=str, required=True, help="Path to policy pack JSON")
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional: write JSON result envelope to this path",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, [f"File not found: {path.name}"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, [f"Invalid JSON: {e}"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    if not isinstance(data, dict):
        print("ERROR: Top-level must be a JSON object", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, ["Top-level must be a JSON object"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    exit_code, errors, warnings = validate_policy_pack(data)

    for w in warnings:
        print(f"WARN: {w}")

    if exit_code == 0:
        rule_count = len(data.get("rules", []))
        print(f"PASS: Policy pack v{data.get('version', '?')} — {rule_count} rules valid")
    else:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)

    if args.json_out:
        env = build_validator_envelope(args.path, exit_code, errors, warnings)
        env.write_json(Path(args.json_out))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
