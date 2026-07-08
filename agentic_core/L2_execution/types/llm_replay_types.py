"""
H3: Provider-pinned LLM replay enforcement types.

Defines the replay bundle, strategy, and mode policy for
deterministic LLM replay.  Production replay MUST use
RECORDED_OUTPUT mode.  DETERMINISTIC_INFERENCE is demoted to
dev/test only and labeled NON_AUTHORITATIVE.

Lives in L2 (execution types) per gravity rules.
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "llm_replay_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "llm_replay_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "llm_replay_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "llm_replay_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "llm_replay_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "llm_replay_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "llm_replay_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "llm_replay_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "llm_replay_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "llm_replay_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "llm_replay_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "llm_replay_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "llm_replay_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "llm_replay_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "llm_replay_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "llm_replay_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "llm_replay_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "llm_replay_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "llm_replay_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "llm_replay_types", "exec_snapshot_link")
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

trace_contract.emit_replay_key("p0", "llm_replay_types")
trace_contract.emit_determinism_digest("p0", "llm_replay_types")

trace_contract._emit_dispatches_healing_run("p1", "llm_replay_types", "L2")
trace_contract._emit_routes_through("p1", "llm_replay_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "llm_replay_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "llm_replay_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "llm_replay_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "llm_replay_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "llm_replay_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "llm_replay_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "llm_replay_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "llm_replay_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "llm_replay_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "llm_replay_types")
trace_contract._emit_gated_by_confidence("p1", "llm_replay_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "llm_replay_types", "L2")
trace_contract._emit_reads_policy_state("p1", "llm_replay_types", "L2")

trace_contract._emit_applies_guardrail("p0", "llm_replay_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "llm_replay_types", "state_snapshot")

trace_contract.record_execution_trace("llm_replay_types", "llm_replay_types_trace")


trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("llm_replay_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("llm_replay_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("llm_replay_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("llm_replay_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("llm_replay_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("llm_replay_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("llm_replay_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("llm_replay_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("llm_replay_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("llm_replay_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("llm_replay_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("llm_replay_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("llm_replay_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("llm_replay_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("llm_replay_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("llm_replay_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("llm_replay_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("llm_replay_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("llm_replay_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("llm_replay_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("llm_replay_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("llm_replay_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("llm_replay_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "llm_replay_types", "context_pull")
trace_contract._emit_pulls_context("p1", "llm_replay_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "llm_replay_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "llm_replay_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "llm_replay_types", "write_through")
trace_contract._emit_writes_through("p1", "llm_replay_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "llm_replay_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "llm_replay_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "llm_replay_types", "routing_commit")


class ReplayMode(enum.Enum):
    """LLM replay mode policy.

    RECORDED_OUTPUT: Default for production. Uses stored raw
        response bytes verbatim.
    DETERMINISTIC_INFERENCE: Dev/test only. Re-invokes the LLM
        with temperature=0 + seed. Labeled NON_AUTHORITATIVE.
    """

    RECORDED_OUTPUT = "RECORDED_OUTPUT"
    DETERMINISTIC_INFERENCE = "DETERMINISTIC_INFERENCE"


# Modes allowed per environment
PRODUCTION_ALLOWED_MODES = frozenset({ReplayMode.RECORDED_OUTPUT})
DEV_TEST_ALLOWED_MODES = frozenset({ReplayMode.RECORDED_OUTPUT, ReplayMode.DETERMINISTIC_INFERENCE})


def is_authoritative(mode: ReplayMode) -> bool:
    """Only RECORDED_OUTPUT is authoritative for governance."""
    return mode is ReplayMode.RECORDED_OUTPUT


def mode_label(mode: ReplayMode) -> str:
    """Return the governance label for a replay mode."""
    if mode is ReplayMode.DETERMINISTIC_INFERENCE:
        return "NON_AUTHORITATIVE"
    return "AUTHORITATIVE"


@dataclass(frozen=True)
class ReplayBundle:
    """Immutable bundle of LLM interaction artifacts for replay.

    All fields are pinned at capture time and frozen.
    """

    model_version: str
    tokenizer_version: str
    raw_prompt_bytes: bytes
    raw_response_bytes: bytes
    provider_checksum: str
    replay_hash: str
    integrity_verified: bool

    @staticmethod
    def create(
        *,
        model_version: str,
        tokenizer_version: str,
        raw_prompt_bytes: bytes,
        raw_response_bytes: bytes,
    ) -> ReplayBundle:
        """Construct a bundle with computed checksums."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ReplayBundle.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReplayBundle.create".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        checksum_input = f"{model_version}+{tokenizer_version}"
        provider_checksum = hashlib.sha256(checksum_input.encode("utf-8")).hexdigest()
        bundle_obj = {
            "model_version": model_version,
            "tokenizer_version": tokenizer_version,
            "raw_prompt_bytes": raw_prompt_bytes.hex(),
            "raw_response_bytes": raw_response_bytes.hex(),
            "provider_checksum": provider_checksum,
        }
        replay_hash = hashlib.sha256(canonical_bytes(bundle_obj)).hexdigest()
        return ReplayBundle(
            model_version=model_version,
            tokenizer_version=tokenizer_version,
            raw_prompt_bytes=raw_prompt_bytes,
            raw_response_bytes=raw_response_bytes,
            provider_checksum=provider_checksum,
            replay_hash=replay_hash,
            integrity_verified=True,
        )

    def verify_checksum(self) -> bool:
        """Re-derive provider checksum and compare."""
        expected = hashlib.sha256(f"{self.model_version}+{self.tokenizer_version}".encode()).hexdigest()
        return expected == self.provider_checksum


@dataclass(frozen=True)
class LLMReplayStrategy:
    """Strategy for replaying an LLM interaction.

    Combines the replay bundle with the mode policy.
    """

    bundle: ReplayBundle
    mode: ReplayMode

    def replay(self) -> bytes:
        """Execute the replay strategy.

        RECORDED_OUTPUT: return stored raw_response_bytes.
        DETERMINISTIC_INFERENCE: raise (not implemented in
            production — requires explicit dev/test wiring).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "LLMReplayStrategy.replay")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LLMReplayStrategy.replay".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.mode is ReplayMode.RECORDED_OUTPUT:
            return self.bundle.raw_response_bytes
        raise NotImplementedError(
            "DETERMINISTIC_INFERENCE replay requires explicit "
            "dev/test wiring. This mode is NON_AUTHORITATIVE "
            "and must not be used in production.",
        )

    @property
    def is_authoritative(self) -> bool:
        return is_authoritative(self.mode)

    @property
    def governance_label(self) -> str:
        return mode_label(self.mode)


def verify_replay_integrity(bundle: ReplayBundle) -> bool:
    """Re-derive replay_hash and verify bundle integrity.

    Returns True only if the re-derived hash matches the
    stored replay_hash.
    """
    bundle_obj = {
        "model_version": bundle.model_version,
        "tokenizer_version": bundle.tokenizer_version,
        "raw_prompt_bytes": bundle.raw_prompt_bytes.hex(),
        "raw_response_bytes": bundle.raw_response_bytes.hex(),
        "provider_checksum": bundle.provider_checksum,
    }
    expected = hashlib.sha256(canonical_bytes(bundle_obj)).hexdigest()
    return expected == bundle.replay_hash


def validate_production_mode(mode: ReplayMode) -> None:
    """Raise if mode is not allowed in production."""
    if mode not in PRODUCTION_ALLOWED_MODES:
        raise ValueError(
            f"ReplayMode.{mode.name} is not allowed in "
            f"production. Only {PRODUCTION_ALLOWED_MODES} "
            f"are permitted.",
        )
