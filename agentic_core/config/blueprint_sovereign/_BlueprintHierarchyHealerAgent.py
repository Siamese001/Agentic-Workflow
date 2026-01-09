from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

import shutil
from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

from agentic_core.L5_safety.guardrails.hierarchy_healer import HierarchyHealerAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

# NOT_AN_AGENT — utility healer class, not a true agent — excluded from agent discovery
class _BlueprintHierarchyHealerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    [L3 AGENT] The Structural Surgeon.
    Directive: Physically relocate files to satisfy Depth-4 Canon.
    """
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.blueprint = CORE_SUBFOLDER_MAP #

    async def execute(self, file_path: str):
                    
        path_obj = Path(file_path)
        # Identify L1 (e.g., L5_safety) from path
        parts = path_obj.parts
        if "agentic_core" in parts:
            l1_idx = parts.index("agentic_core") + 1
            l1_layer = parts[l1_idx]
            
            # Check if file is "floating" at L1 (Depth 3)
            if len(parts) == l1_idx + 2 and l1_layer in self.blueprint:
                target_l2 = self.blueprint[l1_layer][0] # Default to P1 layer
                target_dir = Path(self.ctx.project_root) / "agentic_core" / l1_layer / target_l2
                
                target_dir.mkdir(parents=True, exist_ok=True)
                (target_dir / "__init__.py").touch() # Ensure importability
                
                new_path = target_dir / path_obj.name
                shutil.move(str(path_obj), str(new_path)) #
                
                return {"healed": True, "move_to": str(new_path), "reason": "Depth-4 Alignment"}
        return {"healed": False}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
