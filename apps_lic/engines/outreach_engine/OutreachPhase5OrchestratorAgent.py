from __future__ import annotations
"""
Outreach Engine Observability Module

Provides comprehensive observability:
- Execution tracing
- Metrics collection
- Audit reporting
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto
import time


from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .context import OutreachEngineContext
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


class OutreachTraceLevel(Enum):
    """Trace levels for observability."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OutreachMetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class OutreachTraceStep:
    """A single step in an execution trace."""
    step_id: str
    agent_name: str
    action: str
    level: OutreachTraceLevel
    duration_ms: float
    success: bool
    details: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachExecutionTrace:
    """Complete execution trace for a mission."""
    trace_id: str
    mission_name: str
    steps: List[OutreachTraceStep]
    start_time: str
    end_time: Optional[str]
    success: bool
    total_duration_ms: float


@dataclass
class OutreachMetric:
    """A single Metric measurement."""
    name: str
    metric_type: OutreachMetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OutreachExecutionTracer:
    """
    Traces execution of outreach operations.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        self.ctx = ctx
        self._traces: Dict[str, OutreachExecutionTrace] = {}
        self._current_trace: Optional[str] = None
        self._step_counter = 0

    def start_trace(self, mission_name: str) -> str:
        """Start a new execution trace."""
        import uuid
        trace_id = str(uuid.uuid4())[:8]

        self._traces[trace_id] = OutreachExecutionTrace(
            trace_id=trace_id,
            mission_name=mission_name,
            steps=[],
            start_time=datetime.now().isoformat(),
            end_time=None,
            success=False,
            total_duration_ms=0,
        )

        self._current_trace = trace_id
        return trace_id

    def add_step(
        self,
        agent_name: str,
        action: str,
        level: OutreachTraceLevel = OutreachTraceLevel.INFO,
        duration_ms: float = 0,
        success: bool = True,
        details: str = "",
    ) -> str:
        """Add a step to the current trace."""
        if not self._current_trace:
            return ""

        self._step_counter += 1
        step_id = f"step_{self._step_counter}"

        step = OutreachTraceStep(
            step_id=step_id,
            agent_name=agent_name,
            action=action,
            level=level,
            duration_ms=duration_ms,
            success=success,
            details=details,
        )

        self._traces[self._current_trace].steps.append(step)
        return step_id

    def end_trace(self, success: bool = True) -> Optional[OutreachExecutionTrace]:
        """End the current trace."""
        if not self._current_trace:
            return None

        trace = self._traces[self._current_trace]
        trace.end_time = datetime.now().isoformat()
        trace.success = success

        # Calculate total duration
        if trace.steps:
            trace.total_duration_ms = sum(s.duration_ms for s in trace.steps)

        self._current_trace = None
        return trace

    def get_trace(self, trace_id: str) -> Optional[OutreachExecutionTrace]:
        """Get a trace by ID."""
        return self._traces.get(trace_id)

    def get_all_traces(self) -> List[OutreachExecutionTrace]:
        """Get all traces."""
        return list(self._traces.values())


class OutreachMetricsCollector:
    """
    Collects metrics for outreach operations.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        self.ctx = ctx
        self._metrics: List[OutreachMetric] = []
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}

    def counter(self, name: str, value: float = 1, labels: Dict[str, str] = None) -> Any:
        """Increment a counter Metric."""
        self._counters[name] = self._counters.get(name, 0) + value

        self._metrics.append(OutreachMetric(
            name=name,
            metric_type=OutreachMetricType.COUNTER,
            value=self._counters[name],
            labels=labels or {},
        ))

    def gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> Any:
        """Set a gauge Metric."""
        self._gauges[name] = value

        self._metrics.append(OutreachMetric(
            name=name,
            metric_type=OutreachMetricType.GAUGE,
            value=value,
            labels=labels or {},
        ))

    def timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None) -> Any:
        """Record a timer Metric."""
        self._metrics.append(OutreachMetric(
            name=name,
            metric_type=OutreachMetricType.TIMER,
            value=duration_ms,
            labels=labels or {},
        ))

    def get_counter(self, name: str) -> float:
        """Get a counter value."""
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float:
        """Get a gauge value."""
        return self._gauges.get(name, 0)

    def get_all_metrics(self) -> List[OutreachMetric]:
        """Get all metrics."""
        return self._metrics

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "total_metrics": len(self._metrics),
        }


class OutreachAuditReporter:
    """
    Generates audit reports for outreach operations.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        self.ctx = ctx
        self._reports: List[Dict[str, Any]] = []

    def generate_report(
        self,
        mission_name: str,
        trace: Optional[OutreachExecutionTrace] = None,
        metrics: Optional[List[OutreachMetric]] = None,
    ) -> Dict[str, Any]:
        """Generate an audit report."""
        report = {
            "mission_name": mission_name,
            "timestamp": datetime.now().isoformat(),
            "campaign": self.ctx.current_campaign,
            "leads_count": len(self.ctx.leads),
            "contacts_count": len(self.ctx.contacts),
            "messages_count": len(self.ctx.messages),
            "signals": list(self.ctx.signals),
            "results": self.ctx.results,
            "budget": {
                "current_cost": self.ctx.budget.current_cost,
                "remaining": self.ctx.budget.get_remaining(),
            },
        }

        if trace:
            report["trace"] = {
                "trace_id": trace.trace_id,
                "steps_count": len(trace.steps),
                "success": trace.success,
                "duration_ms": trace.total_duration_ms,
            }

        if metrics:
            report["metrics_count"] = len(metrics)

        self._reports.append(report)
        return report

    def get_reports(self) -> List[Dict[str, Any]]:
        """Get all reports."""
        return self._reports


class OutreachPhase5OrchestratorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Orchestrates Phase 5 observability for outreach.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        self.ctx = ctx
        self.tracer = OutreachExecutionTracer(ctx)
        self.metrics = OutreachMetricsCollector(ctx)
        self.reporter = OutreachAuditReporter(ctx)
        self._current_mission: Optional[str] = None

    def start_mission(self, mission_name: str) -> str:
        """Start observability for a mission."""
        self._current_mission = mission_name
        trace_id = self.tracer.start_trace(mission_name)
        self.metrics.counter("missions_started")
        return trace_id

    def track_agent(self, agent_name: str, action: str) -> str:
        """Track an agent execution."""
        step_id = self.tracer.add_step(agent_name, action)
        self.metrics.counter(f"agent_{agent_name}_executions")
        return step_id

    def complete_agent(self, step_id: str, success: bool = True, duration_ms: float = 0) -> Any:
        """Complete an agent execution."""
        if success:
            self.metrics.counter("agent_successes")
        else:
            self.metrics.counter("agent_failures")

        self.metrics.timer("agent_duration", duration_ms)

    def end_mission(self, success: bool = True) -> Optional[OutreachExecutionTrace]:
        """End observability for a mission."""
        trace = self.tracer.end_trace(success)

        if success:
            self.metrics.counter("missions_succeeded")
        else:
            self.metrics.counter("missions_failed")

        self._current_mission = None
        return trace

    def generate_report(self, mission_name: str = None) -> Dict[str, Any]:
        """Generate an audit report."""
        name = mission_name or self._current_mission or "unknown"

        # Get latest trace
        traces = self.tracer.get_all_traces()
        trace = traces[-1] if traces else None

        return self.reporter.generate_report(
            mission_name=name,
            trace=trace,
            metrics=self.metrics.get_all_metrics(),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "traces": len(self.tracer.get_all_traces()),
            "metrics": self.metrics.get_summary(),
            REPORTS_DIR: len(self.reporter.get_reports()),
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
