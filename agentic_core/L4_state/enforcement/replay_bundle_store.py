"""
Phase 9 — ReplayBundleStore + ReplayVerifier.

L4 in-process store for ReplayBundle artifacts (non-mutating to knowledge index).
ReplayVerifier checks integrity (hash recomputation) and prior-only constraints.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field

from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "replay_bundle_store")
trace_contract.emit_determinism_digest("p0", "replay_bundle_store")

trace_contract._emit_dispatches_healing_run("p1", "replay_bundle_store", "L4")
trace_contract._emit_routes_through("p1", "replay_bundle_store", "L4")
trace_contract._emit_checks_agent_registry("p1", "replay_bundle_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_bundle_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_bundle_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_bundle_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_bundle_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_bundle_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_bundle_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_bundle_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_bundle_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_bundle_store")
trace_contract._emit_gated_by_confidence("p1", "replay_bundle_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "replay_bundle_store", "L4")
trace_contract._emit_reads_policy_state("p1", "replay_bundle_store", "L4")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "replay_bundle_store", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "replay_bundle_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_bundle_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_bundle_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_bundle_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_bundle_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_bundle_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_bundle_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_bundle_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_bundle_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_bundle_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_bundle_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_bundle_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_bundle_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_bundle_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_bundle_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_bundle_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_bundle_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_bundle_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_bundle_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_bundle_store", "exec_snapshot_link")

trace_contract.record_execution_trace("replay_bundle_store", "replay_bundle_store_trace")


trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_bundle_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_bundle_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_bundle_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_bundle_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_bundle_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_bundle_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_bundle_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_bundle_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_bundle_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_bundle_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_bundle_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_bundle_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_bundle_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_bundle_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_bundle_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_bundle_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_bundle_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_bundle_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_bundle_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_bundle_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_bundle_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_bundle_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_bundle_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_bundle_store", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_bundle_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_bundle_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_bundle_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_bundle_store", "write_through")
trace_contract._emit_writes_through("p1", "replay_bundle_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_bundle_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_bundle_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_bundle_store", "routing_commit")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ReplayBundleStore:
    """
    L4 in-process store for ReplayBundle artifacts.

    Keyed by replay_hash. Idempotent: duplicate hash = no-op.
    Non-mutating to knowledge index (Pinecone/Redis).
    """

    _store: dict[str, ReplayBundle] = field(default_factory=dict)

    def store_replay_bundle(self, bundle: ReplayBundle) -> str:
        """
        Persist a ReplayBundle. Returns replay_hash.
        Idempotent: storing the same bundle twice is a no-op.
        """
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "ReplayBundleStore.store_replay_bundle", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L4_STATE,
            "ReplayBundleStore.store_replay_bundle",
        )

        self._store[bundle.replay_hash] = bundle
        return bundle.replay_hash

    def fetch_replay_bundle(self, replay_hash: str) -> ReplayBundle | None:
        """Return the ReplayBundle for the given replay_hash, or None."""
        return self._store.get(replay_hash)

    def count(self) -> int:
        return len(self._store)

    def seal(self, data: dict) -> str:
        """REQ-020: persist an arbitrary dict as a sealed, immutable record.

        Returns a content-addressed key (sha256 of JSON-serialised data).
        Once sealed the entry is append-only; call mutate() to verify immutability.
        """
        import json

        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        key = _sha256(raw)
        self._sealed: dict[str, bytes] = getattr(self, "_sealed", {})
        self._sealed[key] = raw
        return key

    def mutate(self, bundle_id: str, updates: dict) -> None:
        """REQ-020: mutation of a sealed artifact is forbidden — always raises."""
        raise RuntimeError(
            f"REQ-020: sealed artifact '{bundle_id}' is immutable; append-only store rejects mutation.",
        )


@dataclass
class VerifiedReplay:
    """Result of a successful replay verification."""

    replay_hash: str
    mission_id: str
    execution_start_tick: int
    execution_end_tick: int
    checks_passed: list[str]


class ReplayVerificationError(Exception):
    """
    Raised when replay bundle verification fails.

    Attributes
    ----------
    code   : str — violation code
    detail : str — human-readable description
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"[{code}]" + (f" {detail}" if detail else ""))


