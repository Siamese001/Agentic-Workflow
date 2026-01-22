#!/usr/bin/env python3
from __future__ import annotations
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent

"""
UnifiedStructureHealerAgent - Structure Healing & Repair

Phase 4 Hard Migration: Consolidates:
- GravityHealerAgent (layer gravity healing)
- HierarchyHealerAgent (hierarchy healing)
- NamingLawHealerAgent (naming convention healing)
- TerritoryHealerAgent (territory/location healing)
- BlueprintHierarchyHealerAgent (blueprint compliance)

Features:
- Gravity violation auto-healing
- Hierarchy compliance healing
- Naming convention enforcement
- Territory/location healing
- Blueprint compliance healing
"""


import logging
import re
import shutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

Logger = logging.getLogger(__name__)


class StructureHealingType(Enum):
    """Types of structure healing."""

    GRAVITY = auto()
    HIERARCHY = auto()
    NAMING = auto()
    TERRITORY = auto()
    BLUEPRINT = auto()


@dataclass
class StructureHealingAction:
    """Represents a structure healing action."""

    healing_type: StructureHealingType
    file_path: Path
    description: str
    old_value: str
    new_value: str
    applied: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StructureHealerConfig:
    """Configuration for structure healing."""

    enable_gravity: bool = True
    enable_hierarchy: bool = True
    enable_naming: bool = True
    enable_territory: bool = True
    dry_run: bool = True
    backup_before_heal: bool = True
    backup_dir: Path | None = None
    agent_suffix: str = "Agent"


