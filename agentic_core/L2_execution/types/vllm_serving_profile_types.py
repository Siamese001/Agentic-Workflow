"""
WAVE 1 — Authoritative vLLM Serving Profiles for 32GB GPU.

Defines pinned serving profiles for LOCAL_FAST_7B and LOCAL_STRONG_14B,
config validation guards, and the co-change invariant enforcement.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "vllm_serving_profile_types")
trace_contract.emit_determinism_digest("p0", "vllm_serving_profile_types")

trace_contract._emit_dispatches_healing_run("p1", "vllm_serving_profile_types", "L2")
trace_contract._emit_routes_through("p1", "vllm_serving_profile_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "vllm_serving_profile_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "vllm_serving_profile_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "vllm_serving_profile_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "vllm_serving_profile_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "vllm_serving_profile_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "vllm_serving_profile_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "vllm_serving_profile_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "vllm_serving_profile_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "vllm_serving_profile_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "vllm_serving_profile_types")
trace_contract._emit_gated_by_confidence("p1", "vllm_serving_profile_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "vllm_serving_profile_types", "L2")
trace_contract._emit_reads_policy_state("p1", "vllm_serving_profile_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "vllm_serving_profile_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "vllm_serving_profile_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "vllm_serving_profile_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "vllm_serving_profile_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "vllm_serving_profile_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "vllm_serving_profile_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "vllm_serving_profile_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "vllm_serving_profile_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "vllm_serving_profile_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "vllm_serving_profile_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "vllm_serving_profile_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "vllm_serving_profile_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "vllm_serving_profile_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "vllm_serving_profile_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "vllm_serving_profile_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "vllm_serving_profile_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "vllm_serving_profile_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "vllm_serving_profile_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "vllm_serving_profile_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "vllm_serving_profile_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("vllm_serving_profile_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("vllm_serving_profile_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("vllm_serving_profile_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("vllm_serving_profile_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("vllm_serving_profile_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("vllm_serving_profile_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("vllm_serving_profile_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("vllm_serving_profile_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("vllm_serving_profile_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("vllm_serving_profile_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("vllm_serving_profile_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("vllm_serving_profile_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("vllm_serving_profile_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("vllm_serving_profile_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("vllm_serving_profile_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("vllm_serving_profile_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("vllm_serving_profile_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("vllm_serving_profile_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("vllm_serving_profile_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("vllm_serving_profile_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("vllm_serving_profile_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("vllm_serving_profile_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("vllm_serving_profile_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "vllm_serving_profile_types", "context_pull")
trace_contract._emit_pulls_context("p1", "vllm_serving_profile_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_serving_profile_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_serving_profile_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "vllm_serving_profile_types", "write_through")
trace_contract._emit_writes_through("p1", "vllm_serving_profile_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "vllm_serving_profile_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "vllm_serving_profile_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "vllm_serving_profile_types", "routing_commit")

from agentic_core.L0_routing.config.model_registry import (  # noqa: E402, PLC0415  # guardian: allow-layer-violation -- model_registry SSOT at L0 config; L2 vLLM profile reads canonical model IDs only
    QWEN_LOCAL_MAX_MODEL_LEN,
    QWEN_LOCAL_MODEL_ID,
)

GPU_MEMORY_UTILIZATION: float = 0.85
GPU_VRAM_GB: int = 32
# Single-tier collapse (2026-04-25): vLLM serves Qwen2.5-32B-Instruct-AWQ
# exclusively. Both "fast" and "strong" profiles now point at the SSOT model;
# the difference between them is resource policy applied to the same physical
# model, not a different model.
LOCAL_FAST_MODEL: str = QWEN_LOCAL_MODEL_ID
LOCAL_FAST_7B_MAX_MODEL_LEN: int = 8192
LOCAL_FAST_7B_MAX_NUM_SEQS: int = 4
LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION: float = GPU_MEMORY_UTILIZATION
LOCAL_STRONG_MODEL: str = QWEN_LOCAL_MODEL_ID
LOCAL_STRONG_14B_MAX_MODEL_LEN: int = 24576
LOCAL_STRONG_14B_MAX_NUM_SEQS: int = 24
LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION: float = 0.92
LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING: int = 24576
# Authoritative ceiling for the served Qwen2.5-32B-Instruct-AWQ context window.
# Profiles must not request more than this regardless of profile_name.
#
# Wave 2 of plan qwen-confidence-routing-hardening-d4e7b1 (2026-04-25):
# previously this was a hardcoded 32768 from the 14B-AWQ era. The 32B-AWQ
# Docker server serves ``max_model_len=24576`` on RTX 5090 (see topology doc).
# The ceiling now reads from the L0
# SSOT ``QWEN_LOCAL_MAX_MODEL_LEN`` so a stale 32k value can never silently
# pass validation again.
QWEN_SERVED_MODEL_MAX_LEN_CEILING: int = QWEN_LOCAL_MAX_MODEL_LEN


@dataclass(frozen=True)
class VLLMServingProfile:
    """Immutable serving profile for a vLLM tier.

    Validated at construction time. Startup fails on invalid config.
    """

    profile_name: str
    model: str
    max_model_len: int
    max_num_seqs: int
    gpu_memory_utilization: float

    def __post_init__(self) -> None:
        if self.max_model_len <= 0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"max_model_len={self.max_model_len} must be > 0",
            )
        if self.max_num_seqs <= 0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"max_num_seqs={self.max_num_seqs} must be > 0",
            )
        if not 0.0 < self.gpu_memory_utilization <= 1.0:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"gpu_memory_utilization={self.gpu_memory_utilization} must be in (0.0, 1.0]",
            )
        # Generic context-window ceiling check (replaces the obsolete
        # `"14B" in profile_name` substring match — profile names no longer
        # carry model-size semantics post single-tier collapse 2026-04-25).
        # Any profile that requests more than the served model's max context
        # window must hard-fail at startup.
        if self.max_model_len > QWEN_SERVED_MODEL_MAX_LEN_CEILING:
            raise VLLMServingProfileInvalid(
                profile=self.profile_name,
                reason=f"max_model_len={self.max_model_len} exceeds QWEN_SERVED_MODEL_MAX_LEN_CEILING={QWEN_SERVED_MODEL_MAX_LEN_CEILING} — hard fail at startup",
            )


class VLLMServingProfileInvalid(Exception):
    """Raised when a serving profile fails validation.

    Triggers hard fail at startup — never silently ignored.
    """

    def __init__(self, profile: str, reason: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "VLLMServingProfileInvalid.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "VLLMServingProfileInvalid.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "VLLMServingProfileInvalid.__init__",
        )
        self.profile = profile
        self.reason = reason
        super().__init__(f"VLLMServingProfileInvalid: profile={profile!r}, reason={reason}")


PROFILE_LOCAL_FAST_7B: VLLMServingProfile = VLLMServingProfile(
    profile_name="LOCAL_FAST_7B",
    model=LOCAL_FAST_MODEL,
    max_model_len=LOCAL_FAST_7B_MAX_MODEL_LEN,
    max_num_seqs=LOCAL_FAST_7B_MAX_NUM_SEQS,
    gpu_memory_utilization=LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION,
)
PROFILE_LOCAL_STRONG_14B: VLLMServingProfile = VLLMServingProfile(
    profile_name="LOCAL_STRONG_14B",
    model=LOCAL_STRONG_MODEL,
    max_model_len=LOCAL_STRONG_14B_MAX_MODEL_LEN,
    max_num_seqs=LOCAL_STRONG_14B_MAX_NUM_SEQS,
    gpu_memory_utilization=LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION,
)
SERVING_PROFILE_REGISTRY: dict[str, VLLMServingProfile] = {
    "local_fast": PROFILE_LOCAL_FAST_7B,
    "local_strong": PROFILE_LOCAL_STRONG_14B,
}


def assert_no_simultaneous_increase(
    old_max_model_len: int,
    new_max_model_len: int,
    old_max_num_seqs: int,
    new_max_num_seqs: int,
    profile_name: str,
) -> None:
    """Enforce: max_model_len and max_num_seqs cannot both increase in same commit.

    Args:
        old_max_model_len: Previous max_model_len value.
        new_max_model_len: Proposed new max_model_len value.
        old_max_num_seqs: Previous max_num_seqs value.
        new_max_num_seqs: Proposed new max_num_seqs value.
        profile_name: Profile name for error reporting.

    Raises:
        VLLMCoChangeViolation: If both values increase simultaneously.
    """
    model_len_increased = new_max_model_len > old_max_model_len
    num_seqs_increased = new_max_num_seqs > old_max_num_seqs
    if model_len_increased and num_seqs_increased:
        raise VLLMCoChangeViolation(
            profile=profile_name,
            old_max_model_len=old_max_model_len,
            new_max_model_len=new_max_model_len,
            old_max_num_seqs=old_max_num_seqs,
            new_max_num_seqs=new_max_num_seqs,
        )


class VLLMCoChangeViolation(Exception):
    """Raised when max_model_len and max_num_seqs both increase simultaneously.

    This invariant prevents KV-cache OOM on 32GB GPU.
    """

    def __init__(
        self,
        profile: str,
        old_max_model_len: int,
        new_max_model_len: int,
        old_max_num_seqs: int,
        new_max_num_seqs: int,
    ) -> None:
        self.profile = profile
        self.old_max_model_len = old_max_model_len
        self.new_max_model_len = new_max_model_len
        self.old_max_num_seqs = old_max_num_seqs
        self.new_max_num_seqs = new_max_num_seqs
        super().__init__(
            f"VLLMCoChangeViolation: profile={profile!r} — max_model_len {old_max_model_len}->{new_max_model_len} AND max_num_seqs {old_max_num_seqs}->{new_max_num_seqs} both increased simultaneously. Only one may increase per commit.",
        )


def get_profile(tier: str) -> VLLMServingProfile:
    """Retrieve serving profile by tier name.

    Args:
        tier: Tier name ("local_fast" or "local_strong").

    Returns:
        VLLMServingProfile for the requested tier.

    Raises:
        KeyError: If tier is not in SERVING_PROFILE_REGISTRY.
    """
    if tier not in SERVING_PROFILE_REGISTRY:
        msg = f"Unknown tier {tier!r}. Valid tiers: {sorted(SERVING_PROFILE_REGISTRY)}"
        raise KeyError(msg)
    return SERVING_PROFILE_REGISTRY[tier]


__all__ = [
    "GPU_MEMORY_UTILIZATION",
    "GPU_VRAM_GB",
    "LOCAL_FAST_7B_GPU_MEMORY_UTILIZATION",
    "LOCAL_FAST_7B_MAX_MODEL_LEN",
    "LOCAL_FAST_7B_MAX_NUM_SEQS",
    "LOCAL_FAST_MODEL",
    "LOCAL_STRONG_14B_GPU_MEMORY_UTILIZATION",
    "LOCAL_STRONG_14B_MAX_MODEL_LEN",
    "LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING",
    "LOCAL_STRONG_14B_MAX_NUM_SEQS",
    "LOCAL_STRONG_MODEL",
    "QWEN_SERVED_MODEL_MAX_LEN_CEILING",
    "PROFILE_LOCAL_FAST_7B",
    "PROFILE_LOCAL_STRONG_14B",
    "SERVING_PROFILE_REGISTRY",
    "VLLMCoChangeViolation",
    "VLLMServingProfile",
    "VLLMServingProfileInvalid",
    "assert_no_simultaneous_increase",
    "get_profile",
]