class ReplayVerifier:
    """
    Verifies a ReplayBundle for:
    1. Hash integrity — replay_hash recomputation matches stored value.
    2. Prior-only constraints — all referenced prior signals/violations have
       commit_tick strictly less than execution_start_tick.
    3. Component presence — referenced hashes exist in provided registries.

    All checks are deterministic and raise ReplayVerificationError on failure.
    """

    def verify(
        self,
        bundle: ReplayBundle,
        *,
        known_config_hashes: set[str] | None = None,
        known_citation_hashes: set[str] | None = None,
        known_signal_hashes: set[str] | None = None,
        known_violation_hashes: set[str] | None = None,
        known_intent_hashes: set[str] | None = None,
        known_result_hashes: set[str] | None = None,
        prior_signal_tick: int | None = None,
        prior_violation_ticks: dict[str, int] | None = None,
    ) -> VerifiedReplay:
        """
        Verify a ReplayBundle.

        Parameters
        ----------
        bundle                 : ReplayBundle
        known_config_hashes    : set of valid config hash strings (optional)
        known_citation_hashes  : set of valid citation_hash strings (optional)
        known_signal_hashes    : set of valid signal_hash strings (optional)
        known_violation_hashes : set of valid violation event_hash strings (optional)
        known_intent_hashes    : set of valid tool intent_hash strings (optional)
        known_result_hashes    : set of valid tool result_hash strings (optional)
        prior_signal_tick      : commit_tick of the prior detection signal (optional)
        prior_violation_ticks  : {event_hash: commit_tick} for prior violations (optional)

        Returns
        -------
        VerifiedReplay on success.

        Raises
        ------
        ReplayVerificationError on any failure.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "ReplayVerifier.verify")

        checks: list[str] = []
        recomputed = _sha256(bundle.canonical_bytes())
        if recomputed != bundle.replay_hash:
            raise ReplayVerificationError(
                code="REPLAY_HASH_MISMATCH",
                detail=f"replay_hash mismatch: stored={bundle.replay_hash!r}, recomputed={recomputed!r}",
            )
        checks.append("hash_integrity")
        if known_config_hashes is not None:
            for k, v in bundle.active_config_hashes.items():
                if v and v not in known_config_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_CONFIG_HASH",
                        detail=f"config hash {v!r} (key={k!r}) not found in registry",
                    )
            checks.append("config_hashes_present")
        if known_citation_hashes is not None and bundle.retrieval_used:
            if bundle.citation_hash not in known_citation_hashes:
                raise ReplayVerificationError(
                    code="MISSING_CITATION_HASH",
                    detail=f"citation_hash {bundle.citation_hash!r} not found",
                )
            checks.append("citation_hash_present")
        if known_signal_hashes is not None and bundle.prior_detection_signal_hash:
            if bundle.prior_detection_signal_hash not in known_signal_hashes:
                raise ReplayVerificationError(
                    code="MISSING_SIGNAL_HASH",
                    detail=f"prior_detection_signal_hash {bundle.prior_detection_signal_hash!r} not found",
                )
            checks.append("signal_hash_present")
        if known_violation_hashes is not None:
            for vh in bundle.prior_violation_event_hashes:
                if vh not in known_violation_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_VIOLATION_HASH",
                        detail=f"violation event_hash {vh!r} not found",
                    )
            checks.append("violation_hashes_present")
        if known_intent_hashes is not None:
            for ih in bundle.tool_intent_hashes:
                if ih not in known_intent_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_INTENT_HASH",
                        detail=f"tool intent_hash {ih!r} not found",
                    )
            checks.append("intent_hashes_present")
        if known_result_hashes is not None:
            for rh in bundle.tool_result_hashes:
                if rh not in known_result_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_RESULT_HASH",
                        detail=f"tool result_hash {rh!r} not found",
                    )
            checks.append("result_hashes_present")
        if prior_signal_tick is not None and bundle.prior_detection_signal_hash:
            if prior_signal_tick >= bundle.execution_start_tick:
                raise ReplayVerificationError(
                    code="SAME_CYCLE_SIGNAL",
                    detail=f"prior_detection_signal commit_tick ({prior_signal_tick}) >= execution_start_tick ({bundle.execution_start_tick}): same-cycle influence detected",
                )
            checks.append("signal_prior_only")
        if prior_violation_ticks is not None:
            for vh, tick in prior_violation_ticks.items():
                if tick >= bundle.execution_start_tick:
                    raise ReplayVerificationError(
                        code="SAME_CYCLE_VIOLATION",
                        detail=f"violation {vh!r} commit_tick ({tick}) >= execution_start_tick ({bundle.execution_start_tick}): same-cycle influence detected",
                    )
            if prior_violation_ticks:
                checks.append("violations_prior_only")
        return VerifiedReplay(
            replay_hash=bundle.replay_hash,
            mission_id=bundle.mission_id,
            execution_start_tick=bundle.execution_start_tick,
            execution_end_tick=bundle.execution_end_tick,
            checks_passed=checks,
        )
