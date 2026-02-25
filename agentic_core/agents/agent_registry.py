"""Central Agent Registry - Single Source of Truth

Registry of all agents with their 2×2 execution profiles.
"""

from typing import Dict
import json
import hashlib

from .types.agent_execution_profile import (
    AgentExecutionProfile,
    ReasoningIntensity,
    ExecutionMode,
    compute_registry_digest
)


# Central registry - single source of truth
# Deterministic ordering: sorted by agent_id for any serialization
AGENT_REGISTRY: Dict[str, AgentExecutionProfile] = {
    # High reasoning agents (LLM_API)
    "SovereignLLMGateway": AgentExecutionProfile(
        agent_id="SovereignLLMGateway",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "gemini-pro"),
        notes="Primary LLM gateway for high-reasoning tasks"
    ),
    
    "ExecutiveStrategyAgent": AgentExecutionProfile(
        agent_id="ExecutiveStrategyAgent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "claude-3-sonnet"),
        notes="Strategic planning and executive decision making"
    ),
    
    "ResumeAssemblyAgent": AgentExecutionProfile(
        agent_id="ResumeAssemblyAgent",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "gpt-3.5-turbo"),
        notes="Resume content generation and assembly"
    ),
    
    # Low reasoning agents (DETERMINISTIC)
    "ClassificationComplianceHealer": AgentExecutionProfile(
        agent_id="ClassificationComplianceHealer",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
        notes="Deterministic classification compliance healing"
    ),
    
    "ValidationOrchestrator": AgentExecutionProfile(
        agent_id="ValidationOrchestrator",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
        notes="Deterministic validation orchestration"
    ),
    
    "HybridRetrieverConfig": AgentExecutionProfile(
        agent_id="HybridRetrieverConfig",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
        notes="Deterministic hybrid retrieval configuration"
    ),
    
    "UnifiedWorkflowConfig": AgentExecutionProfile(
        agent_id="UnifiedWorkflowConfig",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
        notes="Deterministic workflow configuration management"
    ),
}


def get_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID.
    
    Args:
        agent_id: The agent identifier to look up
        
    Returns:
        AgentExecutionProfile for the specified agent
        
    Raises:
        KeyError: If agent_id is not found in registry
    """
    if agent_id not in AGENT_REGISTRY:
        raise KeyError(f"Agent '{agent_id}' not found in registry. Available agents: {sorted(AGENT_REGISTRY.keys())}")
    
    return AGENT_REGISTRY[agent_id]


def registry_digest() -> str:
    """Compute SHA256 digest over canonical JSON of sorted registry.
    
    Returns:
        SHA256 hash string for determinism verification
    """
    # Convert registry to canonical format
    registry_data = {
        agent_id: profile.to_dict()
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
    }
    
    return compute_registry_digest(registry_data)


def get_all_agent_ids() -> tuple[str, ...]:
    """Get all registered agent IDs in deterministic order.
    
    Returns:
        Tuple of sorted agent IDs
    """
    return tuple(sorted(AGENT_REGISTRY.keys()))


def get_llm_agents() -> tuple[str, ...]:
    """Get all LLM-capable agent IDs.
    
    Returns:
        Tuple of agent IDs with LLM_API execution mode
    """
    return tuple(
        agent_id for agent_id, profile in sorted(AGENT_REGISTRY.items())
        if profile.execution_mode == ExecutionMode.LLM_API
    )


def get_deterministic_agents() -> tuple[str, ...]:
    """Get all deterministic agent IDs.
    
    Returns:
        Tuple of agent IDs with DETERMINISTIC execution mode
    """
    return tuple(
        agent_id for agent_id, profile in sorted(AGENT_REGISTRY.items())
        if profile.execution_mode == ExecutionMode.DETERMINISTIC
    )


def validate_registry() -> None:
    """Validate registry consistency and constraints."""
    # Check for duplicate agent IDs
    agent_ids = list(AGENT_REGISTRY.keys())
    if len(agent_ids) != len(set(agent_ids)):
        raise ValueError("Duplicate agent IDs found in registry")
    
    # Validate each profile
    for agent_id, profile in AGENT_REGISTRY.items():
        if profile.agent_id != agent_id:
            raise ValueError(f"Profile agent_id '{profile.agent_id}' doesn't match registry key '{agent_id}'")
    
    # Ensure at least one LLM agent and one deterministic agent
    llm_agents = get_llm_agents()
    deterministic_agents = get_deterministic_agents()
    
    if not llm_agents:
        raise ValueError("Registry must contain at least one LLM_API agent")
    
    if not deterministic_agents:
        raise ValueError("Registry must contain at least one DETERMINISTIC agent")


if __name__ == "__main__":
    # Registry validation and info
    validate_registry()
    
    print(f"Agent Registry: {len(AGENT_REGISTRY)} agents")
    print(f"Registry Digest: {registry_digest()}")
    print(f"LLM Agents: {get_llm_agents()}")
    print(f"Deterministic Agents: {get_deterministic_agents()}")
    
    # Example lookup
    try:
        profile = get_profile("SovereignLLMGateway")
        print(f"\nSovereignLLMGateway Profile: {profile}")
    except KeyError as e:
        print(f"Error: {e}")
