"""LicReflectionAgent — LIC domain reflection agent.

Originally from: LeadQualityAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-A) — now subclasses BaseReflectionAgent.
"""

from dataclasses import dataclass

from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


# STUB: OutreachAgent base class (deprecated)
# RETIRED: OutreachAgent removed from active agent pool (2026-02-08)


@dataclass
class LicReflectionAgent(BaseReflectionAgent):
    """Reflects on LIC campaign execution and suggests improvements.

    Inherits execute() and heal() from BaseReflectionAgent.
    Domain-specific post-reflection logic may be added via _post_reflect().
    """
