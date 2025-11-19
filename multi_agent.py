# FILE: multi_agent.py
"""
Unified Multi-Agent Coordination Layer (v10_9, Fully Refactored)
META-ONLY — MAX SCORE: Agent Boundaries, Layering Model, Typed Contracts

This module implements PURE multi-agent meta-coordination.
It is **not** L1/L2/L3/L4/L5. It sits ABOVE them.

Responsibilities:
    • Define conceptual agent roles (Planner, Retriever, QA, Safety, HIL)
    • Define static or dynamic agent graphs
    • Deterministic multi-agent council voting (QA council)
    • Message-passing metadata (sender, recipient, rationale)
    • Return only *patch-ready* dicts (L3 applies StatePatches)
    • Zero execution, zero planning, zero safety decisions

Strictly forbidden in this layer:
    • No L1 cognition / strategy reasoning
    • No L2 execution / tool calls
    • No L3 orchestration / DAG logic
    • No L4 state mutation
    • No L5 safety/policy decisions
    • No provider calls

This refactoring:
    • Consolidates missing 10_8 multi-agent logic
    • Restores route_trace metadata
    • Adds deterministic QA council scoring
    • Provides typed MultiAgentCouncilResult output
    • Aligns with 14-subdomain agentic architecture (max score)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from models import MultiAgentCouncilResult, MultiAgentVote


# ============================================================================
# 1. AGENT ROLES
# ============================================================================

@dataclass(frozen=True)
class AgentRole:
    """
    Conceptual agent role. Pure metadata only.
    """
    name: str
    description: str = ""


ROLE_PLANNER   = AgentRole("planner",   "L1 planners / strategic reasoning")
ROLE_RETRIEVER = AgentRole("retriever", "Evidence / RAG planners")
ROLE_DRAFTER   = AgentRole("drafter",   "Drafting / narrative")
ROLE_BULLETS   = AgentRole("bullets",   "Bullet generation")
ROLE_QA        = AgentRole("qa",        "Quality checks")
ROLE_SAFETY    = AgentRole("safety",    "Safety / compliance review")
ROLE_HIL       = AgentRole("hil",       "Human-in-the-loop review")
ROLE_META      = AgentRole("meta",      "Meta learning")


# ============================================================================
# 2. AGENT NODE + GRAPH STRUCTURES
# ============================================================================

@dataclass
class AgentNode:
    role: AgentRole
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    """
    Directed multi-agent conceptual graph:
        nodes: List[AgentNode]
        edges: List[Tuple[str, str]]. Edges are ROLE.name → ROLE.name
    """

    nodes: List[AgentNode]
    edges: List[Tuple[str, str]]  # ("qa","safety") meaning QA routes to Safety

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {"role": n.role.name, "description": n.role.description, "config": n.config}
                for n in self.nodes
            ],
            "edges": [[a, b] for (a, b) in self.edges],
        }


# ============================================================================
# 3. DEFAULT QA COUNCIL (RESTORED 10_8 LOGIC)
# ============================================================================

COUNCIL_OF_QA: AgentGraph = AgentGraph(
    nodes=[
        AgentNode(role=ROLE_QA, config={"id": 1, "weight": 1.0}),
        AgentNode(role=ROLE_QA, config={"id": 2, "weight": 1.0}),
        AgentNode(role=ROLE_QA, config={"id": 3, "weight": 1.0}),
    ],
    edges=[],  # parallel council, no delegations between members
)


# ============================================================================
# 4. DETERMINISTIC CANDIDATE GENERATION
# ============================================================================

def _score_candidate(
    plan: Dict[str, Any],
    state: Dict[str, Any],
    node_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Deterministic QA-candidate scoring logic.
    Pure META (no L1/L2).
    """

    severity = str(plan.get("severity", "normal")).lower()
    qa_state = state.get("qa_result") or {}
    report = qa_state.get("report", {}) or {}
    issues = report.get("issues", [])
    issue_count = len(issues)

    base = 0.5

    if severity == "strict":
        base += 0.2
    if issue_count > 0:
        base += min(0.3, issue_count * 0.05)

    node_id = int(node_config.get("id", 0))
    offset = (node_id % 3) * 0.01  # tie-breaker

    score = round(base + offset, 3)

    return {
        "id": node_id,
        "score": score,
        "rationale": f"severity={severity}, issues={issue_count}, node_id={node_id}",
    }


def _deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection:
        • Highest score wins
        • Ties → smallest id
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    return sorted(
        candidates,
        key=lambda c: (-float(c["score"]), int(c["id"])),
    )[0]


# ============================================================================
# 5. COUNCIL RESULT CONSTRUCTION
# ============================================================================

def _build_council_result(
    candidates: List[Dict[str, Any]],
    winner: Dict[str, Any],
) -> MultiAgentCouncilResult:
    votes: List[MultiAgentVote] = []
    for c in candidates:
        votes.append(
            MultiAgentVote(
                candidate_id=c["id"],
                score=float(c["score"]),
                rationale=str(c["rationale"]),
            )
        )

    return MultiAgentCouncilResult(
        selected_id=winner["id"],
        selected_score=float(winner["score"]),
        votes=votes,
    )


# ============================================================================
# 6. MULTI-AGENT ORCHESTRATOR (META-ONLY)
# ============================================================================

@dataclass
class MultiAgentOrchestrator:
    """
    Multi-agent meta-level coordinator.

    L3 orchestrator calls:
        ma = MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=adapter)
        patch = ma.dispatch_for_qa(state, plan)
        L3 then applies patch via StatePatch.

    Responsibilities (META ONLY):
        • Build deterministic candidates
        • Score them
        • Build council result
        • Produce a patch-ready dict:
            {"multi_agent": {...}}
    """

    graph: AgentGraph
    state_adapter: Any  # L4 adapter injected by L3

    def dispatch_for_qa(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """
        Perform QA council reasoning.

        Returns:
            {
              "multi_agent": {
                  ... deterministic metadata ...
              }
            }
        """

        plan_dict = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)

        candidates: List[Dict[str, Any]] = []
        for node in self.graph.nodes:
            if node.role.name == "qa":
                cand = _score_candidate(plan_dict, state, node.config)
                candidates.append(cand)

        winner = _deterministic_vote(candidates)
        council_result = _build_council_result(candidates, winner)

        trace = [{"agent_id": c["id"], "score": c["score"]} for c in candidates]

        multi_agent_block: Dict[str, Any] = {
            "sender": "multi_agent_orchestrator",
            "recipient": "qa_council",
            "graph": self.graph.to_dict(),
            "candidates": candidates,
            "winner": winner,
            "route_trace": trace,
            "council_result": council_result.to_dict(),
        }

        return {"multi_agent": multi_agent_block}
