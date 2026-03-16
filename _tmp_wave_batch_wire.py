"""Batch wire missing emitters for wave: 6 gap files + 9 additional files."""

changed = []

# ═══════════════════════════════════════════════════════════════════════
# Group A: 5 files needing FULL wiring (have only 3 emitters currently)
# ═══════════════════════════════════════════════════════════════════════

GROUP_A_FILES = {
    "system_learning/engines/historical_backfill_engine.py": "historical_backfill_engine",
    "tests/system_learning/test_historical_backfill_engine.py": "test_historical_backfill_engine",
    "tests/system_learning/test_healing_backups_rca_waves.py": "test_healing_backups_rca_waves",
    "tests/unit/system_learning/engines/test_cross_repo_system_learning_import.py": "test_cross_repo_system_learning_import",
    "apps_shared/utils/rank_observability_components_util.py": "rank_observability_components_util",
}

FULL_IMPORT = """\
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)"""

def full_calls(n):
    return (
        f'emit_determinism_digest("p0", "{n}")\n'
        f'emit_replay_key("p0", "{n}")\n'
        f'_emit_records_execution_trace("p0", "evidence", "{n}")\n'
        f'_emit_applies_guardrail("p0", "{n}", "p0_governance")\n'
        f'_emit_snapshots_state("p0", "{n}", "state_snapshot")\n'
        f'_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)\n'
        f'_emit_authorize_and_execute("p2", "{n}", "execution_auth")\n'
        f'_emit_validates_capability("p2", "{n}", "capability_check")\n'
        f'_emit_routes_to_capability("p2", "{n}", "capability_route")\n'
        f'_emit_writes_via_uwg("p2", "{n}", "uwg_write")\n'
        f'_emit_blocks_direct_write("p2", "{n}", "direct_write_block")\n'
        f'_emit_records_tool_invocation("p2", "{n}", "tool_invocation")\n'
        f'_emit_captures_execution_output("p2", "{n}", "exec_output")\n'
        f'_emit_dispatches_agent("p3", "{n}", "agent_dispatch")\n'
        f'_emit_coordinates_agents("p3", "{n}", "agent_coordination")\n'
        f'_emit_records_workflow_lineage("p3", "{n}", "workflow_lineage")\n'
        f'_emit_records_healing_outcome("p3", "{n}", "healing_outcome")\n'
        f'_emit_escalates_failure("p3", "{n}", "failure_escalation")\n'
        f'_emit_orchestrates_workflow("p3", "{n}", "workflow_orchestration")\n'
        f'_emit_dispatches_healing_run("p3", "{n}", "healing_dispatch")\n'
        f'_emit_invokes_evaluation("p3", "{n}", "evaluation_signal")\n'
        f'_emit_records_telemetry_event("p4", "{n}", "telemetry_event")\n'
        f'_emit_captures_evaluation_metric("p4", "{n}", "eval_metric")\n'
        f'_emit_stores_embedding("p4", "{n}", "embedding_store")\n'
        f'_emit_updates_meta_learning_state("p4", "{n}", "meta_learning")\n'
        f'_emit_links_execution_to_snapshot("p4", "{n}", "exec_snapshot_link")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_1")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_2")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_3")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_4")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_5")\n'
        f'_emit_emits_metric_event("{n}", "p4obs", "metric_6")\n'
        f'_emit_records_incident_event("{n}", "p4obs", "incident")\n'
        f'_emit_captures_runtime_anomaly("{n}", "p4obs", "anomaly")\n'
        f'_emit_writes_observability_log("{n}", "p4obs", "obs_log")\n'
        f'_emit_updates_monitoring_state("{n}", "p4obs", "mon_state")\n'
        f'_emit_triggers_alert("{n}", "p4obs", "alert")\n'
        f'_emit_links_incident_trace("{n}", "p4obs", "trace_link")\n'
        f'_emit_captures_pattern("{n}", "p3lm", "pattern")\n'
        f'_emit_records_learning_event("{n}", "p3lm", "learning_event")\n'
        f'_emit_writes_learning_snapshot("{n}", "p3lm", "snapshot")\n'
        f'_emit_feeds_meta_learning("{n}", "p3lm", "meta_feed")\n'
        f'_emit_updates_routing_strategy("{n}", "p3lm", "routing")\n'
        f'_emit_improves_agent_policy("{n}", "p3lm", "policy")\n'
        f'_emit_stores_learning_state("{n}", "p3lm", "state")\n'
        f'_emit_pulls_context("p1", "{n}", "context_pull")\n'
        f'_emit_execution_terminates_at_uwg("p1", "{n}", "uwg_term")\n'
        f'_emit_writes_through("p1", "{n}", "write_through")\n'
        f'_emit_validated_by_safety_plane("p1", "{n}", "safety_validation")\n'
        f'_emit_proposal_commits_routing("p1", "{n}", "routing_commit")'
    )

OLD_IMPORT_PATTERN = (
    "from agentic_core.runtime.lifecycle_trace_contract import (\n"
    "    _emit_emits_metric_event,\n"
    "    _emit_records_execution_trace,\n"
    "    emit_determinism_digest,\n"
    ")"
)

