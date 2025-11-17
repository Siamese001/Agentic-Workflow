"""Prompt builder and renderer."""
from __future__ import annotations

from typing import Dict, List

from .models import Message
from .services import PromptTemplateManager, ServiceBundle
from .telemetry import log_event


class PromptStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services
        self.templates = PromptTemplateManager()

    def render_prompt(self, instructions: str, context: List[Message]) -> Dict[str, str]:
        history = "\n".join(msg.content for msg in context)
        prompt = self.templates.render("{instructions}\n\n{history}", instructions=instructions, history=history)
        log_event("prompt_render", {"length": len(prompt)})
        return {"prompt": prompt}
