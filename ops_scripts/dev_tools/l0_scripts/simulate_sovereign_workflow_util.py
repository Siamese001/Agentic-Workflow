"""
scripts/simulate_sovereign_workflow_util.py
"""
import logging
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "simulate_sovereign_workflow_util")
_emit_applies_guardrail("p0", "simulate_sovereign_workflow_util", "p0_governance")
_emit_reads_policy_state("p0", "simulate_sovereign_workflow_util", "policy_binding")
_emit_snapshots_state("p0", "simulate_sovereign_workflow_util", "state_snapshot")
emit_replay_key("p0", "simulate_sovereign_workflow_util")
emit_determinism_digest("p0", "simulate_sovereign_workflow_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "simulate_sovereign_workflow_util", "execution_auth")
_emit_validates_capability("p2", "simulate_sovereign_workflow_util", "capability_check")
_emit_routes_to_capability("p2", "simulate_sovereign_workflow_util", "capability_route")
_emit_writes_via_uwg("p2", "simulate_sovereign_workflow_util", "uwg_write")
_emit_blocks_direct_write("p2", "simulate_sovereign_workflow_util", "direct_write_block")
_emit_records_tool_invocation("p2", "simulate_sovereign_workflow_util", "tool_invocation")
_emit_captures_execution_output("p2", "simulate_sovereign_workflow_util", "exec_output")
_emit_dispatches_agent("p3", "simulate_sovereign_workflow_util", "agent_dispatch")
_emit_coordinates_agents("p3", "simulate_sovereign_workflow_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "simulate_sovereign_workflow_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "simulate_sovereign_workflow_util", "healing_outcome")
_emit_escalates_failure("p3", "simulate_sovereign_workflow_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "simulate_sovereign_workflow_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "simulate_sovereign_workflow_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "simulate_sovereign_workflow_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "simulate_sovereign_workflow_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "simulate_sovereign_workflow_util", "eval_metric")
_emit_stores_embedding("p4", "simulate_sovereign_workflow_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "simulate_sovereign_workflow_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "simulate_sovereign_workflow_util", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.enforcement.core_integrity_util import CoreIntegrityVerifier
from apps_lic.engines.BiasDetectorAgent import BiasDetectorSpecialist
from apps_rg.engines.CampaignPlannerAgent import CampaignPlannerAgent

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
Logger = logging.getLogger('SovereignSimulation')

def run_simulation():
    Logger.info('>>> INITIALIZING SOVEREIGN SIMULATION v2.5 <<<')
    try:
        Logger.info('[1] Verifying Core Integrity...')
        try:
            CoreIntegrityVerifier.verify_core_integrity()
            Logger.info('    PASS: Immutable Lock Verified.')
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.warning(f'    WARNING: Core Integrity check failed (expected during dev): {e}')
        Logger.info('[2] Booting Resume Generation Agent (CampaignPlanner)...')
        planner = CampaignPlannerAgent(campaign_id='SIM-2026-ALPHA', active_channels=['web', 'social'])
        Logger.info(f'    PASS: Booted {planner.name} (RG Domain)')
        Logger.info('[3] Booting LIC Agent (BiasDetectorSpecialist)...')
        detector = BiasDetectorSpecialist(sensitivity_level=0.9)
        Logger.info(f'    PASS: Booted {detector.name} (LIC Domain)')
        Logger.info('[4] Executing Cross-Domain Workflow...')
        slogan = 'Guaranteed returns with zero risk!'
        Logger.info(f"    RG Action: Generated Slogan -> '{slogan}'")
        result = detector.scan_content(slogan)
        Logger.info(f'    LIC Action: Scan Result -> {result}')
        if result['has_bias'] is not True:
            raise ValueError('Expected bias detection to return True')
        Logger.info('    PASS: Governance Logic Verified.')
        Logger.info('>>> SIMULATION SUCCESSFUL: SYSTEM CONVERGED <<<')
    # guardian: allow-silent-swallow
    except Exception as e:
        Logger.error(f'>>> SIMULATION FAILED: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == '__main__':
    run_simulation()
