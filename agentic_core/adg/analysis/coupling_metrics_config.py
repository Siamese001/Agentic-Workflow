"""E16: Coupling / Cohesion Metrics — Martin's package-level metrics.

Computes the classic Robert C. Martin stability metrics for every module:

  Ca  = Afferent coupling   (fan_in:  # modules that depend on this one)
  Ce  = Efferent coupling   (fan_out: # modules this one depends on)
  I   = Instability         Ce / (Ca + Ce)        0=stable, 1=unstable
  A   = Abstractness        # abstract classes / total classes
  D   = Distance from main sequence   |A + I - 1|  (0=on line, 1=far off)

Zones:
  D < 0.3  → Zone of Pain (stable + concrete — hard to change)
  D > 0.7  → Zone of Uselessness (unstable + abstract — useless abstractions)

Usage::

    from agentic_core.adg.analysis.coupling_metrics import compute_coupling_metrics

    report = compute_coupling_metrics(result)
    for m in report.top_pain_zone[:10]:
        print(m.module_path, m.distance, m.zone)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# Configuration constants

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from tqdm import tqdm

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

_ABSTRACT_BASE_NAMES: frozenset[str] = frozenset({"ABC", "ABCMeta", "Protocol", "abstract"})


@dataclass
class ModuleMetrics:
    """Martin stability metrics for one module."""

    module_path: str
    ca: int = 0
    ce: int = 0
    instability: float = 0.0
    abstractness: float = 0.0
    distance: float = 0.0
    zone: str = "BALANCED"
    total_classes: int = 0
    abstract_classes: int = 0

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "ca": self.ca,
            "ce": self.ce,
            "instability": round(self.instability, 3),
            "abstractness": round(self.abstractness, 3),
            "distance": round(self.distance, 3),
            "zone": self.zone,
            "total_classes": self.total_classes,
            "abstract_classes": self.abstract_classes,
        }


@dataclass
class CouplingMetricsReport:
    """Full coupling/cohesion metrics for the entire repository."""

    metrics_by_module: dict[str, ModuleMetrics] = field(default_factory=dict)

    @property
    def top_pain_zone(self) -> list[ModuleMetrics]:
        """Modules in the Zone of Pain (D < 0.3, I < 0.3) — high risk."""
        pain = [m for m in self.metrics_by_module.values() if m.zone == "PAIN"]
        return sorted(pain, key=lambda m: m.distance)

    @property
    def top_uselessness_zone(self) -> list[ModuleMetrics]:
        """Modules in the Zone of Uselessness (D > 0.7) — dead abstractions."""
        useless = [m for m in self.metrics_by_module.values() if m.zone == "USELESSNESS"]
        return sorted(useless, key=lambda m: -m.distance)

    @property
    def most_unstable(self) -> list[ModuleMetrics]:
        """Top 20 most unstable (I near 1.0) modules."""
        return sorted(
            self.metrics_by_module.values(),
            key=lambda m: -m.instability,
        )[:20]

    @property
    def most_stable(self) -> list[ModuleMetrics]:
        """Top 20 most stable (I near 0.0) modules with high fan_in."""
        return sorted(
            [m for m in self.metrics_by_module.values() if m.ca > 0],
            key=lambda m: (m.instability, -m.ca),
        )[:20]

    def to_dict(self) -> dict:
        return {
            "total_modules": len(self.metrics_by_module),
            "pain_zone_count": len(self.top_pain_zone),
            "uselessness_zone_count": len(self.top_uselessness_zone),
            "top_pain_zone": [m.to_dict() for m in self.top_pain_zone[:20]],
            "top_uselessness_zone": [m.to_dict() for m in self.top_uselessness_zone[:20]],
            "most_unstable": [m.to_dict() for m in self.most_unstable],
            "most_stable": [m.to_dict() for m in self.most_stable],
            "metrics_by_module": {path: m.to_dict() for path, m in sorted(self.metrics_by_module.items())},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _classify_zone(instability: float, abstractness: float) -> str:
    distance = abs(abstractness + instability - 1.0)
    if distance < 0.3 and instability < 0.3:
        return "PAIN"
    if distance > 0.7:
        return "USELESSNESS"
    return "BALANCED"


def compute_coupling_metrics(result: ScanResult) -> CouplingMetricsReport:
    """Compute Martin coupling/cohesion metrics for all scanned modules.

    Algorithm:
    1. Single pass over edges to build Ca/Ce for each module.
    2. Derive abstractness (A) from ``implements`` edges pointing to ABC/Protocol.
    3. Compute I, A, D and zone classification per module.
    """
    ca: dict[str, set[str]] = {}
    ce: dict[str, set[str]] = {}
    abstract_count: dict[str, int] = {}
    total_class_count: dict[str, int] = {}

    for edge in tqdm(result.edges, desc="Processing", unit="item"):
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue

        from_path = edge.from_name[len(_MODULE_PREFIX) :]

        if edge.relation_type in ("imports", "calls", "instantiates", "implements"):
            if edge.to_name.startswith(_MODULE_PREFIX):
                to_path = edge.to_name[len(_MODULE_PREFIX) :]
                if from_path != to_path:
                    ce.setdefault(from_path, set()).add(to_path)
                    ca.setdefault(to_path, set()).add(from_path)

        if edge.relation_type == "implements":
            sym = edge.symbol or ""
            mod = from_path
            total_class_count[mod] = total_class_count.get(mod, 0) + 1
            if any(base in sym for base in _ABSTRACT_BASE_NAMES):
                abstract_count[mod] = abstract_count.get(mod, 0) + 1

    all_modules = set(result.modules)
    all_modules |= set(ca.keys()) | set(ce.keys())

    metrics: dict[str, ModuleMetrics] = {}
    for mod in tqdm(all_modules, desc="Processing", unit="item"):
        ca_n = len(ca.get(mod, set()))
        ce_n = len(ce.get(mod, set()))
        total = ca_n + ce_n
        instability = round(ce_n / total, 3) if total else 0.0

        total_cls = total_class_count.get(mod, 0)
        abstract_cls = abstract_count.get(mod, 0)
        abstractness = round(abstract_cls / total_cls, 3) if total_cls else 0.0

        distance = round(abs(abstractness + instability - 1.0), 3)
        zone = _classify_zone(instability, abstractness)

        metrics[mod] = ModuleMetrics(
            module_path=mod,
            ca=ca_n,
            ce=ce_n,
            instability=instability,
            abstractness=abstractness,
            distance=distance,
            zone=zone,
            total_classes=total_cls,
            abstract_classes=abstract_cls,
        )

    return CouplingMetricsReport(metrics_by_module=metrics)


__all__ = [
    "CouplingMetricsReport",
    "ModuleMetrics",
    "compute_coupling_metrics",
]
