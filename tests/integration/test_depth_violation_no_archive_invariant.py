"""
Wave 0A Invariant: LocationHealerAgent must never archive files under sovereign roots
for depth violations (DEEP VIOLATION or SHALLOW VIOLATION).

Root cause this guards against: The archive fallback in _apply_healing_strategy()
was firing for depth violations that slipped through the strategy map or produced
no-op moves, causing 1,031 unintended file deletions in run11.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_depth_violation_no_archive_invariant")
# REMOVED: _emit_applies_guardrail("p0", "test_depth_violation_no_archive_invariant", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_depth_violation_no_archive_invariant", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_depth_violation_no_archive_invariant", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_depth_violation_no_archive_invariant", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_depth_violation_no_archive_invariant", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_depth_violation_no_archive_invariant", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_depth_violation_no_archive_invariant", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_depth_violation_no_archive_invariant", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_depth_violation_no_archive_invariant", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_depth_violation_no_archive_invariant", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_depth_violation_no_archive_invariant", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_depth_violation_no_archive_invariant", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_depth_violation_no_archive_invariant", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_depth_violation_no_archive_invariant", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_depth_violation_no_archive_invariant", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_depth_violation_no_archive_invariant", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_depth_violation_no_archive_invariant", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_depth_violation_no_archive_invariant", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_depth_violation_no_archive_invariant", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_depth_violation_no_archive_invariant", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_depth_violation_no_archive_invariant", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_depth_violation_no_archive_invariant", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_depth_violation_no_archive_invariant", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_depth_violation_no_archive_invariant", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_depth_violation_no_archive_invariant", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_depth_violation_no_archive_invariant", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_depth_violation_no_archive_invariant", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_depth_violation_no_archive_invariant", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_depth_violation_no_archive_invariant", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_depth_violation_no_archive_invariant", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_depth_violation_no_archive_invariant", "write_through")
# REMOVED: _emit_writes_through("p1", "test_depth_violation_no_archive_invariant", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_depth_violation_no_archive_invariant", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_depth_violation_no_archive_invariant", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_depth_violation_no_archive_invariant", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_depth_violation_no_archive_invariant", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_depth_violation_no_archive_invariant", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_depth_violation_no_archive_invariant", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_depth_violation_no_archive_invariant", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_depth_violation_no_archive_invariant", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_depth_violation_no_archive_invariant", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_depth_violation_no_archive_invariant", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_depth_violation_no_archive_invariant", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_depth_violation_no_archive_invariant", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_depth_violation_no_archive_invariant", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_depth_violation_no_archive_invariant", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_depth_violation_no_archive_invariant")
# REMOVED: _emit_gated_by_confidence("p1", "test_depth_violation_no_archive_invariant", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_depth_violation_no_archive_invariant")
# REMOVED: emit_determinism_digest("p0", "test_depth_violation_no_archive_invariant")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_depth_violation_no_archive_invariant", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_depth_violation_no_archive_invariant", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_depth_violation_no_archive_invariant", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_depth_violation_no_archive_invariant", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_depth_violation_no_archive_invariant", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_depth_violation_no_archive_invariant", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_depth_violation_no_archive_invariant", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_depth_violation_no_archive_invariant", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_depth_violation_no_archive_invariant", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_depth_violation_no_archive_invariant", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_depth_violation_no_archive_invariant", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_depth_violation_no_archive_invariant", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_depth_violation_no_archive_invariant", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_depth_violation_no_archive_invariant", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_depth_violation_no_archive_invariant", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_depth_violation_no_archive_invariant", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_depth_violation_no_archive_invariant", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_depth_violation_no_archive_invariant", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_depth_violation_no_archive_invariant", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_depth_violation_no_archive_invariant", "exec_snapshot_link")

# Under --import-mode=importlib pytest collects this as package tests/agentic_core,
# so bare 'from agentic_core...' resolves into tests/ not the project root.
_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

SOVEREIGN_ROOTS = [APPS_LIC_DIR, APPS_RG_DIR, AGENTIC_CORE_DIR, APPS_SHARED_DIR]

DEPTH_VIOLATION_MESSAGES = [
    "DEEP VIOLATION: file is too deep",
    "SHALLOW VIOLATION: file is too shallow",
    "DEEP VIOLATION at apps_lic/engines/FooAgent.py",
    "SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py",
]


@pytest.fixture
def healer(tmp_path):
    """Minimal LocationHealerAgent configured against tmp_path as project root."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

    agent = LocationHealerAgent.__new__(LocationHealerAgent)
    agent.project_root = tmp_path
    agent._autonomous_mode = False
    return agent, tmp_path


