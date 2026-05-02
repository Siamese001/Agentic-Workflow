"""Runtime-glue services for apps_underwriting_ai.

Services wire static configuration (YAML rubrics, spine manifests) and
runtime telemetry (judge events, audit scans) into the existing engine
pipeline. They are intentionally thin — orchestration lives in engines;
services just load, emit, or scan.

Public API:
  - :class:`RubricWiringService` — loads + caches the judge rubric YAML
  - :class:`LLMJudgeTelemetryService` — emits `judge_result` events
  - :class:`PreMigrationAuditService` — AST scan for durable-write leakage
"""
from __future__ import annotations

from apps_underwriting_ai.services.llm_judge_telemetry_service import (
    JudgeTelemetryEvent,
    LLMJudgeTelemetryService,
)
from apps_underwriting_ai.services.pre_migration_audit_service import (
    AuditFinding,
    AuditReport,
    PreMigrationAuditService,
)
from apps_underwriting_ai.services.rubric_wiring_service import (
    RubricSpec,
    RubricWiringService,
)

__all__ = [
    "AuditFinding",
    "AuditReport",
    "JudgeTelemetryEvent",
    "LLMJudgeTelemetryService",
    "PreMigrationAuditService",
    "RubricSpec",
    "RubricWiringService",
]
