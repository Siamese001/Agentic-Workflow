# FILE: agents.py
"""
Unified Multi-Agent Coordination Module (v10_9) — META LAYER ONLY

This module provides meta-level multi-agent coordination for v10_9.
It sits conceptually *above* the L1–L5 layers and owns ONLY:

    • Agent role & graph definitions (roles, nodes, edges).
    • Multi-agent council / committee graph structures.
    • Deterministic voting and metadata construction.
    • High-level orchestration helpers for QA councils and similar
      meta-level reviews.

Non-responsibilities (to preserve L1–L5 purity):

    • NO planning (L1 cognition).
    • NO tool/LLM execution (L2).
    • NO control-flow orchestration / phase changes (L3).
    • NO state mutation logic (L4).
    • NO safety/policy decisions (L5).

L3 orchestrators may call:

    - MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=...)
        .dispatch_for_qa(state, plan) -> Dict[str, Any]

The returned dict is intended to be applied into L4 via StatePatch
by L3 orchestrators, e.g.:

    for key, value in council_state.items():
        state_adapter.apply_patch(StatePatch(key=key, value=value))

This design satisfies Agentic constraints:

    • Layering Model (ID 1): this file is meta-only.
    • Agent Boundaries (ID 2): each agent role is conceptual only.
    • Typed Contracts (ID 3): outputs are clean dicts and can wrap
      models.MultiAgentCouncilResult where desired.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional

from models import MultiAgentVote, MultiAgentCouncilResult


# =============================================================================
# 1. AGENT ROLE & GRAPH DEFINITIONS
# =============================================================================


class AgentRole(str, Enum):
    """
    Conceptual agent roles used in meta-level graphs.

    These roles are NOT executable agents themselves; they are
    labels used by higher layers (L2/L3/meta) to reason about
    responsibilities and flows.
    """

    PLANNER = "planner"
    RETRIEVER = "retriever"
    DRAFTER = "drafter"
    BULLET = "bullet"
    QA = "qa"
    SAFETY = "safety"
    HIL = "hil"
    META = "meta"


@dataclass
class AgentNode:
    """
    Node in a meta-level agent graph.

    Fields:
        role:   conceptual AgentRole (planner, qa, safety, etc.)
        config: arbitrary agent-specific metadata (id, weight, tags)
    """

    role: AgentRole
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    """
    Directed meta-level agent graph.

    nodes:
        list of AgentNode objects
    edges:
        list of (from_role, to_role) tuples, conceptual only
    """

    nodes: List[AgentNode]
    edges: List[Tuple[AgentRole, AgentRole]]  # (from_role, to_role)


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """
    Deterministic summary of an agent graph, exposing only roles & edges.

    This is safe to record in state and telemetry and can be used
    by downstream tools or UIs to visualize the multi-agent topology.
    """

    def _role_value(r: AgentRole) -> str:
        return r.value

    return {
        "nodes": [
            {"role": _role_value(n.role), "config": dict(n.config)}
            for n in graph.nodes
        ],
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
# 2. DETERMINISTIC SCORING AND VOTING HELPERS
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

    The algorithm is intentionally lightweight and stable:
        • base score = 0.5
        • +0.2 for "strict" severity
        • +min(0.3, issue_count * 0.05)
        • +tie-breaker offset based on node id
    """
    severity = str(plan.get("severity", "normal")).lower()
    qa_state = state.get("qa_result") or {}
    report = qa_state.get("report") or {}
    issues = report.get("issues", []) if isinstance(report, dict) else []
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

    This helper is central to council behavior and is deliberately
    pure and side-effect free.
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 999_999))),
    )
    return sorted_candidates[0]


def build_council_result(
    candidates: List[Dict[str, Any]],
    winner: Dict[str, Any],
) -> MultiAgentCouncilResult:
    """
    Construct a MultiAgentCouncilResult (typed model) from candidate
    dicts and the chosen winner.

    This maintains a typed contract while allowing callers to store
    or transform the result as plain dicts when needed.
    """
    votes: List[MultiAgentVote] = []
    for cand in candidates:
        votes.append(
            MultiAgentVote(
                candidate_id=cand.get("id"),
                score=float(cand.get("score", 0.0)),
                rationale=str(cand.get("rationale", "")),
            )
        )

    return MultiAgentCouncilResult(
        selected_id=winner.get("id"),
        selected_score=float(winner.get("score", 0.0)),
        votes=votes,
    )


# =============================================================================
# 3. MULTI-AGENT ORCHESTRATOR (QA COUNCIL, META-LEVEL)
# =============================================================================


