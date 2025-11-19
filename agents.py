# FILE: agents.py
"""
Unified Multi-Agent Coordination Module (v10_9) — ENTERPRISE REFACTOR

This module provides meta-level multi-agent coordination for v10_9.
It sits conceptually *above* the L1–L5 layers and owns ONLY:

    • Agent role & graph definitions (roles, nodes, edges).
    • Multi-agent QA council orchestration (for meta-level QA).
    • Deterministic voting and metadata construction.

Non-responsibilities (to preserve L1–L5 purity):
    • NO planning (L1).
    • NO tool/LLM execution (L2).
    • NO control-flow orchestration (L3).
    • NO state mutation logic (L4).
    • NO safety decisions (L5).

L3 orchestrators may call:

    - MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=...)
        .dispatch_for_qa(state, plan) -> Dict[str, Any]

The returned dict is intended to be applied into L4 via StatePatch
by L3 orchestrators, e.g.:

    for key, value in council_state.items():
        state_adapter.apply_patch(StatePatch(key=key, value=value))
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple


# =============================================================================
# 1. AGENT ROLE & GRAPH DEFINITIONS
# =============================================================================


class AgentRole(str, Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    DRAFTER = "drafter"
    BULLET = "bullet"
    QA = "qa"
    SAFETY = "safety"


@dataclass
class AgentNode:
    role: AgentRole
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    nodes: List[AgentNode]
    edges: List[Tuple[AgentRole, AgentRole]]  # (from_role, to_role)


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """
    Deterministic summary of an agent graph, exposing only roles & edges.
    """
    def _role_value(r: AgentRole) -> str:
        return r.value

    return {
        "nodes": [_role_value(n.role) for n in graph.nodes],
        "edges": [[_role_value(a), _role_value(b)] for (a, b) in graph.edges],
    }


# -----------------------------------------------------------------------------
# COUNCIL_OF_QA graph: three QA agents, no edges (parallel council)
# -----------------------------------------------------------------------------

COUNCIL_OF_QA = AgentGraph(
    nodes=[
        AgentNode(AgentRole.QA, {"id": 1, "weight": 1.0}),
        AgentNode(AgentRole.QA, {"id": 2, "weight": 1.0}),
        AgentNode(AgentRole.QA, {"id": 3, "weight": 1.0}),
    ],
    edges=[],  # council members operate in parallel, no directed edges
)


# =============================================================================
# 2. DETERMINISTIC VOTING HELPERS
# =============================================================================


def _qa_candidate_scores(
    plan: Dict[str, Any],
    state: Dict[str, Any],
    node_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute a deterministic QA "candidate" with a score for a given
    council member.

    This is NOT an LLM call. It uses simple heuristics based on plan
    severity and existing QA issues in the state.

    Higher score → more likely to be selected.
    """
    severity = str(plan.get("severity", "normal")).lower()
    issues = (state.get("qa_result") or {}).get("report", {}).get("issues", [])
    issue_count = len(issues)

    base = 0.5
    if severity == "strict":
        base += 0.2
    if issue_count > 0:
        base += min(0.3, issue_count * 0.05)

    # Slight deterministic offset based on node id to break ties
    node_id = int(node_config.get("id", 0) or 0)
    offset = (node_id % 3) * 0.01

    score = round(base + offset, 3)
    return {
        "id": node_id,
        "score": score,
        "rationale": f"severity={severity}, issues={issue_count}, node_id={node_id}",
    }


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection:
        • Highest score wins.
        • Ties broken by smallest id.
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 999999))),
    )
    return sorted_candidates[0]


# =============================================================================
# 3. MULTI-AGENT ORCHESTRATOR (META-LEVEL)
# =============================================================================


@dataclass
class MultiAgentOrchestrator:
    """
    Multi-agent meta-orchestrator.

    This sits above L1–L5 and coordinates agent graphs, but does NOT:
        • call tools/LLMs
        • mutate state directly
        • own safety/policy

    L3 orchestrators pass:
        - graph: AgentGraph (e.g., COUNCIL_OF_QA)
        - state_adapter: StateAdapter (L4), used only via its public API.

    The orchestrator returns a dict representing patches to be applied
    via L4.StateAdapter (e.g., "multi_agent" or "qa_council" blocks).
    """

    graph: AgentGraph
    state_adapter: Any  # Typed as Any to avoid import cycles; must expose .state

    # -------------------------------------------------------------------------
    # QA COUNCIL ENTRYPOINT
    # -------------------------------------------------------------------------

    def dispatch_for_qa(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """
        Execute a QA council pass:

            • Build a synthetic "message" capturing the QA objective.
            • Generate candidates for each QA agent (score + rationale).
            • Choose a winner via deterministic_vote.
            • Return a dict of fields to patch into state via L4.

        NOTE: This method does NOT mutate state_adapter internally; L3
        remains responsible for applying patches via StatePatch.
        """
        # Build synthetic message for the council
        if isinstance(plan, dict):
            objective = str(plan.get("objective", ""))
            severity = str(plan.get("severity", "normal"))
        else:
            objective = str(getattr(plan, "objective", "") or "")
            severity = str(getattr(plan, "severity", "normal") or "")

        synthetic_message = {
            "role": "system",
            "content": (
                f"QA council evaluation for objective: {objective or 'unspecified-objective'}; "
                f"severity: {severity or 'normal'}"
            ),
        }

        # Build candidates
        plan_dict = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
        candidates: List[Dict[str, Any]] = []
        for node in self.graph.nodes:
            if node.role != AgentRole.QA:
                continue
            cand = _qa_candidate_scores(plan_dict, state, node.config)
            candidates.append(cand)

        vote = deterministic_vote(candidates)

        multi_agent_block: Dict[str, Any] = {
            "last_message": synthetic_message,
            "sender": "orchestrator",
            "recipient": "qa_council",
            "graph_summary": summarize_graph(self.graph),
            "candidates": candidates,
            "winner": vote,
        }

        # Return fields to be patched into L4 state
        return {
            "multi_agent": multi_agent_block,
        }
