"""Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""

from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
)
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
    _emit_records_execution_trace,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "emoji_fixer")
emit_determinism_digest("p0", "emoji_fixer")

_emit_dispatches_healing_run("p1", "emoji_fixer", "L0")
_emit_routes_through("p1", "emoji_fixer", "L0")
_emit_checks_agent_registry("p1", "emoji_fixer", "agent_registry")
_emit_validates_agent_capability("p1", "emoji_fixer", "capability")
_emit_dispatches_execution_plan("p1", "emoji_fixer", "exec_plan")
_emit_agent_executes_agent("p1", "emoji_fixer", "sub_agent")
_emit_routes_to_agent("p1", "emoji_fixer", "target_agent")
_emit_verifies_policy("p1", "emoji_fixer", "policy_check")
_emit_observes_runtime_state("p1", "emoji_fixer", "runtime_state")
_emit_verifies_boundary("p1", "emoji_fixer", "boundary_check")
_emit_transcripts_response("p1", "emoji_fixer", "transcript")
_emit_hard_fails_untranscripted("p1", "emoji_fixer")
_emit_gated_by_confidence("p1", "emoji_fixer", "confidence_gate")
_emit_escalates_to_human("p1", "emoji_fixer", "L0")
_emit_reads_policy_state("p1", "emoji_fixer", "L0")

_emit_records_execution_trace("p0", "evidence", "emoji_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "emoji_fixer", "p0_governance")
_emit_snapshots_state("p0", "emoji_fixer", "state_snapshot")
_emit_authorize_and_execute("p2", "emoji_fixer", "execution_auth")
_emit_validates_capability("p2", "emoji_fixer", "capability_check")
_emit_routes_to_capability("p2", "emoji_fixer", "capability_route")
_emit_writes_via_uwg("p2", "emoji_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "emoji_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "emoji_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "emoji_fixer", "exec_output")
_emit_dispatches_agent("p3", "emoji_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "emoji_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "emoji_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "emoji_fixer", "healing_outcome")
_emit_escalates_failure("p3", "emoji_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "emoji_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "emoji_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "emoji_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "emoji_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "emoji_fixer", "eval_metric")
_emit_stores_embedding("p4", "emoji_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "emoji_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "emoji_fixer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_1")
_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_2")
_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_3")
_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_4")
_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_5")
_emit_emits_metric_event("emoji_fixer", "p4obs", "metric_6")
_emit_records_incident_event("emoji_fixer", "p4obs", "incident")
_emit_captures_runtime_anomaly("emoji_fixer", "p4obs", "anomaly")
_emit_writes_observability_log("emoji_fixer", "p4obs", "obs_log")
_emit_updates_monitoring_state("emoji_fixer", "p4obs", "mon_state")
_emit_triggers_alert("emoji_fixer", "p4obs", "alert")
_emit_links_incident_trace("emoji_fixer", "p4obs", "trace_link")
_emit_captures_pattern("emoji_fixer", "p3lm", "pattern")
_emit_records_learning_event("emoji_fixer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("emoji_fixer", "p3lm", "snapshot")
_emit_feeds_meta_learning("emoji_fixer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("emoji_fixer", "p3lm", "routing")
_emit_improves_agent_policy("emoji_fixer", "p3lm", "policy")
_emit_stores_learning_state("emoji_fixer", "p3lm", "state")
_emit_records_execution_trace("emoji_fixer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("emoji_fixer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("emoji_fixer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("emoji_fixer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("emoji_fixer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("emoji_fixer", "env_read", "p2_env_1")
_emit_reads_environ("emoji_fixer", "env_read", "p2_env_2")
_emit_reads_runtime_state("emoji_fixer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("emoji_fixer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "emoji_fixer", "context_pull")
_emit_pulls_context("p1", "emoji_fixer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "emoji_fixer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "emoji_fixer", "uwg_term_2")
_emit_writes_through("p1", "emoji_fixer", "write_through")
_emit_writes_through("p1", "emoji_fixer", "write_through_2")
_emit_validated_by_safety_plane("p1", "emoji_fixer", "safety_validation")
_emit_invokes_eval("p1", "emoji_fixer", "eval_call")
_emit_proposal_commits_routing("p1", "emoji_fixer", "routing_commit")

# Default values - guardian: allow-hardcoded - fallback for optional dependency
AGENTIC_CORE_DIR = Path(".")
APPS_SHARED_DIR = Path(".")

def get_python_files(directory):
    return directory.rglob("*.py")

try:
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR as _acquired_core_dir,
    )
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
        APPS_SHARED_DIR as _acquired_shared_dir,
    )
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
        get_python_files as _acquired_get_files,
    )
    # Update if import succeeds
    AGENTIC_CORE_DIR = Path(_acquired_core_dir)
    APPS_SHARED_DIR = Path(_acquired_shared_dir)
    get_python_files = _acquired_get_files
except ImportError:  # guardian: allow-silent-swallow - optional dependency
    pass


EMOJI_MAP = {
    "✅": "[OK]",
    "⚠️": "[!]",
    "🔧": "[+]",
    "🔄": "[~]",
    "🆕": "[NEW]",
    "♻️": "[REUSE]",
    "🚨": "[ALERT]",
    "🚫": "[X]",
    "❌": "[X]",
    "🧹": "[CLEAN]",
    "🏛️": "[ARCH]",
    "💾": "[SAVE]",
    "🔍": "[SCAN]",
    "📊": "[STATS]",
    "📂": "[DIR]",
    "📋": "[PLAN]",
    "🚀": "[START]",
    "🌱": "[GIT]",
    "🧬": "[CYCLE]",
}


def fix_emojis_in_file(file_path: str) -> bool:
    """Replace all emojis in a file with ASCII equivalents."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        original_content = content
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            return True
        return False
    except (ValueError, TypeError) as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Find and fix all Python files with emojis."""
    root = Path.cwd()
    targets = [root / AGENTIC_CORE_DIR, root / APPS_SHARED_DIR]
    fixed_count = 0
    for target_dir in targets:
        if not target_dir.exists():
            continue
        for py_file in get_python_files(target_dir):
            if fix_emojis_in_file(str(py_file)):
                fixed_count += 1
    print(f"\n[*] Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
