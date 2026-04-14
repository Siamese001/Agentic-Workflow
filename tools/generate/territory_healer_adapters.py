"""
TerritoryHealerAdapters - Adapter classes to make existing agents work with TerritoryHealerProtocol.

This provides a bridge between the existing agent implementations and the new
simplified territory-level healing interface.
"""

import logging
from pathlib import Path
from typing import Any

from agentic_core.base_agents.territory_healer_protocol import (
    HealingContext,
    HealingResult,
    ScanResult,
    TerritoryHealerProtocol,
    Violation,
)
from tqdm import tqdm

logger = logging.getLogger("TerritoryHealerAdapters")


def _normalize_territory_name(territory: str) -> str:
    """Normalize territory names and reject traversal-like input."""
    territory_path = Path(territory)
    if territory_path.is_absolute() or ".." in territory_path.parts:
        raise ValueError(f"Invalid territory: {territory}")
    normalized = str(territory_path).replace("\\", "/").strip("./")
    if not normalized:
        raise ValueError("Territory must not be empty")
    return normalized


def _path_in_territory(project_root: Path, territory: str, raw_path: str) -> bool:
    """Return True when a violation path belongs to the requested territory."""
    if not raw_path:
        return False
    territory = _normalize_territory_name(territory)
    territory_root = (project_root / territory).resolve()
    try:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (project_root / candidate).resolve()
        else:
            candidate = candidate.resolve()
        candidate.relative_to(territory_root)
        return True
    except (OSError, ValueError):
        normalized = raw_path.replace("\\", "/")
        return normalized == territory or normalized.startswith(f"{territory}/")


def _as_list(value: Any) -> list[Any]:
    """Coerce possibly-null collections to a list."""
    return value if isinstance(value, list) else []