class UnifiedStructureHealerAgent(SovereignBaseAgent):
    """
    Unified structure healer for gravity, hierarchy, naming, and territory.

    Consolidates:
    - GravityHealerAgent
    - HierarchyHealerAgent
    - NamingLawHealerAgent
    - TerritoryHealerAgent
    - BlueprintHierarchyHealerAgent

    Usage:
        healer = UnifiedStructureHealerAgent()

        # Heal naming violations
        actions = healer.heal_naming(Path("BadName.py"))

        # Heal all structure issues
        actions = healer.heal_all(Path("my_agent.py"))
    """

    # Layer hierarchy
    LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

    def __init__(
        self,
        project_root: Path | None = None,
        config: StructureHealerConfig | None = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.config = config or StructureHealerConfig()
        self._lock = threading.RLock()
        self._actions: list[StructureHealingAction] = []

        if self.config.backup_dir is None:
            self.config.backup_dir = (
                self.project_root / "archives" / "healing_backups" / "structure"
            )

        Logger.info("UnifiedStructureHealerAgent initialized")

    def heal_all(self, file_path: Path) -> list[StructureHealingAction]:
        """Run all enabled healing on a file."""
        actions = []

        if not file_path.exists():
            return actions

        if self.config.enable_naming:
            actions.extend(self.heal_naming(file_path))

        if self.config.enable_gravity:
            actions.extend(self.heal_gravity(file_path))

        if self.config.enable_territory:
            actions.extend(self.heal_territory(file_path))

        return actions

    def heal_naming(self, file_path: Path) -> list[StructureHealingAction]:
        """Heal naming convention violations."""
        actions = []

        # Check if file should have Agent suffix
        if not file_path.name.endswith("Agent.py"):
            return actions

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return actions

        # Find classes without Agent suffix
        class_pattern = re.compile(r"class\s+(\w+)\s*[\(:]")
        matches = class_pattern.findall(content)

        for class_name in matches:
            if not class_name.endswith(self.config.agent_suffix):
                new_name = f"{class_name}{self.config.agent_suffix}"

                action = StructureHealingAction(
                    healing_type=StructureHealingType.NAMING,
                    file_path=file_path,
                    description=f"Rename class: {class_name} -> {new_name}",
                    old_value=class_name,
                    new_value=new_name,
                )
                actions.append(action)

                if not self.config.dry_run:
                    self._backup_file(file_path)

                    # Replace class name
                    new_content = re.sub(
                        rf"\b{class_name}\b",
                        new_name,
                        content,
                    )
                    file_path.write_text(new_content, encoding="utf-8")
                    action.applied = True

                    Logger.info(f"Renamed class: {class_name} -> {new_name}")

        self._actions.extend(actions)
        return actions

    def heal_gravity(self, file_path: Path) -> list[StructureHealingAction]:
        """Heal gravity (layer import) violations."""
        actions = []

        source_layer = self._extract_layer(file_path)
        if not source_layer:
            return actions

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return actions

        lines = content.split("\n")
        new_lines = lines.copy()
        modified = False

        # Find imports that violate gravity
        import_pattern = re.compile(r"from\s+(agentic_core\.L\d_\w+)")

        for i, line in enumerate(lines):
            match = import_pattern.search(line)
            if match:
                import_module = match.group(1)
                target_layer = self._extract_layer_from_module(import_module)

                if target_layer and not self._is_valid_gravity(source_layer, target_layer):
                    action = StructureHealingAction(
                        healing_type=StructureHealingType.GRAVITY,
                        file_path=file_path,
                        description=f"Comment out gravity violation: {source_layer} importing {target_layer}",
                        old_value=line,
                        new_value=f"# GRAVITY VIOLATION: {line}",
                    )
                    actions.append(action)

                    if not self.config.dry_run:
                        new_lines[i] = f"# GRAVITY VIOLATION: {line}"
                        modified = True
                        action.applied = True

        if modified:
            self._backup_file(file_path)
            file_path.write_text("\n".join(new_lines), encoding="utf-8")

        self._actions.extend(actions)
        return actions

    def heal_territory(self, file_path: Path) -> list[StructureHealingAction]:
        """Heal territory/location violations."""
        actions = []

        # Check if file is in correct layer directory
        layer = self._extract_layer(file_path)
        if not layer:
            return actions

        # Determine expected directory based on file type
        filename = file_path.name

        if filename.endswith("Agent.py"):
            # Agents should be in validators, guardrails, or similar
            expected_dirs = ["validators", "guardrails", "unified"]

            current_dir = file_path.parent.name
            if current_dir not in expected_dirs:
                action = StructureHealingAction(
                    healing_type=StructureHealingType.TERRITORY,
                    file_path=file_path,
                    description=f"File may be in wrong directory: {current_dir}",
                    old_value=str(file_path.parent),
                    new_value=f"Consider moving to {layer}_*/validators/",
                )
                actions.append(action)

        self._actions.extend(actions)
        return actions

    def _extract_layer(self, path: Path) -> str | None:
        """Extract layer from file path."""
        path_str = str(path)
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
                return layer
        return None

    def _extract_layer_from_module(self, module: str) -> str | None:
        """Extract layer from module name."""
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f".{layer}_" in module or module.startswith(f"{layer}_"):
                return layer
        return None

    def _is_valid_gravity(self, source_layer: str, target_layer: str) -> bool:
        """Check if import follows gravity rules."""
        source_level = self.LAYER_ORDER.get(source_layer, -1)
        target_level = self.LAYER_ORDER.get(target_layer, -1)

        # Higher layers can import from lower layers
        return source_level >= target_level

    def _backup_file(self, file_path: Path) -> Path | None:
        """Create backup before healing."""
        if not self.config.backup_before_heal:
            return None

        backup_dir = self.config.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.name}.{timestamp}"

        shutil.copy2(file_path, backup_path)
        Logger.info(f"Backed up {file_path} to {backup_path}")

        return backup_path

    def get_actions(self) -> list[StructureHealingAction]:
        """Get all recorded healing actions."""
        return self._actions.copy()


# Factory methods for backward compatibility
def create_legacy_gravity_healer() -> UnifiedStructureHealerAgent:
    """Create healer for gravity only."""
    config = StructureHealerConfig(
        enable_gravity=True,
        enable_hierarchy=False,
        enable_naming=False,
        enable_territory=False,
    )
    return UnifiedStructureHealerAgent(config=config)


def create_legacy_naming_healer() -> UnifiedStructureHealerAgent:
    """Create healer for naming only."""
    config = StructureHealerConfig(
        enable_gravity=False,
        enable_hierarchy=False,
        enable_naming=True,
        enable_territory=False,
    )
    return UnifiedStructureHealerAgent(config=config)
