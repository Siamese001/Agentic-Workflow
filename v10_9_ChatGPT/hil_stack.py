"""Human-in-the-loop handling."""
from __future__ import annotations

from typing import Dict

from .models import HILDecision, Message
from .services import ServiceBundle
from .telemetry import log_event


class HILStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services

    def assess(self, message: Message) -> Dict[str, HILDecision]:
        decision = HILDecision(requires_human="?" in message.content, rationale="Detected uncertainty" if "?" in message.content else "Auto" )
        log_event("hil_assess", {"requires_human": decision.requires_human})
        return {"hil_decision": decision}

    def reconcile(self, message: Message, human_edit: str | None = None) -> Dict[str, Message]:
        if human_edit:
            revised = Message(role="assistant", content=human_edit)
        else:
            revised = message
        log_event("hil_reconcile", {"edited": bool(human_edit)})
        return {"message": revised}