@pytest.mark.parametrize("violation_msg", DEPTH_VIOLATION_MESSAGES)
@pytest.mark.parametrize("sovereign_root", SOVEREIGN_ROOTS)
def test_depth_violation_never_archived(healer, sovereign_root, violation_msg):
    from agentic_core.L0_routing.config.path_constants import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent
    from agentic_core.L5_safety.utils.location_constants_util import HEALING_STRATEGY_MAP
    from agentic_core.L5_safety.utils.location_constants_util import HEALING_STRATEGY_MAP
    from agentic_core.L5_safety.config.structure_blueprint import (
    """
    Invariant: _apply_healing_strategy must never return ARCHIVED for any
    DEEP VIOLATION or SHALLOW VIOLATION message under a sovereign root.
    """
    agent, tmp_path = healer

    # Create a fake file under the sovereign root
    sovereign_dir = tmp_path / sovereign_root / "engines"
    sovereign_dir.mkdir(parents=True, exist_ok=True)
    fake_file = sovereign_dir / "TestAgent.py"
    fake_file.write_text("class TestAgent: pass\n")

    archives_root = tmp_path / ".healing_backups"
    archives_root.mkdir(parents=True, exist_ok=True)

    affected_paths: list[Path] = []
    import_touched_paths: list[Path] = []

    result = agent._apply_healing_strategy(
        file_path=fake_file,
        msg=violation_msg,
        archives_root=archives_root,
        dry_run=False,
        affected_paths=affected_paths,
        import_touched_paths=import_touched_paths,
    )

    action = result.get("action_taken", "")
    assert "ARCHIVED" not in action.upper(), (
        f"INVARIANT VIOLATED: {sovereign_root} file was ARCHIVED for depth violation.\n"
        f"  File: {fake_file}\n"
        f"  Violation: {violation_msg}\n"
        f"  Result: {result}"
    )

    # Confirm the file was not actually moved to archives
    assert fake_file.exists(), (
        f"INVARIANT VIOLATED: {sovereign_root} file was physically moved/deleted "
        f"for depth violation: {violation_msg}"
    )


def test_identity_path_guard_returns_skipped(healer):
    """
    Bug 3 guard: when _heal_depth_violation computes target_path == file_path
    (depth already correct), it must return SKIPPED, not fall to archive.
    """
    agent, tmp_path = healer

    apps_dir = tmp_path / APPS_LIC_DIR / "engines"
    apps_dir.mkdir(parents=True, exist_ok=True)
    fake_file = apps_dir / "FooAgent.py"
    fake_file.write_text("class FooAgent: pass\n")

    affected_paths: list[Path] = []
    import_touched_paths: list[Path] = []

    # Patch SOVEREIGN_REGISTRY to return depth=2 (matching the file's actual depth=2)
    mock_registry = {APPS_LIC_DIR: {"depth": 2, "subfolders": ["engines", "reasoning"]}}
    with patch(
        "agentic_core.L5_safety.reasoning.LocationHealerAgent.SOVEREIGN_REGISTRY",
        mock_registry,
    ):
        result = agent._heal_depth_violation(
            file_path=fake_file,
            msg="DEEP VIOLATION: file is too deep",
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

    action = result.get("action_taken", "")
    assert "SKIPPED" in action.upper() or "depth already correct" in action.lower(), (
        f"Identity-path guard failed — expected SKIPPED, got: {result}"
    )
    assert fake_file.exists(), "File was moved despite identity-path guard"


def test_shallow_violation_in_strategy_map():
    """Bug 2 guard: SHALLOW VIOLATION must be in HEALING_STRATEGY_MAP."""
#  # MOVED: from agentic_core.L5_safety.utils.location_constants_util import HEALING_STRATEGY_MAP

    assert "SHALLOW VIOLATION" in HEALING_STRATEGY_MAP, (
        "SHALLOW VIOLATION missing from HEALING_STRATEGY_MAP — shallow files will fall to archive fallback"
    )


def test_pascal_in_non_agent_folder_in_strategy_map():
    """Bug 5 guard: PASCAL_IN_NON_AGENT_FOLDER must be in HEALING_STRATEGY_MAP."""
#  # MOVED: from agentic_core.L5_safety.utils.location_constants_util import HEALING_STRATEGY_MAP

    assert "PASCAL_IN_NON_AGENT_FOLDER" in HEALING_STRATEGY_MAP, (
        "PASCAL_IN_NON_AGENT_FOLDER missing from HEALING_STRATEGY_MAP — "
        "PascalCase agent files in engines/ will be archived instead of moved to reasoning/"
    )


def test_apps_rg_apps_lic_depth_is_two():
    """Bug 1 guard: apps_rg and apps_lic must have depth=2 in get_all_territories()."""
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint import (
        get_all_territories,
    )

    for territory in (APPS_RG_DIR, APPS_LIC_DIR):
        depth = get_all_territories().get(territory, {}).get("depth")
        assert depth == 2, (
            f"SSOT depth split: {territory} has depth={depth} in get_all_territories(), "
            f"expected 2. This causes DEEP VIOLATION false positives and archive fallback."
        )
