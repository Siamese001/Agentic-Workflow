"""
LocationAgent.py — Backward-compatibility re-export shim.

Created during LCD+ decommission (Phase 0.3 Step 4).
Routes imports to the canonical core/ module.

Usage (unchanged):
    from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
"""

from agentic_core.L5_safety.validators.core.LocationAgent import (  # noqa: F401
    LocationAgent,
    get_location_agent,
    is_path_compliant,
)
