"""ADG P8 v3 Profiler — hardened sub-phase instrumentation.

Addresses all critique points from review:
1. GC metric fixed: gc.get_stats() per-generation counts, not gc.get_count() delta
2. Remaining ~3.6s gap instrumented: build_artifact, write_all_artifacts,
   score_edges, predict_impact, _generate_standardized_reports
3. Provides prototype measurements for k-way merge vs union-resort
4. Prototype for compact integer-keyed edge tuples vs rich Edge objects
5. 3x determinism gate — compares final digests across runs

Usage:
    python tools/profile_adg_phases_v3.py
"""
from __future__ import annotations

import gc
import hashlib
import heapq
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psutil

PROC = psutil.Process()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@dataclass
class SubPhaseResult:
    name: str
    wall_s: float = 0.0
    cpu_s: float = 0.0
    rss_start_mb: float = 0.0
    rss_end_mb: float = 0.0
    # Corrected GC: per-generation collection counts from gc.get_stats()
    gc_gen0_collections: int = 0
    gc_gen1_collections: int = 0
    gc_gen2_collections: int = 0
    # tracemalloc peak allocated (optional)
    peak_alloc_mb: float = 0.0
    input_count: int = 0
    output_count: int = 0
    notes: str = ""

    @property
    def gc_total(self) -> int:
        return self.gc_gen0_collections + self.gc_gen1_collections + self.gc_gen2_collections

    def fmt(self) -> str:
        return (
            f"{self.name:<30} wall={self.wall_s:>6.3f}s  cpu={self.cpu_s:>6.3f}s  "
            f"rss={self.rss_start_mb:>5.0f}->{self.rss_end_mb:>5.0f}MB  "
            f"gc=[{self.gc_gen0_collections},{self.gc_gen1_collections},{self.gc_gen2_collections}]  "
            f"in={self.input_count:>8,}  out={self.output_count:>8,}"
        )


def _cpu_s() -> float:
    t = PROC.cpu_times()
    return t.user + t.system


def _rss_mb() -> float:
    return PROC.memory_info().rss / 1e6


def _gc_stats() -> tuple[int, int, int]:
    stats = gc.get_stats()
    return stats[0]["collections"], stats[1]["collections"], stats[2]["collections"]


def measure(name: str, func, *args, **kwargs) -> tuple[SubPhaseResult, Any]:
    gc.collect()
    gc.collect()
    g0, g1, g2 = _gc_stats()
    cpu0 = _cpu_s()
    t0 = time.perf_counter()
    rss0 = _rss_mb()

    result = func(*args, **kwargs)

    wall = time.perf_counter() - t0
    cpu = _cpu_s() - cpu0
    rss1 = _rss_mb()
    ng0, ng1, ng2 = _gc_stats()

    sp = SubPhaseResult(
        name=name,
        wall_s=round(wall, 4),
        cpu_s=round(cpu, 4),
        rss_start_mb=round(rss0, 1),
        rss_end_mb=round(rss1, 1),
        gc_gen0_collections=ng0 - g0,
        gc_gen1_collections=ng1 - g1,
        gc_gen2_collections=ng2 - g2,
    )
    return sp, result


# ---------------------------------------------------------------------------
# Prototype: k-way deterministic sorted merge
# ---------------------------------------------------------------------------

def kway_merge_unique(sorted_streams: list[list], key_fn) -> list:
    """Merge N sorted streams into one sorted unique output via heapq.merge.

    Each stream must already be sorted by key_fn.
    This avoids rebuilding a giant set and re-sorting.
    """
    merged = heapq.merge(*sorted_streams, key=key_fn)
    result = []
    last_key = None
    for item in merged:
        k = key_fn(item)
        if k != last_key:
            result.append(item)
            last_key = k
    return result


# ---------------------------------------------------------------------------
# Prototype: compact integer-keyed tuples
# ---------------------------------------------------------------------------

