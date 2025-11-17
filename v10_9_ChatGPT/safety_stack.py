"""Safety checks for PII, injection, and constitutional review."""
from __future__ import annotations

from typing import Dict, List

from .models import Message, SafetyReport
from .services import ServiceBundle
from .telemetry import log_event


class SafetyStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services

    def sanitize(self, message: Message) -> Dict[str, Message]:
        cleaned = message.content.replace("PII", "[REDACTED]")
        log_event("safety_sanitize", {})
        return {"message": Message(role=message.role, content=cleaned)}

    def review(self, message: Message) -> Dict[str, SafetyReport]:
        issues: List[str] = []
        if "unsafe" in message.content:
            issues.append("content flagged")
        report = SafetyReport(safe=not issues, issues=issues)
        log_event("safety_review", {"safe": report.safe})
        return {"safety_report": report}
