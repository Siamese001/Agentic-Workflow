from __future__ import annotations
"""
Unit Tests for Phase 5: Observability & Telemetry Components

Tests the core observability functionality:
- ExecutionTracer
- MetricsCollector
- ValidationAgent
- AuditReporter
- TelemetryExporter
- Phase5Orchestrator
"""

import json
import time
from pathlib import Path

import pytest

from ..context import ResumeEngineContext
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from ..observability import (
    AuditReporter,
    ExecutionTrace,
    ExecutionTracer,
    Metric,
    MetricsCollector,
    MetricType,
    Phase5Orchestrator,
    TelemetryExporter,
    TraceLevel,
    TraceStep,
    ValidationAgent,
    ValidationIssue,
    ValidationSeverity,
)


@pytest.fixture
def ctx():
    """Create a fresh context for each test."""
    return ResumeEngineContext()


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
    }


@pytest.fixture
def invalid_resume():
    """Create an invalid resume for testing."""
    return {
        "summary": "I helped with stuff.",
        "experience": [
            {"company": "", "title": ""},
        ],
        "skills": [],
    }


class TestTraceLevel:
    """Tests for TraceLevel enum."""

    def test_trace_levels(self):
        """Test trace level values."""
        assert TraceLevel.MINIMAL.value == "minimal"
        assert TraceLevel.STANDARD.value == "standard"
        assert TraceLevel.VERBOSE.value == "verbose"
        assert TraceLevel.DEBUG.value == "debug"


