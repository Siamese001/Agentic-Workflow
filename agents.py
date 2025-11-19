# FILE: agents.py
"""
Unified Multi-Agent Coordination Module (v10_9) — META LAYER ONLY (RESTORED)

This module provides meta-level multi-agent coordination for v10_9.
It sits conceptually *above* the L1–L5 layers and owns ONLY:

    • Agent role & graph definitions (roles, nodes, edges).
    • Multi-agent council / committee graph structures.
    • Deterministic voting and metadata construction.
    • High-level orchestration helpers for QA / Safety / Meta councils.
    • Council results suitable for self-correction and observability.

Non-responsibilities (to preserve L1–L5 purity):

    • NO planning (L1 cognition).
    • NO execution (L2 tools/LLMs).
    • NO DAG orchestration (L3 control flow).
    • NO state mutation (L4 writes).
    • NO safety/policy decisions (L5 enforcement).
    • NO provider/SDK logic.

All multi-agent behavior here is *advisory* and expressed via
typed council results and patch payloads. L3/L4/L5 remain the
source of truth for execution, state, and safety.

This refactor restores and extends v10_8-style multi-agent
capabilities (QA councils, committee voting, cross-role
delegation metadata) while preserving strict agentic layering
and typed contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import (
    MultiAgentVote,
    MultiAgentCouncilResult,
    SelfCorrectionSurface,
    PlanObject,
)


# ============================================================================
# 1. AGENT ROLES & NODES
# ============================================================================


class AgentRole:
    """Conceptual agent roles used in meta-level graphs.

    These roles are NOT executable agents themselves; they are
    labels used by higher layers (L2/L3/meta) to reason about
    responsibilities and flows.

    Each role must own at most 1–2 capabilities to preserve
    agentic subdomain boundaries.
    """

    PLANNER = "planner"       # strategy / planning advisor
    RETRIEVER = "retriever"   # retrieval / RAG advisor
    DRAFTER = "drafter"       # drafting advisor
    BULLET = "bullet"         # bullet-style achievements advisor
    QA = "qa"                 # QA advisor
    SAFETY = "safety"         # safety advisor (non-binding)
    HIL = "hil"               # HIL advisor (escalation semantics)
    META = "meta"             # meta-learning / self-correction advisor


# Backwards-compatible uppercase names (used in original v10_9)
PLANNER = AgentRole.PLANNER
RETRIEVER = AgentRole.RETRIEVER
DRAFTER = AgentRole.DRAFTER
BULLET = AgentRole.BULLET
QA = AgentRole.QA
SAFETY = AgentRole.SAFETY
HIL = AgentRole.HIL
META = AgentRole.META


@dataclass
class AgentNode:
    """Node in a meta-level agent graph.

    Fields:
        role:   conceptual AgentRole (planner, qa, safety, etc.)
        config: arbitrary agent-specific metadata (id, weight, tags)

    This is a *pure data* structure, used for council configuration
    and observability only.
    """

    role: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    """Meta-level agent graph configuration.

    Fields:
        nodes: mapping of node_name -> AgentNode
        edges: mapping of node_name -> list of downstream node_names
        metadata: arbitrary graph-level metadata

    This graph is *static configuration* for councils and never
    executes tools or mutates state.
    """

    nodes: Dict[str, AgentNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, name: str, role: str, **config: Any) -> None:
        self.nodes[name] = AgentNode(role=role, config=dict(config))

    def add_edge(self, source: str, target: str) -> None:
        self.edges.setdefault(source, []).append(target)


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """Return a pure-data summary of an AgentGraph for observability.

    This is safe to serialize and log.
    """
    return {
        "nodes": {name: {"role": node.role, "config": node.config} for name, node in graph.nodes.items()},
        "edges": {src: list(tgts) for src, tgts in graph.edges.items()},
        "metadata": dict(graph.metadata),
    }


# ============================================================================
# 2. QA / SAFETY COUNCIL CONFIGURATION
# ============================================================================


# A default QA council that mirrors v10_8-style multi-agent QA review:
#   • qa_primary: main QA advisor
#   • qa_secondary: secondary QA advisor (slightly different weighting)
#   • safety_observer: safety-focused advisor (non-binding)
#   • meta_observer: meta-learning-focused advisor
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
    metadata={"type": "qa_council", "version": "v10_9"},
)


# ============================================================================
# 3. QA / SAFETY SCORING & VOTING
# ============================================================================


def _qa_candidate_scores(
    graph: AgentGraph,
    state: Dict[str, Any],
    plan: Any,
) -> List[Dict[str, Any]]:
    """Compute deterministic QA candidate scores for each QA node.

    Inputs:
        • graph: AgentGraph describing the QA council.
        • state: current orchestration state (read-only view).
        • plan:  QA PlanObject or plain dict with "severity" field.

    Outputs:
        List[dict]: each with {id, node_name, score, rationale, role}.
    """
    # Severity hint from plan
    severity = "normal"
    if isinstance(plan, PlanObject):
        severity = str(plan.get("severity", "normal")).lower()
    elif isinstance(plan, dict):
        severity = str(plan.get("severity", "normal")).lower()

    qa_state = state.get("qa_result") or {}
    report = (qa_state.get("report") or qa_state) or {}
    issues = report.get("issues", [])
    issue_count = len(issues)

    candidates: List[Dict[str, Any]] = []
    for node_name, node in graph.nodes.items():
        if node.role not in (AgentRole.QA, AgentRole.SAFETY, AgentRole.META):
            continue

        node_id = int(node.config.get("id", 0) or 0)
        weight = float(node.config.get("weight", 1.0))
        tier = str(node.config.get("tier", "primary"))

        base = 0.5

        # Severity influences base score
        if severity == "strict":
            base += 0.2
        elif severity == "high":
            base += 0.1

        # More issues → higher scrutiny
        if issue_count > 0:
            base += min(0.3, issue_count * 0.05)

        # Tier-specific adjustments
        if tier == "primary":
            base += 0.05
        elif tier == "secondary":
            base += 0.02

        # Deterministic offset for tie-breaking
        offset = (node_id % 3) * 0.01

        score = round((base * weight) + offset, 3)
        candidates.append(
            {
                "id": node_id,
                "node_name": node_name,
                "role": node.role,
                "score": score,
                "rationale": f"severity={severity}, issues={issue_count}, tier={tier}, id={node_id}",
            }
        )

    return candidates


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministic selection:
        • Highest score wins.
        • Ties broken by smallest id.

    Returns:
        winner: dict with at least {id, node_name, score, role, rationale}
    """
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
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 0))),
    )
    return sorted_candidates[0]


