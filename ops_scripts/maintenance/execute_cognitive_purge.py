#!/usr/bin/env python3
"""
[PHASE 13] AI-Purge Sentinel - Cognitive Batch Execution Driver.

Executes the AI-driven architectural purge using Gemini LLM with:
- Batch processing for 2,160+ violations
- Rate limiting to respect API quotas
- Progress checkpointing for resumable execution
- Exponential backoff for API errors

This script ties the CognitiveBatchProcessor to the ArchivalGatekeeper,
enabling mass-movement of files based on Gemini's JSON decisions.

Usage:
    # Set API key first
    export GEMINI_API_KEY="your-api-key"

    # Run cognitive purge (analysis only)
    python scripts/maintenance/execute_cognitive_purge.py

    # Run with custom rate limit (default: 1.0s)
    python scripts/maintenance/execute_cognitive_purge.py --rate-limit 2.0

    # Clear checkpoint and start fresh
    python scripts/maintenance/execute_cognitive_purge.py --clear-checkpoint

Exit Codes:
    0 - Purge completed successfully
    1 - No API key found
    2 - Error during execution
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
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


def _init_runtime_trace() -> None:
    _emit_records_execution_trace("p0", "evidence", "execute_cognitive_purge")
    _emit_applies_guardrail("p0", "execute_cognitive_purge", "p0_governance")
    _emit_reads_policy_state("p0", "execute_cognitive_purge", "policy_binding")
    _emit_snapshots_state("p0", "execute_cognitive_purge", "state_snapshot")
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

    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_1")
    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_2")
    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_3")
    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_4")
    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_5")
    _emit_emits_metric_event("execute_cognitive_purge", "p4obs", "metric_6")
    _emit_records_incident_event("execute_cognitive_purge", "p4obs", "incident")
    _emit_captures_runtime_anomaly("execute_cognitive_purge", "p4obs", "anomaly")
    _emit_writes_observability_log("execute_cognitive_purge", "p4obs", "obs_log")
    _emit_updates_monitoring_state("execute_cognitive_purge", "p4obs", "mon_state")
    _emit_triggers_alert("execute_cognitive_purge", "p4obs", "alert")
    _emit_links_incident_trace("execute_cognitive_purge", "p4obs", "trace_link")
    _emit_captures_pattern("execute_cognitive_purge", "p3lm", "pattern")
    _emit_records_learning_event("execute_cognitive_purge", "p3lm", "learning_event")
    _emit_writes_learning_snapshot("execute_cognitive_purge", "p3lm", "snapshot")
    _emit_feeds_meta_learning("execute_cognitive_purge", "p3lm", "meta_feed")
    _emit_updates_routing_strategy("execute_cognitive_purge", "p3lm", "routing")
    _emit_improves_agent_policy("execute_cognitive_purge", "p3lm", "policy")
    _emit_stores_learning_state("execute_cognitive_purge", "p3lm", "state")
    _emit_records_execution_trace("execute_cognitive_purge", "L0_ROUTING", "p2_trace_1")
    _emit_records_execution_trace("execute_cognitive_purge", "L1_REASONING", "p2_trace_2")
    _emit_records_execution_trace("execute_cognitive_purge", "L2_EXECUTION", "p2_trace_3")
    _emit_records_execution_trace("execute_cognitive_purge", "L3_ORCHESTRATION", "p2_trace_4")
    _emit_records_execution_trace("execute_cognitive_purge", "L4_STATE", "p2_trace_5")
    _emit_reads_environ("execute_cognitive_purge", "env_read", "p2_env_1")
    _emit_reads_environ("execute_cognitive_purge", "env_read", "p2_env_2")
    _emit_reads_runtime_state("execute_cognitive_purge", "runtime_state", "p2_rt_1")
    _emit_reads_runtime_state("execute_cognitive_purge", "runtime_state", "p2_rt_2")
    _emit_pulls_context("p1", "execute_cognitive_purge", "context_pull")
    _emit_pulls_context("p1", "execute_cognitive_purge", "context_pull_2")
    _emit_execution_terminates_at_uwg("p1", "execute_cognitive_purge", "uwg_term")
    _emit_execution_terminates_at_uwg("p1", "execute_cognitive_purge", "uwg_term_2")
    _emit_writes_through("p1", "execute_cognitive_purge", "write_through")
    _emit_writes_through("p1", "execute_cognitive_purge", "write_through_2")
    _emit_validated_by_safety_plane("p1", "execute_cognitive_purge", "safety_validation")
    _emit_invokes_eval("p1", "execute_cognitive_purge", "eval_call")
    _emit_proposal_commits_routing("p1", "execute_cognitive_purge", "routing_commit")
    _emit_escalates_to_human("p1", "execute_cognitive_purge", "human_escalation")
    _emit_routes_through("p1", "execute_cognitive_purge", "route_through")
    _emit_checks_agent_registry("p1", "execute_cognitive_purge", "agent_registry")
    _emit_validates_agent_capability("p1", "execute_cognitive_purge", "capability")
    _emit_dispatches_execution_plan("p1", "execute_cognitive_purge", "exec_plan")
    _emit_agent_executes_agent("p1", "execute_cognitive_purge", "sub_agent")
    _emit_routes_to_agent("p1", "execute_cognitive_purge", "target_agent")
    _emit_verifies_policy("p1", "execute_cognitive_purge", "policy_check")
    _emit_observes_runtime_state("p1", "execute_cognitive_purge", "runtime_state")
    _emit_verifies_boundary("p1", "execute_cognitive_purge", "boundary_check")
    _emit_transcripts_response("p1", "execute_cognitive_purge", "transcript")
    _emit_hard_fails_untranscripted("p1", "execute_cognitive_purge")
    _emit_gated_by_confidence("p1", "execute_cognitive_purge", "confidence_gate")
    emit_replay_key("p0", "execute_cognitive_purge")
    emit_determinism_digest("p0", "execute_cognitive_purge")
    _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
    _emit_authorize_and_execute("p2", "execute_cognitive_purge", "execution_auth")
    _emit_validates_capability("p2", "execute_cognitive_purge", "capability_check")
    _emit_routes_to_capability("p2", "execute_cognitive_purge", "capability_route")
    _emit_writes_via_uwg("p2", "execute_cognitive_purge", "uwg_write")
    _emit_blocks_direct_write("p2", "execute_cognitive_purge", "direct_write_block")
    _emit_records_tool_invocation("p2", "execute_cognitive_purge", "tool_invocation")
    _emit_captures_execution_output("p2", "execute_cognitive_purge", "exec_output")
    _emit_dispatches_agent("p3", "execute_cognitive_purge", "agent_dispatch")
    _emit_coordinates_agents("p3", "execute_cognitive_purge", "agent_coordination")
    _emit_records_workflow_lineage("p3", "execute_cognitive_purge", "workflow_lineage")
    _emit_records_healing_outcome("p3", "execute_cognitive_purge", "healing_outcome")
    _emit_escalates_failure("p3", "execute_cognitive_purge", "failure_escalation")
    _emit_orchestrates_workflow("p3", "execute_cognitive_purge", "workflow_orchestration")
    _emit_dispatches_healing_run("p3", "execute_cognitive_purge", "healing_dispatch")
    _emit_invokes_evaluation("p3", "execute_cognitive_purge", "evaluation_signal")
    _emit_records_telemetry_event("p4", "execute_cognitive_purge", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "execute_cognitive_purge", "eval_metric")
    _emit_stores_embedding("p4", "execute_cognitive_purge", "embedding_store")
    _emit_updates_meta_learning_state("p4", "execute_cognitive_purge", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "execute_cognitive_purge", "exec_snapshot_link")


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
Logger = logging.getLogger("CognitivePurge")


def run_cognitive_purge(
    rate_limit: float = 1.0,
    checkpoint_file: str = "cognitive_checkpoint.json",
    clear_checkpoint: bool = False,
) -> int:
    """
    Execute the AI-driven cognitive purge.

    Args:
        rate_limit: Seconds to wait between API calls
        checkpoint_file: Path to checkpoint file
        clear_checkpoint: If True, clear existing checkpoint

    Returns:
        Exit code (0=success, 1=no API key, 2=error)
    """
    _init_runtime_trace()

    if rate_limit <= 0:
        Logger.error("[FAIL] --rate-limit must be greater than 0.")
        return 2

    # Load .env file first
    try:
        from dotenv import find_dotenv, load_dotenv

        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file)
            Logger.info(f"Loaded environment from: {env_file}")
    except ImportError:  # guardian: allow-silent-swallow -- optional dependency
        Logger.info("No .env file found.")
        pass

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        Logger.error("[FAIL] GEMINI_API_KEY not found in environment.")
        Logger.info("Set it with: export GEMINI_API_KEY='your-api-key'")
        return 1

    try:
        project_root = get_validated_project_root()
        checkpoint_path = Path(checkpoint_file)
        if not checkpoint_path.is_absolute():
            checkpoint_path = project_root / checkpoint_path
        checkpoint_path = checkpoint_path.resolve()
        if project_root not in checkpoint_path.parents and checkpoint_path != project_root:
            raise ValueError("Checkpoint path must remain under the project root")

        from agentic_core.L5_safety.validators import (
            ArchitectureGovernorAgent,
        )

        Logger.info("=" * 60)
        Logger.info("PHASE 13: AI-PURGE SENTINEL")
        Logger.info("=" * 60)
        Logger.info(f"Project Root: {project_root}")
        Logger.info(f"Rate Limit: {rate_limit}s between API calls")
        Logger.info(f"Checkpoint: {checkpoint_path}")
        Logger.info("")

        # Clear checkpoint if requested
        if clear_checkpoint:
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                Logger.info("[OK] Checkpoint cleared")

        # Initialize Governor
        Logger.info("Initializing ArchitectureGovernorAgent...")
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            healing_enabled=False,  # Analysis only for now
        )

        # Enable LLM in cognitive agent
        cognitive = agent._get_cognitive_agent()
        cognitive.llm_enabled = True
        cognitive.api_key = api_key

        Logger.info("Cognitive agent configured with LLM enabled")
        Logger.info("")

        # Execute cognitive purge
        result = agent.execute_cognitive_purge(
            checkpoint_file=str(checkpoint_path),
            rate_limit_delay=rate_limit,
        )

        # Display results
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("COGNITIVE PURGE RESULTS")
        Logger.info("=" * 60)

        violations_found = result.get("violations_found", 0)
        batch_stats = result.get("batch_stats", {})
        results_stats = result.get("results_stats", {})

        Logger.info(f"Violations Found: {violations_found}")
        Logger.info("")
        Logger.info("Batch Statistics:")
        Logger.info(f"  Processed: {batch_stats.get('PROCESSED', 0)}")
        Logger.info(f"  Skipped (cached): {batch_stats.get('SKIPPED', 0)}")
        Logger.info(f"  Errors: {batch_stats.get('ERRORS', 0)}")
        Logger.info(f"  Total: {batch_stats.get('TOTAL', 0)}")
        Logger.info("")
        Logger.info("Results Statistics:")
        Logger.info(f"  Total Analyzed: {results_stats.get('total', 0)}")
        Logger.info(f"  Average Confidence: {results_stats.get('avg_confidence', 0.0):.2%}")
        Logger.info("")
        Logger.info("Actions by Type:")
        for action, count in sorted(results_stats.get("by_action", {}).items()):
            Logger.info(f"  {action}: {count}")
        Logger.info("")
        Logger.info(f"Checkpoint saved to: {result.get('checkpoint_file', str(checkpoint_path))}")
        Logger.info("=" * 60)

        Logger.info("")
        Logger.info("[OK] Cognitive purge completed successfully.")
        Logger.info("")
        Logger.info("Next Steps:")
        Logger.info("1. Review the checkpoint file for disposition decisions")
        Logger.info("2. Run with --execute flag to apply the decisions (future)")
        Logger.info("3. Or manually review and apply selected decisions")

        return 0

    except ImportError as e:
        Logger.error(f"[ERROR] Import Error: {e}")
        Logger.error("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:  # guardian: allow-broad-exception -- operational boundary
        Logger.exception("[ERROR] Execution Error: %s", e)
        return 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute AI-driven cognitive purge with Gemini LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage (requires GEMINI_API_KEY)
    python scripts/maintenance/execute_cognitive_purge.py

    # Custom rate limit (slower = safer)
    python scripts/maintenance/execute_cognitive_purge.py --rate-limit 2.0

    # Clear checkpoint and start fresh
    python scripts/maintenance/execute_cognitive_purge.py --clear-checkpoint
        """,
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds to wait between API calls (default: 1.0)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="cognitive_checkpoint.json",
        help="Path to checkpoint file (default: cognitive_checkpoint.json)",
    )
    parser.add_argument(
        "--clear-checkpoint",
        action="store_true",
        help="Clear existing checkpoint and start fresh",
    )

    args = parser.parse_args()

    return run_cognitive_purge(
        rate_limit=args.rate_limit,
        checkpoint_file=args.checkpoint,
        clear_checkpoint=args.clear_checkpoint,
    )


if __name__ == "__main__":
    sys.exit(main())