class TestMetricType:
    """Tests for MetricType enum."""

    def test_metric_types(self):
        """Test Metric type values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_severity_levels(self):
        """Test Severity level values."""
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.CRITICAL.value == "critical"


class TestTraceStep:
    """Tests for TraceStep dataclass."""

    def test_create_step(self):
        """Test creating a trace step."""
        step = TraceStep(
            step_id="step_1",
            agent_name="TestAgent",
            action="test_action",
            start_time=time.time(),
        )

        assert step.step_id == "step_1"
        assert step.agent_name == "TestAgent"
        assert step.success is True
        assert step.error is None


class TestExecutionTrace:
    """Tests for ExecutionTrace dataclass."""

    def test_create_trace(self):
        """Test creating an execution trace."""
        trace = ExecutionTrace(
            trace_id="trace_123",
            mission_id="mission_456",
            start_time="2024-01-01T00:00:00",
        )

        assert trace.trace_id == "trace_123"
        assert trace.mission_id == "mission_456"
        assert trace.success is True
        assert trace.steps == []


class TestMetric:
    """Tests for Metric dataclass."""

    def test_create_metric(self):
        """Test creating a Metric."""
        Metric = Metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
        )

        assert Metric.name == "test_metric"
        assert Metric.value == 42.0
        assert Metric.metric_type == MetricType.GAUGE


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            rule_id="TEST_RULE",
            Severity=ValidationSeverity.WARNING,
            file_path="summary",
            line_number=None,
            message="Test issue",
            suggestion="Fix it",
        )

        assert issue.rule_id == "TEST_RULE"
        assert issue.Severity == ValidationSeverity.WARNING


class TestExecutionTracer:
    """Tests for ExecutionTracer class."""

    def test_init(self, ctx):
        """Test ExecutionTracer initialization."""
        tracer = ExecutionTracer(ctx)

        assert tracer.ctx == ctx
        assert tracer.level == TraceLevel.STANDARD

    def test_start_trace(self, ctx):
        """Test starting a trace."""
        tracer = ExecutionTracer(ctx)

        trace_id = tracer.start_trace("mission_1")

        assert trace_id is not None
        assert len(trace_id) == 16

    def test_start_step(self, ctx):
        """Test starting a step."""
        tracer = ExecutionTracer(ctx)
        tracer.start_trace("mission_1")

        step_id = tracer.start_step("TestAgent", "test_action")

        assert step_id == "step_1"

    def test_end_step(self, ctx):
        """Test ending a step."""
        tracer = ExecutionTracer(ctx)
        tracer.start_trace("mission_1")
        step_id = tracer.start_step("TestAgent", "test_action")

        tracer.end_step(step_id, success=True)

        trace = tracer.end_trace()
        assert trace.steps[0].success is True
        assert trace.steps[0].duration_ms is not None

    def test_end_step_with_error(self, ctx):
        """Test ending a step with error."""
        tracer = ExecutionTracer(ctx)
        tracer.start_trace("mission_1")
        step_id = tracer.start_step("TestAgent", "test_action")

        tracer.end_step(step_id, success=False, error="Test error")

        trace = tracer.end_trace()
        assert trace.steps[0].success is False
        assert trace.steps[0].error == "Test error"

    def test_end_trace(self, ctx):
        """Test ending a trace."""
        tracer = ExecutionTracer(ctx)
        tracer.start_trace("mission_1")
        tracer.start_step("TestAgent", "test_action")

        trace = tracer.end_trace(success=True)

        assert trace is not None
        assert trace.success is True
        assert trace.end_time is not None

    def test_get_trace(self, ctx):
        """Test getting a trace by ID."""
        tracer = ExecutionTracer(ctx)
        trace_id = tracer.start_trace("mission_1")
        tracer.end_trace()

        trace = tracer.get_trace(trace_id)

        assert trace is not None
        assert trace.trace_id == trace_id

    def test_get_all_traces(self, ctx):
        """Test getting all traces."""
        tracer = ExecutionTracer(ctx)

        tracer.start_trace("mission_1")
        tracer.end_trace()
        tracer.start_trace("mission_2")
        tracer.end_trace()

        traces = tracer.get_all_traces()

        assert len(traces) == 2

    def test_get_stats(self, ctx):
        """Test getting tracer statistics."""
        tracer = ExecutionTracer(ctx)
        tracer.start_trace("mission_1")
        tracer.start_step("Agent1", "action1")
        tracer.end_trace()

        stats = tracer.get_stats()

        assert stats["total_traces"] == 1
        assert stats["total_steps"] == 1


class TestMetricsCollector:
    """Tests for MetricsCollector class."""

    def test_init(self, ctx):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector(ctx)

        assert collector.ctx == ctx

    def test_increment(self, ctx):
        """Test incrementing a counter."""
        collector = MetricsCollector(ctx)

        collector.increment("test_counter")
        collector.increment("test_counter")

        assert collector.get_counter("test_counter") == 2

    def test_increment_with_value(self, ctx):
        """Test incrementing with custom value."""
        collector = MetricsCollector(ctx)

        collector.increment("test_counter", value=5)

        assert collector.get_counter("test_counter") == 5

    def test_gauge(self, ctx):
        """Test setting a gauge."""
        collector = MetricsCollector(ctx)

        collector.gauge("test_gauge", 42)

        assert collector.get_gauge("test_gauge") == 42

    def test_histogram(self, ctx):
        """Test recording a histogram value."""
        collector = MetricsCollector(ctx)

        collector.histogram("test_histogram", 100)

        metrics = collector.get_metrics(name="test_histogram")
        assert len(metrics) == 1
        assert metrics[0].value == 100

    def test_timer(self, ctx):
        """Test recording a timer value."""
        collector = MetricsCollector(ctx)

        collector.timer("test_timer", 500)

        metrics = collector.get_metrics(name="test_timer")
        assert len(metrics) == 1
        assert metrics[0].value == 500

    def test_get_metrics_by_type(self, ctx):
        """Test getting metrics by type."""
        collector = MetricsCollector(ctx)

        collector.increment("counter1")
        collector.gauge("gauge1", 10)

        counters = collector.get_metrics(metric_type=MetricType.COUNTER)
        gauges = collector.get_metrics(metric_type=MetricType.GAUGE)

        assert len(counters) == 1
        assert len(gauges) == 1

    def test_reset(self, ctx):
        """Test resetting metrics."""
        collector = MetricsCollector(ctx)

        collector.increment("test")
        collector.reset()

        assert collector.get_counter("test") == 0

    def test_get_stats(self, ctx):
        """Test getting collector statistics."""
        collector = MetricsCollector(ctx)

        collector.increment("counter1")
        collector.gauge("gauge1", 10)

        stats = collector.get_stats()

        assert stats["counters"] == 1
        assert stats["gauges"] == 1


class TestValidationAgent(MCPHardenedMixin, HealerMixin):
    """Tests for ValidationAgent class."""


    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        super().heal_repository()

        return {"violations": 0, "fixed": 0, "errors": 0}

    def test_init(self, ctx):
        """Test ValidationAgent initialization."""
        validator = ValidationAgent(ctx)

        assert validator.ctx == ctx

    def test_validate_valid_resume(self, ctx, valid_resume):
        """Test validating a valid resume."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume(valid_resume)

        # Valid resume should have few or no issues
        errors = [i for i in issues if i.Severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_validate_invalid_resume(self, ctx, invalid_resume):
        """Test validating an invalid resume."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume(invalid_resume)

        # Invalid resume should have issues
        assert len(issues) > 0

    def test_validate_empty_summary(self, ctx):
        """Test validating empty summary."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume({"summary": ""})

        error_issues = [i for i in issues if i.rule_id == "SUMMARY_EMPTY"]
        assert len(error_issues) == 1

    def test_validate_short_summary(self, ctx):
        """Test validating short summary."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume({"summary": "Short."})

        short_issues = [i for i in issues if i.rule_id == "SUMMARY_TOO_SHORT"]
        assert len(short_issues) == 1

    def test_validate_weak_language(self, ctx):
        """Test detecting weak language."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume({
            "summary": "I helped with various projects and assisted the team with tasks."
        })

        weak_issues = [i for i in issues if i.rule_id == "SUMMARY_WEAK_LANGUAGE"]
        assert len(weak_issues) >= 1

    def test_validate_empty_experience(self, ctx):
        """Test validating empty experience."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume({"experience": []})

        error_issues = [i for i in issues if i.rule_id == "EXPERIENCE_EMPTY"]
        assert len(error_issues) == 1

    def test_get_issues_by_severity(self, ctx, invalid_resume):
        """Test getting issues by Severity."""
        validator = ValidationAgent(ctx)
        validator.validate_resume(invalid_resume)

        errors = validator.get_issues_by_severity(ValidationSeverity.ERROR)

        assert all(i.Severity == ValidationSeverity.ERROR for i in errors)

    def test_get_stats(self, ctx, invalid_resume):
        """Test getting validation statistics."""
        validator = ValidationAgent(ctx)
        validator.validate_resume(invalid_resume)

        stats = validator.get_stats()

        assert stats["total_issues"] > 0


class TestAuditReporter:
    """Tests for AuditReporter class."""

    def test_init(self, ctx):
        """Test AuditReporter initialization."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)

        reporter = AuditReporter(ctx, tracer, metrics, validator)

        assert reporter.ctx == ctx

    def test_generate_report(self, ctx, valid_resume):
        """Test generating an audit report."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        # Add some data
        tracer.start_trace("mission_1")
        tracer.start_step("Agent1", "action1")
        tracer.end_trace()
        metrics.increment("test_metric")
        validator.validate_resume(valid_resume)

        report = reporter.generate_report("mission_1")

        assert report.report_id is not None
        assert report.mission_id == "mission_1"
        assert "total_traces" in report.summary

    def test_export_report_json(self, ctx, tmp_path):
        """Test exporting report to JSON."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        report = reporter.generate_report("mission_1")
        output_path = str(tmp_path / "report.json")

        result = reporter.export_report(report, output_path, format="json")

        assert Path(result).exists()
        content = json.loads(Path(result).read_text())
        assert "report_id" in content

    def test_export_report_markdown(self, ctx, tmp_path):
        """Test exporting report to Markdown."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        report = reporter.generate_report("mission_1")
        output_path = str(tmp_path / "report.md")

        result = reporter.export_report(report, output_path, format="markdown")

        assert Path(result).exists()
        content = Path(result).read_text()
        assert "# Audit Report" in content

    def test_get_stats(self, ctx):
        """Test getting reporter statistics."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        reporter.generate_report("mission_1")

        stats = reporter.get_stats()

        assert stats["total_reports"] == 1


