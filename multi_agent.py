# FILE: multi_agent.py
"""
Unified Multi-Agent Patterns (v10_10) — TOPOLOGY FACTORY (REFACTORED)

This module implements the "Org Chart" of the agent (Pillar 2).
It provides standard factories to instantiate `AgentGraph` topologies.

Responsibilities:
    1. Topology Factories: Linear, Star, Council, Committee patterns.
    2. Edge Logic: Defines how agents connect (Advisor vs. Supervisor).
    3. Zero-Loss Port: Restores v10_9 patterns using v10_10 Pydantic models.

Refactor Highlights (v10_10):
    • Uses `agents.AgentGraph` and `AgentNode` strict models.
    • Removes implicit dict merging in favor of explicit graph construction.
"""

from __future__ import annotations

from typing import List, Dict, Any
from agents import AgentGraph, AgentNode, AgentRole

# =============================================================================
# PATTERN ENUMS
# =============================================================================

class MultiAgentPattern(str):
    LINEAR_PIPELINE = "linear_pipeline"
    STAR_HUB = "star_hub"
    COUNCIL = "council"
    COMMITTEE = "committee"

# =============================================================================
# TOPOLOGY FACTORIES
# =============================================================================

def build_linear_pipeline(roles: List[str]) -> AgentGraph:
    """
    Builds a sequential chain: A -> B -> C.
    Useful for processing steps (e.g. Drafter -> QA -> Safety).
    """
    graph = AgentGraph(metadata={"pattern": MultiAgentPattern.LINEAR_PIPELINE})
    
    previous_id = None
    
    for i, role_name in enumerate(roles):
        node_id = role_name.lower()
        
        # Create Node
        node = AgentNode(
            id=node_id,
            role=AgentRole(name=role_name, weight=1.0)
        )
        graph.add_node(node)
        
        # Create Edge from previous
        if previous_id:
            graph.edges.setdefault(previous_id, []).append(node_id)
            
        previous_id = node_id
        
    return graph


def build_star_hub(hub_role: str, spoke_roles: List[str]) -> AgentGraph:
    """
    Builds a Hub-and-Spoke model.
    Hub connects to all spokes. Spokes only connect to Hub.
    Useful for Orchestrator (Hub) delegating to Specialists (Spokes).
    """
    graph = AgentGraph(metadata={"pattern": MultiAgentPattern.STAR_HUB})
    
    hub_id = hub_role.lower()
    
    # Create Hub
    graph.add_node(AgentNode(
        id=hub_id,
        role=AgentRole(name=hub_role, weight=2.0, tier="primary")
    ))
    
    # Create Spokes
    for spoke_name in spoke_roles:
        spoke_id = spoke_name.lower()
        
        graph.add_node(AgentNode(
            id=spoke_id,
            role=AgentRole(name=spoke_name, weight=1.0)
        ))
        
        # Bidirectional Edge
        graph.edges.setdefault(hub_id, []).append(spoke_id)
        graph.edges.setdefault(spoke_id, []).append(hub_id)
        
    return graph


def build_committee(roles: List[str]) -> AgentGraph:
    """
    Builds a flat group with no directed edges.
    Useful for simple voting where everyone is equal.
    """
    graph = AgentGraph(metadata={"pattern": MultiAgentPattern.COMMITTEE})
    
    for role_name in roles:
        node_id = role_name.lower()
        graph.add_node(AgentNode(
            id=node_id,
            role=AgentRole(name=role_name, weight=1.0)
        ))
        
    return graph


def build_council(role_name: str, size: int = 3) -> AgentGraph:
    """
    Builds a homogeneous group of identical roles (e.g., 3 Reviewers).
    Useful for 'Jury' patterns to reduce variance.
    """
    graph = AgentGraph(metadata={"pattern": MultiAgentPattern.COUNCIL})
    
    for i in range(size):
        node_id = f"{role_name.lower()}_{i+1}"
        graph.add_node(AgentNode(
            id=node_id,
            role=AgentRole(name=role_name, weight=1.0, config={"id": i+1})
        ))
        
    return graph
