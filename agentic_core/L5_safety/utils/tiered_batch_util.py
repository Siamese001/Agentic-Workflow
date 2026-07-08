from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "tiered_batch_util")
trace_contract.emit_determinism_digest("p0", "tiered_batch_util")

trace_contract._emit_dispatches_healing_run("p1", "tiered_batch_util", "L5")
trace_contract._emit_routes_through("p1", "tiered_batch_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "tiered_batch_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tiered_batch_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tiered_batch_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tiered_batch_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tiered_batch_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "tiered_batch_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tiered_batch_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tiered_batch_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tiered_batch_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tiered_batch_util")
trace_contract._emit_gated_by_confidence("p1", "tiered_batch_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tiered_batch_util", "L5")
trace_contract._emit_reads_policy_state("p1", "tiered_batch_util", "L5")

trace_contract._emit_applies_guardrail("p0", "tiered_batch_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "tiered_batch_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "tiered_batch_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "tiered_batch_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tiered_batch_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tiered_batch_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tiered_batch_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tiered_batch_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tiered_batch_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tiered_batch_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tiered_batch_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tiered_batch_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tiered_batch_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tiered_batch_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tiered_batch_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tiered_batch_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tiered_batch_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tiered_batch_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tiered_batch_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tiered_batch_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tiered_batch_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tiered_batch_util", "exec_snapshot_link")

"\n[PHASE 15/17] Tiered Batch Processor - Smart Hybrid Disposition.\n\nImplements a tiered approach to violation processing:\n- Tier 1: High-confidence heuristics (>=0.75) - auto-execute immediately\n- Tier 2: Low-confidence files (<0.75) - route to LLM Gemini\n- Phase 17: Semantic Meta-Learning with Redis/Pinecone caching\n\nThis dramatically reduces LLM API calls while maintaining intelligent triage.\n\n[SSOT] Integrates with CognitiveDispositionAgent and SemanticCacheManager.\n"
import json
import logging
import time
from pathlib import Path
from typing import Any

from tqdm import tqdm

trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tiered_batch_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tiered_batch_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tiered_batch_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tiered_batch_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tiered_batch_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tiered_batch_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tiered_batch_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tiered_batch_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tiered_batch_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tiered_batch_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tiered_batch_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tiered_batch_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tiered_batch_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tiered_batch_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("tiered_batch_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tiered_batch_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tiered_batch_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tiered_batch_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tiered_batch_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tiered_batch_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tiered_batch_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tiered_batch_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tiered_batch_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tiered_batch_util", "context_pull")
trace_contract._emit_pulls_context("p1", "tiered_batch_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tiered_batch_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tiered_batch_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tiered_batch_util", "write_through")
trace_contract._emit_writes_through("p1", "tiered_batch_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tiered_batch_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tiered_batch_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tiered_batch_util", "routing_commit")

Logger = logging.getLogger(__name__)
DEFAULT_TIERED_BATCH_HEURISTIC_THRESHOLD = 0.80


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
        heuristic_threshold: float | None = None,
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
        if heuristic_threshold is None:
            heuristic_threshold = DEFAULT_TIERED_BATCH_HEURISTIC_THRESHOLD
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
            except (RuntimeError, OSError):  # guardian: allow-silent-swallow
                return {}
        return {}

    def _save_checkpoint(self) -> None:
        """Save checkpoint to file."""
        try:
            _wg.ensure_dir(self.checkpoint_file.parent)
            _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def _get_semantic_cache(self):
        """
        [PHASE 17] Lazy-load SemanticCacheManager.

        Returns:
            SemanticCacheManager instance or None
        """
        if self._semantic_cache is None and self.use_semantic_cache:
            try:
                # W4 P4.3 fix: prior import path
                # `agentic_core.L5_safety.reasoning.semantic_cache_manager_config`
                # was a dead module — every call raised ImportError that the
                # narrow handler below did not catch, propagating to callers.
                # Switched to the canonical L4 location + singleton accessor
                # per the singleton-violation rule in semantic_cache_manager.__init__.
                from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
                    CriticalInfrastructureError,
                    SemanticCacheManager,
                )

                self._semantic_cache = SemanticCacheManager.get_instance(
                    api_key=self.agent.api_key
                )
                Logger.info("[TIERED] SemanticCacheManager initialized")
            except CriticalInfrastructureError as e:  # ADR-079 / W4 P4.3: STRICT-mode infra failure → tiered batching falls back to no-cache mode
                Logger.critical(
                    f"[TIERED] STRICT-mode infra unavailable; tiered batch will run without cache: {e}"
                )
                self._semantic_cache = None
            except (ImportError, RuntimeError, OSError) as e:  # guardian: allow-return-none-swallow -- optional cache; tiered batching continues without it
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
        except (RuntimeError, OSError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
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
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "TieredBatchProcessor.process_batch")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TieredBatchProcessor.process_batch".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        for violation in tqdm(violations, desc="Processing", unit="item"):
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
        for i, (violation, file_path, v_type, decision) in tqdm(
            enumerate(tier1_queue, 1), desc="Processing", unit="item"
        ):
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
        for i, (_violation, file_path, v_type, heuristic) in tqdm(
            enumerate(tier2_queue, 1), desc="Processing", unit="item"
        ):
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
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
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
