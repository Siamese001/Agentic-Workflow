"""H4: True end-to-end local vs full stopwatch on identical corpus + cache state.

Runs the full generate_full_adg pipeline twice in the same process:
  Run A — local mode (enable_zip=False, enable_reports=False)
  Run B — full mode  (enable_zip=True,  enable_reports=True)

Both runs share the same pre-warmed scan cache so timing differences reflect
only the pipeline work, not scan I/O variance.

Outputs adg_p8_v8_e2e.json with directly measured wall times for every
named sub-span, plus peak RSS for each run.

Usage:
    python tools/profile_v8_e2e.py
"""
from __future__ import annotations

import gc
import json
import sys
import tempfile
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

proc = psutil.Process()


def rss_mb() -> float:
    return proc.memory_info().rss / 1024 / 1024


# ---------------------------------------------------------------------------
# Inline pipeline runner with per-span instrumentation
# ---------------------------------------------------------------------------

def run_pipeline(
    *,
    enable_zip: bool,
    enable_reports: bool,
    out_dir: Path,
    ts: str,
    result,        # pre-built ScanResult
    artifact,      # pre-built ADGArtifact
) -> dict:
    """Run the post-scan pipeline phases and record per-span wall times."""
    import os

    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
    from agentic_core.adg.analysis.CanonicalSnapshot import (
        build_snapshot,
        load_latest_snapshot,
        save_snapshot,
    )
    from agentic_core.adg.analysis.GraphDiff import diff_snapshots
    from agentic_core.adg.analysis.ImpactReport import impact_summary, predict_impact
    from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
    from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations
    from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry

    spans: dict[str, float] = {}
    peak_rss = rss_mb()

    def span(name: str, fn):
        nonlocal peak_rss
        gc.collect()
        t0 = time.perf_counter()
        r = fn()
        elapsed = time.perf_counter() - t0
        spans[name] = round(elapsed, 4)
        peak_rss = max(peak_rss, rss_mb())
        return r

    # W: write all artifacts (fused W3+W9)
    paths = span("write_artifacts", lambda: write_all_artifacts(
        artifact, out_dir=out_dir, ts=ts,
        write_sqlite=True, write_split_planes=True,
    ))

    # PL1: score_edges
    scored_edges = span("score_edges", lambda: score_edges(list(result.edges)))

    # PL2: confidence_summary
    conf_summary = span("confidence_summary", lambda: confidence_summary(scored_edges))

    # PL3: route_violations
    violation_edges = [
        e for e in result.edges
        if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
    ]
    repair_routes = span("route_violations", lambda: route_violations(violation_edges))
    routing_summary = span("repair_routing_summary", lambda: repair_routing_summary(repair_routes))

    # PL5: predict_impact
    violation_sources = [
        e.source_file for e in result.edges
        if e.relation_type == "imports" and e.source_file
        and any(e.source_file.startswith(p) for p in (
            "agentic_core/L2_execution",
            "agentic_core/L0_routing",
            "agentic_core/L5_safety",
        ))
    ]
    seed_files: list[str] = []
    seen: set[str] = set()
    for sf in violation_sources:
        if sf not in seen:
            seen.add(sf)
            seed_files.append(sf)
        if len(seed_files) >= 5:
            break
    if not seed_files:
        seed_files = list(result.modules[:5])

    impact_report = span("predict_impact", lambda: predict_impact(result, seed_files))
    imp_summary = span("impact_summary", lambda: impact_summary(impact_report))

    # PL7: build_snapshot
    snap_path = out_dir / f"adg_graphsnap_{ts}.json"
    snapshot = span("build_snapshot", lambda: build_snapshot(result))

    # PL8: load_snapshot_diff (use out_dir — first run will have no prev)
    prev = load_latest_snapshot(out_dir)
    if prev is not None:
        graph_diff = span("diff_snapshots", lambda: diff_snapshots(prev, snapshot))
    else:
        spans["diff_snapshots"] = 0.0

    # PL9: save_snapshot
    span("save_snapshot", lambda: save_snapshot(snapshot, snap_path))

    # PL10: ownership registry
    span("ownership_registry", lambda: OwnershipRegistry.from_scan_result(result))

    # PL11: persist_to_memory (skip — requires MCP/Redis, not measurable in offline profile)
    spans["persist_to_memory"] = float("nan")

    # PL12: generate_reports (full mode only)
    if enable_reports:
        from tools.generate_full_adg import _generate_standardized_reports
        rpt = span("generate_reports", lambda: _generate_standardized_reports(
            out_dir, ts, artifact,
            result=result,
            repo_root=ROOT,
            enable_determinism_probe=False,
        ))
    else:
        spans["generate_reports"] = 0.0

    # PL13: zip creation (full mode only)
    if enable_zip:
        from tools.generate_full_adg import _create_zip_archive
        artifact_files = [
            paths.snapshot, paths.sqlite,
            paths.file_graph, paths.symbol_graph, paths.governance_graph,
            snap_path,
        ]
        span("zip_creation", lambda: _create_zip_archive(out_dir, ts, artifact_files))
    else:
        spans["zip_creation"] = 0.0

    total = sum(v for v in spans.values() if v == v)  # skip NaN
    spans["_total_measurable"] = round(total, 4)
    spans["_peak_rss_mb"] = round(peak_rss, 1)
    spans["_enable_zip"] = enable_zip
    spans["_enable_reports"] = enable_reports
    return spans


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    from agentic_core.adg.artifact.builder_types import build_artifact
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"

    print("=== ADG v8 E2E Profile: local vs full mode ===")
    print()

    # Phase 0: scan (shared — cached)
    print("Phase 0: scan (cache-warmed)...")
    rss_pre_scan = rss_mb()
    t0 = time.perf_counter()
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)
    result = scanner.scan()
    t_scan = time.perf_counter() - t0
    rss_post_scan = rss_mb()
    print(f"  scan: {t_scan:.2f}s  RSS: {rss_post_scan:.0f} MB (+{rss_post_scan-rss_pre_scan:.0f} MB)")
    gc.collect()

    # Phase 1: build artifact (shared)
    print("Phase 1: build_artifact...")
    t0 = time.perf_counter()
    artifact = build_artifact(result, repo_root=ROOT)
    t_build = time.perf_counter() - t0
    rss_post_build = rss_mb()
    print(f"  build: {t_build:.2f}s  RSS: {rss_post_build:.0f} MB (+{rss_post_build-rss_post_scan:.0f} MB)")
    gc.collect()

    # Run A: LOCAL mode
    print()
    print("Run A: LOCAL mode (zip=OFF, reports=OFF)...")
    with tempfile.TemporaryDirectory() as td_local:
        rss_pre_a = rss_mb()
        t0 = time.perf_counter()
        spans_local = run_pipeline(
            enable_zip=False, enable_reports=False,
            out_dir=Path(td_local), ts="v8local",
            result=result, artifact=artifact,
        )
        t_local = time.perf_counter() - t0
    print(f"  total: {t_local:.2f}s  peak RSS: {spans_local['_peak_rss_mb']:.0f} MB")
    gc.collect()

    # Run B: FULL mode
    print()
    print("Run B: FULL mode (zip=ON, reports=ON)...")
    with tempfile.TemporaryDirectory() as td_full:
        rss_pre_b = rss_mb()
        t0 = time.perf_counter()
        spans_full = run_pipeline(
            enable_zip=True, enable_reports=True,
            out_dir=Path(td_full), ts="v8full",
            result=result, artifact=artifact,
        )
        t_full = time.perf_counter() - t0
    print(f"  total: {t_full:.2f}s  peak RSS: {spans_full['_peak_rss_mb']:.0f} MB")
    gc.collect()

    # --- Report ---
    print()
    print("=" * 64)
    print("DIRECTLY MEASURED: local vs full mode comparison")
    print("=" * 64)
    print(f"  Shared phases:")
    print(f"    scan (cached):    {t_scan:.2f}s")
    print(f"    build_artifact:   {t_build:.2f}s")
    print()
    print(f"  {'Span':<28}  {'LOCAL':>8}  {'FULL':>8}  {'DELTA':>8}")
    print(f"  {'-'*28}  {'-'*8}  {'-'*8}  {'-'*8}")

    all_spans = sorted(k for k in spans_local if not k.startswith("_"))
    for k in all_spans:
        vl = spans_local.get(k, float("nan"))
        vf = spans_full.get(k, float("nan"))
        if vl != vl or vf != vf:  # NaN
            print(f"  {k:<28}  {'(skip)':>8}  {'(skip)':>8}  {'—':>8}")
            continue
        delta = vf - vl
        print(f"  {k:<28}  {vl:>8.2f}  {vf:>8.2f}  {delta:>+8.2f}")

    print(f"  {'-'*28}  {'-'*8}  {'-'*8}  {'-'*8}")
    tl_total = t_scan + t_build + t_local
    tf_total = t_scan + t_build + t_full
    print(f"  {'TOTAL (scan+build+pipeline)':<28}  {tl_total:>8.2f}  {tf_total:>8.2f}  {tl_total-tf_total:>+8.2f}")
    print()
    print(f"  Peak RSS local:  {spans_local['_peak_rss_mb']:.0f} MB")
    print(f"  Peak RSS full:   {spans_full['_peak_rss_mb']:.0f} MB")

    # --- Persist ---
    profile = {
        "version": "v8",
        "note": "H4: true e2e local vs full — directly measured, same corpus+cache",
        "shared": {
            "scan_s": round(t_scan, 3),
            "build_s": round(t_build, 3),
            "entities": len(artifact.entities),
            "relations": len(artifact.relations),
        },
        "local_mode": spans_local,
        "full_mode": spans_full,
        "totals": {
            "local_total_s": round(tl_total, 3),
            "full_total_s": round(tf_total, 3),
            "local_minus_full_s": round(tl_total - tf_total, 3),
        },
    }
    out_path = ROOT / "artifacts" / "adg_p8_v8_e2e.json"
    out_path.write_text(json.dumps(profile, indent=2))
    print(f"Profile written: {out_path}")


if __name__ == "__main__":
    main()
