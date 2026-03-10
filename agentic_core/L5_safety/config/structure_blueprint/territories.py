"""
Territories Module — backward-compatible re-export from _constants.

All territory definitions, types, and build machinery now live in _constants.py
(the leaf node). This module re-exports them for backward compatibility.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    LAYER_OVERRIDES,
    SOVEREIGN_TERRITORIES,
    SubfolderDefinition,
    TerritoryDefinition,
    build_sovereign_territories,
)
