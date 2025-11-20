# FILE: agents.py
"""
Unified Multi-Agent Coordination (v10_10) — META COUNCILS (REFACTORED)

This module implements the "Social Layer" of the agent (Pillar 2).
It manages multi-agent topologies (Councils, Juries) and voting logic.

Responsibilities:
    1. Agent Graph: Define nodes (personas) and edges (communication).
    2. Council Voting: Deterministic consensus mechanisms (Pillar 5).
    3. Dispute Resolution: Weighted scoring based on agent authority.

Refactor Highlights (v10_10):
    • Strict Typing: Returns `MultiAgentCouncilResult` (Pydantic).
    • Declarative Graphs: Agents defined by config, not class hierarchy.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import Field

from models import (
    AgenticBaseModel,
    MultiAgentCouncilResult,
    MultiAgentVote,
    PlanObject
)
from runtime_utils import record_event

# =============================================================================
# GRAPH PRIMITIVES
# =============================================================================

class AgentRole(AgenticBaseModel):
    """Defines a persona/role in a council."""
    name: str
    weight: float = 1.0
    focus_area: str = "general"
    tier: str = "primary" # primary, observer, tie-breaker

class AgentNode(AgenticBaseModel):
    """A single agent instance in a graph."""
    id: str
    role: AgentRole
    config: Dict[str, Any] = Field(default_factory=dict)

class AgentGraph(AgenticBaseModel):
    """Topological definition of a multi-agent group."""
    nodes: Dict[str, AgentNode] = Field(default_factory=dict)
    edges: Dict[str, List[str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_node(self, node: AgentNode) -> None:
        self.nodes[node.id] = node


# =============================================================================
# STANDARD COUNCILS (Pillar 2: Boundaries)
# =============================================================================

def build_qa_council(severity: str = "normal") -> AgentGraph:
    """
    Constructs a standard QA Council graph.
    Adjusts weights based on task severity (Pillar 5: Capability).
    """
    graph = AgentGraph(metadata={"type": "qa_council", "severity": severity})
    
    # 1. Primary Reviewer
    graph.add_node(AgentNode(
        id="qa_primary",
        role=AgentRole(name="QA_Primary", weight=1.0, focus_area="accuracy")
    ))
    
    # 2. Safety Observer (Higher weight in high severity)
    safety_weight = 1.5 if severity in ("high", "critical") else 0.8
    graph.add_node(AgentNode(
        id="safety_observer",
        role=AgentRole(name="Safety_Observer", weight=safety_weight, focus_area="policy")
    ))

    # 3. Meta Critic (Tie breaker)
    graph.add_node(AgentNode(
        id="meta_critic",
        role=AgentRole(name="Meta_Critic", weight=0.5, tier="tie-breaker")
    ))

    return graph


# =============================================================================
# VOTING ENGINE
# =============================================================================

class CouncilManager:
    """
    Orchestrates voting and consensus for a given graph.
    """
    
    def run_council(
        self, 
        graph: AgentGraph, 
        context: Dict[str, Any], 
        plan: PlanObject
    ) -> MultiAgentCouncilResult:
        """
        Simulates a council session.
        In v10_10, this calculates scores deterministically based on findings.
        """
        votes: List[MultiAgentVote] = []
        
        # Context extraction
        qa_result = context.get("qa_result", {})
        issues = []
        # Handle both dict and Pydantic forms
        if isinstance(qa_result, dict):
             report = qa_result.get("report", {})
             issues = report.get("findings", [])
        elif hasattr(qa_result, "report"):
             issues = qa_result.report.findings

        issue_count = len(issues)

        for node_id, node in graph.nodes.items():
            score, decision, rationale = self._calculate_vote(node, issue_count, plan)
            
            votes.append(MultiAgentVote(
                agent_id=node_id,
                decision=decision,
                confidence=score,
                rationale=rationale,
                payload={"role": node.role.name}
            ))

        # Aggregation Logic (Weighted Vote)
        final_decision = self._aggregate_votes(votes, graph)
        
        return MultiAgentCouncilResult(
            votes=votes,
            aggregated_decision=final_decision,
            aggregated_confidence=1.0, # Simplified
            rationale=f"Council consensus: {final_decision}",
            metadata={"graph_id": graph.metadata.get("type")}
        )

    def _calculate_vote(self, node: AgentNode, issue_count: int, plan: PlanObject) -> tuple[float, str, str]:
        """
        Deterministic logic for agent voting.
        """
        # Base Logic: If issues exist, critics vote 'revise'.
        # Safety always votes 'escalate' if issues are high.
        
        if node.role.name == "Safety_Observer":
            if issue_count > 0:
                return 0.9, "escalate", "Safety issues detected."
            return 1.0, "allow", "No safety issues."
            
        if node.role.name == "QA_Primary":
            if issue_count > 0:
                return 0.8, "revise", f"Found {issue_count} QA findings."
            return 1.0, "allow", "Clean QA report."
            
        # Default / Meta
        return 0.5, "allow", "Passive observer."

    def _aggregate_votes(self, votes: List[MultiAgentVote], graph: AgentGraph) -> str:
        """
        Weighted aggregation.
        """
        scores = {"allow": 0.0, "revise": 0.0, "escalate": 0.0}
        
        for v in votes:
            node = graph.nodes.get(v.agent_id)
            weight = node.role.weight if node else 1.0
            scores[v.decision] += (v.confidence * weight)
            
        # Return winner
        winner = max(scores, key=scores.get)
        record_event("council_vote", {"winner": winner, "scores": scores})
        return winner

# Singleton Helper
COUNCIL_MANAGER = CouncilManager()
