"""CPU optimization baseline benchmark script.

Measures wall-clock time for every major CPU-bound workload in the repo.
Run with: python tools/_benchmark_cpu.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import multiprocessing
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Top-level picklable functions for ProcessPool ──────────────────────────


def _parse_file(path: str) -> int:
    """Parse a Python file with AST, return node count."""
    try:
        data = pathlib.Path(path).read_bytes()
        return len(list(ast.walk(ast.parse(data))))
    except Exception:
        return 0


def _hash_file(path: str) -> str:
    """SHA-256 hash a file."""
    try:
        return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except Exception:
        return ""


def _parse_and_visit(path: str) -> tuple[int, int, int]:
    """Full visitor walk: parse + count FunctionDef + ClassDef + Import nodes."""
    try:
        data = pathlib.Path(path).read_bytes()
        tree = ast.parse(data)
        funcs = classes = imports = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
        return funcs, classes, imports
    except Exception:
        return 0, 0, 0


# ── Benchmark helpers ──────────────────────────────────────────────────────


def _fmt(val: float) -> str:
    return f"{val:.3f}s"


def run_benchmarks() -> dict:
    from agentic_core.adg.extraction.static_scanner import _iter_python_files

    print("=" * 70)
    print("CPU OPTIMIZATION BASELINE BENCHMARK")
    print(f"Python {sys.version.split()[0]}  |  {multiprocessing.cpu_count()} logical CPUs")
    print("=" * 70)

    results: dict = {}

    # ── B1: File discovery ──────────────────────────────────────────────────
    t0 = time.perf_counter()
    files = [str(p) for p in _iter_python_files(ROOT)]
    t1 = time.perf_counter()
    results["file_discovery"] = {"files": len(files), "wall_s": t1 - t0}
    print(f"\n[B1] File discovery: {len(files)} files in {_fmt(t1 - t0)}")

    # ── B2: Serial AST parse ────────────────────────────────────────────────
    t0 = time.perf_counter()
    serial_counts = [_parse_file(f) for f in files]
    t1 = time.perf_counter()
    serial_ast = t1 - t0
    results["serial_ast_parse"] = {
        "files": len(files),
        "wall_s": serial_ast,
        "files_per_s": len(files) / serial_ast,
    }
    print(
        f"[B2] Serial AST parse: {len(files)} files in {_fmt(serial_ast)} "
        f"({len(files) / serial_ast:.0f} files/s)"
    )

    # ── B3: Parallel AST parse (ProcessPool) — worker sweep ────────────────
    print("[B3] Parallel AST parse (ProcessPool) sweep:")
    best_parallel = serial_ast
    best_workers = 1
    for nw in [8, 16, 24, 32]:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=nw) as ex:
            _ = list(ex.map(_parse_file, files, chunksize=60))
        t1 = time.perf_counter()
        wall = t1 - t0
        speedup = serial_ast / wall
        results[f"parallel_ast_w{nw}"] = {"wall_s": wall, "speedup": speedup}
        print(f"     w={nw:2d}: {_fmt(wall)}  speedup={speedup:.2f}x  ({len(files) / wall:.0f} files/s)")
        if wall < best_parallel:
            best_parallel = wall
            best_workers = nw
    print(f"     Best: w={best_workers}  ({serial_ast / best_parallel:.2f}x speedup)")

    # ── B4: Serial full visitor (parse+walk) — simulates scanner ───────────
    t0 = time.perf_counter()
    serial_visit = [_parse_and_visit(f) for f in files]
    t1 = time.perf_counter()
    serial_visit_time = t1 - t0
    results["serial_full_visitor"] = {"wall_s": serial_visit_time}
    print(
        f"\n[B4] Serial full visitor (parse+walk): {_fmt(serial_visit_time)} "
        f"({len(files) / serial_visit_time:.0f} files/s)"
    )

    # ── B5: Parallel full visitor sweep ─────────────────────────────────────
    print("[B5] Parallel full visitor sweep:")
    for nw in [16, 24, 32]:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=nw) as ex:
            _ = list(ex.map(_parse_and_visit, files, chunksize=60))
        t1 = time.perf_counter()
        wall = t1 - t0
        speedup = serial_visit_time / wall
        results[f"parallel_visitor_w{nw}"] = {"wall_s": wall, "speedup": speedup}
        print(f"     w={nw:2d}: {_fmt(wall)}  speedup={speedup:.2f}x")

    # ── B6: SHA-256 hashing (serial vs parallel) ────────────────────────────
    t0 = time.perf_counter()
    _ = [_hash_file(f) for f in files]
    t1 = time.perf_counter()
    serial_hash = t1 - t0
    results["serial_hash"] = {"wall_s": serial_hash}
    print(
        f"\n[B6] Serial SHA-256 hash: {len(files)} files in {_fmt(serial_hash)} "
        f"({len(files) / serial_hash:.0f} files/s)"
    )

    # Thread pool for I/O-bound hashing
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=32) as ex:
        _ = list(ex.map(_hash_file, files))
    t1 = time.perf_counter()
    thread_hash = t1 - t0
    print(f"     ThreadPool w=32: {_fmt(thread_hash)}  speedup={serial_hash / thread_hash:.2f}x")
    results["thread_hash_w32"] = {"wall_s": thread_hash, "speedup": serial_hash / thread_hash}

    # ── B7: JSON serialization (report gen workload) ─────────────────────────
    sample_data = {
        "modules": [{"id": i, "name": f"mod_{i}", "layer": "L2"} for i in range(7500)],
        "edges": [{"src": i, "dst": i + 1, "rel": "calls", "kind": "static"} for i in range(50000)],
    }
    t0 = time.perf_counter()
    for _ in range(10):
        s = json.dumps(sample_data, sort_keys=True)
    t1 = time.perf_counter()
    json_dumps = (t1 - t0) / 10
    results["json_dumps_50k_edges"] = {"wall_ms": json_dumps * 1000, "size_mb": len(s) / 1e6}
    print(f"\n[B7] JSON dumps (50k edges, {len(s) / 1e6:.1f} MB): {json_dumps * 1000:.1f}ms/iter")

    # orjson if available
    try:
        import orjson

        t0 = time.perf_counter()
        for _ in range(10):
            ob = orjson.dumps(sample_data)
        t1 = time.perf_counter()
        orjson_dumps = (t1 - t0) / 10
        speedup = json_dumps / orjson_dumps
        results["orjson_dumps"] = {"wall_ms": orjson_dumps * 1000, "speedup": speedup}
        print(f"     orjson dumps: {orjson_dumps * 1000:.1f}ms/iter  speedup={speedup:.2f}x")
    except ImportError:
        print("     orjson: not installed")

    # ── B8: ADG scan cache hit timing ────────────────────────────────────────
    import subprocess

    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    except Exception:
        commit = ""
    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
    if cache_path.exists():
        scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)
        t0 = time.perf_counter()
        res = scanner.scan(commit_sha=commit)
        t1 = time.perf_counter()
        full_scan = t1 - t0
        cache_rate = res.manifest.cache_hit_rate
        results["adg_full_scan"] = {
            "wall_s": full_scan,
            "modules": len(res.modules),
            "edges": len(res.edges),
            "cache_hit_rate": cache_rate,
        }
        print(
            f"\n[B8] ADG full scan: {len(res.modules)} modules, "
            f"{len(res.edges)} edges in {_fmt(full_scan)} "
            f"(cache={cache_rate:.1%})"
        )
    else:
        print("\n[B8] ADG full scan: cache not found, skipping")

    # ── B9: pytest collection overhead ──────────────────────────────────────
    print("\n[B9] pytest collection timing:")
    for suite in ["tests/unit_min_deps", "tests/adg", "tests/governance", "tests/guardian"]:
        suite_path = ROOT / suite
        if not suite_path.exists():
            continue
        t0 = time.perf_counter()
        r = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite_path), "--collect-only", "-q", "--tb=no"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        t1 = time.perf_counter()
        # Extract collected count
        for line in r.stdout.splitlines():
            if "collected" in line or "selected" in line:
                count_info = line.strip()
                break
        else:
            count_info = "?"
        results[f"collect_{suite.split('/')[-1]}"] = {"wall_s": t1 - t0}
        print(f"     {suite:35s}: {_fmt(t1 - t0)}  ({count_info})")

    # ── B10: pytest execution (sequential) ──────────────────────────────────
    print("\n[B10] pytest execution (sequential):")
    for suite, label in [
        ("tests/unit_min_deps", "unit_min_deps"),
        ("tests/governance", "governance"),
        ("tests/guardian", "guardian"),
        ("tests/adg", "adg"),
    ]:
        suite_path = ROOT / suite
        if not suite_path.exists():
            continue
        t0 = time.perf_counter()
        r = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite_path), "-q", "--tb=no", "-x"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        t1 = time.perf_counter()
        wall = t1 - t0
        for line in r.stdout.splitlines():
            if "passed" in line or "failed" in line or "error" in line:
                summary = line.strip()
                break
        else:
            summary = r.returncode
        results[f"pytest_{label}"] = {"wall_s": wall, "returncode": r.returncode}
        print(f"     {suite:35s}: {_fmt(wall)}  {summary}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("BOTTLENECK CLASSIFICATION SUMMARY")
    print("=" * 70)
    if "serial_ast_parse" in results and "parallel_ast_w12" in results:
        best_w = max(
            [(k, v) for k, v in results.items() if k.startswith("parallel_ast_w")],
            key=lambda x: x[1].get("speedup", 0),
        )
        print(
            f"  AST parse (SCANNER): CPU-BOUND  serial={results['serial_ast_parse']['wall_s']:.3f}s  "
            f"best_parallel={best_w[1]['wall_s']:.3f}s ({best_w[1]['speedup']:.2f}x)  -> {best_w[0]}"
        )
    if "serial_hash" in results:
        print(
            f"  SHA-256 hashing:     I/O-BOUND   serial={results['serial_hash']['wall_s']:.3f}s  "
            f"thread8={results.get('thread_hash_w8', {}).get('wall_s', '?')}"
        )
    if "adg_full_scan" in results:
        r = results["adg_full_scan"]
        bottleneck = "CACHE-HIT FAST PATH" if r["cache_hit_rate"] > 0.95 else "CPU-BOUND"
        print(f"  ADG scan:            {bottleneck}  {r['wall_s']:.3f}s  cache={r['cache_hit_rate']:.1%}")

    return results


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmarks()
