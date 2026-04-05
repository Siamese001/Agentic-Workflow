"""ADG P8 v4 Profiler — exactness-first, write-path instrumented.

Addresses remaining critique points:
1. No forced gc.collect() between phases — real warm-path only
2. k-way merge uses full equality tuple, not hash — exact correctness
3. Samples the 3498 dropped edges to find exact field-level reason for mismatch
4. Compact-sort measured as full encode->sort->back-map pipeline
5. Real write path instrumented via correct imports
6. Determinism gate via subprocess fresh-process invocations

Usage:
    python tools/profile_adg_phases_v4.py [--skip-write] [--skip-determinism]
"""
from __future__ import annotations

import gc
import heapq
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psutil

PROC = psutil.Process()
SKIP_WRITE = "--skip-write" in sys.argv
SKIP_DETERMINISM = "--skip-determinism" in sys.argv


# ---------------------------------------------------------------------------
# Measurement (NO forced GC between phases)
# ---------------------------------------------------------------------------

@dataclass
class SP:
    name: str
    wall_s: float = 0.0
    cpu_s: float = 0.0
    rss_start_mb: float = 0.0
    rss_end_mb: float = 0.0
    gc0: int = 0
    gc1: int = 0
    gc2: int = 0
    input_count: int = 0
    output_count: int = 0
    notes: str = ""

    def display(self) -> None:
        rss_d = self.rss_end_mb - self.rss_start_mb
        print(
            f"  [{self.name:<35}] "
            f"wall={self.wall_s:>6.3f}s  cpu={self.cpu_s:>6.3f}s  "
            f"rss={rss_d:+5.0f}MB  "
            f"gc=[{self.gc0},{self.gc1},{self.gc2}]  "
            f"in={self.input_count:>8,}  out={self.output_count:>8,}"
            + (f"  {self.notes}" if self.notes else ""),
        )


def _cpu() -> float:
    t = PROC.cpu_times()
    return t.user + t.system


def _rss() -> float:
    return PROC.memory_info().rss / 1e6


def _gc() -> tuple[int, int, int]:
    s = gc.get_stats()
    return s[0]["collections"], s[1]["collections"], s[2]["collections"]


def measure(name: str, func, *args, **kwargs) -> tuple[SP, Any]:
    """Measure a phase without forcing GC — real warm-path behavior."""
    g0, g1, g2 = _gc()
    cpu0 = _cpu()
    t0 = time.perf_counter()
    rss0 = _rss()

    result = func(*args, **kwargs)

    wall = time.perf_counter() - t0
    ng0, ng1, ng2 = _gc()
    sp = SP(
        name=name,
        wall_s=round(wall, 4),
        cpu_s=round(_cpu() - cpu0, 4),
        rss_start_mb=round(rss0, 1),
        rss_end_mb=round(_rss(), 1),
        gc0=ng0 - g0, gc1=ng1 - g1, gc2=ng2 - g2,
    )
    return sp, result


# ---------------------------------------------------------------------------
# Exact k-way merge using full equality tuple (not hash)
# ---------------------------------------------------------------------------

def _edge_equality_tuple(e) -> tuple:
    """All fields that participate in Edge.__eq__ (frozen dataclass = all fields)."""
    return (
        e.from_name, e.relation_type, e.to_name, e.edge_kind,
        e.source_file, e.line_no, e.symbol,
        e.semantic_type, e.confidence,
        e.source_span_start, e.source_span_end,
        e.source_span_line, e.source_span_column,
        e.target_span_start, e.target_span_end,
        e.target_span_line, e.target_span_column,
        e.dynamic_resolution,
    )


def kway_merge_exact(sorted_streams: list[list], sort_key_fn, eq_tuple_fn) -> list:
    """Merge N sorted streams; dedup by full equality tuple, not hash.

    Each stream must be sorted by sort_key_fn on the same total order.
    Uses heapq.merge for O(n log k) merge, then streaming exact dedup.
    """
    merged = heapq.merge(*sorted_streams, key=sort_key_fn)
    result = []
    seen: set[tuple] = set()
    for item in merged:
        eq = eq_tuple_fn(item)
        if eq not in seen:
            seen.add(eq)
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# Compact sort: full encode -> sort -> back-map pipeline
# ---------------------------------------------------------------------------