for fpath, mod_name in GROUP_A_FILES.items():
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    if OLD_IMPORT_PATTERN not in content:
        print(f"WARN: import block not found in {fpath}, skipping")
        continue

    old_calls = (
        f'emit_determinism_digest("p0", "{mod_name}")\n'
        f'_emit_records_execution_trace("p0", "evidence", "{mod_name}")\n'
        f'_emit_emits_metric_event("{mod_name}", "p4obs", "metric_1")'
    )
    if old_calls not in content:
        print(f"WARN: emitter calls not found in {fpath}, skipping")
        continue

    content = content.replace(OLD_IMPORT_PATTERN, FULL_IMPORT)
    content = content.replace(old_calls, full_calls(mod_name))

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    changed.append(fpath)
    print(f"✓ A: {fpath}")

# ═══════════════════════════════════════════════════════════════════════
# Group B: test_sl_gap_fixes.py — add missing P3 learning/P4 obs/P1
# ═══════════════════════════════════════════════════════════════════════

SL = "tests/system_learning/test_sl_gap_fixes.py"
with open(SL, "r", encoding="utf-8") as f:
    c = f.read()

# --- imports ---
REPLACEMENTS = [
    # add _emit_execution_terminates_at_uwg
    ("    _emit_emits_metric_event,\n    _emit_escalates_failure,",
     "    _emit_emits_metric_event,\n    _emit_escalates_failure,\n    _emit_execution_terminates_at_uwg,"),
    # add feeds/improves before invokes
    ("    _emit_invokes_evaluation,\n    _emit_links_execution_to_snapshot,",
     "    _emit_feeds_meta_learning,\n    _emit_improves_agent_policy,\n    _emit_invokes_evaluation,\n    _emit_links_execution_to_snapshot,"),
    # add proposal/pulls after orchestrates
    ("    _emit_orchestrates_workflow,\n    _emit_reads_policy_state,",
     "    _emit_orchestrates_workflow,\n    _emit_proposal_commits_routing,\n    _emit_pulls_context,\n    _emit_reads_policy_state,"),
    # add records_incident_event/records_learning_event
    ("    _emit_records_healing_outcome,\n    _emit_records_telemetry_event,",
     "    _emit_records_healing_outcome,\n    _emit_records_incident_event,\n    _emit_records_learning_event,\n    _emit_records_telemetry_event,"),
    # add stores_learning_state/triggers_alert/updates_monitoring_state/updates_routing_strategy
    ("    _emit_stores_embedding,\n    _emit_updates_meta_learning_state,",
     "    _emit_stores_embedding,\n    _emit_stores_learning_state,\n    _emit_triggers_alert,\n    _emit_updates_meta_learning_state,\n    _emit_updates_monitoring_state,\n    _emit_updates_routing_strategy,"),
    # add validated_by_safety_plane/writes_learning_snapshot/writes_observability_log/writes_through before emit_determinism_digest
    ("    emit_determinism_digest,\n    emit_replay_key,\n)",
     "    _emit_validated_by_safety_plane,\n    _emit_writes_learning_snapshot,\n    _emit_writes_observability_log,\n    _emit_writes_through,\n    emit_determinism_digest,\n    emit_replay_key,\n)"),
    # add captures_pattern/captures_runtime_anomaly
    ("    _emit_captures_execution_output,\n    _emit_coordinates_agents,",
     "    _emit_captures_execution_output,\n    _emit_captures_pattern,\n    _emit_captures_runtime_anomaly,\n    _emit_coordinates_agents,"),
]

for old, new in REPLACEMENTS:
    if old in c:
        c = c.replace(old, new)
    else:
        print(f"WARN: SL replacement not found: {old[:60]}...")

# --- emitter calls ---
SL_OLD_EMIT = '_emit_emits_metric_event("test_sl_gap_fixes", "p4obs", "metric_1")\n_emit_captures_evaluation_metric'
SL_NEW_EMIT = (
    '_emit_emits_metric_event("test_sl_gap_fixes", "p4obs", "metric_1")\n'
    '_emit_records_incident_event("test_sl_gap_fixes", "p4obs", "incident")\n'
    '_emit_captures_runtime_anomaly("test_sl_gap_fixes", "p4obs", "anomaly")\n'
    '_emit_writes_observability_log("test_sl_gap_fixes", "p4obs", "obs_log")\n'
    '_emit_updates_monitoring_state("test_sl_gap_fixes", "p4obs", "mon_state")\n'
    '_emit_triggers_alert("test_sl_gap_fixes", "p4obs", "alert")\n'
    '_emit_links_incident_trace("test_sl_gap_fixes", "p4obs", "trace_link")\n'
    '_emit_captures_pattern("test_sl_gap_fixes", "p3lm", "pattern")\n'
    '_emit_records_learning_event("test_sl_gap_fixes", "p3lm", "learning_event")\n'
    '_emit_writes_learning_snapshot("test_sl_gap_fixes", "p3lm", "snapshot")\n'
    '_emit_feeds_meta_learning("test_sl_gap_fixes", "p3lm", "meta_feed")\n'
    '_emit_updates_routing_strategy("test_sl_gap_fixes", "p3lm", "routing")\n'
    '_emit_improves_agent_policy("test_sl_gap_fixes", "p3lm", "policy")\n'
    '_emit_stores_learning_state("test_sl_gap_fixes", "p3lm", "state")\n'
    '_emit_pulls_context("p1", "test_sl_gap_fixes", "context_pull")\n'
    '_emit_execution_terminates_at_uwg("p1", "test_sl_gap_fixes", "uwg_term")\n'
    '_emit_writes_through("p1", "test_sl_gap_fixes", "write_through")\n'
    '_emit_validated_by_safety_plane("p1", "test_sl_gap_fixes", "safety_validation")\n'
    '_emit_proposal_commits_routing("p1", "test_sl_gap_fixes", "routing_commit")\n'
    '_emit_captures_evaluation_metric'
)
if SL_OLD_EMIT in c:
    c = c.replace(SL_OLD_EMIT, SL_NEW_EMIT)
