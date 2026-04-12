"""Synthetic fixture: agent whose execute() is pure super-delegation.

Pre-hardening: is_stub_body returns False (not pass/…/raise/docstring).
Post-hardening: is_super_only_delegation returns True → violation.
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


class FakeSuperDelegationAgent(SovereignBaseAgent):
    """Agent that delegates execute entirely to super — effectively a stub."""

    def execute(self, **kwargs):
        return super().execute(**kwargs)
