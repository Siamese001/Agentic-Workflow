"""Phase-level ADG profiler with P8 sub-phase instrumentation.

Instruments the warm-run hot path (post-scan phases) with:
- Sub-phase wall/cpu/RSS timing
- Edge representation metrics
- String interning stats
- GC collection counts

Usage:
    python tools/profile_adg_phases_v2.py [--full-scan]
"""
from __future__ import annotations

import gc
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psutil

PROC = psutil.Process()


@dataclass
class SubPhaseResult:
    name: str
    wall_s: float = 0.0
    cpu_s: float = 0.0
    rss_start_mb: float = 0.0
    rss_end_mb: float = 0.0
    gc_collections: int = 0
    input_count: int = 0  # edges in / items processed
    output_count: int = 0  # edges out / items produced
    bytes_processed: int = 0
    notes: str = ""


@dataclass
class RepresentationMetrics:
    edges_before_dedup: int = 0
    edges_after_dedup: int = 0
    edges_after_post_scan: int = 0
    edges_after_w1b: int = 0
    unique_from_names: int = 0
    unique_to_names: int = 0
    unique_relation_types: int = 0
    avg_edge_size_bytes: int = 0
    canonical_text_bytes: int = 0
    string_intern_hits: int = 0  # estimate via sys.intern


def _snap_cpu() -> float:
    t = PROC.cpu_times()
    return t.user + t.system


def _snap_rss_mb() -> float:
    return PROC.memory_info().rss / 1e6


def _snap_gc() -> int:
    return sum(gc.get_count())


def run_subphase(name: str, func, *args, **kwargs) -> tuple[SubPhaseResult, Any]:
    gc.collect()  # Clean slate
    gc.disable()
    cpu0 = _snap_cpu()
    t0 = time.perf_counter()
    rss0 = _snap_rss_mb()
    gc0 = _snap_gc()

    result = func(*args, **kwargs)

    wall = time.perf_counter() - t0
    cpu = _snap_cpu() - cpu0
    rss1 = _snap_rss_mb()
    gc1 = _snap_gc()
    gc.enable()

    sp = SubPhaseResult(
        name=name,
        wall_s=round(wall, 4),
        cpu_s=round(cpu, 4),
        rss_start_mb=round(rss0, 1),
        rss_end_mb=round(rss1, 1),
        gc_collections=gc1 - gc0,
    )
    return sp, result


