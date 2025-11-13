"""Append signature information to the outreach draft."""
from __future__ import annotations

from ..core import LICBaseAgent


class SignatureAgent(LICBaseAgent):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context)

    def attach(self, draft: str, route_decision) -> str:
        signature = "Best regards,\nLIC Outreach Bot"
        return f"{draft}\n\n{signature}"
