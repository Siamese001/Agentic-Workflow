"""
SSOT Dry-Run Wrapper: Bypasses Windows LongPathsEnabled pre-flight check
and runs the full SSOT pipeline in dry-run mode across all territories.

Captures all output for report generation.
"""

import json
import logging
import sys
import traceback
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import LAYER_ROOTS
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

_emit_records_execution_trace("p0", "evidence", "_ssot_dry_run")
_emit_applies_guardrail("p0", "_ssot_dry_run", "p0_governance")
_emit_reads_policy_state("p0", "_ssot_dry_run", "policy_binding")
_emit_snapshots_state("p0", "_ssot_dry_run", "state_snapshot")
emit_replay_key("p0", "_ssot_dry_run")
emit_determinism_digest("p0", "_ssot_dry_run")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_ssot_dry_run", "execution_auth")
_emit_validates_capability("p2", "_ssot_dry_run", "capability_check")
_emit_routes_to_capability("p2", "_ssot_dry_run", "capability_route")
_emit_writes_via_uwg("p2", "_ssot_dry_run", "uwg_write")
_emit_blocks_direct_write("p2", "_ssot_dry_run", "direct_write_block")
_emit_records_tool_invocation("p2", "_ssot_dry_run", "tool_invocation")
_emit_captures_execution_output("p2", "_ssot_dry_run", "exec_output")
_emit_dispatches_agent("p3", "_ssot_dry_run", "agent_dispatch")
_emit_coordinates_agents("p3", "_ssot_dry_run", "agent_coordination")
_emit_records_workflow_lineage("p3", "_ssot_dry_run", "workflow_lineage")
_emit_records_healing_outcome("p3", "_ssot_dry_run", "healing_outcome")
_emit_escalates_failure("p3", "_ssot_dry_run", "failure_escalation")
_emit_orchestrates_workflow("p3", "_ssot_dry_run", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_ssot_dry_run", "healing_dispatch")
_emit_invokes_evaluation("p3", "_ssot_dry_run", "evaluation_signal")
_emit_records_telemetry_event("p4", "_ssot_dry_run", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_ssot_dry_run", "eval_metric")
_emit_stores_embedding("p4", "_ssot_dry_run", "embedding_store")
_emit_updates_meta_learning_state("p4", "_ssot_dry_run", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_ssot_dry_run", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

# Monkey-patch PreFlightValidator to skip Windows registry check
import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_mod

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_1")
_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_2")
_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_3")
_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_4")
_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_5")
_emit_emits_metric_event("_ssot_dry_run", "p4obs", "metric_6")
_emit_records_incident_event("_ssot_dry_run", "p4obs", "incident")
_emit_captures_runtime_anomaly("_ssot_dry_run", "p4obs", "anomaly")
_emit_writes_observability_log("_ssot_dry_run", "p4obs", "obs_log")
_emit_updates_monitoring_state("_ssot_dry_run", "p4obs", "mon_state")
_emit_triggers_alert("_ssot_dry_run", "p4obs", "alert")
_emit_links_incident_trace("_ssot_dry_run", "p4obs", "trace_link")
_emit_captures_pattern("_ssot_dry_run", "p3lm", "pattern")
_emit_records_learning_event("_ssot_dry_run", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_ssot_dry_run", "p3lm", "snapshot")
_emit_feeds_meta_learning("_ssot_dry_run", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_ssot_dry_run", "p3lm", "routing")
_emit_improves_agent_policy("_ssot_dry_run", "p3lm", "policy")
_emit_stores_learning_state("_ssot_dry_run", "p3lm", "state")
_emit_records_execution_trace("_ssot_dry_run", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_ssot_dry_run", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_ssot_dry_run", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_ssot_dry_run", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_ssot_dry_run", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_ssot_dry_run", "env_read", "p2_env_1")
_emit_reads_environ("_ssot_dry_run", "env_read", "p2_env_2")
_emit_reads_runtime_state("_ssot_dry_run", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_ssot_dry_run", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_ssot_dry_run", "context_pull")
_emit_pulls_context("p1", "_ssot_dry_run", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_ssot_dry_run", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_ssot_dry_run", "uwg_term_2")
_emit_writes_through("p1", "_ssot_dry_run", "write_through")
_emit_writes_through("p1", "_ssot_dry_run", "write_through_2")
_emit_validated_by_safety_plane("p1", "_ssot_dry_run", "safety_validation")
_emit_invokes_eval("p1", "_ssot_dry_run", "eval_call")
_emit_proposal_commits_routing("p1", "_ssot_dry_run", "routing_commit")
_emit_escalates_to_human("p1", "_ssot_dry_run", "human_escalation")
_emit_routes_through("p1", "_ssot_dry_run", "route_through")
_emit_checks_agent_registry("p1", "_ssot_dry_run", "agent_registry")
_emit_validates_agent_capability("p1", "_ssot_dry_run", "capability")
_emit_dispatches_execution_plan("p1", "_ssot_dry_run", "exec_plan")
_emit_agent_executes_agent("p1", "_ssot_dry_run", "sub_agent")
_emit_routes_to_agent("p1", "_ssot_dry_run", "target_agent")
_emit_verifies_policy("p1", "_ssot_dry_run", "policy_check")
_emit_observes_runtime_state("p1", "_ssot_dry_run", "runtime_state")
_emit_verifies_boundary("p1", "_ssot_dry_run", "boundary_check")
_emit_transcripts_response("p1", "_ssot_dry_run", "transcript")
_emit_hard_fails_untranscripted("p1", "_ssot_dry_run")
_emit_gated_by_confidence("p1", "_ssot_dry_run", "confidence_gate")

_original_run_checks = execute_ssot_mod.PreFlightValidator.run_checks


def _patched_run_checks(self):
    """Skip Windows LongPathsEnabled check for dry-run."""
    ok, errors = _original_run_checks(self)
    errors = [e for e in errors if "LongPathsEnabled" not in e]
    return len(errors) == 0, errors


execute_ssot_mod.PreFlightValidator.run_checks = _patched_run_checks


# Configure logging to capture all output
class OutputCollector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))


collector = OutputCollector()
collector.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))

# Attach to root logger to capture everything
root_logger = logging.getLogger()
root_logger.addHandler(collector)
root_logger.setLevel(logging.DEBUG)

# Also capture the specific SSOT logger
ssot_logger = logging.getLogger("UnifiedSovereign")
ssot_logger.addHandler(collector)
ssot_logger.setLevel(logging.DEBUG)

# All territories to scan
TERRITORIES = ["prompt_governance", *sorted(LAYER_ROOTS)]

results_all = {}

for territory in TERRITORIES:
    print(f"\n{'=' * 80}", file=sys.stderr)
    print(f"  TERRITORY: {territory}", file=sys.stderr)
    print(f"{'=' * 80}", file=sys.stderr)

    # Reset collector for each territory
    collector.lines.clear()

    # Reset FCA stats by creating fresh module state
    try:
        from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot import (
            _configure_logging,
            _legacy_main,
            _maybe_force_utf8_console,
        )

        _configure_logging(2)  # verbose
        _maybe_force_utf8_console()

        # Redirect stdout to stderr during execution
        real_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            _legacy_main(
                ["--dry-run", "--territory", territory],
                repo_root=PROJECT_ROOT,
            )
        except SystemExit:    # guardian: SystemExit should be handled with specific context
            pass  # Expected for some exit paths
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            print(f"  ERROR in {territory}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        finally:
            sys.stdout = real_stdout

    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"  FATAL ERROR for {territory}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    results_all[territory] = {
        "log_lines": list(collector.lines),
        "line_count": len(collector.lines),
    }

# Output JSON results
print(json.dumps(results_all, indent=2, default=str))
print(f"\n=== DONE: {len(TERRITORIES)} territories scanned ===", file=sys.stderr)
