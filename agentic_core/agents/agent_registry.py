"""Agent Registry - Single Source of Truth for Agent Execution Profiles.

Provides centralized agent profile registry with reasoning intensity and execution mode
classifications for all agents in the system.
"""

from agentic_core.agents.types.agent_execution_profile import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
)

# Central registry of all agent execution profiles
AGENT_REGISTRY: dict[str, AgentExecutionProfile] = {
    # Core SSOT agents (deterministic)
    "reconciler": AgentExecutionProfile(
        agent_id="reconciler",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "location": AgentExecutionProfile(
        agent_id="location",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "hierarchy": AgentExecutionProfile(
        agent_id="hierarchy",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "arch_governor": AgentExecutionProfile(
        agent_id="arch_governor",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "gravity_repair": AgentExecutionProfile(
        agent_id="gravity_repair",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "system_architect": AgentExecutionProfile(
        agent_id="system_architect",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "file_classification": AgentExecutionProfile(
        agent_id="file_classification",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    "root_hygiene": AgentExecutionProfile(
        agent_id="root_hygiene",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
    ),
    # LLM-powered agents (API-based)
    "conversational_repair": AgentExecutionProfile(
        agent_id="conversational_repair",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
    ),
    "cognitive_disposition": AgentExecutionProfile(
        agent_id="cognitive_disposition",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
    ),
}


def get_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID.

    Args:
        agent_id: The unique agent identifier

    Returns:
        AgentExecutionProfile for the specified agent

    Raises:
        KeyError: If agent_id is not found in the registry
    """
    try:
        return AGENT_REGISTRY[agent_id]
    except KeyError as exc:
        raise KeyError(
            f"Agent '{agent_id}' not found in registry. Available agents: {list(AGENT_REGISTRY.keys())}"
        ) from exc


def registry_digest() -> dict[str, str]:
    """Generate a digest of the agent registry for validation.

    Returns:
        Dictionary mapping agent_id to their profile signature
    """
    digest = {}
    for agent_id, profile in AGENT_REGISTRY.items():
        # Create a deterministic signature for each profile
        profile_str = f"{profile.agent_id}:{profile.reasoning_intensity.value}:{profile.execution_mode.value}"
        digest[agent_id] = profile_str
    return digest
