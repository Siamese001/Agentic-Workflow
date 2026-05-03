"""Synthetic fixture: agent whose execute() is pure super-delegation.

Pre-hardening: is_stub_body returns False (not pass/…/raise/docstring).
Post-hardening: is_super_only_delegation returns True → violation.
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class FakeSuperDelegationAgent(SovereignBaseAgent):
    """Agent that delegates execute entirely to super — effectively a stub."""

    def execute(self, **kwargs):
        return super().execute(**kwargs)
