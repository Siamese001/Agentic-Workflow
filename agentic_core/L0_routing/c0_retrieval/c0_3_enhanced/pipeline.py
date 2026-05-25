"""Phase 3 — main C0.3 orchestration: ``run_graph_traverse``.

Stages (line-for-line with the spec):
  1. validate_input
  2. extract_anchors
  3. resolve_anchors
  4. build_traversal_plan
  5. bounded_graph_walk
  6. gate_node_edge
  7. accept_reject_flag
  8. build_output_pool
  9. build_manifest
 10. emit_otel_spans

The function returns a fully-formed ``GraphExpandedEvidencePool`` ready for
C0.4. It never mutates inputs and never opens a SQLite connection.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import Mapping, Sequence

from .adapter import (
    AmbiguousAnchorResolution,
    GraphAdapterHealth,
    GraphNeighbor,
    GraphTraversalAdapter,
    ProjectionManifest,
    UnresolvedAnchorResolution,
)
from .contracts import (
    AcceptedGraphNeighbor,
    AnchorCandidate,
    AnchorCandidateSet,
    AnchorType,
    ContradictionCandidate,
    ContradictionType,
    FreshnessClass,
    FreshnessStatus,
    GapFinding,
    GapType,
    GraphExpandedEvidencePool,
    GraphTraversalManifest,
    GraphTraversalPlan,
    GraphTraverseInput,
    HydratedEvidence,
    InstructionPayloadFlag,
    RejectedGraphNeighbor,
    RejectionReason,
    ResolvedAnchorSet,
    ResolvedGraphAnchor,
    SupersessionCandidate,
    SupportTarget,
    compute_manifest_hash,
)
from .gates import GateName, apply_all_gates
from .otel import C0GraphSpan, GraphSpanRecorder, NullSpanRecorder
from .plan import build_traversal_plan
from .security import quarantine_neighbor_payload


# ---------------------------------------------------------------------------
# Stage 1 — validate_input
# ---------------------------------------------------------------------------


def _validate_input(inp: GraphTraverseInput, adapter: GraphTraversalAdapter) -> None:
    # Field-level validation already happened in __post_init__. Add adapter
    # health + projection currency cross-checks here.
    health: GraphAdapterHealth = adapter.health_check()
    if not health.healthy:
        raise RuntimeError(
            f"GraphTraversalAdapter unhealthy: backend={health.backend} err={health.last_error}"
        )


# ---------------------------------------------------------------------------
# Stage 2 — extract_anchors
# ---------------------------------------------------------------------------


def _extract_anchors(inp: GraphTraverseInput) -> AnchorCandidateSet:
    candidates: list[AnchorCandidate] = []
    unresolved: list[AnchorCandidate] = []
    for ev in inp.hydrated_candidates:
        # 1. exact ID hits (highest precedence, confidence 0.85)
        for ident in ev.extracted_ids:
            if ident.strip():
                candidates.append(
                    AnchorCandidate(
                        anchor_value=ident.strip(),
                        anchor_type=AnchorType.UNKNOWN,
                        original_evidence_id=ev.evidence_id,
                        hint_source_id=ev.source_id,
                        hint_source_version=ev.source_version,
                        hint_file_path=ev.file_path_or_doc_id,
                        confidence=0.85,
                    )
                )
        # 2. symbols (code-leaning) — confidence 0.7
        for sym in ev.extracted_symbols:
            if sym.strip():
                candidates.append(
                    AnchorCandidate(
                        anchor_value=sym.strip(),
                        anchor_type=AnchorType.CODE_SYMBOL,
                        original_evidence_id=ev.evidence_id,
                        hint_source_id=ev.source_id,
                        hint_source_version=ev.source_version,
                        hint_file_path=ev.file_path_or_doc_id,
                        confidence=0.7,
                    )
                )
        # 3. entities (docs-leaning) — confidence 0.55, NOT every noun
        for ent in ev.extracted_entities:
            if ent.strip() and len(ent.strip()) >= 3:
                candidates.append(
                    AnchorCandidate(
                        anchor_value=ent.strip(),
                        anchor_type=AnchorType.UNKNOWN,
                        original_evidence_id=ev.evidence_id,
                        hint_source_id=ev.source_id,
                        hint_source_version=ev.source_version,
                        hint_file_path=ev.file_path_or_doc_id,
                        confidence=0.55,
                    )
                )
        # 4. file_path_or_doc_id — always include if present
        if ev.file_path_or_doc_id:
            candidates.append(
                AnchorCandidate(
                    anchor_value=ev.file_path_or_doc_id,
                    anchor_type=AnchorType.DOCUMENT,
                    original_evidence_id=ev.evidence_id,
                    hint_source_id=ev.source_id,
                    hint_source_version=ev.source_version,
                    hint_file_path=ev.file_path_or_doc_id,
                    confidence=0.6,
                )
            )
        # 5. source_id fallback if NOTHING else extracted
        if (
            not ev.extracted_ids
            and not ev.extracted_symbols
            and not ev.extracted_entities
            and not ev.file_path_or_doc_id
        ):
            unresolved.append(
                AnchorCandidate(
                    anchor_value=ev.source_id,
                    anchor_type=AnchorType.DOCUMENT,
                    original_evidence_id=ev.evidence_id,
                    hint_source_id=ev.source_id,
                    hint_source_version=ev.source_version,
                    confidence=0.3,
                )
            )
            candidates.append(unresolved[-1])
    return AnchorCandidateSet(
        candidates=tuple(candidates),
        unresolved_anchor_candidates=tuple(unresolved),
    )


# ---------------------------------------------------------------------------
# Stage 3 — resolve_anchors
# ---------------------------------------------------------------------------


def _resolve_anchors(
    candidates: AnchorCandidateSet,
    adapter: GraphTraversalAdapter,
    inp: GraphTraverseInput,
) -> ResolvedAnchorSet:
    resolved: list[ResolvedGraphAnchor] = []
    ambiguous: list[AnchorCandidate] = []
    unresolved: list[AnchorCandidate] = list(candidates.unresolved_anchor_candidates)
    scope = {
        "tenant_scope": inp.tenant_scope,
        "region_scope": inp.region_scope,
        "data_class_scope": inp.data_class_scope,
        "acl_scope": inp.acl_scope,
    }
    seen_resolved: set[str] = set()
    for cand in candidates.candidates:
        result = adapter.resolve_anchor(cand, scope)
        if isinstance(result, ResolvedGraphAnchor):
            if result.resolved_node_id in seen_resolved:
                continue
            seen_resolved.add(result.resolved_node_id)
            resolved.append(result)
        elif isinstance(result, AmbiguousAnchorResolution):
            ambiguous.append(cand)
        elif isinstance(result, UnresolvedAnchorResolution):
            unresolved.append(cand)
    return ResolvedAnchorSet(
        resolved=tuple(resolved),
        ambiguous=tuple(ambiguous),
        unresolved=tuple(unresolved),
    )


# ---------------------------------------------------------------------------
# Stage 5 — bounded_graph_walk
# ---------------------------------------------------------------------------


@dataclass
class _WalkResult:
    accepted: list[AcceptedGraphNeighbor]
    rejected: list[RejectedGraphNeighbor]
    nodes_seen: int
    edges_seen: int
    hops_used: int
    nodes_accepted_set: set[str]
    edges_seen_set: set[tuple[str, str, str]]
    blocked_relation_types_seen: set[str]
    instruction_flags: list[InstructionPayloadFlag]


def _bounded_graph_walk(
    *,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    adapter: GraphTraversalAdapter,
    resolved: ResolvedAnchorSet,
    pm: ProjectionManifest,
    span_recorder: GraphSpanRecorder,
) -> _WalkResult:
    accepted: list[AcceptedGraphNeighbor] = []
    rejected: list[RejectedGraphNeighbor] = []
    instruction_flags: list[InstructionPayloadFlag] = []
    nodes_accepted: set[str] = set()
    edges_seen: set[tuple[str, str, str]] = set()
    blocked_relation_types_seen: set[str] = set()
    nodes_seen = 0
    edges_seen_count = 0
    hops_used = 0

    walk_span = span_recorder.start(
        C0GraphSpan.TRAVERSE,
        attributes={
            "graph_source": pm.graph_source,
            "graph_snapshot_id": pm.snapshot_pointer,
            "projection_version": pm.projection_version,
            "start_node_count": len(resolved.resolved),
        },
    )

    if inp.max_hops <= 0 or not resolved.resolved:
        span_recorder.end(
            walk_span,
            attributes={
                "nodes_seen": 0,
                "edges_seen": 0,
                "hops_used": 0,
            },
        )
        return _WalkResult(
            accepted=[],
            rejected=[],
            nodes_seen=0,
            edges_seen=0,
            hops_used=0,
            nodes_accepted_set=set(),
            edges_seen_set=edges_seen,
            blocked_relation_types_seen=blocked_relation_types_seen,
            instruction_flags=[],
        )

    # frontier: (node_id, depth, relation_path_so_far)
    frontier: deque[tuple[str, int, tuple[str, ...]]] = deque()
    seen_nodes: set[str] = set()
    for anchor in resolved.resolved:
        seen_nodes.add(anchor.resolved_node_id)
        frontier.append((anchor.resolved_node_id, 0, ()))

    deadline_ns = time.perf_counter_ns() + inp.max_latency_ms * 1_000_000

    # Adapter is asked WITHOUT a relation filter so disallowed/non-priority
    # relations are still surfaced and the gate layer can:
    #   (a) reject them with the precise gate name (G6),
    #   (b) populate ``blocked_relation_types_seen`` in the manifest.
    # The plan still bounds traversal via gate G6/G8/G9.
    relation_filter: tuple[str, ...] = ()
    per_anchor_limit = max(1, plan.max_neighbors_by_anchor)

    while frontier:  # guardian: allow-retry-without-backoff -- BFS frontier; deadline/max_nodes are bounds, not unbounded retry
        if time.perf_counter_ns() > deadline_ns:
            break
        if nodes_seen >= inp.max_nodes:
            break
        if edges_seen_count >= inp.max_edges:
            break

        cur_id, depth, rel_path = frontier.popleft()
        if depth >= inp.max_hops:
            continue
        hops_used = max(hops_used, depth + 1)

        try:
            neighbors = adapter.get_neighbors(
                cur_id,
                relation_filter,
                {
                    "tenant_scope": inp.tenant_scope,
                    "region_scope": inp.region_scope,
                },
                per_anchor_limit,
            )
        except Exception as exc:  # guardian: allow-broad -- adapter failure must not crash C0.3  # guardian: allow-retry-without-backoff -- BFS frontier drain; deadline/max bounds are the backoff
            rejected.append(
                RejectedGraphNeighbor(
                    neighbor_id=f"<adapter-error:{cur_id}>",
                    relation_path=rel_path or ("?",),
                    rejection_reason=RejectionReason.GRAPH_SOURCE_BLOCKED,
                    failed_gate="adapter_error",
                    hop_distance=depth + 1,
                    source_id=cur_id,
                    acl_status="unknown",
                    freshness_status=FreshnessStatus.UNKNOWN,
                )
            )
            del exc
            continue

        for raw_n in neighbors:
            if nodes_seen >= inp.max_nodes:
                break
            if edges_seen_count >= inp.max_edges:
                break
            edge_key = (cur_id, raw_n.node_id, raw_n.relation_type)
            if edge_key in edges_seen:
                continue
            edges_seen.add(edge_key)
            edges_seen_count += 1
            nodes_seen += 1
            full_rel_path = rel_path + (raw_n.relation_type,)
            new_hop = depth + 1
            neighbor = GraphNeighbor(
                node_id=raw_n.node_id,
                node_type=raw_n.node_type,
                source_id=raw_n.source_id,
                source_type=raw_n.source_type,
                source_version=raw_n.source_version,
                relation_type=raw_n.relation_type,
                relation_path=full_rel_path,
                hop_distance=new_hop,
                tenant=raw_n.tenant,
                region=raw_n.region,
                data_class=raw_n.data_class,
                acl_status=raw_n.acl_status,
                freshness_status=raw_n.freshness_status,
                confidence=raw_n.confidence,
                lineage_refs=raw_n.lineage_refs,
                span_ref=raw_n.span_ref,
                graph_source=raw_n.graph_source,
                projection_version=raw_n.projection_version,
                snapshot_pointer=raw_n.snapshot_pointer,
                payload_preview=raw_n.payload_preview,
                is_projected=raw_n.is_projected,
                authority_class=raw_n.authority_class,
            )

            # Phase 6 — instruction-payload quarantine. We attempt detection
            # FIRST so that even an otherwise-valid neighbor is excluded
            # from prompt-eligible context.
            ip_flag = quarantine_neighbor_payload(neighbor, support_target=inp.support_target)
            if ip_flag is not None:
                instruction_flags.append(ip_flag)
                if not ip_flag.allowed_for_security_analysis:
                    rejected.append(
                        RejectedGraphNeighbor(
                            neighbor_id=neighbor.node_id,
                            relation_path=full_rel_path,
                            rejection_reason=RejectionReason.INSTRUCTION_LIKE_PAYLOAD,
                            failed_gate="C0.3.SECURITY_QUARANTINE",
                            hop_distance=new_hop,
                            source_id=neighbor.source_id,
                            acl_status=neighbor.acl_status,
                            freshness_status=neighbor.freshness_status,
                        )
                    )
                    continue

            ctx = {
                "seen_node_ids": seen_nodes,
                "projection_manifest": pm,
                "flag_categories": (),
            }
            decision = apply_all_gates(neighbor, inp, plan, ctx)
            if not decision.accepted:
                if decision.rejection_reason == RejectionReason.RELATION_TYPE_NOT_ALLOWED:
                    blocked_relation_types_seen.add(neighbor.relation_type)
                rejected.append(
                    RejectedGraphNeighbor(
                        neighbor_id=neighbor.node_id,
                        relation_path=full_rel_path,
                        rejection_reason=decision.rejection_reason or RejectionReason.SUPPORT_TARGET_MISMATCH,
                        failed_gate=decision.gate.value if decision.gate else "?",
                        hop_distance=new_hop,
                        source_id=neighbor.source_id,
                        acl_status=neighbor.acl_status,
                        freshness_status=neighbor.freshness_status,
                    )
                )
                continue

            inclusion_reason = _inclusion_reason_for(neighbor, plan)
            support_contribution = _support_contribution_for(neighbor, plan)
            authority_contribution = neighbor.authority_class or "default"
            flag_categories = decision.flag_categories or ()
            flag_categories = _augment_flag_categories(neighbor, plan, flag_categories)

            accepted_neighbor = AcceptedGraphNeighbor(
                neighbor_id=neighbor.node_id,
                neighbor_type=neighbor.node_type,
                source_id=neighbor.source_id,
                source_type=neighbor.source_type,
                source_version=neighbor.source_version,
                relation_path=full_rel_path,
                relation_types=tuple(dict.fromkeys(full_rel_path)),
                hop_distance=new_hop,
                inclusion_reason=inclusion_reason,
                support_contribution=support_contribution,
                authority_contribution=authority_contribution,
                freshness_status=neighbor.freshness_status,
                acl_status=neighbor.acl_status,
                confidence=neighbor.confidence,
                lineage_refs=neighbor.lineage_refs,
                graph_source=neighbor.graph_source,
                span_ref=neighbor.span_ref,
                projection_version=neighbor.projection_version,
                snapshot_pointer=neighbor.snapshot_pointer,
                flag_categories=tuple(flag_categories),
                payload_preview=neighbor.payload_preview,
                is_projected=neighbor.is_projected,
            )
            accepted.append(accepted_neighbor)
            nodes_accepted.add(neighbor.node_id)

            # Continue traversal from accepted neighbor unless cycle
            if neighbor.node_id not in seen_nodes:
                seen_nodes.add(neighbor.node_id)
                frontier.append((neighbor.node_id, new_hop, full_rel_path))

    span_recorder.end(
        walk_span,
        attributes={
            "nodes_seen": nodes_seen,
            "edges_seen": edges_seen_count,
            "hops_used": hops_used,
            "latency_ms": int(
                (time.perf_counter_ns() - (deadline_ns - inp.max_latency_ms * 1_000_000)) / 1_000_000
            ),
        },
    )
    return _WalkResult(
        accepted=accepted,
        rejected=rejected,
        nodes_seen=nodes_seen,
        edges_seen=edges_seen_count,
        hops_used=hops_used,
        nodes_accepted_set=nodes_accepted,
        edges_seen_set=edges_seen,
        blocked_relation_types_seen=blocked_relation_types_seen,
        instruction_flags=instruction_flags,
    )


def _inclusion_reason_for(neighbor: GraphNeighbor, plan: GraphTraversalPlan) -> str:
    if neighbor.relation_type == "contradicts" and plan.contradiction_scan_enabled:
        return "contradiction surface preserved"
    if neighbor.relation_type in ("supersedes", "superseded_by") and plan.supersession_scan_enabled:
        return "supersession surface preserved"
    if neighbor.relation_type in ("defines", "implements"):
        return "authoritative definition / implementation"
    if neighbor.relation_type in ("imports", "calls", "depends_on", "depended_on_by"):
        return "dependency context"
    if neighbor.relation_type in ("owns", "owned_by"):
        return "ownership context"
    if neighbor.relation_type in ("observed_in", "trace", "deployment", "ticket", "remediated_by"):
        return "runtime / incident context"
    if neighbor.relation_type in ("derived_from", "source_version", "source_authority", "approved_by"):
        return "source lineage / authority"
    if neighbor.relation_type in ("references", "parent_of", "child_of"):
        return "structural reference"
    if neighbor.relation_type == "governed_by":
        return "policy / version authority"
    return f"relation '{neighbor.relation_type}' supports target"


def _support_contribution_for(neighbor: GraphNeighbor, plan: GraphTraversalPlan) -> str:
    primary = plan.replay_metadata.get("primary_relations", ())
    if not isinstance(primary, (list, tuple)):
        primary = ()
    if neighbor.relation_type in primary:
        return "primary"
    if neighbor.relation_type in plan.relation_priority_order:
        return "secondary"
    return "background"


def _augment_flag_categories(
    neighbor: GraphNeighbor,
    plan: GraphTraversalPlan,
    existing: Sequence[str],
) -> tuple[str, ...]:
    out: list[str] = list(existing)
    rel = neighbor.relation_type
    if rel == "contradicts":
        out.append("contradiction_candidate")
    if rel in ("supersedes", "superseded_by"):
        out.append("supersession_candidate")
    if rel in ("imports", "calls", "depends_on", "depended_on_by") and plan.dependency_scan_enabled:
        out.append("dependency_context")
    if rel in ("owns", "owned_by") and plan.owner_scan_enabled:
        out.append("ownership_context")
    if rel in ("observed_in", "trace", "deployment", "ticket", "remediated_by") and plan.runtime_scan_enabled:
        out.append("runtime_context")
    if rel in ("defines", "implements") and plan.definition_scan_enabled:
        out.append("implementation_context")
    if (
        rel in ("derived_from", "source_version", "source_authority", "approved_by")
        and plan.lineage_scan_enabled
    ):
        out.append("lineage_edge")
    if rel == "source_authority" and plan.source_authority_scan_enabled:
        out.append("source_authority_context")
    freshness_value = (
        neighbor.freshness_status.value
        if isinstance(neighbor.freshness_status, FreshnessStatus)
        else str(neighbor.freshness_status)
    )
    if freshness_value == FreshnessStatus.STALE.value:
        out.append("stale_candidate")
    # de-dup preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for item in out:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return tuple(deduped)


# ---------------------------------------------------------------------------
# Stage 6/7 helpers — buckets + contradictions
# ---------------------------------------------------------------------------


def _bucket_accepted(
    accepted: Sequence[AcceptedGraphNeighbor],
) -> dict[str, tuple[AcceptedGraphNeighbor, ...]]:
    buckets: dict[str, list[AcceptedGraphNeighbor]] = {
        "lineage": [],
        "dependency": [],
        "ownership": [],
        "source_authority": [],
        "implementation": [],
        "runtime": [],
        "prior_run": [],
    }
    for n in accepted:
        if "lineage_edge" in n.flag_categories:
            buckets["lineage"].append(n)
        if "dependency_context" in n.flag_categories:
            buckets["dependency"].append(n)
        if "ownership_context" in n.flag_categories:
            buckets["ownership"].append(n)
        if "source_authority_context" in n.flag_categories:
            buckets["source_authority"].append(n)
        if "implementation_context" in n.flag_categories:
            buckets["implementation"].append(n)
        if "runtime_context" in n.flag_categories:
            buckets["runtime"].append(n)
    # prior_run currently empty — placeholder for sealed-run / eval-bundle wiring
    return {k: tuple(v) for k, v in buckets.items()}


def _build_contradictions(
    accepted: Sequence[AcceptedGraphNeighbor],
    plan: GraphTraversalPlan,
) -> tuple[
    tuple[ContradictionCandidate, ...],
    tuple[SupersessionCandidate, ...],
]:
    contradictions: list[ContradictionCandidate] = []
    supersessions: list[SupersessionCandidate] = []
    if not plan.contradiction_scan_enabled and not plan.supersession_scan_enabled:
        return tuple(contradictions), tuple(supersessions)
    for n in accepted:
        rel = n.relation_path[-1] if n.relation_path else ""
        if rel == "contradicts" and plan.contradiction_scan_enabled:
            kind = _classify_contradiction(n)
            contradictions.append(
                ContradictionCandidate(
                    conflict_type=kind,
                    source_a=n.source_id,
                    source_b=n.lineage_refs[0] if n.lineage_refs else n.source_id,
                    relation_path=n.relation_path,
                    severity="medium",
                    confidence=n.confidence,
                    downstream_required_behavior="surface_caveat",
                    note=n.inclusion_reason,
                )
            )
        if rel == "supersedes" and plan.supersession_scan_enabled:
            supersessions.append(
                SupersessionCandidate(
                    superseded_source_id=(n.lineage_refs[0] if n.lineage_refs else n.source_id),
                    superseding_source_id=n.source_id,
                    relation_path=n.relation_path,
                    confidence=n.confidence,
                    reason=n.inclusion_reason,
                )
            )
        elif rel == "superseded_by" and plan.supersession_scan_enabled:
            supersessions.append(
                SupersessionCandidate(
                    superseded_source_id=n.source_id,
                    superseding_source_id=(n.lineage_refs[0] if n.lineage_refs else n.source_id),
                    relation_path=n.relation_path,
                    confidence=n.confidence,
                    reason=n.inclusion_reason,
                )
            )
    return tuple(contradictions), tuple(supersessions)


def _classify_contradiction(n: AcceptedGraphNeighbor) -> ContradictionType:
    src_type = (n.source_type or "").lower()
    if src_type in ("docs", "doc"):
        return ContradictionType.DOCS_VS_CODE
    if src_type == "code":
        return ContradictionType.DOCS_VS_CODE
    if src_type in ("logs", "trace", "runtime"):
        return ContradictionType.RUNTIME_VS_DESIGN
    if src_type == "policy":
        return ContradictionType.POLICY_VS_IMPLEMENTATION
    if "version" in (n.source_version or "").lower():
        return ContradictionType.VERSION
    return ContradictionType.SEMANTIC


def _build_gaps(
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    accepted: Sequence[AcceptedGraphNeighbor],
    resolved: ResolvedAnchorSet,
    pm: ProjectionManifest,
) -> tuple[GapFinding, ...]:
    gaps: list[GapFinding] = []
    has_owner = any("ownership_context" in n.flag_categories for n in accepted)
    has_runtime = any("runtime_context" in n.flag_categories for n in accepted)
    has_implementation = any("implementation_context" in n.flag_categories for n in accepted)
    has_lineage = any("lineage_edge" in n.flag_categories for n in accepted)

    target = inp.support_target.value if isinstance(inp.support_target, SupportTarget) else inp.support_target

    for ev in inp.hydrated_candidates:
        if not has_owner and plan.owner_scan_enabled:
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_OWNER,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters="No ownership/authority context found for this evidence",
                    severity="medium",
                    suggested_refine_tactic="resolve_owner_via_owns_relation",
                    can_answer_with_caveat=True,
                )
            )
        if (
            not has_runtime
            and plan.runtime_scan_enabled
            and target
            in (
                SupportTarget.INCIDENT_EVIDENCE.value,
                SupportTarget.ROOT_CAUSE_RANKING.value,
            )
        ):
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_RUNTIME_EVIDENCE,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters="Runtime/incident target lacks observed_in/trace edges",
                    severity="high",
                    suggested_refine_tactic="add_runtime_lane_or_widen_trace_window",
                    can_answer_with_caveat=False,
                )
            )
        if (
            not has_implementation
            and plan.definition_scan_enabled
            and target == SupportTarget.CODE_LOCATION.value
        ):
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_IMPLEMENTATION_LINK,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters="Code location lacks defines/implements edges",
                    severity="medium",
                    suggested_refine_tactic="resolve_symbol_to_module_or_class",
                    can_answer_with_caveat=True,
                )
            )
        if not has_lineage and plan.lineage_scan_enabled:
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_SOURCE_LINEAGE,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters="Cannot trace this evidence to canonical source",
                    severity="medium",
                    suggested_refine_tactic="follow_derived_from_chain",
                    can_answer_with_caveat=True,
                )
            )
        if ev.span_ref is None and ev.citation_anchor_status not in ("ok", None):
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_STABLE_CITATION_ANCHOR,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters="No span_ref / citation anchor for this evidence",
                    severity="medium",
                    suggested_refine_tactic="resolve_span_via_section_or_line_range",
                    can_answer_with_caveat=True,
                )
            )

    if pm.is_stale:
        for ev in inp.hydrated_candidates[:1]:  # one gap per stale projection
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_GRAPH_PROJECTION,
                    affected_evidence_id=ev.evidence_id,
                    why_it_matters=f"Projection stale: {pm.stale_reason or 'snapshot drift'}",
                    severity="high",
                    suggested_refine_tactic="rebuild_graphdb_projection",
                    can_answer_with_caveat=False,
                )
            )

    if resolved.unresolved:
        for cand in resolved.unresolved:
            gaps.append(
                GapFinding(
                    gap_type=GapType.MISSING_EXACT_SYMBOL_RESOLUTION,
                    affected_evidence_id=cand.original_evidence_id,
                    why_it_matters=f"Anchor '{cand.anchor_value}' did not resolve",
                    severity="low",
                    suggested_refine_tactic="broaden_anchor_search_or_tag_unknown",
                    can_answer_with_caveat=True,
                )
            )

    return tuple(gaps)


# ---------------------------------------------------------------------------
# Stage 9 — build_manifest
# ---------------------------------------------------------------------------


def _build_manifest(
    *,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    pm: ProjectionManifest,
    walk: _WalkResult,
    latency_ms: int,
    replay_seed: str,
) -> GraphTraversalManifest:
    payload = {
        "graph_source": pm.graph_source,
        "graph_snapshot_id": pm.snapshot_pointer,
        "projection_version": pm.projection_version,
        "traversal_policy_hash": inp.policy_hash,
        "allowed_relation_types_used": sorted(plan.allowed_relation_types),
        "blocked_relation_types_seen": sorted(walk.blocked_relation_types_seen),
        "hops_used": walk.hops_used,
        "nodes_seen": walk.nodes_seen,
        "edges_seen": walk.edges_seen,
        "nodes_accepted": len(walk.accepted),
        "edges_accepted": sum(len(n.relation_path) for n in walk.accepted),
        "nodes_rejected": len({r.neighbor_id for r in walk.rejected}),
        "edges_rejected": len(walk.rejected),
        "latency_ms": latency_ms,
        "budget_remaining": {
            "nodes": max(0, inp.max_nodes - walk.nodes_seen),
            "edges": max(0, inp.max_edges - walk.edges_seen),
            "hops": max(0, inp.max_hops - walk.hops_used),
            "latency_ms": max(0, inp.max_latency_ms - latency_ms),
        },
        "replay_seed": replay_seed,
    }
    manifest_hash = compute_manifest_hash(payload)
    return GraphTraversalManifest(
        graph_source=str(payload["graph_source"]),
        graph_snapshot_id=str(payload["graph_snapshot_id"]),
        projection_version=str(payload["projection_version"]),
        traversal_policy_hash=str(payload["traversal_policy_hash"]),
        allowed_relation_types_used=tuple(payload["allowed_relation_types_used"]),  # type: ignore[arg-type]
        blocked_relation_types_seen=tuple(payload["blocked_relation_types_seen"]),  # type: ignore[arg-type]
        hops_used=int(payload["hops_used"]),  # type: ignore[arg-type]
        nodes_seen=int(payload["nodes_seen"]),  # type: ignore[arg-type]
        edges_seen=int(payload["edges_seen"]),  # type: ignore[arg-type]
        nodes_accepted=int(payload["nodes_accepted"]),  # type: ignore[arg-type]
        edges_accepted=int(payload["edges_accepted"]),  # type: ignore[arg-type]
        nodes_rejected=int(payload["nodes_rejected"]),  # type: ignore[arg-type]
        edges_rejected=int(payload["edges_rejected"]),  # type: ignore[arg-type]
        latency_ms=int(payload["latency_ms"]),  # type: ignore[arg-type]
        budget_remaining=payload["budget_remaining"],  # type: ignore[arg-type]
        replay_seed=replay_seed,
        manifest_hash=manifest_hash,
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def run_graph_traverse(
    inp: GraphTraverseInput,
    adapter: GraphTraversalAdapter,
    *,
    span_recorder: GraphSpanRecorder | None = None,
) -> GraphExpandedEvidencePool:
    """Orchestrate C0.3 stages 1..10 and return ``GraphExpandedEvidencePool``.

    ``span_recorder`` defaults to ``NullSpanRecorder``, which captures spans
    in-memory and never imports an OTEL SDK at import time.
    """
    recorder = span_recorder or NullSpanRecorder()

    # Stage 1 — validate
    _validate_input(inp, adapter)
    pm = adapter.get_projection_manifest()

    # Stage 2 — extract
    extract_span = recorder.start(
        C0GraphSpan.ANCHOR_EXTRACT,
        attributes={
            "route_replay_key": inp.route_replay_key,
            "support_target": (
                inp.support_target.value
                if isinstance(inp.support_target, SupportTarget)
                else str(inp.support_target)
            ),
            "candidate_count": len(inp.hydrated_candidates),
        },
    )
    candidates = _extract_anchors(inp)
    recorder.end(
        extract_span,
        attributes={
            "extracted_anchor_count": len(candidates.candidates),
            "unresolved_anchor_count": len(candidates.unresolved_anchor_candidates),
        },
    )

    # Stage 3 — resolve
    resolve_span = recorder.start(
        C0GraphSpan.ANCHOR_RESOLVE,
        attributes={"graph_source": pm.graph_source},
    )
    resolved = _resolve_anchors(candidates, adapter, inp)
    recorder.end(
        resolve_span,
        attributes={
            "resolved_node_count": len(resolved.resolved),
            "ambiguous_node_count": len(resolved.ambiguous),
            "unresolved_node_count": len(resolved.unresolved),
        },
    )

    # Stage 4 — plan
    plan_span = recorder.start(C0GraphSpan.PLAN, attributes={})
    start_nodes = tuple(a.resolved_node_id for a in resolved.resolved)
    plan = build_traversal_plan(inp=inp, start_nodes=start_nodes, projection_version=pm.projection_version)
    recorder.end(
        plan_span,
        attributes={
            "allowed_relation_types": ",".join(plan.allowed_relation_types),
            "max_hops": inp.max_hops,
            "max_nodes": inp.max_nodes,
            "max_edges": inp.max_edges,
            "contradiction_scan_enabled": plan.contradiction_scan_enabled,
            "dependency_scan_enabled": plan.dependency_scan_enabled,
            "lineage_scan_enabled": plan.lineage_scan_enabled,
        },
    )

    # Stage 5 + 6 + 7 — bounded walk + gates + accept/reject + flags
    started = time.perf_counter_ns()
    walk = _bounded_graph_walk(
        inp=inp,
        plan=plan,
        adapter=adapter,
        resolved=resolved,
        pm=pm,
        span_recorder=recorder,
    )
    latency_ms = max(0, int((time.perf_counter_ns() - started) / 1_000_000))

    gate_span = recorder.start(C0GraphSpan.GATE, attributes={})
    acl_rej = sum(1 for r in walk.rejected if r.rejection_reason == RejectionReason.ACL_FAILED)
    fresh_rej = sum(
        1
        for r in walk.rejected
        if r.rejection_reason == RejectionReason.STALE
        or r.rejection_reason == RejectionReason.PROJECTION_STALE
    )
    relevance_rej = sum(
        1
        for r in walk.rejected
        if r.rejection_reason
        in (
            RejectionReason.INTERESTING_NOT_RELEVANT,
            RejectionReason.SUPPORT_TARGET_MISMATCH,
        )
    )
    relation_rej = sum(
        1 for r in walk.rejected if r.rejection_reason == RejectionReason.RELATION_TYPE_NOT_ALLOWED
    )
    recorder.end(
        gate_span,
        attributes={
            "nodes_accepted": len(walk.accepted),
            "nodes_rejected": len(walk.rejected),
            "edges_accepted": sum(len(n.relation_path) for n in walk.accepted),
            "edges_rejected": len(walk.rejected),
            "acl_rejections": acl_rej,
            "freshness_rejections": fresh_rej,
            "relevance_rejections": relevance_rej,
            "relation_rejections": relation_rej,
        },
    )

    # Stage 5b — contradictions / supersessions
    contradiction_span = recorder.start(C0GraphSpan.CONTRADICTION_SCAN, attributes={})
    contradictions, supersessions = _build_contradictions(walk.accepted, plan)
    recorder.end(
        contradiction_span,
        attributes={
            "contradiction_candidates": len(contradictions),
            "supersession_candidates": len(supersessions),
            "material_conflicts": sum(1 for c in contradictions if c.severity in ("high", "blocker")),
            "conflict_types": ",".join(
                sorted(
                    {
                        c.conflict_type.value
                        if isinstance(c.conflict_type, ContradictionType)
                        else str(c.conflict_type)
                        for c in contradictions
                    }
                )
            ),
        },
    )

    # Stage 8 — buckets + maps
    buckets = _bucket_accepted(walk.accepted)
    entity_map: dict[str, list[str]] = {}
    symbol_map: dict[str, list[str]] = {}
    relation_map: dict[str, list[str]] = {}
    for ev in inp.hydrated_candidates:
        if ev.extracted_entities:
            entity_map[ev.evidence_id] = list(ev.extracted_entities)
        if ev.extracted_symbols:
            symbol_map[ev.evidence_id] = list(ev.extracted_symbols)
    for n in walk.accepted:
        relation_map.setdefault(n.neighbor_id, []).extend(n.relation_path)

    gaps = _build_gaps(inp, plan, walk.accepted, resolved, pm)

    # Stage 9 — manifest
    manifest = _build_manifest(
        inp=inp,
        plan=plan,
        pm=pm,
        walk=walk,
        latency_ms=latency_ms,
        replay_seed=str(plan.replay_metadata.get("seed", "")),
    )

    # Stage 10 — emit span
    emit_span = recorder.start(C0GraphSpan.EMIT, attributes={})
    pool = GraphExpandedEvidencePool(
        original_candidates=tuple(inp.hydrated_candidates),
        accepted_graph_neighbors=tuple(walk.accepted),
        rejected_graph_neighbors=tuple(walk.rejected),
        entity_map={k: tuple(v) for k, v in entity_map.items()},
        symbol_map={k: tuple(v) for k, v in symbol_map.items()},
        relation_map={k: tuple(v) for k, v in relation_map.items()},
        lineage_edges=buckets["lineage"],
        dependency_context=buckets["dependency"],
        ownership_context=buckets["ownership"],
        source_authority_context=buckets["source_authority"],
        contradiction_candidates=contradictions,
        supersession_candidates=supersessions,
        implementation_context=buckets["implementation"],
        runtime_context=buckets["runtime"],
        prior_run_context=buckets["prior_run"],
        graph_traversal_manifest=manifest,
        instruction_payload_flags=tuple(walk.instruction_flags),
        gap_findings=gaps,
        unresolved_anchors=resolved.unresolved,
        ambiguous_anchors=resolved.ambiguous,
    )
    recorder.end(
        emit_span,
        attributes={
            "accepted_neighbor_count": len(pool.accepted_graph_neighbors),
            "rejected_neighbor_count": len(pool.rejected_graph_neighbors),
            "lineage_edge_count": len(pool.lineage_edges),
            "dependency_context_count": len(pool.dependency_context),
            "runtime_context_count": len(pool.runtime_context),
            "contradiction_count": len(pool.contradiction_candidates),
            "graph_manifest_hash": manifest.manifest_hash,
        },
    )
    return pool


__all__ = ["run_graph_traverse"]
