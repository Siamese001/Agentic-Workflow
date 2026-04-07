"""Phase-level ADG profiler — proves or disproves scanner as CPU bottleneck.

Records wall time, process CPU time, bytes, file count, edge count, and peak RSS
for each discrete phase of the ADG scan pipeline.

Usage:
    python tools/profile_adg_phases.py [--full-scan]

Without --full-scan: measures all phases except actual _scan_file() calls.
With --full-scan: runs a complete timed scan (slow, ~60-120s).
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psutil

PROC = psutil.Process()


@dataclass
class PhaseResult:
    name: str
    wall_s: float = 0.0
    cpu_s: float = 0.0       # process CPU seconds (user+system)
    items: int = 0            # files / edges / whatever is counted
    bytes_io: int = 0
    edges_out: int = 0
    peak_rss_mb: float = 0.0
    notes: str = ""


def _snap_cpu() -> float:
    t = PROC.cpu_times()
    return t.user + t.system


def _snap_rss_mb() -> float:
    return PROC.memory_info().rss / 1e6


def run_phase(name: str, func, *args, **kwargs) -> tuple[PhaseResult, object]:
    cpu0 = _snap_cpu()
    t0 = time.perf_counter()
    rss0 = _snap_rss_mb()
    result = func(*args, **kwargs)
    wall = time.perf_counter() - t0
    cpu = _snap_cpu() - cpu0
    rss_peak = _snap_rss_mb()
    ph = PhaseResult(
        name=name,
        wall_s=round(wall, 3),
        cpu_s=round(cpu, 3),
        peak_rss_mb=round(max(rss0, rss_peak), 1),
    )
    return ph, result


def main(full_scan: bool = False) -> None:
    phases: list[PhaseResult] = []
    print("=" * 72)
    print("ADG Phase-Level Profiler")
    print(f"full_scan={full_scan}  pid={os.getpid()}  cpu_count={psutil.cpu_count(logical=True)}")
    print("=" * 72)

    # ── P1: File discovery ───────────────────────────────────────────────────
    from agentic_core.adg.extraction.static_scanner import _iter_python_files

    def _discover():
        return list(_iter_python_files(ROOT, include_tests=True))

    ph, all_files = run_phase("P1_file_discovery", _discover)
    ph.items = len(all_files)
    ph.notes = f"{len(all_files)} .py files found"
    phases.append(ph)
    print(f"[P1] file_discovery:  wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  files={len(all_files)}")

    # ── P2: stat + size survey ───────────────────────────────────────────────
    def _stat_files():
        total = 0
        size_dist = []
        for f in all_files:
            sz = f.stat().st_size
            total += sz
            size_dist.append(sz)
        return total, sorted(size_dist, reverse=True)

    ph, (total_bytes, size_dist) = run_phase("P2_stat_size", _stat_files)
    ph.items = len(all_files)
    ph.bytes_io = total_bytes
    ph.notes = (
        f"total={total_bytes/1e6:.1f}MB  "
        f"p50={size_dist[len(size_dist)//2]/1024:.1f}KB  "
        f"p99={size_dist[int(len(size_dist)*0.01)]/1024:.1f}KB  "
        f"max={size_dist[0]/1024:.1f}KB"
    )
    phases.append(ph)
    print(f"[P2] stat+size:       wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  {ph.notes}")

    # ── P3: File hashing (serial, as scan() does) ────────────────────────────
    from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

    def _hash_files():
        return {f: file_hash(f) for f in all_files}

    ph, file_hashes = run_phase("P3_file_hashing", _hash_files)
    ph.items = len(file_hashes)
    ph.bytes_io = total_bytes
    ph.notes = f"{total_bytes/1e6:.1f}MB hashed  throughput={total_bytes/max(ph.wall_s,0.001)/1e6:.0f}MB/s"
    phases.append(ph)
    print(f"[P3] file_hashing:    wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  {ph.notes}")

    # ── P4: Cache load ───────────────────────────────────────────────────────
    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"

    def _load_cache():
        return ScanCache.load(cache_path) if cache_path.exists() else ScanCache()

    ph, cache = run_phase("P4_cache_load", _load_cache)
    ph.notes = f"cache_path_exists={cache_path.exists()}  size_mb={cache_path.stat().st_size/1e6:.1f}" if cache_path.exists() else "no cache"
    phases.append(ph)
    print(f"[P4] cache_load:      wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  rss={ph.peak_rss_mb:.0f}MB  {ph.notes}")

    # ── P5: Cache hit check (per-file lookup, no actual parse) ───────────────
    def _check_cache_hits():
        hits, misses = 0, 0
        miss_files = []
        for f in all_files:
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            fhash = file_hashes[f]
            _, _, _, cache_hit = cache.get(rel, fhash)
            if cache_hit:
                hits += 1
            else:
                misses += 1
                miss_files.append((f, f.stat().st_size))
        return hits, misses, miss_files

    ph, (hits, misses, miss_files) = run_phase("P5_cache_check", _check_cache_hits)
    ph.items = hits + misses
    total_miss_bytes = sum(s for _, s in miss_files)
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    ph.notes = (
        f"hits={hits}  misses={misses}  hit_rate={hit_rate:.1%}  "
        f"miss_bytes={total_miss_bytes/1e6:.1f}MB"
    )
    phases.append(ph)
    print(f"[P5] cache_check:     wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  {ph.notes}")

    # Miss file size distribution
    miss_files.sort(key=lambda x: -x[1])
    print(f"     miss_files={len(miss_files)}  largest_kb=[{', '.join(str(round(s/1024,1)) for _,s in miss_files[:8])}]")

    # ── P6: AST parse cost estimate (sample 100 miss files) ─────────────────
    import ast as _ast

    sample_miss = miss_files[:100]
    sample_bytes = sum(s for _, s in sample_miss)

    def _ast_sample():
        node_counts = []
        for f, _ in sample_miss:
            try:
                src = f.read_bytes()
                tree = _ast.parse(src)
                node_counts.append(len(list(_ast.walk(tree))))
            except SyntaxError:
                node_counts.append(0)
        return node_counts

    ph, node_counts = run_phase("P6_ast_sample_parse", _ast_sample)
    ph.items = len(sample_miss)
    ph.bytes_io = sample_bytes
    avg_nodes = sum(node_counts) / max(len(node_counts), 1)
    throughput_files_s = len(sample_miss) / max(ph.wall_s, 0.001)
    # Extrapolate to all miss files
    extrap_s = len(miss_files) / max(throughput_files_s, 0.001) if miss_files else 0
    ph.notes = (
        f"sample={len(sample_miss)}files  avg_nodes={avg_nodes:.0f}  "
        f"{throughput_files_s:.0f}files/s  extrap_miss={extrap_s:.1f}s"
    )
    phases.append(ph)
    print(f"[P6] ast_sample:      wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  {ph.notes}")
    print(f"     ESTIMATE: {len(miss_files)} miss files would take ~{extrap_s:.1f}s (serial parse only)")

    # Full cache hit path: estimate time to replay cached edges
    cache_hit_files = hits
    extrap_cache_replay = ph.wall_s * (cache_hit_files / max(len(sample_miss), 1)) * 0.05  # cache replay ~5% of parse
    print(f"     ESTIMATE: {cache_hit_files} cache-hit files replay ~{extrap_cache_replay:.1f}s (fast path)")

    # ── P7: Normalizer warm-up ───────────────────────────────────────────────
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    def _normalizer_warmup():
        n = IdentityNormalizer(repo_root=ROOT)
        n._get_known_files()
        return n

    ph, normalizer = run_phase("P7_normalizer_warmup", _normalizer_warmup)
    ph.notes = "single os.walk to pre-warm known-files cache"
    phases.append(ph)
    print(f"[P7] normalizer_warm: wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s")

    # ── P8: Full scan (optional) ─────────────────────────────────────────────
    if full_scan:
        import subprocess

        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        try:
            commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
        except Exception:
            commit_sha = ""

        os.environ["ADG_SKIP_SELF_TEST"] = "1"

        scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)

        def _full_scan():
            return scanner.scan(commit_sha=commit_sha)

        ph, scan_result = run_phase("P8_full_scan", _full_scan)
        ph.items = len(scan_result.modules)
        ph.edges_out = len(scan_result.edges)
        ph.notes = (
            f"modules={len(scan_result.modules)}  edges={len(scan_result.edges)}  "
            f"cache_hit_rate={scan_result.manifest.cache_hit_rate:.1%}  "
            f"cache_hits={scan_result.manifest.cache_hits}  misses={scan_result.manifest.cache_misses}"
        )
        phases.append(ph)
        print(f"[P8] full_scan:       wall={ph.wall_s:.3f}s  cpu={ph.cpu_s:.3f}s  rss={ph.peak_rss_mb:.0f}MB")
        print(f"     {ph.notes}")

        # Derived: how much of full_scan is cache-miss parse vs hit replay?
        if ph.wall_s > 0:
            # From P6 we extrapolated miss parse time
            miss_parse_pct = min(100, extrap_s / ph.wall_s * 100)
            print(f"     DERIVED: miss_parse share of full_scan wall = ~{miss_parse_pct:.0f}%")

        os.environ.pop("ADG_SKIP_SELF_TEST", None)

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("PHASE SUMMARY")
    print("=" * 72)
    fmt = "{:<25} {:>8} {:>8} {:>10} {:>10}"
    print(fmt.format("Phase", "wall_s", "cpu_s", "items", "rss_mb"))
    print("-" * 72)
    for p in phases:
        print(fmt.format(p.name, f"{p.wall_s:.3f}", f"{p.cpu_s:.3f}", str(p.items), f"{p.peak_rss_mb:.0f}"))

    print()
    print("BOTTLENECK CANDIDATES:")
    if miss_files:
        print(f"  - Cache miss parse (serial):  ~{extrap_s:.1f}s for {len(miss_files)} files")
        print(f"  - Cache hit replay (fast):    ~{extrap_cache_replay:.1f}s for {hits} files")
    print(f"  - File hashing:               {phases[2].wall_s:.3f}s")
    print(f"  - Cache load:                 {phases[3].wall_s:.3f}s  ({ph.notes if cache_path.exists() else 'no cache'})")

    print()
    print("CPU UTILIZATION PREDICTION:")
    total_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)
    # If scanner is serial Python, it occupies ~1 thread
    single_thread_cpu_pct = 100.0 / total_cores
    print(f"  - 1 serial Python thread on {total_cores}-thread machine = ~{single_thread_cpu_pct:.1f}% total CPU")
    print("  - Observed 30-35% suggests 9-11 threads active simultaneously")
    print("  - Likely: cache deserialization + orjson + file I/O + parent/child overlap")

    # Save evidence
    out = ROOT / "artifacts" / "adg_phase_profile.json"
    out.write_text(json.dumps([asdict(p) for p in phases], indent=2))
    print(f"\nEvidence saved: {out}")


if __name__ == "__main__":
    full_scan = "--full-scan" in sys.argv
    main(full_scan=full_scan)
