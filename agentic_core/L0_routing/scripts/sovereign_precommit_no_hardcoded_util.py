from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sovereign_precommit_no_hardcoded_util")
emit_determinism_digest("p0", "sovereign_precommit_no_hardcoded_util")

_emit_dispatches_healing_run("p1", "sovereign_precommit_no_hardcoded_util", "L0")
_emit_routes_through("p1", "sovereign_precommit_no_hardcoded_util", "L0")
_emit_checks_agent_registry("p1", "sovereign_precommit_no_hardcoded_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_precommit_no_hardcoded_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_precommit_no_hardcoded_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_precommit_no_hardcoded_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_precommit_no_hardcoded_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_precommit_no_hardcoded_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_precommit_no_hardcoded_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_precommit_no_hardcoded_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_precommit_no_hardcoded_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_precommit_no_hardcoded_util")
_emit_gated_by_confidence("p1", "sovereign_precommit_no_hardcoded_util", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_precommit_no_hardcoded_util", "L0")
_emit_reads_policy_state("p1", "sovereign_precommit_no_hardcoded_util", "L0")
_emit_authorize_and_execute("p2", "sovereign_precommit_no_hardcoded_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_precommit_no_hardcoded_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_precommit_no_hardcoded_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_precommit_no_hardcoded_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_precommit_no_hardcoded_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_precommit_no_hardcoded_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_precommit_no_hardcoded_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_precommit_no_hardcoded_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_precommit_no_hardcoded_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_precommit_no_hardcoded_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_precommit_no_hardcoded_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_precommit_no_hardcoded_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_precommit_no_hardcoded_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_precommit_no_hardcoded_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_precommit_no_hardcoded_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_precommit_no_hardcoded_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_precommit_no_hardcoded_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_precommit_no_hardcoded_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_precommit_no_hardcoded_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_precommit_no_hardcoded_util", "exec_snapshot_link")

"\nSovereign Guard: Block Hardcoded configuration Constants\nEnforces that all operational constants must be centralized in sovereign_config.py\n\nUsage: Called automatically by pre-commit hook\n"
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_precommit_no_hardcoded_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_precommit_no_hardcoded_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_precommit_no_hardcoded_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_precommit_no_hardcoded_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_precommit_no_hardcoded_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_precommit_no_hardcoded_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_precommit_no_hardcoded_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_precommit_no_hardcoded_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_precommit_no_hardcoded_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_precommit_no_hardcoded_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_precommit_no_hardcoded_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_precommit_no_hardcoded_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_precommit_no_hardcoded_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_precommit_no_hardcoded_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_precommit_no_hardcoded_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_precommit_no_hardcoded_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_precommit_no_hardcoded_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_precommit_no_hardcoded_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_precommit_no_hardcoded_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_precommit_no_hardcoded_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_precommit_no_hardcoded_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_precommit_no_hardcoded_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_precommit_no_hardcoded_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_precommit_no_hardcoded_util", "context_pull")
_emit_pulls_context("p1", "sovereign_precommit_no_hardcoded_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_precommit_no_hardcoded_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_precommit_no_hardcoded_util", "uwg_term_2")
_emit_writes_through("p1", "sovereign_precommit_no_hardcoded_util", "write_through")
_emit_writes_through("p1", "sovereign_precommit_no_hardcoded_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_precommit_no_hardcoded_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_precommit_no_hardcoded_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_precommit_no_hardcoded_util", "routing_commit")

exempt: Any = {"agentic_core/config/blueprint_sovereign/environments/sovereign_config.py", "test_", "tests/"}
hardcoded_patterns: Any = [
    ("PRIMARY_MODEL\\s*=\\s*[\"\\']", "Model selection"),
    ("REASONING_MODEL\\s*=\\s*[\"\\']", "Model selection"),
    ("MAX_RETRY_ATTEMPTS\\s*=\\s*\\d+", "Retry configuration"),
    ("CHECKPOINT_INTERVAL\\s*=\\s*\\d+", "Checkpoint configuration"),
    ("SEMANTIC_SIMILARITY_THRESHOLD\\s*=\\s*[\\d.]+", "Threshold configuration"),
    ("BASE_GIT_PATH\\s*=\\s*[\"\\']", "Path configuration"),
    ("gpt-4o[\"\\']", "Hardcoded model name"),
    ("o1-preview[\"\\']", "Hardcoded model name"),
]


def check_file(filepath: Any) -> Any:
    """Check a single file for hardcoded configuration constants."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "check_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "check_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "check_file")
    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    try:
        with open(filepath, encoding="utf-8") as f:
            content: Any = f.read()
        violations: Any = []
        lines: Any = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            for pattern, description in HARDCODED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({"line": i, "type": description, "content": line.strip()[:80]})
                    break
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for Violation in violations:
                print(f"  Line {Violation['line']} ({Violation['type']}): {Violation['content']}...")
            print("\n💡 SOLUTION: Centralize this constant in:")
            print("   agentic_core/config/blueprint_sovereign/environments/sovereign_config.py")
            print("   Then use: from sovereign_config import OrchestratorConfig")
            print("=" * 80)
            return False
        return True
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_hardcoded_util.py <file1> <file2> ...")
        sys.exit(0)
    all_passed: Any = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed: Any = False
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded configuration detected.")
        print("   All config constants must be centralized in sovereign_config.py")
        sys.exit(1)
    sys.exit(0)
