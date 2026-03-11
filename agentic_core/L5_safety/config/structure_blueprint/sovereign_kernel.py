"""Sovereign Kernel Manifest — Immutable Core Components.

Declares the minimal sovereign kernel that cannot be removed or bypassed
without compromising system integrity. Extensions (meta-learning, DPO,
pattern engines) must not create reverse dependencies into kernel internals.

Invariant: Failure of any extension must not affect kernel operation.
"""

from __future__ import annotations

from typing import FrozenSet


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Sovereign Kernel Components (immutable, non-removable)
# ---------------------------------------------------------------------------
SOVEREIGN_KERNEL_COMPONENTS: frozenset[str] = frozenset({
    # L0 Routing — route only, no mutation authority
    "agentic_core.L0_routing",
    # L5 Safety — certify only, no write authority
    "agentic_core.L5_safety",
    # L2 Execution Core + Universal Write Gateway — only mutation chokepoint
    "agentic_core.L2_execution",
    # Determinism + Replay Core
    "agentic_core.determinism",
    "agentic_core.replay",
    # AgentExecutionProfileRegistry (LOW/HIGH enforcement)
    "agentic_core.agents.agent_registry",
    # SovereignLLMGateway (sole LLM egress seam)
    "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
    # Interfaces (kernel contracts)
    "agentic_core.interfaces",
    # Embeddings (kernel infrastructure)
    "agentic_core.embeddings",
    # Runtime components (kernel infrastructure)
    "agentic_core.runtime",
    # Prompt governance (kernel security)
    "agentic_core.prompt_governance",
    # Core classification kernel
    "agentic_core.core",
    # Validators base (kernel infrastructure)
    "agentic_core.L5_safety.validators.base_detector_validator",
    # Mixins (kernel infrastructure)
    "agentic_core.mixins",
    # Utils (kernel infrastructure)
    "agentic_core.utils",
    # Semantic memory (kernel infrastructure)
    "agentic_core.semantic_memory",
    # L1 Cognition (kernel infrastructure)
    "agentic_core.L1_cognition",
    # L3 Orchestration (kernel infrastructure)
    "agentic_core.L3_orchestration",
    # L4 State (kernel infrastructure)
    "agentic_core.L4_state",
    # Config (kernel infrastructure)
    "agentic_core.config",
    # Patterns (kernel infrastructure)
    "agentic_core.patterns",
    # Base agents (kernel infrastructure)
    "agentic_core.base_agents",
})


# ---------------------------------------------------------------------------
# Modular Extensions (removable without breaking kernel guarantees)
# ---------------------------------------------------------------------------
MODULAR_EXTENSIONS: frozenset[str] = frozenset({
    # All system_learning modules are extensions
    "system_learning",
    # Meta-learning pipeline and engines (explicitly listed for clarity)
    "system_learning.pipelines.meta_learning_pipeline",
    "system_learning.engines.healing_outcome_aggregator",
    "system_learning.engines.pattern_analysis_engine",
    "system_learning.engines.healing_config_optimizer",
    "system_learning.engines.code_quality_signal_engine",
    "system_learning.engines.classification_feedback_engine",
    "system_learning.engines.entropy_telemetry_engine",
    "system_learning.engines.surface_isolation_validator",
    "system_learning.engines.change_package_impl",
    # DPO and policy recommendation
    "system_learning.engines.rlhf_optimizer",
    "system_learning.engines.policy_recommendation_engine",
    # RAG and context systems
    "agentic_core.rag",
    "agentic_core.context",
    # C0 context (informational only)
    "agentic_core.L0_routing.seams.c0_context_retriever",
    # Healing tier router components (router itself is kernel via L2_execution)
    "agentic_core.L2_execution.healers.healing_tier_config",
    "agentic_core.L2_execution.healers.healing_tier_dispatcher",
    # Monitoring and telemetry (non-authoritative)
    "agentic_core.monitoring",
    "agentic_core.telemetry",
})


def is_kernel_component(module_path: str) -> bool:
    """Check if a given module path is part of the sovereign kernel."""
    # Normalize path separators for cross-platform consistency
    normalized = module_path.replace("/", ".").replace("\\", ".")
    # Check for exact match or prefix match for submodules
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
        return True, "kernel_component"
    if is_modular_extension(module_path):
        return True, "modular_extension"
    return False, f"unclassified_module: {module_path}"


__all__ = [
    "SOVEREIGN_KERNEL_COMPONENTS",
    "MODULAR_EXTENSIONS",
    "is_kernel_component",
    "is_modular_extension",
    "validate_boundary",
]
