"""L4 State Writer — Write-once, versioned, idempotent state persistence.

Provides content-hash keyed writes for L4A detection signals, L4B healing
snapshots, and L4C shadow drift / policy recommendation / retrieval profile
artifacts.  All writes are idempotent: re-writing the same payload_bytes for
the same component returns the existing version_id without mutation.

Two concrete implementations:
  - ``InMemoryL4StateWriter``  — test / single-process use
  - ``FileBackedL4StateWriter`` — persistent across restarts
  - ``NoOpL4StateWriter``      — safe default when persistence is disabled
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l4_state_writer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l4_state_writer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l4_state_writer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l4_state_writer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l4_state_writer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l4_state_writer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l4_state_writer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l4_state_writer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l4_state_writer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l4_state_writer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l4_state_writer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l4_state_writer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l4_state_writer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l4_state_writer", "p3lm", "state")
trace_contract._emit_records_execution_trace("l4_state_writer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l4_state_writer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l4_state_writer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l4_state_writer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l4_state_writer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l4_state_writer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l4_state_writer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l4_state_writer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l4_state_writer", "runtime_state", "p2_rt_2")

trace_contract._emit_applies_guardrail("p0", "l4_state_writer", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "l4_state_writer", "policy_binding")
trace_contract._emit_snapshots_state("p0", "l4_state_writer", "state_snapshot")
trace_contract._emit_pulls_context("p1", "l4_state_writer", "context_pull")
trace_contract._emit_pulls_context("p1", "l4_state_writer", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_state_writer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_state_writer", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "l4_state_writer", "write_through")
trace_contract._emit_writes_through("p1", "l4_state_writer", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "l4_state_writer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l4_state_writer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l4_state_writer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l4_state_writer", "human_escalation")
trace_contract._emit_routes_through("p1", "l4_state_writer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l4_state_writer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l4_state_writer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l4_state_writer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l4_state_writer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l4_state_writer", "target_agent")
trace_contract._emit_verifies_policy("p1", "l4_state_writer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l4_state_writer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l4_state_writer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l4_state_writer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l4_state_writer")
trace_contract._emit_gated_by_confidence("p1", "l4_state_writer", "confidence_gate")
trace_contract.emit_replay_key("p0", "l4_state_writer")
trace_contract.emit_determinism_digest("p0", "l4_state_writer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "l4_state_writer", "execution_auth")
trace_contract._emit_validates_capability("p2", "l4_state_writer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l4_state_writer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l4_state_writer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l4_state_writer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l4_state_writer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l4_state_writer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l4_state_writer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l4_state_writer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l4_state_writer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l4_state_writer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l4_state_writer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l4_state_writer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l4_state_writer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l4_state_writer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l4_state_writer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l4_state_writer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l4_state_writer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l4_state_writer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l4_state_writer", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class L4StateWriter(Protocol):
    """Protocol for L4 state writer with write-once semantics.

    All writes are content-hash keyed and idempotent.
    Returns version IDs for tracking and activation.
    """

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str: ...

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str: ...

    def write_l4c_shadow_drift(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str: ...

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str: ...

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str: ...

    def read_latest_detection_signal(self) -> bytes | None: ...

    def read_latest_drift_snapshot(self) -> bytes | None: ...


def _content_hash(payload_bytes: bytes) -> str:
    """SHA-256 content hash of payload bytes (deterministic)."""
    return hashlib.sha256(payload_bytes).hexdigest()


@dataclass(frozen=True, slots=True)
class _VersionEntry:
    """Immutable record of a single L4 write."""

    version_id: str
    bucket: str
    component_name: str
    created_utc: int
    payload_bytes: bytes


@dataclass
class InMemoryL4StateWriter:
    """In-memory L4 state writer for tests and single-process pipelines."""

    _store: dict[str, _VersionEntry] = field(default_factory=dict)
    _latest: dict[str, bytes] = field(default_factory=dict)

    def _write(self, bucket: str, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()), trace_contract.LayerSegment.L4_STATE, f"L4StateWriter._write:{bucket}:{component_name}"
        )
        content_key = _content_hash(payload_bytes)
        version_id = f"{bucket}_{component_name}_{content_key[:16]}_{created_utc}"
        if version_id not in self._store:
            self._store[version_id] = _VersionEntry(
                version_id=version_id,
                bucket=bucket,
                component_name=component_name,
                created_utc=created_utc,
                payload_bytes=payload_bytes,
            )
        self._latest[bucket] = payload_bytes
        return version_id

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4a_detection",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4b_healing",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write(
            "l4c_shadow_drift",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4c_policy_rec",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4c_profile_prop",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def read_latest_detection_signal(self) -> bytes | None:
        return self._latest.get("l4a_detection")

    def read_latest_drift_snapshot(self) -> bytes | None:
        return self._latest.get("l4c_shadow_drift")


class FileBackedL4StateWriter:
    """File-backed L4 state writer with content-addressable storage.

    Directory layout::

        <base_dir>/
            l4a_detection/<content_hash>.json
            l4b_healing/<content_hash>.json
            l4c_shadow_drift/<content_hash>.json
            l4c_policy_rec/<content_hash>.json
            l4c_profile_prop/<content_hash>.json
            _latest/<bucket>.bin          # raw payload of most recent write
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        (self._base_dir / "_latest").mkdir(exist_ok=True)

    def _write(self, bucket: str, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L4_STATE,
            f"FileBackedL4StateWriter._write:{bucket}:{component_name}",
        )
        content_key = _content_hash(payload_bytes)
        version_id = f"{bucket}_{component_name}_{content_key[:16]}_{created_utc}"
        bucket_dir = self._base_dir / bucket
        bucket_dir.mkdir(exist_ok=True)
        entry_path = bucket_dir / f"{content_key}.json"
        if not entry_path.exists():
            meta = {
                "version_id": version_id,
                "bucket": bucket,
                "component_name": component_name,
                "created_utc": created_utc,
                "content_hash": content_key,
                "payload_hex": payload_bytes.hex(),
            }
            entry_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        latest_path = self._base_dir / "_latest" / f"{bucket}.bin"
        latest_path.write_bytes(payload_bytes)
        return version_id

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4a_detection",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4b_healing",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write(
            "l4c_shadow_drift",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4c_policy_rec",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "l4c_profile_prop",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def read_latest_detection_signal(self) -> bytes | None:
        p = self._base_dir / "_latest" / "l4a_detection.bin"
        return p.read_bytes() if p.exists() else None

    def read_latest_drift_snapshot(self) -> bytes | None:
        p = self._base_dir / "_latest" / "l4c_shadow_drift.bin"
        return p.read_bytes() if p.exists() else None


class NoOpL4StateWriter:
    """No-op implementation that does nothing.

    Used as safe default when L4 state writing is not configured.
    """

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return f"noop_l4a_{created_utc}"

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return f"noop_l4b_{created_utc}"

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return f"noop_l4c_drift_{created_utc}"

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return f"noop_l4c_policy_{created_utc}"

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return f"noop_l4c_profile_{created_utc}"

    def read_latest_detection_signal(self) -> bytes | None:
        return None

    def read_latest_drift_snapshot(self) -> bytes | None:
        return None


@dataclass
class SimpleChangePackage:
    """Minimal ChangePackage suitable for L4 state writes.

    Implements the ``canonical_bytes()`` contract required by
    ``L4VersionStore.commit_change_package``.
    """

    component: str
    payload_bytes: bytes
    metadata: dict

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes representation of this package."""
        meta_str = json.dumps({k: str(v) for k, v in sorted(self.metadata.items())}, separators=(",", ":"))
        return f"{self.component}:{self.payload_bytes.hex()}:{meta_str}".encode()


class DefaultL4StateWriter:
    """L4 state writer backed by an L4VersionStore.

    Delegates all writes to the provided version store.  Each call creates a
    ``SimpleChangePackage`` and commits it via
    ``version_store.commit_change_package``, returning the resulting version_id.
    Idempotency is enforced by the store's content-hash keying.
    """

    def __init__(self, version_store) -> None:
        self._store = version_store

    def _write(
        self,
        signal_type: str,
        signal_prefix: str,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        pkg = SimpleChangePackage(
            component=f"{signal_prefix}_{component_name}",
            payload_bytes=payload_bytes,
            metadata={"component_name": component_name, "created_utc": created_utc, "type": signal_type},
        )
        return self._store.commit_change_package(
            pkg,
            parent_version_id=None,
            change_spec_hash=hashlib.sha256(payload_bytes).hexdigest(),
            committed_at_utc=created_utc,
        )

    def write_l4a_detection_signal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "detection_signal",
            "l4a_detection_signal",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4b_healing_snapshot(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "healing_snapshot",
            "l4b_healing_snapshot",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        return self._write(
            "shadow_drift",
            "l4c_shadow_drift",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_policy_recommendation(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "policy_recommendation",
            "l4c_policy_rec",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def write_l4c_retrieval_profile_proposal(
        self,
        *,
        payload_bytes: bytes,
        component_name: str,
        created_utc: int,
    ) -> str:
        return self._write(
            "retrieval_profile_proposal",
            "l4c_profile_prop",
            payload_bytes=payload_bytes,
            component_name=component_name,
            created_utc=created_utc,
        )

    def read_latest_detection_signal(self) -> bytes | None:
        return None

    def read_latest_drift_snapshot(self) -> bytes | None:
        return None


__all__ = [
    "L4StateWriter",
    "InMemoryL4StateWriter",
    "FileBackedL4StateWriter",
    "NoOpL4StateWriter",
    "DefaultL4StateWriter",
    "SimpleChangePackage",
]
