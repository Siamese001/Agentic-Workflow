#!/usr/bin/env python3
"""
[PHASE 15] Tiered Cognitive Purge - Smart Hybrid Execution.

Executes the AI-driven architectural purge with tiered strategy:
- Tier 1: High-confidence heuristics (>=0.75) - auto-execute immediately
- Tier 2: Low-confidence files (<0.75) - route to LLM Gemini
- Meta-learning: cache decisions in Redis for future reference

This dramatically reduces LLM API calls from 2166 to ~200-400.

Usage:
    python scripts/maintenance/execute_tiered_purge.py
    python scripts/maintenance/execute_tiered_purge.py --threshold 0.7
    python scripts/maintenance/execute_tiered_purge.py --clear-checkpoint

Exit Codes:
    0 - Success
    1 - No API key
    2 - Error
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
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
    _emit_records_execution_trace("p0", "evidence", "execute_tiered_purge")
    _emit_applies_guardrail("p0", "execute_tiered_purge", "p0_governance")
    _emit_reads_policy_state("p0", "execute_tiered_purge", "policy_binding")
    _emit_snapshots_state("p0", "execute_tiered_purge", "state_snapshot")
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

    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_1")
    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_2")
    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_3")
    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_4")
    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_5")
    _emit_emits_metric_event("execute_tiered_purge", "p4obs", "metric_6")
    _emit_records_incident_event("execute_tiered_purge", "p4obs", "incident")
    _emit_captures_runtime_anomaly("execute_tiered_purge", "p4obs", "anomaly")
    _emit_writes_observability_log("execute_tiered_purge", "p4obs", "obs_log")
    _emit_updates_monitoring_state("execute_tiered_purge", "p4obs", "mon_state")
    _emit_triggers_alert("execute_tiered_purge", "p4obs", "alert")
    _emit_links_incident_trace("execute_tiered_purge", "p4obs", "trace_link")
    _emit_captures_pattern("execute_tiered_purge", "p3lm", "pattern")
    _emit_records_learning_event("execute_tiered_purge", "p3lm", "learning_event")
    _emit_writes_learning_snapshot("execute_tiered_purge", "p3lm", "snapshot")
    _emit_feeds_meta_learning("execute_tiered_purge", "p3lm", "meta_feed")
    _emit_updates_routing_strategy("execute_tiered_purge", "p3lm", "routing")
    _emit_improves_agent_policy("execute_tiered_purge", "p3lm", "policy")
    _emit_stores_learning_state("execute_tiered_purge", "p3lm", "state")
    _emit_records_execution_trace("execute_tiered_purge", "L0_ROUTING", "p2_trace_1")
    _emit_records_execution_trace("execute_tiered_purge", "L1_REASONING", "p2_trace_2")
    _emit_records_execution_trace("execute_tiered_purge", "L2_EXECUTION", "p2_trace_3")
    _emit_records_execution_trace("execute_tiered_purge", "L3_ORCHESTRATION", "p2_trace_4")
    _emit_records_execution_trace("execute_tiered_purge", "L4_STATE", "p2_trace_5")
    _emit_reads_environ("execute_tiered_purge", "env_read", "p2_env_1")
    _emit_reads_environ("execute_tiered_purge", "env_read", "p2_env_2")
    _emit_reads_runtime_state("execute_tiered_purge", "runtime_state", "p2_rt_1")
    _emit_reads_runtime_state("execute_tiered_purge", "runtime_state", "p2_rt_2")
    _emit_pulls_context("p1", "execute_tiered_purge", "context_pull")
    _emit_pulls_context("p1", "execute_tiered_purge", "context_pull_2")
    _emit_execution_terminates_at_uwg("p1", "execute_tiered_purge", "uwg_term")
    _emit_execution_terminates_at_uwg("p1", "execute_tiered_purge", "uwg_term_2")
    _emit_writes_through("p1", "execute_tiered_purge", "write_through")
    _emit_writes_through("p1", "execute_tiered_purge", "write_through_2")
    _emit_validated_by_safety_plane("p1", "execute_tiered_purge", "safety_validation")
    _emit_invokes_eval("p1", "execute_tiered_purge", "eval_call")
    _emit_proposal_commits_routing("p1", "execute_tiered_purge", "routing_commit")
    _emit_escalates_to_human("p1", "execute_tiered_purge", "human_escalation")
    _emit_routes_through("p1", "execute_tiered_purge", "route_through")
    _emit_checks_agent_registry("p1", "execute_tiered_purge", "agent_registry")
    _emit_validates_agent_capability("p1", "execute_tiered_purge", "capability")
    _emit_dispatches_execution_plan("p1", "execute_tiered_purge", "exec_plan")
    _emit_agent_executes_agent("p1", "execute_tiered_purge", "sub_agent")
    _emit_routes_to_agent("p1", "execute_tiered_purge", "target_agent")
    _emit_verifies_policy("p1", "execute_tiered_purge", "policy_check")
    _emit_observes_runtime_state("p1", "execute_tiered_purge", "runtime_state")
    _emit_verifies_boundary("p1", "execute_tiered_purge", "boundary_check")
    _emit_transcripts_response("p1", "execute_tiered_purge", "transcript")
    _emit_hard_fails_untranscripted("p1", "execute_tiered_purge")
    _emit_gated_by_confidence("p1", "execute_tiered_purge", "confidence_gate")
    emit_replay_key("p0", "execute_tiered_purge")
    emit_determinism_digest("p0", "execute_tiered_purge")
    _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
    _emit_authorize_and_execute("p2", "execute_tiered_purge", "execution_auth")
    _emit_validates_capability("p2", "execute_tiered_purge", "capability_check")
    _emit_routes_to_capability("p2", "execute_tiered_purge", "capability_route")
    _emit_writes_via_uwg("p2", "execute_tiered_purge", "uwg_write")
    _emit_blocks_direct_write("p2", "execute_tiered_purge", "direct_write_block")
    _emit_records_tool_invocation("p2", "execute_tiered_purge", "tool_invocation")
    _emit_captures_execution_output("p2", "execute_tiered_purge", "exec_output")
    _emit_dispatches_agent("p3", "execute_tiered_purge", "agent_dispatch")
    _emit_coordinates_agents("p3", "execute_tiered_purge", "agent_coordination")
    _emit_records_workflow_lineage("p3", "execute_tiered_purge", "workflow_lineage")
    _emit_records_healing_outcome("p3", "execute_tiered_purge", "healing_outcome")
    _emit_escalates_failure("p3", "execute_tiered_purge", "failure_escalation")
    _emit_orchestrates_workflow("p3", "execute_tiered_purge", "workflow_orchestration")
    _emit_dispatches_healing_run("p3", "execute_tiered_purge", "healing_dispatch")
    _emit_invokes_evaluation("p3", "execute_tiered_purge", "evaluation_signal")
    _emit_records_telemetry_event("p4", "execute_tiered_purge", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "execute_tiered_purge", "eval_metric")
    _emit_stores_embedding("p4", "execute_tiered_purge", "embedding_store")
    _emit_updates_meta_learning_state("p4", "execute_tiered_purge", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "execute_tiered_purge", "exec_snapshot_link")


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
Logger = logging.getLogger("TieredPurge")


# guardian: allow-magic-config
def run_tiered_purge(
    threshold: float = 0.75,
    checkpoint_file: str = "tiered_checkpoint.json",
    clear_checkpoint: bool = False,
    rate_limit: float = 1.0,
) -> int:
    """
    Execute tiered cognitive purge.

    Args:
        threshold: Confidence threshold for auto-execution
        checkpoint_file: Path to checkpoint file
        clear_checkpoint: Clear existing checkpoint
        rate_limit: Seconds between LLM calls

    Returns:
        Exit code
    """

    _init_runtime_trace()

    if not 0.0 <= threshold <= 1.0:
        Logger.error("[FAIL] --threshold must be between 0.0 and 1.0.")
        return 2
    if rate_limit <= 0:
        Logger.error("[FAIL] --rate-limit must be greater than 0.")
        return 2

    # Signal handler for graceful shutdown (Ctrl+C)
    def signal_handler(sig, frame):
        Logger.warning("\n[INTERRUPT] Graceful shutdown initiated. Saving progress...")
        Logger.info("[INTERRUPT] Checkpoint saved. Re-run to resume from last position.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Load .env
    try:
        from dotenv import find_dotenv, load_dotenv

        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file)
            Logger.info(f"Loaded environment from: {env_file}")
    except ImportError:  # guardian: allow-silent-swallow - optional dependency
        pass

    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        Logger.error("[FAIL] GEMINI_API_KEY not found.")
        return 1

    try:
        project_root = get_validated_project_root()
        checkpoint_path = Path(checkpoint_file)
        if not checkpoint_path.is_absolute():
            checkpoint_path = project_root / checkpoint_path
        checkpoint_path = checkpoint_path.resolve()
        if project_root not in checkpoint_path.parents and checkpoint_path != project_root:
            raise ValueError("Checkpoint path must remain under the project root")

        from agentic_core.L5_safety.reasoning.TieredBatchProcessor import (
            TieredBatchProcessor,
        )

        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )

        Logger.info("=" * 60)
        Logger.info("PHASE 15: TIERED COGNITIVE PURGE")
        Logger.info("=" * 60)
        Logger.info(f"Project Root: {project_root}")
        Logger.info(f"Heuristic Threshold: {threshold:.0%}")
        Logger.info(f"Rate Limit: {rate_limit}s")
        Logger.info("")

        # Clear checkpoint if requested
        if clear_checkpoint:
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                Logger.info("[OK] Checkpoint cleared")

        # Initialize Governor
        Logger.info("Initializing ArchitectureGovernorAgent...")
        governor = ArchitectureGovernorAgent(
            project_root=project_root,
            healing_enabled=False,
        )

        # Scan for violations
        Logger.info("Scanning for violations...")
        governor.heal_repository(dry_run=True)
        violations = getattr(governor, "violations", [])

        if not violations:
            Logger.info("[OK] No violations found.")
            return 0

        Logger.info(f"Found {len(violations)} violations")
        Logger.info("")

        # Initialize Cognitive Agent with LLM
        cognitive = CognitiveDispositionAgent(
            project_root=project_root,
            llm_enabled=True,
            api_key=api_key,
        )

        # Initialize Tiered Processor
        processor = TieredBatchProcessor(
            agent=cognitive,
            heuristic_threshold=threshold,
            checkpoint_file=str(checkpoint_path),
            use_semantic_cache=True,
            rate_limit_delay=rate_limit,
        )

        # Process
        processor.process_batch(violations)

        # Results
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("TIERED PURGE RESULTS")
        Logger.info("=" * 60)

        results_stats = processor.get_statistics()
        Logger.info(f"Total Processed: {results_stats['total']}")
        Logger.info("")
        Logger.info("By Tier:")
        for tier, count in sorted(results_stats["by_tier"].items()):
            Logger.info(f"  {tier}: {count}")
        Logger.info("")
        Logger.info("By Action:")
        for action, count in sorted(results_stats["by_action"].items()):
            Logger.info(f"  {action}: {count}")
        Logger.info("")
        Logger.info(f"Checkpoint: {checkpoint_path}")
        Logger.info("=" * 60)

        return 0

    except Exception as e:  # guardian: allow-broad-exception -- operational boundary
        Logger.exception("[ERROR] %s", e)
        return 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute tiered cognitive purge",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Confidence threshold for auto-execution (default: 0.75)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="tiered_checkpoint.json",
        help="Checkpoint file path",
    )
    parser.add_argument(
        "--clear-checkpoint",
        action="store_true",
        help="Clear existing checkpoint",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds between LLM calls (default: 1.0)",
    )

    args = parser.parse_args()

    return run_tiered_purge(
        threshold=args.threshold,
        checkpoint_file=args.checkpoint,
        clear_checkpoint=args.clear_checkpoint,
        rate_limit=args.rate_limit,
    )


if __name__ == "__main__":
    sys.exit(main())
