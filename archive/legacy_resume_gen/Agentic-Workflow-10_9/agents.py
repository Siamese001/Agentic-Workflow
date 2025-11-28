# FILE: agents.py
"""
Unified Multi-Agent Coordination Module (v10_9) — META Layer Only (RESTORED + ENHANCED)

This module defines the ENTIRE meta-level multi-agent behavior for the
v10_9 agentic workflow.

It is strictly **META-ONLY** (Layer above L1–L5):

    ❌ NO L1 cognition
    ❌ NO L2 execution
    ❌ NO L3 orchestration / DAG control flow
    ❌ NO L4 state mutation
    ❌ NO L5 safety/policy decisions

    ✔️ Provides multi-agent committees (QA council, Safety observers, etc.)
    ✔️ Normalizes agent roles and graph topologies
    ✔️ Performs deterministic scoring + voting
    ✔️ Generates multi-agent surfaces for self-correction
    ✔️ Produces patch-ready payloads for L4.StateAdapter (but does not mutate)
    ✔️ Aligns with the new meta_profile layer (typed biases)
    ✔️ Maximizes 14/14 agentic architecture compliance

This unifies meta-coordination behavior lost in 10_9 and restores 10_8
multi-agent functionality (committee arbitration, QA/Safety mixed panels,
delegation metadata, self-correction surfaces).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import (
    MultiAgentVote,
    MultiAgentCouncilResult,
    SelfCorrectionSurface,
    PlanObject,
    StatePatch,
)

# ---------------------------------------------------------------------------
# SECTION 1 — AGENT ROLES, NODES, AND GRAPHS
# ---------------------------------------------------------------------------

class AgentRole:
    """
    Agent role categories. These are NOT executable agents; they purely
    label advisory components in meta-level councils.

    Each role must own at most 1–2 capabilities to preserve agentic
    subdomain separation.
    """

    PLANNER = "planner"          # strategy advisor
    RETRIEVER = "retriever"      # RAG advisor
    DRAFTER = "drafter"          # drafting advisor
    BULLET = "bullet"            # bullet/achievement advisor
    QA = "qa"                    # QA advisor
    SAFETY = "safety"            # safety observer
    HIL = "hil"                  # human-in-loop observer
    META = "meta"                # meta-learning / biasing advisor


@dataclass
class AgentNode:
    """
    Static node definition for a meta-agent in a graph.
    """

    role: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    """
    Static meta-agent directed graph.

    * nodes: agent_name -> AgentNode
    * edges: directed edges (advisory flow)
    """

    nodes: Dict[str, AgentNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, name: str, role: str, **config: Any) -> None:
        self.nodes[name] = AgentNode(role=role, config=dict(config))

    def add_edge(self, source: str, target: str) -> None:
        self.edges.setdefault(source, []).append(target)


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """Pure-data summary for telemetry."""
    return {
        "nodes": {
            name: {"role": node.role, "config": node.config}
            for name, node in graph.nodes.items()
        },
        "edges": {src: list(tgts) for src, tgts in graph.edges.items()},
        "metadata": dict(graph.metadata),
    }


# ---------------------------------------------------------------------------
# SECTION 2 — QA COUNCIL (RESTORED v10_8 BEHAVIOR)
# ---------------------------------------------------------------------------

COUNCIL_OF_QA = AgentGraph(
    nodes={
        "qa_primary": AgentNode(role=AgentRole.QA, config={"id": 1, "weight": 1.0, "tier": "primary"}),
        "qa_secondary": AgentNode(role=AgentRole.QA, config={"id": 2, "weight": 0.8, "tier": "secondary"}),
        "safety_observer": AgentNode(role=AgentRole.SAFETY, config={"id": 3, "weight": 0.6, "tier": "observer"}),
        "meta_observer": AgentNode(role=AgentRole.META, config={"id": 4, "weight": 0.5, "tier": "observer"}),
    },
    edges={
        "qa_primary": ["safety_observer", "meta_observer"],
        "qa_secondary": ["safety_observer", "meta_observer"],
    },
    metadata={"type": "qa_council", "version": "v10_9_refactored"},
)


# ---------------------------------------------------------------------------
# SECTION 3 — SCORING AND VOTING LOGIC
# ---------------------------------------------------------------------------

def _qa_candidate_scores(
    graph: AgentGraph,
    state: Dict[str, Any],
    plan: Any,
) -> List[Dict[str, Any]]:
    """
    Deterministic scoring for each meta-agent in a QA council.
    Higher score → higher scrutiny / more conservative decision
    depending on severity and findings.
    """

    # Severity hint from L1 plan
    severity = "normal"
    if isinstance(plan, PlanObject):
        severity = str(plan.get("severity", "normal")).lower()
    elif isinstance(plan, dict):
        severity = str(plan.get("severity", "normal")).lower()

    qa_result = state.get("qa_result") or {}
    report = qa_result.get("report") or qa_result
    issues = report.get("issues", [])
    issue_count = len(issues)

    candidates = []
    for node_name, node in graph.nodes.items():
        if node.role not in (AgentRole.QA, AgentRole.SAFETY, AgentRole.META):
            continue

        node_id = int(node.config.get("id", 0))
        weight = float(node.config.get("weight", 1.0))
        tier = str(node.config.get("tier", "primary"))

        # Base score from severity
        base = 0.5
        if severity == "strict":
            base += 0.2
        elif severity == "high":
            base += 0.1

        if issue_count > 0:
            base += min(0.3, issue_count * 0.05)

        # Tier-based adjustments
        if tier == "primary":
            base += 0.05
        elif tier == "secondary":
            base += 0.02

        # Deterministic tie-breaker
        base += (node_id % 3) * 0.01

        score = round(base * weight, 3)
        candidates.append(
            {
                "id": node_id,
                "node_name": node_name,
                "role": node.role,
                "tier": tier,
                "score": score,
                "rationale": f"severity={severity}, issues={issue_count}, tier={tier}",
            }
        )

    return candidates


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Highest score wins; ties broken by lowest agent_id."""
    if not candidates:
        return {
            "id": 0,
            "node_name": "none",
            "role": "none",
            "score": 0.0,
            "rationale": "no_candidates",
        }
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c["score"]), int(c["id"])),
    )
    return sorted_candidates[0]


