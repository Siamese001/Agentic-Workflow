"""LicReflectionAgent — LIC domain reflection agent.

Originally from: LeadQualityAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-A) — now subclasses BaseReflectionAgent.
"""
from dataclasses import dataclass
from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class LicReflectionAgent(BaseReflectionAgent):
    """Reflects on LIC campaign execution and suggests improvements.

    Inherits execute() and heal() from BaseReflectionAgent.
    Domain-specific post-reflection logic may be added via _post_reflect().
    """
