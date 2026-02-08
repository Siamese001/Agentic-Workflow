"""
Territories Module — backward-compatible re-export from _constants.

All territory definitions, types, and build machinery now live in _constants.py
(the leaf node). This module re-exports them for backward compatibility.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    LAYER_OVERRIDES,
    SOVEREIGN_TERRITORIES,
    SubfolderDefinition,
    TerritoryDefinition,
    build_sovereign_territories,
)
