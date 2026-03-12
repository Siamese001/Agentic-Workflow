"""
Governance Module — backward-compatible re-export from _constants.

All governance configuration now lives in _constants.py (the leaf node).
This module re-exports them for backward compatibility.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
)
