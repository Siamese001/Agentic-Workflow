"""ADG Test Accelerator — uses the Architecture Dependency Graph to:

1. **Gap analysis** (`gap`): rank uncovered production modules by fan-in.
2. **Scoped selection** (`scope`): given changed files, emit only the test
   files that cover them (or their transitive importers) via ADG edges.
3. **Parallel groups** (`groups`): partition test files into N balanced
   groups by ADG layer for use with pytest-xdist ``--dist worksteal``.
4. **Full report** (`report`): JSON combining all three above.
5. **Collection safety** (`collection-safety`): analyze test file import
   safety via static ADG graph (resolvable, missing, syntax errors, cycles).

Usage::

    # Gap analysis
    python tools/adg_test_accelerator.py gap [--top 20] [--layer L5]

    # Scoped test selection (pipe to pytest -p no:randomly)
    python tools/adg_test_accelerator.py scope --changed agentic_core/L0_routing/config/path_constants.py

    # Parallel groups (4 workers)
    python tools/adg_test_accelerator.py groups --workers 4

    # Full JSON report
    python tools/adg_test_accelerator.py report --out docs/reports/plans/adg_test_report.json

    # Collection safety analysis
    python tools/adg_test_accelerator.py collection-safety [--layer L0] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
import time
from collections import defaultdict
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_logger = logging.getLogger(__name__)

from agentic_core.adg.analysis.hotspot_index_types import HotspotIndex
from agentic_core.adg.analysis.test_gap_types import detect_test_gaps
from agentic_core.adg.contracts.schema_util import module_path_to_layer
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner, ScanResult

# Constants
DEFAULT_MAX_DEPTH = 4
DEFAULT_TOP_N = 30

# Worker defaults — workload-aware via cpu_optimizer
# Default uses pytest_mixed workload class in batch mode (safe for 9950X3D)
defaults: dict[str, int] = {
    "pytest_mixed": 24,
    "interactive_reserve": 4,
    "batch_reserve": 2,
}
DEFAULT_WORKERS: int = 24  # pytest_mixed batch default
DEFAULT_WORKERS_BATCH: int = DEFAULT_WORKERS
DEFAULT_WORKERS_INTERACTIVE: int = 20  # 24 - 4 reserve
PROBLEM_FILE_DISPLAY_LIMIT = 20
SYMBOL_PREFIX = "ADG::Symbol::"
MODULE_PREFIX = "ADG::Module::"

_PRODUCTION_EXCLUDES = frozenset(("tests/", "ops_scripts/", "tools/", ".py.bak"))


def _is_production(path: str) -> bool:
    """Check if path represents a production module (not test/ops/tool)."""
    norm = path.replace("\\", "/")
    return not any(norm.startswith(exclude) or norm.endswith(exclude) for exclude in _PRODUCTION_EXCLUDES)


def _symbol_to_path(sym: str) -> str:
    """Convert ADG::Symbol::a.b.c -> a/b/c.py (best-effort)."""
    return sym.replace(".", "/") + ".py"


def _module_adg_to_path(adg_name: str) -> str:
    """Strip ADG::Module:: prefix."""
    if adg_name.startswith(MODULE_PREFIX):
        return adg_name[len(MODULE_PREFIX) :]
    return adg_name


# ---------------------------------------------------------------------------
# Core data structures built from one scan
# ---------------------------------------------------------------------------


class ADGIndex:
    """Pre-built index for O(1) queries over a ScanResult."""

    def __init__(self, result: ScanResult) -> None:
        self.result = result
        self.hotspot = HotspotIndex.build(result)

        # prod_to_tests: production module path -> set of test file paths
        self.prod_to_tests: dict[str, set[str]] = defaultdict(set)

        # test_to_prods: test file path -> set of production module paths
        self.test_to_prods: dict[str, set[str]] = defaultdict(set)

        # imports graph: module -> set of modules it imports (for transitivity)
        self.imports: dict[str, set[str]] = defaultdict(set)
        self.imported_by: dict[str, set[str]] = defaultdict(set)

        self._build()

    def _build(self) -> None:
        for edge in self.result.edges:
            src = edge.source_file.replace("\\", "/")
            rel = edge.relation_type

            if rel == "covers":
                to_name = edge.to_name
                if to_name.startswith(SYMBOL_PREFIX):
                    prod_path = _symbol_to_path(to_name[len(SYMBOL_PREFIX) :])
                elif to_name.startswith(MODULE_PREFIX):
                    prod_path = _module_adg_to_path(to_name)
                else:
                    continue

                test_src = src
                if "tests/" in test_src:
                    self.prod_to_tests[prod_path].add(test_src)
                    self.test_to_prods[test_src].add(prod_path)

            elif rel == "imports":
                frm = _module_adg_to_path(edge.from_name)
                to = _module_adg_to_path(edge.to_name)
                self.imports[frm].add(to)
                self.imported_by[to].add(frm)

    def transitive_importers(
        self,
        module_path: str,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> set[str]:
        """Return all modules that (transitively) import module_path.

        Args:
            module_path: The module path to find importers for
            max_depth: Maximum depth for transitive search (default: 4)

        Returns:
            Set of module paths that import the given module
        """
        visited: set[str] = set()
        queue = [module_path]
        depth = 0
        while queue and depth < max_depth:
            next_q: list[str] = []
            for m in queue:
                for imp in self.imported_by.get(m, set()):
                    if imp not in visited:
                        visited.add(imp)
                        next_q.append(imp)
            queue = next_q
            depth += 1
        return visited

    def tests_for_changed(self, changed_paths: list[str]) -> set[str]:
        """Return all test files that cover any changed module or its importers."""
        tests: set[str] = set()
        for cp in changed_paths:
            norm = cp.replace("\\", "/")
            # Direct covers
            tests.update(self.prod_to_tests.get(norm, set()))
            # Transitive: things that import this module
            for imp in self.transitive_importers(norm):
                tests.update(self.prod_to_tests.get(imp, set()))
        return tests

    def layer_of(self, test_path: str) -> str:
        """Infer layer from ADG or path heuristic."""
        norm = test_path.replace("\\", "/")
        for prods in [self.test_to_prods.get(norm, set())]:
            for prod in prods:
                layer = module_path_to_layer(prod)
                if layer and layer != "unknown":
                    return layer
        # Fall back to path heuristic
        for ln in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{ln}_" in norm or f"/{ln.lower()}_" in norm:
                return ln
        return "other"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_gap(args: argparse.Namespace, idx: ADGIndex) -> int:
    """Print uncovered production modules ranked by fan-in.

    Args:
        args: Parsed command line arguments
        idx: Pre-built ADG index

    Returns:
        Exit code (0 for success)
    """
    try:
        report = detect_test_gaps(idx.result, hotspot_index=idx.hotspot)
    except Exception as e:
        _logger.error(f"Failed to detect test gaps: {e}")
        return 1

    entries = report.uncovered_modules
    if args.layer:
        entries = [e for e in entries if e.layer == args.layer]

    # Validate and apply top limit
    top_n = max(1, getattr(args, "top", DEFAULT_TOP_N))
    entries = sorted(entries, key=lambda e: -e.fan_in)[:top_n]

    print(f"Coverage rate : {report.coverage_rate:.1%}")
    print(f"Total production modules : {report.total_production_modules}")
    print(f"Covered   : {len(report.covered_modules)}")
    print(f"Uncovered : {len(report.uncovered_modules)}")
    print()
    print(f"{'fan_in':>6}  {'layer':<6}  module_path")
    print("-" * 70)
    for e in entries:
        print(f"{e.fan_in:>6}  {e.layer:<6}  {e.module_path}")

    print()
    print("Gap by layer:")
    for layer, count in sorted(report.gap_by_layer.items()):
        print(f"  {layer}: {count}")

    return 0


def cmd_scope(args: argparse.Namespace, idx: ADGIndex) -> int:
    """Emit test files that cover the changed modules (one per line).

    Args:
        args: Parsed command line arguments
        idx: Pre-built ADG index

    Returns:
        Exit code (0 for success, 1 if no tests found)
    """
    changed = [c.strip() for c in args.changed if c.strip()]
    if not changed and args.stdin:
        try:
            changed = [l.strip() for l in sys.stdin if l.strip()]
        except KeyboardInterrupt:
            _logger.info("Interrupted by user")
            return 130

    if not changed:
        _logger.error("No changed files specified.")
        return 1

    try:
        tests = idx.tests_for_changed(changed)
    except Exception as e:
        _logger.error(f"Failed to determine tests for changed files: {e}")
        return 1

    if args.format == "pytest":
        # Space-separated for use as: pytest $(python ... scope ...)
        existing = [t for t in sorted(tests) if pathlib.Path(t).exists()]
        print(" ".join(existing) if existing else "")
    elif args.format == "json":
        existing = sorted(t for t in tests if pathlib.Path(t).exists())
        print(json.dumps({"changed": changed, "impacted_tests": existing}, indent=2))
    else:
        for t in sorted(tests):
            print(t)

    if not tests:
        _logger.warning(f"No ADG coverage signal found for: {changed}")
        _logger.warning("Run full suite (no scoping possible)")
        return 1

    return 0


def cmd_collection_safety(args: argparse.Namespace, idx: ADGIndex) -> int:
    """Analyze test file collection safety via ADG import graph.

    Queries existing ADGIndex.imports and ADG data to classify each test file:
    - RESOLVABLE: All imports exist and are reachable
    - MISSING: Target module does not exist in ADG
    - SYNTAX_ERROR: Target module has syntax errors
    - CIRCULAR: Target module is in an import cycle
    - STALE_PATH: Module exists but filesystem path differs from ADG path

    Maps to PyTest Lifecycle triage:
    - Check 1.1 (MISSING) -> production_bug_fix
    - Check 1.2 (STALE_PATH) -> stale_reference_fix
    - Neither -> ANTI_PATTERN -> BLOCKED

    Args:
        args: Parsed command line arguments
        idx: Pre-built ADG index

    Returns:
        Exit code (0 for success)
    """
    from pathlib import Path

    # Build lookup sets from ADG data
    all_modules = set(idx.result.modules)
    syntax_errors = set(idx.result.syntax_errors)

    # Build cycle detection set
    cycle_nodes = {edge.to_name for edge in idx.result.edges if edge.relation_type == "in_cycle"}

    # Collect all test files from ADG
    test_files = sorted(
        {
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        },
    )

    if not test_files:
        _logger.warning("No test files found in ADG scan")
        return 0

    # Filter by layer if requested
    if args.layer:
        test_files = [tf for tf in test_files if idx.layer_of(tf) == args.layer]

    # Analyze each test file
    file_reports = []
    summary = {
        "files_scanned": len(test_files),
        "collection_safe": 0,
        "collection_fatal": 0,
        "by_category": {
            "resolvable": 0,
            "missing": 0,
            "syntax_error": 0,
            "circular": 0,
            "stale_path": 0,
            "anti_pattern": 0,
        },
        "by_layer": defaultdict(int),
    }

    repo_root = Path(".")

    for test_file in test_files:
        # Get all modules this test file imports
        imported_modules = idx.imports.get(test_file, set())

        file_status = "resolvable"
        issues = []

        for module in imported_modules:
            # Convert ADG module format to filesystem path if needed
            if module.startswith("ADG::Module::"):
                module_path = module[13:]  # Strip prefix
            else:
                module_path = module

            # Check each category
            if module_path not in all_modules:
                file_status = "missing"
                issues.append(f"MISSING: {module_path}")
            elif module_path in syntax_errors:
                file_status = "syntax_error"
                issues.append(f"SYNTAX_ERROR: {module_path}")
            elif any(m in cycle_nodes for m in imported_modules):
                file_status = "circular"
                issues.append(f"CIRCULAR: {module_path}")
            else:
                # Check if filesystem path matches ADG path
                fs_path = repo_root / f"{module_path}.py"
                if not fs_path.exists():
                    # Try as package
                    fs_path = repo_root / module_path / "__init__.py"

                if not fs_path.exists():
                    file_status = "stale_path"
                    issues.append(f"STALE_PATH: {module_path}")

        # Determine if collection-safe
        is_safe = file_status == "resolvable"

        # Map to PyTest Lifecycle triage
        triage_category = "resolvable"
        if file_status == "missing":
            triage_category = "production_bug_fix"  # Check 1.1
        elif file_status == "stale_path":
            triage_category = "stale_reference_fix"  # Check 1.2
        elif file_status in ["syntax_error", "circular"]:
            triage_category = "anti_pattern"  # BLOCKED

        # Update summary
        summary["by_category"][file_status] += 1
        summary["by_layer"][idx.layer_of(test_file)] += 1
        if is_safe:
            summary["collection_safe"] += 1
        else:
            summary["collection_fatal"] += 1

        file_reports.append(
            {
                "file": test_file,
                "layer": idx.layer_of(test_file),
                "status": file_status,
                "collection_safe": is_safe,
                "triage_category": triage_category,
                "issues": issues,
                "imports_count": len(imported_modules),
            },
        )

    # Build final report
    report = {
        "meta": {
            "scanner_version": idx.result.manifest.scanner_version,
            "total_modules": len(all_modules),
            "syntax_errors": len(syntax_errors),
            "cycle_nodes": len(cycle_nodes),
        },
        "summary": summary,
        "files": file_reports,
    }

    # Output
    if args.json:
        try:
            out_path = Path(args.json)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            _logger.info(f"Collection safety report written to: {out_path}")
        except OSError as e:
            _logger.error(f"Failed to write report: {e}")
            return 1
    else:
        # Summary output
        print("Collection Safety Analysis")
        print("=========================")
        print(f"Files scanned: {summary['files_scanned']}")
        print(f"Collection-safe: {summary['collection_safe']}")
        print(f"Collection-fatal: {summary['collection_fatal']}")
        print()
        print("By category:")
        for cat, count in summary["by_category"].items():
            if count > 0:
                print(f"  {cat}: {count}")
        print()
        print("By layer:")
        for layer, count in sorted(summary["by_layer"].items()):
            print(f"  {layer}: {count}")
        print()

        # Show problematic files
        problematic = [f for f in file_reports if not f["collection_safe"]]
        if problematic:
            print("Problematic files (collection-fatal):")
            display_limit = min(len(problematic), PROBLEM_FILE_DISPLAY_LIMIT)
            for f in problematic[:display_limit]:
                print(f"  {f['file']} [{f['status']}] -> {f['triage_category']}")
                for issue in f["issues"]:
                    print(f"    {issue}")
            if len(problematic) > PROBLEM_FILE_DISPLAY_LIMIT:
                print(f"  ... and {len(problematic) - PROBLEM_FILE_DISPLAY_LIMIT} more")

    return 0


def cmd_groups(args: argparse.Namespace, idx: ADGIndex) -> int:
    """Partition test files into N balanced groups by layer.

    Args:
        args: Parsed command line arguments
        idx: Pre-built ADG index

    Returns:
        Exit code (0 for success)
    """
    n = max(1, args.workers)  # Ensure at least 1 worker

    # Collect all test files from result
    all_test_files: list[str] = sorted(
        {
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        },
    )

    if not all_test_files:
        _logger.warning("No test files found")
        print(
            json.dumps({"workers": [], "total_files": 0, "layers": {}})
            if args.format == "json"
            else "No test files found"
        )
        return 0

    # Group by layer
    by_layer: dict[str, list[str]] = defaultdict(list)
    for tf in all_test_files:
        layer = idx.layer_of(tf)
        by_layer[layer].append(tf)

    # Assign layers to workers round-robin by descending layer size
    workers: list[list[str]] = [[] for _ in range(n)]
    worker_sizes = [0] * n
    for layer in sorted(by_layer, key=lambda l: -len(by_layer[l])):
        # assign to smallest worker
        target = min(range(n), key=lambda i: worker_sizes[i])
        workers[target].extend(by_layer[layer])
        worker_sizes[target] += len(by_layer[layer])

    if args.format == "json":
        out: dict[str, Any] = {
            f"worker_{i}": {
                "files": workers[i],
                "count": len(workers[i]),
            }
            for i in range(n)
        }
        out["total_files"] = len(all_test_files)
        out["layers"] = {k: len(v) for k, v in sorted(by_layer.items())}
        print(json.dumps(out, indent=2))
    else:
        for i, group in enumerate(workers):
            print(f"\n# Worker {i} ({len(group)} files):")
            for f in group:
                print(f"  {f}")

    return 0


def cmd_report(args: argparse.Namespace, idx: ADGIndex) -> int:
    """Write a full JSON report combining gap analysis and layer breakdown.

    Args:
        args: Parsed command line arguments
        idx: Pre-built ADG index

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        report = detect_test_gaps(idx.result, hotspot_index=idx.hotspot)
    except Exception as e:
        _logger.error(f"Failed to detect test gaps: {e}")
        return 1

    # Build coverage map
    covered_by: dict[str, list[str]] = {}
    for prod, tests in idx.prod_to_tests.items():
        covered_by[prod] = sorted(tests)

    # Layer breakdown of test files
    all_test_files = sorted(
        {
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        },
    )
    layer_counts: dict[str, int] = defaultdict(int)
    for tf in all_test_files:
        layer_counts[idx.layer_of(tf)] += 1

    out: dict[str, Any] = {
        "meta": {
            "scanner_version": idx.result.manifest.scanner_version,
            "schema_version": idx.result.manifest.schema_version,
            "parsed_module_count": idx.result.manifest.parsed_module_count,
            "syntax_error_count": idx.result.manifest.syntax_error_count,
            "test_covers_count": idx.result.manifest.test_covers_count,
        },
        "gap_summary": report.to_dict(),
        "test_layer_distribution": dict(sorted(layer_counts.items())),
        "coverage_map_sample": dict(list(covered_by.items())[:50]),
        "highest_risk_gaps": [e.to_dict() for e in report.highest_risk_gaps[:30]],
    }

    try:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Report written to: {out_path}")
        print(f"Coverage rate    : {report.coverage_rate:.1%}")
        print(f"Uncovered modules: {len(report.uncovered_modules)}/{report.total_production_modules}")
        print(f"Syntax errors    : {idx.result.manifest.syntax_error_count}")
        return 0
    except OSError as e:
        _logger.error(f"Failed to write report: {e}")
        return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ADG Test Accelerator")
    p.add_argument(
        "--no-tests",
        action="store_true",
        help="Scan without test files (faster, for gap analysis only)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # gap
    gap = sub.add_parser("gap", help="Show uncovered production modules ranked by fan-in")
    gap.add_argument("--top", type=int, default=30, help="Show top N uncovered modules")
    gap.add_argument("--layer", default=None, help="Filter to a specific layer (e.g. L5)")

    # scope
    scope = sub.add_parser("scope", help="Emit test files covering changed modules")
    scope.add_argument(
        "--changed",
        nargs="*",
        default=[],
        metavar="FILE",
        help="Changed file paths (relative to repo root)",
    )
    scope.add_argument("--stdin", action="store_true", help="Read changed files from stdin (one per line)")
    scope.add_argument("--format", choices=["lines", "pytest", "json"], default="lines")

    # groups
    grp = sub.add_parser("groups", help="Partition tests into N parallel worker groups")
    grp.add_argument("--workers", type=int, default=4)
    grp.add_argument("--format", choices=["text", "json"], default="text")

    # report
    rpt = sub.add_parser("report", help="Write full JSON report")
    rpt.add_argument("--out", default="docs/reports/plans/adg_test_report.json")

    # collection-safety
    cs = sub.add_parser("collection-safety", help="Analyze test file collection safety via ADG")
    cs.add_argument("--layer", default=None, help="Filter to a specific layer (e.g. L0)")
    cs.add_argument("--json", default=None, help="Output JSON report to file")

    return p


def main() -> int:
    """Main entry point with proper exit code handling.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = _build_parser()
    args = parser.parse_args()

    include_tests = not args.no_tests
    t0 = time.time()
    _logger.info(f"Scanning (include_tests={include_tests})...")

    try:
        scanner = ADGStaticScanner(include_tests=include_tests)
        result = scanner.scan()
    except Exception as e:
        _logger.error(f"ADG scan failed: {e}")
        return 1

    _logger.info(
        f"Scan done in {time.time() - t0:.1f}s — {len(result.modules)} modules, {len(result.edges)} edges",
    )

    idx = ADGIndex(result)

    command_map = {
        "gap": cmd_gap,
        "scope": cmd_scope,
        "groups": cmd_groups,
        "report": cmd_report,
        "collection-safety": cmd_collection_safety,
    }

    cmd_func = command_map.get(args.command)
    if cmd_func is None:
        _logger.error(f"Unknown command: {args.command}")
        return 1

    return cmd_func(args, idx)


if __name__ == "__main__":
    sys.exit(main())
