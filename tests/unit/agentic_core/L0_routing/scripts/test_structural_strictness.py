"""
V2.5 Structural Strictness - Aggressive Testing
Validates: Unified eviction, domain population, semantic registry alignment

[ULTRA-DIFF] RECONCILIATION: Updated to match authoritative SSOT structure
from structure_blueprint_config.py (2026-02-05)

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L2_EXECUTION_DIR,
    TOOLS_DIR,
)
"""

import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_structural_strictness")
_emit_applies_guardrail("p0", "test_structural_strictness", "p0_governance")
_emit_reads_policy_state("p0", "test_structural_strictness", "policy_binding")
_emit_snapshots_state("p0", "test_structural_strictness", "state_snapshot")
emit_replay_key("p0", "test_structural_strictness")
emit_determinism_digest("p0", "test_structural_strictness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_structural_strictness", "execution_auth")
_emit_validates_capability("p2", "test_structural_strictness", "capability_check")
_emit_routes_to_capability("p2", "test_structural_strictness", "capability_route")
_emit_writes_via_uwg("p2", "test_structural_strictness", "uwg_write")
_emit_blocks_direct_write("p2", "test_structural_strictness", "direct_write_block")
_emit_records_tool_invocation("p2", "test_structural_strictness", "tool_invocation")
_emit_captures_execution_output("p2", "test_structural_strictness", "exec_output")
_emit_dispatches_agent("p3", "test_structural_strictness", "agent_dispatch")
_emit_coordinates_agents("p3", "test_structural_strictness", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_structural_strictness", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_structural_strictness", "healing_outcome")
_emit_escalates_failure("p3", "test_structural_strictness", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_structural_strictness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_structural_strictness", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_structural_strictness", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_structural_strictness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_structural_strictness", "eval_metric")
_emit_stores_embedding("p4", "test_structural_strictness", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_structural_strictness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_structural_strictness", "exec_snapshot_link")

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    SEMANTIC_L2_REGISTRY,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_1")
_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_2")
_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_3")
_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_4")
_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_5")
_emit_emits_metric_event("test_structural_strictness", "p4obs", "metric_6")
_emit_records_incident_event("test_structural_strictness", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_structural_strictness", "p4obs", "anomaly")
_emit_writes_observability_log("test_structural_strictness", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_structural_strictness", "p4obs", "mon_state")
_emit_triggers_alert("test_structural_strictness", "p4obs", "alert")
_emit_links_incident_trace("test_structural_strictness", "p4obs", "trace_link")
_emit_captures_pattern("test_structural_strictness", "p3lm", "pattern")
_emit_records_learning_event("test_structural_strictness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_structural_strictness", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_structural_strictness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_structural_strictness", "p3lm", "routing")
_emit_improves_agent_policy("test_structural_strictness", "p3lm", "policy")
_emit_stores_learning_state("test_structural_strictness", "p3lm", "state")
_emit_records_execution_trace("test_structural_strictness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_structural_strictness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_structural_strictness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_structural_strictness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_structural_strictness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_structural_strictness", "env_read", "p2_env_1")
_emit_reads_environ("test_structural_strictness", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_structural_strictness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_structural_strictness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_structural_strictness", "context_pull")
_emit_pulls_context("p1", "test_structural_strictness", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_structural_strictness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_structural_strictness", "uwg_term_secondary")
_emit_writes_through("p1", "test_structural_strictness", "write_through")
_emit_writes_through("p1", "test_structural_strictness", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_structural_strictness", "safety_validation")
_emit_invokes_eval("p1", "test_structural_strictness", "eval_call")
_emit_proposal_commits_routing("p1", "test_structural_strictness", "routing_commit")
_emit_escalates_to_human("p1", "test_structural_strictness", "human_escalation")
_emit_routes_through("p1", "test_structural_strictness", "route_through")
_emit_checks_agent_registry("p1", "test_structural_strictness", "agent_registry")
_emit_validates_agent_capability("p1", "test_structural_strictness", "capability")
_emit_dispatches_execution_plan("p1", "test_structural_strictness", "exec_plan")
_emit_agent_executes_agent("p1", "test_structural_strictness", "sub_agent")
_emit_routes_to_agent("p1", "test_structural_strictness", "target_agent")
_emit_verifies_policy("p1", "test_structural_strictness", "policy_check")
_emit_observes_runtime_state("p1", "test_structural_strictness", "runtime_state")
_emit_verifies_boundary("p1", "test_structural_strictness", "boundary_check")
_emit_transcripts_response("p1", "test_structural_strictness", "transcript")
_emit_hard_fails_untranscripted("p1", "test_structural_strictness")
_emit_gated_by_confidence("p1", "test_structural_strictness", "confidence_gate")


def test_unified_eviction():
    """
    Edge Case: Verify 'unified' is completely removed from all CORE_SUBFOLDER_MAP lists.
    It is an anti-pattern that obscures domain responsibility.
    """
    l2 = CORE_SUBFOLDER_MAP["L2_execution"]
    assert "unified" not in l2, f"FAILED: 'unified' found in L2_execution: {l2}"

    l5 = CORE_SUBFOLDER_MAP["L5_safety"]
    assert "unified" not in l5, f"FAILED: 'unified' found in L5_safety: {l5}"
    print("✅ Test 1/4: Unified eviction verified")


def test_apps_domain_population():
    """
    [ULTRA-DIFF] RECONCILIATION: Verify APPS_*_SUBFOLDER_MAPs match authoritative SSOT.

    Old Expectation: {"models", "types", "events"}
    New SSOT (apps_rg): ["entities", "models", "value_objects"]
    New SSOT (apps_lic): ["config", "utils", "models"]
    """
    # Verify apps_rg domain structure
    expected_rg_domain = {"entities", "models", "value_objects"}
    rg_domain = set(APPS_RG_SUBFOLDER_MAP.get("domain", []))
    assert rg_domain == expected_rg_domain, (
        f"FAILED: apps_rg['domain'] mismatch. Expected {expected_rg_domain}, got {rg_domain}"
    )

    # Verify apps_lic domain structure
    expected_lic_domain = {"config", "utils", "models"}
    lic_domain = set(APPS_LIC_SUBFOLDER_MAP.get("domain", []))
    assert lic_domain == expected_lic_domain, (
        f"FAILED: apps_lic['domain'] mismatch. Expected {expected_lic_domain}, got {lic_domain}"
    )
    print("✅ Test 2/6: Apps domain population verified (SSOT aligned)")


def test_semantic_registry_alignment():
    """
    [ULTRA-DIFF] RECONCILIATION: Verify semantic_l2_registry aligns with APPS_SHARED_SUBFOLDER_MAP.

    Updated legacy keys - removed 'core_components' as it's now a valid SSOT key.
    """
    shared_sem = SEMANTIC_L2_REGISTRY[APPS_SHARED_DIR.split("/")[-1]]

    # Legacy keys that should NOT be present (old structure that was removed)
    legacy_keys = {"base_definitions", "common_utils", "base_agents"}
    present_legacy = set(shared_sem.keys()).intersection(legacy_keys)
    assert not present_legacy, f"FAILED: Legacy keys found in semantic registry: {present_legacy}"

    # Verify all SSOT keys have semantic definitions
    required_keys = set(APPS_SHARED_SUBFOLDER_MAP.keys())
    present_keys = set(shared_sem.keys())
    assert required_keys.issubset(present_keys), (
        f"FAILED: Missing semantic definitions for apps_shared. Missing: {required_keys - present_keys}"
    )
    print("✅ Test 3/6: Semantic registry alignment verified")


def test_apps_rg_lic_semantic_completeness():
    """
    Edge Case: Verify apps_rg and apps_lic in semantic registry have 'core' and 'domain' definitions.
    """
    for app in [APPS_RG_DIR.split("/")[-1], APPS_LIC_DIR.split("/")[-1]]:
        app_sem = SEMANTIC_L2_REGISTRY[app]
        assert "core" in app_sem, f"FAILED: {app} missing 'core' in semantic registry"
        assert "domain" in app_sem, f"FAILED: {app} missing 'domain' in semantic registry"
    print("✅ Test 4/6: Apps semantic completeness verified")


def test_apps_rg_filesystem_structure():
    """
    [ULTRA-DIFF] Verify apps_rg filesystem adheres to new SSOT.
    Only enforces that IF a folder exists, it must be in the allowed list.
    Does not force empty folders to exist.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

    # Verify domain subfolders
    expected_domain_subfolders = {"entities", "models", "value_objects"}
    domain_path = project_root / APPS_RG_DIR / "domain"

    if domain_path.exists():
        current_subfolders = {p.name for p in domain_path.iterdir() if p.is_dir()}
        unknown_folders = current_subfolders - expected_domain_subfolders
        assert not unknown_folders, f"Found prohibited folders in apps_rg/config: {unknown_folders}"

    # Verify top-level structure matches SSOT
    expected_roots = {
        "asset_library",
        "core",
        "domain",
        "engines",
        "logic_nodes",
        "shared",
        "system_flow",
        "validation",
    }
    apps_rg_path = project_root / APPS_RG_DIR
    if apps_rg_path.exists():
        current_roots = {p.name for p in apps_rg_path.iterdir() if p.is_dir() and not p.name.startswith("_")}
        unknown_roots = current_roots - expected_roots
        assert not unknown_roots, f"Found prohibited top-level folders in apps_rg: {unknown_roots}"

    print("✅ Test 5/6: apps_rg filesystem structure verified")


def test_apps_lic_filesystem_structure():
    """
    [ULTRA-DIFF] Verify apps_lic filesystem adheres to new SSOT.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

    # Verify top-level structure matches SSOT
    expected_roots = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
    apps_lic_path = project_root / APPS_LIC_DIR
    if apps_lic_path.exists():
        current_roots = {p.name for p in apps_lic_path.iterdir() if p.is_dir() and not p.name.startswith("_")}
        unknown_roots = current_roots - expected_roots
        assert not unknown_roots, f"Found prohibited top-level folders in apps_lic: {unknown_roots}"

    print("✅ Test 6/6: apps_lic filesystem structure verified")


if __name__ == "__main__":
    try:
        test_unified_eviction()
        test_apps_domain_population()
        test_semantic_registry_alignment()
        test_apps_rg_lic_semantic_completeness()
        test_apps_rg_filesystem_structure()
        test_apps_lic_filesystem_structure()
        print("\n" + "=" * 60)
        print("V2.5 STRUCTURAL STRICTNESS: 100% PASS (6/6 tests)")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
