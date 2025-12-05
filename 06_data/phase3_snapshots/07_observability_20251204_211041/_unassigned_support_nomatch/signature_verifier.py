"""Append signature information to the outreach draft."""
from __future__ import annotations


class SignatureAgent:
    def attach(self, draft: str, route_decision) -> str:
        signature = "Best regards,\nLIC Outreach Bot"
        return f"{draft}\n\n{signature}"
