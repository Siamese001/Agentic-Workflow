"""C0.3 graph-skill hardening utilities.

Zero-loss overlay for augmented_skills_graph / master_skills_arsenal_ledger.
Adds deeper traversal receipts, precise edge typing, metric heterogeneity controls,
reverse traversal indexes, sibling rejection reasons, and frontier-depth summaries.
No existing skill rows, facts, graph nodes, or graph edges are removed.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Iterable

SOURCE_AUTHORITY = "augmented_skills_graph"
HARDENING_SCHEMA_VERSION = "c03_graph_skill_hardening_v2"
DEFAULT_MAX_DEPTH = 4
DEFAULT_NEIGHBOR_LIMIT = 24

EDGE_ALIASES = {
    "career_track_contains_pillar": "track_contains_pillar",
    "career_track_contains_epoch": "track_contains_epoch",
    "epoch_contains_pillar": "epoch_contains_pillar",
    "capability_domain_contains_skill": "domain_contains_skill",
    "skill_supported_by_fact": "skill_supported_by_fact",
    "employment_hosts_fact": "employment_hosts_fact",
    "employment_in_career_track": "employment_in_track",
    "skill_row_pillar_projection": "skill_projects_to_pillar",
    "skill_row_fact_id_links": "skill_links_fact_fallback",
}

METRIC_BUCKET_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("revenue_growth", ("revenue", "renewal", "pipeline", "sales", "gtm", "$")),
    ("cost_efficiency", ("cost", "savings", "expense", "efficiency", "automation", "manual")),
    ("latency_performance", ("latency", "throughput", "runtime", "speed", "cycle time")),
    ("quality_accuracy", ("accuracy", "quality", "defect", "error", "precision", "recall")),
    ("adoption_enablement", ("adoption", "enablement", "users", "nps", "self-service")),
    ("risk_governance", ("risk", "audit", "governance", "compliance", "control", "lineage")),
    ("scale_reliability", ("scale", "reliability", "slo", "uptime", "availability", "platform")),
    ("delivery_velocity", ("delivery", "launch", "implementation", "deployment", "release")),
    ("model_ai_outcome", ("llm", "model", "agent", "rag", "genai", "inference")),
    ("portfolio_operating", ("portfolio", "program", "operating", "stakeholder", "transformation")),
)

@dataclass(frozen=True)
class C03GraphHardeningPolicy:
    max_depth: int = DEFAULT_MAX_DEPTH
    neighbor_limit: int = DEFAULT_NEIGHBOR_LIMIT
    min_metric_bucket_count: int = 5
    max_same_metric_bucket_share: float = 0.34
    require_reverse_paths: bool = True
    require_rejected_siblings: bool = True
    require_frontier_receipts: bool = True

@dataclass
class GraphIndex:
    forward: dict[str, list[dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))
    reverse: dict[str, list[dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))
    rows_by_skill: dict[str, dict[str, Any]] = field(default_factory=dict)
    nodes_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    facts_by_skill: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    skills_by_fact: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    skills_by_pillar: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    skills_by_domain: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))


def _stable_digest(obj: Any) -> str:
    import json
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def infer_metric_bucket(text: str, fact_id: str = "") -> str:
    corpus = f"{text} {fact_id}".lower()
    for bucket, terms in METRIC_BUCKET_RULES:
        if any(term in corpus for term in terms):
            return bucket
    if any(ch.isdigit() for ch in corpus) or "%" in corpus:
        return "quantified_other"
    return "non_metric_context"


def canonical_edge(edge: dict[str, Any]) -> dict[str, Any]:
    et = str(edge.get("edge_type") or "").strip()
    src = str(edge.get("source_node_id") or edge.get("from") or "").strip()
    tgt = str(edge.get("target_node_id") or edge.get("to") or "").strip()
    role = EDGE_ALIASES.get(et, et or "unknown_edge")
    return {
        **edge,
        "edge_type": et,
        "source_node_id": src,
        "target_node_id": tgt,
        "edge_role": role,
        "edge_precision": edge.get("edge_precision") or "typed_directed_non_causal_unless_declared",
        "c03_traversal_eligible": bool(src and tgt),
        "c03_reverse_traversal_eligible": bool(src and tgt),
    }


def build_graph_index(graph: dict[str, Any]) -> GraphIndex:
    idx = GraphIndex()
    for node in graph.get("graph_nodes") or []:
        if isinstance(node, dict):
            nid = str(node.get("node_id") or node.get("id") or "").strip()
            if nid:
                idx.nodes_by_id[nid] = node
    for row in graph.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("skill_id") or "").strip()
        if not sid:
            continue
        idx.rows_by_skill[sid] = row
        pillar = str(row.get("pillar") or "").strip()
        if pillar:
            idx.skills_by_pillar[pillar].add(sid)
        for fid in row.get("fact_id_links") or []:
            fid = str(fid).strip()
            if fid:
                idx.facts_by_skill[sid].add(fid)
                idx.skills_by_fact[fid].add(sid)
    for raw in graph.get("graph_edges") or []:
        if not isinstance(raw, dict):
            continue
        e = canonical_edge(raw)
        src, tgt = e["source_node_id"], e["target_node_id"]
        if not src or not tgt:
            continue
        idx.forward[src].append(e)
        idx.reverse[tgt].append(e)
        if e["edge_type"] == "skill_supported_by_fact":
            idx.facts_by_skill[src].add(tgt)
            idx.skills_by_fact[tgt].add(src)
        if e["edge_type"] == "capability_domain_contains_skill":
            idx.skills_by_domain[src].add(tgt)
    return idx


def _edge_to_step(edge: dict[str, Any], direction: str) -> dict[str, Any]:
    if direction == "reverse":
        source = edge["target_node_id"]
        target = edge["source_node_id"]
    else:
        source = edge["source_node_id"]
        target = edge["target_node_id"]
    return {
        "edge_type": edge.get("edge_type"),
        "edge_role": edge.get("edge_role") or EDGE_ALIASES.get(str(edge.get("edge_type") or ""), "unknown_edge"),
        "direction": direction,
        "from": source,
        "to": target,
        "precision": edge.get("edge_precision") or "typed_directed",
        "note": edge.get("note") or edge.get("rationale") or "materialized graph edge",
    }


def traverse_between_nodes(index: GraphIndex, start: str, goals: Iterable[str], *, max_depth: int = DEFAULT_MAX_DEPTH, reverse: bool = False) -> list[list[dict[str, Any]]]:
    goal_set = {str(g) for g in goals if str(g).strip()}
    if not start or not goal_set:
        return []
    adjacency = index.reverse if reverse else index.forward
    direction = "reverse" if reverse else "forward"
    q: deque[tuple[str, list[dict[str, Any]]]] = deque([(start, [])])
    seen = {(start, 0)}
    out: list[list[dict[str, Any]]] = []
    while q:
        node, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for edge in adjacency.get(node, [])[:DEFAULT_NEIGHBOR_LIMIT]:
            nxt = edge["source_node_id"] if reverse else edge["target_node_id"]
            step = _edge_to_step(edge, direction)
            new_path = path + [step]
            if nxt in goal_set:
                out.append(new_path)
            key = (nxt, len(new_path))
            if key not in seen:
                seen.add(key)
                q.append((nxt, new_path))
    return out[:10]


def build_frontier_receipt(index: GraphIndex, roots: Iterable[str], *, max_depth: int = DEFAULT_MAX_DEPTH) -> dict[str, Any]:
    frontier_by_depth: dict[str, int] = {}
    visited: set[str] = set()
    frontier = {str(r) for r in roots if str(r).strip()}
    for depth in range(max_depth + 1):
        frontier -= visited
        frontier_by_depth[str(depth)] = len(frontier)
        visited |= frontier
        nxt: set[str] = set()
        for node in frontier:
            for edge in index.forward.get(node, [])[:DEFAULT_NEIGHBOR_LIMIT]:
                nxt.add(edge["target_node_id"])
        frontier = nxt
    return {
        "max_depth": max_depth,
        "frontier_size_by_depth": frontier_by_depth,
        "visited_node_count": len(visited),
        "receipt_type": "c03_traversal_sufficiency_frontier",
    }


def rejected_sibling_skills(index: GraphIndex, selected_skill_ids: Iterable[str], *, limit: int = 80) -> list[dict[str, Any]]:
    selected = {str(s) for s in selected_skill_ids if str(s).strip()}
    rejected: list[dict[str, Any]] = []
    for sid in sorted(selected):
        row = index.rows_by_skill.get(sid) or {}
        pillar = str(row.get("pillar") or "").strip()
        siblings = sorted(index.skills_by_pillar.get(pillar, set()) - selected)
        for sib in siblings[:8]:
            sib_row = index.rows_by_skill.get(sib) or {}
            reason = "lower_ranked_same_pillar_sibling"
            if str(sib_row.get("activation_status") or "").startswith("ACTIVE") is False:
                reason = f"inactive_or_unapproved:{sib_row.get('activation_status')}"
            elif not (sib_row.get("fact_id_links") or []):
                reason = "missing_fact_id_links"
            rejected.append({
                "selected_skill_id": sid,
                "rejected_skill_id": sib,
                "pillar": pillar,
                "reason": reason,
                "selected_metric_bucket": infer_metric_bucket(" ".join(map(str, row.get("allowed_phrases") or [])), sid),
                "rejected_metric_bucket": infer_metric_bucket(" ".join(map(str, sib_row.get("allowed_phrases") or [])), sib),
            })
            if len(rejected) >= limit:
                return rejected
    return rejected


def metric_heterogeneity_receipt(selected_facts: Iterable[dict[str, Any]], fact_claims: dict[str, str] | None = None) -> dict[str, Any]:
    claims = fact_claims or {}
    buckets: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    for f in selected_facts:
        fid = str(f.get("fact_id") or f.get("candidate_fact_id") or "").strip()
        text = str(f.get("claim_text") or claims.get(fid) or claims.get(fid.split("_metric_", 1)[0]) or "")
        bucket = infer_metric_bucket(text, fid)
        buckets[bucket] += 1
        rows.append({"fact_id": fid, "metric_bucket": bucket, "claim_excerpt": text[:180]})
    total = sum(buckets.values()) or 1
    largest_share = max((v / total for v in buckets.values()), default=0.0)
    return {
        "receipt_type": "c03_metric_heterogeneity",
        "metric_bucket_counts": dict(sorted(buckets.items())),
        "metric_bucket_count": len(buckets),
        "largest_metric_bucket_share": round(largest_share, 4),
        "selected_fact_metric_rows": rows[:160],
    }


def harden_c03_graph_expansion(expansion: dict[str, Any], graph: dict[str, Any], *, fact_claims: dict[str, str] | None = None, policy: C03GraphHardeningPolicy | None = None) -> dict[str, Any]:
    policy = policy or C03GraphHardeningPolicy()
    index = build_graph_index(graph)
    selected_skills = [str(s.get("skill_id")) for s in expansion.get("selected_skills") or [] if s.get("skill_id")]
    selected_facts = [dict(f) for f in expansion.get("selected_facts") or []]
    roots = list(dict.fromkeys([*(expansion.get("tracks_with_facts") or []), *selected_skills[:20]]))
    forward_paths: dict[str, Any] = {}
    reverse_paths: dict[str, Any] = {}
    for f in selected_facts[:80]:
        fid = str(f.get("fact_id") or "")
        sid = str(f.get("skill_id") or "")
        if sid and fid:
            forward_paths[f"{sid}->{fid}"] = traverse_between_nodes(index, sid, [fid], max_depth=policy.max_depth)
            reverse_paths[f"{fid}->{sid}"] = traverse_between_nodes(index, fid, [sid], max_depth=policy.max_depth, reverse=True)
    hetero = metric_heterogeneity_receipt(selected_facts, fact_claims)
    largest = float(hetero.get("largest_metric_bucket_share") or 0.0)
    bucket_count = int(hetero.get("metric_bucket_count") or 0)
    guardrail_errors: list[str] = []
    if bucket_count < policy.min_metric_bucket_count:
        guardrail_errors.append(f"metric_bucket_count_below_min:{bucket_count}<{policy.min_metric_bucket_count}")
    if largest > policy.max_same_metric_bucket_share:
        guardrail_errors.append(f"largest_metric_bucket_share_above_max:{largest}>{policy.max_same_metric_bucket_share}")
    hardened = {
        **expansion,
        "schema": f"{expansion.get('schema', 'track_weighted_graph_expansion_v1')}+{HARDENING_SCHEMA_VERSION}",
        "c03_graph_hardening_schema": HARDENING_SCHEMA_VERSION,
        "c03_graph_traversal_depth_max": policy.max_depth,
        "c03_forward_deep_paths": forward_paths,
        "c03_reverse_deep_paths": reverse_paths,
        "c03_frontier_receipt": build_frontier_receipt(index, roots, max_depth=policy.max_depth),
        "c03_rejected_sibling_skills": rejected_sibling_skills(index, selected_skills),
        "c03_metric_heterogeneity_receipt": hetero,
        "c03_graph_guardrail_errors": guardrail_errors,
        "c03_graph_guardrail_status": "PASS" if not guardrail_errors else "WARN",
        "c03_no_loss_overlay_digest": _stable_digest({"selected_skills": selected_skills, "selected_facts": selected_facts, "schema": HARDENING_SCHEMA_VERSION}),
    }
    return hardened


def harden_augmented_skills_graph_payload(graph: dict[str, Any]) -> dict[str, Any]:
    """Return graph with canonical edge metadata added; never removes existing content."""
    edges = [canonical_edge(e) if isinstance(e, dict) else e for e in graph.get("graph_edges") or []]
    meta = dict(graph.get("graph_metadata") or {})
    meta.setdefault("c03_graph_hardening_schema", HARDENING_SCHEMA_VERSION)
    meta["c03_edge_precision_required"] = True
    meta["c03_reverse_traversal_supported"] = True
    meta["c03_metric_heterogeneity_required"] = True
    return {**graph, "graph_metadata": meta, "graph_edges": edges}
