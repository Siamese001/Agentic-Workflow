"""Refine the call-to-action portion of the draft."""
from __future__ import annotations


class CTAAgent:
    def adjust(self, draft: str, route_decision) -> str:
        cta_line = "CTA: Would you be open to a 15-minute chat next week?"
        return f"{draft}\n\n{cta_line}"
