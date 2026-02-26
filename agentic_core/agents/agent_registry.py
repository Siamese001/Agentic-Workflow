"""Central Agent Registry - Single Source of Truth

Registry of all agents with their 2×2 execution profiles.
"""

import logging

from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort

from .types.agent_execution_profile import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
    compute_registry_digest,
)

logger = logging.getLogger(__name__)


# Compile-time frozen registry - no external data loading
# All agents compiled into code with frozen allowed_models
EXECUTION_PROFILES: dict[str, AgentExecutionProfile] = {
    # High reasoning agents (LLM_API) - GEMINI mandate enforced
    "SovereignLLMGateway": AgentExecutionProfile(
        agent_id="SovereignLLMGateway",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="Primary LLM gateway for high-reasoning tasks",
    ),
    "DispatchOutreachToolsAgent": AgentExecutionProfile(
        agent_id="DispatchOutreachToolsAgent",
        reasoning_intensity=ReasoningIntensity.MEDIUM,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="apps_lic outreach tools dispatcher",
    ),
    "ExecutiveStrategyAgent": AgentExecutionProfile(
        agent_id="ExecutiveStrategyAgent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="Strategic planning and executive decision making",
    ),
    "ResumeAssemblyAgent": AgentExecutionProfile(
        agent_id="ResumeAssemblyAgent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="Resume content generation and assembly",
    ),
    # apps_* agents - LLM_API with frozen models
    "profile_analysis_agent": AgentExecutionProfile(
        agent_id="profile_analysis_agent",
        reasoning_intensity=ReasoningIntensity.MEDIUM,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="Profile analysis and assessment",
    ),
    "research_agent": AgentExecutionProfile(
        agent_id="research_agent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("qwen-vllm", "gemini-2.5-pro"),  # Frozen, includes GEMINI
        notes="Research and information gathering",
    ),
    # Low reasoning agents (DETERMINISTIC) - empty allowed_models
    "ClassificationComplianceHealer": AgentExecutionProfile(
        agent_id="ClassificationComplianceHealer",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),  # Empty for deterministic agents
        notes="Deterministic classification compliance healing",
    ),
    "ValidationOrchestrator": AgentExecutionProfile(
        agent_id="ValidationOrchestrator",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),  # Empty for deterministic agents
        notes="Deterministic validation orchestration",
    ),
    "HybridRetrieverConfig": AgentExecutionProfile(
        agent_id="HybridRetrieverConfig",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),  # Empty for deterministic agents
        notes="Deterministic hybrid retrieval configuration",
    ),
    "UnifiedWorkflowConfig": AgentExecutionProfile(
        agent_id="UnifiedWorkflowConfig",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),  # Empty for deterministic agents
        notes="Deterministic workflow configuration management",
    ),
}


def _validate_registry_sovereignty() -> None:
    """Validate registry invariants at module import time - fail-fast."""
    logger.info("Validating compile-time frozen registry sovereignty...")

    # Verify no duplicate agent IDs
    agent_ids = list(EXECUTION_PROFILES.keys())
    if len(agent_ids) != len(set(agent_ids)):
        raise RuntimeError("Duplicate agent IDs detected in compile-time frozen registry")

    # Validate each profile
    for agent_id, profile in EXECUTION_PROFILES.items():
        if profile.agent_id != agent_id:
            raise RuntimeError(
                f"Profile agent_id '{profile.agent_id}' doesn't match registry key '{agent_id}'"
            )

        # GEMINI mandate for LLM_API agents
        if profile.execution_mode == ExecutionMode.LLM_API:
            if "gemini-2.5-pro" not in profile.allowed_models:
                raise RuntimeError(
                    f"LLM_API agent '{agent_id}' must allow 'gemini-2.5-pro' for retry escalation. "
                    f"Current allowed_models: {profile.allowed_models}"
                )

        # Deterministic agents must have empty allowed_models
        if profile.execution_mode == ExecutionMode.DETERMINISTIC and profile.allowed_models:
            raise RuntimeError(
                f"DETERMINISTIC agent '{agent_id}' must have empty allowed_models. "
                f"Current allowed_models: {profile.allowed_models}"
            )

    # Ensure at least one LLM agent and one deterministic agent
    llm_agents = get_llm_agents()
    deterministic_agents = get_deterministic_agents()

    if not llm_agents:
        raise RuntimeError("Registry must contain at least one LLM_API agent")

    if not deterministic_agents:
        raise RuntimeError("Registry must contain at least one DETERMINISTIC agent")

    logger.info(
        f"Registry sovereignty validated: {len(EXECUTION_PROFILES)} total agents, "
        f"{len(llm_agents)} LLM_API, {len(deterministic_agents)} DETERMINISTIC"
    )