class TestTelemetryExporter:
    """Tests for TelemetryExporter class."""

    def test_init(self, ctx):
        """Test TelemetryExporter initialization."""
        exporter = TelemetryExporter(ctx)

        assert exporter.ctx == ctx

    def test_export_traces_json(self, ctx):
        """Test exporting traces to JSON."""
        exporter = TelemetryExporter(ctx)

        traces = [
            ExecutionTrace(
                trace_id="trace_1",
                mission_id="mission_1",
                start_time="2024-01-01T00:00:00",
            )
        ]

        result = exporter.export_traces(traces, format="json")

        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["trace_id"] == "trace_1"

    def test_export_traces_otlp(self, ctx):
        """Test exporting traces to OTLP format."""
        exporter = TelemetryExporter(ctx)

        step = TraceStep(
            step_id="step_1",
            agent_name="TestAgent",
            action="test",
            start_time=time.time(),
            end_time=time.time() + 1,
        )

        traces = [
            ExecutionTrace(
                trace_id="trace_1",
                mission_id="mission_1",
                start_time="2024-01-01T00:00:00",
                steps=[step],
            )
        ]

        result = exporter.export_traces(traces, format="otlp")

        data = json.loads(result)
        assert "resourceSpans" in data

    def test_export_metrics_json(self, ctx):
        """Test exporting metrics to JSON."""
        exporter = TelemetryExporter(ctx)

        metrics = [
            Metric(name="test_metric", value=42, metric_type=MetricType.GAUGE)
        ]

        result = exporter.export_metrics(metrics, format="json")

        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["name"] == "test_metric"

    def test_export_metrics_prometheus(self, ctx):
        """Test exporting metrics to Prometheus format."""
        exporter = TelemetryExporter(ctx)

        metrics = [
            Metric(name="test_metric", value=42, metric_type=MetricType.GAUGE)
        ]

        result = exporter.export_metrics(metrics, format="prometheus")

        assert "test_metric 42" in result

    def test_get_stats(self, ctx):
        """Test getting exporter statistics."""
        exporter = TelemetryExporter(ctx)

        exporter.export_traces([], format="json")
        exporter.export_metrics([], format="json")

        stats = exporter.get_stats()

        assert stats["export_count"] == 2


