"""Runtime-glue services for apps_underwriting_ai.

Services wire static configuration (YAML rubrics, spine manifests) and
runtime telemetry (judge events, audit scans) into the existing engine
pipeline. They are intentionally thin — orchestration lives in engines;
services just load, emit, or scan.

Public API:
  - :class:`RubricWiringService` — loads + caches the judge rubric YAML
  - :class:`LLMJudgeTelemetryService` — emits `judge_result` events
  - :class:`PreMigrationAuditService` — AST scan for durable-write leakage
  - :func:`generate_frontier_rationale` — frontier second-judge pairing
    (W3.1, plan ``apps-underwriting-ai-activation-e8a3c5``)
  - :func:`record_pair` / :func:`watchdog_verdict` — rolling Wilson-CI
    agreement tracker for Qwen/frontier pairing (W3.2)
"""
from __future__ import annotations

from apps_underwriting_ai.services.frontier_rationale_judge import (
    generate_frontier_rationale,
)
from apps_underwriting_ai.services.llm_judge_telemetry_service import (
    JudgeTelemetryEvent,
    LLMJudgeTelemetryService,
)
from apps_underwriting_ai.services.pre_migration_audit_service import (
    AuditFinding,
    AuditReport,
    PreMigrationAuditService,
)
from apps_underwriting_ai.services.rationale_agreement_tracker import (
    AGREEMENT_THRESHOLD,
    AgreementSample,
    JACCARD_AGREE_THRESHOLD,
    MIN_SAMPLES,
    ROLLING_WINDOW_SECONDS,
    WatchdogVerdict,
    jaccard_overlap,
    record_pair,
    watchdog_verdict,
)
from apps_underwriting_ai.services.rubric_wiring_service import (
    RubricSpec,
    RubricWiringService,
)

__all__ = [
    "AGREEMENT_THRESHOLD",
    "AgreementSample",
    "AuditFinding",
    "AuditReport",
    "JACCARD_AGREE_THRESHOLD",
    "JudgeTelemetryEvent",
    "LLMJudgeTelemetryService",
    "MIN_SAMPLES",
    "PreMigrationAuditService",
    "ROLLING_WINDOW_SECONDS",
    "RubricSpec",
    "RubricWiringService",
    "WatchdogVerdict",
    "generate_frontier_rationale",
    "jaccard_overlap",
    "record_pair",
    "watchdog_verdict",
]
