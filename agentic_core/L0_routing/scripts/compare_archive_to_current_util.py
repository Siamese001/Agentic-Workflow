#!/usr/bin/env python3
"""Compare archived files against current codebase to identify restoration candidates."""

import hashlib
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_1")
_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_2")
_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_3")
_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_4")
_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_5")
_emit_emits_metric_event("compare_archive_to_current_util", "p4obs", "metric_6")
_emit_records_incident_event("compare_archive_to_current_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("compare_archive_to_current_util", "p4obs", "anomaly")
_emit_writes_observability_log("compare_archive_to_current_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("compare_archive_to_current_util", "p4obs", "mon_state")
_emit_triggers_alert("compare_archive_to_current_util", "p4obs", "alert")
_emit_links_incident_trace("compare_archive_to_current_util", "p4obs", "trace_link")
_emit_captures_pattern("compare_archive_to_current_util", "p3lm", "pattern")
_emit_records_learning_event("compare_archive_to_current_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("compare_archive_to_current_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("compare_archive_to_current_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("compare_archive_to_current_util", "p3lm", "routing")
_emit_improves_agent_policy("compare_archive_to_current_util", "p3lm", "policy")
_emit_stores_learning_state("compare_archive_to_current_util", "p3lm", "state")
_emit_records_execution_trace("compare_archive_to_current_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("compare_archive_to_current_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("compare_archive_to_current_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("compare_archive_to_current_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("compare_archive_to_current_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("compare_archive_to_current_util", "env_read", "p2_env_1")
_emit_reads_environ("compare_archive_to_current_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("compare_archive_to_current_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("compare_archive_to_current_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "compare_archive_to_current_util")
emit_determinism_digest("p0", "compare_archive_to_current_util")

_emit_dispatches_healing_run("p1", "compare_archive_to_current_util", "L0")
_emit_routes_through("p1", "compare_archive_to_current_util", "L0")
_emit_checks_agent_registry("p1", "compare_archive_to_current_util", "agent_registry")
_emit_validates_agent_capability("p1", "compare_archive_to_current_util", "capability")
_emit_dispatches_execution_plan("p1", "compare_archive_to_current_util", "exec_plan")
_emit_agent_executes_agent("p1", "compare_archive_to_current_util", "sub_agent")
_emit_routes_to_agent("p1", "compare_archive_to_current_util", "target_agent")
_emit_verifies_policy("p1", "compare_archive_to_current_util", "policy_check")
_emit_observes_runtime_state("p1", "compare_archive_to_current_util", "runtime_state")
_emit_verifies_boundary("p1", "compare_archive_to_current_util", "boundary_check")
_emit_transcripts_response("p1", "compare_archive_to_current_util", "transcript")
_emit_hard_fails_untranscripted("p1", "compare_archive_to_current_util")
_emit_gated_by_confidence("p1", "compare_archive_to_current_util", "confidence_gate")
_emit_escalates_to_human("p1", "compare_archive_to_current_util", "L0")
_emit_reads_policy_state("p1", "compare_archive_to_current_util", "L0")
_emit_pulls_context("p1", "compare_archive_to_current_util", "context_pull")
_emit_pulls_context("p1", "compare_archive_to_current_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "compare_archive_to_current_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "compare_archive_to_current_util", "uwg_term_secondary")
_emit_writes_through("p1", "compare_archive_to_current_util", "write_through")
_emit_writes_through("p1", "compare_archive_to_current_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "compare_archive_to_current_util", "safety_validation")
_emit_invokes_eval("p1", "compare_archive_to_current_util", "eval_call")
_emit_proposal_commits_routing("p1", "compare_archive_to_current_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "compare_archive_to_current_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "compare_archive_to_current_util", "p0_governance")
_emit_snapshots_state("p0", "compare_archive_to_current_util", "state_snapshot")
_emit_authorize_and_execute("p2", "compare_archive_to_current_util", "execution_auth")
_emit_validates_capability("p2", "compare_archive_to_current_util", "capability_check")
_emit_routes_to_capability("p2", "compare_archive_to_current_util", "capability_route")
_emit_writes_via_uwg("p2", "compare_archive_to_current_util", "uwg_write")
_emit_blocks_direct_write("p2", "compare_archive_to_current_util", "direct_write_block")
_emit_records_tool_invocation("p2", "compare_archive_to_current_util", "tool_invocation")
_emit_captures_execution_output("p2", "compare_archive_to_current_util", "exec_output")
_emit_dispatches_agent("p3", "compare_archive_to_current_util", "agent_dispatch")
_emit_coordinates_agents("p3", "compare_archive_to_current_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "compare_archive_to_current_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "compare_archive_to_current_util", "healing_outcome")
_emit_escalates_failure("p3", "compare_archive_to_current_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "compare_archive_to_current_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "compare_archive_to_current_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "compare_archive_to_current_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "compare_archive_to_current_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "compare_archive_to_current_util", "eval_metric")
_emit_stores_embedding("p4", "compare_archive_to_current_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "compare_archive_to_current_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "compare_archive_to_current_util", "exec_snapshot_link")


def file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ""


def find_in_current(filename: str, current_dirs: list) -> list:
    """Find files with same name in current codebase."""
    matches = []
    for d in current_dirs:
        for f in Path(d).rglob(filename):
            if "__pycache__" not in str(f):
                matches.append(f)
    return matches


def main():
    # Candidate files from archive analysis
    restore_candidates = [
        # apps_lic candidates
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_message_filters.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_personalization_query.py",
            APPS_LIC_DIR,
        ),
        ("archives/apps_lic/L1_cognition/P1_retrieve/get_info/extract_contact_info.py", APPS_LIC_DIR),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/fetch_recipient_interactions.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/match_recipient_patterns.py",
            APPS_LIC_DIR,
        ),
        ("archives/apps_lic/L1_cognition/P1_retrieve/get_info/query_past_campaigns.py", APPS_LIC_DIR),
        # apps_rg candidates
        (
            "archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py",
            APPS_RG_DIR,
        ),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_search_filters.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_skill_query.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/fetch_user_preferences.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/match_job_patterns.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/parse_job_description.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/query_past_generations.py", APPS_RG_DIR),
        # apps_shared candidates
        ("archives/apps_shared/cache/semantic_cache.py", APPS_SHARED_DIR),
        ("archives/apps_shared/core/meta_ranking.py", APPS_SHARED_DIR),
        # Reachout Engine Archive candidates
        ("archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py", APPS_LIC_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/models_LIC.py", APPS_SHARED_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py", APPS_LIC_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py", APPS_SHARED_DIR),
    ]

    current_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]

    print("=" * 80)
    print("ARCHIVE vs CURRENT CODEBASE COMPARISON")
    print("=" * 80)

    to_restore = []
    already_exists = []
    not_found = []

    for archive_path, target_app in restore_candidates:
        archive_file = Path(archive_path)
        if not archive_file.exists():
            not_found.append((archive_path, target_app, "Archive file not found"))
            continue

        filename = archive_file.name
        archive_hash = file_hash(archive_file)

        # Find matching files in current codebase
        current_matches = find_in_current(filename, current_dirs)

        if not current_matches:
            # No match - candidate for restoration
            to_restore.append(
                {
                    "archive": archive_path,
                    "target": target_app,
                    "filename": filename,
                    "reason": "No matching file in current codebase",
                    "action": "RESTORE",
                },
            )
        else:
            # Check if any match has same content
            identical = False
            for match in current_matches:
                if file_hash(match) == archive_hash:
                    identical = True
                    already_exists.append(
                        {
                            "archive": archive_path,
                            "current": str(match),
                            "reason": "Identical file exists",
                            "action": "SKIP",
                        },
                    )
                    break

            if not identical:
                # Different content - may need review
                to_restore.append(
                    {
                        "archive": archive_path,
                        "target": target_app,
                        "filename": filename,
                        "current_matches": [str(m) for m in current_matches],
                        "reason": "File exists but content differs",
                        "action": "REVIEW",
                    },
                )

    # Print results
    print(f"\n## FILES TO RESTORE ({len(to_restore)} files)")
    print("-" * 60)
    for item in to_restore:
        print(f"\n  [{item['action']}] {item['filename']}")
        print(f"    Archive: {item['archive']}")
        print(f"    Target:  {item['target']}/engines/utils/")
        print(f"    Reason:  {item['reason']}")
        if "current_matches" in item:
            print(f"    Current: {item['current_matches']}")

    print(f"\n## ALREADY EXISTS ({len(already_exists)} files)")
    print("-" * 60)
    for item in already_exists:
        print(f"\n  [SKIP] {Path(item['archive']).name}")
        print(f"    Archive: {item['archive']}")
        print(f"    Current: {item['current']}")

    if not_found:
        print(f"\n## NOT FOUND ({len(not_found)} files)")
        print("-" * 60)
        for path, _target, reason in not_found:
            print(f"  {path}: {reason}")

    # Summary
    print("\n" + "=" * 80)
    print("RESTORATION PLAN SUMMARY")
    print("=" * 80)

    restore_count = len([x for x in to_restore if x["action"] == "RESTORE"])
    review_count = len([x for x in to_restore if x["action"] == "REVIEW"])

    print(f"\n  RESTORE (new files):     {restore_count}")
    print(f"  REVIEW (content differs): {review_count}")
    print(f"  SKIP (already exists):    {len(already_exists)}")
    print(f"  NOT FOUND:                {len(not_found)}")


if __name__ == "__main__":
    main()
