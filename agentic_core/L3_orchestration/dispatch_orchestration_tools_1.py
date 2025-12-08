# Ownership: agentic_core / L3_orchestration
# -*- coding: utf-8 -*-
"""Dispatch orchestration tools - atomic wrapper."""

from __future__ import annotations

from typing import Any, Dict, List

from shared.workflow_types import HopStatus, GateDecision


def dispatch_orchestration_tools(request: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch orchestration tools based on request."""
    return {"status": "dispatched", "request": request}


def get_available_tools() -> List[str]:
    """Get list of available orchestration tools."""
    return ["plan", "execute", "validate", "render"]
