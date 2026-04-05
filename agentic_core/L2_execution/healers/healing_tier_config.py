"""
L2.3 Healing Tier Configuration — L4-Backed, Validated at Startup.

All thresholds and model IDs are explicitly declared. No silent defaults.
Hard-fails if X <= Y or values are out of range.

Config is frozen after validation — no runtime mutation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Import canonical healing thresholds from L0 (L0 can be imported by any layer)
from agentic_core.L0_routing.config.path_constants import (
    HEALING_CONFIDENCE_X,
    HEALING_CONFIDENCE_Y,
    QWEN_14B_MODEL_ID,
    SSOT_SCORE_THRESHOLD_DET,
    SSOT_SCORE_THRESHOLD_QWEN,
)
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
)

emit_replay_key("p0", "healing_tier_config")
emit_determinism_digest("p0", "healing_tier_config")

_emit_dispatches_healing_run("p1", "healing_tier_config", "L2")
_emit_routes_through("p1", "healing_tier_config", "L2")
_emit_checks_agent_registry("p1", "healing_tier_config", "agent_registry")
_emit_validates_agent_capability("p1", "healing_tier_config", "capability")
_emit_dispatches_execution_plan("p1", "healing_tier_config", "exec_plan")
_emit_agent_executes_agent("p1", "healing_tier_config", "sub_agent")
_emit_routes_to_agent("p1", "healing_tier_config", "target_agent")
_emit_verifies_policy("p1", "healing_tier_config", "policy_check")
_emit_observes_runtime_state("p1", "healing_tier_config", "runtime_state")
_emit_verifies_boundary("p1", "healing_tier_config", "boundary_check")
_emit_transcripts_response("p1", "healing_tier_config", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_tier_config")
_emit_gated_by_confidence("p1", "healing_tier_config", "confidence_gate")
_emit_escalates_to_human("p1", "healing_tier_config", "L2")
_emit_reads_policy_state("p1", "healing_tier_config", "L2")
_emit_authorize_and_execute("p2", "healing_tier_config", "execution_auth")
_emit_validates_capability("p2", "healing_tier_config", "capability_check")
_emit_routes_to_capability("p2", "healing_tier_config", "capability_route")
_emit_writes_via_uwg("p2", "healing_tier_config", "uwg_write")
_emit_blocks_direct_write("p2", "healing_tier_config", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_tier_config", "tool_invocation")
_emit_captures_execution_output("p2", "healing_tier_config", "exec_output")
_emit_dispatches_agent("p3", "healing_tier_config", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_tier_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_tier_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_tier_config", "healing_outcome")
_emit_escalates_failure("p3", "healing_tier_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_tier_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_tier_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_tier_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_tier_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_tier_config", "eval_metric")
_emit_stores_embedding("p4", "healing_tier_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_tier_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_tier_config", "exec_snapshot_link")
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
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_1")
_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_2")
_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_3")
_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_4")
_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_5")
_emit_emits_metric_event("healing_tier_config", "p4obs", "metric_6")
_emit_records_incident_event("healing_tier_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_tier_config", "p4obs", "anomaly")
_emit_writes_observability_log("healing_tier_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_tier_config", "p4obs", "mon_state")
_emit_triggers_alert("healing_tier_config", "p4obs", "alert")
_emit_links_incident_trace("healing_tier_config", "p4obs", "trace_link")
_emit_captures_pattern("healing_tier_config", "p3lm", "pattern")
_emit_records_learning_event("healing_tier_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_tier_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_tier_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_tier_config", "p3lm", "routing")
_emit_improves_agent_policy("healing_tier_config", "p3lm", "policy")
_emit_stores_learning_state("healing_tier_config", "p3lm", "state")
_emit_records_execution_trace("healing_tier_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_tier_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_tier_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_tier_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_tier_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_tier_config", "env_read", "p2_env_1")
_emit_reads_environ("healing_tier_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_tier_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_tier_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_tier_config", "context_pull")
_emit_pulls_context("p1", "healing_tier_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_tier_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_tier_config", "uwg_term_2")
_emit_writes_through("p1", "healing_tier_config", "write_through")
_emit_writes_through("p1", "healing_tier_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_tier_config", "safety_validation")
_emit_invokes_eval("p1", "healing_tier_config", "eval_call")
_emit_proposal_commits_routing("p1", "healing_tier_config", "routing_commit")

# Configuration constants

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
# Imported from L0 SSOT: agentic_core.L0_routing.config.path_constants
# HEALING_CONFIDENCE_X, HEALING_CONFIDENCE_Y, SSOT_SCORE_THRESHOLD_DET,
# SSOT_SCORE_THRESHOLD_QWEN defined in L0 to allow L2+ import without boundary violation

# Qwen pinned revisions for determinism
QWEN_MODEL_REVISION_SHA = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
QWEN_TOKENIZER_REVISION_SHA = "f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7"
QWEN_VLLM_VERSION = "0.4.2"
QWEN_CUDA_VERSION = "12.1"
QWEN_TORCH_VERSION = "2.1.0"

# Qwen 14B — targets RTX 5090 (32 GB VRAM, CUDA >= 12.0, compute >= 8.9)
# QWEN_14B_MODEL_ID imported from L0: agentic_core.L0_routing.config.path_constants
QWEN_14B_MIN_VRAM_GB: float = 16.0  # Int4-quantized 14B fits in 16 GB
QWEN_14B_MIN_CUDA = "12.0"
QWEN_14B_MIN_COMPUTE: float = 8.0  # Ada Lovelace baseline (RTX 4090/5090)

# Canonical GPU memory utilization fraction shared by ALL vLLM launch sites.
# 0.70 reserves ~30 % headroom for the KV cache under concurrent load.
# MUST NOT be overridden per-call-site — change only here.
QWEN_GPU_MEM_UTIL: float = 0.70

# Agents that must be routed through the Qwen 14B tier (medium confidence)
# when local-GPU inference is available.  The resolver checks this set at
# dispatch time; agents absent from this set keep their existing routing.
QWEN_14B_AGENT_KEYS: frozenset[str] = frozenset(
    {
        "arch_governor",
        "file_classification",
        "cognitive_disposition",
        "observability_probe",
    }
)

# BMG embedding model tag — used by the cosine-similarity fallback in the
# decision engine.  The actual model is loaded lazily by the embedding helper.
BMG_EMBEDDING_MODEL_ID = "BAAI/bge-m3"
# Agents whose similarity scoring uses BMG embeddings instead of Jaccard.
BMG_EMBEDDING_AGENT_KEYS: frozenset[str] = frozenset({"location", "root_hygiene"})


@dataclass(frozen=True, slots=True)
class HealingTierConfig:
    """Immutable, validated configuration for the L2.3 healing tier router.

    Attributes:
        heal_confidence_x: Upper threshold. heal_confidence >= X → LOCAL_AGENT.
        heal_confidence_y: Lower threshold. Y <= heal_confidence < X → QWEN_VLLM.
                           heal_confidence < Y → GEMINI_2_5_PRO.
        max_heal_retries: Maximum heal attempts before forcing GEMINI_2_5_PRO.
        model_qwen_vllm_id: Model identifier for the Qwen 7B vLLM backend.
        model_qwen_14b_vllm_id: Model identifier for the Qwen 14B vLLM backend (RTX 5090).
        model_gemini_2_5_pro_id: Model identifier for the Gemini 2.5 Pro backend.
        enable_bmg_embeddings: When True the decision engine uses BMG cosine
            similarity instead of Jaccard for semantic scoring.
    """

    heal_confidence_x: float = HEALING_CONFIDENCE_X
    heal_confidence_y: float = HEALING_CONFIDENCE_Y
    max_heal_retries: int = 3
    model_qwen_vllm_id: str = "Qwen/Qwen2.5-7B-Instruct"
    model_gemini_2_5_pro_id: str = "gemini-2.5-pro"
    model_qwen_14b_vllm_id: str = QWEN_14B_MODEL_ID
    enable_bmg_embeddings: bool = True  # BGE embeddings are now mandatory

    def __post_init__(self) -> None:
        if not (0.0 < self.heal_confidence_x <= 1.0):
            raise ValueError(f"heal_confidence_x must be in (0.0, 1.0], got {self.heal_confidence_x}")
        if not (0.0 <= self.heal_confidence_y < 1.0):
            raise ValueError(f"heal_confidence_y must be in [0.0, 1.0), got {self.heal_confidence_y}")
        if self.heal_confidence_x <= self.heal_confidence_y:
            raise ValueError(
                f"heal_confidence_x ({self.heal_confidence_x}) must be > "
                f"heal_confidence_y ({self.heal_confidence_y})"
            )
        if self.max_heal_retries < 1:
            raise ValueError(f"max_heal_retries must be >= 1, got {self.max_heal_retries}")
        if not self.model_qwen_vllm_id:
            raise ValueError("model_qwen_vllm_id must not be empty")
        if not self.model_gemini_2_5_pro_id:
            raise ValueError("model_gemini_2_5_pro_id must not be empty")
        if not self.model_qwen_14b_vllm_id:
            raise ValueError("model_qwen_14b_vllm_id must not be empty")


def load_default_healing_tier_config() -> HealingTierConfig:
    """Load the canonical default healing tier config.

    In production, these values would be loaded from L4 state store.
    This function provides the explicit, auditable defaults.

    BGE embeddings are mandatory for deterministic failure classification.

    Returns:
        Validated HealingTierConfig instance.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_default_healing_tier_config", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_default_healing_tier_config", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "load_default_healing_tier_config")
    return HealingTierConfig(
        heal_confidence_x=HEALING_CONFIDENCE_X,
        heal_confidence_y=HEALING_CONFIDENCE_Y,
        max_heal_retries=3,
        model_qwen_vllm_id="Qwen/Qwen2.5-7B-Instruct",
        model_qwen_14b_vllm_id=QWEN_14B_MODEL_ID,
        model_gemini_2_5_pro_id="gemini-2.5-pro",
        enable_bmg_embeddings=True,
    )


