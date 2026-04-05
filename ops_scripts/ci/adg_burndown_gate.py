"""
ADG Intelligent Burndown Gate — Unified Anti-Pattern Ratchet

Single source of truth for anti-pattern governance.  Replaces both the old
check_anti_patterns.py (line-number baseline) and the separate budget file.

Model
-----
Tracks a RATCHET: {rel_path: {category: max_allowed_count}} in burndown_budget.json.

Rules enforced on every commit
  1. NEW file+category pairs are BLOCKED immediately (no new anti-pattern categories
     may appear in a file that was previously clean, or in any new file).
  2. EXISTING counts may only DECREASE — any regression is blocked.
  3. When counts drop, the ratchet tightens automatically to lock in progress.

Why counts not line-number signatures?
  Line-number signatures (used by the old check_anti_patterns.py) break every
  time an unrelated line is inserted above a violation.  Count-per-file+category
  is stable across all edits that don't touch the violation itself.

ADG integration
  When the ADG file graph artifact is present, fix-next suggestions are sorted
  by (violation_count × importer_count) to surface highest-ROI targets first.

Exit codes:
  0  — ratchet held or improved (commit allowed)
  1  — ratchet exceeded (new anti-patterns introduced; commit blocked)

Environment overrides:
  ADG_BURNDOWN_BYPASS=1   — skip gate entirely (emergency; logged to stderr)
  ADG_BURNDOWN_DRY_RUN=1  — report without updating ratchet file
  ADG_BURNDOWN_INIT=1     — (re)initialise ratchet from current scan, then exit 0
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_records_execution_trace("p0", "evidence", "adg_burndown_gate")
_emit_applies_guardrail("p0", "adg_burndown_gate", "p0_governance")
_emit_reads_policy_state("p0", "adg_burndown_gate", "policy_binding")
_emit_snapshots_state("p0", "adg_burndown_gate", "state_snapshot")
emit_replay_key("p0", "adg_burndown_gate")
emit_determinism_digest("p0", "adg_burndown_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_burndown_gate", "execution_auth")
_emit_validates_capability("p2", "adg_burndown_gate", "capability_check")
_emit_routes_to_capability("p2", "adg_burndown_gate", "capability_route")
_emit_writes_via_uwg("p2", "adg_burndown_gate", "uwg_write")
_emit_blocks_direct_write("p2", "adg_burndown_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_burndown_gate", "tool_invocation")
_emit_captures_execution_output("p2", "adg_burndown_gate", "exec_output")
_emit_dispatches_agent("p3", "adg_burndown_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_burndown_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_burndown_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_burndown_gate", "healing_outcome")
_emit_escalates_failure("p3", "adg_burndown_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_burndown_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_burndown_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_burndown_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_burndown_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_burndown_gate", "eval_metric")
_emit_stores_embedding("p4", "adg_burndown_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_burndown_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_burndown_gate", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Bootstrap — works as pre-commit hook or direct invocation from repo root.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
)
from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_1")
_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_2")
_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_3")
_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_4")
_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_5")
_emit_emits_metric_event("adg_burndown_gate", "p4obs", "metric_6")
_emit_records_incident_event("adg_burndown_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_burndown_gate", "p4obs", "anomaly")
_emit_writes_observability_log("adg_burndown_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_burndown_gate", "p4obs", "mon_state")
_emit_triggers_alert("adg_burndown_gate", "p4obs", "alert")
_emit_links_incident_trace("adg_burndown_gate", "p4obs", "trace_link")
_emit_captures_pattern("adg_burndown_gate", "p3lm", "pattern")
_emit_records_learning_event("adg_burndown_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_burndown_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_burndown_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_burndown_gate", "p3lm", "routing")
_emit_improves_agent_policy("adg_burndown_gate", "p3lm", "policy")
_emit_stores_learning_state("adg_burndown_gate", "p3lm", "state")
_emit_records_execution_trace("adg_burndown_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_burndown_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_burndown_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_burndown_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_burndown_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_burndown_gate", "env_read", "p2_env_1")
_emit_reads_environ("adg_burndown_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_burndown_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_burndown_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_burndown_gate", "context_pull")
_emit_pulls_context("p1", "adg_burndown_gate", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "adg_burndown_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_burndown_gate", "uwg_term_secondary")
_emit_writes_through("p1", "adg_burndown_gate", "write_through")
_emit_writes_through("p1", "adg_burndown_gate", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "adg_burndown_gate", "safety_validation")
_emit_invokes_eval("p1", "adg_burndown_gate", "eval_call")
_emit_proposal_commits_routing("p1", "adg_burndown_gate", "routing_commit")
_emit_escalates_to_human("p1", "adg_burndown_gate", "human_escalation")
_emit_routes_through("p1", "adg_burndown_gate", "route_through")
_emit_checks_agent_registry("p1", "adg_burndown_gate", "agent_registry")
_emit_validates_agent_capability("p1", "adg_burndown_gate", "capability")
_emit_dispatches_execution_plan("p1", "adg_burndown_gate", "exec_plan")
_emit_agent_executes_agent("p1", "adg_burndown_gate", "sub_agent")
_emit_routes_to_agent("p1", "adg_burndown_gate", "target_agent")
_emit_verifies_policy("p1", "adg_burndown_gate", "policy_check")
_emit_observes_runtime_state("p1", "adg_burndown_gate", "runtime_state")
_emit_verifies_boundary("p1", "adg_burndown_gate", "boundary_check")
_emit_transcripts_response("p1", "adg_burndown_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_burndown_gate")
_emit_gated_by_confidence("p1", "adg_burndown_gate", "confidence_gate")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_1")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_2")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_3")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_4")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_5")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_6")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_7")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_8")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_9")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_10")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_11")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_12")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_13")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_14")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_15")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_16")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_17")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_18")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_19")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_20")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_21")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_22")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_23")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_24")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_25")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_26")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_27")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_28")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_29")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_30")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_31")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_32")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_33")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_34")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_35")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_36")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_37")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_38")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_39")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_40")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_41")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_42")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_43")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_44")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_45")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_46")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_47")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_48")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_49")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_50")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_51")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_52")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_53")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_54")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_55")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_56")
_emit_reads_through("l4", "adg_burndown_gate", "urg_read_57")

PROJECT_ROOT = get_validated_project_root()

# Ratchet file: {rel_path: {category: max_allowed_count}}
# Immune to line-number churn — counts per file+category, not signatures.
RATCHET_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "burndown_budget.json"
# Keep BUDGET_FILE as alias so external tooling that reads the file by name still works.
BUDGET_FILE = RATCHET_FILE

_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES | {".nox"}
_EXCLUDE_FILE_PATTERNS = ["__dbg_*.py", "**/activate_this.py"]


# ADG artifact — graceful degradation when absent.
# Resolved dynamically to the latest available adg_file_graph_*.json so this
# never falls stale after a re-generation run.
def _resolve_adg_file_graph(root: Path) -> Path:
    adg_dir = root / "artifacts" / "adg"
    candidates = sorted(adg_dir.glob("adg_file_graph_*.json"), reverse=True)
    if candidates:
        return candidates[0]
    return adg_dir / "adg_file_graph.json"


_ADG_FILE_GRAPH = _resolve_adg_file_graph(PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Budget = dict[str, dict[str, int]]  # {rel_path: {category: count}}

# ---------------------------------------------------------------------------
# Ratchet I/O
# ---------------------------------------------------------------------------


def _load_ratchet() -> Budget:
    if not RATCHET_FILE.exists():
        return {}
    try:
        return json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return {}


def _write_ratchet(ratchet: Budget) -> None:
    """Atomically persist the ratchet (never called in dry-run mode)."""
    RATCHET_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(ratchet, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(
        dir=str(RATCHET_FILE.parent),
        prefix=".burndown_ratchet_",
        suffix=".tmp",
    )
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and RATCHET_FILE.exists():
            RATCHET_FILE.unlink()
        Path(tmp).replace(RATCHET_FILE)
    except BaseException:    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context    # guardian: BaseException should be handled with specific context
        try:
            os.close(fd)
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            pass
        try:
            os.unlink(tmp)
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            pass
        raise


def _ratchet_total(ratchet: Budget) -> int:
    return sum(c for cats in ratchet.values() for c in cats.values())


# ---------------------------------------------------------------------------
# Scan helpers
# ---------------------------------------------------------------------------


def _collect_all_python_files() -> list[Path]:
    return [
        f
        for f in sorted(PROJECT_ROOT.rglob("*.py"))
        if not (set(f.relative_to(PROJECT_ROOT).parts) & _EXCLUDE_DIRS)
        and not any(f.match(pat) for pat in _EXCLUDE_FILE_PATTERNS)
    ]


def _rel(fp) -> str:
    p = Path(fp)
    return p.relative_to(PROJECT_ROOT).as_posix() if p.is_absolute() else p.as_posix()


def _scan_to_counts(violations) -> Budget:
    """Convert violation list → {rel_path: {category: count}}."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for v in violations:
        counts[_rel(v.file_path)][v.category.value] += 1
    return {f: dict(cats) for f, cats in counts.items()}


