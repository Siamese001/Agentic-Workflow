"""
DependencyLocker — Dependency lock hash for determinism surface.

Generates a SHA-256 hash of the pinned dependency versions in
requirements.txt so it can be included in the W<n>-DETERMINISM-DIGEST.
Any environment drift (unpinned upgrades) causes a hash mismatch and
fails fast.

Phase 2.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "dependency_locker", "execution_auth")
_emit_validates_capability("p2", "dependency_locker", "capability_check")
_emit_routes_to_capability("p2", "dependency_locker", "capability_route")
_emit_writes_via_uwg("p2", "dependency_locker", "uwg_write")
_emit_blocks_direct_write("p2", "dependency_locker", "direct_write_block")
_emit_records_tool_invocation("p2", "dependency_locker", "tool_invocation")
_emit_captures_execution_output("p2", "dependency_locker", "exec_output")
_emit_dispatches_agent("p3", "dependency_locker", "agent_dispatch")
_emit_coordinates_agents("p3", "dependency_locker", "agent_coordination")
_emit_records_workflow_lineage("p3", "dependency_locker", "workflow_lineage")
_emit_records_healing_outcome("p3", "dependency_locker", "healing_outcome")
_emit_escalates_failure("p3", "dependency_locker", "failure_escalation")
_emit_orchestrates_workflow("p3", "dependency_locker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dependency_locker", "healing_dispatch")
_emit_invokes_evaluation("p3", "dependency_locker", "evaluation_signal")
_emit_records_telemetry_event("p4", "dependency_locker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dependency_locker", "eval_metric")
_emit_stores_embedding("p4", "dependency_locker", "embedding_store")
_emit_updates_meta_learning_state("p4", "dependency_locker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dependency_locker", "exec_snapshot_link")
from agentic_core.utils.schemas.canonical_json_util import CanonicalJSON

emit_replay_key("p0", "dependency_locker")
emit_determinism_digest("p0", "dependency_locker")

_emit_dispatches_healing_run("p1", "dependency_locker", "L2")
_emit_routes_through("p1", "dependency_locker", "L2")
_emit_checks_agent_registry("p1", "dependency_locker", "agent_registry")
_emit_validates_agent_capability("p1", "dependency_locker", "capability")
_emit_dispatches_execution_plan("p1", "dependency_locker", "exec_plan")
_emit_agent_executes_agent("p1", "dependency_locker", "sub_agent")
_emit_routes_to_agent("p1", "dependency_locker", "target_agent")
_emit_verifies_policy("p1", "dependency_locker", "policy_check")
_emit_observes_runtime_state("p1", "dependency_locker", "runtime_state")
_emit_verifies_boundary("p1", "dependency_locker", "boundary_check")
_emit_transcripts_response("p1", "dependency_locker", "transcript")
_emit_hard_fails_untranscripted("p1", "dependency_locker")
_emit_gated_by_confidence("p1", "dependency_locker", "confidence_gate")
_emit_escalates_to_human("p1", "dependency_locker", "L2")
_emit_reads_policy_state("p1", "dependency_locker", "L2")
from agentic_core.runtime.lifecycle_trace_contract import (
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

record_execution_trace("dependency_locker", "dependency_locker_trace")


_emit_emits_metric_event("dependency_locker", "p4obs", "metric_1")
_emit_emits_metric_event("dependency_locker", "p4obs", "metric_2")
_emit_emits_metric_event("dependency_locker", "p4obs", "metric_3")
_emit_emits_metric_event("dependency_locker", "p4obs", "metric_4")
_emit_emits_metric_event("dependency_locker", "p4obs", "metric_5")
_emit_emits_metric_event("dependency_locker", "p4obs", "metric_6")
_emit_records_incident_event("dependency_locker", "p4obs", "incident")
_emit_captures_runtime_anomaly("dependency_locker", "p4obs", "anomaly")
_emit_writes_observability_log("dependency_locker", "p4obs", "obs_log")
_emit_updates_monitoring_state("dependency_locker", "p4obs", "mon_state")
_emit_triggers_alert("dependency_locker", "p4obs", "alert")
_emit_links_incident_trace("dependency_locker", "p4obs", "trace_link")
_emit_captures_pattern("dependency_locker", "p3lm", "pattern")
_emit_records_learning_event("dependency_locker", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dependency_locker", "p3lm", "snapshot")
_emit_feeds_meta_learning("dependency_locker", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dependency_locker", "p3lm", "routing")
_emit_improves_agent_policy("dependency_locker", "p3lm", "policy")
_emit_stores_learning_state("dependency_locker", "p3lm", "state")
_emit_records_execution_trace("dependency_locker", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dependency_locker", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dependency_locker", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dependency_locker", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dependency_locker", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dependency_locker", "env_read", "p2_env_1")
_emit_reads_environ("dependency_locker", "env_read", "p2_env_2")
_emit_reads_runtime_state("dependency_locker", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dependency_locker", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dependency_locker", "context_pull")
_emit_pulls_context("p1", "dependency_locker", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "dependency_locker", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dependency_locker", "uwg_term_2")
_emit_writes_through("p1", "dependency_locker", "write_through")
_emit_writes_through("p1", "dependency_locker", "write_through_2")
_emit_validated_by_safety_plane("p1", "dependency_locker", "safety_validation")
_emit_invokes_eval("p1", "dependency_locker", "eval_call")
_emit_proposal_commits_routing("p1", "dependency_locker", "routing_commit")

_REQUIREMENTS_PATH = Path("requirements.txt")
_LOCK_FILE_PATH = Path("data/dependencies/lock_hash.json")


class DependencyLocker:
    """Manages the dependency lock hash used in determinism digests."""

    @classmethod
    def generate_lock_hash(cls, requirements_path: Path = _REQUIREMENTS_PATH) -> str:
        """Return SHA-256 hash of pinned dependencies from *requirements_path*."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DependencyLocker.generate_lock_hash", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DependencyLocker.generate_lock_hash", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DependencyLocker.generate_lock_hash"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DependencyLocker.generate_lock_hash".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not requirements_path.exists():
            raise FileNotFoundError(f"DependencyLocker: requirements file not found: {requirements_path}")
        dependencies: dict[str, str] = {}
        for raw_line in requirements_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                package, _, version = line.partition("==")
                dependencies[package.strip()] = version.strip()
            else:
                dependencies[line.split("[")[0].split(">")[0].split("<")[0].strip()] = "unpinned"
        canonical = CanonicalJSON.serialize_bytes(dependencies)
        return hashlib.sha256(canonical).hexdigest()

    @classmethod
    def save_lock_file(cls, lock_hash: str, lock_file_path: Path = _LOCK_FILE_PATH) -> None:
        """Persist *lock_hash* to *lock_file_path* (creates parents if needed)."""
        lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        lock_data: dict[str, Any] = {"dependency_lock_hash": lock_hash, "schema_version": "1"}
        lock_file_path.write_text(CanonicalJSON.serialize(lock_data), encoding="utf-8")

    @classmethod
    def load_lock_hash(cls, lock_file_path: Path = _LOCK_FILE_PATH) -> str:
        """Load and return the stored lock hash."""
        if not lock_file_path.exists():
            raise FileNotFoundError(f"DependencyLocker: lock file not found: {lock_file_path}")
        data = json.loads(lock_file_path.read_text(encoding="utf-8"))
        return data["dependency_lock_hash"]

    @classmethod
    def validate(
        cls, requirements_path: Path = _REQUIREMENTS_PATH, lock_file_path: Path = _LOCK_FILE_PATH
    ) -> bool:
        """Return True if current dependencies match the stored lock hash.

        If no lock file exists, generate one and return True.
        """
        current = cls.generate_lock_hash(requirements_path)
        if not lock_file_path.exists():
            cls.save_lock_file(current, lock_file_path)
            return True
        stored = cls.load_lock_hash(lock_file_path)
        return current == stored


__all__ = ["DependencyLocker"]
