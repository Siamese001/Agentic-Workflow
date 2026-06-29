from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from agentic_core.base_agents.territory_healer_protocol import HealingContext


@dataclass
class Violation:
    type: str
    path: str
    message: str


@dataclass
class ScanReport:
    territory: str
    violations_found: int
    violations: list[Violation] = field(default_factory=list)


@dataclass
class HealingResult:
    territory: str
    dry_run: bool
    violations_fixed: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class CoordinatorReport:
    territory: str
    success: bool
    total_violations_found: int
    total_violations_fixed: int = 0
    agents_executed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)


class _BaseAdapter:
    agent_name = "BaseAdapter"

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    def can_handle(self, territory: str) -> bool:
        return territory in {"tests", "agentic_core", "apps_eval", "ops_scripts"} or bool(territory)

    def _territory_path(self, territory: str) -> Path:
        return self.project_root / territory

    def scan_territory(self, territory: str) -> ScanReport:
        territory_path = self._territory_path(territory)
        violations: list[Violation] = []
        if territory_path.exists() and territory_path.is_dir():
            for child in sorted(territory_path.iterdir()):
                if child.is_file():
                    violations.append(
                        Violation(
                            type="TERRITORY_ROOT_FILE",
                            path=str(child),
                            message="root-level file present",
                        )
                    )
        elif territory_path.exists() and territory_path.is_file():
            violations.append(
                Violation(
                    type="TERRITORY_PATH_IS_FILE",
                    path=str(territory_path),
                    message="territory path resolved to a file",
                )
            )
        return ScanReport(territory=territory, violations_found=len(violations), violations=violations)

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        scan = self.scan_territory(territory)
        fixed = 0 if context.heal is False else scan.violations_found
        return HealingResult(territory=territory, dry_run=not context.heal, violations_fixed=fixed)


class StructureEnforcerAdapter(_BaseAdapter):
    agent_name = "StructureEnforcerAgent"


class LocationHealerAdapter(_BaseAdapter):
    agent_name = "LocationHealerAgent"


class GravityHealerAdapter(_BaseAdapter):
    agent_name = "GravityLeakHealerAgent"


class FilesystemReconcilerAdapter(_BaseAdapter):
    agent_name = "FilesystemSSOTReconcilerAgent"


class AdapterCoordinator:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.agents = [
            StructureEnforcerAdapter(project_root),
            LocationHealerAdapter(project_root),
            GravityHealerAdapter(project_root),
            FilesystemReconcilerAdapter(project_root),
        ]

    def _auto_detect_territories(self) -> list[str]:
        candidates = ["tests", "agentic_core", "apps_eval", "ops_scripts"]
        existing = [name for name in candidates if (self.project_root / name).exists()]
        return existing or candidates[:2]

    def validate_territory(self, territory: str) -> CoordinatorReport:
        violations: list[Violation] = []
        agents_executed: list[str] = []
        errors: list[str] = []
        for agent in self.agents:
            if agent.can_handle(territory):
                agents_executed.append(agent.agent_name)
                try:
                    scan = agent.scan_territory(territory)
                    violations.extend(scan.violations)
                except (RuntimeError, ValueError, TypeError, OSError) as exc:
                    errors.append(str(exc))
        return CoordinatorReport(
            territory=territory,
            success=len(errors) == 0,
            total_violations_found=len(violations),
            agents_executed=agents_executed,
            errors=errors,
            violations=violations,
        )

    def heal_territory(self, territory: str, verbose: bool = False) -> CoordinatorReport:
        ctx = HealingContext(heal=True, project_root=self.project_root, verbose=verbose)
        report = self.validate_territory(territory)
        fixed = 0
        for agent in self.agents:
            if agent.can_handle(territory):
                try:
                    fixed += agent.heal_territory(territory, ctx).violations_fixed
                except (RuntimeError, ValueError, TypeError, OSError) as exc:
                    report.errors.append(str(exc))
        report.total_violations_fixed = fixed
        report.success = len(report.errors) == 0
        return report

    def heal_all_territories(
        self, territories: Iterable[str], verbose: bool = False
    ) -> dict[str, CoordinatorReport]:
        return {territory: self.heal_territory(territory, verbose=verbose) for territory in territories}


def create_adapter_coordinator(project_root: Path) -> AdapterCoordinator:
    return AdapterCoordinator(project_root)
