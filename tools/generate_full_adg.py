"""Generate full ADG with entities and relations in the comprehensive format.

Non-redundant output set (5 files, 100% edge coverage):
    adg_snapshot_<ts>.json        Tier 1: CI-light (~50 KB) — metrics only
    adg_indexed_<ts>.sqlite       Tier 2: primary queryable store (~38 MB, all 18 edge types)
    adg_file_graph_<ts>.json      imports, exports, dead_imports, covers, influences, in_cycle
    adg_symbol_graph_<ts>.json    calls, implements, reads_from, writes_to, instantiates, ...
    adg_governance_graph_<ts>.json violates, antipattern, generates_prompt, ...

Timestamp format: MMDDYYYY in US Eastern time  (e.g. 03122026 for March 12, 2026)
Internal state file (not part of the 5-file model):
    adg_graphsnap_<ts>.json       E7 drift detection — previous-run snapshot for diff

NOTE: adg_full.json removed (SQLite supersedes it). test_graph removed (covers lives in file_graph).
NOTE: adg_LATEST_* copies not generated (create_latest_symlinks=False by default).
"""

from __future__ import annotations

import gzip
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
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


def generate_full_adg(adg_artifacts_dir: Path, ts: str, archive_old: bool = True) -> None:
    """Generate full ADG and write all artifact tiers.

    Args:
        adg_artifacts_dir: Directory for ADG artifacts
        ts: Timestamp string (MMDDYYYY format)
        archive_old: If True, archive artifacts older than retention period
    """
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

    print(f"[ADG] Tier 1 snapshot:  {paths.snapshot.name}  ({sizes['snapshot']})")
    print(f"[ADG] Tier 2 sqlite:    {paths.sqlite.name}  ({sizes['sqlite']})")
    print(f"[ADG] file_graph:       {paths.file_graph.name}  ({sizes['file_graph']})")
    print(f"[ADG] symbol_graph:     {paths.symbol_graph.name}  ({sizes['symbol_graph']})")
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

    # --- Memory MCP persistence ---
    _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts)

    # --- Archive old artifacts ---
    if archive_old:
        _archive_old_artifacts(adg_artifacts_dir, ts, retention_days=7)


def _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts: str) -> None:
    """Persist key ADG signals to Memory MCP knowledge graph via ADGMemoryAdapter."""
    try:
        from agentic_core.adg.adapters.memory_mcp_adapter import get_adapter

        adapter = get_adapter()
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"[ADG] Memory MCP unavailable — skipping persistence: {e}")
        return

    diff_edges = 0
    if graph_diff and hasattr(graph_diff, "summary"):
        summary = graph_diff.summary or ""
        import re as _re

        m = _re.search(r"([+-]\d+)\s*edges", summary)
        if m:
            diff_edges = int(m.group(1))

    try:
        adapter.ingest_snapshot(result, ts, diff_edges=diff_edges)
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError) as e:
        print(f"[ADG] Memory MCP: ingest_snapshot failed: {e}")
        return

    violation_edges = [e for e in result.edges if e.relation_type == "violates"]
    total_violations = len(violation_edges)
    critical_count = routing_summary.get("by_severity", {}).get("critical", 0)
    print(
        f"[ADG] Memory MCP: persisted snapshot + layers + hotspots + {min(total_violations, 50)}/{total_violations} violations (critical={critical_count})"
    )


def _archive_old_artifacts(adg_dir: Path, current_ts: str, retention_days: int = 7) -> None:
    """Archive ADG artifacts older than retention period.

    Keeps the most recent N days of artifacts in the main directory.
    Older artifacts are compressed and moved to _archive/YYYY-MM/.

    Args:
        adg_dir: ADG artifacts directory
        current_ts: Current timestamp (MMDDYYYY)
        retention_days: Number of days to keep in main directory
    """
    if not adg_dir.exists():
        print(f"[ADG] Archive: directory {adg_dir} does not exist")
        return

    # Parse current timestamp to get cutoff date
    try:
        current_date = datetime.strptime(current_ts, "%m%d%Y")
        cutoff_date = current_date - timedelta(days=retention_days)
    except (ValueError, TypeError) as e:
        print(f"[ADG] Archive: invalid timestamp format {current_ts}: {e}")
        return

    # Patterns for ADG artifacts to archive
    patterns = [
        "adg_snapshot_*.json",
        "adg_indexed_*.sqlite",
        "adg_file_graph_*.json",
        "adg_symbol_graph_*.json",
        "adg_governance_graph_*.json",
        "adg_graphsnap_*.json",
    ]

    archived_count = 0
    skipped_count = 0
    error_count = 0

    for pattern in patterns:
        for artifact_path in adg_dir.glob(pattern):
            # Extract timestamp from filename (MMDDYYYY format)
            try:
                # Extract 8-digit timestamp from filename
                parts = artifact_path.stem.split("_")
                ts_str = None
                for part in parts:
                    if len(part) == 8 and part.isdigit():
                        ts_str = part
                        break

                if not ts_str:
                    print(f"[ADG] Archive: skipping {artifact_path.name} (no timestamp found)")
                    skipped_count += 1
                    continue

                artifact_date = datetime.strptime(ts_str, "%m%d%Y")

                # Skip if within retention period or is current
                if artifact_date >= cutoff_date or ts_str == current_ts:
                    continue

                # Create archive directory: _archive/YYYY-MM/
                archive_month_dir = adg_dir / "_archive" / artifact_date.strftime("%Y-%m")
                archive_month_dir.mkdir(parents=True, exist_ok=True)

                # Compress and move
                archive_path = archive_month_dir / f"{artifact_path.name}.gz"

                # Compress the file
                with open(artifact_path, "rb") as f_in:
                    with gzip.open(archive_path, "wb", compresslevel=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Verify compressed file exists before deleting original
                if archive_path.exists() and archive_path.stat().st_size > 0:
                    artifact_path.unlink()
                    archived_count += 1
                else:
                    print(f"[ADG] Archive: failed to verify {archive_path.name}")
                    error_count += 1
                    if archive_path.exists():
                        archive_path.unlink()  # Clean up failed compression

            except (ValueError, OSError) as e:
                print(f"[ADG] Archive: error processing {artifact_path.name}: {e}")
                error_count += 1
                continue

    if archived_count > 0:
        print(f"[ADG] Archive: archived {archived_count} old artifacts (retention={retention_days} days)")
    if error_count > 0:
        print(f"[ADG] Archive: {error_count} errors during archival")
    if skipped_count > 0:
        print(f"[ADG] Archive: skipped {skipped_count} files (no timestamp)")


def _infer_layer(path: str) -> str:
    """Infer layer label from file path."""
    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        if f"/{layer}_" in path or f"\\{layer}_" in path or f"/{layer}/" in path:
            return layer
    for prefix in ("apps_shared", "apps_lic", "apps_rg"):
        if path.startswith(prefix) or f"/{prefix}" in path:
            return "L_APP"
    return "L_UNKNOWN"


def main() -> None:
    # Timestamp in US Eastern time, format MMDDYYYY
    est = timezone(timedelta(hours=-5))  # EST (UTC-5); no DST adjustment needed for artifact names
    ts = datetime.now(est).strftime("%m%d%Y")
    adg_artifacts_dir = ROOT / "artifacts" / "adg"
    generate_full_adg(adg_artifacts_dir, ts)


if __name__ == "__main__":
    main()