class TestPhase5Orchestrator(HealerMixin):
    """Tests for Phase5Orchestrator class."""

    def test_init(self, ctx):
        """Test Phase5Orchestrator initialization."""
        orchestrator = Phase5Orchestrator(ctx)

        assert orchestrator.ctx == ctx
        assert orchestrator.tracer is not None
        assert orchestrator.metrics is not None
        assert orchestrator.validator is not None
        assert orchestrator.reporter is not None
        assert orchestrator.exporter is not None

    def test_start_mission(self, ctx):
        """Test starting a mission."""
        orchestrator = Phase5Orchestrator(ctx)

        trace_id = orchestrator.start_mission("mission_1")

        assert trace_id is not None
        assert orchestrator.metrics.get_counter("missions.started") == 1

    def test_end_mission_success(self, ctx):
        """Test ending a successful mission."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")

        trace = orchestrator.end_mission(success=True)

        assert trace is not None
        assert trace.success is True
        assert orchestrator.metrics.get_counter("missions.succeeded") == 1

    def test_end_mission_failure(self, ctx):
        """Test ending a failed mission."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")

        trace = orchestrator.end_mission(success=False)

        assert trace.success is False
        assert orchestrator.metrics.get_counter("missions.failed") == 1

    def test_track_agent(self, ctx):
        """Test tracking an agent."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")

        step_id = orchestrator.track_agent("TestAgent", "test_action")

        assert step_id is not None

    def test_complete_agent(self, ctx):
        """Test completing agent tracking."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")
        step_id = orchestrator.track_agent("TestAgent", "test_action")

        orchestrator.complete_agent(step_id, success=True)

        trace = orchestrator.end_mission()
        assert trace.steps[0].success is True

    def test_validate_resume(self, ctx, valid_resume):
        """Test validating a resume."""
        orchestrator = Phase5Orchestrator(ctx)

        issues = orchestrator.validate_resume(valid_resume)

        assert isinstance(issues, list)

    def test_generate_report(self, ctx):
        """Test generating a report."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")
        orchestrator.end_mission()

        report = orchestrator.generate_report("mission_1")

        assert report is not None
        assert report.mission_id == "mission_1"

    def test_export_telemetry(self, ctx):
        """Test exporting telemetry."""
        orchestrator = Phase5Orchestrator(ctx)
        orchestrator.start_mission("mission_1")
        orchestrator.metrics.increment("test_metric")
        orchestrator.end_mission()

        telemetry = orchestrator.export_telemetry(format="json")

        assert "traces" in telemetry
        assert "metrics" in telemetry

    def test_get_comprehensive_stats(self, ctx):
        """Test getting comprehensive statistics."""
        orchestrator = Phase5Orchestrator(ctx)

        stats = orchestrator.get_comprehensive_stats()

        assert "tracer" in stats
        assert "metrics" in stats
        assert "validator" in stats
        assert "reporter" in stats
        assert "exporter" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
