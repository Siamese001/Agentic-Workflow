"""Synthetic fixture: agent whose execute() returns a trivial dict with 'output' key.

Pre-hardening: dict-key heuristic accepted "output" → no violation.
Post-hardening: only "artifacts"/"artifact" accepted → violation.
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


class FakeTrivialOutputAgent(SovereignBaseAgent):
    """Agent that returns {"output": None} — no real artifact emission."""

    def execute(self, **kwargs):
        return {"output": None}
