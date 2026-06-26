"""Validate C0.3 graph-skill granularity hardening on the canonical graph JSON."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_GRAPH_PATH = Path("apps_rg/fact_inventory/master_skills_arsenal_ledger.json")
REQUIRED_EDGE_TYPES = {
    "career_track_contains_capability_domain",
    "capability_domain_contains_skill",
    "skill_has_metric_bucket",
    "metric_bucket_contains_metric",
    "skill_can_surface_metric",
    "section_can_select_skill",
}
MIN_HARDENED_SKILLS = 12
MIN_METRIC_BUCKETS = 12
MIN_METRIC_OPTIONS = 18


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = graph.get("graph_nodes") or []
    edges = graph.get("graph_edges") or []
    skills = graph.get("skill_rows") or []
    node_ids = [str(n.get("node_id")) for n in nodes if isinstance(n, dict) and n.get("node_id")]
    edge_ids = [str(e.get("edge_id")) for e in edges if isinstance(e, dict) and e.get("edge_id")]
    skill_ids = [str(s.get("skill_id")) for s in skills if isinstance(s, dict) and s.get("skill_id")]
    for label, ids in (("graph_nodes", node_ids), ("graph_edges", edge_ids), ("skill_rows", skill_ids)):
        dupes = [k for k, v in Counter(ids).items() if v > 1]
        if dupes:
            errors.append(f"{label} duplicate ids: {dupes[:20]}")
    edge_types = {str(e.get("edge_type")) for e in edges if isinstance(e, dict)}
    missing_edge_types = sorted(REQUIRED_EDGE_TYPES - edge_types)
    if missing_edge_types:
        errors.append(f"missing required edge types: {missing_edge_types}")
    hardened_skills = [s for s in skills if isinstance(s, dict) and str(s.get("skill_id", "")).startswith("skill:c03:")]
    if len(hardened_skills) < MIN_HARDENED_SKILLS:
        errors.append(f"expected >= {MIN_HARDENED_SKILLS} hardened C0.3 skills; got {len(hardened_skills)}")
    bucket_ids = {str(n.get("node_id")) for n in nodes if isinstance(n, dict) and n.get("node_type") == "metric_bucket"}
    if len(bucket_ids) < MIN_METRIC_BUCKETS:
        errors.append(f"expected >= {MIN_METRIC_BUCKETS} metric buckets; got {len(bucket_ids)}")
    metric_nodes = [n for n in nodes if isinstance(n, dict) and n.get("node_type") == "metric"]
    if len(metric_nodes) < MIN_METRIC_OPTIONS:
        errors.append(f"expected >= {MIN_METRIC_OPTIONS} metric options; got {len(metric_nodes)}")
    buckets_by_section: dict[str, set[str]] = defaultdict(set)
    for s in hardened_skills:
        bucket = str(s.get("metric_bucket") or "")
        for section in s.get("allowed_sections") or []:
            buckets_by_section[str(section)].add(bucket)
        if not s.get("metric_option_ids"):
            errors.append(f"{s.get('skill_id')} missing metric_option_ids")
        guidance = s.get("selection_guidance") if isinstance(s.get("selection_guidance"), dict) else {}
        if guidance.get("prefer_unseen_metric_bucket") is not True:
            errors.append(f"{s.get('skill_id')} missing prefer_unseen_metric_bucket guidance")
    for section, buckets in buckets_by_section.items():
        if len(buckets) < 4:
            errors.append(f"section {section} has weak metric-bucket diversity: {len(buckets)} buckets")
    policy = (graph.get("c03_selection_policies") or {}).get("metric_diversity") or {}
    if policy.get("enabled") is not True:
        errors.append("c03_selection_policies.metric_diversity.enabled must be true")
    if policy.get("require_rejected_sibling_skills") is not True:
        errors.append("metric diversity policy must require rejected sibling skills")
    if policy.get("require_frontier_size_by_hop_depth") is not True:
        errors.append("metric diversity policy must require frontier size by hop depth")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--graph-path", default=str(DEFAULT_GRAPH_PATH))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _repo_root()
    graph_path = Path(args.graph_path)
    if not graph_path.is_absolute():
        graph_path = root / graph_path
    graph = _load(graph_path)
    errors = validate_graph(graph)
    if errors:
        raise SystemExit("C03_GRAPH_SKILL_GRANULARITY_VALIDATION_FAILED: " + "; ".join(errors))
    print(json.dumps({"validation": "PASS", "graph_path": str(graph_path)}, indent=2))


if __name__ == "__main__":
    main()