class HierarchyHealerAdapter(TerritoryHealerProtocol):
    """Adapter for HierarchyHealerAgent to implement TerritoryHealerProtocol."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self._agent = None  # Lazy loaded

    @property
    def agent_name(self) -> str:
        return "HierarchyHealerAgent"

    def _get_agent(self):
        """Lazy load the underlying agent."""
        if self._agent is None:
            from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyHealerAgent

            self._agent = HierarchyHealerAgent(project_root=self.project_root)
        return self._agent

    def can_handle(self, territory: str) -> bool:
        """HierarchyHealer can handle any territory."""
        return True

    def scan_territory(self, territory: str) -> ScanResult:
        """Scan territory for hierarchy violations."""
        territory = _normalize_territory_name(territory)
        agent = self._get_agent()

        # Scan for root violations in the territory
        scan_result = agent.scan_root_violations(target_territory=territory)

        violations = []

        # Convert territory root files to Violation objects
        for v in tqdm(_as_list(scan_result.get("territory_root_files")), desc="Processing", unit="item"):
            violations.append(
                Violation(
                    type="TERRITORY_ROOT_FILE",
                    path=v.get("path", ""),
                    message=v.get("message", f"File at {territory} root"),
                    severity="ERROR",
                    details=v,
                )
            )

        # Convert forbidden folders
        for folder in _as_list(scan_result.get("forbidden_folders")):
            violations.append(
                Violation(
                    type="FORBIDDEN_FOLDER",
                    path=folder,
                    message=f"Forbidden folder at root: {folder}",
                    severity="ERROR",
                )
            )

        # Convert archived files
        for filename in _as_list(scan_result.get("archived_files_at_root")):
            violations.append(
                Violation(
                    type="ARCHIVED_FILE_AT_ROOT",
                    path=filename,
                    message=f"Archived file at root: {filename}",
                    severity="WARNING",
                )
            )

        return ScanResult(
            territory=territory,
            violations_found=len(violations),
            violations=violations,
            scan_metadata=scan_result,
        )

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        """Heal hierarchy violations in territory."""
        agent = self._get_agent()

        # First scan
        scan_result = self.scan_territory(territory)

        actions_taken = []
        errors = []
        violations_fixed = 0

        if context.heal and scan_result.violations_found > 0:
            try:
                # Heal root violations with territory context
                heal_result = agent.heal_root_violations(
                    dry_run=False,
                    target_territory=territory,
                )

                # Track actions
                for action in heal_result.get("actions", []):
                    actions_taken.append(action)
                    if action.get("applied"):
                        violations_fixed += 1

                # Track errors
                errors.extend(heal_result.get("errors", []))

                # Also run test structure mirror validation for tests territory
                if territory == "tests":
                    mirror_result = agent.validate_test_structure_mirror(
                        dry_run=False,
                        execute=True,
                    )
                    if mirror_result.get("folders_created", 0) > 0:
                        actions_taken.append(
                            {
                                "type": "TEST_MIRROR_FOLDERS_CREATED",
                                "count": mirror_result["folders_created"],
                                "applied": True,
                            }
                        )
                        violations_fixed += mirror_result.get("violations_found", 0)

            except Exception as e:
                logger.exception(f"Healing failed for {territory}: {e}")
                errors.append(str(e))

        return HealingResult(
            territory=territory,
            agent_name=self.agent_name,
            violations_found=scan_result.violations_found,
            violations_fixed=violations_fixed,
            actions_taken=actions_taken,
            errors=errors,
            success=len(errors) == 0,
            dry_run=not context.heal,
        )


class LocationHealerAdapter(TerritoryHealerProtocol):
    """Adapter for LocationHealerAgent to implement TerritoryHealerProtocol."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self._agent = None

    @property
    def agent_name(self) -> str:
        return "LocationHealerAgent"

    def _get_agent(self):
        """Lazy load the underlying agent."""
        if self._agent is None:
            from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

            self._agent = LocationHealerAgent(project_root=self.project_root)
        return self._agent

    def can_handle(self, territory: str) -> bool:
        """LocationHealer can handle any territory with Python files."""
        return True

    def scan_territory(self, territory: str) -> ScanResult:
        """Scan territory for location violations (wrong folder, depth issues)."""
        from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

        territory = _normalize_territory_name(territory)
        # Use LocationValidatorAgent for scanning
        validator = LocationValidatorAgent(project_root=self.project_root)
        scan_result = validator.run()

        violations = []

        for v in tqdm(_as_list(scan_result.get("violations")), desc="Processing", unit="item"):
            file_path = v.get("file", "")
            if _path_in_territory(self.project_root, territory, file_path):
                violations.append(
                    Violation(
                        type="LOCATION_VIOLATION",
                        path=file_path,
                        message=v.get("reason", "Location violation"),
                        severity="ERROR",
                        details=v,
                    )
                )

        return ScanResult(
            territory=territory,
            violations_found=len(violations),
            violations=violations,
            scan_metadata=scan_result,
        )

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        """Heal location violations in territory."""
        agent = self._get_agent()

        scan_result = self.scan_territory(territory)
        actions_taken = []
        errors = []
        violations_fixed = 0

        if context.heal and scan_result.violations_found > 0:
            try:
                # Use run_with_cleanup which does scan + heal
                heal_result = agent.run_with_cleanup(dry_run=not context.heal)

                # Extract results
                if isinstance(heal_result, dict):
                    violations_fixed = heal_result.get("actions_applied", 0)
                    actions_taken = heal_result.get("detailed_actions", [])

            except Exception as e:
                logger.exception(f"Location healing failed for {territory}: {e}")
                errors.append(str(e))

        return HealingResult(
            territory=territory,
            agent_name=self.agent_name,
            violations_found=scan_result.violations_found,
            violations_fixed=violations_fixed,
            actions_taken=actions_taken,
            errors=errors,
            success=len(errors) == 0,
            dry_run=not context.heal,
        )


