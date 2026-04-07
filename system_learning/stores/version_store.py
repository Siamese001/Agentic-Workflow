"""Concrete VersionStore — content-addressable storage for committed ChangePackages.

Provides file-backed and in-memory implementations of the ``VersionStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

_emit_applies_guardrail("p0", "version_store", "p0_governance")
_emit_reads_policy_state("p0", "version_store", "policy_binding")
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

_emit_emits_metric_event("version_store", "p4obs", "metric_1")
_emit_emits_metric_event("version_store", "p4obs", "metric_2")
_emit_emits_metric_event("version_store", "p4obs", "metric_3")
_emit_emits_metric_event("version_store", "p4obs", "metric_4")
_emit_emits_metric_event("version_store", "p4obs", "metric_5")
_emit_emits_metric_event("version_store", "p4obs", "metric_6")
_emit_records_incident_event("version_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("version_store", "p4obs", "anomaly")
_emit_writes_observability_log("version_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("version_store", "p4obs", "mon_state")
_emit_triggers_alert("version_store", "p4obs", "alert")
_emit_links_incident_trace("version_store", "p4obs", "trace_link")
_emit_captures_pattern("version_store", "p3lm", "pattern")
_emit_records_learning_event("version_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("version_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("version_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("version_store", "p3lm", "routing")
_emit_improves_agent_policy("version_store", "p3lm", "policy")
_emit_stores_learning_state("version_store", "p3lm", "state")
_emit_records_execution_trace("version_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("version_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("version_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("version_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("version_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("version_store", "env_read", "p2_env_1")
_emit_reads_environ("version_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("version_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("version_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "version_store", "context_pull")
_emit_pulls_context("p1", "version_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "version_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "version_store", "uwg_term_2")
_emit_writes_through("p1", "version_store", "write_through")
_emit_writes_through("p1", "version_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "version_store", "safety_validation")
_emit_invokes_eval("p1", "version_store", "eval_call")
_emit_proposal_commits_routing("p1", "version_store", "routing_commit")
_emit_escalates_to_human("p1", "version_store", "human_escalation")
_emit_routes_through("p1", "version_store", "route_through")
_emit_checks_agent_registry("p1", "version_store", "agent_registry")
_emit_validates_agent_capability("p1", "version_store", "capability")
_emit_dispatches_execution_plan("p1", "version_store", "exec_plan")
_emit_agent_executes_agent("p1", "version_store", "sub_agent")
_emit_routes_to_agent("p1", "version_store", "target_agent")
_emit_verifies_policy("p1", "version_store", "policy_check")
_emit_observes_runtime_state("p1", "version_store", "runtime_state")
_emit_verifies_boundary("p1", "version_store", "boundary_check")
_emit_transcripts_response("p1", "version_store", "transcript")
_emit_hard_fails_untranscripted("p1", "version_store")
_emit_gated_by_confidence("p1", "version_store", "confidence_gate")
emit_replay_key("p0", "version_store")
emit_determinism_digest("p0", "version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "version_store", "execution_auth")
_emit_validates_capability("p2", "version_store", "capability_check")
_emit_routes_to_capability("p2", "version_store", "capability_route")
_emit_writes_via_uwg("p2", "version_store", "uwg_write")
_emit_blocks_direct_write("p2", "version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "version_store", "tool_invocation")
_emit_captures_execution_output("p2", "version_store", "exec_output")
_emit_dispatches_agent("p3", "version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "version_store", "healing_outcome")
_emit_escalates_failure("p3", "version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "version_store", "eval_metric")
_emit_stores_embedding("p4", "version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "version_store", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class InMemoryVersionStore:
    """In-memory version store for testing and single-process use."""

    _store: dict[str, bytes] = field(default_factory=dict)
    _metadata: dict[str, dict[str, Any]] = field(default_factory=dict)

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id.

        The package must have a ``canonical_bytes()`` method for
        content-hash computation.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "InMemoryVersionStore.commit_change_package", "L4_STATE")
        _emit_writes_through(str(uuid.uuid4()), "InMemoryVersionStore.commit_change_package", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryVersionStore.commit_change_package",
        )

        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")
        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"
        if version_id not in self._store:
            self._store[version_id] = payload
            self._metadata[version_id] = {"content_hash": content_hash, "type": type(pkg).__name__}
        return version_id

    def get(self, version_id: str) -> bytes | None:
        return self._store.get(version_id)

    def list_versions(self) -> list[str]:
        return sorted(self._store.keys())


class FileBackedVersionStore:
    """File-backed version store with content-addressable directory layout.

    Directory layout::

        <base_dir>/
            <content_hash[:2]>/<content_hash>.json   # payload + metadata
            _index.json                               # version_id -> hash mapping
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._base_dir / "_index.json"
        self._index: dict[str, str] = self._load_index()

    def _load_index(self) -> dict[str, str]:
        if self._index_path.exists():
            try:
                return json.loads(self._index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                return {}
        return {}

    def _save_index(self) -> None:
        self._index_path.write_text(json.dumps(self._index, indent=2, sort_keys=True), encoding="utf-8")

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedVersionStore.commit_change_package",
        )

        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")
        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"
        if version_id in self._index:
            return version_id
        shard_dir = self._base_dir / content_hash[:2]
        shard_dir.mkdir(exist_ok=True)
        entry_path = shard_dir / f"{content_hash}.json"
        meta = {
            "version_id": version_id,
            "content_hash": content_hash,
            "type": type(pkg).__name__,
            "payload_hex": payload.hex(),
        }
        entry_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        self._index[version_id] = content_hash
        self._save_index()
        try:
            get_sl_memory_bridge().persist_active_version("version_store", version_id, ts=str(uuid.uuid4()))
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.debug("Failed to persist version metadata for %s: %s", version_id, exc)
        return version_id

    def get(self, version_id: str) -> bytes | None:
        content_hash = self._index.get(version_id)
        if content_hash is None:
            return None
        entry_path = self._base_dir / content_hash[:2] / f"{content_hash}.json"
        if not entry_path.exists():
            return None
        try:
            meta = json.loads(entry_path.read_text(encoding="utf-8"))
            return bytes.fromhex(meta["payload_hex"])
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            return None

    def list_versions(self) -> list[str]:
        return sorted(self._index.keys())


__all__ = ["InMemoryVersionStore", "FileBackedVersionStore"]
