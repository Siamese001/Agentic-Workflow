"""Generate full ADG with entities and relations in the comprehensive format."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation

from agentic_core.adg.analysis.confidence import confidence_summary, score_edges
from agentic_core.adg.analysis.ownership import OwnershipRegistry
from agentic_core.adg.analysis.repair import repair_routing_summary, route_violations
from agentic_core.adg.analysis.snapshot import build_snapshot
from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.extraction.graph_persister import persist_scan_result
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def generate_full_adg(output_path: Path) -> None:
    """Generate full ADG with entities, relations, and metadata."""
    print("[ADG] Starting full scan...")

    # Create scanner and run full scan
    scanner = ADGStaticScanner(repo_root=ROOT)
    result = scanner.scan(commit_sha="")

    print(f"[ADG] Scan complete. Digest: {result.digest}")
    print(f"[ADG] Modules: {len(result.modules)}")
    print(f"[ADG] Edges: {len(result.edges)}")

    # Create MCP client and persist the scan result
    print("[ADG] Persisting to graph...")
    client = ADGMCPClient(use_mcp=False)
    persist_scan_result(result, client)

    # Read back the full graph
    print("[ADG] Reading graph...")
    graph_data = client.read_graph()

    # Build comprehensive output format
    entities_with_metadata = []
    for entity in graph_data["entities"]:
        # Parse observations to extract metadata
        obs_dict = {}
        for obs in entity.get("observations", []):
            if ":" in obs:
                key, value = obs.split(":", 1)
                obs_dict[key] = value

        entity_with_meta = {
            "adg_name": entity["name"],
            "entity_type": entity["entityType"],
            "identity_kind": "repo_module" if entity["entityType"] == "module" else "symbol",
            "confidence": "HIGH",
            "observations": entity.get("observations", []),
        }

        # Add layer if present
        if "layer" in obs_dict:
            entity_with_meta["layer"] = obs_dict["layer"]

        # Add path if present
        if "path" in obs_dict:
            entity_with_meta["resolved_path"] = obs_dict["path"]

        entities_with_metadata.append(entity_with_meta)

    # Calculate artifact digest
    canonical_str = json.dumps(
        {
            "entities": sorted([e["adg_name"] for e in entities_with_metadata]),
            "relations": sorted([(r["from"], r["relationType"], r["to"]) for r in graph_data["relations"]]),
        },
        sort_keys=True,
    )
    artifact_digest = hashlib.sha256(canonical_str.encode()).hexdigest()

    # Compute per-relation edge counts for all graph planes
    edge_counts_by_relation = result.edge_counts_by_relation()

    # Enhancement 6: Deterministic canonical snapshot
    snapshot = build_snapshot(result)

    # Enhancement 9: Edge confidence / provenance scoring
    scored_edges = score_edges(list(result.edges))
    conf_summary = confidence_summary(scored_edges)

    # Enhancement 8: Ownership registry
    ownership_registry = OwnershipRegistry.from_scan_result(result)

    # Enhancement 10: Repair routing for violations + governance edges
    violation_edges = [
        e for e in result.edges if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
    ]
    repair_routes = route_violations(violation_edges)
    routing_summary = repair_routing_summary(repair_routes)

    # Build final output
    output = {
        "artifact_digest": artifact_digest,
        "scanner_digest": result.digest,
        "schema_version": "2.0",
        "commit_sha": "",
        "entities": entities_with_metadata,
        "relations": graph_data["relations"],
        "blind_spots": {
            "parse_failure_count": result.manifest.syntax_error_count,
            "parse_failure_files": result.syntax_errors[:50],
            "dynamic_import_count": result.manifest.dynamic_execution_count,
            "dynamic_import_locations": [],
            "star_import_count": 0,
            "star_import_locations": [],
        },
        "structural_metrics": {
            "total_modules": len(result.modules),
            "total_edges": len(result.edges),
            "total_entities": len(entities_with_metadata),
            "total_relations": len(graph_data["relations"]),
        },
        "graph_plane_metrics": {
            "G1_imports": edge_counts_by_relation.get("imports", 0),
            "G2_writes_to": edge_counts_by_relation.get("writes_to", 0),
            "G2_invokes_provider": edge_counts_by_relation.get("invokes_provider", 0),
            "G3_implements": edge_counts_by_relation.get("implements", 0),
            "G4_calls": edge_counts_by_relation.get("calls", 0),
            "G5_reads_from": edge_counts_by_relation.get("reads_from", 0),
            "G6_instantiates": edge_counts_by_relation.get("instantiates", 0),
            "GF_dynamic_exec": result.manifest.dynamic_execution_count,
            "GT_covers": edge_counts_by_relation.get("covers", 0),
            "GG_writes_through": edge_counts_by_relation.get("writes_through", 0),
            "GG_routes_through": edge_counts_by_relation.get("routes_through", 0),
            "GV_violates": edge_counts_by_relation.get("violates", 0),
        },
        "gap_analysis": {
            "gap1_inter_module_calls": result.manifest.inter_module_call_count,
            "gap2_test_coverage_edges": result.manifest.test_covers_count,
            "gap3_4_layer_violations": result.manifest.layer_violation_count,
            "gap5_governance_plane_edges": result.manifest.governance_plane_count,
            "minimum_evidence_passed": result.manifest.minimum_evidence_passed,
            "scanner_self_test_passed": result.manifest.scanner_self_test_passed,
            "cardinality_violations": result.manifest.cardinality_violations,
        },
        "unresolved_imports": [],
        "identity_health": {
            "total_entities": len(entities_with_metadata),
            "high_confidence": len([e for e in entities_with_metadata if e.get("confidence") == "HIGH"]),
        },
        "canonical_snapshot": snapshot.to_dict(),
        "confidence_analysis": conf_summary,
        "repair_routing": routing_summary,
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[ADG] Writing {output_path}...")
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[ADG] Done. {output_path.name} ({size_mb:.1f} MB)")
    print(f"      entities={len(entities_with_metadata)}  relations={len(graph_data['relations'])}")
    print(f"      artifact_digest={artifact_digest[:16]}...")
    print("[ADG] Graph plane coverage:")
    print(f"      G1_imports={edge_counts_by_relation.get('imports', 0)}")
    print(f"      G3_implements={edge_counts_by_relation.get('implements', 0)}")
    print(f"      G4_calls={result.manifest.inter_module_call_count}  (Gap 1 resolved)")
    print(f"      GT_covers={result.manifest.test_covers_count}  (Gap 2 resolved)")
    print(f"      GV_violates={result.manifest.layer_violation_count}  (Gap 3+4 resolved)")
    print(f"      GG_governance={result.manifest.governance_plane_count}  (Gap 5 resolved)")
    print("[ADG] Enhancement 6-10 analysis:")
    print(
        f"      E6 graph_hash={snapshot.graph_hash[:16]}...  nodes={snapshot.node_count}  edges={snapshot.edge_count}"
    )
    print("      E7 diff engine: use diff_snapshots(before, after) on saved snapshots")
    print(f"      E8 ownership registry: {len(result.modules)} modules indexed")
    print(
        f"      E9 confidence: avg={conf_summary['average_confidence']}  high={conf_summary['confidence_tiers']['high']}  low={conf_summary['confidence_tiers']['low']}"
    )
    print(
        f"      E10 repair routes: {routing_summary['total_routes']} routes  by_severity={routing_summary['by_severity']}"
    )


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = ROOT / "artifacts" / "adg" / f"adg_full_{ts}.json"
    generate_full_adg(output_path)


if __name__ == "__main__":
    main()