def build_council_result(
    graph: AgentGraph,
    state: Dict[str, Any],
    plan: Any,
) -> MultiAgentCouncilResult:
    """Build a MultiAgentCouncilResult for a QA/Safety council.

    This produces a stable, typed summary of the QA council's view:

        • individual votes (agent id, decision, confidence, rationale)
        • aggregated decision (allow / revise / escalate)
        • aggregated confidence
        • rationale + metadata

    L3/L5 may use this as an input to self-correction and safety
    arbitration.
    """
    candidates = _qa_candidate_scores(graph, state, plan)
    winner = deterministic_vote(candidates)

    votes: List[MultiAgentVote] = []
    for cand in candidates:
        decision = "revise" if cand["score"] >= 0.8 else "allow"
        if "safety" in cand["role"]:
            # safety observers tilt toward escalate on high severity
            if "strict" in cand["rationale"] or "issues=" in cand["rationale"]:
                decision = "escalate"
        votes.append(
            MultiAgentVote(
                agent_id=str(cand["id"]),
                decision=decision,
                confidence=float(cand["score"]),
                rationale=cand["rationale"],
                payload={
                    "node_name": cand["node_name"],
                    "role": cand["role"],
                },
            )
        )

    # Aggregated decision: winner's decision
    winner_vote = next((v for v in votes if v.agent_id == str(winner["id"])), None)
    aggregated_decision = winner_vote.decision if winner_vote else "allow"
    aggregated_confidence = winner["score"]

    council = MultiAgentCouncilResult(
        votes=votes,
        aggregated_decision=aggregated_decision,
        aggregated_confidence=aggregated_confidence,
        rationale=f"winner={winner['node_name']}({winner['role']}) score={winner['score']}",
        metadata={
            "severity": plan.get("severity", "normal") if isinstance(plan, dict) else getattr(plan, "severity", "normal"),
            "issue_count": len((state.get("qa_result") or {}).get("report", {}).get("issues", [])),
            "graph": summarize_graph(graph),
        },
    )
    return council