def get_execution_profile(agent_id: str) -> AgentExecutionProfile:
    """Get frozen execution profile - no runtime mutation possible.

    Args:
        agent_id: The agent identifier to look up

    Returns:
        AgentExecutionProfile for the specified agent

    Raises:
        V15HardFailAbort: If agent_id is not found in frozen registry
    """
    profile = EXECUTION_PROFILES.get(agent_id)
    if profile is None:
        raise V15HardFailAbort(
            f"Agent '{agent_id}' not in compile-time frozen registry. "
            f"Available agents: {sorted(EXECUTION_PROFILES.keys())}"
        )

    return profile


# Legacy compatibility - map to new frozen registry
AGENT_REGISTRY = EXECUTION_PROFILES


def get_profile(agent_id: str) -> AgentExecutionProfile:
    """Legacy compatibility wrapper."""
    return get_execution_profile(agent_id)


def registry_digest() -> str:
    """Compute SHA256 digest over canonical JSON of sorted registry.

    Returns:
        SHA256 hash string for determinism verification
    """

    # Convert registry to canonical format
    registry_data = {agent_id: profile.to_dict() for agent_id, profile in sorted(EXECUTION_PROFILES.items())}

    return compute_registry_digest(registry_data)


def get_all_agent_ids() -> tuple[str, ...]:
    """Get all registered agent IDs in deterministic order.

    Returns:
        Tuple of sorted agent IDs
    """
    return tuple(sorted(EXECUTION_PROFILES.keys()))


def get_llm_agents() -> tuple[str, ...]:
    """Get all LLM-capable agent IDs.

    Returns:
        Tuple of agent IDs with LLM_API execution mode
    """
    return tuple(
        agent_id
        for agent_id, profile in sorted(EXECUTION_PROFILES.items())
        if profile.execution_mode == ExecutionMode.LLM_API
    )


def get_deterministic_agents() -> tuple[str, ...]:
    """Get all deterministic agent IDs.

    Returns:
        Tuple of agent IDs with DETERMINISTIC execution mode
    """
    return tuple(
        agent_id
        for agent_id, profile in sorted(EXECUTION_PROFILES.items())
        if profile.execution_mode == ExecutionMode.DETERMINISTIC
    )


# Compile-time validation runs at module import - fail-fast before system boot
_validate_registry_sovereignty()


def validate_registry() -> None:
    """Legacy compatibility - registry already validated at import."""
    # Registry already validated at module import time
    pass


if __name__ == "__main__":
    # Registry validation and info
    print(f"Compile-time Frozen Agent Registry: {len(EXECUTION_PROFILES)} agents")
    print(f"Registry Digest: {registry_digest()}")
    print(f"LLM Agents: {get_llm_agents()}")
    print(f"Deterministic Agents: {get_deterministic_agents()}")

    # Example lookup
    try:
        profile = get_execution_profile("SovereignLLMGateway")
        print(f"\nSovereignLLMGateway Profile: {profile}")
    except Exception as e:  # guardian: allow-silent-swallower
        print(f"Error: {e}")
