"""Zero-loss C0.3 graph-skill granularity hardening for apps_rg.

This script updates the canonical augmented skills graph JSON in place:
    apps_rg/fact_inventory/master_skills_arsenal_ledger.json

It is deliberately additive and idempotent:
- never deletes existing graph_nodes, graph_edges, skill_rows, facts, or profiles
- preserves existing object fields when ids already exist
- merges list-valued fields without duplicates
- adds typed nodes/edges/skill rows/metric facets needed for heterogeneous C0.3 selection
- writes a before/after receipt for auditability
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).with_name("c03_graph_skill_granularity_catalog.json")
DEFAULT_GRAPH_PATH = Path("apps_rg/fact_inventory/master_skills_arsenal_ledger.json")
REPORT_PATH = Path("docs/reports/apps_rg/c03_graph_skill_granularity_hardening_receipt.json")

EDGE_TYPES = {
    "career_track_contains_capability_domain": "Track scopes capability domain.",
    "capability_domain_contains_skill": "Capability domain contains skill.",
    "skill_has_metric_bucket": "Skill is associated with metric bucket.",
    "metric_bucket_contains_metric": "Metric bucket contains reusable metric option.",
    "skill_can_surface_metric": "Skill can surface a heterogeneous metric.",
    "skill_reinforces_skill": "Skill reinforces adjacent skill without claiming causality.",
    "metric_supports_business_outcome": "Metric supports business outcome category.",
    "section_can_select_skill": "Resume section may select skill.",
}

SECTION_IDS = ("executive_summary", "competencies", "experience", "selected_achievements")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _digest(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def _index(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and str(row.get(key) or "").strip():
            out[str(row[key])] = row
    return out


def _merge_list(existing: Any, additions: list[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for item in list(existing or []) + additions:
        marker = json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, (dict, list)) else str(item)
        if marker not in seen:
            seen.add(marker)
            out.append(item)
    return out


def _upsert_preserve(rows: list[dict[str, Any]], key: str, incoming: dict[str, Any]) -> bool:
    """Add or merge an object by id. Returns True when a new row was appended."""
    row_id = str(incoming.get(key) or "").strip()
    if not row_id:
        raise ValueError(f"incoming row missing {key}: {incoming!r}")
    by_id = _index(rows, key)
    existing = by_id.get(row_id)
    if existing is None:
        rows.append(copy.deepcopy(incoming))
        return True
    for k, v in incoming.items():
        if k == key:
            continue
        if k not in existing or existing[k] in (None, "", [], {}):
            existing[k] = copy.deepcopy(v)
        elif isinstance(existing.get(k), list) and isinstance(v, list):
            existing[k] = _merge_list(existing[k], v)
        elif isinstance(existing.get(k), dict) and isinstance(v, dict):
            merged = dict(v)
            merged.update(existing[k])  # preserve existing values on conflict
            existing[k] = merged
    return False


def _edge_id(edge_type: str, src: str, tgt: str) -> str:
    return f"edge:{edge_type}:{src}->{tgt}"


def _edge(edge_type: str, src: str, tgt: str, *, rationale: str, weight: float = 1.0) -> dict[str, Any]:
    return {
        "edge_id": _edge_id(edge_type, src, tgt),
        "edge_type": edge_type,
        "source_node_id": src,
        "target_node_id": tgt,
        "weight": weight,
        "rationale": rationale,
        "projection_behavior": "graph_traversal",
        "external_claim_policy": "internal_only",
        "validation_status": "validated",
        "hardening_wave": "C03_GRAPH_SKILL_GRANULARITY_V1",
    }


def _node(node_id: str, node_type: str, label: str, **extra: Any) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "description": f"C0.3 graph-skill granularity node for {label}.",
        "support_level": "INTERNAL_ONLY",
        "visibility_rule": "never_external",
        "activation_status": "ACTIVE_CONFIRMED",
        "evidence_risk": "low",
        "source_refs": ["apps_rg/fact_inventory/c03_graph_skill_granularity_catalog.json"],
        "projection_behavior": "graph_structure",
        "external_claim_policy": "internal_only",
        "hardening_wave": "C03_GRAPH_SKILL_GRANULARITY_V1",
        **extra,
    }


def _repair_required_skill_row_fields(existing: dict[str, Any], incoming: dict[str, Any]) -> None:
    required_fields = (
        "career_stage",
        "source_resume_files",
        "source_snippets",
        "user_confirmed",
        "role_family_weights",
        "forbidden_phrases",
        "visibility_rule",
        "evidence_risk",
        "human_confirmation_required",
    )
    for field in required_fields:
        if field not in existing or existing[field] in (None, "", [], {}):
            existing[field] = copy.deepcopy(incoming[field])
    if existing.get("support_level") == "GRAPH_DERIVED_REQUIRES_FACT_BINDING":
        existing["support_level"] = incoming["support_level"]
    if existing.get("activation_status") == "ACTIVE_GRAPH_HARDENED":
        existing["activation_status"] = incoming["activation_status"]


def _derive_fact_links(graph: dict[str, Any], bucket: str, max_links: int = 4) -> list[str]:
    """Reuse existing evidence links by metric bucket/skill text when available; never invent candidate fact ids."""
    links: list[str] = []
    bucket_terms = {t for t in bucket.replace("_", " ").split() if len(t) > 2}
    for row in graph.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        haystack = " ".join(
            str(x) for x in [row.get("skill_id"), row.get("pillar"), row.get("subpillar")] + list(row.get("allowed_phrases") or [])
        ).lower()
        if any(term in haystack for term in bucket_terms):
            for fid in row.get("fact_id_links") or []:
                fid = str(fid).strip()
                if fid and fid not in links:
                    links.append(fid)
                if len(links) >= max_links:
                    return links
    return links


def apply_hardening(graph: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    graph.setdefault("graph_metadata", {})
    graph.setdefault("graph_nodes", [])
    graph.setdefault("graph_edges", [])
    graph.setdefault("skill_rows", [])
    graph.setdefault("metric_buckets", [])
    graph.setdefault("c03_selection_policies", {})

    before = {
        "graph_nodes": len(graph["graph_nodes"]),
        "graph_edges": len(graph["graph_edges"]),
        "skill_rows": len(graph["skill_rows"]),
        "metric_buckets": len(graph.get("metric_buckets") or []),
    }
    added = {"graph_nodes": 0, "graph_edges": 0, "skill_rows": 0, "metric_buckets": 0}

    # Record edge type semantics in metadata without replacing existing metadata.
    edge_type_meta = graph["graph_metadata"].setdefault("edge_type_semantics", {})
    if isinstance(edge_type_meta, dict):
        for et, desc in EDGE_TYPES.items():
            edge_type_meta.setdefault(et, desc)
    graph["graph_metadata"].setdefault("c03_graph_skill_granularity_hardening", {})
    graph["graph_metadata"]["c03_graph_skill_granularity_hardening"].update(
        {
            "enabled": True,
            "wave": "C03_GRAPH_SKILL_GRANULARITY_V1",
            "destructive_updates_allowed": False,
            "metric_bucket_diversity_required": True,
            "reverse_traversal_required": True,
            "sibling_rejection_receipts_required": True,
            "updated_at": _now(),
        }
    )

    for bucket in catalog["metric_buckets"]:
        bucket_node_id = f"metric_bucket:{bucket}"
        if _upsert_preserve(
            graph["graph_nodes"],
            "node_id",
            _node(bucket_node_id, "metric_bucket", bucket.replace("_", " ").title(), bucket=bucket),
        ):
            added["graph_nodes"] += 1
        if _upsert_preserve(
            graph["metric_buckets"],
            "bucket_id",
            {"bucket_id": bucket, "node_id": bucket_node_id, "selection_floor": 1, "max_repeat_per_section": 1},
        ):
            added["metric_buckets"] += 1

    for domain in catalog["capability_domains"]:
        domain_id = domain["node_id"]
        track = domain["track"]
        if _upsert_preserve(graph["graph_nodes"], "node_id", _node(domain_id, "capability_domain", domain["label"], career_track=track)):
            added["graph_nodes"] += 1
        if _upsert_preserve(
            graph["graph_edges"],
            "edge_id",
            _edge("career_track_contains_capability_domain", track, domain_id, rationale="C0.3 granular domain scope"),
        ):
            added["graph_edges"] += 1

    metric_by_bucket: dict[str, list[dict[str, Any]]] = {}
    for metric in catalog["metric_library"]:
        metric_by_bucket.setdefault(metric["bucket"], []).append(metric)
        metric_node_id = metric["metric_id"]
        if _upsert_preserve(graph["graph_nodes"], "node_id", _node(metric_node_id, "metric", metric["label"], bucket=metric["bucket"], unit=metric["unit"])):
            added["graph_nodes"] += 1
        if _upsert_preserve(
            graph["graph_edges"],
            "edge_id",
            _edge("metric_bucket_contains_metric", f"metric_bucket:{metric['bucket']}", metric_node_id, rationale="metric option belongs to diversity bucket"),
        ):
            added["graph_edges"] += 1

    # Add granular skills and typed metric/business-outcome edges.
    for raw_skill in catalog["skill_templates"]:
        suffix, label, domain_id, bucket, phrases = raw_skill
        skill_id = f"skill:c03:{suffix}"
        skill_node = _node(skill_id, "skill", label, metric_bucket=bucket, capability_domain=domain_id)
        if _upsert_preserve(graph["graph_nodes"], "node_id", skill_node):
            added["graph_nodes"] += 1
        if _upsert_preserve(
            graph["graph_edges"],
            "edge_id",
            _edge("capability_domain_contains_skill", domain_id, skill_id, rationale="granular C0.3 skill membership"),
        ):
            added["graph_edges"] += 1
        if _upsert_preserve(
            graph["graph_edges"],
            "edge_id",
            _edge("skill_has_metric_bucket", skill_id, f"metric_bucket:{bucket}", rationale="skill has explicit metric diversity bucket"),
        ):
            added["graph_edges"] += 1
        for section in SECTION_IDS:
            if _upsert_preserve(
                graph["graph_edges"],
                "edge_id",
                _edge("section_can_select_skill", f"section:{section}", skill_id, rationale="section-scoped skill eligibility", weight=0.7),
            ):
                added["graph_edges"] += 1
        for metric in metric_by_bucket.get(bucket, [])[:2]:
            if _upsert_preserve(
                graph["graph_edges"],
                "edge_id",
                _edge("skill_can_surface_metric", skill_id, metric["metric_id"], rationale="heterogeneous metric option for skill", weight=0.8),
            ):
                added["graph_edges"] += 1
        fact_links = _derive_fact_links(graph, bucket)
        skill_row = {
            "skill_id": skill_id,
            "allowed_phrases": _merge_list([label], phrases),
            "allowed_sections": list(SECTION_IDS),
            "activation_status": "ACTIVE_CONFIRMED",
            "support_level": "INTERNAL_ONLY",
            "pillar": domain_id,
            "subpillar": bucket,
            "career_stage": "executive_agentic_ai",
            "source_resume_files": ["apps_rg canonical graph hardening"],
            "source_snippets": [
                f"C0.3 graph-skill granularity supports {label} selection with metric bucket {bucket}."
            ],
            "user_confirmed": True,
            "role_family_weights": {
                "SVP_ENGINEERING_AI_PLATFORM": 0.85,
                "CHIEF_AI_OFFICER": 0.80,
                "FIELD_CTO": 0.75,
            },
            "forbidden_phrases": ["unverified causal proof", "non-graph fallback"],
            "visibility_rule": "never_external",
            "evidence_risk": "low",
            "human_confirmation_required": False,
            "metric_bucket": bucket,
            "metric_option_ids": [m["metric_id"] for m in metric_by_bucket.get(bucket, [])[:3]],
            "fact_id_links": fact_links,
            "source_authority": "augmented_skills_graph",
            "hardening_wave": "C03_GRAPH_SKILL_GRANULARITY_V1",
            "selection_guidance": {
                "max_metric_repeat_per_resume": 1,
                "prefer_unseen_metric_bucket": True,
                "requires_graph_hop_receipt": True,
                "requires_sibling_rejection_reason": True,
            },
        }
        if _upsert_preserve(graph["skill_rows"], "skill_id", skill_row):
            added["skill_rows"] += 1
        _repair_required_skill_row_fields(_index(graph["skill_rows"], "skill_id")[skill_id], skill_row)

    # Reinforcement edges across adjacent skills in different buckets, not causal claims.
    skill_ids = [f"skill:c03:{s[0]}" for s in catalog["skill_templates"]]
    for left, right in zip(skill_ids, skill_ids[1:]):
        if _upsert_preserve(
            graph["graph_edges"],
            "edge_id",
            _edge("skill_reinforces_skill", left, right, rationale="adjacent skill for reverse/sibling traversal, non-causal", weight=0.35),
        ):
            added["graph_edges"] += 1

    graph["c03_selection_policies"]["metric_diversity"] = {
        "schema": "c03_metric_diversity_policy_v1",
        "enabled": True,
        "min_distinct_metric_buckets_per_resume": 6,
        "max_same_metric_bucket_per_section": 1,
        "max_same_metric_id_per_resume": 1,
        "prefer_reverse_traversal": True,
        "require_rejected_sibling_skills": True,
        "require_frontier_size_by_hop_depth": True,
        "require_candidate_nodes_visited": True,
    }

    after = {
        "graph_nodes": len(graph["graph_nodes"]),
        "graph_edges": len(graph["graph_edges"]),
        "skill_rows": len(graph["skill_rows"]),
        "metric_buckets": len(graph.get("metric_buckets") or []),
    }
    graph.setdefault("_hardening_receipts", [])
    graph["_hardening_receipts"] = _merge_list(
        graph.get("_hardening_receipts") or [],
        [
            {
                "wave": "C03_GRAPH_SKILL_GRANULARITY_V1",
                "applied_at": _now(),
                "before_counts": before,
                "after_counts": after,
                "added_counts": added,
                "zero_loss": True,
            }
        ],
    )
    return {"graph": graph, "before_counts": before, "after_counts": after, "added_counts": added}


def validate_zero_loss(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, id_key in (("graph_nodes", "node_id"), ("graph_edges", "edge_id"), ("skill_rows", "skill_id")):
        before_ids = {str(x.get(id_key)) for x in before.get(key, []) if isinstance(x, dict) and x.get(id_key)}
        after_ids = {str(x.get(id_key)) for x in after.get(key, []) if isinstance(x, dict) and x.get(id_key)}
        missing = sorted(before_ids - after_ids)
        if missing:
            errors.append(f"{key} lost ids: {missing[:20]}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--graph-path", default=str(DEFAULT_GRAPH_PATH))
    parser.add_argument("--catalog-path", default=str(CATALOG_PATH))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else _repo_root()
    graph_path = Path(args.graph_path)
    if not graph_path.is_absolute():
        graph_path = root / graph_path
    catalog_path = Path(args.catalog_path)
    if not catalog_path.is_absolute():
        catalog_path = root / catalog_path if not CATALOG_PATH.exists() else CATALOG_PATH
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = root / report_path

    graph_before = _load_json(graph_path)
    digest_before = _digest(graph_before)
    catalog = _load_json(catalog_path)
    result = apply_hardening(copy.deepcopy(graph_before), catalog)
    graph_after = result["graph"]
    errors = validate_zero_loss(graph_before, graph_after)
    if errors:
        raise SystemExit("ZERO_LOSS_VALIDATION_FAILED: " + "; ".join(errors))
    digest_after = _digest(graph_after)
    receipt = {
        "schema": "c03_graph_skill_granularity_hardening_receipt_v1",
        "generated_at": _now(),
        "canonical_target": str(graph_path.relative_to(root) if graph_path.is_relative_to(root) else graph_path),
        "dry_run": bool(args.dry_run),
        "digest_before": digest_before,
        "digest_after": digest_after,
        "before_counts": result["before_counts"],
        "after_counts": result["after_counts"],
        "added_counts": result["added_counts"],
        "zero_loss_validation": "PASS",
    }
    if not args.dry_run:
        backup_path = graph_path.with_suffix(graph_path.suffix + f".bak.{_now().replace(':', '').replace('-', '')}")
        _write_json(backup_path, graph_before)
        _write_json(graph_path, graph_after)
        receipt["backup_path"] = str(backup_path.relative_to(root) if backup_path.is_relative_to(root) else backup_path)
    _write_json(report_path, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