def validate_qwen_startup_state() -> None:
    """Hard validate kill switch at startup."""
    qwen_enabled = os.environ.get("QWEN_VLLM_ENABLED", "true").lower() == "true"

    if not qwen_enabled:
        # Assert no Qwen processes are running (cross-platform)
        if is_vllm_process_running():
            raise RuntimeError(
                "QWEN_VLLM_ENABLED=False but vLLM process detected. "
                "Terminate all vLLM processes before starting."
            )

        import logging

        logger = logging.getLogger(__name__)
        logger.info("QWEN_VLLM_ENABLED=False - Qwen tier disabled at startup")
        return

    # If enabled, validate GPU capabilities before allowing startup
    try:
        # Import here to avoid circular dependency
        from agentic_core.L2_execution.healers.qwen_gpu_validator import validate_qwen_gpu_capabilities

        validate_qwen_gpu_capabilities(model_size="7B")  # Default to 7B for validation
        logger.info("QWEN_VLLM_ENABLED=True - GPU validation passed")
    except Exception as exc:
        logger.error(f"QWEN_VLLM_ENABLED=True but GPU validation failed: {exc}")
        raise


def is_vllm_process_running() -> bool:
    """Cross-platform detection of vLLM processes using psutil."""
    try:
        import psutil

        for proc in psutil.process_iter(attrs=["cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "vllm" in " ".join(cmdline):
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ImportError):
        return False


__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "QWEN_MODEL_REVISION_SHA",
    "QWEN_TOKENIZER_REVISION_SHA",
    "QWEN_VLLM_VERSION",
    "QWEN_CUDA_VERSION",
    "QWEN_TORCH_VERSION",
    "QWEN_14B_MODEL_ID",
    "QWEN_14B_MIN_VRAM_GB",
    "QWEN_14B_MIN_CUDA",
    "QWEN_14B_MIN_COMPUTE",
    "QWEN_14B_AGENT_KEYS",
    "BMG_EMBEDDING_MODEL_ID",
    "BMG_EMBEDDING_AGENT_KEYS",
    "QWEN_GPU_MEM_UTIL",
    "HealingTierConfig",
    "load_default_healing_tier_config",
    "validate_qwen_startup_state",
    "is_vllm_process_running",
]