class GravityHealerAdapter(TerritoryHealerProtocol):
    """Adapter for GravityLeakHealerAgent to implement TerritoryHealerProtocol."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self._agent = None

    @property
    def agent_name(self) -> str:
        return "GravityLeakHealerAgent"

    def _get_agent(self):
        if self._agent is None:
            from agentic_core.L5_safety.reasoning.GravityLeakHealerAgent import GravityLeakHealerAgent

            self._agent = GravityLeakHealerAgent(project_root=self.project_root)
        return self._agent

    def can_handle(self, territory: str) -> bool:
        """GravityHealer handles all territories for layer violations."""
        return True

    def scan_territory(self, territory: str) -> ScanResult:
        """Scan for gravity violations (layer inversions, import violations)."""
        from agentic_core.L5_safety.reasoning.gravity_validator import GravityValidatorAgent

        territory = _normalize_territory_name(territory)
        # Use GravityValidatorAgent for scanning
        validator = GravityValidatorAgent(project_root=self.project_root)
        scan_result = validator.to_check_dict()

        violations = []

        for v in tqdm(_as_list(scan_result.get("violations")), desc="Processing", unit="item"):
            file_path = v.get("file", "")
            if not _path_in_territory(self.project_root, territory, file_path):
                continue
            violations.append(
                Violation(
                    type="GRAVITY_VIOLATION",
                    path=v.get("file", ""),
                    message=v.get("message", "Layer inversion detected"),
                    severity="ERROR",
                    details=v,
                )
            )

        return ScanResult(
            territory=territory,
            violations_found=len(violations),
            violations=violations,
            scan_metadata=scan_result,
        )

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        """Heal gravity violations in territory."""
        agent = self._get_agent()

        scan_result = self.scan_territory(territory)
        actions_taken = []
        errors = []
        violations_fixed = 0

        if context.heal and scan_result.violations_found > 0:
            try:
                # Use heal_violations
                heal_result = agent.heal_violations(dry_run=not context.heal)

                if isinstance(heal_result, dict):
                    violations_fixed = heal_result.get("fixed", 0)
                    actions_taken = heal_result.get("actions", [])

            except Exception as e:
                logger.exception(f"Gravity healing failed: {e}")
                errors.append(str(e))

        return HealingResult(
            territory=territory,
            agent_name=self.agent_name,
            violations_found=scan_result.violations_found,
            violations_fixed=violations_fixed,
            actions_taken=actions_taken,
            errors=errors,
            success=len(errors) == 0,
            dry_run=not context.heal,
        )


class FilesystemReconcilerAdapter(TerritoryHealerProtocol):
    """Adapter for FilesystemSSOTReconcilerAgent."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self._agent = None

    @property
    def agent_name(self) -> str:
        return "FilesystemSSOTReconcilerAgent"

    def _get_agent(self):
        if self._agent is None:
            from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                FilesystemSSOTReconcilerAgent,
            )

            self._agent = FilesystemSSOTReconcilerAgent(project_root=self.project_root)
        return self._agent

    def can_handle(self, territory: str) -> bool:
        return True

    def scan_territory(self, territory: str) -> ScanResult:
        """Scan for filesystem SSOT violations."""
        from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import FilesystemSSOTValidatorAgent

        territory = _normalize_territory_name(territory)
        # Use validator for scanning
        validator = FilesystemSSOTValidatorAgent(project_root=self.project_root)
        scan_result = validator.to_check_dict()

        violations = []

        for v in tqdm(_as_list(scan_result.get("violations")), desc="Processing", unit="item"):
            file_path = v.get("path", "")
            if not _path_in_territory(self.project_root, territory, file_path):
                continue
            violations.append(
                Violation(
                    type="FILESYSTEM_DRIFT",
                    path=v.get("path", ""),
                    message=v.get("message", "SSOT drift detected"),
                    severity="WARNING",
                    details=v,
                )
            )

        return ScanResult(
            territory=territory,
            violations_found=len(violations),
            violations=violations,
            scan_metadata=scan_result,
        )

    def heal_territory(self, territory: str, context: HealingContext) -> HealingResult:
        """Heal filesystem drift in territory."""
        agent = self._get_agent()

        scan_result = self.scan_territory(territory)
        actions_taken = []
        errors = []

        if context.heal and scan_result.violations_found > 0:
            try:
                heal_result = agent.heal_repository(dry_run=not context.heal, execute=context.heal)

                if isinstance(heal_result, dict):
                    actions_taken = heal_result.get("actions", [])
                    errors = heal_result.get("errors", [])

            except Exception as e:
                logger.exception(f"Filesystem healing failed: {e}")
                errors.append(str(e))

        return HealingResult(
            territory=territory,
            agent_name=self.agent_name,
            violations_found=scan_result.violations_found,
            violations_fixed=len(actions_taken),
            actions_taken=actions_taken,
            errors=errors,
            success=len(errors) == 0,
            dry_run=not context.heal,
        )


def create_adapter_coordinator(project_root: Path | None = None) -> "TerritoryHealingCoordinator":
    """Create coordinator with all adapters registered."""
    from agentic_core.L3_orchestration.reasoning.territory_healing.territory_healing_coordinator import (
        TerritoryHealingCoordinator,
    )

    root = (project_root or Path.cwd()).resolve()
    coordinator = TerritoryHealingCoordinator(root)

    # Register all adapters
    coordinator.register_agent(HierarchyHealerAdapter(root))
    coordinator.register_agent(LocationHealerAdapter(root))
    coordinator.register_agent(GravityHealerAdapter(root))
    coordinator.register_agent(FilesystemReconcilerAdapter(root))

    logger.info(f"Created adapter coordinator with {len(coordinator.agents)} agents")
    return coordinator
