"""Test Coverage Mapper — builds symbol→tests and module→tests mappings from ADG.

Uses the ADG import graph (G1) and inheritance graph (G3) to determine which
test files exercise which source modules and symbols. No heuristics — only
structural import-graph evidence.

Two index types:
  module_to_tests  : source_module_rel_path -> sorted list of test rel paths
  symbol_to_tests  : fully_qualified_symbol  -> sorted list of test rel paths

All paths are repo-relative forward-slash strings.
No silent fallback to full test suite — unmapped modules are reported explicitly.

CLI:
    python -m tools.test_coverage_mapper --changed agentic_core/adg/schema.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


class TestCoverageMapper:
    """Build module→tests and symbol→tests coverage indexes from a ScanResult.

    The mapping is derived purely from the import graph:
      - A test file T covers module M if T transitively imports M.
      - A test file T covers symbol S if T imports or inherits from M where S is defined.
    """

    def __init__(
        self,
        result: ScanResult,
        repo_root: Path | None = None,
    ) -> None:
        self._result = result
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._module_to_tests: dict[str, list[str]] = {}
        self._symbol_to_tests: dict[str, list[str]] = {}
        self._test_modules: set[str] = set()
        self._built = False

    def build(self) -> "TestCoverageMapper":
        """Build both indexes. Idempotent."""
        if self._built:
            return self
        self._collect_test_modules()
        self._build_direct_import_coverage()
        self._build_transitive_coverage()
        self._sort_indexes()
        self._built = True
        return self

    def _collect_test_modules(self) -> None:
        """Identify all test module paths (files under tests/ directory)."""
        for mod_path in self._result.modules:
            if mod_path.startswith("tests/") or "/test_" in mod_path or mod_path.startswith("test_"):
                self._test_modules.add(mod_path)

    def _build_direct_import_coverage(self) -> None:
        """For each test module, record direct imports as covered."""
        module_adg_by_path: dict[str, str] = {}
        for mod_path in self._result.modules:
            adg = _MODULE_PREFIX + mod_path
            module_adg_by_path[mod_path] = adg

        # Build reverse: adg_name -> rel_path for fast lookup
        adg_to_path: dict[str, str] = {v: k for k, v in module_adg_by_path.items()}

        # Build once here so parent_path lookups inside the loop are O(1)
        module_set: set[str] = set(self._result.modules)

        for edge in self._result.edges:
            if edge.relation_type != "imports":
                continue
            from_adg = edge.from_name
            to_adg = edge.to_name

            from_path = adg_to_path.get(from_adg, "")
            if not from_path or from_path not in self._test_modules:
                continue

            # to_adg can be a module or symbol
            if to_adg.startswith(_MODULE_PREFIX):
                target_path = to_adg[len(_MODULE_PREFIX):]
                self._add_coverage(self._module_to_tests, target_path, from_path)
            elif to_adg.startswith(_SYMBOL_PREFIX):
                symbol_name = to_adg[len(_SYMBOL_PREFIX):]
                self._add_coverage(self._symbol_to_tests, symbol_name, from_path)
                # Also credit the parent module (dot-notation up to last segment)
                if "." in symbol_name:
                    parent_dot = ".".join(symbol_name.split(".")[:-1])
                    parent_path = parent_dot.replace(".", "/") + ".py"
                    if parent_path in module_set:
                        self._add_coverage(self._module_to_tests, parent_path, from_path)

    def _build_transitive_coverage(self) -> None:
        """BFS: extend coverage transitively (test imports A, A imports B => test covers B)."""
        # Build reverse import index: module_path -> set of test modules that (directly) import it
        direct_covered_by: dict[str, set[str]] = {}
        for mod_path, tests in self._module_to_tests.items():
            for t in tests:
                if mod_path not in direct_covered_by:
                    direct_covered_by[mod_path] = set()
                direct_covered_by[mod_path].add(t)

        # Build forward import index: module_path -> list of modules it imports
        forward_imports: dict[str, set[str]] = {}
        adg_to_path: dict[str, str] = {}
        for mod_path in self._result.modules:
            adg_to_path[_MODULE_PREFIX + mod_path] = mod_path

        for edge in self._result.edges:
            if edge.relation_type != "imports":
                continue
            from_path = adg_to_path.get(edge.from_name, "")
            to_path = adg_to_path.get(edge.to_name, "")
            if from_path and to_path:
                if from_path not in forward_imports:
                    forward_imports[from_path] = set()
                forward_imports[from_path].add(to_path)

        # BFS from each test module through its import closure
        for test_path in sorted(self._test_modules):
            visited: set[str] = set()
            frontier = list(forward_imports.get(test_path, set()))
            while frontier:
                mod = frontier.pop()
                if mod in visited:
                    continue
                visited.add(mod)
                self._add_coverage(self._module_to_tests, mod, test_path)
                frontier.extend(m for m in forward_imports.get(mod, set()) if m not in visited)

    @staticmethod
    def _add_coverage(index: dict[str, list[str]], key: str, test_path: str) -> None:
        if key not in index:
            index[key] = []
        if test_path not in index[key]:
            index[key].append(test_path)

    def _sort_indexes(self) -> None:
        for k in self._module_to_tests:
            self._module_to_tests[k].sort()
        for k in self._symbol_to_tests:
            self._symbol_to_tests[k].sort()

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def tests_for_module(self, module_rel_path: str) -> list[str]:
        """Return sorted list of test paths that cover the given source module."""
        if not self._built:
            self.build()
        return list(self._module_to_tests.get(module_rel_path, []))

    def tests_for_modules(self, module_paths: list[str]) -> list[str]:
        """Return deduplicated sorted test paths covering all given modules."""
        if not self._built:
            self.build()
        result: set[str] = set()
        for m in module_paths:
            result.update(self._module_to_tests.get(m, []))
        return sorted(result)

    def coverage_report(self) -> dict:
        """Return a summary of coverage gaps and hotspots."""
        if not self._built:
            self.build()
        source_modules = [m for m in self._result.modules if m not in self._test_modules]
        covered = [m for m in source_modules if m in self._module_to_tests]
        uncovered = [m for m in source_modules if m not in self._module_to_tests]
        return {
            "source_module_count": len(source_modules),
            "test_module_count": len(self._test_modules),
            "covered_count": len(covered),
            "uncovered_count": len(uncovered),
            "coverage_pct": round(100.0 * len(covered) / max(len(source_modules), 1), 2),
            "uncovered_modules": sorted(uncovered),
            "hotspot_modules": sorted(
                [
                    {"module": k, "test_count": len(v)}
                    for k, v in self._module_to_tests.items()
                    if len(v) >= 3
                ],
                key=lambda x: -x["test_count"],
            )[:20],
        }

    def to_index_dict(self) -> dict:
        """Serialize both indexes to a deterministic dict."""
        if not self._built:
            self.build()
        return {
            "module_to_tests": {k: v for k, v in sorted(self._module_to_tests.items())},
            "symbol_to_tests": {k: v for k, v in sorted(self._symbol_to_tests.items())},
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _get_scan_result(repo_root: Path) -> ScanResult:
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    return load_or_scan(repo_root=str(repo_root))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ADG Test Coverage Mapper")
    parser.add_argument(
        "--changed",
        nargs="*",
        default=[],
        help="Repo-relative source file paths to look up tests for",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print full coverage report instead of per-file tests",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repo root directory (default: cwd)",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Write full index to a JSON file",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    result = _get_scan_result(repo_root)
    mapper = TestCoverageMapper(result, repo_root=repo_root).build()

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(mapper.to_index_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(f"Index written: {out_path}")

    if args.report:
        report = mapper.coverage_report()
        print(json.dumps(report, indent=2))
        return 0

    if args.changed:
        tests = mapper.tests_for_modules(args.changed)
        if tests:
            print(json.dumps({"tests": tests, "count": len(tests)}, indent=2))
        else:
            print(json.dumps({"tests": [], "count": 0, "note": "No direct test coverage found via ADG"}))
        return 0

    # Default: print coverage report
    report = mapper.coverage_report()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
