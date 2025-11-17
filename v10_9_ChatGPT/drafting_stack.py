"""Draft planning and execution."""
from __future__ import annotations

from typing import Dict

from .clients import AsyncBaseModelClient
from .models import DraftPlan, Message
from .services import ServiceBundle
from .telemetry import log_event


class DraftingStack:
    def __init__(self, services: ServiceBundle, client: AsyncBaseModelClient) -> None:
        self.services = services
        self.client = client

    def plan(self, bullets: list[str]) -> Dict[str, DraftPlan]:
        plan = DraftPlan(sections=bullets)
        log_event("draft_plan", {"sections": len(bullets)})
        return {"draft_plan": plan}

    async def execute(self, plan: DraftPlan) -> Dict[str, Message]:
        text = "\n".join(plan.sections)
        output = await self.client.generate(text)
        message = Message(role="assistant", content=output)
        log_event("draft_execute", {"length": len(output)})
        return {"message": message}
