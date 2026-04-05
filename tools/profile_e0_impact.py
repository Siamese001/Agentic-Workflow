"""E0: predict_impact internals profiling.

Traces every sub-phase of predict_impact() using cProfile + manual
perf_counter spans to identify the exact bottleneck:

  Phase 1: Edge scan to build module_imports / covers_map / violation_sources
  Phase 2: Reverse dependency map construction (the nested prefix-matching loop)
  Phase 3: BFS traversal (max_depth=6)
  Phase 4: Test coverage lookup
  Phase 5: Ownership breakdown (_infer_ownership per impacted module)
  Phase 6: Risk score computation

Uses the warm scan cache so timing is pipeline-comparable (same corpus as v9).

Outputs artifacts/adg_e0_impact_profile.json.
"""
from __future__ import annotations

import cProfile
import io
import json
import pstats
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).parent.parent

proc = psutil.Process()


def rss_mb() -> float:
    return proc.memory_info().rss / 1024 / 1024


def _normalise(name: str) -> str:
    for prefix in ("ADG::Module::", "ADG::Symbol::", "ADG::Layer::"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


_EXECUTION_RELATIONS = frozenset({
    "imports", "calls", "implements", "inherits", "reads_from",
    "writes_to", "invokes_provider", "dynamic_exec", "decorated_by",
})


def profile_predict_impact(result, seed_files: list[str]) -> dict:
    """Run predict_impact with per-phase instrumentation."""
    edges = list(result.edges)
    spans: dict[str, float] = {}

    # --- Phase 1: edge scan ---
    t0 = time.perf_counter()
    module_imports: dict[str, set[str]] = {}
    covers_map: dict[str, set[str]] = {}
    violation_sources: set[str] = set()
    rel_type_counts: dict[str, int] = {}

    for e in edges:
        rel_type_counts[e.relation_type] = rel_type_counts.get(e.relation_type, 0) + 1
        fn = _normalise(e.from_name)
        if e.relation_type == "covers":
            tn = _normalise(e.to_name)
            covers_map.setdefault(tn, set()).add(fn)
        elif e.relation_type == "violates":
            violation_sources.add(fn)
        elif e.relation_type in _EXECUTION_RELATIONS:
            tn = _normalise(e.to_name)
            module_imports.setdefault(fn, set()).add(tn)
    spans["p1_edge_scan"] = round(time.perf_counter() - t0, 4)

    # --- Phase 2: reverse dep map construction ---
    t0 = time.perf_counter()
    module_dot_forms: dict[str, str] = {}
    for m in result.modules:
        dot = m.replace("/", ".").removesuffix(".py")
        module_dot_forms[dot] = m

    reverse_dep: dict[str, set[str]] = {}
    unmatched_syms = 0
    direct_matched = 0
    prefix_matched = 0
    total_sym_lookups = 0
    max_sym_parts = 0

    for from_mod, imported_syms in module_imports.items():
        for sym in imported_syms:
            total_sym_lookups += 1
            sym_dot = sym.replace("/", ".")
            parts = sym_dot.split(".")
            max_sym_parts = max(max_sym_parts, len(parts))
            matched: str | None = None
            for length in range(len(parts), 0, -1):
                candidate = ".".join(parts[:length])
                if candidate in module_dot_forms:
                    matched = module_dot_forms[candidate]
                    if length == len(parts):
                        direct_matched += 1
                    else:
                        prefix_matched += 1
                    break
            if matched is None:
                slash_sym = sym.replace(".", "/")
                if slash_sym in set(result.modules):
                    matched = slash_sym
                    direct_matched += 1
            if matched is None:
                unmatched_syms += 1
            else:
                reverse_dep.setdefault(matched, set()).add(from_mod)

    spans["p2_reverse_dep_build"] = round(time.perf_counter() - t0, 4)

    # --- Phase 3: BFS ---
    t0 = time.perf_counter()
    changed_norm = {f.replace("\\", "/") for f in seed_files}
    frontier: set[str] = set(changed_norm)
    visited: set[str] = set(changed_norm)
    execution_paths: list[tuple[str, str, str]] = []
    bfs_iterations = 0

    for depth in range(6):
        next_frontier: set[str] = set()
        for node in frontier:
            for dependant in reverse_dep.get(node, set()):
                if dependant not in visited:
                    visited.add(dependant)
                    next_frontier.add(dependant)
                    execution_paths.append((dependant, "depends_on", node))
        bfs_iterations += 1
        if not next_frontier:
            break
        frontier = next_frontier

    impacted = sorted(visited - changed_norm)
    spans["p3_bfs"] = round(time.perf_counter() - t0, 4)

    # --- Phase 4: test coverage ---
    t0 = time.perf_counter()
    covering_tests: set[str] = set()
    for mod in visited:
        for test in covers_map.get(mod, set()):
            covering_tests.add(test)
    spans["p4_test_coverage"] = round(time.perf_counter() - t0, 4)

    # --- Phase 5: ownership ---
    t0 = time.perf_counter()
    from agentic_core.adg.analysis.ModuleOwnership import _infer_ownership
    by_owner: dict[str, int] = {}
    for mod in impacted:
        owner = _infer_ownership(mod).owner
        by_owner[owner] = by_owner.get(owner, 0) + 1
    spans["p5_ownership"] = round(time.perf_counter() - t0, 4)

    # --- Phase 6: risk score ---
    t0 = time.perf_counter()
    total_modules = max(len(result.modules), 1)
    breadth_score = min(len(impacted) / total_modules, 1.0) * 0.4
    high_crit = sum(1 for m in impacted if _infer_ownership(m).criticality == "high")
    crit_score = min(high_crit / max(len(impacted), 1), 1.0) * 0.4
    violation_modules = [m for m in impacted if m in violation_sources]
    viol_score = min(len(violation_modules) / max(len(impacted), 1), 1.0) * 0.2
    risk_score = breadth_score + crit_score + viol_score
    spans["p6_risk_score"] = round(time.perf_counter() - t0, 4)

    total = sum(spans.values())
    spans["_total_s"] = round(total, 4)

    return {
        "spans": spans,
        "corpus": {
            "total_edges": len(edges),
            "total_modules": len(result.modules),
            "execution_relation_edges": sum(
                v for k, v in rel_type_counts.items() if k in _EXECUTION_RELATIONS
            ),
            "covers_edges": rel_type_counts.get("covers", 0),
            "violates_edges": rel_type_counts.get("violates", 0),
            "rel_type_counts": dict(sorted(rel_type_counts.items(), key=lambda x: -x[1])),
        },
        "reverse_dep": {
            "module_imports_entries": len(module_imports),
            "total_imported_syms": total_sym_lookups,
            "direct_matched": direct_matched,
            "prefix_matched": prefix_matched,
            "unmatched": unmatched_syms,
            "max_sym_depth": max_sym_parts,
            "reverse_dep_keys": len(reverse_dep),
        },
        "bfs": {
            "seed_files": seed_files,
            "bfs_iterations_used": bfs_iterations,
            "impacted_count": len(impacted),
            "execution_paths_count": len(execution_paths),
        },
        "ownership": {
            "modules_processed": len(impacted),
            "owners_found": len(by_owner),
        },
    }


def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT))

    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"

    print("=== E0: predict_impact internals profiling ===")
    print()
    print("Loading scan result (cached)...")
    t0 = time.perf_counter()
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)
    result = scanner.scan()
    t_scan = time.perf_counter() - t0
    print(f"  scan: {t_scan:.2f}s  edges={len(result.edges)}  modules={len(result.modules)}")

    # Same seed selection logic as generate_full_adg
    violation_sources_raw = [
        e.source_file
        for e in result.edges
        if e.relation_type == "imports" and e.source_file
        and any(e.source_file.startswith(p) for p in (
            "agentic_core/L2_execution",
            "agentic_core/L0_routing",
            "agentic_core/L5_safety",
        ))
    ]
    seed_files: list[str] = []
    seen: set[str] = set()
    for sf in violation_sources_raw:
        if sf not in seen:
            seen.add(sf)
            seed_files.append(sf)
        if len(seed_files) >= 5:
            break
    if not seed_files:
        seed_files = list(result.modules[:5])
    print(f"  seed files: {seed_files}")
    print()

    # --- Instrumented run ---
    print("Running instrumented predict_impact...")
    rss_pre = rss_mb()
    t_total_start = time.perf_counter()
    profile_data = profile_predict_impact(result, seed_files)
    t_total = time.perf_counter() - t_total_start
    rss_post = rss_mb()

    spans = profile_data["spans"]
    print()
    print("=== Per-phase breakdown ===")
    print(f"  {'Phase':<30}  {'Wall':>8}  {'% total':>8}")
    print(f"  {'-'*30}  {'-'*8}  {'-'*8}")
    for k, v in spans.items():
        if k.startswith("_"):
            continue
        pct = v / spans["_total_s"] * 100
        print(f"  {k:<30}  {v:>8.4f}s  {pct:>7.1f}%")
    print(f"  {'-'*30}  {'-'*8}  {'-'*8}")
    print(f"  {'TOTAL':<30}  {spans['_total_s']:>8.4f}s")
    print(f"  (wall from caller: {t_total:.4f}s)")
    print()

    corpus = profile_data["corpus"]
    print("=== Corpus breakdown ===")
    print(f"  total edges:              {corpus['total_edges']:>8,}")
    print(f"  execution-relation edges: {corpus['execution_relation_edges']:>8,}  (iterated in P2 prefix-match)")
    print(f"  covers edges:             {corpus['covers_edges']:>8,}")
    print(f"  violates edges:           {corpus['violates_edges']:>8,}")
    print()
    print("  relation type counts (top 10):")
    for rel, cnt in list(corpus["rel_type_counts"].items())[:10]:
        print(f"    {rel:<40} {cnt:>8,}")
    print()

    rdep = profile_data["reverse_dep"]
    print("=== P2 prefix-match internals ===")
    print(f"  module_imports entries:   {rdep['module_imports_entries']:>8,}")
    print(f"  total symbol lookups:     {rdep['total_imported_syms']:>8,}")
    print(f"  direct matched:           {rdep['direct_matched']:>8,}")
    print(f"  prefix matched:           {rdep['prefix_matched']:>8,}")
    print(f"  unmatched:                {rdep['unmatched']:>8,}")
    print(f"  max symbol depth (parts): {rdep['max_sym_depth']:>8}")
    print(f"  reverse_dep keys:         {rdep['reverse_dep_keys']:>8,}")
    print()

    bfs = profile_data["bfs"]
    print("=== P3 BFS ===")
    print(f"  BFS iterations used:      {bfs['bfs_iterations_used']:>8}")
    print(f"  impacted modules:         {bfs['impacted_count']:>8,}")
    print(f"  execution paths found:    {bfs['execution_paths_count']:>8,}")
    print()

    print(f"  RSS delta: {rss_post - rss_pre:+.0f} MB")
    print()

    # --- cProfile pass on the full function ---
    print("Running cProfile (top 20 by cumtime)...")
    from agentic_core.adg.analysis.ImpactReport import predict_impact
    pr = cProfile.Profile()
    pr.enable()
    predict_impact(result, seed_files)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    cprofile_output = s.getvalue()
    print(cprofile_output[:3000])

    profile_data["cprofile_top20"] = cprofile_output[:4000]
    profile_data["rss_delta_mb"] = round(rss_post - rss_pre, 1)
    profile_data["wall_total_s"] = round(t_total, 4)
    profile_data["seed_files"] = seed_files

    out_path = ROOT / "artifacts" / "adg_e0_impact_profile.json"
    out_path.write_text(json.dumps(profile_data, indent=2))
    print(f"Profile written: {out_path}")


if __name__ == "__main__":
    main()