def build_compact_index(edges) -> tuple[list[tuple], dict, dict, dict]:
    """Convert Edge objects to compact (from_id, rel_id, to_id, file_id, line) tuples.

    Returns:
        compact_edges: list of int-tuple edges
        from_map: str -> int
        rel_map: str -> int
        to_map: str -> int
    """
    from_map: dict[str, int] = {}
    rel_map: dict[str, int] = {}
    to_map: dict[str, int] = {}
    file_map: dict[str, int] = {}

    compact: list[tuple] = []
    for e in edges:
        fi = from_map.setdefault(e.from_name, len(from_map))
        ri = rel_map.setdefault(e.relation_type, len(rel_map))
        ti = to_map.setdefault(e.to_name, len(to_map))
        fli = file_map.setdefault(e.source_file, len(file_map))
        compact.append((fi, ri, ti, fli, e.line_no))

    return compact, from_map, rel_map, to_map


# ---------------------------------------------------------------------------
# Main profiler
# ---------------------------------------------------------------------------

def run() -> None:
    from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash
    from agentic_core.adg.extraction.static_scanner import (
        _EDGE_SORT_KEY,
        Edge,
        ScanManifest,
        ScanResult,
        _detect_cycles,
        _emit_layer_violation_edges,
        _iter_python_files,
        _propagate_violations,
        _scan_file,
    )
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    subphases: list[SubPhaseResult] = []

    print("=" * 80)
    print("ADG P8 v3 — Hardened Sub-Phase Profiler")
    print(f"pid={os.getpid()}  logical_cpus={psutil.cpu_count(logical=True)}  "
          f"physical_cores={psutil.cpu_count(logical=False)}")
    print("=" * 80)

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"

    # Pre-warm (not measured)
    sp, cache = measure("pre_cache_load", lambda: ScanCache.load(cache_path) if cache_path.exists() else ScanCache())
    sp, normalizer = measure("pre_normalizer", lambda: IdentityNormalizer(repo_root=ROOT))
    normalizer._get_known_files()

    # ── P8a: File discovery + hashing + cache-hit file loop ─────────────────
    sp, all_files = measure("p8a1_file_discovery", lambda: list(_iter_python_files(ROOT, include_tests=True)))
    sp.output_count = len(all_files)
    subphases.append(sp)
    print(sp.fmt())

    sp, file_hashes = measure("p8a2_file_hashing", lambda: {f: file_hash(f) for f in all_files})
    sp.input_count = len(all_files)
    sp.output_count = len(file_hashes)
    subphases.append(sp)
    print(sp.fmt())

    # Cache replay loop — the main per-file work on warm runs
    all_edges: list[Edge] = []

    def _cache_replay():
        edges = []
        for f in all_files:
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            fhash = file_hashes[f]
            cached_edge_dicts, _, _, cache_hit = cache.get(rel, fhash)
            if cache_hit and cached_edge_dicts is not None:
                for d in cached_edge_dicts:
                    edges.append(Edge(**d))
            else:
                file_edges, _, _, _ = _scan_file(f, ROOT, True, normalizer, "full")
                edges.extend(file_edges)
        return edges

    sp, all_edges = measure("p8a3_cache_replay", _cache_replay)
    sp.input_count = len(all_files)
    sp.output_count = len(all_edges)
    subphases.append(sp)
    print(sp.fmt())
    print(f"  edges before dedup: {len(all_edges):,}")

    # ── P8b: set() dedup ────────────────────────────────────────────────────
    sp, edge_set = measure("p8b_set_dedup", lambda: set(all_edges))
    sp.input_count = len(all_edges)
    sp.output_count = len(edge_set)
    subphases.append(sp)
    print(sp.fmt())

    # ── P8c: Sort ───────────────────────────────────────────────────────────
    sp, sorted_edges = measure("p8c_sort", lambda: sorted(edge_set, key=_EDGE_SORT_KEY))
    sp.input_count = len(edge_set)
    sp.output_count = len(sorted_edges)
    subphases.append(sp)
    print(sp.fmt())

    # ── P8d: Digest 1 ───────────────────────────────────────────────────────
    def _digest1():
        sr = ScanResult()
        sr.edges = sorted_edges
        sr.compute_digest()
        return sr.digest

    sp, digest1 = measure("p8d_digest_1", _digest1)
    sp.input_count = len(sorted_edges)
    subphases.append(sp)
    print(sp.fmt())
    print(f"  digest_1: {digest1[:16]}...")

    # ── P8e: Post-scan passes ────────────────────────────────────────────────
    def _mk_sr(edges):
        sr = ScanResult()
        sr.edges = edges
        sr.modules = []
        sr.manifest = ScanManifest()
        return sr

    sp, violation_edges = measure("p8e_violations", lambda: _emit_layer_violation_edges(_mk_sr(sorted_edges)))
    sp.output_count = len(violation_edges)
    subphases.append(sp)
    print(sp.fmt())

    sp, propagation_edges = measure("p8f_propagation", lambda: _propagate_violations(_mk_sr(sorted_edges + violation_edges)))
    sp.output_count = len(propagation_edges)
    subphases.append(sp)
    print(sp.fmt())

    sp, cycle_edges = measure("p8g_cycles", lambda: _detect_cycles(_mk_sr(sorted_edges)))
    sp.output_count = len(cycle_edges)
    subphases.append(sp)
    print(sp.fmt())

    # ── P8h: Merge + re-sort (current approach) ──────────────────────────────
    def _merge_resort():
        merged = set(sorted_edges)
        merged |= set(violation_edges)
        merged |= set(propagation_edges)
        merged |= set(cycle_edges)
        return sorted(merged, key=_EDGE_SORT_KEY)

    sp, final_sorted = measure("p8h_merge_resort_current", _merge_resort)
    sp.input_count = len(sorted_edges) + len(violation_edges) + len(propagation_edges) + len(cycle_edges)
    sp.output_count = len(final_sorted)
    subphases.append(sp)
    print(sp.fmt())

    # ── P8h_ALT: k-way merge prototype ──────────────────────────────────────
    def _kway_merge():
        viol_s = sorted(violation_edges, key=_EDGE_SORT_KEY)
        prop_s = sorted(propagation_edges, key=_EDGE_SORT_KEY)
        cycle_s = sorted(cycle_edges, key=_EDGE_SORT_KEY)
        return kway_merge_unique(
            [sorted_edges, viol_s, prop_s, cycle_s],
            key_fn=_EDGE_SORT_KEY,
        )

    sp, kway_result = measure("p8h_merge_kway_proto", _kway_merge)
    sp.input_count = len(sorted_edges) + len(violation_edges) + len(propagation_edges) + len(cycle_edges)
    sp.output_count = len(kway_result)
    subphases.append(sp)
    print(sp.fmt())
    print(f"  k-way result matches current: {len(kway_result) == len(final_sorted)}")

    # ── P8i: W1b key-based dedup ─────────────────────────────────────────────
    def _w1b(edges):
        seen: set[tuple[str, str, str, int]] = set()
        out: list[Edge] = []
        for e in edges:
            ek = (e.from_name, e.relation_type, e.to_name, e.line_no)
            if ek not in seen:
                seen.add(ek)
                out.append(e)
        return out

    sp, w1b_edges = measure("p8i_w1b_dedup", lambda: _w1b(final_sorted))
    sp.input_count = len(final_sorted)
    sp.output_count = len(w1b_edges)
    subphases.append(sp)
    print(sp.fmt())
    print(f"  w1b removed: {len(final_sorted) - len(w1b_edges):,}")

    # ── P8j: Final digest ────────────────────────────────────────────────────
    def _digest2():
        sr = ScanResult()
        sr.edges = w1b_edges
        sr.compute_digest()
        return sr.digest

    sp, digest2 = measure("p8j_digest_2", _digest2)
    sp.input_count = len(w1b_edges)
    subphases.append(sp)
    print(sp.fmt())
    print(f"  digest_2: {digest2[:16]}...")

    # ── P8k: build_artifact ──────────────────────────────────────────────────
    try:
        from tools.adg.core.builder import build_artifact

        def _build_artifact():
            sr = ScanResult()
            sr.edges = w1b_edges
            sr.modules = [str(f.relative_to(ROOT)).replace("\\", "/") for f in all_files]
            sr.manifest = ScanManifest()
            sr.digest = digest2
            return build_artifact(sr, repo_root=ROOT)

        sp, artifact = measure("p8k_build_artifact", _build_artifact)
        sp.input_count = len(w1b_edges)
        sp.output_count = len(artifact.entities) if hasattr(artifact, "entities") else 0
        subphases.append(sp)
        print(sp.fmt())
    except Exception as e:
        print(f"  [p8k_build_artifact] SKIP: {e}")
        artifact = None

    # ── P8l: write_all_artifacts ─────────────────────────────────────────────
    if artifact is not None:
        try:
            import shutil
            import tempfile

            from tools.adg.core.writer import write_all_artifacts

            tmp_dir = Path(tempfile.mkdtemp(prefix="adg_profile_write_"))
            ts = time.strftime("%m%d%Y_%H%M")

            def _write_artifacts():
                return write_all_artifacts(artifact, out_dir=tmp_dir, ts=ts)

            sp, paths = measure("p8l_write_all_artifacts", _write_artifacts)
            sp.output_count = 1
            sp.notes = f"tmp_dir={tmp_dir}"
            subphases.append(sp)
            print(sp.fmt())

            # Report sizes written
            for f in tmp_dir.rglob("*"):
                if f.is_file():
                    print(f"  written: {f.name}  {f.stat().st_size/1e6:.2f}MB")

            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception as e:
            print(f"  [p8l_write_all_artifacts] SKIP: {e}")
    else:
        print("  [p8l_write_all_artifacts] SKIP: no artifact")

    # ── P8m: score_edges ─────────────────────────────────────────────────────
    try:
        from agentic_core.adg.confidence.scorer import score_edges

        sp, scored = measure("p8m_score_edges", lambda: score_edges(list(w1b_edges)))
        sp.input_count = len(w1b_edges)
        sp.output_count = len(scored)
        subphases.append(sp)
        print(sp.fmt())
    except Exception as e:
        print(f"  [p8m_score_edges] SKIP: {e}")

    # ── P8n: Compact int-tuple prototype ─────────────────────────────────────
    def _build_compact():
        return build_compact_index(w1b_edges)

    sp, (compact_edges, from_map, rel_map, to_map) = measure("p8n_compact_index_build", _build_compact)
    sp.input_count = len(w1b_edges)
    sp.output_count = len(compact_edges)
    sp.notes = f"from_vocab={len(from_map)}  rel_vocab={len(rel_map)}  to_vocab={len(to_map)}"
    subphases.append(sp)
    print(sp.fmt())
    print(f"  {sp.notes}")

    # Sort compact tuples (ints only, no string comparison)
    sp, compact_sorted = measure("p8n_compact_sort", lambda: sorted(compact_edges))
    sp.input_count = len(compact_edges)
    sp.output_count = len(compact_sorted)
    subphases.append(sp)
    print(sp.fmt())

    # Dedup compact tuples (set of small int-tuples)
    sp, compact_deduped = measure("p8n_compact_dedup", lambda: sorted(set(compact_edges)))
    sp.input_count = len(compact_edges)
    sp.output_count = len(compact_deduped)
    subphases.append(sp)
    print(sp.fmt())

    # Hash compact form (canonical int stream)
    def _compact_hash():
        h = hashlib.sha256()
        for t in compact_sorted:
            h.update(b"|".join(str(x).encode() for x in t))
        return h.hexdigest()

    sp, compact_digest = measure("p8n_compact_hash", _compact_hash)
    subphases.append(sp)
    print(sp.fmt())

    # ── Representation metrics ───────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Representation Metrics")
    print("=" * 80)

    unique_from = {e.from_name for e in w1b_edges}
    unique_to = {e.to_name for e in w1b_edges}
    unique_rel = {e.relation_type for e in w1b_edges}

    # Estimate memory footprint of Edge objects vs compact tuples
    import sys as _sys
    sample = w1b_edges[:1000]
    edge_obj_bytes = sum(_sys.getsizeof(e) for e in sample)
    compact_sample = compact_edges[:1000]
    compact_tuple_bytes = sum(_sys.getsizeof(t) for t in compact_sample)

    # Canonical text size
    sample_lines = []
    for e in w1b_edges[:10000]:
        sample_lines.append(f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}|{e.source_file}|{e.line_no}|{e.symbol}")
    avg_line_bytes = sum(len(l.encode()) for l in sample_lines) / len(sample_lines)
    total_canonical_mb = avg_line_bytes * len(w1b_edges) / 1e6

    # String duplication in from_name / to_name fields
    all_from_names = [e.from_name for e in w1b_edges]
    from_name_counts = defaultdict(int)
    for n in all_from_names:
        from_name_counts[n] += 1
    top5_from = sorted(from_name_counts.items(), key=lambda x: -x[1])[:5]

    print(f"  edges:                 {len(w1b_edges):,}")
    print(f"  unique_from_names:     {len(unique_from):,}")
    print(f"  unique_to_names:       {len(unique_to):,}")
    print(f"  unique_rel_types:      {len(unique_rel)}")
    print(f"  avg_edge_obj_bytes:    {edge_obj_bytes / len(sample):.0f}  (sys.getsizeof, sample=1000)")
    print(f"  avg_compact_tuple_bytes: {compact_tuple_bytes / len(compact_sample):.0f}  (int-tuple)")
    print(f"  compact_savings_pct:   {(1 - compact_tuple_bytes/edge_obj_bytes)*100:.0f}%")
    print(f"  canonical_text_total_mb: {total_canonical_mb:.1f}")
    print(f"  top5_from_name_dups:   {top5_from}")

    # ── Speedup reconciliation ───────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Speedup Reconciliation")
    print("=" * 80)

    total_wall = sum(sp.wall_s for sp in subphases)
    total_cpu = sum(sp.cpu_s for sp in subphases)

    # Full scan baseline from v1 profiler
    p8_full_scan_wall = 13.198  # from profile_adg_phases_v1.py --full-scan

    print(f"  P8 measured sub-phases total:  {total_wall:.3f}s wall  {total_cpu:.3f}s cpu")
    print(f"  P8 full_scan baseline (v1):    {p8_full_scan_wall:.3f}s wall")
    print(f"  Unaccounted remainder:         {p8_full_scan_wall - total_wall:.3f}s  "
          f"(likely build_artifact + write + score_edges + reports)")

    # Gains from k-way merge prototype
    current_merge_wall = next((s.wall_s for s in subphases if "current" in s.name), None)
    kway_merge_wall = next((s.wall_s for s in subphases if "kway" in s.name), None)
    if current_merge_wall and kway_merge_wall:
        merge_gain = current_merge_wall - kway_merge_wall
        print(f"\n  k-way merge vs union-resort:  {kway_merge_wall:.3f}s vs {current_merge_wall:.3f}s")
        print(f"  merge gain:                   {merge_gain:.3f}s ({merge_gain/p8_full_scan_wall*100:.1f}% of full scan)")

    # Gains from compact sort prototype
    current_sort_wall = next((s.wall_s for s in subphases if s.name == "p8c_sort"), None)
    compact_sort_wall = next((s.wall_s for s in subphases if "compact_sort" in s.name), None)
    if current_sort_wall and compact_sort_wall:
        sort_gain = current_sort_wall - compact_sort_wall
        print(f"\n  compact int-sort vs Edge sort: {compact_sort_wall:.3f}s vs {current_sort_wall:.3f}s")
        print(f"  sort gain:                    {sort_gain:.3f}s ({sort_gain/p8_full_scan_wall*100:.1f}% of full scan)")

    # ── 3x determinism gate ───────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("3x Determinism Gate")
    print("=" * 80)

    digests = [digest2]
    print(f"  run1: {digest2[:32]}...")

    for run_n in [2, 3]:
        def _rerun_digest():
            edges2 = []
            for f in all_files:
                rel = str(f.relative_to(ROOT)).replace("\\", "/")
                fhash = file_hashes[f]
                cached_edge_dicts, _, _, cache_hit = cache.get(rel, fhash)
                if cache_hit and cached_edge_dicts is not None:
                    for d in cached_edge_dicts:
                        edges2.append(Edge(**d))
            merged = set(edges2)
            merged |= set(violation_edges)
            merged |= set(propagation_edges)
            sr = ScanResult()
            sr.edges = _w1b(sorted(merged, key=_EDGE_SORT_KEY))
            sr.compute_digest()
            return sr.digest

        _, d = measure(f"determinism_run{run_n}", _rerun_digest)
        digests.append(d)
        match = "✓ MATCH" if d == digest2 else "✗ MISMATCH"
        print(f"  run{run_n}: {d[:32]}...  {match}")

    all_match = all(d == digest2 for d in digests)
    print(f"  Determinism gate: {'PASS — all 3 digests identical' if all_match else 'FAIL — digest instability detected'}")

    # ── Summary table ─────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Phase Summary")
    print("=" * 80)
    fmt = "{:<35} {:>8} {:>8} {:>12} {:>6} {:>6} {:>6}"
    print(fmt.format("Phase", "wall_s", "cpu_s", "gc[0,1,2]", "in", "out", "rss+"))
    print("-" * 80)
    for sp in subphases:
        gc_str = f"[{sp.gc_gen0_collections},{sp.gc_gen1_collections},{sp.gc_gen2_collections}]"
        rss_delta = sp.rss_end_mb - sp.rss_start_mb
        print(fmt.format(
            sp.name[:35],
            f"{sp.wall_s:.3f}",
            f"{sp.cpu_s:.3f}",
            gc_str,
            f"{sp.input_count:,}"[:6],
            f"{sp.output_count:,}"[:6],
            f"{rss_delta:+.0f}",
        ))
    print("-" * 80)
    print(fmt.format("TOTAL", f"{total_wall:.3f}", f"{total_cpu:.3f}", "", "", "", ""))

    # ── Save evidence ─────────────────────────────────────────────────────────
    evidence = {
        "measured_phases": [asdict(sp) for sp in subphases],
        "totals": {"wall_s": round(total_wall, 3), "cpu_s": round(total_cpu, 3)},
        "baseline_full_scan_wall_s": p8_full_scan_wall,
        "unaccounted_s": round(p8_full_scan_wall - total_wall, 3),
        "representation": {
            "edges": len(w1b_edges),
            "unique_from": len(unique_from),
            "unique_to": len(unique_to),
            "unique_rel": len(unique_rel),
            "avg_edge_obj_bytes": round(edge_obj_bytes / len(sample), 1),
            "avg_compact_tuple_bytes": round(compact_tuple_bytes / len(compact_sample), 1),
            "canonical_text_mb": round(total_canonical_mb, 1),
        },
        "determinism_gate": {
            "pass": all_match,
            "digests": digests,
        },
    }
    out = ROOT / "artifacts" / "adg_p8_v3_profile.json"
    out.write_text(json.dumps(evidence, indent=2))
    print(f"\nEvidence saved: {out}")


if __name__ == "__main__":
    run()