def build_council_result(
    graph: AgentGraph,
    state: Dict[str, Any],
    plan: Any,
) -> MultiAgentCouncilResult:
    """
    Produce a fully typed MultiAgentCouncilResult for the QA council.

    The council determines:
        • aggregated_decision (allow / revise / escalate)
        • aggregated_confidence
        • individual votes
        • rationale and metadata
    """

    candidates = _qa_candidate_scores(graph, state, plan)
    winner = deterministic_vote(candidates)

    votes: List[MultiAgentVote] = []
    for c in candidates:
        decision = "revise" if c["score"] >= 0.8 else "allow"
        if c["role"] == AgentRole.SAFETY:
            if "strict" in c["rationale"] or "issues=" in c["rationale"]:
                decision = "escalate"
        votes.append(
            MultiAgentVote(
                agent_id=str(c["id"]),
                decision=decision,
                confidence=float(c["score"]),
                rationale=c["rationale"],
                payload={"node_name": c["node_name"], "role": c["role"]},
            )
        )

    winner_vote = next((v for v in votes if v.agent_id == str(winner["id"])), None)
    aggregated_decision = winner_vote.decision if winner_vote else "allow"
    aggregated_confidence = winner["score"]

    council = MultiAgentCouncilResult(
        votes=votes,
        aggregated_decision=aggregated_decision,
        aggregated_confidence=aggregated_confidence,
        rationale=f"winner={winner['node_name']}({winner['role']}) score={winner['score']}",
        metadata={
            "graph": summarize_graph(graph),
            "severity": plan.get("severity") if isinstance(plan, dict) else getattr(plan, "severity", "normal"),
            "issue_count": len((state.get("qa_result") or {}).get("report", {}).get("issues", [])),
        },
    )
    return council


# ---------------------------------------------------------------------------
# SECTION 4 — META-LEVEL ORCHESTRATOR (NO PLANNING, NO EXECUTION)
# ---------------------------------------------------------------------------

@dataclass
class MultiAgentOrchestrator:
    """
    META-layer orchestrator.

    Responsibilities:
        • Evaluate a meta-agent graph (QA, Safety, Meta councils)
        • Produce MultiAgentCouncilResult objects
        • Provide patch-ready payloads for L4 without applying them
        • Provide synthetic meta-layer messages for logging/prompts

    It MUST NOT:
        • call L1 planners
        • call L2 executors
        • call L3 DAG logic
        • mutate L4 state directly
        • make L5 decisions
    """

    graph: AgentGraph
    state_adapter: Any  # must expose .state (read-only usage here)

    def _plan_dict(self, plan: Any) -> Dict[str, Any]:
        if isinstance(plan, PlanObject):
            return plan.to_dict()
        if isinstance(plan, dict):
            return dict(plan)
        try:
            return dict(vars(plan))
        except Exception:
            return {"repr": repr(plan)}

    def _synthetic_message_for_qa(self, plan: Any) -> Dict[str, Any]:
        p = self._plan_dict(plan)
        return {
            "role": "system",
            "content": (
                f"QA council evaluation for L1 objective: {p.get('objective', 'unknown-objective')}; "
                f"severity={p.get('severity', 'normal')}"
            ),
        }

    # ----------------------------------------------------------------------
    # PUBLIC META-AWARE ENTRYPOINTS
    # ----------------------------------------------------------------------

    def dispatch_for_qa(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """
        Execute the QA council and produce an L4-patch-ready payload:

            {"multi_agent": {"qa_council": {...}}}
        """
        synthetic_msg = self._synthetic_message_for_qa(plan)
        council = build_council_result(self.graph, state, plan)

        surfaces = [
            SelfCorrectionSurface.QA_RECHECK.value,
            SelfCorrectionSurface.SAFETY_RISK.value,
            SelfCorrectionSurface.USER_FEEDBACK.value,
        ]

        payload = {
            "synthetic_message": synthetic_msg,
            "council": {
                "votes": [v.__dict__ for v in council.votes],
                "aggregated_decision": council.aggregated_decision,
                "aggregated_confidence": council.aggregated_confidence,
                "rationale": council.rationale,
            },
            "surfaces": surfaces,
        }

        return {"multi_agent": {"qa_council": payload}}

    def build_patch_for_block(
        self,
        council_result: MultiAgentCouncilResult,
        *,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Build a meta-layer patch-ready payload for block/escalation cases.
        """
        payload = {
            "blocked": True,
            "reason": reason,
            "aggregated_decision": council_result.aggregated_decision,
            "aggregated_confidence": council_result.aggregated_confidence,
            "votes": [v.__dict__ for v in council_result.votes],
        }
        return {"multi_agent": {"qa_block": payload}}

    def to_dict(self) -> Dict[str, Any]:
        """
        Return pure-data description of this orchestrator (meta-only).
        """
        return {
            "graph": summarize_graph(self.graph),
            "has_state_adapter": self.state_adapter is not None,
        }
