"""Generate full ADG with entities and relations in the comprehensive format.

Outputs three artifact tiers per run:
    Tier 1  adg_snapshot_<ts>.json      CI-light (~50 KB) — metrics only
    Tier 2  adg_full_<ts>.json          Normalized compact (~15-20 MB vs 57 MB)
    Tier 3  adg_indexed_<ts>.sqlite     Queryable SQLite (~8-12 MB)

Plus four split-plane sub-graphs:
    adg_file_graph_<ts>.json
    adg_symbol_graph_<ts>.json
    adg_test_graph_<ts>.json
    adg_governance_graph_<ts>.json
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # guardian: allow-global-mutation

from agentic_core.adg.analysis.confidence import confidence_summary, score_edges
from agentic_core.adg.analysis.diff import diff_snapshots
from agentic_core.adg.analysis.impact import impact_summary, predict_impact
from agentic_core.adg.analysis.ownership import OwnershipRegistry, _infer_ownership
from agentic_core.adg.analysis.repair import repair_routing_summary, route_violations
from agentic_core.adg.analysis.snapshot import (
    build_snapshot,
    load_latest_snapshot,
    save_snapshot,
)
from agentic_core.adg.artifact.builder import build_artifact
from agentic_core.adg.artifact.multi_writer import write_all_artifacts
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def generate_full_adg(adg_artifacts_dir: Path, ts: str) -> None:
    """Generate full ADG and write all artifact tiers."""
    print("[ADG] Starting full scan...")

    scanner = ADGStaticScanner(repo_root=ROOT)
    result = scanner.scan(commit_sha="")

    print(f"[ADG] Scan complete. Digest: {result.digest}")
    print(f"[ADG] Modules: {len(result.modules)}")
    print(f"[ADG] Edges: {len(result.edges)}")

    # --- Build canonical artifact (schema v3) ---
    print("[ADG] Building canonical artifact...")
    artifact = build_artifact(result, repo_root=ROOT)

    # --- Write all three tiers + split planes ---
    print("[ADG] Writing artifact tiers...")
    paths = write_all_artifacts(artifact, out_dir=adg_artifacts_dir, ts=ts)

    # Size report
    sizes = paths.size_report()
    full_path = paths.full
    full_sz_mb = full_path.stat().st_size / (1024 * 1024) if full_path.exists() else 0

    print(f"[ADG] Tier 1 snapshot:  {paths.snapshot.name}  ({sizes['snapshot']})")
    print(f"[ADG] Tier 2 full:      {paths.full.name}  ({sizes['full']})")
    print(f"[ADG] Tier 3 sqlite:    {paths.sqlite.name}  ({sizes['sqlite']})")
    print(f"[ADG] file_graph:       {paths.file_graph.name}  ({sizes['file_graph']})")
    print(f"[ADG] symbol_graph:     {paths.symbol_graph.name}  ({sizes['symbol_graph']})")
    print(f"[ADG] test_graph:       {paths.test_graph.name}  ({sizes['test_graph']})")
    print(f"[ADG] governance_graph: {paths.governance_graph.name}  ({sizes['governance_graph']})")
    print(f"[ADG] entities={len(artifact.entities)}  relations={len(artifact.relations)}")
    print(f"[ADG] artifact_digest={artifact.artifact_digest[:16]}...")

    # --- E6: graph snapshot + E7: drift ---
    snapshot = build_snapshot(result)
    previous_snapshot = load_latest_snapshot(adg_artifacts_dir)
    if previous_snapshot is not None:
        graph_diff = diff_snapshots(previous_snapshot, snapshot)
        print(f"[ADG] E7 diff: {graph_diff.summary}")
    else:
        graph_diff = None
        print("[ADG] E7 diff: no previous snapshot found (first run)")

    snap_path = adg_artifacts_dir / f"adg_graphsnap_{ts}.json"
    save_snapshot(snapshot, snap_path)
    print(f"[ADG] E7 snapshot saved: {snap_path.name}")

    # --- E8: Ownership ---
    OwnershipRegistry.from_scan_result(result)

    # --- E9: Confidence ---
    scored_edges = score_edges(list(result.edges))
    conf_summary = confidence_summary(scored_edges)

    # --- E10: Repair routing ---
    violation_edges = [
        e for e in result.edges if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
    ]
    repair_routes = route_violations(violation_edges)
    routing_summary = repair_routing_summary(repair_routes)

    # --- E5: Impact prediction ---
    violation_sources = [
        e.source_file
        for e in result.edges
        if e.relation_type == "imports"
        and e.source_file
        and any(
            e.source_file.startswith(p)
            for p in (
                "agentic_core/L2_execution",
                "agentic_core/L0_routing",
                "agentic_core/L5_safety",
            )
        )
    ]
    seed_files: list[str] = []
    seen_seeds: set[str] = set()
    for sf in violation_sources:
        if sf not in seen_seeds:
            seen_seeds.add(sf)
            seed_files.append(sf)
        if len(seed_files) >= 5:
            break
    if not seed_files:
        seed_files = list(result.modules[:5])
    impact_report = predict_impact(result, seed_files)
    imp_summary = impact_summary(impact_report)

    # --- Print analysis summary ---
    edge_counts = result.edge_counts_by_relation()
    print("[ADG] Graph plane coverage:")
    print(f"      G1_imports={edge_counts.get('imports', 0)}")
    print(f"      G3_implements={edge_counts.get('implements', 0)}")
    print(f"      G4_calls={result.manifest.inter_module_call_count}  (Gap 1 resolved)")
    print(f"      GT_covers={result.manifest.test_covers_count}  (Gap 2 resolved)")
    print(f"      GV_violates={result.manifest.layer_violation_count}  (Gap 3+4 resolved)")
    print(f"      GG_governance={result.manifest.governance_plane_count}  (Gap 5 resolved)")
    print("[ADG] Enhancement 5-10 analysis:")
    print(
        f"      E5 impact: {imp_summary['impacted_module_count']} impacted  "
        f"{imp_summary['covering_test_count']} tests  risk={imp_summary['risk_label']} ({imp_summary['risk_score']:.4f})"
    )
    print(
        f"      E6 graph_hash={snapshot.graph_hash[:16]}...  nodes={snapshot.node_count}  edges={snapshot.edge_count}"
    )
    if graph_diff is not None:
        print(f"      E7 drift: {graph_diff.summary}")
    else:
        print("      E7 drift: first run — snapshot persisted for next diff")
    owned_high = sum(
        1
        for e in artifact.entities
        if getattr(e, "entity_type", "") == "module"
        and _infer_ownership(getattr(e, "resolved_path", "")).criticality == "high"
    )
    print(f"      E8 ownership: {len(result.modules)} modules  high_criticality={owned_high}")
    print(
        f"      E9 confidence: avg={conf_summary['average_confidence']}  "
        f"high={conf_summary['confidence_tiers']['high']}  low={conf_summary['confidence_tiers']['low']}"
    )
    print(
        f"      E10 repair routes: {routing_summary['total_routes']} routes  by_severity={routing_summary['by_severity']}"
    )


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    adg_artifacts_dir = ROOT / "artifacts" / "adg"
    generate_full_adg(adg_artifacts_dir, ts)


if __name__ == "__main__":
    main()
