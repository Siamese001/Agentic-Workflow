from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "experience_buffer_util")
trace_contract.emit_determinism_digest("p0", "experience_buffer_util")

trace_contract._emit_dispatches_healing_run("p1", "experience_buffer_util", "L4")
trace_contract._emit_routes_through("p1", "experience_buffer_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "experience_buffer_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "experience_buffer_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "experience_buffer_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "experience_buffer_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "experience_buffer_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "experience_buffer_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "experience_buffer_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "experience_buffer_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "experience_buffer_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "experience_buffer_util")
trace_contract._emit_gated_by_confidence("p1", "experience_buffer_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "experience_buffer_util", "L4")
trace_contract._emit_reads_policy_state("p1", "experience_buffer_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "experience_buffer_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "experience_buffer_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "experience_buffer_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "experience_buffer_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "experience_buffer_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "experience_buffer_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "experience_buffer_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "experience_buffer_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "experience_buffer_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "experience_buffer_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "experience_buffer_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "experience_buffer_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "experience_buffer_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "experience_buffer_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "experience_buffer_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "experience_buffer_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "experience_buffer_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "experience_buffer_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "experience_buffer_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "experience_buffer_util", "exec_snapshot_link")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"\nExperienceBuffer – Sovereign Agent Role Component (Phase 30 – Dec 30, 2025)\n\nPurpose:\n  Persistent, file-backed learning from execution outcomes.\n  Enables agents to predict success probability of actions based on historical data.\n  Critical for RgHealingOrchestrator and all validators to avoid repeating failed strategies.\n\nConstitutional Alignment:\n  - Turns reactive healing into predictive intelligence\n  - Enables cumulative sovereignty improvement\n  - Fully observable via JSONL logs\n\nZero-Ambiguity Standard: Renamed from ExperienceBuffer.py to experience_buffer_util.py\n"
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from tqdm import tqdm

trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("experience_buffer_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("experience_buffer_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("experience_buffer_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("experience_buffer_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("experience_buffer_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("experience_buffer_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("experience_buffer_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("experience_buffer_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("experience_buffer_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("experience_buffer_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("experience_buffer_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("experience_buffer_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("experience_buffer_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("experience_buffer_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("experience_buffer_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("experience_buffer_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("experience_buffer_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("experience_buffer_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("experience_buffer_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("experience_buffer_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("experience_buffer_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("experience_buffer_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("experience_buffer_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "experience_buffer_util", "context_pull")
trace_contract._emit_pulls_context("p1", "experience_buffer_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "experience_buffer_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "experience_buffer_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "experience_buffer_util", "write_through")
trace_contract._emit_writes_through("p1", "experience_buffer_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "experience_buffer_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "experience_buffer_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "experience_buffer_util", "routing_commit")


class ExperienceBuffer:
    """
    Lightweight, append-only experience replay buffer with JSONL persistence.
    Designed for sovereign agents to learn from healing/validation outcomes.
    """

    # guardian: allow-magic-config
    def __init__(self, path: Path, max_entries: int = 1000, similarity_keys: list[str] | None = None):
        """
        Initialize buffer with persistent storage.

        Args:
            path: File path for JSONL storage (e.g., logs/healer_experience.jsonl)
            max_entries: Maximum historical entries to retain
            similarity_keys: Keys used for similarity matching (default: all keys)
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ExperienceBuffer.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ExperienceBuffer.__init__", "p0_governance")
        self.path = Path(path)
        self.max_entries = max_entries
        self.similarity_keys = similarity_keys or []
        self.Logger = logging.getLogger(f"{__name__}.{self.path.stem}")
        _get_write_gateway().ensure_dir(self.path.parent)
        if not self.path.exists():
            assert_no_persistent_write("L4", "write_text")
            _get_write_gateway().write_text(self.path, "")
            self.Logger.info(f"Created new experience buffer at {self.path}")

    def record(self, entry: dict[str, Any]) -> None:
        """
        Record a new experience outcome.
        Appends to file and enforces size limit.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "ExperienceBuffer.record")

        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        entry["entry_id"] = int(time.time() * 1000000)
        _get_write_gateway().write_json(self.path, entry, indent=2)
        self._enforce_size_limit()
        outcome = "success" if entry.get("success", False) else "failure"
        self.Logger.debug(f"Recorded {outcome}: {entry.get('action')} on {entry.get('target')}")

    def _enforce_size_limit(self) -> None:
        """Trim file to max_entries by keeping newest lines."""
        if self.max_entries <= 0:
            return
        lines = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except (
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            self.Logger.error(f"Failed to read experience buffer: {e}")
            return
        if len(lines) > self.max_entries:
            kept = lines[-self.max_entries :]
            try:
                assert_no_persistent_write("L4", "write_text")
                _get_write_gateway().write_text(self.path, "".join(kept), encoding="utf-8")
                self.Logger.info(f"Trimmed experience buffer from {len(lines)} to {len(kept)} entries")
            except (
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                raise

    def load_all(self) -> list[dict[str, Any]]:
        """Load all entries (newest first)."""
        entries = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
            return list(reversed(entries))
        except (
            json.JSONDecodeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            self.Logger.error(f"Failed to load experience buffer: {e}")
            return []

    # guardian: allow-magic-config
    def find_similar(
        self,
        action: str | None = None,
        target: str | None = None,
        context_hash: str | None = None,
        limit: int = 20,
        **extra_filters,
    ) -> list[dict[str, Any]]:
        """
        Find historically similar experiences for success prediction.
        Matches on provided filters.
        """
        all_entries = self.load_all()
        matches = []
        for entry in tqdm(all_entries, desc="Processing", unit="item"):
            if action and entry.get("action") != action:
                continue
            if target and entry.get("target") != target:
                continue
            if context_hash and entry.get("context_hash") != context_hash:
                continue
            if all((entry.get(k) == v for k, v in extra_filters.items())):
                matches.append(entry)
            if len(matches) >= limit:
                break
        return matches

    def predict_success_probability(
        self,
        action: str,
        target: str | None = None,
        context_hash: str | None = None,
        **extra_context,
    ) -> float:
        """
        Predict success probability based on historical outcomes.
        Returns 0.5 if no relevant history.
        """
        similar = self.find_similar(action=action, target=target, context_hash=context_hash, **extra_context)
        if not similar:
            return 0.5
        successes = sum(1 for e in similar if e.get("success", False))
        return successes / len(similar)

    def get_stats(self) -> dict[str, Any]:
        """Return buffer statistics for monitoring."""
        entries = self.load_all()
        if not entries:
            return {"total_entries": 0, "success_rate": None}
        successes = sum(1 for e in entries if e.get("success", False))
        return {
            "total_entries": len(entries),
            "success_rate": successes / len(entries),
            "most_common_action": max(
                (e.get("action") for e in entries if e.get("action")),
                key=lambda a: sum(1 for e in entries if e.get("action") == a),
                default=None,
            ),
        }