def compact_sort_pipeline(edges, sort_key_fn):
    """Full pipeline: build vocab -> encode to int tuples -> sort -> back-map.

    Returns (sorted_edges, encode_s, sort_s, decode_s).
    """
    # Encode: build vocab maps
    t0 = time.perf_counter()
    from_map: dict[str, int] = {}
    to_map: dict[str, int] = {}
    rel_map: dict[str, int] = {}
    file_map: dict[str, int] = {}
    ek_map: dict[str, int] = {}

    encoded: list[tuple] = []
    for e in edges:
        fi = from_map.setdefault(e.from_name, len(from_map))
        ri = rel_map.setdefault(e.relation_type, len(rel_map))
        ti = to_map.setdefault(e.to_name, len(to_map))
        fli = file_map.setdefault(e.source_file, len(file_map))
        eki = ek_map.setdefault(e.edge_kind, len(ek_map))
        # Sort key mirrors _EDGE_SORT_KEY: (from_name, relation_type, to_name, edge_kind, source_file, line_no, symbol)
        # Using IDs preserves same relative ordering IF vocab is built in sorted order
        encoded.append((fi, ri, ti, eki, fli, e.line_no, e))
    encode_s = time.perf_counter() - t0

    # Sort on int prefix (fi, ri, ti, eki, fli, line_no) — stable, no string compare
    t0 = time.perf_counter()
    encoded.sort(key=lambda x: x[:6])
    sort_s = time.perf_counter() - t0

    # Back-map: extract original Edge objects in sorted order
    t0 = time.perf_counter()
    result = [x[6] for x in encoded]
    decode_s = time.perf_counter() - t0

    return result, encode_s, sort_s, decode_s


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

    subphases: list[SP] = []

    print("=" * 80)
    print("ADG P8 v4 — Exactness-First, Write-Path Instrumented")
    print(f"pid={os.getpid()}  logical={psutil.cpu_count(logical=True)}  "
          f"physical={psutil.cpu_count(logical=False)}")
    print(f"skip_write={SKIP_WRITE}  skip_determinism={SKIP_DETERMINISM}")
    print("=" * 80)

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
    cache = ScanCache.load(cache_path) if cache_path.exists() else ScanCache()
    normalizer = IdentityNormalizer(repo_root=ROOT)
    normalizer._get_known_files()

    # ── Phase A: File scan (cache replay) ────────────────────────────────────
    sp, all_files = measure("A1_file_discovery", lambda: list(_iter_python_files(ROOT, include_tests=True)))
    sp.output_count = len(all_files)
    subphases.append(sp); sp.display()

    sp, file_hashes = measure("A2_file_hashing", lambda: {f: file_hash(f) for f in all_files})
    sp.input_count = len(all_files); sp.output_count = len(file_hashes)
    subphases.append(sp); sp.display()

    all_edges: list[Edge] = []

    def _replay():
        edges = []
        for f in all_files:
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            fhash = file_hashes[f]
            cached, _, _, hit = cache.get(rel, fhash)
            if hit and cached is not None:
                for d in cached:
                    edges.append(Edge(**d))
            else:
                fe, _, _, _ = _scan_file(f, ROOT, True, normalizer, "full")
                edges.extend(fe)
        return edges

    sp, all_edges = measure("A3_cache_replay", _replay)
    sp.input_count = len(all_files); sp.output_count = len(all_edges)
    subphases.append(sp); sp.display()

    # ── Phase B: Current pipeline (set + sort) ───────────────────────────────
    sp, edge_set = measure("B1_set_dedup", lambda: set(all_edges))
    sp.input_count = len(all_edges); sp.output_count = len(edge_set)
    subphases.append(sp); sp.display()

    sp, sorted_edges = measure("B2_sort_current", lambda: sorted(edge_set, key=_EDGE_SORT_KEY))
    sp.input_count = len(edge_set); sp.output_count = len(sorted_edges)
    subphases.append(sp); sp.display()

    # ── Phase C: Post-scan passes ─────────────────────────────────────────────
    def _mk(edges):
        sr = ScanResult(); sr.edges = edges; sr.modules = []; sr.manifest = ScanManifest()
        return sr

    sp, viol = measure("C1_violations", lambda: _emit_layer_violation_edges(_mk(sorted_edges)))
    sp.output_count = len(viol); subphases.append(sp); sp.display()

    sp, prop = measure("C2_propagation", lambda: _propagate_violations(_mk(sorted_edges + viol)))
    sp.output_count = len(prop); subphases.append(sp); sp.display()

    sp, cyc = measure("C3_cycles", lambda: _detect_cycles(_mk(sorted_edges)))
    sp.output_count = len(cyc); subphases.append(sp); sp.display()

    # ── Phase D: Merge-resort (current) ──────────────────────────────────────
    def _merge_current():
        merged = set(sorted_edges) | set(viol) | set(prop) | set(cyc)
        return sorted(merged, key=_EDGE_SORT_KEY)

    sp, final_current = measure("D1_merge_resort_current", _merge_current)
    sp.input_count = len(sorted_edges) + len(viol) + len(prop) + len(cyc)
    sp.output_count = len(final_current)
    subphases.append(sp); sp.display()

    # ── Phase D_ALT: k-way exact merge ───────────────────────────────────────
    def _merge_kway_exact():
        viol_s = sorted(viol, key=_EDGE_SORT_KEY)
        prop_s = sorted(prop, key=_EDGE_SORT_KEY)
        cyc_s = sorted(cyc, key=_EDGE_SORT_KEY)
        return kway_merge_exact(
            [sorted_edges, viol_s, prop_s, cyc_s],
            sort_key_fn=_EDGE_SORT_KEY,
            eq_tuple_fn=_edge_equality_tuple,
        )

    sp, final_kway = measure("D2_merge_kway_exact", _merge_kway_exact)
    sp.input_count = len(sorted_edges) + len(viol) + len(prop) + len(cyc)
    sp.output_count = len(final_kway)
    subphases.append(sp); sp.display()

    match_count = len(final_current) == len(final_kway)
    print(f"\n  k-way count match: {match_count}  ({len(final_current)} vs {len(final_kway)})")

    # ── Diagnose the mismatch ─────────────────────────────────────────────────
    if not match_count:
        print("\n  === Mismatch Diagnosis ===")
        current_set = {_edge_equality_tuple(e) for e in final_current}
        kway_set = {_edge_equality_tuple(e) for e in final_kway}
        only_in_current = current_set - kway_set
        only_in_kway = kway_set - current_set
        print(f"  only_in_current: {len(only_in_current)}")
        print(f"  only_in_kway:    {len(only_in_kway)}")

        if only_in_current:
            # Sample up to 3 dropped edges, show all fields
            eq_to_edge = {_edge_equality_tuple(e): e for e in final_current}
            sample = list(only_in_current)[:3]
            print("\n  Sample of edges only in current (union-resort) — these are dropped by k-way:")
            for eq in sample:
                e = eq_to_edge.get(eq)
                if e:
                    print(f"    from={e.from_name[:60]}")
                    print(f"    rel={e.relation_type}  kind={e.edge_kind}  line={e.line_no}")
                    print(f"    to={e.to_name[:60]}")
                    print(f"    semantic_type={e.semantic_type}  confidence={e.confidence}")
                    print(f"    dynamic_resolution={e.dynamic_resolution!r}")
                    print()

        # Check if k-way sort key collisions are the cause
        # Edges with same sort key but different equality tuple
        from itertools import groupby
        collision_count = 0
        for key, group in groupby(sorted_edges, key=_EDGE_SORT_KEY):
            grp = list(group)
            if len(grp) > 1:
                collision_count += len(grp) - 1
        print(f"  sort-key collisions in base sorted_edges: {collision_count}")
        # Check viol stream
        for key, group in groupby(sorted(viol, key=_EDGE_SORT_KEY), key=_EDGE_SORT_KEY):
            grp = list(group)
            if len(grp) > 1:
                collision_count += len(grp) - 1
        print(f"  sort-key collisions including viol: {collision_count}")

    # ── Phase E: W1b dedup ───────────────────────────────────────────────────
    def _w1b(edges):
        seen: set[tuple[str, str, str, int]] = set()
        out: list[Edge] = []
        for e in edges:
            k = (e.from_name, e.relation_type, e.to_name, e.line_no)
            if k not in seen:
                seen.add(k)
                out.append(e)
        return out

    sp, w1b = measure("E1_w1b_dedup", lambda: _w1b(final_current))
    sp.input_count = len(final_current); sp.output_count = len(w1b)
    subphases.append(sp); sp.display()
    print(f"  w1b removed: {len(final_current) - len(w1b):,}")

    # ── Phase F: Digest ───────────────────────────────────────────────────────
    def _digest(edges):
        sr = ScanResult(); sr.edges = edges; sr.compute_digest(); return sr.digest

    sp, final_digest = measure("F1_final_digest", lambda: _digest(w1b))
    sp.input_count = len(w1b); subphases.append(sp); sp.display()
    print(f"  digest: {final_digest[:32]}...")

    # ── Phase G: Compact sort — full encode->sort->back-map pipeline ─────────
    print("\n  === Compact Sort: Full Pipeline ===")

    # NOTE: vocab must be built from the same total-order as string sort to be equivalent.
    # We build vocab in string-sorted order so int IDs preserve relative ordering.
    all_from_sorted = sorted({e.from_name for e in w1b})
    all_rel_sorted = sorted({e.relation_type for e in w1b})
    all_to_sorted = sorted({e.to_name for e in w1b})
    all_ek_sorted = sorted({e.edge_kind for e in w1b})
    all_file_sorted = sorted({e.source_file for e in w1b})

    from_id = {s: i for i, s in enumerate(all_from_sorted)}
    rel_id = {s: i for i, s in enumerate(all_rel_sorted)}
    to_id = {s: i for i, s in enumerate(all_to_sorted)}
    ek_id = {s: i for i, s in enumerate(all_ek_sorted)}
    file_id = {s: i for i, s in enumerate(all_file_sorted)}

    # Shuffle w1b to remove pre-sort advantage
    import random
    shuffled = w1b.copy()
    random.shuffle(shuffled)

    # G1: encode (with pre-sorted vocab)
    def _encode():
        return [(from_id[e.from_name], rel_id[e.relation_type], to_id[e.to_name],
                 ek_id[e.edge_kind], file_id[e.source_file], e.line_no, i)
                for i, e in enumerate(shuffled)]

    sp, encoded = measure("G1_compact_encode", _encode)
    sp.input_count = len(shuffled); sp.output_count = len(encoded)
    subphases.append(sp); sp.display()

    # G2: sort compact int tuples
    sp, sorted_compact = measure("G2_compact_sort_ints", lambda: sorted(encoded, key=lambda x: x[:6]))
    sp.input_count = len(encoded); sp.output_count = len(sorted_compact)
    subphases.append(sp); sp.display()

    # G3: back-map to Edge objects in sorted order
    sp, compact_result = measure("G3_compact_backresolve", lambda: [shuffled[x[6]] for x in sorted_compact])
    sp.input_count = len(sorted_compact); sp.output_count = len(compact_result)
    subphases.append(sp); sp.display()

    # G4: verify compact sort matches string sort (same total order)
    compact_keys = [_EDGE_SORT_KEY(e) for e in compact_result[:100]]
    string_keys = [_EDGE_SORT_KEY(e) for e in w1b[:100]]
    order_match = compact_keys == string_keys
    print(f"  compact sort order matches string sort (first 100): {order_match}")
    if not order_match:
        for i, (ck, sk) in enumerate(zip(compact_keys, string_keys)):
            if ck != sk:
                print(f"  first mismatch at index {i}: compact={ck[:2]}  string={sk[:2]}")
                break

    compact_total_wall = (
        next(s.wall_s for s in subphases if s.name == "G1_compact_encode") +
        next(s.wall_s for s in subphases if s.name == "G2_compact_sort_ints") +
        next(s.wall_s for s in subphases if s.name == "G3_compact_backresolve")
    )
    string_sort_wall = next(s.wall_s for s in subphases if s.name == "B2_sort_current")
    print(f"  compact pipeline total: {compact_total_wall:.3f}s  vs string sort: {string_sort_wall:.3f}s  "
          f"ratio: {string_sort_wall/compact_total_wall:.1f}x")

    # ── Phase H: Real write path ─────────────────────────────────────────────
    if not SKIP_WRITE:
        print("\n  === Real Write Path ===")
        try:
            from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
            from agentic_core.adg.artifact.builder_types import build_artifact

            # Build a minimal ScanResult to pass to build_artifact
            scan_result = ScanResult()
            scan_result.edges = w1b
            scan_result.modules = [str(f.relative_to(ROOT)).replace("\\", "/") for f in all_files]
            scan_result.manifest = ScanManifest()
            scan_result.digest = final_digest

            sp, artifact = measure("H1_build_artifact", lambda: build_artifact(scan_result, repo_root=ROOT))
            sp.input_count = len(w1b)
            sp.output_count = len(artifact.entities) if hasattr(artifact, "entities") else 0
            subphases.append(sp); sp.display()

            tmp_dir = Path(tempfile.mkdtemp(prefix="adg_write_profile_"))
            ts_str = time.strftime("%m%d%Y_%H%M%S")

            sp, paths = measure("H2_write_all_artifacts",
                                lambda: write_all_artifacts(artifact, out_dir=tmp_dir, ts=ts_str))
            sp.output_count = len(list(tmp_dir.rglob("*")))
            subphases.append(sp); sp.display()

            for f in sorted(tmp_dir.rglob("*")):
                if f.is_file():
                    print(f"    written: {f.name:<50} {f.stat().st_size/1e6:.2f}MB")

            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

        except Exception as exc:
            print(f"  Write path FAILED: {exc}")
    else:
        print("  [Write path skipped — use without --skip-write to measure]")

    # ── Phase I: Determinism via fresh subprocesses ───────────────────────────
    if not SKIP_DETERMINISM:
        print("\n  === 3x Determinism Gate (fresh processes) ===")

        det_script = ROOT / "tools" / "_adg_digest_only.py"
        det_script.write_text(
            "import sys, os\n"
            "sys.path.insert(0, r'" + str(ROOT) + "')\n"
            "os.environ['ADG_SKIP_SELF_TEST'] = '1'\n"
            "from pathlib import Path\n"
            "from agentic_core.adg.extraction.static_scanner import ADGStaticScanner\n"
            "ROOT = Path(r'" + str(ROOT) + "')\n"
            "cache_path = ROOT / 'artifacts' / 'adg' / 'cache' / 'scan_result_cache.json'\n"
            "scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)\n"
            "result = scanner.scan()\n"
            "print(f'EDGES={len(result.edges)}')\n"
            "print(f'DIGEST={result.digest}')\n",
        )

        det_digests = []
        det_edge_counts = []
        for run_n in range(1, 4):
            t0 = time.perf_counter()
            try:
                proc = subprocess.run(  # noqa: S603
                    [sys.executable, str(det_script)],
                    capture_output=True, text=True, timeout=120, cwd=str(ROOT),
                )
                wall = time.perf_counter() - t0
                lines = proc.stdout.strip().splitlines()
                digest = next((l.split("=", 1)[1] for l in lines if l.startswith("DIGEST=")), "ERROR")
                edges = next((l.split("=", 1)[1] for l in lines if l.startswith("EDGES=")), "?")
                det_digests.append(digest)
                det_edge_counts.append(edges)
                match = "✓" if (len(det_digests) == 1 or digest == det_digests[0]) else "✗ MISMATCH"
                print(f"  run{run_n}: wall={wall:.2f}s  edges={edges}  digest={digest[:32]}...  {match}")
                if proc.returncode != 0 and proc.stderr:
                    errs = [l for l in proc.stderr.splitlines() if "Error" in l or "FATAL" in l]
                    for e in errs[:3]:
                        print(f"    stderr: {e}")
            except Exception as exc:
                print(f"  run{run_n}: FAILED — {exc}")
                det_digests.append("FAILED")

        det_script.unlink(missing_ok=True)

        all_match = len(set(det_digests)) == 1 and det_digests[0] not in ("ERROR", "FAILED")
        print(f"  Determinism gate: {'PASS' if all_match else 'FAIL'}")
        if not all_match and len(set(det_digests)) > 1:
            print(f"  distinct digests: {set(det_digests)}")
    else:
        det_digests = []
        print("  [Determinism gate skipped — use without --skip-determinism]")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Phase Summary (no forced GC — real warm-path timing)")
    print("=" * 80)
    fmt = "{:<38} {:>7} {:>7} {:>8} {:>8} {:>8}"
    print(fmt.format("Phase", "wall_s", "cpu_s", "gc[0,1]", "in", "out"))
    print("-" * 80)
    total_wall = total_cpu = 0.0
    for sp in subphases:
        total_wall += sp.wall_s; total_cpu += sp.cpu_s
        print(fmt.format(
            sp.name[:38], f"{sp.wall_s:.3f}", f"{sp.cpu_s:.3f}",
            f"[{sp.gc0},{sp.gc1}]",
            f"{sp.input_count:,}"[:8], f"{sp.output_count:,}"[:8],
        ))
    print("-" * 80)
    print(fmt.format("TOTAL", f"{total_wall:.3f}", f"{total_cpu:.3f}", "", "", ""))

    print()
    print("=" * 80)
    print("Reconciliation vs 13.198s full-scan baseline")
    print("=" * 80)
    baseline = 13.198
    print(f"  Measured sub-phases (no GC tax):  {total_wall:.3f}s")
    print(f"  Full-scan baseline:               {baseline:.3f}s")
    delta = baseline - total_wall
    print(f"  Unaccounted (write+reports+plumb): {delta:.3f}s")

    # Gain estimates if k-way + compact land correctly
    kway_wall = next((s.wall_s for s in subphases if "kway" in s.name), None)
    current_merge = next((s.wall_s for s in subphases if "current" in s.name and "merge" in s.name), None)
    b2 = next((s.wall_s for s in subphases if s.name == "B2_sort_current"), None)
    g_total = next((s.wall_s for s in subphases if s.name == "G1_compact_encode"), None)
    g2 = next((s.wall_s for s in subphases if s.name == "G2_compact_sort_ints"), None)
    g3 = next((s.wall_s for s in subphases if s.name == "G3_compact_backresolve"), None)

    if kway_wall and current_merge:
        merge_gain = current_merge - kway_wall
        print(f"\n  merge gain (if k-way correctness proven): {merge_gain:.3f}s → "
              f"{baseline:.3f} → {baseline-merge_gain:.3f}s = {baseline/(baseline-merge_gain):.2f}x")
    if b2 and g_total and g2 and g3:
        pipeline_wall = g_total + g2 + g3
        sort_gain = b2 - pipeline_wall
        print(f"  sort gain (compact pipeline):             {sort_gain:.3f}s → "
              f"{baseline:.3f} → {baseline-sort_gain:.3f}s = {baseline/(baseline-sort_gain):.2f}x")
        if kway_wall and current_merge:
            combined = merge_gain + sort_gain
            print(f"  combined gain (both, independent):       {combined:.3f}s → "
                  f"{baseline:.3f} → {baseline-combined:.3f}s = {baseline/(baseline-combined):.2f}x")
            print("  NOTE: gains may overlap — treat as upper bound until integrated")

    # Save evidence
    evidence = {
        "phases": [asdict(sp) for sp in subphases],
        "totals": {"wall_s": round(total_wall, 3), "cpu_s": round(total_cpu, 3)},
        "baseline_s": baseline,
        "unaccounted_s": round(delta, 3),
        "kway_count_match": match_count,
        "determinism": {"digests": det_digests, "pass": len(set(det_digests)) == 1} if det_digests else {},
    }
    out = ROOT / "artifacts" / "adg_p8_v4_profile.json"
    out.write_text(json.dumps(evidence, indent=2))
    print(f"\nEvidence saved: {out}")


if __name__ == "__main__":
    run()
