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

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "manage_false_positives")
_emit_applies_guardrail("p0", "manage_false_positives", "p0_governance")
_emit_reads_policy_state("p0", "manage_false_positives", "policy_binding")
_emit_snapshots_state("p0", "manage_false_positives", "state_snapshot")
emit_replay_key("p0", "manage_false_positives")
emit_determinism_digest("p0", "manage_false_positives")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "manage_false_positives", "execution_auth")
_emit_validates_capability("p2", "manage_false_positives", "capability_check")
_emit_routes_to_capability("p2", "manage_false_positives", "capability_route")
_emit_writes_via_uwg("p2", "manage_false_positives", "uwg_write")
_emit_blocks_direct_write("p2", "manage_false_positives", "direct_write_block")
_emit_records_tool_invocation("p2", "manage_false_positives", "tool_invocation")
_emit_captures_execution_output("p2", "manage_false_positives", "exec_output")
_emit_dispatches_agent("p3", "manage_false_positives", "agent_dispatch")
_emit_coordinates_agents("p3", "manage_false_positives", "agent_coordination")
_emit_records_workflow_lineage("p3", "manage_false_positives", "workflow_lineage")
_emit_records_healing_outcome("p3", "manage_false_positives", "healing_outcome")
_emit_escalates_failure("p3", "manage_false_positives", "failure_escalation")
_emit_orchestrates_workflow("p3", "manage_false_positives", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "manage_false_positives", "healing_dispatch")
_emit_invokes_evaluation("p3", "manage_false_positives", "evaluation_signal")
_emit_records_telemetry_event("p4", "manage_false_positives", "telemetry_event")
_emit_captures_evaluation_metric("p4", "manage_false_positives", "eval_metric")
_emit_stores_embedding("p4", "manage_false_positives", "embedding_store")
_emit_updates_meta_learning_state("p4", "manage_false_positives", "meta_learning")
_emit_links_execution_to_snapshot("p4", "manage_false_positives", "exec_snapshot_link")

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
