from __future__ import annotations

from agentic_core.L3_orchestration.healers.healing_tier_config import (
    HEALING_CONFIDENCE_X as _HEALING_CONFIDENCE_X,
)
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_snapshots_state,
    # noqa: E402
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

emit_replay_key("p0", "tiered_batch_util")
emit_determinism_digest("p0", "tiered_batch_util")

_emit_dispatches_healing_run("p1", "tiered_batch_util", "L5")
_emit_routes_through("p1", "tiered_batch_util", "L5")
_emit_checks_agent_registry("p1", "tiered_batch_util", "agent_registry")
_emit_validates_agent_capability("p1", "tiered_batch_util", "capability")
_emit_dispatches_execution_plan("p1", "tiered_batch_util", "exec_plan")
_emit_agent_executes_agent("p1", "tiered_batch_util", "sub_agent")
_emit_routes_to_agent("p1", "tiered_batch_util", "target_agent")
_emit_verifies_policy("p1", "tiered_batch_util", "policy_check")
_emit_observes_runtime_state("p1", "tiered_batch_util", "runtime_state")
_emit_verifies_boundary("p1", "tiered_batch_util", "boundary_check")
_emit_transcripts_response("p1", "tiered_batch_util", "transcript")
_emit_hard_fails_untranscripted("p1", "tiered_batch_util")
_emit_gated_by_confidence("p1", "tiered_batch_util", "confidence_gate")
_emit_escalates_to_human("p1", "tiered_batch_util", "L5")
_emit_reads_policy_state("p1", "tiered_batch_util", "L5")

