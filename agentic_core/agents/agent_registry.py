"""Agent Registry - Single Source of Truth for Agent Execution Profiles."""

from agentic_core.agents.types.agent_execution_profile import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
)

AGENT_REGISTRY: dict[str, AgentExecutionProfile] = {
    "reconciler": AgentExecutionProfile(
        agent_id="reconciler",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "location": AgentExecutionProfile(
        agent_id="location",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "hierarchy": AgentExecutionProfile(
        agent_id="hierarchy",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "arch_governor": AgentExecutionProfile(
        agent_id="arch_governor",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "gravity_repair": AgentExecutionProfile(
        agent_id="gravity_repair",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "system_architect": AgentExecutionProfile(
        agent_id="system_architect",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "file_classification": AgentExecutionProfile(
        agent_id="file_classification",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "root_hygiene": AgentExecutionProfile(
        agent_id="root_hygiene",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "conversational_repair": AgentExecutionProfile(
        agent_id="conversational_repair",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "gpt-3.5-turbo", "claude-3-opus"),
    ),
    "cognitive_disposition": AgentExecutionProfile(
        agent_id="cognitive_disposition",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "claude-3-opus"),
    ),
}


def get_execution_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID (canonical name for L2 dispatcher)."""
    return get_profile(agent_id)


def get_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID."""
    try:
        return AGENT_REGISTRY[agent_id]
    except KeyError as exc:
        raise KeyError(
            f"Agent '{agent_id}' not found in registry. Available: {list(AGENT_REGISTRY.keys())}"
        ) from exc


def registry_digest() -> dict[str, str]:
    """Generate a digest of the agent registry for validation."""
    return {
        agent_id: f"{p.agent_id}:{p.reasoning_intensity.value}:{p.execution_mode.value}"
        for agent_id, p in AGENT_REGISTRY.items()
    }