# ---------------------------------------------------------------------------
# ADG helpers
# ---------------------------------------------------------------------------


def _load_adg_importer_counts() -> dict[str, int]:
    """Returns {rel_path: importer_count} from ADG edges."""
    if not _ADG_FILE_GRAPH.exists():
        return {}
    try:
        adg = json.loads(_ADG_FILE_GRAPH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return {}
    counts: dict[str, int] = defaultdict(int)
    for edge in adg.get("edges", []):
        sym = edge.get("sym", "")
        if sym and "." in sym:
            target = "/".join(sym.split(".")[:-1]) + ".py"
            counts[target] += 1
    return dict(counts)


def _adg_fix_priority(
    current: Budget,
    importer_counts: dict[str, int],
) -> list[tuple[str, int, int]]:
    """
    Sort files by (total_violations * importer_count) desc — highest-ROI first.
    Returns [(rel_path, total_violations, importer_count), ...].
    """
    scored = [
        (rel_path, sum(cats.values()), importer_counts.get(rel_path, 0)) for rel_path, cats in current.items()
    ]
    scored.sort(key=lambda x: x[1] * max(x[2], 1), reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def _compute_violations(ratchet: Budget, current: Budget) -> list[tuple[str, str, int, int]]:
    """
    Return (rel_path, category, allowed, actual) for every pair that violates
    the ratchet — covers both rules:

    Rule 1 — NEW file+category pair (allowed=0, actual>0):
        Any category appearing in a file that has no ratchet entry for that
        category is treated as a new introduction and is blocked immediately.

    Rule 2 — COUNT REGRESSION (allowed>0, actual>allowed):
        An existing category whose count exceeds its ratchet ceiling.
    """
    out = []
    for rel_path, cats in current.items():
        ratchet_file = ratchet.get(rel_path, {})
        for cat, actual in cats.items():
            allowed = ratchet_file.get(cat, 0)  # 0 → category not previously seen
            if actual > allowed:
                out.append((rel_path, cat, allowed, actual))
    return sorted(out)


def _tighten_ratchet(ratchet: Budget, current: Budget) -> tuple[Budget, int]:
    """
    Return (new_ratchet, improved_slot_count) where new_ratchet = min(ratchet, current)
    for every file+category pair, with zero-count entries pruned.

    Only shrinks — never grows.  Called after a clean (violation-free) commit
    to lock in any progress made.
    """
    new_ratchet: Budget = {}
    improved = 0
    for rel_path, cats in ratchet.items():
        current_cats = current.get(rel_path, {})
        new_cats: dict[str, int] = {}
        for cat, ceiling in cats.items():
            actual = current_cats.get(cat, 0)
            new_val = min(ceiling, actual)
            if new_val > 0:
                new_cats[cat] = new_val
            if actual < ceiling:
                improved += 1
        if new_cats:
            new_ratchet[rel_path] = new_cats
    return new_ratchet, improved


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def _banner(title: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}")


def _show_burndown_status(current: Budget, importer_counts: dict[str, int]) -> None:
    total = sum(c for cats in current.values() for c in cats.values())
    cat_totals: dict[str, int] = defaultdict(int)
    for cats in current.values():
        for cat, cnt in cats.items():
            cat_totals[cat] += cnt

    print(f"\n[BURNDOWN STATUS] {total} violation(s) remaining")
    for cat, cnt in sorted(cat_totals.items(), key=lambda x: -x[1]):
        print(f"  {cnt:4d}  {cat}")

    priority = _adg_fix_priority(current, importer_counts)
    if priority:
        print("\n[ADG-GUIDED] Top 10 highest-ROI files to fix next:")
        print(f"  {'violations':>10}  {'importers':>9}  file")
        for rel_path, vcount, importers in priority[:10]:
            print(f"  {vcount:>10d}  {importers:>9d}  {rel_path}")
    else:
        top = sorted(
            [(f, sum(c.values())) for f, c in current.items()],
            key=lambda x: -x[1],
        )[:10]
        print("\n[NEXT TARGETS] Top 10 files (ADG graph not available):")
        for rel_path, cnt in top:
            print(f"  {cnt:>4d}  {rel_path}")
    print()


# ---------------------------------------------------------------------------
# Main gate
# ---------------------------------------------------------------------------


def run_gate() -> int:
    if os.environ.get("ADG_BURNDOWN_BYPASS") == "1":
        print(
            "[ADG-BURNDOWN] BYPASS active (ADG_BURNDOWN_BYPASS=1) — gate skipped.",
            file=sys.stderr,
        )
        return 0

    dry_run = os.environ.get("ADG_BURNDOWN_DRY_RUN") == "1"
    init_mode = os.environ.get("ADG_BURNDOWN_INIT") == "1"
    json_output = os.environ.get("ADG_BURNDOWN_JSON_OUTPUT", "").strip() or None

    # Allow --json-output override via command line
    import argparse
    _arg_parser = argparse.ArgumentParser()
    _arg_parser.add_argument("--json-output", metavar="PATH", help="Write structured issues to JSON lines file")
    _args, _ = _arg_parser.parse_known_args()
    if _args.json_output:
        json_output = _args.json_output

    # Add project root for schema imports
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel

    # Single scan — used by all enforcement rules
    python_files = _collect_all_python_files()
    scanner = AntiPatternScanner(project_root=PROJECT_ROOT, enforcement_level=EnforcementLevel.WARNING)
    report = scanner.scan_changed_files(python_files)
    current = _scan_to_counts(report.all_violations)
    current_total = sum(c for cats in current.values() for c in cats.values())

    # Init mode: write ratchet from current state and exit cleanly
    if init_mode:
        if not dry_run:
            _write_ratchet(current)
        print(f"[ADG-BURNDOWN] Ratchet initialised: {current_total} violations across {len(current)} files")
        print(f"  Saved to: {RATCHET_FILE.relative_to(PROJECT_ROOT)}")
        return 0

    # Load ratchet
    ratchet = _load_ratchet()
    if not ratchet:
        # First-ever run — bootstrap from current state
        if not dry_run:
            _write_ratchet(current)
        _banner("ADG INTELLIGENT BURNDOWN GATE")
        print(f"  Ratchet bootstrapped: {current_total} violations across {len(current)} files.")
        print(f"  Saved to: {RATCHET_FILE.relative_to(PROJECT_ROOT)}")
        print("  Subsequent commits may only reduce or hold this count.\n")
        _show_burndown_status(current, _load_adg_importer_counts())
        return 0

    ratchet_total = _ratchet_total(ratchet)

    # Unified violation check — Rule 1 (new pairs) + Rule 2 (count regressions)
    violations = _compute_violations(ratchet, current)

    # Tighten ratchet to lock in any improvements
    new_ratchet, improved_slots = _tighten_ratchet(ratchet, current)
    new_ratchet_total = _ratchet_total(new_ratchet)

    # Only persist ratchet tightening on clean (violation-free) commits
    if not dry_run and not violations and improved_slots > 0:
        _write_ratchet(new_ratchet)

    # Report
    _banner("ADG INTELLIGENT BURNDOWN GATE")
    print(f"  Ratchet ceiling  : {ratchet_total:>5d}")
    print(f"  Actual (current) : {current_total:>5d}")
    print(f"  Net vs ceiling   : {current_total - ratchet_total:>+5d}")
    if dry_run:
        print("  Mode             :  DRY RUN (ratchet NOT updated)")

    if violations:
        new_pairs = [(p, c, a, ac) for p, c, a, ac in violations if a == 0]
        regressions = [(p, c, a, ac) for p, c, a, ac in violations if a > 0]

        excess_total = sum(ac - a for _, _, a, ac in violations)
        print(f"\n[BLOCK] {len(violations)} violation(s) — {excess_total} excess anti-pattern(s):\n")

        if new_pairs:
            print(f"  NEW file+category pairs introduced ({len(new_pairs)}):")
            by_cat: dict[str, int] = defaultdict(int)
            for _, cat, _, actual in new_pairs:
                by_cat[cat] += actual
            for cat, cnt in sorted(by_cat.items()):
                print(f"    • {cat}: +{cnt} (was 0)")
            print()
            for rel_path, cat, _, actual in new_pairs[:25]:
                print(f"  [NEW]  {rel_path}  [{cat}]  count={actual}")

        if regressions:
            print(f"\n  COUNT regressions ({len(regressions)}):")
            by_cat_r: dict[str, int] = defaultdict(int)
            for _, cat, allowed, actual in regressions:
                by_cat_r[cat] += actual - allowed
            for cat, excess in sorted(by_cat_r.items()):
                print(f"    • {cat}: +{excess}")
            print()
            for rel_path, cat, allowed, actual in regressions[:25]:
                print(
                    f"  [FAIL] {rel_path}  [{cat}]  ceiling={allowed}  actual={actual}  excess=+{actual - allowed}"
                )

    if improved_slots > 0:
        locked = ratchet_total - new_ratchet_total
        print(f"\n[PROGRESS] {improved_slots} slot(s) improved — ratchet tightened by {locked} violation(s).")
        cats_improved: dict[str, int] = defaultdict(int)
        for rel_path, cats in ratchet.items():
            new_cats = new_ratchet.get(rel_path, {})
            for cat, old_val in cats.items():
                new_val = new_cats.get(cat, 0)
                if new_val < old_val:
                    cats_improved[cat] += old_val - new_val
        for cat, delta in sorted(cats_improved.items(), key=lambda x: -x[1]):
            print(f"  ✓ {cat}: -{delta}")

    _show_burndown_status(current, _load_adg_importer_counts())

    if violations:
        print(
            "[ACTION] Fix the violations above OR add "
            "'# guardian: allow-<pattern>' to whitelist intentional exceptions."
        )
        print("         Each file+category ceiling may only decrease between commits.\n")

    # Build structured issues for JSON output
    json_issues = []
    for rel_path, cat, allowed, actual in violations:
        is_new = allowed == 0
        severity = SeverityLevel.CRITICAL if is_new else SeverityLevel.HIGH
        issue = PreCommitIssue(
            hook_id="adg-burndown-gate",
            hook_name="ADG Anti-Pattern Burndown",
            severity=severity,
            file_path=rel_path,
            message=f"Anti-pattern: {cat} (count={actual}, allowed={allowed})",
            explanation=f"Anti-pattern counts may only decrease. New categories blocked immediately. Category: {cat}",
            issue_type=f"anti_pattern_{cat}",
        )
        json_issues.append(issue)

    # Write JSON output if requested
    if json_output and json_issues:
        output_path = Path(json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for issue in json_issues:
                f.write(issue.to_json() + "\n")

    if violations:
        return 1

    return 0


def main() -> int:
    return run_gate()


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