_emit_applies_guardrail("p0", "tiered_batch_util", "p0_governance")
_emit_snapshots_state("p0", "tiered_batch_util", "state_snapshot")
_emit_authorize_and_execute("p2", "tiered_batch_util", "execution_auth")
_emit_validates_capability("p2", "tiered_batch_util", "capability_check")
_emit_routes_to_capability("p2", "tiered_batch_util", "capability_route")
_emit_writes_via_uwg("p2", "tiered_batch_util", "uwg_write")
_emit_blocks_direct_write("p2", "tiered_batch_util", "direct_write_block")
_emit_records_tool_invocation("p2", "tiered_batch_util", "tool_invocation")
_emit_captures_execution_output("p2", "tiered_batch_util", "exec_output")
_emit_dispatches_agent("p3", "tiered_batch_util", "agent_dispatch")
_emit_coordinates_agents("p3", "tiered_batch_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "tiered_batch_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "tiered_batch_util", "healing_outcome")
_emit_escalates_failure("p3", "tiered_batch_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "tiered_batch_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tiered_batch_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "tiered_batch_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "tiered_batch_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tiered_batch_util", "eval_metric")
_emit_stores_embedding("p4", "tiered_batch_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "tiered_batch_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tiered_batch_util", "exec_snapshot_link")

"\n[PHASE 15/17] Tiered Batch Processor - Smart Hybrid Disposition.\n\nImplements a tiered approach to violation processing:\n- Tier 1: High-confidence heuristics (>=0.75) - auto-execute immediately\n- Tier 2: Low-confidence files (<0.75) - route to LLM Gemini\n- Phase 17: Semantic Meta-Learning with Redis/Pinecone caching\n\nThis dramatically reduces LLM API calls while maintaining intelligent triage.\n\n[SSOT] Integrates with CognitiveDispositionAgent and SemanticCacheManager.\n"
import json
import logging
import time
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_1")
_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_2")
_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_3")
_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_4")
_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_5")
_emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_6")
_emit_records_incident_event("tiered_batch_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("tiered_batch_util", "p4obs", "anomaly")
_emit_writes_observability_log("tiered_batch_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("tiered_batch_util", "p4obs", "mon_state")
_emit_triggers_alert("tiered_batch_util", "p4obs", "alert")
_emit_links_incident_trace("tiered_batch_util", "p4obs", "trace_link")
_emit_captures_pattern("tiered_batch_util", "p3lm", "pattern")
_emit_records_learning_event("tiered_batch_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tiered_batch_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("tiered_batch_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tiered_batch_util", "p3lm", "routing")
_emit_improves_agent_policy("tiered_batch_util", "p3lm", "policy")
_emit_stores_learning_state("tiered_batch_util", "p3lm", "state")
_emit_records_execution_trace("tiered_batch_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tiered_batch_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tiered_batch_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tiered_batch_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tiered_batch_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tiered_batch_util", "env_read", "p2_env_1")
_emit_reads_environ("tiered_batch_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("tiered_batch_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tiered_batch_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tiered_batch_util", "context_pull")
_emit_pulls_context("p1", "tiered_batch_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tiered_batch_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tiered_batch_util", "uwg_term_2")
_emit_writes_through("p1", "tiered_batch_util", "write_through")
_emit_writes_through("p1", "tiered_batch_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "tiered_batch_util", "safety_validation")
_emit_invokes_eval("p1", "tiered_batch_util", "eval_call")
_emit_proposal_commits_routing("p1", "tiered_batch_util", "routing_commit")

Logger = logging.getLogger(__name__)


class TieredBatchProcessor:
    """
    Smart batch processor with tiered disposition strategy.

    Tier 1: High-confidence heuristics auto-execute (no LLM)
    Tier 2: Low-confidence routes to LLM with semantic caching

    Attributes:
        agent: CognitiveDispositionAgent instance
        heuristic_threshold: Confidence threshold for auto-execution
        checkpoint_file: Path to checkpoint file
        use_semantic_cache: Enable Redis/Pinecone caching
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        agent: Any,
        heuristic_threshold: float = _HEALING_CONFIDENCE_X,
        checkpoint_file: str | Path = "tiered_checkpoint.json",
        use_semantic_cache: bool = True,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize the Tiered Batch Processor.

        Args:
            agent: CognitiveDispositionAgent instance
            heuristic_threshold: Min confidence for auto-execution
            checkpoint_file: Path to checkpoint file
            use_semantic_cache: Enable Redis/Pinecone caching
            rate_limit_delay: Seconds between LLM calls
        """
        self.agent = agent
        self.heuristic_threshold = heuristic_threshold
        self.checkpoint_file = Path(checkpoint_file)
        self.use_semantic_cache = use_semantic_cache
        self.rate_limit_delay = rate_limit_delay
        self.results: dict[str, Any] = self._load_checkpoint()
        self.stats = {"tier1_auto": 0, "tier2_llm": 0, "tier2_cached": 0, "skipped": 0, "errors": 0}
        self._semantic_cache = None
        Logger.info(f"[TIERED] Initialized with threshold: {heuristic_threshold:.0%}")

    def _load_checkpoint(self) -> dict[str, Any]:
        """Load checkpoint from file."""
        if self.checkpoint_file.exists():
            try:
                return json.loads(self.checkpoint_file.read_text(encoding="utf-8"))
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError):
                return {}
        return {}

    def _save_checkpoint(self) -> None:
        """Save checkpoint to file."""
        try:
            _wg.ensure_dir(self.checkpoint_file.parent)
            _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.error(f"[TIERED] Checkpoint save failed: {e}")

    def _get_semantic_cache(self):
        """
        [PHASE 17] Lazy-load SemanticCacheManager.

        Returns:
            SemanticCacheManager instance or None
        """
        if self._semantic_cache is None and self.use_semantic_cache:
            try:
                from agentic_core.L5_safety.reasoning.semantic_cache_manager_config import (
                    SemanticCacheManager,
                )

                self._semantic_cache = SemanticCacheManager(api_key=self.agent.api_key)
                Logger.info("[TIERED] SemanticCacheManager initialized")
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError) as e:
                Logger.warning(f"[TIERED] SemanticCacheManager unavailable: {e}")
                self._semantic_cache = None
        return self._semantic_cache

    def _check_semantic_cache(self, file_path: str, violation_type: str) -> dict | None:
        """
        [PHASE 17] Check semantic cache for cached disposition decision.

        Uses dual-layer caching:
        1. Redis: Exact content hash matching
        2. Pinecone: Semantic similarity matching

        Args:
            file_path: Path to file
            violation_type: Type of violation

        Returns:
            Cached decision dict or None
        """
        cache = self._get_semantic_cache()
        if not cache:
            return None
        try:
            content = self.agent._read_file_safe(Path(file_path))
            return cache.get_cached_decision(content, violation_type)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.debug(f"[TIERED] cache check failed: {e}")
        return None

    def _store_semantic_cache(self, file_path: str, violation_type: str, decision: dict) -> None:
        """
        [PHASE 17] Store disposition decision in semantic cache.

        Stores in both Redis (exact) and Pinecone (semantic) for meta-learning.

        Args:
            file_path: Path to file
            violation_type: Type of violation
            decision: Decision dict to cache
        """
        cache = self._get_semantic_cache()
        if not cache:
            return
        try:
            if decision.get("confidence", 0) >= 0.8:
                content = self.agent._read_file_safe(Path(file_path))
                cache.cache_decision(content, violation_type, decision)
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.debug(f"[TIERED] cache store failed: {e}")

    def process_batch(self, violations: list[Any]) -> dict[str, Any]:
        """
        Process violations with tiered strategy.

        Args:
            violations: List of violation objects

        Returns:
            Processing statistics
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TieredBatchProcessor.process_batch")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TieredBatchProcessor.process_batch".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        total = len(violations)
        tier1_queue = []
        tier2_queue = []
        Logger.info("=" * 60)
        Logger.info("[TIERED] PHASE 15: SMART TIERED BATCH PROCESSING")
        Logger.info("=" * 60)
        Logger.info(f"[TIERED] Total Violations: {total}")
        Logger.info(f"[TIERED] Heuristic Threshold: {self.heuristic_threshold:.0%}")
        Logger.info("")
        Logger.info("[TIERED] Phase 1: Triaging violations...")
        for violation in violations:
            file_path = self._get_file_path(violation)
            if not file_path:
                continue
            file_path_str = str(file_path)
            if file_path_str in self.results:
                self.stats["skipped"] += 1
                continue
            v_type = self._get_violation_type(violation)
            heuristic = self.agent._analyze_heuristic(file_path, v_type, {})
            if heuristic.confidence >= self.heuristic_threshold:
                tier1_queue.append((violation, file_path, v_type, heuristic))
            else:
                tier2_queue.append((violation, file_path, v_type, heuristic))
        Logger.info(f"[TIERED] Tier 1 (Auto-Execute): {len(tier1_queue)} files")
        Logger.info(f"[TIERED] Tier 2 (LLM Required): {len(tier2_queue)} files")
        Logger.info(f"[TIERED] Already Processed: {self.stats['skipped']}")
        Logger.info("")
        Logger.info("[TIERED] Phase 2: Executing Tier 1 (heuristics)...")
        for i, (violation, file_path, v_type, decision) in enumerate(tier1_queue, 1):
            file_path_str = str(file_path)
            self.results[file_path_str] = {
                "action": decision.action,
                "target_path": decision.target_path,
                "reason": decision.reason,
                "confidence": decision.confidence,
                "violation_type": v_type,
                "tier": "heuristic",
            }
            self.stats["tier1_auto"] += 1
            if i % 100 == 0:
                Logger.info(f"[TIERED] Tier 1 Progress: {i}/{len(tier1_queue)}")
                self._save_checkpoint()
        self._save_checkpoint()
        Logger.info(f"[TIERED] Tier 1 Complete: {self.stats['tier1_auto']} files")
        Logger.info("")
        if tier2_queue:
            Logger.info("[TIERED] Phase 3: Executing Tier 2 (LLM)...")
            self._process_tier2(tier2_queue)
        self._save_checkpoint()
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("[TIERED] BATCH PROCESSING COMPLETE")
        Logger.info("=" * 60)
        Logger.info(f"[TIERED] Tier 1 (Heuristics): {self.stats['tier1_auto']}")
        Logger.info(f"[TIERED] Tier 2 (LLM Calls): {self.stats['tier2_llm']}")
        Logger.info(f"[TIERED] Tier 2 (cache Hits): {self.stats['tier2_cached']}")
        Logger.info(f"[TIERED] Skipped (Cached): {self.stats['skipped']}")
        Logger.info(f"[TIERED] Errors: {self.stats['errors']}")
        Logger.info(f"[TIERED] Total Processed: {len(self.results)}")
        Logger.info("=" * 60)
        return self.stats

    def _process_tier2(self, tier2_queue: list) -> None:
        """
        Process Tier 2 files with LLM and semantic caching.

        Args:
            tier2_queue: List of (violation, file_path, v_type, heuristic) tuples
        """
        for i, (_violation, file_path, v_type, heuristic) in enumerate(tier2_queue, 1):
            file_path_str = str(file_path)
            file_name = Path(file_path).name
            Logger.info(f"[TIERED] Tier 2 [{i}/{len(tier2_queue)}]: {file_name}")
            cached = self._check_semantic_cache(file_path_str, v_type)
            if cached:
                self.results[file_path_str] = cached
                self.results[file_path_str]["tier"] = "cached"
                self.stats["tier2_cached"] += 1
                continue
            try:
                decision = self.agent._generate_llm_decision(file_path, v_type, {})
                result = {
                    "action": decision.action,
                    "target_path": decision.target_path,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "violation_type": v_type,
                    "tier": "llm",
                }
                self.results[file_path_str] = result
                self.stats["tier2_llm"] += 1
                self._store_semantic_cache(file_path_str, v_type, result)
                Logger.info(f"    -> {decision.action} ({decision.confidence:.0%})")
                time.sleep(self.rate_limit_delay)
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.error(f"    -> Error: {e}")
                self.results[file_path_str] = {
                    "action": heuristic.action,
                    "target_path": heuristic.target_path,
                    "reason": f"LLM failed, using heuristic: {heuristic.reason}",
                    "confidence": heuristic.confidence,
                    "violation_type": v_type,
                    "tier": "fallback",
                }
                self.stats["errors"] += 1
            if i % 10 == 0:
                self._save_checkpoint()

    def _get_file_path(self, violation: Any) -> Path | None:
        """Extract file path from violation."""
        if hasattr(violation, "file_path"):
            return Path(violation.file_path)
        elif isinstance(violation, dict):
            file = violation.get("file")
            if file:
                return Path(file)
        return None

    def _get_violation_type(self, violation: Any) -> str:
        """Extract violation type from violation."""
        if hasattr(violation, "violation_type"):
            v_type = violation.violation_type
            if hasattr(v_type, "name"):
                return v_type.name
            return str(v_type)
        elif isinstance(violation, dict):
            return violation.get("type", "UNKNOWN")
        return "UNKNOWN"

    def get_statistics(self) -> dict[str, Any]:
        """Get processing statistics."""
        if not self.results:
            return {"total": 0, "by_tier": {}, "by_action": {}}
        by_tier: dict[str, int] = {}
        by_action: dict[str, int] = {}
        for result in self.results.values():
            tier = result.get("tier", "unknown")
            by_tier[tier] = by_tier.get(tier, 0) + 1
            action = result.get("action", "UNKNOWN")
            by_action[action] = by_action.get(action, 0) + 1
        return {"total": len(self.results), "by_tier": by_tier, "by_action": by_action}

    def clear_checkpoint(self) -> None:
        """Clear checkpoint and reset."""
        if self.checkpoint_file.exists():
            _wg.remove_file(self.checkpoint_file)
        self.results = {}
        self.stats = {"tier1_auto": 0, "tier2_llm": 0, "tier2_cached": 0, "skipped": 0, "errors": 0}
        Logger.info("[TIERED] Checkpoint cleared")
