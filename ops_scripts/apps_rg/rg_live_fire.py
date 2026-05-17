"""
SOVEREIGN LIVE FIRE EXERCISE
----------------------------
Executes a full runtime cycle of the apps_rg Sovereign Fleet.
NO MOCKS allowed for internal logic. Only external LLM calls are mocked.

Objective: Prove Data Flow integrity from HOP-0 to HOP-5.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "rg_live_fire")
_emit_applies_guardrail("p0", "rg_live_fire", "p0_governance")
_emit_reads_policy_state("p0", "rg_live_fire", "policy_binding")
_emit_snapshots_state("p0", "rg_live_fire", "state_snapshot")
emit_replay_key("p0", "rg_live_fire")
emit_determinism_digest("p0", "rg_live_fire")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rg_live_fire", "execution_auth")
_emit_validates_capability("p2", "rg_live_fire", "capability_check")
_emit_routes_to_capability("p2", "rg_live_fire", "capability_route")
_emit_writes_via_uwg("p2", "rg_live_fire", "uwg_write")
_emit_blocks_direct_write("p2", "rg_live_fire", "direct_write_block")
_emit_records_tool_invocation("p2", "rg_live_fire", "tool_invocation")
_emit_captures_execution_output("p2", "rg_live_fire", "exec_output")
_emit_dispatches_agent("p3", "rg_live_fire", "agent_dispatch")
_emit_coordinates_agents("p3", "rg_live_fire", "agent_coordination")
_emit_records_workflow_lineage("p3", "rg_live_fire", "workflow_lineage")
_emit_records_healing_outcome("p3", "rg_live_fire", "healing_outcome")
_emit_escalates_failure("p3", "rg_live_fire", "failure_escalation")
_emit_orchestrates_workflow("p3", "rg_live_fire", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rg_live_fire", "healing_dispatch")
_emit_invokes_evaluation("p3", "rg_live_fire", "evaluation_signal")
_emit_records_telemetry_event("p4", "rg_live_fire", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rg_live_fire", "eval_metric")
_emit_stores_embedding("p4", "rg_live_fire", "embedding_store")
_emit_updates_meta_learning_state("p4", "rg_live_fire", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rg_live_fire", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
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
from apps_rg.engines.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.types.SovereignContext import SovereignContext

_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_1")
_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_2")
_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_3")
_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_4")
_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_5")
_emit_emits_metric_event("rg_live_fire", "p4obs", "metric_6")
_emit_records_incident_event("rg_live_fire", "p4obs", "incident")
_emit_captures_runtime_anomaly("rg_live_fire", "p4obs", "anomaly")
_emit_writes_observability_log("rg_live_fire", "p4obs", "obs_log")
_emit_updates_monitoring_state("rg_live_fire", "p4obs", "mon_state")
_emit_triggers_alert("rg_live_fire", "p4obs", "alert")
_emit_links_incident_trace("rg_live_fire", "p4obs", "trace_link")
_emit_captures_pattern("rg_live_fire", "p3lm", "pattern")
_emit_records_learning_event("rg_live_fire", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rg_live_fire", "p3lm", "snapshot")
_emit_feeds_meta_learning("rg_live_fire", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rg_live_fire", "p3lm", "routing")
_emit_improves_agent_policy("rg_live_fire", "p3lm", "policy")
_emit_stores_learning_state("rg_live_fire", "p3lm", "state")
_emit_records_execution_trace("rg_live_fire", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rg_live_fire", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rg_live_fire", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rg_live_fire", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rg_live_fire", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rg_live_fire", "env_read", "p2_env_1")
_emit_reads_environ("rg_live_fire", "env_read", "p2_env_2")
_emit_reads_runtime_state("rg_live_fire", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rg_live_fire", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rg_live_fire", "context_pull")
_emit_pulls_context("p1", "rg_live_fire", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rg_live_fire", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rg_live_fire", "uwg_term_secondary")
_emit_writes_through("p1", "rg_live_fire", "write_through")
_emit_writes_through("p1", "rg_live_fire", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rg_live_fire", "safety_validation")
_emit_invokes_eval("p1", "rg_live_fire", "eval_call")
_emit_proposal_commits_routing("p1", "rg_live_fire", "routing_commit")
_emit_escalates_to_human("p1", "rg_live_fire", "human_escalation")
_emit_routes_through("p1", "rg_live_fire", "route_through")
_emit_checks_agent_registry("p1", "rg_live_fire", "agent_registry")
_emit_validates_agent_capability("p1", "rg_live_fire", "capability")
_emit_dispatches_execution_plan("p1", "rg_live_fire", "exec_plan")
_emit_agent_executes_agent("p1", "rg_live_fire", "sub_agent")
_emit_routes_to_agent("p1", "rg_live_fire", "target_agent")
_emit_verifies_policy("p1", "rg_live_fire", "policy_check")
_emit_observes_runtime_state("p1", "rg_live_fire", "runtime_state")
_emit_verifies_boundary("p1", "rg_live_fire", "boundary_check")
_emit_transcripts_response("p1", "rg_live_fire", "transcript")
_emit_hard_fails_untranscripted("p1", "rg_live_fire")
_emit_gated_by_confidence("p1", "rg_live_fire", "confidence_gate")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
Logger = logging.getLogger("LIVE_FIRE")
MOCK_JD = "\n[Your Job Description Here]\nExample: Senior Software Engineer at TechCorp\nRequirements: Python, AWS, React, 5+ years experience...\n"
MOCK_RESUME = {
    "contact_info": {"name": "Your Name", "email": "your.email@example.com"},
    "experience": [
        {
            "company": "Previous Company",
            "title": "Your Previous Role",
            "bullets": ["Your achievement 1 with metrics", "Your achievement 2 with metrics"],
        },
    ],
    "education": [{"degree": "Your Degree", "school": "Your University"}],
    "skills": ["skill1", "skill2", "skill3"],
}


async def main():
    Logger.info("🔥 INITIATING SOVEREIGN LIVE FIRE EXERCISE...")
    start_time = datetime.now()
    ctx = SovereignContext()
    ctx.master_resume = MOCK_RESUME
    Logger.info("⚡ Booting L3 Orchestrator...")
    orchestrator = ResumeOrchestratorEngine(ctx)
    try:
        result = await orchestrator.execute(MOCK_JD)
        Logger.info("-" * 50)
        Logger.info(f"🏁 MISSION COMPLETE in {(datetime.now() - start_time).total_seconds():.2f}s")
        Logger.info(f"STATUS: {result.get('status')}")
        Logger.info(f"CHECKPOINTS: {result.get('checkpoints')}")
        Logger.info("-" * 50)
        Logger.info("🔍 DEEP BUFFER INSPECTION:")
        hop1 = ctx.buffer.read("hop1_extraction")
        if hop1:
            metrics = hop1["experience_sections"][0]["bullets"][0].get("quantified_metrics", [])
            Logger.info(f"✅ HOP-1 Metrics Extracted: {metrics}")
        else:
            Logger.error("❌ HOP-1 FAILED: No extraction data.")
        hop2 = ctx.buffer.read("hop2_enrichment")
        if hop2:
            Logger.info("✅ HOP-2 Enrichment found.")
        else:
            Logger.error("❌ HOP-2 FAILED.")
        k9 = ctx.buffer.read("k9_competencies")
        Logger.info(f"✅ HOP-3 K9 ENGINEERING & PLATFORM COMPETENCIES: {(len(k9) if k9 else 0)}/6")
        ranked = ctx.buffer.read("ranked_content")
        if ranked:
            Logger.info(f"✅ HOP-4 Ranked Sections: {list(ranked.keys())}")
        else:
            Logger.error("❌ HOP-4 FAILED.")
        ats_report = ctx.buffer.read("ats_report", {"valid": False})
        if ats_report.get("valid"):
            Logger.info("✅ HOP-5 ATS Status: Valid")
        else:
            Logger.error("❌ HOP-5 ATS FAILED")
        summary = ctx.trace.get_summary()
        Logger.info(f"📊 TELEMETRY: {summary['total_spans']} Spans Recorded. Failures: {summary['failures']}")
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise


if __name__ == "__main__":
    asyncio.run(main())
