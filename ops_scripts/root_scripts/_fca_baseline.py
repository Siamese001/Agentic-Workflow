"""PHASE 0 WAVE 0.1: FCA baseline reproduction — save artifact for diffing."""

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
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
    except Exception:
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
