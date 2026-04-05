"""ADG Pipeline Profiler v6 — Patch D0 + D1.

D0: Decompose the 8.22s plumbing bucket into real sub-spans:
    score_edges, confidence_summary, route_violations, repair_routing_summary,
    predict_impact, impact_summary, build_snapshot/save_snapshot/diff,
    OwnershipRegistry, _persist_adg_to_memory, _generate_standardized_reports,
    zip creation.

D1: Trace BA3 + W3 + W9 as one normalization family to determine whether
    IdentityNormalizer output from BA3 can be reused directly by W3 and W9.
    Measures: shared object identity, re-computation cost, and object sizes.

Usage:
    python tools/profile_adg_phases_v6.py           # full pipeline
    python tools/profile_adg_phases_v6.py --no-write  # skip write path
    python tools/profile_adg_phases_v6.py --no-plumbing  # skip heavy plumbing (fast)
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore[import]
    _PROC = psutil.Process()
    def _rss_mb() -> float:
        return _PROC.memory_info().rss / 1024 / 1024
except ImportError:
    def _rss_mb() -> float:
        return 0.0

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ADG_SKIP_SELF_TEST", "1")
# Suppress Redis/git side-effects in plumbing sub-spans
os.environ.setdefault("ADG_SKIP_REDIS", "1")
os.environ.setdefault("ADG_SKIP_GIT", "1")


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------

@dataclass
class PhaseResult:
    name: str
    wall: float
    cpu: float
    rss_delta_mb: float
    gc_gen0: int
    gc_gen1: int
    extra: dict

    def display(self, indent: int = 0) -> str:
        pad = " " * indent
        extra_str = ("  " + "  ".join(f"{k}={v}" for k, v in self.extra.items())) if self.extra else ""
        return (
            f"{pad}[{self.name:<46}] wall={self.wall:7.3f}s  cpu={self.cpu:7.3f}s"
            f"  rss={self.rss_delta_mb:+5.0f}MB  gc=[{self.gc_gen0},{self.gc_gen1}]"
            f"{extra_str}"
        )


class _Timer:
    def __init__(self, name: str) -> None:
        self.name = name
        self._wall0 = self._cpu0 = self._rss0 = 0.0
        self._gc0: list[dict] = []
        self.result: PhaseResult | None = None

    def __enter__(self) -> "_Timer":
        gc.collect()
        self._gc0 = gc.get_stats()
        self._wall0 = time.perf_counter()
        self._cpu0 = time.process_time()
        self._rss0 = _rss_mb()
        return self

    def __exit__(self, *_: Any) -> None:
        wall = time.perf_counter() - self._wall0
        cpu = time.process_time() - self._cpu0
        rss = _rss_mb() - self._rss0
        gc1 = gc.get_stats()
        dg0 = gc1[0]["collections"] - self._gc0[0]["collections"]
        dg1 = gc1[1]["collections"] - self._gc0[1]["collections"]
        self.result = PhaseResult(self.name, wall, cpu, rss, dg0, dg1, {})


def _p(name: str) -> _Timer:
    return _Timer(name)


# ---------------------------------------------------------------------------
# D1 helpers — normalization family tracer
# ---------------------------------------------------------------------------

def _object_size_mb(obj: Any) -> float:
    """Shallow size via sys.getsizeof, in MB."""
    return sys.getsizeof(obj) / 1024 / 1024


def _d1_trace_normalization_family(result: Any, artifact: Any) -> list[PhaseResult]:
    """D1: Run BA3 + W3 + W9 independently and together, measuring re-use opportunity.

    BA3 = _populate_symbol_entities (IdentityNormalizer + symbol projection)
    W3  = ArtifactNormalizer().normalize(artifact)  (compact graph for SQLite)
    W9  = split_artifact(artifact)                  (3-plane JSON split)

    Key question: do W3 and W9 re-derive work already done in BA3?
    """
    from agentic_core.adg.artifact.builder_types import ADGArtifact, ADGArtifactBuilder
    from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer
    from agentic_core.adg.artifact.SplitArtifact import split_artifact
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    phases: list[PhaseResult] = []

    # --- D1-A: Isolated IdentityNormalizer.normalize_all (the kernel inside BA3) ---
    with _p("D1A_identity_normalizer_isolated") as t:
        iso_normalizer = IdentityNormalizer(repo_root=ROOT)
        iso_edges_normalized = [
            iso_normalizer.normalize(e.from_name)
            for e in result.edges[:5000]  # sample — full list would be 685k
        ]
    assert t.result is not None
    t.result.extra["sample"] = "5000_edges"
    t.result.extra["normalizer_id"] = str(id(iso_normalizer))
    phases.append(t.result)

    # --- D1-B: Full BA3 (as in build_artifact) — creates IdentityNormalizer internally ---
    builder = ADGArtifactBuilder(repo_root=ROOT)
    artifact_d1 = ADGArtifact(
        commit_sha=result.commit_sha or "",
        repo_state_hash=result.repo_state_hash or "",
        scanner_digest=result.digest or "",
        type_surface_map=getattr(result, "type_surface_map", {}),
    )
    # populate relations first (needed before symbol entities)
    builder._populate_relations(result, artifact_d1)
    builder._populate_module_entities(result, artifact_d1)

    with _p("D1B_BA3_symbol_entities_full") as t:
        builder._populate_symbol_entities(result, artifact_d1)
    assert t.result is not None
    t.result.extra["entities"] = str(len(artifact_d1.entities))
    t.result.extra["normalizer_id"] = str(id(builder._normalizer))
    phases.append(t.result)

    # Complete artifact so W3/W9 have something real to process
    builder._build_identity_health(artifact_d1)
    builder._compute_structural_metrics(result, artifact_d1)
    builder._collect_blind_spots(result, artifact_d1)
    artifact_d1.compute_digest()

    # --- D1-C: W3 ArtifactNormalizer — creates its OWN normalizer (potential duplication) ---
    with _p("D1C_W3_artifact_normalizer") as t:
        w3_normalizer = ArtifactNormalizer()
        ng_full = w3_normalizer.normalize(artifact_d1)
    assert t.result is not None
    t.result.extra["nodes"] = str(len(ng_full.nodes))
    t.result.extra["edges"] = str(len(ng_full.edges))
    t.result.extra["normalizer_id"] = str(id(w3_normalizer))
    phases.append(t.result)

    # --- D1-D: W9 split_artifact — another full artifact traversal ---
    with _p("D1D_W9_split_artifact") as t:
        planes = split_artifact(artifact_d1)
    assert t.result is not None
    file_ec = len(getattr(planes.file_graph, "edges", []) or [])
    sym_ec = len(getattr(planes.symbol_graph, "edges", []) or [])
    gov_ec = len(getattr(planes.governance_graph, "edges", []) or [])
    t.result.extra["file_edges"] = str(file_ec)
    t.result.extra["sym_edges"] = str(sym_ec)
    t.result.extra["gov_edges"] = str(gov_ec)
    phases.append(t.result)

    # --- D1-E: Summary — are the normalizers the same object? ---
    same_normalizer = (id(builder._normalizer) == id(w3_normalizer))
    phases.append(PhaseResult(
        name="D1_SUMMARY",
        wall=0.0, cpu=0.0, rss_delta_mb=0.0, gc_gen0=0, gc_gen1=0,
        extra={
            "BA3_and_W3_share_normalizer": str(same_normalizer),
            "BA3_normalizer_class": type(builder._normalizer).__name__,
            "W3_normalizer_class": type(w3_normalizer).__name__,
            "duplicate_work_detected": str(not same_normalizer),
            "entities_built": str(len(artifact_d1.entities)),
            "relations_built": str(len(artifact_d1.relations)),
        },
    ))

    return phases


# ---------------------------------------------------------------------------
# D0 — plumbing sub-span profiler
# ---------------------------------------------------------------------------

def _d0_plumbing(result: Any, artifact: Any, adg_dir: Path) -> list[PhaseResult]:
    """D0: Decompose all post-write plumbing into measured sub-spans."""
    from agentic_core.adg.analysis.CanonicalSnapshot import (
        build_snapshot,
        load_latest_snapshot,
        save_snapshot,
    )
    from agentic_core.adg.analysis.EdgeConfidence import confidence_summary, score_edges
    from agentic_core.adg.analysis.GraphDiff import diff_snapshots
    from agentic_core.adg.analysis.ImpactReport import impact_summary, predict_impact
    from agentic_core.adg.analysis.ModuleOwnership import OwnershipRegistry
    from agentic_core.adg.analysis.RepairRoute import repair_routing_summary, route_violations

    phases: list[PhaseResult] = []

    # --- PL1: score_edges ---
    with _p("PL1_score_edges") as t:
        scored_edges = score_edges(list(result.edges))
    assert t.result is not None
    t.result.extra["edges"] = str(len(result.edges))
    phases.append(t.result)

    # --- PL2: confidence_summary ---
    with _p("PL2_confidence_summary") as t:
        conf_summary = confidence_summary(scored_edges)
    assert t.result is not None
    phases.append(t.result)

    # --- PL3: route_violations ---
    with _p("PL3_route_violations") as t:
        violation_edges = [
            e for e in result.edges
            if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
        ]
        repair_routes = route_violations(violation_edges)
    assert t.result is not None
    t.result.extra["violation_edges"] = str(len(violation_edges))
    phases.append(t.result)

    # --- PL4: repair_routing_summary ---
    with _p("PL4_repair_routing_summary") as t:
        routing_summary = repair_routing_summary(repair_routes)
    assert t.result is not None
    phases.append(t.result)

    # --- PL5: predict_impact ---
    seed_files = sorted({
        e.source_file for e in result.edges
        if e.relation_type == "imports" and e.source_file
        and e.source_file.startswith("agentic_core/")
    })[:5] or list(result.modules[:5])
    with _p("PL5_predict_impact") as t:
        impact_report = predict_impact(result, seed_files)
    assert t.result is not None
    t.result.extra["seeds"] = str(len(seed_files))
    phases.append(t.result)

    # --- PL6: impact_summary ---
    with _p("PL6_impact_summary") as t:
        imp_summary = impact_summary(impact_report)
    assert t.result is not None
    phases.append(t.result)

    # --- PL7: build_snapshot ---
    with _p("PL7_build_snapshot") as t:
        snapshot = build_snapshot(result)
    assert t.result is not None
    phases.append(t.result)

    # --- PL8: load_latest_snapshot + diff ---
    with _p("PL8_load_snapshot_diff") as t:
        previous_snapshot = load_latest_snapshot(adg_dir)
        if previous_snapshot is not None:
            graph_diff = diff_snapshots(previous_snapshot, snapshot)
        else:
            graph_diff = None
    assert t.result is not None
    t.result.extra["has_prev"] = str(previous_snapshot is not None)
    phases.append(t.result)

    # --- PL9: save_snapshot ---
    snap_path = adg_dir / "adg_graphsnap_v6probe.json"
    with _p("PL9_save_snapshot") as t:
        save_snapshot(snapshot, snap_path)
    assert t.result is not None
    phases.append(t.result)

    # --- PL10: OwnershipRegistry ---
    with _p("PL10_ownership_registry") as t:
        OwnershipRegistry.from_scan_result(result)
    assert t.result is not None
    t.result.extra["modules"] = str(len(result.modules))
    phases.append(t.result)

    # --- PL11: _persist_adg_to_memory (MCP) ---
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_full_adg as _gfa  # type: ignore[import]
    with _p("PL11_persist_to_memory") as t:
        try:
            _gfa._persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, "v6probe")
        except Exception as e:
            pass  # MCP may be unavailable; timing is still captured
    assert t.result is not None
    phases.append(t.result)

    # --- PL12: _generate_standardized_reports ---
    with _p("PL12_generate_reports") as t:
        try:
            _gfa._generate_standardized_reports(
                adg_dir, "v6probe", artifact,
                result=result, repo_root=ROOT,
                enable_determinism_probe=False,
            )
        except Exception:
            pass  # may fail if sqlite not present; timing still valid
    assert t.result is not None
    phases.append(t.result)

    # --- PL13: zip creation ---
    artifact_files = [f for f in adg_dir.glob("*.json") if "v6probe" in f.name]
    with _p("PL13_zip_creation") as t:
        if artifact_files:
            try:
                _gfa._create_zip_archive(adg_dir, "v6probe", artifact_files)
            except Exception:
                pass
    assert t.result is not None
    t.result.extra["files"] = str(len(artifact_files))
    phases.append(t.result)

    return phases


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-plumbing", action="store_true", help="Skip D0 plumbing spans (faster)")
    args = parser.parse_args()

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
    if not cache_path.exists():
        print(f"ERROR: warm cache not found at {cache_path}")
        sys.exit(1)

    print("=" * 88)
    print("ADG Pipeline Profiler v6 — Plumbing Decomposition (D0) + Normalization Family (D1)")
    print(f"pid={os.getpid()}  cache={cache_path.stat().st_size // 1024 // 1024}MB")
    print(f"no_write={args.no_write}  no_plumbing={args.no_plumbing}")
    print("=" * 88)

    all_phases: list[PhaseResult] = []

    # ---- Scan ----
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)

    t_total_start = time.perf_counter()

    with _p("P_scan") as t_scan:
        result = scanner.scan()
    assert t_scan.result is not None
    t_scan.result.extra["edges"] = str(len(result.edges))
    t_scan.result.extra["digest"] = result.digest[:16] + "..."
    all_phases.append(t_scan.result)
    print(t_scan.result.display())
    print()

    # ---- Build artifact (reuse v5 approach) ----
    from agentic_core.adg.artifact.builder_types import build_artifact
    print("  === build_artifact ===")
    with _p("P_build_artifact") as t_build:
        artifact = build_artifact(result, repo_root=ROOT)
    assert t_build.result is not None
    t_build.result.extra["entities"] = str(len(artifact.entities))
    t_build.result.extra["relations"] = str(len(artifact.relations))
    all_phases.append(t_build.result)
    print(t_build.result.display(indent=2))
    print()

    # ---- Write artifacts ----
    with tempfile.TemporaryDirectory(prefix="adg_v6_probe_") as tmpdir:
        adg_dir = Path(tmpdir)

        if not args.no_write:
            from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
            print("  === write_all_artifacts ===")
            with _p("P_write_artifacts") as t_write:
                write_all_artifacts(artifact, out_dir=adg_dir, ts="v6probe")
            assert t_write.result is not None
            all_phases.append(t_write.result)
            print(t_write.result.display(indent=2))
            print()
        else:
            t_write = _Timer("P_write_artifacts")
            t_write.result = PhaseResult("P_write_artifacts", 0.0, 0.0, 0.0, 0, 0, {"skipped": "true"})
            print("  [write_all_artifacts skipped]\n")

        # ---- D1: Normalization family ----
        print("  === D1: Normalization family (BA3 + W3 + W9) ===")
        d1_phases = _d1_trace_normalization_family(result, artifact)
        for p in d1_phases:
            print(p.display(indent=2))
        all_phases.extend(d1_phases)
        print()

        # ---- D0: Plumbing decomposition ----
        if not args.no_plumbing:
            print("  === D0: Plumbing sub-spans ===")
            d0_phases = _d0_plumbing(result, artifact, adg_dir)
            for p in d0_phases:
                print(p.display(indent=2))
            all_phases.extend(d0_phases)
            print()
        else:
            d0_phases = []
            print("  [Plumbing skipped — use without --no-plumbing to measure]\n")

    t_total_end = time.perf_counter()
    pipeline_wall = t_total_end - t_total_start

    # ---- Summary ----
    scan_wall = t_scan.result.wall
    build_wall = t_build.result.wall
    write_wall = t_write.result.wall if t_write.result else 0.0
    d1_wall = sum(p.wall for p in d1_phases)
    d0_wall = sum(p.wall for p in d0_phases)

    print("=" * 88)
    print("Pipeline Stopwatch")
    print("=" * 88)
    measured = scan_wall + build_wall + write_wall + d0_wall
    overhead = pipeline_wall - measured

    def _pct(v: float) -> str:
        return f"({100*v/pipeline_wall:.1f}%)" if pipeline_wall > 0 else ""

    print(f"  scan                : {scan_wall:7.3f}s  {_pct(scan_wall)}")
    print(f"  build_artifact      : {build_wall:7.3f}s  {_pct(build_wall)}")
    if not args.no_write:
        print(f"  write_artifacts     : {write_wall:7.3f}s  {_pct(write_wall)}")
    if not args.no_plumbing:
        print(f"  plumbing (D0 total) : {d0_wall:7.3f}s  {_pct(d0_wall)}")
        print("  --- plumbing breakdown ---")
        for p in d0_phases:
            if p.name != "D1_SUMMARY":
                print(f"      {p.name:<44}: {p.wall:6.3f}s  ({100*p.wall/d0_wall:.1f}%)" if d0_wall > 0 else f"      {p.name}")
    print(f"  overhead (gc/timer) : {overhead:7.3f}s  {_pct(overhead)}")
    print(f"  PIPELINE TOTAL      : {pipeline_wall:7.3f}s  (100.0%)")

    print()
    print("  === D1: Normalization family summary ===")
    d1_summary = next((p for p in d1_phases if p.name == "D1_SUMMARY"), None)
    if d1_summary:
        for k, v in d1_summary.extra.items():
            print(f"      {k}: {v}")
    ba3_wall = next((p.wall for p in d1_phases if p.name == "D1B_BA3_symbol_entities_full"), 0.0)
    w3_wall = next((p.wall for p in d1_phases if p.name == "D1C_W3_artifact_normalizer"), 0.0)
    w9_wall = next((p.wall for p in d1_phases if p.name == "D1D_W9_split_artifact"), 0.0)
    print(f"      BA3_wall={ba3_wall:.3f}s  W3_wall={w3_wall:.3f}s  W9_wall={w9_wall:.3f}s")
    print(f"      normalization_family_total={ba3_wall+w3_wall+w9_wall:.3f}s")
    if ba3_wall + w3_wall > 0:
        overlap_pct = 100 * w3_wall / (ba3_wall + w3_wall)
        print(f"      W3_as_pct_of_BA3+W3={overlap_pct:.1f}%  (potential duplicate work if same root)")

    # ---- Save evidence ----
    evidence = {
        "pipeline_wall": pipeline_wall,
        "scan_wall": scan_wall,
        "build_wall": build_wall,
        "write_wall": write_wall,
        "d0_plumbing_total": d0_wall,
        "d1_normalization_total": d1_wall,
        "d0_breakdown": [
            {"name": p.name, "wall": p.wall, "cpu": p.cpu, "extra": p.extra}
            for p in d0_phases
        ],
        "d1_breakdown": [
            {"name": p.name, "wall": p.wall, "cpu": p.cpu, "extra": p.extra}
            for p in d1_phases
        ],
    }
    out_path = ROOT / "artifacts" / "adg_p8_v6_profile.json"
    out_path.write_text(json.dumps(evidence, indent=2))
    print(f"\nEvidence saved: {out_path}")


if __name__ == "__main__":
    main()
