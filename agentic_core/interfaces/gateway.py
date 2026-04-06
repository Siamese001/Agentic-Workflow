"""
agentic_core/interfaces/gateway.py

Sovereign LLM Gateway interface for apps_* consumption.

Re-exports SovereignLLMGateway and GenerationRequest so apps_* tools that
legitimately need to call the gateway (e.g. GeminiLLMClient) can import
from the approved interface boundary rather than directly from L2.

# Configuration constants

AUTHORITY CONSTRAINTS:
- Gateway is the sole outbound LLM seam — all calls must pass through it
- No model resolution outside the gateway
- No embedding instantiation
- No tier selection bypass

USAGE (apps_*):
    from agentic_core.interfaces.gateway import (
        SovereignLLMGateway,
        GenerationRequest,
    )
"""

from __future__ import annotations

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
from agentic_core.L2_execution.types.gateway_types import GenerationRequest

__all__ = [
    "SovereignLLMGateway",
    "GenerationRequest",
]
