"""ProactiveAgent — RG domain proactive task agent.

Originally from: CapabilityMonitorAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-B) — now subclasses BaseProactiveAgent.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from apps_shared.reasoning.BaseProactiveAgent import BaseProactiveAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class ProactiveAgent(BaseProactiveAgent):
    """Agent that proactively identifies and executes RG resume tasks.

    Inherits execute() skeleton from BaseProactiveAgent.
    scheduler/handoff/monitor must be injected externally before execute().
    """

    def __post_init__(self) -> None:
        """Initialize proactive agent."""
        super().__post_init__()
        self.name = 'ProactiveAgent'
