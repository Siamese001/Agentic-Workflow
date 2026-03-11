"""Enhancement 8: Ownership / blast-radius overlay.

Associates each module in the ADG with:
  - owner: logical domain (platform, apps_rg, apps_lic, apps_shared, safety, etc.)
  - criticality: low / medium / high
  - runtime_surface: CI / prod / healing / governance

Also provides OwnershipRegistry.blast_radius_report() that combines
ownership metadata with a blast-radius node set to produce a structured
impact report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal

Owner = Literal["platform", "apps_rg", "apps_lic", "apps_shared", "safety", "observability", "unknown"]
Criticality = Literal["low", "medium", "high"]
RuntimeSurface = Literal["CI", "prod", "healing", "governance", "unknown"]


@dataclass
class ModuleOwnership:
    """Ownership metadata for a single module path."""

    module_path: str
    owner: Owner = "unknown"
    criticality: Criticality = "medium"
    runtime_surface: RuntimeSurface = "unknown"

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "owner": self.owner,
            "criticality": self.criticality,
            "runtime_surface": self.runtime_surface,
        }


_PREFIX_OWNER_MAP: list[tuple[str, Owner, Criticality, RuntimeSurface]] = [
    ("agentic_core/L0_routing", "platform", "high", "prod"),
    ("agentic_core/L1_cognition", "platform", "high", "prod"),
    ("agentic_core/L2_execution", "platform", "high", "governance"),
    ("agentic_core/L3_orchestration", "platform", "high", "prod"),
    ("agentic_core/L4_memory", "platform", "medium", "prod"),
    ("agentic_core/L5_safety", "safety", "high", "governance"),
    ("agentic_core/L6_observability", "observability", "medium", "prod"),
    ("agentic_core/adg", "platform", "high", "CI"),
    ("apps_rg/", "apps_rg", "medium", "prod"),
    ("apps_lic/", "apps_lic", "medium", "prod"),
    ("apps_shared/", "apps_shared", "medium", "prod"),
    ("system_learning/", "platform", "medium", "healing"),
    ("ops_scripts/", "platform", "low", "CI"),
    ("tools/", "platform", "low", "CI"),
    ("tests/", "platform", "low", "CI"),
]


def _infer_ownership(module_path: str) -> ModuleOwnership:
    """Infer ownership from module path prefix rules."""
    norm = module_path.replace("\\", "/").lstrip("ADG::Module::")
    for prefix, owner, criticality, surface in _PREFIX_OWNER_MAP:
        if norm.startswith(prefix):
            return ModuleOwnership(
                module_path=module_path,
                owner=owner,
                criticality=criticality,
                runtime_surface=surface,
            )
    return ModuleOwnership(module_path=module_path)


class OwnershipRegistry:
    """Registry that provides ownership lookups and blast-radius reports.

    Usage:
        registry = OwnershipRegistry.from_scan_result(result)
        report = registry.blast_radius_report("agentic_core/L2_execution/UniversalWriteGateway.py", impact_nodes)
    """

    def __init__(self) -> None:
        self._map: dict[str, ModuleOwnership] = {}

    @classmethod
    def from_scan_result(cls, result: object) -> "OwnershipRegistry":
        """Build registry from a ScanResult's module list."""
        reg = cls()
        for mod in getattr(result, "modules", []):
            reg._map[mod] = _infer_ownership(mod)
        return reg

    @classmethod
    def from_module_list(cls, modules: list[str]) -> "OwnershipRegistry":
        reg = cls()
        for mod in modules:
            reg._map[mod] = _infer_ownership(mod)
        return reg

    def get(self, module_path: str) -> ModuleOwnership:
        return self._map.get(module_path, _infer_ownership(module_path))

    def blast_radius_report(
        self,
        changed_module: str,
        impacted_modules: list[str],
    ) -> dict:
        """Produce a blast-radius report for a changed module.

        Args:
            changed_module: The module that changed.
            impacted_modules: All transitively impacted modules (from query_engine).

        Returns:
            Structured dict with owner, criticality, impacted domains, and
            a HIGH/MEDIUM/LOW aggregate risk level.
        """
        changed_meta = self.get(changed_module)

        impacted_by_owner: dict[str, list[str]] = {}
        high_count = 0
        for mod in impacted_modules:
            meta = self.get(mod)
            impacted_by_owner.setdefault(meta.owner, []).append(mod)
            if meta.criticality == "high":
                high_count += 1

        if changed_meta.criticality == "high" or high_count >= 3:
            aggregate_risk = "HIGH"
        elif high_count >= 1 or changed_meta.criticality == "medium":
            aggregate_risk = "MEDIUM"
        else:
            aggregate_risk = "LOW"

        surfaces: set[str] = {changed_meta.runtime_surface}
        for mod in impacted_modules:
            surfaces.add(self.get(mod).runtime_surface)
        surfaces.discard("unknown")

        return {
            "changed_module": changed_module,
            "owner": changed_meta.owner,
            "criticality": changed_meta.criticality,
            "runtime_surface": changed_meta.runtime_surface,
            "aggregate_risk": aggregate_risk,
            "impacted_module_count": len(impacted_modules),
            "impacted_high_criticality_count": high_count,
            "affected_domains": sorted(impacted_by_owner.keys()),
            "affected_surfaces": sorted(surfaces),
            "impacted_by_owner": {k: sorted(v) for k, v in sorted(impacted_by_owner.items())},
        }

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in sorted(self._map.items())}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
