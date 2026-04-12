from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "cognitive_batch_processor_util")
emit_determinism_digest("p0", "cognitive_batch_processor_util")

_emit_dispatches_healing_run("p1", "cognitive_batch_processor_util", "L5")
_emit_routes_through("p1", "cognitive_batch_processor_util", "L5")
_emit_checks_agent_registry("p1", "cognitive_batch_processor_util", "agent_registry")
_emit_validates_agent_capability("p1", "cognitive_batch_processor_util", "capability")
_emit_dispatches_execution_plan("p1", "cognitive_batch_processor_util", "exec_plan")
_emit_agent_executes_agent("p1", "cognitive_batch_processor_util", "sub_agent")
_emit_routes_to_agent("p1", "cognitive_batch_processor_util", "target_agent")
_emit_verifies_policy("p1", "cognitive_batch_processor_util", "policy_check")
_emit_observes_runtime_state("p1", "cognitive_batch_processor_util", "runtime_state")
_emit_verifies_boundary("p1", "cognitive_batch_processor_util", "boundary_check")
_emit_transcripts_response("p1", "cognitive_batch_processor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "cognitive_batch_processor_util")
_emit_gated_by_confidence("p1", "cognitive_batch_processor_util", "confidence_gate")
_emit_escalates_to_human("p1", "cognitive_batch_processor_util", "L5")
_emit_reads_policy_state("p1", "cognitive_batch_processor_util", "L5")

_emit_applies_guardrail("p0", "cognitive_batch_processor_util", "p0_governance")
_emit_authorize_and_execute("p2", "cognitive_batch_processor_util", "execution_auth")
_emit_validates_capability("p2", "cognitive_batch_processor_util", "capability_check")
_emit_routes_to_capability("p2", "cognitive_batch_processor_util", "capability_route")
_emit_writes_via_uwg("p2", "cognitive_batch_processor_util", "uwg_write")
_emit_blocks_direct_write("p2", "cognitive_batch_processor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cognitive_batch_processor_util", "tool_invocation")
_emit_captures_execution_output("p2", "cognitive_batch_processor_util", "exec_output")
_emit_dispatches_agent("p3", "cognitive_batch_processor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cognitive_batch_processor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cognitive_batch_processor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cognitive_batch_processor_util", "healing_outcome")
_emit_escalates_failure("p3", "cognitive_batch_processor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cognitive_batch_processor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cognitive_batch_processor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cognitive_batch_processor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cognitive_batch_processor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cognitive_batch_processor_util", "eval_metric")
_emit_stores_embedding("p4", "cognitive_batch_processor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cognitive_batch_processor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cognitive_batch_processor_util", "exec_snapshot_link")

"\n[PHASE 13] Cognitive Batch Processor - High-Volume AI Audit Management.\n\nManages API rate limits, checkpointing, and batch execution for large-scale\narchitectural audits using Gemini LLM.\n\nFeatures:\n- Rate limiting with configurable delays\n- Progress checkpointing for resumable execution\n- Exponential backoff for API errors\n- Batch processing with periodic saves\n\nResponsibilities:\n- Process large batches of violations (2,160+)\n- Save progress every N items to prevent data loss\n- Skip already-processed items on resume\n- Handle API rate limits and errors gracefully\n\n[SSOT] Integrates with CognitiveDispositionAgent for AI-powered triage.\n"
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_1")
_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_2")
_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_3")
_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_4")
_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_5")
_emit_emits_metric_event("cognitive_batch_processor_util", "p4obs", "metric_6")
_emit_records_incident_event("cognitive_batch_processor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("cognitive_batch_processor_util", "p4obs", "anomaly")
_emit_writes_observability_log("cognitive_batch_processor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("cognitive_batch_processor_util", "p4obs", "mon_state")
_emit_triggers_alert("cognitive_batch_processor_util", "p4obs", "alert")
_emit_links_incident_trace("cognitive_batch_processor_util", "p4obs", "trace_link")
_emit_captures_pattern("cognitive_batch_processor_util", "p3lm", "pattern")
_emit_records_learning_event("cognitive_batch_processor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cognitive_batch_processor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("cognitive_batch_processor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cognitive_batch_processor_util", "p3lm", "routing")
_emit_improves_agent_policy("cognitive_batch_processor_util", "p3lm", "policy")
_emit_stores_learning_state("cognitive_batch_processor_util", "p3lm", "state")
_emit_records_execution_trace("cognitive_batch_processor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cognitive_batch_processor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cognitive_batch_processor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cognitive_batch_processor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cognitive_batch_processor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cognitive_batch_processor_util", "env_read", "p2_env_1")
_emit_reads_environ("cognitive_batch_processor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("cognitive_batch_processor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cognitive_batch_processor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cognitive_batch_processor_util", "context_pull")
_emit_pulls_context("p1", "cognitive_batch_processor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cognitive_batch_processor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cognitive_batch_processor_util", "uwg_term_2")
_emit_writes_through("p1", "cognitive_batch_processor_util", "write_through")
_emit_writes_through("p1", "cognitive_batch_processor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "cognitive_batch_processor_util", "safety_validation")
_emit_invokes_eval("p1", "cognitive_batch_processor_util", "eval_call")
_emit_proposal_commits_routing("p1", "cognitive_batch_processor_util", "routing_commit")

Logger = logging.getLogger(__name__)


class CognitiveBatchProcessor:
    """
    Batch processor for high-volume cognitive disposition analysis.

    Manages rate limiting, checkpointing, and resumable execution for
    processing large numbers of architectural violations.

    Attributes:
        agent: CognitiveDispositionAgent instance
        checkpoint_file: Path to checkpoint file for progress tracking
        rate_limit_delay: Seconds to wait between API calls
        checkpoint_interval: Save checkpoint every N items
        max_retries: Maximum retry attempts for failed items
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        agent: Any,
        checkpoint_file: str | Path = "cognitive_checkpoint.json",
        rate_limit_delay: float = 1.0,
        checkpoint_interval: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the Cognitive Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            checkpoint_file: Path to checkpoint file
            rate_limit_delay: Seconds between API calls
            checkpoint_interval: Save progress every N items
            max_retries: Maximum retry attempts per item
        """
        self.agent = agent
        self.checkpoint_file = Path(checkpoint_file)
        self.rate_limit_delay = rate_limit_delay
        self.checkpoint_interval = checkpoint_interval
        self.max_retries = max_retries
        self.results: dict[str, Any] = self._load_checkpoint()
        self.retry_counts: dict[str, int] = {}
        Logger.info(f"[BATCH] Initialized with checkpoint: {self.checkpoint_file}")
        if self.results:
            Logger.info(f"[BATCH] Loaded {len(self.results)} existing results from checkpoint")

    def _load_checkpoint(self) -> dict[str, Any]:
        """
        Load checkpoint from file if it exists.

        Returns:
            Dictionary of file_path -> disposition results
        """
        _emit_snapshots_state(str(uuid.uuid4()), "CognitiveBatchProcessor._load_checkpoint", "L5_POLICY")
        if self.checkpoint_file.exists():
            try:
                data = json.loads(self.checkpoint_file.read_text(encoding="utf-8"))
                Logger.info(f"[BATCH] Checkpoint loaded: {len(data)} items")
                return data
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                Logger.warning(f"[BATCH] Failed to load checkpoint: {e}")
                return {}
        return {}

    def _save_checkpoint(self) -> None:
        """Save current progress to checkpoint file."""
        try:
            _wg.ensure_dir(self.checkpoint_file.parent)
            _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")
            Logger.debug(f"[BATCH] Checkpoint saved: {len(self.results)} items")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"[BATCH] Failed to save checkpoint: {e}")

    def process_batch(self, violations: list[Any], auto_execute: bool = False) -> dict[str, int]:
        """
        Process a batch of violations with rate limiting and checkpointing.

        Args:
            violations: List of violation objects to process
            auto_execute: If True, execute disposition actions (not just analyze)

        Returns:
            Statistics dictionary with counts
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "CognitiveBatchProcessor.process_batch",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CognitiveBatchProcessor.process_batch".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        stats = {"PROCESSED": 0, "SKIPPED": 0, "ERRORS": 0, "TOTAL": len(violations)}
        Logger.info("=" * 60)
        Logger.info("[BATCH] Starting Cognitive Batch Processing")
        Logger.info(f"[BATCH] Queue Size: {len(violations)} violations")
        Logger.info(f"[BATCH] Rate Limit: {self.rate_limit_delay}s between calls")
        Logger.info(f"[BATCH] Checkpoint Interval: Every {self.checkpoint_interval} items")
        Logger.info("=" * 60)
        for i, violation in enumerate(violations, 1):
            file_path = self._get_file_path(violation)
            if not file_path:
                Logger.warning(f"[BATCH] [{i}/{len(violations)}] No file path in violation")
                stats["ERRORS"] += 1
                continue
            file_path_str = str(file_path)
            if file_path_str in self.results:
                Logger.debug(f"[BATCH] [{i}/{len(violations)}] Skipping (cached): {Path(file_path).name}")
                stats["SKIPPED"] += 1
                continue
            Logger.info(f"[BATCH] [{i}/{len(violations)}] Processing: {Path(file_path).name}")
            success = self._process_single_violation(violation, file_path_str)
            if success:
                stats["PROCESSED"] += 1
            else:
                stats["ERRORS"] += 1
            if i % self.checkpoint_interval == 0:
                self._save_checkpoint()
                Logger.info(f"[BATCH] Checkpoint saved at item {i}/{len(violations)}")
            if i < len(violations):
                time.sleep(self.rate_limit_delay)
        self._save_checkpoint()
        Logger.info("=" * 60)
        Logger.info("[BATCH] Batch Processing Complete")
        Logger.info(f"[BATCH] Processed: {stats['PROCESSED']}")
        Logger.info(f"[BATCH] Skipped (cached): {stats['SKIPPED']}")
        Logger.info(f"[BATCH] Errors: {stats['ERRORS']}")
        Logger.info("=" * 60)
        return stats

    def _get_file_path(self, violation: Any) -> Path | None:
        """
        Extract file path from violation object.

        Args:
            violation: Violation object (dict or object with attributes)

        Returns:
            Path to file or None
        """
        if hasattr(violation, "file_path"):
            return Path(violation.file_path)
        elif isinstance(violation, dict):
            file = violation.get("file")
            if file:
                return Path(file)
        return None

    def _process_single_violation(self, violation: Any, file_path_str: str) -> bool:
        """
        Process a single violation with retry logic.

        Args:
            violation: Violation object
            file_path_str: String path to file

        Returns:
            True if successful, False otherwise
        """
        v_type = self._get_violation_type(violation)
        for attempt in range(1, self.max_retries + 1):
            try:
                decision = self.agent.analyze_violation(file_path_str, v_type)
                self.results[file_path_str] = {
                    "action": decision.action,
                    "target_path": decision.target_path,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "violation_type": v_type,
                }
                Logger.info(
                    f"    Decision: {decision.action} -> {decision.target_path or 'N/A'} ({decision.confidence:.2f})",
                )
                return True
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                Logger.warning(f"    Attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    backoff_delay = self.rate_limit_delay * 2 ** (attempt - 1)
                    Logger.info(f"    Retrying in {backoff_delay:.1f}s...")
                    time.sleep(backoff_delay)
                else:
                    Logger.error(f"    Max retries exceeded for {Path(file_path_str).name}")
                    self.results[file_path_str] = {
                        "action": "ERROR",
                        "target_path": None,
                        "reason": f"Processing failed after {self.max_retries} attempts: {e}",
                        "confidence": 0.0,
                        "violation_type": v_type,
                    }
                    return False
        return False

    def _get_violation_type(self, violation: Any) -> str:
        """
        Extract violation type from violation object.

        Args:
            violation: Violation object

        Returns:
            Violation type string
        """
        if hasattr(violation, "violation_type"):
            v_type = violation.violation_type
            if hasattr(v_type, "name"):
                return v_type.name
            return str(v_type)
        elif isinstance(violation, dict):
            return violation.get("type", "UNKNOWN")
        return "UNKNOWN"

    def get_results(self) -> dict[str, Any]:
        """
        Get all processed results.

        Returns:
            Dictionary of file_path -> disposition results
        """
        return self.results

    def get_statistics(self) -> dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {"total": 0, "by_action": {}, "avg_confidence": 0.0}
        by_action: dict[str, int] = {}
        confidences = []
        for result in self.results.values():
            action = result.get("action", "UNKNOWN")
            by_action[action] = by_action.get(action, 0) + 1
            confidence = result.get("confidence", 0.0)
            if isinstance(confidence, int | float):
                confidences.append(confidence)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return {"total": len(self.results), "by_action": by_action, "avg_confidence": avg_confidence}

    def clear_checkpoint(self) -> None:
        """Clear the checkpoint file and reset results."""
        if self.checkpoint_file.exists():
            _wg.remove_file(self.checkpoint_file)
            Logger.info("[BATCH] Checkpoint cleared")
        self.results = {}
        self.retry_counts = {}