else:
    print("WARN: SL emitter calls not found")

with open(SL, "w", encoding="utf-8") as f:
    f.write(c)
changed.append(SL)
print(f"✓ B: {SL}")

# ═══════════════════════════════════════════════════════════════════════
# Group C: 9 new files — add P1 emitters (writes_through etc.)
# ═══════════════════════════════════════════════════════════════════════

GROUP_C = {
    "agentic_core/L2_execution/enforcement/transcript_freezer.py": "transcript_freezer",
    "agentic_core/L5_safety/core_kernel/classification_kernel.py": "classification_kernel",
    "agentic_core/L5_safety/validators/global_mutation_validator.py": "global_mutation_validator",
    "agentic_core/L5_safety/validators/magic_validator.py": "magic_validator",
    "agentic_core/L5_safety/validators/path_fragility_validator.py": "path_fragility_validator",
    "agentic_core/L5_safety/validators/type_erasure_validator.py": "type_erasure_validator",
    "agentic_core/utils/workflow_engines/answer_support.py": "answer_support",
    "tests/governance/test_layer_sovereignty_enforcer.py": "test_layer_sovereignty_enforcer",
    "tests/integration/test_adg_composition_graph.py": "test_adg_composition_graph",
}

P1_EXTRA_IMPORTS = (
    "    _emit_execution_terminates_at_uwg,\n"
    "    _emit_proposal_commits_routing,\n"
    "    _emit_pulls_context,\n"
    "    _emit_validated_by_safety_plane,\n"
    "    _emit_writes_through,"
)

def p1_calls(n):
    return (
        f'_emit_pulls_context("p1", "{n}", "context_pull")\n'
        f'_emit_execution_terminates_at_uwg("p1", "{n}", "uwg_term")\n'
        f'_emit_writes_through("p1", "{n}", "write_through")\n'
        f'_emit_validated_by_safety_plane("p1", "{n}", "safety_validation")\n'
        f'_emit_proposal_commits_routing("p1", "{n}", "routing_commit")'
    )

for fpath, mod_name in GROUP_C.items():
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already wired
    if '_emit_pulls_context("p1"' in content:
        print(f"SKIP: {fpath} already has P1 pulls_context")
        continue

    # 1. Add imports to the second import block (all Group C files have 2 import blocks)
    # Find the second "from agentic_core.runtime.lifecycle_trace_contract import (" and add before closing ")"
    first_idx = content.find("from agentic_core.runtime.lifecycle_trace_contract import (")
    if first_idx < 0:
        print(f"WARN: no import block in {fpath}")
        continue
    second_idx = content.find("from agentic_core.runtime.lifecycle_trace_contract import (", first_idx + 1)
    if second_idx < 0:
        # Only one import block - add imports to it
        target_idx = first_idx
    else:
        target_idx = second_idx

    # Find the closing ")" of the target import block
    close_paren = content.find("\n)", target_idx)
    if close_paren < 0:
        print(f"WARN: no closing paren in {fpath}")
        continue

    # Insert the extra imports before the closing paren
    content = content[:close_paren] + "\n" + P1_EXTRA_IMPORTS + content[close_paren:]

    # 2. Add emitter calls after the P0 snapshots_state call
    p0_marker = f'_emit_snapshots_state("p0", "{mod_name}", "state_snapshot")'
    p1_marker = f'_emit_reads_policy_state("p1", "{mod_name}", "L5")'

    if p1_marker in content:
        content = content.replace(p1_marker, p1_marker + "\n" + p1_calls(mod_name))
    elif p0_marker in content:
        content = content.replace(p0_marker, p0_marker + "\n" + p1_calls(mod_name))
    else:
        print(f"WARN: no insertion point in {fpath}")
        continue

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    changed.append(fpath)
    print(f"✓ C: {fpath}")

# ═══════════════════════════════════════════════════════════════════════
print(f"\n=== Total files changed: {len(changed)} ===")
for f in changed:
    print(f"  {f}")
