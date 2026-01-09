"""
L3 Workflow Engines Registry

Canonical exports for L3 orchestration layer.

Note: IOrchestratorAgent relocated to ../interfaces/ (2026-01-07)
      for proper ABC architectural placement.
"""

try:
    from ..interfaces.IOrchestratorAgent import IOrchestratorAgent
except ImportError:
    IOrchestratorAgent = None

try:
    from .McpConnectionManagerAgent import McpConnectionManagerAgent
except ImportError:
    McpConnectionManagerAgent = None

__all__ = [
    "IOrchestratorAgent",
    "McpConnectionManagerAgent",
]
