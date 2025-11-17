"""QA validation suite."""
from __future__ import annotations

from typing import Dict, List

from .models import Message, QAResult
from .services import ServiceBundle
from .telemetry import log_event


class QAStack:
    def __init__(self, services: ServiceBundle) -> None:
        self.services = services

    def run_checks(self, message: Message) -> Dict[str, QAResult]:
        findings: List[str] = []
        if len(message.content) < 10:
            findings.append("response too short")
        result = QAResult(passed=not findings, findings=findings)
        log_event("qa_checks", {"passed": result.passed})
        return {"qa_result": result}
