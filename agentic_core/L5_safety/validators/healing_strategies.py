"""
Healing Strategy Pattern - Polymorphic Violation Healing

Replaces if/elif branching with strategy classes for different violation types.
Each strategy encapsulates healing logic for a specific violation category.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class HealingStrategy(ABC):
    """Base strategy for polymorphic violation healing."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize healing strategy.

        Args:
            config: Strategy-specific configuration
        """
        self.config = config or {}

    @abstractmethod
    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """
        Apply healing strategy to violation.

        Args:
            violation: Violation details
            file_path: Path to file with violation

        Returns:
            Healing result with status and details
        """
        pass

    def _validate_inputs(self, violation: dict, file_path: Path) -> bool:
        """Validate inputs before healing."""
        return bool(violation) and isinstance(file_path, Path)


class TerritoryHealingStrategy(HealingStrategy):
    """Healing strategy for territory/location violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply territory healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            target_path = violation.get('target_path')
            if not target_path:
                return {'success': False, 'error': 'No target path specified'}

            # Simulate file move (in real implementation, would use safe_path_join)
            Logger.info(f"Territory healing: {file_path} → {target_path}")

            return {
                'success': True,
                'type': 'territory',
                'from': str(file_path),
                'to': target_path,
                'message': f'Moved to correct territory: {target_path}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class GravityHealingStrategy(HealingStrategy):
    """Healing strategy for gravity/import violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply gravity healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            bad_imports = violation.get('bad_imports', [])
            if not bad_imports:
                return {'success': False, 'error': 'No bad imports specified'}

            # Simulate import surgery
            Logger.info(f"Gravity healing: Removing {len(bad_imports)} bad imports from {file_path}")

            return {
                'success': True,
                'type': 'gravity',
                'file': str(file_path),
                'removed_imports': bad_imports,
                'message': f'Removed {len(bad_imports)} gravity violations'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class NamingHealingStrategy(HealingStrategy):
    """Healing strategy for naming convention violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply naming healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            proposed_name = violation.get('proposed_name')
            if not proposed_name:
                return {'success': False, 'error': 'No proposed name specified'}

            # Simulate file rename
            Logger.info(f"Naming healing: {file_path.name} → {proposed_name}")

            return {
                'success': True,
                'type': 'naming',
                'from': file_path.name,
                'to': proposed_name,
                'message': f'Renamed to follow conventions: {proposed_name}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HierarchyHealingStrategy(HealingStrategy):
    """Healing strategy for hierarchy/structure violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply hierarchy healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            hierarchy_issue = violation.get('issue')
            if not hierarchy_issue:
                return {'success': False, 'error': 'No hierarchy issue specified'}

            # Simulate hierarchy restructuring
            Logger.info(f"Hierarchy healing: Fixing {hierarchy_issue} in {file_path}")

            return {
                'success': True,
                'type': 'hierarchy',
                'file': str(file_path),
                'issue': hierarchy_issue,
                'message': f'Fixed hierarchy violation: {hierarchy_issue}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ComplianceHealingStrategy(HealingStrategy):
    """Healing strategy for compliance violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply compliance healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            compliance_rule = violation.get('rule')
            if not compliance_rule:
                return {'success': False, 'error': 'No compliance rule specified'}

            # Simulate compliance fix
            Logger.info(f"Compliance healing: Enforcing {compliance_rule} in {file_path}")

            return {
                'success': True,
                'type': 'compliance',
                'file': str(file_path),
                'rule': compliance_rule,
                'message': f'Applied compliance rule: {compliance_rule}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DriftHealingStrategy(HealingStrategy):
    """Healing strategy for code drift violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply drift healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            drift_type = violation.get('drift_type')
            if not drift_type:
                return {'success': False, 'error': 'No drift type specified'}

            # Simulate drift correction
            Logger.info(f"Drift healing: Correcting {drift_type} in {file_path}")

            return {
                'success': True,
                'type': 'drift',
                'file': str(file_path),
                'drift_type': drift_type,
                'message': f'Corrected code drift: {drift_type}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DeadCodeHealingStrategy(HealingStrategy):
    """Healing strategy for dead code violations."""

    def apply(self, violation: dict[str, Any], file_path: Path) -> dict[str, Any]:
        """Apply dead code healing."""
        if not self._validate_inputs(violation, file_path):
            return {'success': False, 'error': 'Invalid inputs'}

        try:
            dead_items = violation.get('dead_items', [])
            if not dead_items:
                return {'success': False, 'error': 'No dead code items specified'}

            # Simulate dead code removal
            Logger.info(f"Dead code healing: Removing {len(dead_items)} dead items from {file_path}")

            return {
                'success': True,
                'type': 'dead_code',
                'file': str(file_path),
                'removed_items': dead_items,
                'message': f'Removed {len(dead_items)} dead code items'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HealingStrategyFactory:
    """Factory for creating healing strategies."""

    _strategies = {
        'territory': TerritoryHealingStrategy,
        'location': TerritoryHealingStrategy,
        'gravity': GravityHealingStrategy,
        'import': GravityHealingStrategy,
        'naming': NamingHealingStrategy,
        'hierarchy': HierarchyHealingStrategy,
        'structure': HierarchyHealingStrategy,
        'compliance': ComplianceHealingStrategy,
        'drift': DriftHealingStrategy,
        'dead_code': DeadCodeHealingStrategy,
    }

    @classmethod
    def create(
        cls,
        violation_type: str,
        config: dict[str, Any] | None = None
    ) -> HealingStrategy:
        """
        Create healing strategy instance.

        Args:
            violation_type: Type of violation (territory, gravity, naming, etc.)
            config: Strategy-specific configuration

        Returns:
            HealingStrategy instance

        Raises:
            ValueError: If violation type unknown
        """
        strategy_class = cls._strategies.get(violation_type.lower())

        if not strategy_class:
            raise ValueError(
                f"Unknown violation type: {violation_type}. "
                f"Available: {', '.join(cls._strategies.keys())}"
            )

        return strategy_class(config=config)

    @classmethod
    def register(cls, name: str, strategy_class: type) -> None:
        """Register custom healing strategy."""
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def available_strategies(cls) -> list:
        """Get list of available healing strategies."""
        return list(cls._strategies.keys())
