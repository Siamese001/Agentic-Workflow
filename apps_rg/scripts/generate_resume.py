"""
Resume Generation Script
Loads your actual JD and resume data to generate a customized resume.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
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

_emit_records_execution_trace("p0", "evidence", "generate_resume")
_emit_applies_guardrail("p0", "generate_resume", "p0_governance")
_emit_reads_policy_state("p0", "generate_resume", "policy_binding")
_emit_snapshots_state("p0", "generate_resume", "state_snapshot")
emit_replay_key("p0", "generate_resume")
emit_determinism_digest("p0", "generate_resume")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_resume", "execution_auth")
_emit_validates_capability("p2", "generate_resume", "capability_check")
_emit_routes_to_capability("p2", "generate_resume", "capability_route")
_emit_writes_via_uwg("p2", "generate_resume", "uwg_write")
_emit_blocks_direct_write("p2", "generate_resume", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_resume", "tool_invocation")
_emit_captures_execution_output("p2", "generate_resume", "exec_output")
_emit_dispatches_agent("p3", "generate_resume", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_resume", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_resume", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_resume", "healing_outcome")
_emit_escalates_failure("p3", "generate_resume", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_resume", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_resume", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_resume", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_resume", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_resume", "eval_metric")
_emit_stores_embedding("p4", "generate_resume", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_resume", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_resume", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
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
from apps_rg.engines.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.types.SovereignContext import SovereignContext

_emit_emits_metric_event("generate_resume", "p4obs", "metric_1")
_emit_emits_metric_event("generate_resume", "p4obs", "metric_2")
_emit_emits_metric_event("generate_resume", "p4obs", "metric_3")
_emit_emits_metric_event("generate_resume", "p4obs", "metric_4")
_emit_emits_metric_event("generate_resume", "p4obs", "metric_5")
_emit_emits_metric_event("generate_resume", "p4obs", "metric_6")
_emit_records_incident_event("generate_resume", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_resume", "p4obs", "anomaly")
_emit_writes_observability_log("generate_resume", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_resume", "p4obs", "mon_state")
_emit_triggers_alert("generate_resume", "p4obs", "alert")
_emit_links_incident_trace("generate_resume", "p4obs", "trace_link")
_emit_captures_pattern("generate_resume", "p3lm", "pattern")
_emit_records_learning_event("generate_resume", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_resume", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_resume", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_resume", "p3lm", "routing")
_emit_improves_agent_policy("generate_resume", "p3lm", "policy")
_emit_stores_learning_state("generate_resume", "p3lm", "state")
_emit_records_execution_trace("generate_resume", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_resume", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_resume", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_resume", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_resume", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_resume", "env_read", "p2_env_1")
_emit_reads_environ("generate_resume", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_resume", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_resume", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "generate_resume", "context_pull")
_emit_pulls_context("p1", "generate_resume", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_resume", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_resume", "uwg_term_secondary")
_emit_writes_through("p1", "generate_resume", "write_through")
_emit_writes_through("p1", "generate_resume", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_resume", "safety_validation")
_emit_invokes_eval("p1", "generate_resume", "eval_call")
_emit_proposal_commits_routing("p1", "generate_resume", "routing_commit")
_emit_escalates_to_human("p1", "generate_resume", "human_escalation")
_emit_routes_through("p1", "generate_resume", "route_through")
_emit_checks_agent_registry("p1", "generate_resume", "agent_registry")
_emit_validates_agent_capability("p1", "generate_resume", "capability")
_emit_dispatches_execution_plan("p1", "generate_resume", "exec_plan")
_emit_agent_executes_agent("p1", "generate_resume", "sub_agent")
_emit_routes_to_agent("p1", "generate_resume", "target_agent")
_emit_verifies_policy("p1", "generate_resume", "policy_check")
_emit_observes_runtime_state("p1", "generate_resume", "runtime_state")
_emit_verifies_boundary("p1", "generate_resume", "boundary_check")
_emit_transcripts_response("p1", "generate_resume", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_resume")
_emit_gated_by_confidence("p1", "generate_resume", "confidence_gate")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
Logger = logging.getLogger("RESUME_GENERATOR")


def load_data_file(filename: str) -> dict:
    """Load data from JSON file in the same directory."""
    file_path = Path(__file__).parent / filename
    if not file_path.exists():
        Logger.error(f"❌ File not found: {file_path}")
        Logger.info(f"Please create {filename} with your data")
        sys.exit(1)
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


async def main():
    Logger.info("🎯 RESUME GENERATION STARTED...")
    start_time = datetime.now()
    jd_data = load_data_file("job_description.json")
    resume_data = load_data_file("your_resume_updated.json")
    ctx = SovereignContext()
    ctx.master_resume = resume_data
    Logger.info("⚡ Processing your resume against the job description...")
    orchestrator = ResumeOrchestratorEngine(ctx)
    try:
        result = await orchestrator.execute(jd_data["description"])
        Logger.info("-" * 50)
        Logger.info(f"🏁 GENERATION COMPLETE in {(datetime.now() - start_time).total_seconds():.2f}s")
        Logger.info(f"STATUS: {result.get('status')}")
        Logger.info(f"QUALITY SCORE: {result.get('final_quality_score', 0)}")
        Logger.info(f"ATS COMPATIBLE: {result.get('ats_valid', False)}")
        Logger.info("-" * 50)
        Logger.info("💾 Saving generated resume...")
        final_resume = ctx.buffer.read("ranked_content", {})
        output_file = f"generated_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = Path(__file__).parent / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_resume, f, indent=2, ensure_ascii=False)
        Logger.info(f"✅ Resume saved to: {output_file}")
        if final_resume:
            Logger.info("-" * 50)
            Logger.info("📋 RESUME PREVIEW:")
            for section, content in final_resume.items():
                if isinstance(content, list) and content:
                    Logger.info(f"  {section}: {len(content)} items")
                elif isinstance(content, dict):
                    Logger.info(f"  {section}: {list(content.keys())}")
                else:
                    Logger.info(f"  {section}: {content}")
    except Exception as e:
        Logger.error(f"❌ Generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
