"""E15: Test Gap Detector.

Surfaces modules that have zero ``covers`` edges pointing to them — these
are production modules with no test coverage signal in the ADG.

Outputs:
  ``TestGapReport`` with:
    - ``uncovered_modules``:  production modules with no covers edges
    - ``covered_modules``:    production modules that have at least one covers edge
    - ``coverage_rate``:      fraction of production modules covered
    - ``gap_by_layer``:       per-layer breakdown of gaps
    - ``highest_risk_gaps``:  uncovered modules with the most importers
                              (highest blast radius if they break)

Usage::

    from agentic_core.adg.analysis.test_gap import detect_test_gaps

    report = detect_test_gaps(result, hotspot_index=idx)
    print(report.summary)
    for m in report.highest_risk_gaps[:10]:
        print(m)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import module_path_to_layer

if TYPE_CHECKING:
    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.extraction.static_scanner import ScanResult

_MODULE_PREFIX = "ADG::Module::"

_PRODUCTION_EXCLUDES: tuple[str, ...] = (
    "tests/",
    "ops_scripts/",
    "tools/",
    ".py.bak",
)


def _is_production(module_path: str) -> bool:
    """Return True iff module_path is a production (non-test, non-ops) file."""
    norm = module_path.replace("\\", "/")
    return not any(norm.startswith(exc) or norm.endswith(exc) for exc in _PRODUCTION_EXCLUDES)


@dataclass
class TestGapEntry:
    """One uncovered production module."""

    module_path: str
    layer: str
    fan_in: int = 0

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "fan_in": self.fan_in,
        }


@dataclass
class TestGapReport:
    """Full test-coverage gap analysis."""

    uncovered_modules: list[TestGapEntry] = field(default_factory=list)
    covered_modules: list[str] = field(default_factory=list)
    total_production_modules: int = 0
    coverage_rate: float = 0.0
    gap_by_layer: dict[str, int] = field(default_factory=dict)
    highest_risk_gaps: list[TestGapEntry] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"test_gap coverage={self.coverage_rate:.1%} "
            f"covered={len(self.covered_modules)} "
            f"uncovered={len(self.uncovered_modules)} "
            f"total_production={self.total_production_modules}"
        )

    def to_dict(self) -> dict:
        return {
            "total_production_modules": self.total_production_modules,
            "covered_count": len(self.covered_modules),
            "uncovered_count": len(self.uncovered_modules),
            "coverage_rate": round(self.coverage_rate, 4),
            "summary": self.summary,
            "gap_by_layer": dict(sorted(self.gap_by_layer.items())),
            "highest_risk_gaps": [e.to_dict() for e in self.highest_risk_gaps],
            "uncovered_modules": [e.to_dict() for e in self.uncovered_modules],
            "covered_modules": sorted(self.covered_modules),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def detect_test_gaps(
    result: ScanResult,
    hotspot_index: HotspotIndex | None = None,
    include_layers: list[str] | None = None,
) -> TestGapReport:
    """Detect production modules with no ADG test-coverage signal.

    Algorithm:
    1. Collect all module_paths that appear as ``to_name`` in a ``covers`` edge.
    2. From ``result.modules``, filter to production-only paths.
    3. Modules in (2) not in (1) are the test gaps.
    4. Optionally filter to ``include_layers`` if provided.
    5. Sort gaps by fan_in descending (highest blast-radius first).

    Args:
        result: Full ScanResult from the static scanner.
        hotspot_index: Optional pre-built HotspotIndex for fan_in lookup.
        include_layers: Optional layer whitelist — gaps are only reported for
                        modules in these layers.
    """
    # Step 1: modules that are covered
    covered: set[str] = set()
    for edge in result.edges:
        if edge.relation_type == "covers":
            to_name = edge.to_name
            if to_name.startswith(_MODULE_PREFIX):
                covered.add(to_name[len(_MODULE_PREFIX) :])

    # Step 2: production modules
    production = [m for m in result.modules if _is_production(m)]

    # Step 3 & 4: gaps
    gap_by_layer: dict[str, int] = {}
    uncovered: list[TestGapEntry] = []
    covered_list: list[str] = []

    for mod in production:
        layer = module_path_to_layer(mod)
        if include_layers and layer not in include_layers:
            continue

        fi = hotspot_index.fan_in(mod) if hotspot_index else 0

        if mod not in covered:
            entry = TestGapEntry(module_path=mod, layer=layer, fan_in=fi)
            uncovered.append(entry)
            gap_by_layer[layer] = gap_by_layer.get(layer, 0) + 1
        else:
            covered_list.append(mod)

    total_prod = len(production)
    cov_rate = len(covered_list) / total_prod if total_prod else 0.0

    # Step 5: highest risk = most importers
    highest_risk = sorted(uncovered, key=lambda e: -e.fan_in)[:20]

    return TestGapReport(
        uncovered_modules=sorted(uncovered, key=lambda e: e.module_path),
        covered_modules=sorted(covered_list),
        total_production_modules=total_prod,
        coverage_rate=cov_rate,
        gap_by_layer=gap_by_layer,
        highest_risk_gaps=highest_risk,
    )


__all__ = [
    "TestGapReport",
    "TestGapEntry",
    "detect_test_gaps",
]
