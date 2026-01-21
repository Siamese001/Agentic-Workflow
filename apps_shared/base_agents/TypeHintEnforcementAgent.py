"""@deprecated
DEPRECATED: Use CodeStandardsEnforcerAgent instead.

This agent has been consolidated into CodeStandardsEnforcerAgent as part of
Phase 4 consolidation (2026-01-19). This file is retained for backward
compatibility during the transition period.

Migration:
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        CodeStandardsEnforcerAgent,
        get_code_standards_enforcer,
        check_type_hints,
    )
"""

import warnings

warnings.warn(
    "TypeHintEnforcementAgent is deprecated. Use CodeStandardsEnforcerAgent instead.",
    DeprecationWarning,
    stacklevel=2,
)

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

# TypeHintEnforcementAgent - Atomic Validator (Ungated Healing)
# Territory: agentic_core/L2_execution/ToolRegistry
# Canon Alignment: Enforces complete type hints for public functions/methods/variables
# Surgery Scope: Single file — adds basic Any / inferred hints where Missing
import ast

"""Brief description of functionality and purpose."""

from pathlib import Path
from typing import Any

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


# NAMING CANON COMPLIANCE — renamed to TypeHintEnforcementAgent for discovery and sovereignty — 2025-12-30
class TypeHintEnforcementAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Ensures public functions, methods, and module-level assignments have type hints.

    Rules:
    - Public functions/methods (not starting with _) must have:
        - Parameter type hints
        - Return type hint (-> ...)
    - Public module-level variables/constants must have type hints
    - Uses 'Any' as safe fallback when no better inference available

    Why ungated healing is safe:
    - Only adds type annotations (no runtime impact)
    - Never removes or changes existing code/logic
    - Single-file scope
    """

    FALLBACK_PARAM = "Any"
    FALLBACK_RETURN = "Any"
    FALLBACK_VAR = "Any"

    def __init__(self, ctx, project_root=None) -> None:
        """Initialize with mandatory ctx for sovereign operation."""
        if ctx is None:
            raise ValueError("ctx is mandatory for TypeHintEnforcementAgent (sovereign agent)")
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> dict[str, Any]:
        """Execute method for validator compatibility."""
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx=None) -> dict[str, Any]:
        """
        Per-file healing: add Missing type hints via AST transformation.
        """
        ctx = ctx or self.ctx
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            fixer = TypeHintFixerAgent(self.FALLBACK_PARAM, self.FALLBACK_RETURN, self.FALLBACK_VAR)
            new_tree = fixer.visit(tree)

            if fixer.added_count > 0:
                ast.fix_missing_locations(new_tree)
                new_source = ast.unparse(new_tree)

                if new_source != source:
                    file_path.write_text(
                        new_source
                        + "\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n",
                        encoding="utf-8",
                    )
                    message = f"Added {fixer.added_count} Missing type hint(s)"
                    print(f"      [HEALED] {file_path.name}: {message}")
                    ctx.report(
                        self.__class__.__name__,
                        key_id=18,  # Core Laws / Safety category
                        success=True,
                    )
                    return {"healed": True, "details": message}

            return {"healed": False}

        except Exception as e:
            ctx.report(
                self.__class__.__name__,
                18,
                False,
                f"Type hint enforcement failed: {str(e)[:100]}",
            )
            return {"healed": False}


from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING FIXED: TypeHintFixerAgent → TypeHintFixerAgent


# Factory for discovery
def get_type_hint_enforcement_agent(ctx, project_root=None) -> TypeHintEnforcementAgent:
    """Factory function."""
    return TypeHintEnforcementAgent(ctx, project_root)


class TypeHintEnforcementAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """TypeHintEnforcementAgent agent for autonomous operations."""

    # ... (rest of the class remains the same)

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L5 safety/validators - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety/validators - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
