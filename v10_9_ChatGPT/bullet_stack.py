"""Bullet planning and execution."""
from __future__ import annotations

from typing import Dict, List

from .models import BulletPlan, Message
from .services import ServiceBundle
from .telemetry import log_event


class BulletStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services

    def plan(self, context: str) -> Dict[str, BulletPlan]:
        bullets = [f"key point {i+1}: {context}" for i in range(3)]
        plan = BulletPlan(bullets=bullets)
        log_event("bullet_plan", {"count": len(bullets)})
        return {"bullet_plan": plan}

    def execute(self, plan: BulletPlan) -> Dict[str, List[Message]]:
        messages = [Message(role="assistant", content=bullet) for bullet in plan.bullets]
        log_event("bullet_execute", {"count": len(messages)})
        return {"messages": messages}
