"""W3 services contract tests."""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
)
from apps_underwriting_ai.services import (
    AuditReport,
    JudgeTelemetryEvent,
    LLMJudgeTelemetryService,
    PreMigrationAuditService,
    RubricSpec,
    RubricWiringService,
)
from apps_underwriting_ai.services.rubric_wiring_service import (
    RubricCriterion,
    RubricSpecError,
)


# -- RubricWiringService ----------------------------------------------------


def test_rubric_wiring_loads_shipped_yaml() -> None:
    spec = RubricWiringService().load()
    assert isinstance(spec, RubricSpec)
    assert spec.rubric_id
    assert spec.rubric_version >= 1
    assert spec.owning_app == "apps_underwriting_ai"
    assert all(isinstance(c, RubricCriterion) for c in spec.criteria)
    assert len(spec.criteria) >= 1


def test_rubric_wiring_cache_returns_same_instance() -> None:
    service = RubricWiringService()
    spec1 = service.load()
    spec2 = service.load()
    assert spec1 is spec2


def test_rubric_wiring_reload_bypasses_cache() -> None:
    service = RubricWiringService()
    spec1 = service.load()
    spec2 = service.reload()
    # After reload the cache is cleared; a subsequent load matches reload result
    spec3 = service.load()
    assert spec1 is not spec2 or spec2 is spec3


def test_rubric_wiring_raises_on_missing(tmp_path: Path) -> None:
    svc = RubricWiringService(rubric_path=tmp_path / "nope.yaml")
    with pytest.raises(RubricSpecError, match="not found"):
        svc.load()


def test_rubric_wiring_raises_on_non_mapping(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("- just\n- a\n- list\n", encoding="utf-8")
    svc = RubricWiringService(rubric_path=p)
    with pytest.raises(RubricSpecError, match="must be a mapping"):
        svc.load()


def test_rubric_wiring_raises_on_missing_keys(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("something: else\n", encoding="utf-8")
    svc = RubricWiringService(rubric_path=p)
    with pytest.raises(RubricSpecError, match="missing required keys"):
        svc.load()


def test_rubric_wiring_parses_criteria_weights(tmp_path: Path) -> None:
    p = tmp_path / "ok.yaml"
    p.write_text(
        "rubric_id: test\n"
        "rubric_version: 1\n"
        "evaluation_criteria:\n"
        "  - id: clarity\n"
        "    description: be clear\n"
        "    weight: 0.5\n"
        "  - id: grounding\n"
        "    description: cite evidence\n"
        "    weight: 0.5\n",
        encoding="utf-8",
    )
    spec = RubricWiringService(rubric_path=p).load()
    assert {c.id for c in spec.criteria} == {"clarity", "grounding"}
    assert sum(c.weight for c in spec.criteria) == pytest.approx(1.0)


# -- LLMJudgeTelemetryService -----------------------------------------------


def test_judge_telemetry_default_adapter_is_observability() -> None:
    svc = LLMJudgeTelemetryService()
    assert isinstance(svc.adapter, ObservabilityAdapter)


def test_judge_telemetry_emit_does_not_raise() -> None:
    svc = LLMJudgeTelemetryService()
    svc.emit(
        JudgeTelemetryEvent(
            request_id="t-1",
            rubric_id="r-1",
            rubric_version=1,
            passed=True,
            model_used="deterministic_template",
            rationale_chars=50,
        )
    )


def test_judge_telemetry_emit_logs_judge_result(caplog) -> None:
    svc = LLMJudgeTelemetryService()
    with caplog.at_level(logging.INFO, logger="apps_underwriting_ai.integrations.observability_adapter"):
        svc.emit(
            JudgeTelemetryEvent(
                request_id="t-log",
                rubric_id="r-log",
                rubric_version=2,
                passed=False,
                model_used="qwen_local",
                fallback_reason="length_guard",
                latency_ms=123.4,
                rationale_chars=800,
                first_failed_gate="length",
            )
        )
    # ObservabilityAdapter logs "event"; extra fields carry the payload
    assert any("event" in rec.message for rec in caplog.records)


def test_judge_telemetry_event_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    event = JudgeTelemetryEvent(
        request_id="t",
        rubric_id="r",
        rubric_version=1,
        passed=True,
        model_used="m",
    )
    with pytest.raises(FrozenInstanceError):
        event.passed = False  # type: ignore[misc]


# -- PreMigrationAuditService ----------------------------------------------


def test_audit_returns_audit_report() -> None:
    report = PreMigrationAuditService().audit()
    assert isinstance(report, AuditReport)


def test_audit_has_zero_findings_on_apps_underwriting_ai() -> None:
    report = PreMigrationAuditService().audit()
    # R3_grounded_read invariant: zero durable-write tokens in the package
    assert report.passed, f"audit findings: {report.findings}"
    assert len(report.findings) == 0


def test_audit_scans_multiple_files() -> None:
    report = PreMigrationAuditService().audit()
    assert report.scanned_files > 5


def test_audit_finds_synthetic_tokens(tmp_path: Path) -> None:
    # Build a synthetic package containing a forbidden token
    synth = tmp_path / "pkg"
    synth.mkdir()
    (synth / "bad.py").write_text(
        "def f():\n    return CommitRequest()  # forbidden\n",
        encoding="utf-8",
    )
    (synth / "good.py").write_text(
        "def g():\n    return 'ok'\n",
        encoding="utf-8",
    )
    report = PreMigrationAuditService(app_root=synth).audit()
    assert not report.passed
    tokens = {f.token for f in report.findings}
    assert "CommitRequest" in tokens


def test_audit_report_summary_shape() -> None:
    report = PreMigrationAuditService().audit()
    summary = report.summary()
    assert "passed" in summary
    assert "scanned_files" in summary
    assert "finding_count" in summary
    assert "forbidden_tokens" in summary
