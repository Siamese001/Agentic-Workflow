"""ADG extraction package -- static AST-based scanner and registry scanner."""

from agentic_core.adg.extraction.agent_registry_scanner import (
    AgentRegistryEdge,
    AgentRegistryResult,
    scan_agent_registry,
)
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner, Edge, ScanResult

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = [
    "ADGStaticScanner",
    "Edge",
    "ScanResult",
    "AgentRegistryEdge",
    "AgentRegistryResult",
    "scan_agent_registry",
]