@dataclass
class MultiAgentOrchestrator:
    """
    Multi-agent meta-orchestrator.

    This sits above L1–L5 and coordinates agent graphs, but does NOT:
        • call tools/LLMs
        • mutate state directly
        • own safety/policy
        • implement workflow phases

    L3 orchestrators pass:
        - graph: AgentGraph (e.g., COUNCIL_OF_QA)
        - state_adapter: StateAdapter (L4), used only via .state to
          read the current state; L3 is responsible for applying any
          patches via StatePatch.

    Typical usage from L3:

        ma = MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=adapter)
        council_patch = ma.dispatch_for_qa(state, plan)
        for key, value in council_patch.items():
            state_adapter.apply_patch(StatePatch(key=key, value=value))
    """

    graph: AgentGraph
    state_adapter: Any  # Typed as Any to avoid import cycles; must expose .state

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------

    def _build_synthetic_message(self, plan: Any) -> Dict[str, Any]:
        """
        Build a synthetic "message" capturing the QA objective for
        traceability and prompt-layer context.

        This does not call any LLM; it simply encodes the intent.
        """
        if isinstance(plan, dict):
            objective = str(plan.get("objective", "") or "")
            severity = str(plan.get("severity", "normal") or "")
        else:
            objective = str(getattr(plan, "objective", "") or "")
            severity = str(getattr(plan, "severity", "normal") or "")

        return {
            "role": "system",
            "content": (
                f"QA council evaluation for objective: {objective or 'unspecified-objective'}; "
                f"severity: {severity or 'normal'}"
            ),
        }

    def _plan_to_dict(self, plan: Any) -> Dict[str, Any]:
        """
        Normalize a plan object into a dict for inspection. This function
        is defensive and safe to call on PlanObject or plain dicts.
        """
        if hasattr(plan, "to_dict"):
            return plan.to_dict()  # type: ignore[return-value]
        if isinstance(plan, dict):
            return dict(plan)
        # Fallback: attempt best-effort conversion via vars()
        try:
            return dict(vars(plan))
        except TypeError:
            return {"repr": repr(plan)}

    # -------------------------------------------------------------------------
    # QA COUNCIL ENTRYPOINT
    # -------------------------------------------------------------------------

    def dispatch_for_qa(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """
        Execute a QA council pass *at the meta layer*:

            • Build a synthetic "message" capturing the QA objective.
            • Generate candidates for each QA agent (score + rationale).
            • Choose a winner via deterministic_vote.
            • Build a MultiAgentCouncilResult and serialize it.
            • Return a dict of fields to patch into state via L4
              (e.g., under key "multi_agent").

        IMPORTANT:

            • This method does NOT mutate state_adapter internally.
            • L3 remains responsible for applying patches via StatePatch.
            • No LLMs/tools/SDK calls are performed here.
        """
        synthetic_message = self._build_synthetic_message(plan)
        plan_dict = self._plan_to_dict(plan)

        # Build candidates for QA council members
        candidates: List[Dict[str, Any]] = []
        for node in self.graph.nodes:
            if node.role != AgentRole.QA:
                continue
            cand = _qa_candidate_scores(plan_dict, state, node.config)
            candidates.append(cand)

        winner = deterministic_vote(candidates)
        council_result = build_council_result(candidates, winner)

        multi_agent_block: Dict[str, Any] = {
            "last_message": synthetic_message,
            "sender": "orchestrator",
            "recipient": "qa_council",
            "graph_summary": summarize_graph(self.graph),
            "candidates": candidates,
            "winner": winner,
            "council_result": council_result.to_dict(),
        }

        # Return fields to be patched into L4 state.
        # L3 will typically do:
        #   StatePatch(key="multi_agent", value=multi_agent_block)
        return {
            "multi_agent": multi_agent_block,
        }

    # -------------------------------------------------------------------------
    # EXTENSION HOOKS (NO-OP BY DEFAULT)
    # -------------------------------------------------------------------------

    def build_patch_for_block(self, block_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience helper: construct a dict suitable for use as a
        StatePatch value, allowing L3 to decide the key.

        Example:

            patch_dict = ma.build_patch_for_block("multi_agent", {...})
            state_adapter.apply_patch(StatePatch(key="multi_agent",
                                                 value=patch_dict["multi_agent"]))
        """
        return {str(block_name): payload}

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a pure-data view of the orchestrator configuration (graph
        + minimal state metadata). This is useful for debugging and
        serialization, but does not include live state.
        """
        return {
            "graph": summarize_graph(self.graph),
            "has_state_adapter": self.state_adapter is not None,
        }