# ============================================================================
# 4. MULTI-AGENT ORCHESTRATOR (META ONLY)
# ============================================================================


@dataclass
class MultiAgentOrchestrator:
    """Meta-level multi-agent orchestrator.

    This is a *pure meta layer* construct. It may:

        • Read state via state_adapter.state (L4 read-only).
        • Evaluate meta-graphs (AgentGraph).
        • Produce MultiAgentCouncilResult objects.
        • Build patch payloads for L3/L4 to apply.

    It may NOT:

        • plan tasks (L1)
        • execute tools / LLMs (L2)
        • own safety/policy (L5 decisions)
        • implement workflow phases (L3)

    L3 orchestrators may call:

        ma = MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=adapter)
        council_patch = ma.dispatch_for_qa(state, plan)
        for key, value in council_patch.items():
            state_adapter.apply_patch(StatePatch(key=key, value=value))
    """

    graph: AgentGraph
    state_adapter: Any  # Typed as Any to avoid import cycles; must expose .state

    # --------------------------------------------------------------------- #
    # Internal utilities
    # --------------------------------------------------------------------- #

    def _role_value(self, node_name: str) -> str:
        node = self.graph.nodes.get(node_name)
        return node.role if node is not None else "unknown"

    def _build_synthetic_message(self, plan: Any) -> Dict[str, Any]:
        """Build a synthetic system-style message capturing QA objective.

        This does not call any LLM; it simply encodes the intent for
        downstream prompt layers.
        """
        pdict = self._plan_to_dict(plan)
        objective = pdict.get("objective", "unspecified-objective")
        severity = pdict.get("severity", "normal")
        return {
            "role": "system",
            "content": (
                f"QA council evaluation for objective: {objective}; severity: {severity}"
            ),
        }

    def _plan_to_dict(self, plan: Any) -> Dict[str, Any]:
        """Normalize a plan object into a dict for inspection.

        This function is defensive and safe to call on PlanObject or
        plain dicts.
        """
        if isinstance(plan, PlanObject):
            return plan.to_dict()
        if isinstance(plan, dict):
            return dict(plan)
        try:
            return dict(vars(plan))
        except TypeError:
            return {"repr": repr(plan)}

    # --------------------------------------------------------------------- #
    # Public multi-agent entrypoints
    # --------------------------------------------------------------------- #

    def dispatch_for_qa(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """Execute a QA council pass *at the meta layer*.

        Steps:
            • Build a synthetic message capturing QA objective.
            • Construct a MultiAgentCouncilResult for the QA council.
            • Annotate with self-correction surfaces.
            • Return a patch payload suitable for L4.StateAdapter.

        Returns:
            dict suitable for use as:

                patch = ma.dispatch_for_qa(state, plan)
                state_adapter.apply_patch(StatePatch(key="multi_agent", value=patch["multi_agent"]))
        """
        synthetic_message = self._build_synthetic_message(plan)
        council = build_council_result(self.graph, state, plan)

        surfaces: List[SelfCorrectionSurface] = [
            SelfCorrectionSurface.QA_RECHECK,
            SelfCorrectionSurface.SAFETY_RISK,
            SelfCorrectionSurface.USER_FEEDBACK,
        ]

        payload = {
            "synthetic_message": synthetic_message,
            "council": {
                "votes": [v.__dict__ for v in council.votes],
                "aggregated_decision": council.aggregated_decision,
                "aggregated_confidence": council.aggregated_confidence,
                "rationale": council.rationale,
            },
            "surfaces": [s.value for s in surfaces],
        }

        return {"multi_agent": {"qa_council": payload}}

    def build_patch_for_block(
        self,
        council_result: MultiAgentCouncilResult,
        *,
        reason: str,
    ) -> Dict[str, Any]:
        """Build a convenient patch for block/escalation surfaces.

        This method does not apply the patch; it only builds the
        payload. L3/L4 must decide whether and how to persist it.

        Typical usage:

            council = build_council_result(...)
            patch = ma.build_patch_for_block(council, reason="safety_block")
            state_adapter.apply_patch(StatePatch(key="multi_agent", value=patch["multi_agent"]))
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
        """Return a pure-data view of the orchestrator configuration.

        Includes:
            • graph summary
            • presence of state_adapter (no live state)
        """
        return {
            "graph": summarize_graph(self.graph),
            "has_state_adapter": self.state_adapter is not None,
        }
