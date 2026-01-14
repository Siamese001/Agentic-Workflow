"""
L1Agent - Consolidated Base for L1 Cognition Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP via SovereignBaseAgent (root injection)
- L1SubatomicTestingMixin: Thought validation testing

L1 agents handle cognition - thinking, reasoning, understanding.

MRO HARDENING:
- Inheritance order: Specialized Mixins -> SovereignBaseAgent (includes MCP)
- MCPHardenedMixin is now in SovereignBaseAgent - DO NOT add it here
- MRO: HealerMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


@dataclass
class L1Agent(HealerMixin, SovereignBaseAgent):
    """
    Consolidated base for L1 Cognition agents.
    
    MRO HARDENING:
    - HealerMixin: First (specialized layer capability)
    - SovereignBaseAgent: Last (root - includes MCPHardenedMixin)
    
    MRO: HealerMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations via SovereignBaseAgent
    
    L1 Table Decision:
    - Basic Self-Testing: YES (thought validation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L1Agent"
    layer: str = "L1"
    
    def __post_init__(self):
        """Cooperative MRO initialization."""
        super().__post_init__()
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        if _call_path is None:
            _call_path = set()
        result = super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        return result
    
    def _run_self_tests(self) -> Dict[str, Any]:
        """Override in subclass to implement self-tests."""
        return {"status": "not_implemented", "tests": 0}
