"""
agentic_core/interfaces/execution_contracts.py

Sovereign execution contracts interface for apps_* consumption.

Re-exports key_source, AgentOutputContract, and wrap_output so apps_*
engines can import from the approved interface boundary.

AUTHORITY CONSTRAINTS:
- key_source: read-only secret access through approved seam
- AgentOutputContract / wrap_output: output wrapping types only

USAGE (apps_*):
    from agentic_core.interfaces.execution_contracts import (
        get_current_secret,
        AgentOutputContract,
        wrap_output,
    )
"""

from __future__ import annotations

try:
    from agentic_core.L2_execution.enforcement.key_source import get_current_secret
    from agentic_core.L2_execution.types.agent_output_contract import (
        AgentOutputContract,
        wrap_output,
    )

    _AVAILABLE = True
except ImportError:
    get_current_secret = None  # type: ignore[assignment]
    AgentOutputContract = None  # type: ignore[assignment]
    wrap_output = None  # type: ignore[assignment]
    _AVAILABLE = False

__all__ = [
    "get_current_secret",
    "AgentOutputContract",
    "wrap_output",
]
