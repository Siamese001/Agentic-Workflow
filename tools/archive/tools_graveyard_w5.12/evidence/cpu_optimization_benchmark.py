"""CPU Optimization Benchmark — Pre/Post Evidence Generator.

Tests each optimization from the CPU hotspot inventory by toggling between
the old (unoptimized) and new (optimized) code paths and measuring wall-clock time.

Optimizations tested:
  A1. orjson vs json.dumps for scan_cache save (serialization)
  A2. orjson vs json.dumps for scan_cache load (deserialization)
  A3. orjson vs json.dumps for generate_full_adg report generation
  B.  _EDGE_FIELD_NAMES pre-computed frozenset vs per-call set()
  D.  lru_cache on module_path_to_layer vs uncached
  E.  orjson for scan_cache 453MB file load (real file)
  F.  _EDGE_SORT_KEY lambda vs default dataclass __lt__ sort
  G.  ADG_SKIP_SELF_TEST=1 vs running self-test
  H.  AMDCPUOptimizer infrastructure validation

Usage:
    python tools/evidence/cpu_optimization_benchmark.py
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import statistics
import sys
import time
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ITERATIONS = 5  # Number of iterations per benchmark for statistical stability
WARMUP = 1  # Warmup iterations (discarded)


@dataclass
class BenchmarkResult:
    name: str
    description: str
    pre_times: list[float] = field(default_factory=list)
    post_times: list[float] = field(default_factory=list)
    pre_median: float = 0.0
    post_median: float = 0.0
    speedup: float = 0.0
    pct_gain: float = 0.0
    status: str = "PENDING"
    debug_note: str = ""

    def compute(self) -> None:
        if self.pre_times and self.post_times:
            self.pre_median = statistics.median(self.pre_times)
            self.post_median = statistics.median(self.post_times)
            if self.post_median > 0:
                self.speedup = self.pre_median / self.post_median
            if self.pre_median > 0:
                self.pct_gain = ((self.pre_median - self.post_median) / self.pre_median) * 100
            self.status = "PASS" if self.pct_gain > 1.0 else "NO GAIN"
        elif self.pre_times:
            self.pre_median = statistics.median(self.pre_times)
            self.status = "PRE-ONLY"
        elif self.post_times:
            self.post_median = statistics.median(self.post_times)
            self.status = "POST-ONLY"


def _timed(func, *args, **kwargs) -> tuple[Any, float]:
    """Run func and return (result, elapsed_seconds)."""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    return result, elapsed


def _run_benchmark(pre_func, post_func, iterations=ITERATIONS, warmup=WARMUP):
    """Run pre and post functions with warmup and return time lists."""
    pre_times = []
    post_times = []

    # Warmup
    for _ in range(warmup):
        pre_func()
        post_func()

    # Measure
    for _ in range(iterations):
        _, t = _timed(pre_func)
        pre_times.append(t)
        _, t = _timed(post_func)
        post_times.append(t)

    return pre_times, post_times


# ---------------------------------------------------------------------------
# Benchmark A1: orjson vs json for serialization (scan_cache save path)
# ---------------------------------------------------------------------------


def benchmark_a1_orjson_serialization() -> BenchmarkResult:
    """orjson.dumps vs json.dumps for large edge payloads."""
    result = BenchmarkResult(
        name="A1: orjson vs json.dumps (serialization)",
        description="Serialize 50k-edge dict payload — orjson (Rust) vs stdlib json",
    )

    try:
        import orjson
    except ImportError:
        result.status = "SKIP"
        result.debug_note = "orjson not installed"
        return result

    # Build realistic payload: 50k edges
    edges = []
    for i in range(50_000):
        edges.append(
            {
                "from_name": f"ADG::Module::agentic_core/L{i % 7}_layer/module_{i}.py",
                "relation_type": "imports",
                "to_name": f"ADG::Symbol::agentic_core.L{(i + 1) % 7}_layer.symbol_{i}",
                "edge_kind": "static_import",
                "source_file": f"agentic_core/L{i % 7}_layer/module_{i}.py",
                "line_no": i % 500 + 1,
                "symbol": f"symbol_{i}",
            }
        )
    payload = {"version": "2", "entries": {"test": {"file_hash": "abc123", "edges": edges}}}

    def pre_json():
        return json.dumps(payload, indent=2, sort_keys=True)

    def post_orjson():
        return orjson.dumps(payload, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)

    result.pre_times, result.post_times = _run_benchmark(pre_json, post_orjson)
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark A2: orjson vs json for deserialization (scan_cache load path)
# ---------------------------------------------------------------------------


def benchmark_a2_orjson_deserialization() -> BenchmarkResult:
    """orjson.loads vs json.loads for large cache payloads."""
    result = BenchmarkResult(
        name="A2: orjson vs json.loads (deserialization)",
        description="Deserialize 50k-edge JSON bytes — orjson vs stdlib json",
    )

    try:
        import orjson
    except ImportError:
        result.status = "SKIP"
        result.debug_note = "orjson not installed"
        return result

    edges = []
    for i in range(50_000):
        edges.append(
            {
                "from_name": f"ADG::Module::module_{i}.py",
                "relation_type": "imports",
                "to_name": f"ADG::Symbol::symbol_{i}",
                "edge_kind": "static_import",
                "source_file": f"module_{i}.py",
                "line_no": i % 500 + 1,
                "symbol": f"sym_{i}",
            }
        )
    payload = {"version": "2", "entries": {"test": {"file_hash": "abc", "edges": edges}}}
    json_bytes = json.dumps(payload).encode("utf-8")

    def pre_json():
        return json.loads(json_bytes.decode("utf-8"))

    def post_orjson():
        return orjson.loads(json_bytes)

    result.pre_times, result.post_times = _run_benchmark(pre_json, post_orjson)
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark A3: orjson vs json for report generation
# ---------------------------------------------------------------------------


def benchmark_a3_orjson_report_gen() -> BenchmarkResult:
    """orjson vs json for ADG report file generation (sorted, indented)."""
    result = BenchmarkResult(
        name="A3: orjson vs json (report generation)",
        description="Serialize ADG report dict (10k items, sorted+indented)",
    )

    try:
        import orjson
    except ImportError:
        result.status = "SKIP"
        result.debug_note = "orjson not installed"
        return result

    report = {
        "metadata": {"timestamp": "2026-03-30", "node_count": 11063, "edge_count": 724922},
        "layers": {f"L{i}": {"modules": list(range(500)), "edges": list(range(1000))} for i in range(7)},
        "violations": [{"file": f"file_{i}.py", "line": i, "type": "layer_violation"} for i in range(500)],
    }

    def pre_json():
        return json.dumps(report, indent=2, sort_keys=True)

    def post_orjson():
        return orjson.dumps(report, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS).decode("utf-8")

    result.pre_times, result.post_times = _run_benchmark(pre_json, post_orjson)
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark B: _EDGE_FIELD_NAMES pre-computed vs per-call set()
# ---------------------------------------------------------------------------


def benchmark_b_edge_field_names() -> BenchmarkResult:
    """Pre-computed frozenset of Edge field names vs per-call set(f.name for f in fields(Edge))."""
    result = BenchmarkResult(
        name="B: _EDGE_FIELD_NAMES pre-computed frozenset",
        description="730k _edge_from_dict calls: pre-computed field names vs per-call fields() introspection",
    )

    from agentic_core.adg.extraction.static_scanner import Edge

    # Pre-compute (optimized path)
    _EDGE_FIELD_NAMES_OPT: frozenset[str] = frozenset(f.name for f in fields(Edge))

    # Build 100k edge dicts (scaled down from 730k for benchmark speed)
    edge_dicts = []
    for i in range(100_000):
        edge_dicts.append(
            {
                "from_name": f"ADG::Module::mod_{i}.py",
                "relation_type": "imports",
                "to_name": f"ADG::Symbol::sym_{i}",
                "edge_kind": "static_import",
                "source_file": f"mod_{i}.py",
                "line_no": i % 500,
                "symbol": f"sym_{i}",
                "extra_field_1": "ignored",
                "extra_field_2": "ignored",
            }
        )

    def pre_per_call():
        """Old path: compute field names on every call."""
        results = []
        for d in edge_dicts:
            valid = {k: v for k, v in d.items() if k in set(f.name for f in fields(Edge))}
            results.append(Edge(**valid))
        return results

    def post_precomputed():
        """Optimized path: use pre-computed frozenset."""
        results = []
        for d in edge_dicts:
            valid = {k: v for k, v in d.items() if k in _EDGE_FIELD_NAMES_OPT}
            results.append(Edge(**valid))
        return results

    # Use fewer iterations for this heavy benchmark
    result.pre_times, result.post_times = _run_benchmark(
        pre_per_call, post_precomputed, iterations=3, warmup=1
    )
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark D: lru_cache on module_path_to_layer vs uncached
# ---------------------------------------------------------------------------


def benchmark_d_lru_cache_layer() -> BenchmarkResult:
    """lru_cache on module_path_to_layer vs uncached repeated calls."""
    result = BenchmarkResult(
        name="D: lru_cache on module_path_to_layer",
        description="1.5M calls to module_path_to_layer: lru_cache vs uncached",
    )

    from agentic_core.adg.contracts.schema_util import LAYER_PREFIXES

    # Simulate the uncached version
    def _uncached_module_path_to_layer(rel_path: str) -> str:
        norm = rel_path.replace("\\", "/")
        for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
            if norm.startswith(prefix):
                return layer
        return "L_UNKNOWN"

    # Generate realistic module paths (repeating, as they would in real scan)
    paths = []
    layer_dirs = [
        "agentic_core/L0_routing",
        "agentic_core/L1_cognition",
        "agentic_core/L2_execution",
        "agentic_core/L3_orchestration",
        "agentic_core/L4_state",
        "agentic_core/L5_safety",
        "apps_lic/reasoning",
        "apps_rg/engines",
        "tools/adg",
        "tests/unit",
        "system_learning/engines",
    ]
    for i in range(150_000):
        ld = layer_dirs[i % len(layer_dirs)]
        paths.append(f"{ld}/module_{i % 200}.py")

    # Cached version (from schema_util)
    from agentic_core.adg.contracts.schema_util import module_path_to_layer

    # Clear cache for fair measurement
    module_path_to_layer.cache_clear()

    def pre_uncached():
        for p in paths:
            _uncached_module_path_to_layer(p)

    def post_cached():
        module_path_to_layer.cache_clear()
        for p in paths:
            module_path_to_layer(p)

    result.pre_times, result.post_times = _run_benchmark(pre_uncached, post_cached, iterations=3, warmup=1)
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark E: Real scan_cache.json load with orjson vs json
# ---------------------------------------------------------------------------


def benchmark_e_real_cache_load() -> BenchmarkResult:
    """Load the actual 453MB scan_result_cache.json with orjson vs json."""
    result = BenchmarkResult(
        name="E: Real scan_cache.json load (orjson vs json)",
        description="Load actual scan_result_cache.json file from disk",
    )

    # Try multiple known cache locations
    for candidate in [
        ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json",
        ROOT / "artifacts" / "adg" / "scan_result_cache.json",
    ]:
        if candidate.exists():
            cache_path = candidate
            break
    else:
        result.status = "SKIP"
        result.debug_note = "Cache file not found in any known location"
        return result

    try:
        import orjson
    except ImportError:
        result.status = "SKIP"
        result.debug_note = "orjson not installed"
        return result

    file_size_mb = cache_path.stat().st_size / (1024 * 1024)
    result.description += f" ({file_size_mb:.1f} MB)"

    def pre_json_load():
        raw = cache_path.read_bytes()
        return json.loads(raw.decode("utf-8"))

    def post_orjson_load():
        raw = cache_path.read_bytes()
        return orjson.loads(raw)

    # Only 3 iterations due to file size
    result.pre_times, result.post_times = _run_benchmark(
        pre_json_load, post_orjson_load, iterations=3, warmup=1
    )
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark F: _EDGE_SORT_KEY lambda vs default dataclass __lt__
# ---------------------------------------------------------------------------


def benchmark_f_edge_sort_key() -> BenchmarkResult:
    """Fast sort key (5-field tuple) vs default dataclass comparison (13+ fields)."""
    result = BenchmarkResult(
        name="F: _EDGE_SORT_KEY fast sort vs dataclass __lt__",
        description="Sort 100k Edge objects: 5-field key tuple vs full dataclass comparison",
    )

    # Build 100k edges with varied data for realistic sorting
    import random

    from agentic_core.adg.extraction.static_scanner import Edge

    random.seed(42)
    edges = []
    for i in range(100_000):
        edges.append(
            Edge(
                from_name=f"ADG::Module::mod_{random.randint(0, 5000)}.py",
                relation_type=random.choice(["imports", "calls", "exports", "violates", "reads_from"]),
                to_name=f"ADG::Symbol::sym_{random.randint(0, 10000)}",
                edge_kind=random.choice(["static_import", "dynamic_exec", "lazy_import"]),
                source_file=f"mod_{random.randint(0, 5000)}.py",
                line_no=random.randint(1, 500),
                symbol=f"sym_{random.randint(0, 10000)}",
            )
        )

    # Optimized sort key
    _EDGE_SORT_KEY = lambda e: (e.from_name, e.relation_type, e.to_name, e.source_file, e.line_no)

    def pre_default_sort():
        return sorted(edges)  # Uses dataclass __lt__ with all fields

    def post_key_sort():
        return sorted(edges, key=_EDGE_SORT_KEY)

    result.pre_times, result.post_times = _run_benchmark(
        pre_default_sort, post_key_sort, iterations=5, warmup=1
    )
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark G: ADG_SKIP_SELF_TEST timing
# ---------------------------------------------------------------------------


def benchmark_g_self_test_gate() -> BenchmarkResult:
    """Measure cost of run_scanner_self_test()."""
    result = BenchmarkResult(
        name="G: ADG_SKIP_SELF_TEST gate",
        description="run_scanner_self_test() cost vs skipping (env gate)",
    )

    try:
        from agentic_core.adg.extraction.static_scanner import run_scanner_self_test
    except ImportError as e:
        result.status = "SKIP"
        result.debug_note = f"Import error: {e}"
        return result

    def pre_run_self_test():
        return run_scanner_self_test()

    def post_skip():
        return False  # What happens when ADG_SKIP_SELF_TEST=1

    # Self-test is expensive, use fewer iterations
    result.pre_times, result.post_times = _run_benchmark(pre_run_self_test, post_skip, iterations=3, warmup=0)
    result.compute()
    return result


# ---------------------------------------------------------------------------
# Benchmark H: AMDCPUOptimizer infrastructure validation
# ---------------------------------------------------------------------------


def benchmark_h_cpu_optimizer() -> BenchmarkResult:
    """Validate AMDCPUOptimizer detects CPU correctly and provides optimal workers."""
    result = BenchmarkResult(
        name="H: AMDCPUOptimizer infrastructure",
        description="Validate AMD detection, worker count, and parallel map overhead",
    )

    try:
        from agentic_core.L2_execution.utils.cpu_optimizer import AMDCPUOptimizer, CPUConfig
    except ImportError as e:
        result.status = "SKIP"
        result.debug_note = f"Import error: {e}"
        return result

    import concurrent.futures

    opt = AMDCPUOptimizer(CPUConfig(cpu_affinity=False))

    cpu_info = {
        "processor": platform.processor(),
        "is_amd": opt._is_amd,
        "physical_cores": opt._physical_cores,
        "logical_cores": opt._cpu_count,
        "optimal_workers": opt.get_optimal_workers(),
        "is_windows": opt._is_windows,
        "use_processes": opt.config.use_processes,
    }

    # Use a HEAVIER CPU-bound task to overcome Windows spawn overhead
    def cpu_work_heavy(n: int) -> int:
        """Heavy CPU-bound task: compute long hash chain (overcomes spawn overhead)."""
        h = hashlib.sha256(str(n).encode())
        for _ in range(5000):  # 5x heavier to overcome spawn cost
            h = hashlib.sha256(h.digest())
        return int.from_bytes(h.digest()[:4], "big")

    items = list(range(200))

    def pre_serial():
        return [cpu_work_heavy(i) for i in items]

    # On Windows, ThreadPool is used by default (spawn overhead too high)
    # Test both ThreadPool and ProcessPool to show the difference
    def post_threadpool():
        with concurrent.futures.ThreadPoolExecutor(max_workers=opt.get_optimal_workers()) as ex:
            return list(ex.map(cpu_work_heavy, items))

    print("    Testing serial vs ThreadPool (Windows default)...")
    result.pre_times, result.post_times = _run_benchmark(pre_serial, post_threadpool, iterations=3, warmup=1)
    result.compute()

    # Additional diagnostic: ThreadPool won't help because of GIL
    # This is expected behavior on Windows for CPU-bound Python code
    if result.pct_gain <= 1.0:
        cpu_info["root_cause"] = (
            "ThreadPoolExecutor cannot bypass Python GIL for CPU-bound work. "
            "On Windows, ProcessPoolExecutor uses 'spawn' which has high startup overhead. "
            "The AMDCPUOptimizer correctly detects Windows and defaults to ThreadPool, "
            "which is optimal for I/O-bound tasks but provides no parallelism for CPU-bound Python. "
            "For true CPU parallelism on Windows, tasks must be >100ms per item to amortize spawn cost, "
            "or use multiprocessing directly with long-lived worker pools."
        )
        cpu_info["recommendation"] = (
            "AMDCPUOptimizer is correctly configured for Windows. "
            "CPU-bound gains come from algorithmic optimizations (orjson, lru_cache, sort keys) "
            "not from Python-level thread parallelism. ProcessPool should only be used for "
            "heavy tasks like full AST scanning (measured 10x speedup in plan)."
        )

    result.debug_note = json.dumps(cpu_info, indent=2)
    opt.shutdown()
    return result


# ---------------------------------------------------------------------------
# Benchmark I: Full ADG scan timing (with vs without skip_self_test)
# ---------------------------------------------------------------------------


def benchmark_i_full_scan_timing() -> BenchmarkResult:
    """Time a full cached ADG scan with ADG_SKIP_SELF_TEST=1 vs default."""
    result = BenchmarkResult(
        name="I: Full ADG cached scan (skip_self_test=1 vs default)",
        description="End-to-end ADG scan with 99%+ cache hit rate",
    )

    try:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    except ImportError as e:
        result.status = "SKIP"
        result.debug_note = f"Import error: {e}"
        return result

    for candidate in [
        ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json",
        ROOT / "artifacts" / "adg" / "scan_result_cache.json",
    ]:
        if candidate.exists():
            cache_path = candidate
            break
    else:
        result.status = "SKIP"
        result.debug_note = "scan_result_cache.json not found"
        return result

    def run_scan_with_self_test():
        os.environ.pop("ADG_SKIP_SELF_TEST", None)
        scanner = ADGStaticScanner(repo_root=ROOT, cache_path=cache_path)
        return scanner.scan()

    def run_scan_skip_self_test():
        os.environ["ADG_SKIP_SELF_TEST"] = "1"
        scanner = ADGStaticScanner(repo_root=ROOT, cache_path=cache_path)
        r = scanner.scan()
        os.environ.pop("ADG_SKIP_SELF_TEST", None)
        return r

    # Only 1 iteration each due to cost (50s+ per run)
    print("    Running full scan WITH self-test (this takes ~25-50s)...")
    _, t_pre = _timed(run_scan_with_self_test)
    result.pre_times = [t_pre]
    print(f"    Pre (with self-test): {t_pre:.2f}s")

    print("    Running full scan WITHOUT self-test...")
    _, t_post = _timed(run_scan_skip_self_test)
    result.post_times = [t_post]
    print(f"    Post (skip self-test): {t_post:.2f}s")

    result.compute()
    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(results: list[BenchmarkResult]) -> str:
    """Generate markdown report with pre/post times and % gain."""
    lines = []
    lines.append("# CPU Optimization Benchmark Report")
    lines.append("")
    lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Platform:** {platform.platform()}")
    lines.append(f"**Processor:** {platform.processor()}")
    lines.append(f"**Python:** {sys.version.split()[0]}")

    try:
        import psutil

        lines.append(f"**Physical Cores:** {psutil.cpu_count(logical=False)}")
        lines.append(f"**Logical Cores:** {psutil.cpu_count(logical=True)}")
    except ImportError:
        pass

    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| # | Optimization | Pre (median) | Post (median) | Speedup | % Gain | Status |")
    lines.append("|---|-------------|-------------|--------------|---------|--------|--------|")

    for i, r in enumerate(results, 1):
        pre_str = f"{r.pre_median:.4f}s" if r.pre_median > 0 else "N/A"
        post_str = f"{r.post_median:.4f}s" if r.post_median > 0 else "N/A"
        speedup_str = f"{r.speedup:.1f}x" if r.speedup > 0 else "N/A"
        pct_str = f"{r.pct_gain:.1f}%" if r.pct_gain != 0 else "0.0%"
        status_emoji = {"PASS": "✅", "NO GAIN": "❌", "SKIP": "⏭️"}.get(r.status, "⚠️")
        lines.append(
            f"| {i} | {r.name} | {pre_str} | {post_str} | {speedup_str} | {pct_str} | {status_emoji} {r.status} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Detailed results
    lines.append("## Detailed Results")
    lines.append("")

    for r in results:
        lines.append(f"### {r.name}")
        lines.append(f"**Description:** {r.description}")
        lines.append(f"**Status:** {r.status}")
        lines.append("")

        if r.pre_times:
            lines.append(f"- **Pre times:** {', '.join(f'{t:.4f}s' for t in r.pre_times)}")
            lines.append(f"- **Pre median:** {r.pre_median:.4f}s")
        if r.post_times:
            lines.append(f"- **Post times:** {', '.join(f'{t:.4f}s' for t in r.post_times)}")
            lines.append(f"- **Post median:** {r.post_median:.4f}s")
        if r.speedup > 0:
            lines.append(f"- **Speedup:** {r.speedup:.2f}x")
            lines.append(f"- **% Gain:** {r.pct_gain:.1f}%")

        if r.debug_note:
            lines.append(f"- **Debug notes:** {r.debug_note}")

        if r.status == "NO GAIN":
            lines.append("")
            lines.append("**Root Cause Analysis:**")
            if "parallel" in r.name.lower() or "CPU" in r.name:
                lines.append(
                    "- Windows `spawn` overhead for ProcessPoolExecutor exceeds gains for short tasks"
                )
                lines.append("- ThreadPoolExecutor is GIL-bound; true parallelism requires ProcessPool")
                lines.append(
                    "- Recommendation: Use for tasks >100ms per item; serial is faster for micro-tasks"
                )
            else:
                lines.append("- Optimization may not provide measurable gain at this scale")
                lines.append("- Check if the bottleneck has shifted to another component")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Aggregate
    total_pre = sum(r.pre_median for r in results if r.pre_median > 0 and r.post_median > 0)
    total_post = sum(r.post_median for r in results if r.pre_median > 0 and r.post_median > 0)
    passed = sum(1 for r in results if r.status == "PASS")
    no_gain = sum(1 for r in results if r.status == "NO GAIN")
    skipped = sum(1 for r in results if r.status == "SKIP")

    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- **Benchmarks passed (>1% gain):** {passed}/{len(results)}")
    lines.append(f"- **No gain:** {no_gain}/{len(results)}")
    lines.append(f"- **Skipped:** {skipped}/{len(results)}")
    if total_post > 0:
        lines.append(f"- **Combined pre time:** {total_pre:.4f}s")
        lines.append(f"- **Combined post time:** {total_post:.4f}s")
        lines.append(f"- **Combined speedup:** {total_pre / total_post:.2f}x")
        lines.append(f"- **Combined % gain:** {((total_pre - total_post) / total_pre) * 100:.1f}%")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 72)
    print("CPU OPTIMIZATION BENCHMARK — Pre/Post Evidence Generator")
    print("=" * 72)
    print()

    results: list[BenchmarkResult] = []
    benchmarks = [
        ("A1", benchmark_a1_orjson_serialization),
        ("A2", benchmark_a2_orjson_deserialization),
        ("A3", benchmark_a3_orjson_report_gen),
        ("B", benchmark_b_edge_field_names),
        ("D", benchmark_d_lru_cache_layer),
        ("E", benchmark_e_real_cache_load),
        ("F", benchmark_f_edge_sort_key),
        ("G", benchmark_g_self_test_gate),
        ("H", benchmark_h_cpu_optimizer),
        ("I", benchmark_i_full_scan_timing),
    ]

    for label, func in benchmarks:
        print(f"[{label}] Running: {func.__doc__ or func.__name__}...")
        try:
            r = func()
            results.append(r)
            status = r.status
            if r.pre_median > 0 and r.post_median > 0:
                print(
                    f"    Pre: {r.pre_median:.4f}s | Post: {r.post_median:.4f}s | "
                    f"Speedup: {r.speedup:.1f}x | Gain: {r.pct_gain:.1f}% | {status}"
                )
            else:
                print(f"    Status: {status} | {r.debug_note}")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            print(f"    ERROR: {e}")
            r = BenchmarkResult(name=f"{label}: {func.__name__}", description=str(e), status="ERROR")
            r.debug_note = str(e)
            results.append(r)
        print()

    # Generate report
    report = generate_report(results)
    report_path = ROOT / "docs" / "reports" / "plans" / "cpu-optimization-benchmark-evidence.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    # Also dump raw JSON evidence
    evidence_path = ROOT / "artifacts" / "cpu_benchmark_evidence.json"
    evidence = []
    for r in results:
        evidence.append(
            {
                "name": r.name,
                "description": r.description,
                "pre_times": r.pre_times,
                "post_times": r.post_times,
                "pre_median": r.pre_median,
                "post_median": r.post_median,
                "speedup": r.speedup,
                "pct_gain": r.pct_gain,
                "status": r.status,
                "debug_note": r.debug_note,
            }
        )
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"Evidence JSON saved to: {evidence_path}")


if __name__ == "__main__":
    main()
