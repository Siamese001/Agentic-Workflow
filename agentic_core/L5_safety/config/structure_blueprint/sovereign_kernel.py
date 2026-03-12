"""Sovereign Kernel Manifest — Immutable Core Components.

Declares the minimal sovereign kernel that cannot be removed or bypassed
without compromising system integrity. Extensions (meta-learning, DPO,
pattern engines) must not create reverse dependencies into kernel internals.

Invariant: Failure of any extension must not affect kernel operation.
"""
from __future__ import annotations
from typing import FrozenSet
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
SOVEREIGN_KERNEL_COMPONENTS: frozenset[str] = frozenset({'agentic_core.L0_routing', 'agentic_core.L5_safety', 'agentic_core.L2_execution', 'agentic_core.determinism', 'agentic_core.replay', 'agentic_core.agents.agent_registry', 'agentic_core.L2_execution.enforcement.SovereignLLMGateway', 'agentic_core.interfaces', 'agentic_core.embeddings', 'agentic_core.runtime', 'agentic_core.prompt_governance', 'agentic_core.core', 'agentic_core.L5_safety.validators.base_detector_validator', 'agentic_core.mixins', 'agentic_core.utils', 'agentic_core.semantic_memory', 'agentic_core.L1_cognition', 'agentic_core.L3_orchestration', 'agentic_core.L4_state', 'agentic_core.config', 'agentic_core.patterns', 'agentic_core.base_agents'})
MODULAR_EXTENSIONS: frozenset[str] = frozenset({'system_learning', 'system_learning.pipelines.meta_learning_pipeline', 'system_learning.engines.healing_outcome_aggregator', 'system_learning.engines.pattern_analysis_engine', 'system_learning.engines.healing_config_optimizer', 'system_learning.engines.code_quality_signal_engine', 'system_learning.engines.classification_feedback_engine', 'system_learning.engines.entropy_telemetry_engine', 'system_learning.engines.surface_isolation_validator', 'system_learning.engines.change_package_impl', 'system_learning.engines.rlhf_optimizer', 'system_learning.engines.policy_recommendation_engine', 'agentic_core.rag', 'agentic_core.context', 'agentic_core.L0_routing.seams.c0_context_retriever', 'agentic_core.L2_execution.healers.healing_tier_config', 'agentic_core.L2_execution.healers.healing_tier_dispatcher', 'agentic_core.monitoring', 'agentic_core.telemetry'})

def is_kernel_component(module_path: str) -> bool:
    """Check if a given module path is part of the sovereign kernel."""
    normalized = module_path.replace('/', '.').replace('\\', '.')
    for kernel_path in SOVEREIGN_KERNEL_COMPONENTS:
        if normalized == kernel_path or normalized.startswith(kernel_path + '.'):
            return True
    return False

def is_modular_extension(module_path: str) -> bool:
    """Check if a given module path is a modular extension."""
    normalized = module_path.replace('/', '.').replace('\\', '.')
    for ext_path in MODULAR_EXTENSIONS:
        if normalized == ext_path or normalized.startswith(ext_path + '.'):
            return True
    return False

def validate_boundary(module_path: str) -> tuple[bool, str]:
    """Validate that a module respects kernel/extension boundary.

    Returns:
        (is_valid, reason) tuple
    """
    if is_kernel_component(module_path):
        return (True, 'kernel_component')
    if is_modular_extension(module_path):
        return (True, 'modular_extension')
    return (False, f'unclassified_module: {module_path}')
__all__ = ['SOVEREIGN_KERNEL_COMPONENTS', 'MODULAR_EXTENSIONS', 'is_kernel_component', 'is_modular_extension', 'validate_boundary']
