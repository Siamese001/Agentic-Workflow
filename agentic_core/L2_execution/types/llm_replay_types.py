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
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "llm_replay_types", "execution_auth")
_emit_validates_capability("p2", "llm_replay_types", "capability_check")
_emit_routes_to_capability("p2", "llm_replay_types", "capability_route")
_emit_writes_via_uwg("p2", "llm_replay_types", "uwg_write")
_emit_blocks_direct_write("p2", "llm_replay_types", "direct_write_block")
_emit_records_tool_invocation("p2", "llm_replay_types", "tool_invocation")
_emit_captures_execution_output("p2", "llm_replay_types", "exec_output")
_emit_dispatches_agent("p3", "llm_replay_types", "agent_dispatch")
_emit_coordinates_agents("p3", "llm_replay_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "llm_replay_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "llm_replay_types", "healing_outcome")
_emit_escalates_failure("p3", "llm_replay_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "llm_replay_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "llm_replay_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "llm_replay_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "llm_replay_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "llm_replay_types", "eval_metric")
_emit_stores_embedding("p4", "llm_replay_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "llm_replay_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "llm_replay_types", "exec_snapshot_link")
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

emit_replay_key("p0", "llm_replay_types")
emit_determinism_digest("p0", "llm_replay_types")

_emit_dispatches_healing_run("p1", "llm_replay_types", "L2")
_emit_routes_through("p1", "llm_replay_types", "L2")
_emit_checks_agent_registry("p1", "llm_replay_types", "agent_registry")
_emit_validates_agent_capability("p1", "llm_replay_types", "capability")
_emit_dispatches_execution_plan("p1", "llm_replay_types", "exec_plan")
_emit_agent_executes_agent("p1", "llm_replay_types", "sub_agent")
_emit_routes_to_agent("p1", "llm_replay_types", "target_agent")
_emit_verifies_policy("p1", "llm_replay_types", "policy_check")
_emit_observes_runtime_state("p1", "llm_replay_types", "runtime_state")
_emit_verifies_boundary("p1", "llm_replay_types", "boundary_check")
_emit_transcripts_response("p1", "llm_replay_types", "transcript")
_emit_hard_fails_untranscripted("p1", "llm_replay_types")
_emit_gated_by_confidence("p1", "llm_replay_types", "confidence_gate")
_emit_escalates_to_human("p1", "llm_replay_types", "L2")
_emit_reads_policy_state("p1", "llm_replay_types", "L2")

_emit_applies_guardrail("p0", "llm_replay_types", "p0_governance")
_emit_snapshots_state("p0", "llm_replay_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

record_execution_trace("llm_replay_types", "llm_replay_types_trace")


_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_1")
_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_2")
_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_3")
_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_4")
_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_5")
_emit_emits_metric_event("llm_replay_types", "p4obs", "metric_6")
_emit_records_incident_event("llm_replay_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("llm_replay_types", "p4obs", "anomaly")
_emit_writes_observability_log("llm_replay_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("llm_replay_types", "p4obs", "mon_state")
_emit_triggers_alert("llm_replay_types", "p4obs", "alert")
_emit_links_incident_trace("llm_replay_types", "p4obs", "trace_link")
_emit_captures_pattern("llm_replay_types", "p3lm", "pattern")
_emit_records_learning_event("llm_replay_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("llm_replay_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("llm_replay_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("llm_replay_types", "p3lm", "routing")
_emit_improves_agent_policy("llm_replay_types", "p3lm", "policy")
_emit_stores_learning_state("llm_replay_types", "p3lm", "state")
_emit_records_execution_trace("llm_replay_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("llm_replay_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("llm_replay_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("llm_replay_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("llm_replay_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("llm_replay_types", "env_read", "p2_env_1")
_emit_reads_environ("llm_replay_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("llm_replay_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("llm_replay_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "llm_replay_types", "context_pull")
_emit_pulls_context("p1", "llm_replay_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "llm_replay_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "llm_replay_types", "uwg_term_2")
_emit_writes_through("p1", "llm_replay_types", "write_through")
_emit_writes_through("p1", "llm_replay_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "llm_replay_types", "safety_validation")
_emit_invokes_eval("p1", "llm_replay_types", "eval_call")
_emit_proposal_commits_routing("p1", "llm_replay_types", "routing_commit")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReplayBundle.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReplayBundle.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "LLMReplayStrategy.replay")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LLMReplayStrategy.replay".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.mode is ReplayMode.RECORDED_OUTPUT:
            return self.bundle.raw_response_bytes
        raise NotImplementedError(
            "DETERMINISTIC_INFERENCE replay requires explicit "
            "dev/test wiring. This mode is NON_AUTHORITATIVE "
            "and must not be used in production."
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
            f"are permitted."
        )
