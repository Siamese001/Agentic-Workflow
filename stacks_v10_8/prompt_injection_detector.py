"""Lightweight prompt injection detector for v10.8 stacks."""
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class PromptInjectionDetector(BaseModel):
    """Heuristic detector that scans text for prompt injection triggers."""

    triggers: List[str] = [
        "ignore previous",
        "disregard above",
        "override system",
        "simulate system",
        "developer instructions",
    ]

    def detect(self, text: str) -> Dict[str, Any]:
        findings = []
        lower = (text or "").lower()
        for trigger in self.triggers:
            if trigger in lower:
                findings.append({"type": "injection", "trigger": trigger})
        return {"findings": findings, "is_safe": len(findings) == 0}
