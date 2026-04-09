"""C7 G3: CHOOSE THE LANE - Route to execution path.

10C-REQ-157: Route to local tool external model memory network Universal Write Gate
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .access_classifier import AccessType


class Lane(Enum):
    """Execution lanes."""
    LOCAL_TOOL = auto()
    EXTERNAL_MODEL = auto()
    MEMORY_STORE = auto()
    NETWORK_API = auto()
    UNIVERSAL_WRITE_GATE = auto()
    FALLBACK = auto()


@dataclass
class LaneSelection:
    """Result of lane selection."""
    lane: Lane
    target: str
    requires_sandbox: bool
    requires_audit: bool
    priority: int  # Lower is higher priority


class LaneRouter:
    """C7 G3: Lane router.
    
    10C-REQ-157: Route to local tool external model memory network UWG.
    """
    
    def __init__(self) -> None:
        self._lane_map: dict[AccessType, Lane] = {
            AccessType.READ: Lane.LOCAL_TOOL,
            AccessType.TOOL: Lane.LOCAL_TOOL,
            AccessType.MODEL: Lane.EXTERNAL_MODEL,
            AccessType.NETWORK: Lane.NETWORK_API,
            AccessType.MEMORY: Lane.MEMORY_STORE,
            AccessType.WRITE: Lane.UNIVERSAL_WRITE_GATE,
        }
        
        self._targets: dict[Lane, list[str]] = {
            Lane.LOCAL_TOOL: ["local_executor", "tool_runner"],
            Lane.EXTERNAL_MODEL: ["claude", "gpt", "gemini"],
            Lane.MEMORY_STORE: ["vector_store", "cache_layer"],
            Lane.NETWORK_API: ["http_client", "api_gateway"],
            Lane.UNIVERSAL_WRITE_GATE: ["uwg_clerk"],
        }
    
    def route(self, access_type: AccessType, preference: str = "") -> LaneSelection:
        """Select lane for access type."""
        lane = self._lane_map.get(access_type, Lane.FALLBACK)
        
        # Select target
        targets = self._targets.get(lane, ["default"])
        
        # Use preference if valid
        if preference and preference in targets:
            target = preference
        else:
            target = targets[0]  # Default to first
        
        # Determine requirements
        requires_sandbox = lane in (Lane.EXTERNAL_MODEL, Lane.NETWORK_API)
        requires_audit = lane in (Lane.NETWORK_API, Lane.UNIVERSAL_WRITE_GATE)
        priority = self._get_priority(lane)
        
        return LaneSelection(
            lane=lane,
            target=target,
            requires_sandbox=requires_sandbox,
            requires_audit=requires_audit,
            priority=priority,
        )
    
    def _get_priority(self, lane: Lane) -> int:
        """Get priority for lane (lower = higher priority)."""
        priorities = {
            Lane.LOCAL_TOOL: 1,
            Lane.MEMORY_STORE: 2,
            Lane.EXTERNAL_MODEL: 3,
            Lane.NETWORK_API: 4,
            Lane.UNIVERSAL_WRITE_GATE: 5,
            Lane.FALLBACK: 10,
        }
        return priorities.get(lane, 10)
    
    def register_lane_mapping(self, access_type: AccessType, lane: Lane) -> None:
        """Register lane mapping for access type."""
        self._lane_map[access_type] = lane
    
    def register_target(self, lane: Lane, target: str) -> None:
        """Register target for lane."""
        if lane not in self._targets:
            self._targets[lane] = []
        self._targets[lane].append(target)
