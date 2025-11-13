"""Refine the call-to-action portion of the draft."""
from __future__ import annotations

from ..core import LICBaseAgent


class CTAAgent(LICBaseAgent):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context)

    def adjust(self, draft: str, route_decision) -> str:
        cta_line = "CTA: Would you be open to a 15-minute chat next week?"
        return f"{draft}\n\n{cta_line}"
