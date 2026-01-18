"""
Observability & Telemetry Module - Phase 5 Implementation

This module provides advanced observability capabilities:
- ExecutionTracer: Tracks agent execution with timing and results
- MetricsCollector: Collects and aggregates performance metrics
- AuditReporter: Generates comprehensive audit reports
- TelemetryExporter: Exports telemetry data for external systems
- ValidationAgent: Pattern enforcement and code quality checks
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto


import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .context import ResumeEngineContext


class TraceLevel(Enum):
    """Trace detail levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    VERBOSE = "verbose"
    DEBUG = "debug"


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TraceStep:
    """A single step in an execution trace."""
    step_id: str
    agent_name: str
    action: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Complete execution trace for a healing mission."""
    trace_id: str
    mission_id: str
    start_time: str
    end_time: Optional[str] = None
    steps: List[TraceStep] = field(default_factory=list)
    total_duration_ms: Optional[float] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """A single Metric measurement."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    """A validation issue found during analysis."""
    rule_id: str
    Severity: ValidationSeverity
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: Optional[str] = None


@dataclass
class AuditReport:
    """Comprehensive audit report."""
    report_id: str
    generated_at: str
    mission_id: str
    summary: Dict[str, Any]
    traces: List[ExecutionTrace]
    metrics: List[Metric]
    validation_issues: List[ValidationIssue]
    recommendations: List[str]


class ExecutionTracer:
    """
    Tracks agent execution with detailed timing and results.

    Features:
    - Step-by-step execution tracking
    - Timing measurements
    - Error capture
    - Metadata attachment
    """

    def __init__(self, ctx: ResumeEngineContext, level: TraceLevel = TraceLevel.STANDARD):
        self.ctx = ctx
        self.level = level
        self._traces: Dict[str, ExecutionTrace] = {}
        self._current_trace: Optional[ExecutionTrace] = None
        self._step_counter = 0

    def start_trace(self, mission_id: str) -> str:
        """
        Start a new execution trace.

        Args:
            mission_id: ID of the mission being traced

        Returns:
            Trace ID
        """
        trace_id = hashlib.sha256(
            f"{mission_id}_{time.time()}".encode()
        ).hexdigest()[:16]

        self._current_trace = ExecutionTrace(
            trace_id=trace_id,
            mission_id=mission_id,
            start_time=datetime.now().isoformat(),
        )

        self._traces[trace_id] = self._current_trace
        self._step_counter = 0

        return trace_id

    def start_step(
        self,
        agent_name: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start a new step in the current trace.

        Args:
            agent_name: Name of the agent executing
            action: Description of the action
            metadata: Optional metadata

        Returns:
            Step ID
        """
        if not self._current_trace:
            return ""

        self._step_counter += 1
        step_id = f"step_{self._step_counter}"

        step = TraceStep(
            step_id=step_id,
            agent_name=agent_name,
            action=action,
            start_time=time.time(),
            metadata=metadata or {},
        )

        self._current_trace.steps.append(step)

        return step_id

    def end_step(
        self,
        step_id: str,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        End a step in the current trace.

        Args:
            step_id: ID of the step to end
            success: Whether the step succeeded
            error: Error message if failed
            metadata: Additional metadata
        """
        if not self._current_trace:
            return

        for step in self._current_trace.steps:
            if step.step_id == step_id:
                step.end_time = time.time()
                step.duration_ms = (step.end_time - step.start_time) * 1000
                step.success = success
                step.error = error
                if metadata:
                    step.metadata.update(metadata)
                break

    def end_trace(self, success: bool = True) -> Optional[ExecutionTrace]:
        """
        End the current trace.

        Args:
            success: Whether the mission succeeded

        Returns:
            The completed trace
        """
        if not self._current_trace:
            return None

        self._current_trace.end_time = datetime.now().isoformat()
        self._current_trace.success = success

        # Calculate total duration
        if self._current_trace.steps:
            first_step = self._current_trace.steps[0]
            last_step = self._current_trace.steps[-1]
            if last_step.end_time:
                self._current_trace.total_duration_ms = (
                    last_step.end_time - first_step.start_time
                ) * 1000

        trace = self._current_trace
        self._current_trace = None

        return trace

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Get a trace by ID."""
        return self._traces.get(trace_id)

    def get_all_traces(self) -> List[ExecutionTrace]:
        """Get all traces."""
        return list(self._traces.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get tracer statistics."""
        total_traces = len(self._traces)
        successful = sum(1 for t in self._traces.values() if t.success)
        total_steps = sum(len(t.steps) for t in self._traces.values())

        return {
            "total_traces": total_traces,
            "successful_traces": successful,
            "failed_traces": total_traces - successful,
            "total_steps": total_steps,
            "trace_level": self.level.value,
        }


class MetricsCollector:
    """
    Collects and aggregates performance metrics.

    Features:
    - Counter, gauge, histogram, timer metrics
    - Tag-based filtering
    - Aggregation functions
    """

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx
        self._metrics: List[Metric] = []
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}

    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter Metric."""
        key = self._make_key(name, tags)
        self._counters[key] = self._counters.get(key, 0) + value

        self._metrics.append(Metric(
            name=name,
            value=self._counters[key],
            metric_type=MetricType.COUNTER,
            tags=tags or {},
        ))

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge Metric."""
        key = self._make_key(name, tags)
        self._gauges[key] = value

        self._metrics.append(Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {},
        ))

    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value."""
        self._metrics.append(Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {},
        ))

    def timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timer value."""
        self._metrics.append(Metric(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            tags=tags or {},
        ))

    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a Metric."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_str}"

    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0)

    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
    ) -> List[Metric]:
        """Get metrics with optional filtering."""
        result = self._metrics

        if name:
            result = [m for m in result if m.name == name]

        if metric_type:
            result = [m for m in result if m.metric_type == metric_type]

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get collector statistics."""
        return {
            "total_metrics": len(self._metrics),
            "counters": len(self._counters),
            "gauges": len(self._gauges),
            "by_type": {
                t.value: sum(1 for m in self._metrics if m.metric_type == t)
                for t in MetricType
            },
        }

    def reset(self):
        """Reset all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()


class ValidationAgent:
    """
    Pattern enforcement and code quality validation.

    Features:
    - Resume content validation
    - Quality pattern checks
    - ATS compatibility validation
    - Metric verification
    """

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx
        self._issues: List[ValidationIssue] = []

    def validate_resume(self, resume: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate a resume for quality issues.

        Args:
            resume: Resume dictionary

        Returns:
            List of validation issues
        """
        self._issues.clear()

        # Check summary
        if "summary" in resume:
            self._validate_summary(resume["summary"])

        # Check experience
        if "experience" in resume:
            self._validate_experience(resume["experience"])

        # Check skills
        if "skills" in resume:
            self._validate_skills(resume["skills"])

        return self._issues

    def _validate_summary(self, summary: str):
        """Validate resume summary."""
        if not summary:
            self._add_issue(
                "SUMMARY_EMPTY",
                ValidationSeverity.ERROR,
                "summary",
                None,
                "Summary is empty",
                "Add a compelling professional summary",
            )
            return

        # Check length
        if len(summary) < 50:
            self._add_issue(
                "SUMMARY_TOO_SHORT",
                ValidationSeverity.WARNING,
                "summary",
                None,
                f"Summary is too short ({len(summary)} chars)",
                "Expand summary to at least 100 characters",
            )

        # Check for metrics
        if not re.search(r"\d+[%+]?", summary):
            self._add_issue(
                "SUMMARY_NO_METRICS",
                ValidationSeverity.WARNING,
                "summary",
                None,
                "Summary lacks quantified achievements",
                "Add specific metrics (e.g., 'increased revenue by 25%')",
            )

        # Check for weak words
        weak_words = ["helped", "assisted", "worked on", "responsible for"]
        for word in weak_words:
            if word.lower() in summary.lower():
                self._add_issue(
                    "SUMMARY_WEAK_LANGUAGE",
                    ValidationSeverity.INFO,
                    "summary",
                    None,
                    f"Summary contains weak language: '{word}'",
                    "Use stronger action verbs (e.g., 'led', 'delivered', 'achieved')",
                )

    def _validate_experience(self, experience: List[Dict[str, Any]]):
        """Validate experience section."""
        if not experience:
            self._add_issue(
                "EXPERIENCE_EMPTY",
                ValidationSeverity.ERROR,
                "experience",
                None,
                "Experience section is empty",
                "Add work experience entries",
            )
            return

        for i, exp in enumerate(experience):
            # Check required fields
            if not exp.get("company"):
                self._add_issue(
                    "EXPERIENCE_NO_COMPANY",
                    ValidationSeverity.ERROR,
                    "experience",
                    i,
                    f"Experience entry {i+1} Missing company name",
                    "Add company name",
                )

            if not exp.get("title"):
                self._add_issue(
                    "EXPERIENCE_NO_TITLE",
                    ValidationSeverity.ERROR,
                    "experience",
                    i,
                    f"Experience entry {i+1} Missing job title",
                    "Add job title",
                )

            # Check description
            desc = exp.get("description", "")
            if desc and not re.search(r"\d+", desc):
                self._add_issue(
                    "EXPERIENCE_NO_METRICS",
                    ValidationSeverity.WARNING,
                    "experience",
                    i,
                    f"Experience entry {i+1} lacks metrics",
                    "Add quantified achievements",
                )

    def _validate_skills(self, skills: List[str]):
        """Validate skills section."""
        if not skills:
            self._add_issue(
                "SKILLS_EMPTY",
                ValidationSeverity.WARNING,
                "skills",
                None,
                "Skills section is empty",
                "Add relevant skills",
            )
            return

        if len(skills) < 5:
            self._add_issue(
                "SKILLS_TOO_FEW",
                ValidationSeverity.INFO,
                "skills",
                None,
                f"Only {len(skills)} skills listed",
                "Consider adding more relevant skills",
            )

    def _add_issue(
        self,
        rule_id: str,
        Severity: ValidationSeverity,
        file_path: str,
        line_number: Optional[int],
        message: str,
        suggestion: Optional[str] = None,
    ):
        """Add a validation issue."""
        self._issues.append(ValidationIssue(
            rule_id=rule_id,
            Severity=Severity,
            file_path=file_path,
            line_number=line_number,
            message=message,
            suggestion=suggestion,
        ))

    def get_issues(self) -> List[ValidationIssue]:
        """Get all validation issues."""
        return self._issues

    def get_issues_by_severity(self, Severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by Severity."""
        return [i for i in self._issues if i.Severity == Severity]

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "total_issues": len(self._issues),
            "by_severity": {
                s.value: sum(1 for i in self._issues if i.Severity == s)
                for s in ValidationSeverity
            },
        }


class AuditReporter:
    """
    Generates comprehensive audit reports.

    Features:
    - Mission summary
    - Execution traces
    - Metrics aggregation
    - Validation issues
    - Recommendations
    """

    def __init__(
        self,
        ctx: ResumeEngineContext,
        tracer: ExecutionTracer,
        metrics: MetricsCollector,
        validator: ValidationAgent,
    ):
        self.ctx = ctx
        self.tracer = tracer
        self.metrics = metrics
        self.validator = validator
        self._reports: List[AuditReport] = []

    def generate_report(self, mission_id: str) -> AuditReport:
        """
        Generate a comprehensive audit report.

        Args:
            mission_id: ID of the mission

        Returns:
            AuditReport
        """
        report_id = hashlib.sha256(
            f"{mission_id}_{time.time()}".encode()
        ).hexdigest()[:16]

        # Gather data
        traces = self.tracer.get_all_traces()
        all_metrics = self.metrics.get_metrics()
        issues = self.validator.get_issues()

        # Generate summary
        summary = self._generate_summary(traces, all_metrics, issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(traces, issues)

        report = AuditReport(
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            mission_id=mission_id,
            summary=summary,
            traces=traces,
            metrics=all_metrics,
            validation_issues=issues,
            recommendations=recommendations,
        )

        self._reports.append(report)

        return report

    def _generate_summary(
        self,
        traces: List[ExecutionTrace],
        metrics: List[Metric],
        issues: List[ValidationIssue],
    ) -> Dict[str, Any]:
        """Generate report summary."""
        total_duration = sum(
            t.total_duration_ms or 0 for t in traces
        )

        return {
            "total_traces": len(traces),
            "successful_traces": sum(1 for t in traces if t.success),
            "total_steps": sum(len(t.steps) for t in traces),
            "total_duration_ms": total_duration,
            "total_metrics": len(metrics),
            "total_issues": len(issues),
            "critical_issues": sum(
                1 for i in issues if i.Severity == ValidationSeverity.CRITICAL
            ),
            "error_issues": sum(
                1 for i in issues if i.Severity == ValidationSeverity.ERROR
            ),
        }

    def _generate_recommendations(
        self,
        traces: List[ExecutionTrace],
        issues: List[ValidationIssue],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for failed traces
        failed = [t for t in traces if not t.success]
        if failed:
            recommendations.append(
                f"Review {len(failed)} failed execution(s) for root cause analysis"
            )

        # Check for critical issues
        critical = [i for i in issues if i.Severity == ValidationSeverity.CRITICAL]
        if critical:
            recommendations.append(
                f"Address {len(critical)} critical issue(s) immediately"
            )

        # Check for slow steps
        slow_steps = []
        for trace in traces:
            for step in trace.steps:
                if step.duration_ms and step.duration_ms > 5000:
                    slow_steps.append(step)

        if slow_steps:
            recommendations.append(
                f"Optimize {len(slow_steps)} slow step(s) taking >5s"
            )

        # Check for Missing metrics
        if not [i for i in issues if "METRICS" in i.rule_id]:
            pass  # Metrics present
        else:
            recommendations.append(
                "Add quantified achievements to improve ATS compatibility"
            )

        if not recommendations:
            recommendations.append("No immediate actions required")

        return recommendations

    def export_report(
        self,
        report: AuditReport,
        output_path: Optional[str] = None,
        format: str = "json",
    ) -> str:
        """
        Export a report to file.

        Args:
            report: Report to export
            output_path: Output file path
            format: Output format (json, markdown)

        Returns:
            Path to exported file
        """
        if not output_path:
            output_path = f"audit_report_{report.report_id}.{format}"

        if format == "json":
            content = self._to_json(report)
        else:
            content = self._to_markdown(report)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content)

        return output_path

    def _to_json(self, report: AuditReport) -> str:
        """Convert report to JSON."""
        def serialize(obj, seen=None):
            if seen is None:
                seen = set()

            obj_id = id(obj)
            if obj_id in seen:
                return "<circular>"

            if hasattr(obj, "__dict__"):
                seen.add(obj_id)
                result = {}
                for k, v in obj.__dict__.items():
                    # Skip context objects to avoid circular refs
                    if k in ("ctx", "context", "_client", "client"):
                        continue
                    result[k] = serialize(v, seen)
                return result
            elif isinstance(obj, list):
                return [serialize(i, seen) for i in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v, seen) for k, v in obj.items()}
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                return str(obj)

        return json.dumps(serialize(report), indent=2)

    def _to_markdown(self, report: AuditReport) -> str:
        """Convert report to Markdown."""
        lines = [
            f"# Audit Report: {report.report_id}",
            f"\nGenerated: {report.generated_at}",
            f"\nMission: {report.mission_id}",
            "\n## Summary\n",
        ]

        for key, value in report.summary.items():
            lines.append(f"- **{key}**: {value}")

        lines.append("\n## Recommendations\n")
        for rec in report.recommendations:
            lines.append(f"- {rec}")

        if report.validation_issues:
            lines.append("\n## Validation Issues\n")
            for issue in report.validation_issues:
                lines.append(f"- [{issue.Severity.value.upper()}] {issue.message}")

        return "\n".join(lines)

    def get_reports(self) -> List[AuditReport]:
        """Get all generated reports."""
        return self._reports

    def get_stats(self) -> Dict[str, Any]:
        """Get reporter statistics."""
        return {
            "total_reports": len(self._reports),
        }


class TelemetryExporter:
    """
    Exports telemetry data for external systems.

    Features:
    - JSON export
    - OpenTelemetry format
    - Custom exporters
    """

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx
        self._export_count = 0

    def export_traces(
        self,
        traces: List[ExecutionTrace],
        format: str = "json",
    ) -> str:
        """Export traces to string format."""
        if format == "json":
            return self._traces_to_json(traces)
        elif format == "otlp":
            return self._traces_to_otlp(traces)
        return ""

    def export_metrics(
        self,
        metrics: List[Metric],
        format: str = "json",
    ) -> str:
        """Export metrics to string format."""
        if format == "json":
            return self._metrics_to_json(metrics)
        elif format == "prometheus":
            return self._metrics_to_prometheus(metrics)
        return ""

    def _traces_to_json(self, traces: List[ExecutionTrace]) -> str:
        """Convert traces to JSON."""
        def serialize(obj):
            if hasattr(obj, "__dict__"):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif isinstance(obj, Enum):
                return obj.value
            return obj

        self._export_count += 1
        return json.dumps([serialize(t) for t in traces], indent=2)

    def _traces_to_otlp(self, traces: List[ExecutionTrace]) -> str:
        """Convert traces to OpenTelemetry format."""
        otlp_traces = []

        for trace in traces:
            otlp_trace = {
                "traceId": trace.trace_id,
                "spans": [],
            }

            for step in trace.steps:
                Span = {
                    "spanId": step.step_id,
                    "name": f"{step.agent_name}.{step.action}",
                    "startTimeUnixNano": int(step.start_time * 1e9),
                    "endTimeUnixNano": int((step.end_time or step.start_time) * 1e9),
                    "status": {"code": 1 if step.success else 2},
                }
                otlp_trace["spans"].append(Span)

            otlp_traces.append(otlp_trace)

        self._export_count += 1
        return json.dumps({"resourceSpans": otlp_traces}, indent=2)

    def _metrics_to_json(self, metrics: List[Metric]) -> str:
        """Convert metrics to JSON."""
        def serialize(m):
            return {
                "name": m.name,
                "value": m.value,
                "type": m.metric_type.value,
                "timestamp": m.timestamp,
                "tags": m.tags,
            }

        self._export_count += 1
        return json.dumps([serialize(m) for m in metrics], indent=2)

    def _metrics_to_prometheus(self, metrics: List[Metric]) -> str:
        """Convert metrics to Prometheus format."""
        lines = []

        for Metric in metrics:
            tags_str = ",".join(f'{k}="{v}"' for k, v in Metric.tags.items())
            if tags_str:
                lines.append(f"{Metric.name}{{{tags_str}}} {Metric.value}")
            else:
                lines.append(f"{Metric.name} {Metric.value}")

        self._export_count += 1
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get exporter statistics."""
        return {
            "export_count": self._export_count,
        }


class Phase5Orchestrator:
    """
    Orchestrates all Phase 5 observability components.

    Combines:
    - Execution tracing
    - Metrics collection
    - Validation
    - Audit reporting
    - Telemetry export
    """

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx

        self.tracer = ExecutionTracer(ctx)
        self.metrics = MetricsCollector(ctx)
        self.validator = ValidationAgent(ctx)
        self.reporter = AuditReporter(ctx, self.tracer, self.metrics, self.validator)
        self.exporter = TelemetryExporter(ctx)

    def start_mission(self, mission_id: str) -> str:
        """Start observability for a mission."""
        trace_id = self.tracer.start_trace(mission_id)
        self.metrics.increment("missions.started")
        return trace_id

    def end_mission(self, success: bool = True) -> Optional[ExecutionTrace]:
        """End observability for a mission."""
        trace = self.tracer.end_trace(success)

        if success:
            self.metrics.increment("missions.succeeded")
        else:
            self.metrics.increment("missions.failed")

        return trace

    def track_agent(
        self,
        agent_name: str,
        action: str,
    ) -> str:
        """Start tracking an agent action."""
        step_id = self.tracer.start_step(agent_name, action)
        self.metrics.increment("agents.invocations", tags={"agent": agent_name})
        return step_id

    def complete_agent(
        self,
        step_id: str,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Complete tracking an agent action."""
        self.tracer.end_step(step_id, success, error)

        if not success:
            self.metrics.increment("agents.failures")

    def validate_resume(self, resume: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate a resume."""
        issues = self.validator.validate_resume(resume)
        self.metrics.gauge("validation.issues", len(issues))
        return issues

    def generate_report(self, mission_id: str) -> AuditReport:
        """Generate an audit report."""
        return self.reporter.generate_report(mission_id)

    def export_telemetry(self, format: str = "json") -> Dict[str, str]:
        """Export all telemetry data."""
        traces = self.tracer.get_all_traces()
        metrics = self.metrics.get_metrics()

        return {
            "traces": self.exporter.export_traces(traces, format),
            "metrics": self.exporter.export_metrics(metrics, format),
        }

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            "tracer": self.tracer.get_stats(),
            "metrics": self.metrics.get_stats(),
            "validator": self.validator.get_stats(),
            "reporter": self.reporter.get_stats(),
            "exporter": self.exporter.get_stats(),
        }
