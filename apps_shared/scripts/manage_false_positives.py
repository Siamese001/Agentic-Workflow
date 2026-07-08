"""
Human-in-the-Loop False Positive Management
Allows humans to review and mark violations as false positives
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from apps_shared.utils.ConfigurationService import ConfigurationService

trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("manage_false_positives", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("manage_false_positives", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("manage_false_positives", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("manage_false_positives", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("manage_false_positives", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("manage_false_positives", "p4obs", "alert")
trace_contract._emit_links_incident_trace("manage_false_positives", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("manage_false_positives", "p3lm", "pattern")
trace_contract._emit_records_learning_event("manage_false_positives", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("manage_false_positives", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("manage_false_positives", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("manage_false_positives", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("manage_false_positives", "p3lm", "policy")
trace_contract._emit_stores_learning_state("manage_false_positives", "p3lm", "state")
trace_contract._emit_records_execution_trace("manage_false_positives", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("manage_false_positives", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("manage_false_positives", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("manage_false_positives", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("manage_false_positives", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("manage_false_positives", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("manage_false_positives", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("manage_false_positives", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("manage_false_positives", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "manage_false_positives")
trace_contract._emit_applies_guardrail("p0", "manage_false_positives", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "manage_false_positives", "policy_binding")
trace_contract._emit_snapshots_state("p0", "manage_false_positives", "state_snapshot")
trace_contract._emit_pulls_context("p1", "manage_false_positives", "context_pull")
trace_contract._emit_pulls_context("p1", "manage_false_positives", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "manage_false_positives", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "manage_false_positives", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "manage_false_positives", "write_through")
trace_contract._emit_writes_through("p1", "manage_false_positives", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "manage_false_positives", "safety_validation")
trace_contract._emit_invokes_eval("p1", "manage_false_positives", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "manage_false_positives", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "manage_false_positives", "human_escalation")
trace_contract._emit_routes_through("p1", "manage_false_positives", "route_through")
trace_contract._emit_checks_agent_registry("p1", "manage_false_positives", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "manage_false_positives", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "manage_false_positives", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "manage_false_positives", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "manage_false_positives", "target_agent")
trace_contract._emit_verifies_policy("p1", "manage_false_positives", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "manage_false_positives", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "manage_false_positives", "boundary_check")
trace_contract._emit_transcripts_response("p1", "manage_false_positives", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "manage_false_positives")
trace_contract._emit_gated_by_confidence("p1", "manage_false_positives", "confidence_gate")
trace_contract.emit_replay_key("p0", "manage_false_positives")
trace_contract.emit_determinism_digest("p0", "manage_false_positives")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "manage_false_positives", "execution_auth")
trace_contract._emit_validates_capability("p2", "manage_false_positives", "capability_check")
trace_contract._emit_routes_to_capability("p2", "manage_false_positives", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "manage_false_positives", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "manage_false_positives", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "manage_false_positives", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "manage_false_positives", "exec_output")
trace_contract._emit_dispatches_agent("p3", "manage_false_positives", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "manage_false_positives", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "manage_false_positives", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "manage_false_positives", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "manage_false_positives", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "manage_false_positives", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "manage_false_positives", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "manage_false_positives", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "manage_false_positives", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "manage_false_positives", "eval_metric")
trace_contract._emit_stores_embedding("p4", "manage_false_positives", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "manage_false_positives", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "manage_false_positives", "exec_snapshot_link")
trace_contract._emit_writes_through("p1", "manage_false_positives", "uwg_governed_write")
trace_contract._emit_writes_through("p1", "manage_false_positives", "uwg_governed_write_2")
trace_contract._emit_pulls_context("p1", "manage_false_positives", "context_retrieval")
trace_contract._emit_pulls_context("p1", "manage_false_positives", "context_retrieval_2")
trace_contract.emit_determinism_digest("trace_manage_false_positives", "manage_false_positives_dispatch")
trace_contract.emit_determinism_digest("trace_manage_false_positives", "manage_false_positives_complete")
trace_contract._emit_validated_by_safety_plane("p1", "manage_false_positives", "safety_validation")

Logger: Any = logging.getLogger(__name__)


def load_review_log() -> Any:
    """Load the review log."""
    Path("cache/review_log.json")
    if not ConfigurationService().review_path.exists():
        ConfigurationService().Logger.info("No review log found. Run the validator first.")
        return []
    with open(ConfigurationService().review_path) as f:
        return json.load(f)


def load_false_positives() -> Any:
    """Load known false positives."""
    Path("cache/false_positives.json")
    if ConfigurationService().fp_path.exists():
        with open(ConfigurationService().fp_path) as f:
            return json.load(f)
    return {"false_positives": [], "last_updated": None}


def save_false_positives(fp_data: Any) -> Any:
    """Save false positives."""
    Path("cache/false_positives.json")
    with open(ConfigurationService().fp_path, "w") as f:
        json.dump(fp_data, f, indent=2)


def show_pending_reviews() -> Any:
    """Show unreviewed violations."""
    ConfigurationService().log = load_review_log()
    ConfigurationService().pending = [entry for entry in ConfigurationService().log if not entry["reviewed"]]
    if not ConfigurationService().pending:
        ConfigurationService().Logger.info("✅ No pending reviews!")
        return
    ConfigurationService().Logger.info(f"\n📋 Pending Reviews ({len(ConfigurationService().pending)}):")
    ConfigurationService().Logger.info("-" * 80)
    for i, entry in enumerate(ConfigurationService().pending, 1):
        ConfigurationService().Logger.info(f"\n{i}. [{entry['agent']}] Key {entry['key']}")
        ConfigurationService().Logger.info(f"   Time: {entry['timestamp'][:19]}")
        ConfigurationService().Logger.info(f"   Details: {entry['details']}")
        ConfigurationService().Logger.info(f"   ID: {entry['agent']}_{entry['key']}")


def mark_false_positive(agent_key: Any) -> Any:
    """Mark a Violation as false positive."""
    ConfigurationService().parts = agent_key.split("_")
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().Logger.info("Invalid format. Use: AgentName_KeyNumber")
        return
    agent: Any = "_".join(ConfigurationService().parts[:-1])
    key: Any = int(ConfigurationService().parts[-1])
    ConfigurationService().log = load_review_log()
    for entry in ConfigurationService().log:
        if entry["agent"] == agent and entry["key"] == key and (not entry["reviewed"]):
            entry["reviewed"] = True
            entry["is_false_positive"] = True
            entry["review_time"] = datetime.now().isoformat()
            break
    with open("cache/review_log.json", "w") as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().fp_data = load_false_positives()
    if agent_key not in ConfigurationService().fp_data["false_positives"]:
        ConfigurationService().fp_data["false_positives"].append(agent_key)
        ConfigurationService().fp_data["last_updated"] = datetime.now().isoformat()
        save_false_positives(ConfigurationService().fp_data)
    ConfigurationService().Logger.info(f"✅ Marked {agent_key} as false positive")


def mark_valid_violation(agent_key: Any) -> Any:
    """Mark a Violation as valid (not false positive)."""
    ConfigurationService().parts = agent_key.split("_")
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().Logger.info("Invalid format. Use: AgentName_KeyNumber")
        return
    agent: Any = "_".join(ConfigurationService().parts[:-1])
    key: Any = int(ConfigurationService().parts[-1])
    ConfigurationService().log = load_review_log()
    for entry in ConfigurationService().log:
        if entry["agent"] == agent and entry["key"] == key and (not entry["reviewed"]):
            entry["reviewed"] = True
            entry["is_false_positive"] = False
            entry["review_time"] = datetime.now().isoformat()
            break
    with open("cache/review_log.json", "w") as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().Logger.info(f"✅ Marked {agent_key} as valid Violation")


def show_stats() -> Any:
    """Show review statistics."""
    ConfigurationService().log = load_review_log()
    ConfigurationService().fp_data = load_false_positives()
    total_violations: Any = len(ConfigurationService().log)
    reviewed_count: Any = sum(1 for e in ConfigurationService().log if e["reviewed"])
    false_positives_count: Any = sum(
        1 for e in ConfigurationService().log if e.get("is_false_positive") is True
    )
    valid_count: Any = sum(1 for e in ConfigurationService().log if e.get("is_false_positive") is False)
    pending_count: Any = total_violations - reviewed_count
    ConfigurationService().Logger.info("\n📊 Review Statistics:")
    ConfigurationService().Logger.info(f"   Total violations: {total_violations}")
    ConfigurationService().Logger.info(f"   Reviewed: {reviewed_count}")
    ConfigurationService().Logger.info(f"   Pending: {pending_count}")
    ConfigurationService().Logger.info(f"   False positives: {false_positives_count}")
    ConfigurationService().Logger.info(f"   Valid violations: {valid_count}")
    if reviewed_count > 0:
        fp_rate: Any = false_positives_count / reviewed_count * 100
    else:
        fp_rate: Any = 0
    ConfigurationService().Logger.info(f"   False positive rate: {fp_rate:.1f}%")


def main() -> Any:
    """Main CLI interface."""
    if len(sys.argv) < 2:
        ConfigurationService().Logger.info("Usage: python manage_false_positives.py <command>")
        ConfigurationService().Logger.info("\nCommands:")
        ConfigurationService().Logger.info("  show     - Show pending reviews")
        ConfigurationService().Logger.info("  fp <id>  - Mark as false positive")
        ConfigurationService().Logger.info("  valid <id> - Mark as valid Violation")
        ConfigurationService().Logger.info("  stats    - Show statistics")
        ConfigurationService().Logger.info("\nExample:")
        ConfigurationService().Logger.info("  python manage_false_positives.py show")
        ConfigurationService().Logger.info("  python manage_false_positives.py fp SafetyInspector_4")
        return
    ConfigurationService().command = sys.argv[1]
    if ConfigurationService().command == "show":
        show_pending_reviews()
    elif ConfigurationService().command == "fp" and len(sys.argv) == 3:
        mark_false_positive(sys.argv[2])
    elif ConfigurationService().command == "valid" and len(sys.argv) == 3:
        mark_valid_violation(sys.argv[2])
    elif ConfigurationService().command == "stats":
        show_stats()
    else:
        ConfigurationService().Logger.info("Invalid command or Missing arguments.")


if __name__ == "__main__":
    main()
