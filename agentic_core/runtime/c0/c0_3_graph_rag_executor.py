"""C0.3 Graph-RAG Executor — generic glue layer between RouteContract and
run_graph_traverse().

Responsibilities (single-responsibility, no app_id branching):
  1. Check whether the route carries an active graph traversal policy.
  2. Resolve the graph adapter via adapter_registry.resolve_graph_adapter().
  3. Build a GraphTraverseInput from the route policy + hydrated candidates.
  4. Call run_graph_traverse() and return the GraphExpandedEvidencePool.
  5. Map the pool onto graph_rag_extension fields so callers can augment
     the FinalEvidenceContract without knowing C0.3 internals.

Never called for terminal/cache routes (R1A, R1B, R5).
Never called when graph_traverse_policy is None or is_active=False.
Never calls run_graph_traverse() unless the policy is fully live-wired.

W4: chroma-graphrag-core-wiring-gaps-b3f7a1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Sequence

from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
    AdapterResolutionStatus,
    resolve_graph_adapter,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
    AclStatus,
    FreshnessClass,
    GraphExpandedEvidencePool,
    GraphTraverseInput,
    HydratedEvidence,
    RetrievalLane,
    SupportTarget,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import run_graph_traverse

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Graph-RAG execution result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphRagResult:
    """Result of a C0.3 graph traversal attempt.

    On success:  executed=True, pool carries the full GraphExpandedEvidencePool.
    On skip:     executed=False, skip_reason explains why traversal was not run.
    On failure:  executed=False, error carries the exception message.

    callers MUST check ``executed`` before consuming ``pool``.
    """

    executed: bool
    pool: Optional[GraphExpandedEvidencePool] = None
    skip_reason: str = ""
    error: str = ""

    @property
    def nodes_accepted(self) -> int:
        if self.pool is None:
            return 0
        return len(self.pool.accepted_graph_neighbors)

    @property
    def nodes_rejected(self) -> int:
        if self.pool is None:
            return 0
        return len(self.pool.rejected_graph_neighbors)

    @property
    def contradiction_count(self) -> int:
        if self.pool is None:
            return 0
        return len(self.pool.contradiction_candidates)

    @property
    def manifest_hash(self) -> str:
        if self.pool is None:
            return ""
        return self.pool.graph_traversal_manifest.manifest_hash


# ---------------------------------------------------------------------------
# GraphTraverseInput builder helpers
# ---------------------------------------------------------------------------


def _hydrate_candidates_from_evidence_items(
    evidence_items: Sequence[object],
) -> tuple[HydratedEvidence, ...]:
    """Build minimal HydratedEvidence stubs from FinalEvidenceContract evidence_items.

    In a fully realised system the evidence items would carry all hydration
    metadata.  For the W4 wiring layer we build conservative stubs that satisfy
    the HydratedEvidence contract so run_graph_traverse() can proceed without
    any app-specific hydration logic in core.

    Each stub carries:
      - evidence_id / source_id  from the EvidenceItem fields
      - retrieval_lane = GRAPH_SEED  (canonical C0.3 graph seeding lane)
      - acl_status = CLEARED  (upstream ACL is pre-cleared before C0 entry)
      - candidate_text_or_payload = content_snippet
    """
    stubs: list[HydratedEvidence] = []
    for raw in evidence_items:
        ev_id = getattr(raw, "evidence_id", None) or str(id(raw))
        src_id = getattr(raw, "source_ref", ev_id)
        text = getattr(raw, "content_snippet", "") or ""
        stubs.append(
            HydratedEvidence(
                evidence_id=ev_id,
                source_id=src_id,
                retrieval_lane=RetrievalLane.GRAPH_SEED,
                acl_status=AclStatus.CLEARED,
                candidate_text_or_payload=text,
            )
        )
    return tuple(stubs)


def _build_traverse_input(
    route: RouteContract,
    policy: GraphTraversePolicy,
    hydrated_candidates: tuple[HydratedEvidence, ...],
) -> GraphTraverseInput:
    """Construct a GraphTraverseInput from a live GraphTraversePolicy.

    All limit fields come from the policy; identity fields from RouteContract.
    The caller is responsible for ensuring policy.is_active == True before
    calling this function.
    """
    policy_hash = getattr(route, "signature", "") or route.route_id
    blueprint_hash = route.route_policy_ref or route.route_id
    return GraphTraverseInput(
        route_id=route.route_id,
        route_replay_key=route.replay_key or route.route_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        support_target=SupportTarget.CLAIM_CHECK,
        freshness_class=FreshnessClass.CURRENT,
        max_hops=policy.max_hops,
        max_nodes=policy.max_nodes if policy.max_nodes > 0 else 200,
        max_edges=policy.max_edges if policy.max_edges > 0 else 400,
        allowed_relation_types=policy.allowed_relation_types,
        hydrated_candidates=hydrated_candidates,
    )


# ---------------------------------------------------------------------------
# Public executor entry-point
# ---------------------------------------------------------------------------


def maybe_run_graph_rag(
    route: RouteContract,
    evidence_items: Sequence[object],
) -> GraphRagResult:
    """Conditionally execute C0.3 graph traversal for a grounded route.

    Decision tree:
      1. No policy on route                          → skip (NOT_CONFIGURED)
      2. Policy present but not active               → skip (DEFERRED)
      3. No adapter ref in policy                    → skip (NO_ADAPTER_REF)
      4. Adapter resolution fails                    → skip (ADAPTER_RESOLUTION_FAILED)
      5. No hydrated candidates to walk from         → skip (NO_CANDIDATES)
      6. run_graph_traverse() raises                 → skip (EXECUTION_ERROR)
      7. Success                                     → executed=True, pool populated

    Always fail-soft — callers receive a GraphRagResult and decide whether to
    propagate errors or proceed with plain evidence.

    Args:
        route:          Frozen RouteContract from L0.
        evidence_items: Sequence of EvidenceItem (or any object with
                        ``evidence_id``, ``source_ref``, ``content_snippet``).

    Returns:
        GraphRagResult with executed=True on success, executed=False otherwise.
    """
    policy: Optional[GraphTraversePolicy] = route.graph_traverse_policy

    # Step 1 — no policy
    if policy is None:
        _LOGGER.debug(
            "maybe_run_graph_rag: route=%s no graph_traverse_policy → skip",
            route.route_id,
        )
        return GraphRagResult(executed=False, skip_reason="NOT_CONFIGURED")

    # Step 2 — policy not active (live_wiring_deferred or expansion disabled)
    if not policy.is_active:
        _LOGGER.debug(
            "maybe_run_graph_rag: route=%s policy present but is_active=False"
            " (graph_expansion_allowed=%s live_wiring_deferred=%s) → skip",
            route.route_id,
            policy.graph_expansion_allowed,
            policy.live_wiring_deferred,
        )
        return GraphRagResult(executed=False, skip_reason="DEFERRED")

    # Step 3 — no adapter ref
    adapter_ref = policy.graph_adapter_ref.strip() if policy.graph_adapter_ref else ""
    if not adapter_ref:
        _LOGGER.warning(
            "maybe_run_graph_rag: route=%s policy is_active=True but"
            " graph_adapter_ref is empty → skip",
            route.route_id,
        )
        return GraphRagResult(
            executed=False,
            skip_reason="NO_ADAPTER_REF",
            error="graph_traverse_policy.graph_adapter_ref is empty",
        )

    # Step 4 — resolve adapter
    resolution = resolve_graph_adapter(adapter_ref)
    if resolution.status != AdapterResolutionStatus.RESOLVED:
        _LOGGER.warning(
            "maybe_run_graph_rag: route=%s adapter_ref=%r resolution_status=%s"
            " reason=%s → skip",
            route.route_id,
            adapter_ref,
            resolution.status,
            resolution.reason,
        )
        return GraphRagResult(
            executed=False,
            skip_reason="ADAPTER_RESOLUTION_FAILED",
            error=f"{resolution.status}: {resolution.reason}",
        )

    adapter = resolution.adapter

    # Step 5 — build hydrated candidates
    hydrated = _hydrate_candidates_from_evidence_items(evidence_items)
    if not hydrated:
        _LOGGER.info(
            "maybe_run_graph_rag: route=%s no evidence items to hydrate → skip",
            route.route_id,
        )
        return GraphRagResult(executed=False, skip_reason="NO_CANDIDATES")

    # Step 6 — build input + run traversal
    try:
        traverse_input = _build_traverse_input(route, policy, hydrated)
        pool = run_graph_traverse(traverse_input, adapter)
        _LOGGER.info(
            "maybe_run_graph_rag: route=%s traversal complete"
            " nodes_accepted=%d nodes_rejected=%d contradictions=%d"
            " manifest_hash=%s",
            route.route_id,
            len(pool.accepted_graph_neighbors),
            len(pool.rejected_graph_neighbors),
            len(pool.contradiction_candidates),
            pool.graph_traversal_manifest.manifest_hash,
        )
        return GraphRagResult(executed=True, pool=pool)
    except Exception as exc:  # guardian: allow-broad-exception -- run_graph_traverse may raise from adapter code outside core
        _LOGGER.error(
            "maybe_run_graph_rag: route=%s traversal raised %s: %s",
            route.route_id,
            type(exc).__name__,
            exc,
        )
        return GraphRagResult(
            executed=False,
            skip_reason="EXECUTION_ERROR",
            error=f"{type(exc).__name__}: {exc}",
        )


__all__ = [
    "GraphRagResult",
    "maybe_run_graph_rag",
]
