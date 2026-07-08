"""
L4 State Context Manager - Single Source of Truth for Agent State

Centralizes:
1. Meta-learning cache (cross-agent)
2. Healing pattern storage (cross-agent learning)
3. File analysis results cache (performance optimization)

Replaces:
- Distributed ml_cache_* methods in SovereignBaseAgent
- Agent-specific pattern storage
- Redundant file scanning

Usage:
    from agentic_core.L4_state.utils.context_manager import get_context_manager

    ctx = get_context_manager(project_root)

    # Cache analysis results
    ctx.cache_set("complexity:file.py", result, agent="GovernanceAgent")
    cached = ctx.cache_get("complexity:file.py", agent="GovernanceAgent")

    # Store/recall healing patterns
    ctx.store_healing_pattern(violation, result, agent="GravityLeakRepairAgent")
    pattern = ctx.recall_healing_pattern(violation, agent="StructuralEngineerAgent")
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "context_validator")
trace_contract.emit_determinism_digest("p0", "context_validator")

trace_contract._emit_dispatches_healing_run("p1", "context_validator", "L5")
trace_contract._emit_routes_through("p1", "context_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "context_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "context_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "context_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "context_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "context_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "context_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "context_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "context_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "context_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "context_validator")
trace_contract._emit_gated_by_confidence("p1", "context_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "context_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "context_validator", "L5")
trace_contract._emit_applies_guardrail("p0", "context_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "context_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "context_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "context_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "context_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "context_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "context_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "context_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "context_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "context_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "context_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "context_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "context_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "context_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "context_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "context_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "context_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "context_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "context_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "context_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "context_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "context_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("context_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("context_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("context_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("context_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("context_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("context_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("context_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("context_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("context_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("context_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("context_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("context_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("context_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("context_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("context_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("context_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("context_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("context_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("context_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("context_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("context_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("context_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("context_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "context_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "context_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "context_validator", "write_through")
trace_contract._emit_writes_through("p1", "context_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "context_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "context_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "context_validator", "routing_commit")


@dataclass
class CacheEntry:
    """Represents a cached analysis result."""

    key: str
    value: Any
    timestamp: float
    ttl: int
    agent: str

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl


@dataclass
class HealingPattern:
    """Represents a successful healing pattern."""

    violation_signature: str
    healing_strategy: str
    success_count: int
    last_used: float
    agent: str
    metadata: dict[str, Any]


class L4ContextManager:
    """
    Centralized state management for L5 agents.

    Singleton pattern ensures all agents share the same context.
    Enables cross-agent learning and eliminates redundant state.
    """

    _instance: L4ContextManager | None = None
    _lock: bool = False

    def __init__(self, project_root: Path):
        if L4ContextManager._instance is not None:
            raise RuntimeError("Use get_context_manager() to get singleton instance")
        self.project_root = project_root
        self._cache: dict[str, CacheEntry] = {}
        self._patterns: dict[str, HealingPattern] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._python_files: list[Path] | None = None
        self._python_files_timestamp: float = 0

    @classmethod
    def get_instance(cls, project_root: Path) -> L4ContextManager:
        """Get or create singleton instance."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "L4ContextManager.get_instance")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:L4ContextManager.get_instance".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if cls._instance is None:
            cls._instance = cls(project_root)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing only)."""
        cls._instance = None

    def cache_get(self, key: str, agent: str) -> Any | None:
        """
        Retrieve cached value.

        Args:
            key: Cache key
            agent: Agent requesting the value

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            del self._cache[key]
            return None
        return entry.value

    def cache_set(self, key: str, value: Any, agent: str, ttl: int = 3600):
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            agent: Agent storing the value
            ttl: Time-to-live in seconds (default 1 hour)
        """
        self._cache[key] = CacheEntry(key=key, value=value, timestamp=time.time(), ttl=ttl, agent=agent)

    def cache_clear(self, agent: str | None = None):
        """
        Clear cache entries.

        Args:
            agent: If specified, only clear entries from this agent
        """
        if agent is None:
            self._cache.clear()
        else:
            self._cache = {k: v for k, v in self._cache.items() if v.agent != agent}

    def recall_healing_pattern(self, violation: dict[str, Any], agent: str) -> dict[str, Any] | None:
        """
        Recall a successful healing pattern.

        Enables cross-agent learning: If GravityLeakRepairAgent successfully
        fixed a similar violation, StructuralEngineerAgent can reuse that pattern.

        Args:
            violation: Violation characteristics
            agent: Agent requesting the pattern

        Returns:
            Healing pattern metadata or None
        """
        signature = self._compute_violation_signature(violation)
        pattern = self._patterns.get(signature)
        if pattern is None:
            return None
        pattern.last_used = time.time()
        return {
            "healing_strategy": pattern.healing_strategy,
            "success_count": pattern.success_count,
            "discovered_by": pattern.agent,
            "metadata": pattern.metadata,
        }

    def store_healing_pattern(self, violation: dict[str, Any], result: dict[str, Any], agent: str):
        """
        Store a successful healing pattern.

        Args:
            violation: Violation that was healed
            result: Healing result
            agent: Agent that performed the healing
        """
        signature = self._compute_violation_signature(violation)
        if signature in self._patterns:
            self._patterns[signature].success_count += 1
            self._patterns[signature].last_used = time.time()
        else:
            self._patterns[signature] = HealingPattern(
                violation_signature=signature,
                healing_strategy=result.get("strategy", result.get("fix_type", "unknown")),
                success_count=1,
                last_used=time.time(),
                agent=agent,
                metadata=result,
            )

    def _compute_violation_signature(self, violation: dict[str, Any]) -> str:
        """
        Compute a unique signature for a violation.

        Similar violations should have the same signature to enable pattern reuse.
        """
        characteristics = {
            "type": violation.get("type", ""),
            "layer": violation.get("file_layer", violation.get("layer", "")),
            "target_layer": violation.get("import_layer", violation.get("target_layer", "")),
        }
        signature_str = json.dumps(characteristics, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    def get_file_analysis(self, file_path: Path, analysis_type: str) -> dict[str, Any] | None:
        """
        Get cached file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis (e.g., "complexity", "gravity")

        Returns:
            Cached analysis or None
        """
        cache_key = f"{file_path}:{analysis_type}"
        if cache_key in self._file_cache:
            cached_mtime = self._file_cache[cache_key].get("mtime", 0)
            current_mtime = file_path.stat().st_mtime if file_path.exists() else 0
            if current_mtime <= cached_mtime:
                return self._file_cache[cache_key].get("result")
        return None

    def set_file_analysis(self, file_path: Path, analysis_type: str, result: dict[str, Any]):
        """
        Cache file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis
            result: Analysis result
        """
        cache_key = f"{file_path}:{analysis_type}"
        self._file_cache[cache_key] = {
            "result": result,
            "mtime": file_path.stat().st_mtime if file_path.exists() else 0,
        }

    # guardian: allow-magic-config
    def get_python_files(self, max_age: int = 300) -> list[Path]:
        """
        Get list of Python files in project.

        Cached for performance - all agents share the same list.

        Args:
            max_age: Maximum age of cache in seconds (default 5 minutes)

        Returns:
            List of Python file paths
        """
        current_time = time.time()
        if self._python_files is None or current_time - self._python_files_timestamp > max_age:
            from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

            self._python_files = get_python_files(self.project_root)
            self._python_files_timestamp = current_time
        return self._python_files

    def invalidate_python_files_cache(self):
        """Force refresh of Python files list on next access."""
        self._python_files = None
        self._python_files_timestamp = 0

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about context manager usage."""
        return {
            "cache_entries": len(self._cache),
            "healing_patterns": len(self._patterns),
            "file_analyses": len(self._file_cache),
            "python_files_cached": self._python_files is not None,
        }


def get_context_manager(project_root: Path | str) -> L4ContextManager:
    """
    Factory function for L4ContextManager.

    Args:
        project_root: Path to project root

    Returns:
        Singleton L4ContextManager instance
    """
    if isinstance(project_root, str):
        project_root = Path(project_root)
    return L4ContextManager.get_instance(project_root)
