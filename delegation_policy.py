from typing import Dict, Any
from multi_agent import AgentRole


def can_delegate(from_role: AgentRole, to_role: AgentRole) -> bool:
    """
    Deterministic fixed delegation policy.
    """
    if from_role == AgentRole.PLANNER:
        return to_role in {AgentRole.RETRIEVER, AgentRole.DRAFTER, AgentRole.QA}
    if from_role == AgentRole.RETRIEVER:
        return to_role == AgentRole.DRAFTER
    if from_role == AgentRole.DRAFTER:
        return to_role == AgentRole.QA
    if from_role == AgentRole.QA:
        return to_role == AgentRole.SAFETY
    return False


def delegation_metadata(sender: AgentRole, recipient: AgentRole) -> Dict[str, Any]:
    return {
        "from": sender.value,
        "to": recipient.value,
        "allowed": can_delegate(sender, recipient),
    }