def profile_scan_instrumented(repo_root: Path, include_tests: bool = True) -> dict:
    """Instrumented scan that measures P8 sub-phases explicitly."""
    from agentic_core.adg.extraction.static_scanner import (
        ADGStaticScanner,
        _emit_layer_violation_edges,
        _propagate_violations,
        _detect_cycles,
        _violation_propagation_eligibility,
        _stamp_semantic_types_with_stats,
        _merge_surface_evidence,
        _EDGE_SORT_KEY,
        Edge,
        ScanResult,
    )
    from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    subphases: list[SubPhaseResult] = []
    rep = RepresentationMetrics()

    # Pre-warm
    cache_path = repo_root / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
    cache = ScanCache.load(cache_path) if cache_path.exists() else ScanCache()
    normalizer = IdentityNormalizer(repo_root=repo_root)
    normalizer._get_known_files()

    scanner = ADGStaticScanner(repo_root=repo_root, include_tests=include_tests, cache_path=cache_path)

    # Mimic scan() initialization phases P1-P7 (already measured)
    # Jump straight to P8 instrumentation

    print("=" * 72)
    print("P8 Sub-Phase Instrumentation")
    print("=" * 72)

    # Get files
    from agentic_core.adg.extraction.static_scanner import _iter_python_files
    all_files = list(_iter_python_files(repo_root, include_tests=include_tests))
    file_hashes = {f: file_hash(f) for f in all_files}

    # Collect edges (simulate the file loop)
    all_edges: list[Edge] = []
    modules_seen: list[str] = []
    surface_evidence_totals = {
        "decomposes_into_expected_count": 0,
        "controls_flow_expected_count": 0,
        "flows_to_expected_count": 0,
        "emits_side_effect_expected_count": 0,
        "resolves_callsite_expected_count": 0,
        "tests_execution_of_expected_count": 0,
        "type_surface_candidate_count": 0,
        "semantic_preexisting_count": 0,
        "semantic_exact_map_count": 0,
        "semantic_fallback_count": 0,
        "semantic_raw_edge_kind_count": 0,
    }

    # P8a: File scan loop (already fast at 99% hit rate, but measure it)
    def _scan_loop():
        edges = []
        for f in all_files:
            rel = str(f.relative_to(repo_root)).replace("\\", "/")
            fhash = file_hashes[f]
            cached_edge_dicts, cached_type_map, cached_surface_evidence, cache_hit = cache.get(rel, fhash)
            if cache_hit and cached_edge_dicts is not None:
                # Fast path: replay cached edges
                for d in cached_edge_dicts:
                    edges.append(Edge(**d))
            else:
                # Slow path: actually scan (rare)
                from agentic_core.adg.extraction.static_scanner import _scan_file
                file_edges, _, _, _ = _scan_file(f, repo_root, include_tests, normalizer, "full")
                edges.extend(file_edges)
        return edges

    sp, all_edges = run_subphase("p8a_file_scan", _scan_loop)
    sp.input_count = len(all_files)
    sp.output_count = len(all_edges)
    subphases.append(sp)
    print(f"[P8a] file_scan:    wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(all_edges):,}  gc={sp.gc_collections}")

    rep.edges_before_dedup = len(all_edges)

    # P8b: Dedup (set)
    def _dedup():
        return set(all_edges)

    sp, edge_set = run_subphase("p8b_dedup_set", _dedup)
    sp.input_count = len(all_edges)
    sp.output_count = len(edge_set)
    subphases.append(sp)
    print(f"[P8b] dedup_set:    wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  unique={len(edge_set):,}  gc={sp.gc_collections}")
    rep.edges_after_dedup = len(edge_set)

    # P8c: Sort
    def _sort_edges():
        return sorted(edge_set, key=_EDGE_SORT_KEY)

    sp, sorted_edges = run_subphase("p8c_sort", _sort_edges)
    sp.input_count = len(edge_set)
    sp.output_count = len(sorted_edges)
    subphases.append(sp)
    print(f"[P8c] sort:         wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(sorted_edges):,}  gc={sp.gc_collections}")

    # P8d: First digest
    from agentic_core.adg.extraction.static_scanner import ScanResult

    def _first_digest():
        sr = ScanResult()
        sr.edges = sorted_edges
        sr.compute_digest()
        return sr.digest

    sp, digest1 = run_subphase("p8d_digest_1", _first_digest)
    sp.input_count = len(sorted_edges)
    subphases.append(sp)
    print(f"[P8d] digest_1:     wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  gc={sp.gc_collections}")

    # P8e: Violation edges
    def _violations():
        from agentic_core.adg.extraction.static_scanner import ScanResult, ScanManifest
        sr = ScanResult()
        sr.edges = sorted_edges
        sr.modules = []
        sr.manifest = ScanManifest()
        return _emit_layer_violation_edges(sr)

    sp, violation_edges = run_subphase("p8e_violations", _violations)
    sp.output_count = len(violation_edges)
    subphases.append(sp)
    print(f"[P8e] violations:   wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(violation_edges):,}  gc={sp.gc_collections}")

    # P8f: Propagation
    def _propagation():
        from agentic_core.adg.extraction.static_scanner import ScanResult, ScanManifest
        sr = ScanResult()
        sr.edges = sorted_edges + (violation_edges or [])
        sr.modules = []
        sr.manifest = ScanManifest()
        return _propagate_violations(sr)

    sp, propagation_edges = run_subphase("p8f_propagation", _propagation)
    sp.output_count = len(propagation_edges)
    subphases.append(sp)
    print(f"[P8f] propagation:  wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(propagation_edges):,}  gc={sp.gc_collections}")

    # P8g: Cycle detection
    def _cycles():
        from agentic_core.adg.extraction.static_scanner import ScanResult, ScanManifest
        sr = ScanResult()
        sr.edges = sorted_edges
        sr.modules = []
        sr.manifest = ScanManifest()
        return _detect_cycles(sr)

    sp, cycle_edges = run_subphase("p8g_cycles", _cycles)
    sp.output_count = len(cycle_edges)
    subphases.append(sp)
    print(f"[P8g] cycles:       wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(cycle_edges):,}  gc={sp.gc_collections}")

    # P8h: Merge and re-sort
    def _merge_and_sort():
        merged = set(sorted_edges)
        if violation_edges:
            merged |= set(violation_edges)
        if propagation_edges:
            merged |= set(propagation_edges)
        if cycle_edges:
            merged |= set(cycle_edges)
        return sorted(merged, key=_EDGE_SORT_KEY)

    sp, final_sorted = run_subphase("p8h_merge_resort", _merge_and_sort)
    sp.input_count = len(sorted_edges) + len(violation_edges or []) + len(propagation_edges or []) + len(cycle_edges or [])
    sp.output_count = len(final_sorted)
    subphases.append(sp)
    print(f"[P8h] merge_resort: wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(final_sorted):,}  gc={sp.gc_collections}")
    rep.edges_after_post_scan = len(final_sorted)

    # P8i: W1b key-based dedup
    def _w1b_dedup():
        seen: set[tuple[str, str, str, int]] = set()
        deduped: list[Edge] = []
        for e in final_sorted:
            ek = (e.from_name, e.relation_type, e.to_name, e.line_no)
            if ek not in seen:
                seen.add(ek)
                deduped.append(e)
        return deduped

    sp, w1b_edges = run_subphase("p8i_w1b_dedup", _w1b_dedup)
    sp.input_count = len(final_sorted)
    sp.output_count = len(w1b_edges)
    subphases.append(sp)
    print(f"[P8i] w1b_dedup:    wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  edges={len(w1b_edges):,}  removed={len(final_sorted)-len(w1b_edges)}  gc={sp.gc_collections}")
    rep.edges_after_w1b = len(w1b_edges)

    # P8j: Final digest
    def _final_digest():
        sr = ScanResult()
        sr.edges = w1b_edges
        sr.compute_digest()
        return sr.digest

    sp, digest2 = run_subphase("p8j_digest_2", _final_digest)
    sp.input_count = len(w1b_edges)
    subphases.append(sp)
    print(f"[P8j] digest_2:     wall={sp.wall_s:.3f}s  cpu={sp.cpu_s:.3f}s  gc={sp.gc_collections}")

    # Representation metrics
    print()
    print("=" * 72)
    print("Representation Metrics")
    print("=" * 72)

    # Count unique strings
    all_from = set(e.from_name for e in w1b_edges)
    all_to = set(e.to_name for e in w1b_edges)
    all_rel = set(e.relation_type for e in w1b_edges)

    rep.unique_from_names = len(all_from)
    rep.unique_to_names = len(all_to)
    rep.unique_relation_types = len(all_rel)

    # Estimate canonical text size
    sample_size = min(10000, len(w1b_edges))
    sample_edges = w1b_edges[:sample_size]
    canonical_lines = []
    for e in sample_edges:
        line = f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}|{e.source_file}|{e.line_no}|{e.symbol}"
        canonical_lines.append(line)
    sample_bytes = sum(len(l.encode("utf-8")) for l in canonical_lines)
    avg_line_bytes = sample_bytes / sample_size if sample_size > 0 else 0
    rep.canonical_text_bytes = int(avg_line_bytes * len(w1b_edges))
    rep.avg_edge_size_bytes = int(avg_line_bytes)

    print(f"  edges_before_dedup:     {rep.edges_before_dedup:,}")
    print(f"  edges_after_set_dedup:  {rep.edges_after_dedup:,}")
    print(f"  edges_after_post_scan:  {rep.edges_after_post_scan:,}")
    print(f"  edges_after_w1b:        {rep.edges_after_w1b:,}")
    print(f"  unique_from_names:      {rep.unique_from_names:,}")
    print(f"  unique_to_names:        {rep.unique_to_names:,}")
    print(f"  unique_relation_types:  {rep.unique_relation_types}")
    print(f"  avg_edge_canonical_bytes: {rep.avg_edge_size_bytes}")
    print(f"  estimated_canonical_text_mb: {rep.canonical_text_bytes/1e6:.1f}")

    # Summary
    print()
    print("=" * 72)
    print("Sub-Phase Summary")
    print("=" * 72)
    total_wall = sum(sp.wall_s for sp in subphases)
    total_cpu = sum(sp.cpu_s for sp in subphases)
    fmt = "{:<25} {:>8} {:>8} {:>10} {:>10} {:>6}"
    print(fmt.format("Phase", "wall_s", "cpu_s", "input", "output", "gc"))
    print("-" * 72)
    for sp in subphases:
        print(fmt.format(
            sp.name,
            f"{sp.wall_s:.3f}",
            f"{sp.cpu_s:.3f}",
            str(sp.input_count),
            str(sp.output_count),
            str(sp.gc_collections)
        ))
    print("-" * 72)
    print(fmt.format("TOTAL", f"{total_wall:.3f}", f"{total_cpu:.3f}", "", "", ""))

    # Save evidence
    evidence = {
        "subphases": [asdict(sp) for sp in subphases],
        "representation": asdict(rep),
        "totals": {"wall_s": total_wall, "cpu_s": total_cpu},
    }
    out = ROOT / "artifacts" / "adg_p8_subphase_profile.json"
    out.write_text(json.dumps(evidence, indent=2))
    print(f"\nEvidence saved: {out}")

    return evidence


if __name__ == "__main__":
    profile_scan_instrumented(ROOT, include_tests=True)
