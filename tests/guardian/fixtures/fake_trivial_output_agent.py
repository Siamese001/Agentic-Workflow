"""Synthetic fixture: agent whose execute() returns a trivial dict with 'output' key.

Pre-hardening: dict-key heuristic accepted "output" → no violation.
Post-hardening: only "artifacts"/"artifact" accepted → violation.
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class FakeTrivialOutputAgent(SovereignBaseAgent):
    """Agent that returns {"output": None} — no real artifact emission."""

    def execute(self, **kwargs):
        return {"output": None}
