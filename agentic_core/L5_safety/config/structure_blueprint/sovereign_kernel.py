"""Sovereign Kernel Manifest — Immutable Core Components.

Declares the minimal sovereign kernel that cannot be removed or bypassed
without compromising system integrity. Extensions (meta-learning, DPO,
pattern engines) must not create reverse dependencies into kernel internals.

Invariant: Failure of any extension must not affect kernel operation.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_kernel")
emit_determinism_digest("p0", "sovereign_kernel")

_emit_dispatches_healing_run("p1", "sovereign_kernel", "L5")
_emit_routes_through("p1", "sovereign_kernel", "L5")
_emit_escalates_to_human("p1", "sovereign_kernel", "L5")
_emit_reads_policy_state("p1", "sovereign_kernel", "L5")

SOVEREIGN_KERNEL_COMPONENTS: frozenset[str] = frozenset(
    {
        "agentic_core.L0_routing",
        "agentic_core.L5_safety",
        "agentic_core.L2_execution",
        "agentic_core.determinism",
        "agentic_core.replay",
        "agentic_core.agents.agent_registry",
        "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
        "agentic_core.interfaces",
        "agentic_core.embeddings",
        "agentic_core.runtime",
        "agentic_core.prompt_governance",
        "agentic_core.core",
        "agentic_core.L5_safety.validators.base_detector_validator",
        "agentic_core.mixins",
        "agentic_core.utils",
        "agentic_core.semantic_memory",
        "agentic_core.L1_cognition",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.config",
        "agentic_core.patterns",
        "agentic_core.base_agents",
    }
)
MODULAR_EXTENSIONS: frozenset[str] = frozenset(
    {
        "system_learning",
        "system_learning.pipelines.meta_learning_pipeline",
        "system_learning.engines.healing_outcome_aggregator",
        "system_learning.engines.pattern_analysis_engine",
        "system_learning.engines.healing_config_optimizer",
        "system_learning.engines.code_quality_signal_engine",
        "system_learning.engines.classification_feedback_engine",
        "system_learning.engines.entropy_telemetry_engine",
        "system_learning.engines.surface_isolation_validator",
        "system_learning.engines.change_package_impl",
        "system_learning.engines.rlhf_optimizer",
        "system_learning.engines.policy_recommendation_engine",
        "agentic_core.rag",
        "agentic_core.context",
        "agentic_core.L0_routing.seams.c0_context_retriever",
        "agentic_core.L2_execution.healers.healing_tier_config",
        "agentic_core.L2_execution.healers.healing_tier_dispatcher",
        "agentic_core.monitoring",
        "agentic_core.telemetry",
    }
)


def is_kernel_component(module_path: str) -> bool:
    """Check if a given module path is part of the sovereign kernel."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_kernel_component", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_kernel_component", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "is_kernel_component")
    normalized = module_path.replace("/", ".").replace("\\", ".")
    for kernel_path in SOVEREIGN_KERNEL_COMPONENTS:
        if normalized == kernel_path or normalized.startswith(kernel_path + "."):
            return True
    return False


def is_modular_extension(module_path: str) -> bool:
    """Check if a given module path is a modular extension."""
    normalized = module_path.replace("/", ".").replace("\\", ".")
    for ext_path in MODULAR_EXTENSIONS:
        if normalized == ext_path or normalized.startswith(ext_path + "."):
            return True
    return False


def validate_boundary(module_path: str) -> tuple[bool, str]:
    """Validate that a module respects kernel/extension boundary.

    Returns:
        (is_valid, reason) tuple
    """
    if is_kernel_component(module_path):
        return (True, "kernel_component")
    if is_modular_extension(module_path):
        return (True, "modular_extension")
    return (False, f"unclassified_module: {module_path}")


__all__ = [
    "SOVEREIGN_KERNEL_COMPONENTS",
    "MODULAR_EXTENSIONS",
    "is_kernel_component",
    "is_modular_extension",
    "validate_boundary",
]
