"""Toolsmith Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L2_execution.utils.toolsmith_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L2_execution.reasoning.ToolsmithAgent import` and `import agentic_core.L2_execution.reasoning.ToolsmithAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L2_execution.utils.toolsmith_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L2_execution__reasoning__ToolsmithAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_ToolsmithAgent.json
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.utils.toolsmith_util import (
    GeneratedTool as _GeneratedTool,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    ToolSpec as _ToolSpec,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    create_tool_spec as _create_tool_spec,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    generate_tool_from_template as _generate_tool_from_template,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    get_tool_categories as _get_tool_categories,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    get_tool_template as _get_tool_template,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    list_builtin_templates as _list_builtin_templates,
)
from agentic_core.L2_execution.utils.toolsmith_util import (
    validate_tool_code as _validate_tool_code,
)


class ToolSpec:
    """DEPRECATED: Use agentic_core.L2_execution.utils.toolsmith_util.ToolSpec instead."""

    def __init__(self, **kwargs):
        warnings.warn("ToolSpec is deprecated. Use toolsmith_util.ToolSpec instead.", DeprecationWarning)
        self._impl = _ToolSpec(**kwargs)


class GeneratedTool:
    """DEPRECATED: Use agentic_core.L2_execution.utils.toolsmith_util.GeneratedTool instead."""

    def __init__(self, **kwargs):
        warnings.warn(
            "GeneratedTool is deprecated. Use toolsmith_util.GeneratedTool instead.", DeprecationWarning
        )
        self._impl = _GeneratedTool(**kwargs)


class ToolsmithAgent(SovereignBaseAgent):
    """
    DEPRECATED: Toolsmith Agent - now delegates to toolsmith_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L2_execution.utils.toolsmith_util directly.
    """

    def __init__(self):
        """Initialize ToolsmithAgent (deprecated, use toolsmith_util instead)."""
        super().__init__(name="ToolsmithAgent", layer="L2")

        warnings.warn(
            "ToolsmithAgent is deprecated. Use agentic_core.L2_execution.utils.toolsmith_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.tools: dict[str, Any] = {}
        self.templates: dict[str, str] = {}
        self.categories = _get_tool_categories()

    def get_tool_template(self, template_name: str) -> str | None:
        """Get a built-in tool template."""
        return _get_tool_template(template_name)

    def list_builtin_templates(self) -> dict[str, str]:
        """List all available built-in templates."""
        return _list_builtin_templates()

    def generate_tool_from_template(
        self,
        template_name: str,
        category: str = "general",
        custom_params: dict[str, Any] | None = None,
    ) -> Any | None:
        """Generate a tool from a template."""
        return _generate_tool_from_template(template_name, category, custom_params)

    def validate_tool_code(self, code: str) -> dict[str, Any]:
        """Validate generated tool code."""
        return _validate_tool_code(code)

    def get_tool_categories(self) -> dict[str, str]:
        """Get available tool categories."""
        return _get_tool_categories()

    def create_tool_spec(
        self,
        name: str,
        description: str,
        parameters: dict[str, dict],
        category: str = "general",
    ) -> Any:
        """Create a tool specification."""
        return _create_tool_spec(name, description, parameters, category)
