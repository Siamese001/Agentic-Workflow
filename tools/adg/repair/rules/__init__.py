"""Repair rules for ADG Repair Orchestrator.

Importing this package must eagerly import every built-in rule module so
all @repair_rule decorators run before RuleEngine snapshots the registry.
"""

from .fix_docstring_placeholder import FixDocstringPlaceholderRule
from .fix_guardian_format import FixGuardianFormatRule
from .fix_import_order import FixImportOrderRule
from .fix_layer_assignment import FixLayerAssignmentRule
from .fix_missing_all import FixMissingAllRule
from .fix_missing_typing import FixMissingTypingRule
from .fix_p1_layer_violation import FixP1LayerViolationRule
from .fix_p2_antipatterns import FixP2AntipatternsRule
from .fix_unused_imports import FixUnusedImportsRule

__all__ = [
    "FixDocstringPlaceholderRule",
    "FixGuardianFormatRule",
    "FixImportOrderRule",
    "FixLayerAssignmentRule",
    "FixMissingAllRule",
    "FixMissingTypingRule",
    "FixP1LayerViolationRule",
    "FixP2AntipatternsRule",
    "FixUnusedImportsRule",
]
