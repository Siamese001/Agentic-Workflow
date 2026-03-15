"""E14: Hotspot Index — O(1) fan-in / fan-out / coupling metrics on ScanResult.

Computes a structural hotspot index at build time (one linear pass over edges)
so downstream code can query fan-in, fan-out, and coupling with O(1) lookups.

Definitions:
  fan_in(M)   = number of distinct modules that import M  (afferent coupling Ca)
  fan_out(M)  = number of distinct modules M imports      (efferent coupling Ce)
  instability = Ce / (Ca + Ce)   0=stable, 1=unstable
  coupling(M) = fan_in + fan_out  (raw structural coupling)

A module is a "hotspot" if its coupling exceeds a configurable threshold.

Usage::

    from agentic_core.adg.analysis.hotspot_index import HotspotIndex

    idx = HotspotIndex.build(scan_result)
    fi = idx.fan_in("agentic_core/L0_routing/engines/path_router.py")
    fo = idx.fan_out("agentic_core/L0_routing/engines/path_router.py")
    hotspots = idx.top_hotspots(n=20)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_MODULE_PREFIX = "ADG::Module::"

_DEFAULT_HOTSPOT_THRESHOLD = 10


@dataclass
class ModuleCoupling:
    """Structural coupling metrics for one module."""

    module_path: str
    fan_in: int = 0
    fan_out: int = 0
    instability: float = 0.0
    coupling: int = 0

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "fan_in": self.fan_in,
            "fan_out": self.fan_out,
            "instability": round(self.instability, 3),
            "coupling": self.coupling,
        }


@dataclass
class HotspotIndex:
    """O(1)-queryable structural hotspot index built from a ScanResult.

    Attributes:
        _fan_in:  {module_path: set of distinct importer module_paths}
        _fan_out: {module_path: set of distinct dependency module_paths}
    """

    _fan_in: dict[str, set[str]] = field(default_factory=dict)
    _fan_out: dict[str, set[str]] = field(default_factory=dict)
    _all_modules: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, result: ScanResult) -> HotspotIndex:
        """Build the index in a single linear pass over result.edges.

        Handles both ``ADG::Module::a/b/c.py`` and ``ADG::Symbol::a.b.c``
        node names — the latter is resolved to ``a/b/c.py`` so fan-in
        counts reflect real structural coupling even when edges use
        symbol-level addressing.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HotspotIndex.build")

        idx = cls()
        module_set = set(result.modules)
        idx._all_modules = module_set

        _sym = "ADG::Symbol::"
        _mod = _MODULE_PREFIX

        def _to_path(name: str) -> str | None:
            if name.startswith(_mod):
                return name[len(_mod):]
            if name.startswith(_sym):
                sym = name[len(_sym):]
                parts = sym.split(".")
                # Try from most-specific to least-specific:
                # a.b.c.func -> a/b/c/func.py, a/b/c.py, a/b/__init__.py ...
                for n in range(len(parts), 0, -1):
                    prefix = "/".join(parts[:n])
                    if prefix + ".py" in module_set:
                        return prefix + ".py"
                    # guardian: allow-path-string
                    if prefix + "/__init__.py" in module_set:
                        # guardian: allow-path-string
                        return prefix + "/__init__.py"
            return None

        for edge in result.edges:
            if edge.relation_type not in (
                "imports", "reads_from", "calls", "instantiates", "implements",
            ):
                continue
            if not edge.from_name.startswith(_mod):
                continue

            from_path = edge.from_name[len(_mod):]
            to_path = _to_path(edge.to_name)
            if to_path is None or from_path == to_path:
                continue

            idx._fan_out.setdefault(from_path, set()).add(to_path)
            idx._fan_in.setdefault(to_path, set()).add(from_path)

        return idx

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def fan_in(self, module_path: str) -> int:
        """Number of distinct modules that structurally depend on module_path."""
        return len(self._fan_in.get(module_path, set()))

    def fan_out(self, module_path: str) -> int:
        """Number of distinct modules that module_path depends on."""
        return len(self._fan_out.get(module_path, set()))

    def instability(self, module_path: str) -> float:
        """Ce / (Ca + Ce) — 0.0 = maximally stable, 1.0 = maximally unstable."""
        ca = self.fan_in(module_path)
        ce = self.fan_out(module_path)
        total = ca + ce
        return round(ce / total, 3) if total else 0.0

    def coupling(self, module_path: str) -> int:
        """Raw structural coupling = fan_in + fan_out."""
        return self.fan_in(module_path) + self.fan_out(module_path)

    def metrics(self, module_path: str) -> ModuleCoupling:
        """Return full coupling metrics for one module."""
        ca = self.fan_in(module_path)
        ce = self.fan_out(module_path)
        total = ca + ce
        inst = round(ce / total, 3) if total else 0.0
        return ModuleCoupling(
            module_path=module_path,
            fan_in=ca,
            fan_out=ce,
            instability=inst,
            coupling=total,
        )

    def top_hotspots(
        self,
        n: int = 20,
        threshold: int = _DEFAULT_HOTSPOT_THRESHOLD,
        key: str = "coupling",
    ) -> list[ModuleCoupling]:
        """Return the top-n hotspot modules sorted by *key* descending.

        ``key`` must be one of ``'coupling'``, ``'fan_in'``, ``'fan_out'``,
        ``'instability'``.
        """
        all_paths = self._all_modules | set(self._fan_in) | set(self._fan_out)
        scored = [self.metrics(p) for p in all_paths]
        scored = [m for m in scored if getattr(m, key) >= threshold]
        return sorted(scored, key=lambda m: -getattr(m, key))[:n]

    def importers_of(self, module_path: str) -> list[str]:
        """Sorted list of modules that directly depend on module_path."""
        return sorted(self._fan_in.get(module_path, set()))

    def dependencies_of(self, module_path: str) -> list[str]:
        """Sorted list of modules that module_path directly depends on."""
        return sorted(self._fan_out.get(module_path, set()))

    def stats(self) -> dict:
        """Summary statistics for the entire index."""
        all_paths = self._all_modules | set(self._fan_in) | set(self._fan_out)
        if not all_paths:
            return {"total_modules": 0, "max_fan_in": 0, "max_fan_out": 0, "avg_coupling": 0.0}

        couplings = [self.coupling(p) for p in all_paths]
        fan_ins = [self.fan_in(p) for p in all_paths]
        fan_outs = [self.fan_out(p) for p in all_paths]

        return {
            "total_modules": len(all_paths),
            "max_fan_in": max(fan_ins),
            "max_fan_out": max(fan_outs),
            "max_coupling": max(couplings),
            "avg_coupling": round(sum(couplings) / len(couplings), 2),
            "avg_fan_in": round(sum(fan_ins) / len(fan_ins), 2),
            "avg_fan_out": round(sum(fan_outs) / len(fan_outs), 2),
        }

    def to_json(self, n: int = 50) -> str:
        """Serialise top-n hotspots to JSON."""
        return json.dumps(
            {
                "stats": self.stats(),
                "top_hotspots": [m.to_dict() for m in self.top_hotspots(n=n, threshold=0)],
            },
            indent=2,
            sort_keys=True,
        )


__all__ = [
    "HotspotIndex",
    "ModuleCoupling",
]
