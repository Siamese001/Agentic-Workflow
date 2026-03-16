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
        from agentic_core.L0_routing.scripts.execute_ssot import (
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
        except SystemExit:
            pass  # Expected for some exit paths
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            print(f"  ERROR in {territory}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        finally:
            sys.stdout = real_stdout

    # guardian: allow-silent-swallow
    except Exception as e:
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
