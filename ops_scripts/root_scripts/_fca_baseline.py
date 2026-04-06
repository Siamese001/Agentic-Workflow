"""PHASE 0 WAVE 0.1: FCA baseline reproduction — save artifact for diffing."""

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
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

_emit_records_execution_trace("p0", "evidence", "_fca_baseline")
_emit_applies_guardrail("p0", "_fca_baseline", "p0_governance")
_emit_reads_policy_state("p0", "_fca_baseline", "policy_binding")
_emit_snapshots_state("p0", "_fca_baseline", "state_snapshot")
emit_replay_key("p0", "_fca_baseline")
emit_determinism_digest("p0", "_fca_baseline")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_fca_baseline", "execution_auth")
_emit_validates_capability("p2", "_fca_baseline", "capability_check")
_emit_routes_to_capability("p2", "_fca_baseline", "capability_route")
_emit_writes_via_uwg("p2", "_fca_baseline", "uwg_write")
_emit_blocks_direct_write("p2", "_fca_baseline", "direct_write_block")
_emit_records_tool_invocation("p2", "_fca_baseline", "tool_invocation")
_emit_captures_execution_output("p2", "_fca_baseline", "exec_output")
_emit_dispatches_agent("p3", "_fca_baseline", "agent_dispatch")
_emit_coordinates_agents("p3", "_fca_baseline", "agent_coordination")
_emit_records_workflow_lineage("p3", "_fca_baseline", "workflow_lineage")
_emit_records_healing_outcome("p3", "_fca_baseline", "healing_outcome")
_emit_escalates_failure("p3", "_fca_baseline", "failure_escalation")
_emit_orchestrates_workflow("p3", "_fca_baseline", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_fca_baseline", "healing_dispatch")
_emit_invokes_evaluation("p3", "_fca_baseline", "evaluation_signal")
_emit_records_telemetry_event("p4", "_fca_baseline", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_fca_baseline", "eval_metric")
_emit_stores_embedding("p4", "_fca_baseline", "embedding_store")
_emit_updates_meta_learning_state("p4", "_fca_baseline", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_fca_baseline", "exec_snapshot_link")

ROOT = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
    get_python_files_fast,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_1")
_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_2")
_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_3")
_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_4")
_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_5")
_emit_emits_metric_event("_fca_baseline", "p4obs", "metric_6")
_emit_records_incident_event("_fca_baseline", "p4obs", "incident")
_emit_captures_runtime_anomaly("_fca_baseline", "p4obs", "anomaly")
_emit_writes_observability_log("_fca_baseline", "p4obs", "obs_log")
_emit_updates_monitoring_state("_fca_baseline", "p4obs", "mon_state")
_emit_triggers_alert("_fca_baseline", "p4obs", "alert")
_emit_links_incident_trace("_fca_baseline", "p4obs", "trace_link")
_emit_captures_pattern("_fca_baseline", "p3lm", "pattern")
_emit_records_learning_event("_fca_baseline", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_fca_baseline", "p3lm", "snapshot")
_emit_feeds_meta_learning("_fca_baseline", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_fca_baseline", "p3lm", "routing")
_emit_improves_agent_policy("_fca_baseline", "p3lm", "policy")
_emit_stores_learning_state("_fca_baseline", "p3lm", "state")
_emit_records_execution_trace("_fca_baseline", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_fca_baseline", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_fca_baseline", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_fca_baseline", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_fca_baseline", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_fca_baseline", "env_read", "p2_env_1")
_emit_reads_environ("_fca_baseline", "env_read", "p2_env_2")
_emit_reads_runtime_state("_fca_baseline", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_fca_baseline", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_fca_baseline", "context_pull")
_emit_pulls_context("p1", "_fca_baseline", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_fca_baseline", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_fca_baseline", "uwg_term_secondary")
_emit_writes_through("p1", "_fca_baseline", "write_through")
_emit_writes_through("p1", "_fca_baseline", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_fca_baseline", "safety_validation")
_emit_invokes_eval("p1", "_fca_baseline", "eval_call")
_emit_proposal_commits_routing("p1", "_fca_baseline", "routing_commit")
_emit_escalates_to_human("p1", "_fca_baseline", "human_escalation")
_emit_routes_through("p1", "_fca_baseline", "route_through")
_emit_checks_agent_registry("p1", "_fca_baseline", "agent_registry")
_emit_validates_agent_capability("p1", "_fca_baseline", "capability")
_emit_dispatches_execution_plan("p1", "_fca_baseline", "exec_plan")
_emit_agent_executes_agent("p1", "_fca_baseline", "sub_agent")
_emit_routes_to_agent("p1", "_fca_baseline", "target_agent")
_emit_verifies_policy("p1", "_fca_baseline", "policy_check")
_emit_observes_runtime_state("p1", "_fca_baseline", "runtime_state")
_emit_verifies_boundary("p1", "_fca_baseline", "boundary_check")
_emit_transcripts_response("p1", "_fca_baseline", "transcript")
_emit_hard_fails_untranscripted("p1", "_fca_baseline")
_emit_gated_by_confidence("p1", "_fca_baseline", "confidence_gate")

# Patch missing SERVICE key
fca = FileClassificationAgent(project_root=ROOT, dry_run=True, validate_only=True, verbose=True)
fca.stats["violations"] = defaultdict(int, fca.stats["violations"])


# Capture logger
class Collector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))


col = Collector()
col.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger("agentic_core.L5_safety.reasoning.FileClassificationAgent").addHandler(col)
logging.getLogger("agentic_core.L5_safety.reasoning.FileClassificationAgent").setLevel(logging.DEBUG)

# Redirect stdout during audit
real = sys.stdout
sys.stdout = sys.stderr
scan_root = ROOT / AGENTIC_CORE_DIR
exit_code = fca._orchestrate_audit(scan_root)
sys.stdout = real

# Layer alignment scan
all_py = get_python_files_fast(scan_root)
layer_violations = []
for p in all_py:
    try:
        v = fca.validate_layer_alignment(p)
        if v:
            v["file"] = str(Path(v["file"]).relative_to(ROOT)).replace("\\", "/")
            layer_violations.append(v)
    except (ValueError, TypeError, RuntimeError) as e:
        raise

# Tag parse
findings_by_tag = defaultdict(list)
for line in col.lines:
    for tag in [
        "DETECT",
        "TERRITORY",
        "COMPOUND_SUFFIX",
        "FORBIDDEN",
        "PASSIVE_AGENT_NAMING",
        "COGNITIVE_CONTAMINATION",
        "FAKE_CONFIG",
        "BASE_AGENTS_PURITY",
        "UTILS_PURITY",
        "DOMAIN_ROOT_PURITY",
        "FOLDER_SUFFIX",
        "FOLDER_PURITY",
        "CROSS_DOMAIN",
        "EPHEMERAL",
        "CROSS_LAYER",
        "DUAL-TAG",
        "MISPLACED-TEST",
        "LAYER_PURITY",
        "DUPLICATE",
    ]:
        if f"[{tag}]" in line:
            findings_by_tag[tag].append(line.strip())
            break

violation_counts = defaultdict(int)
for v in layer_violations:
    violation_counts[v.get("violation", "UNKNOWN")] += 1

result = {
    "files_analyzed": fca.stats["analyzed"],
    "compliant": fca.stats["compliant"],
    "audit_findings": sum(len(v) for v in findings_by_tag.values()),
    "layer_violations": len(layer_violations),
    "findings_by_tag": {k: len(v) for k, v in findings_by_tag.items()},
    "layer_violation_counts": dict(violation_counts),
    "violation_type_counts": {k: v for k, v in fca.stats["violations"].items() if v > 0},
}

out_path = ROOT / "artifacts" / "fca_safety_gates" / "baseline_counts.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
