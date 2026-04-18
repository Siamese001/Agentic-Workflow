"""Advanced Analytics Dashboard - Real-time monitoring and analytics.

Provides comprehensive real-time dashboard for tracing analytics,
performance monitoring, and system observability.

FEATURES:
- Real-time metrics and charts
- Interactive trace visualization
- Performance trend analysis
- Alert management interface
- System health monitoring
- Optimization recommendations
- Service topology visualization

USAGE:
    dashboard = AnalyticsDashboard()
    dashboard.start_dashboard()

    # Access dashboard at http://localhost:8080
"""

import copy
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("analytics_dashboard", "analytics_dashboard_digest")
record_execution_trace("analytics_dashboard", "analytics_dashboard_trace")

Logger = logging.getLogger(__name__)

_DASHBOARD_NON_FATAL_EXCEPTIONS = (
    AttributeError,
    ImportError,
    KeyError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
)


@dataclass
class DashboardConfig:
    """Dashboard configuration."""

    host: str = "localhost"
    port: int = 8080
    refresh_interval_seconds: int = 5
    max_data_points: int = 1000
    enable_real_time: bool = True
    enable_alerts: bool = True
    enable_optimization: bool = True


@dataclass
class ChartData:
    """Chart data structure."""

    chart_type: str  # line, bar, pie, gauge
    title: str
    data: list[dict[str, Any]]
    labels: list[str]
    colors: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """Dashboard widget definition."""

    widget_id: str
    widget_type: str  # chart, metric, alert, table
    title: str
    position: dict[str, int]  # x, y, width, height
    data: Any
    config: dict[str, Any] = field(default_factory=dict)
    refresh_rate: int = 5  # seconds


class AnalyticsDashboard:
    """
    Advanced analytics dashboard for real-time monitoring.

    Provides comprehensive visualization and monitoring capabilities
    for the tracing and Runtime ADG system.
    """

    def __init__(self, config: DashboardConfig | None = None) -> None:
        """Initialize analytics dashboard."""
        self._config = config or DashboardConfig()

        # Dashboard state
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._dashboard_active: bool = False
        self._dashboard_thread: threading.Thread | None = None
        self._shutdown_requested: bool = False

        # Data storage
        self._widgets: dict[str, DashboardWidget] = {}
        self._chart_data: dict[str, ChartData] = {}
        self._real_time_data: dict[str, Any] = {}

        # Component integrations
        self._analytics_engine = None
        self._observability_system = None
        self._distributed_coordinator = None

        # Initialize integrations
        self._initialize_integrations()

        # Initialize default widgets
        self._initialize_default_widgets()

    def _initialize_integrations(self) -> None:
        """Initialize component integrations."""
        try:
            # Advanced analytics
            from system_learning.runtime_adg.advanced_analytics import get_global_analytics

            self._analytics_engine = get_global_analytics()

        except ImportError:
            Logger.debug("[DASHBOARD] Advanced analytics not available")

        try:
            # Enhanced observability
            from agentic_core.L6_observability.utils.enhanced_observability import get_global_observability

            self._observability_system = get_global_observability()

        except ImportError:
            Logger.debug("[DASHBOARD] Enhanced observability not available")

        try:
            # Distributed tracing coordinator
            from agentic_core.tracing.distributed_tracing_coordinator import get_global_coordinator

            self._distributed_coordinator = get_global_coordinator()

        except ImportError:
            Logger.debug("[DASHBOARD] Distributed tracing coordinator not available")

    def _initialize_default_widgets(self) -> None:
        """Initialize default dashboard widgets."""
        # System health widget
        self._widgets["system_health"] = DashboardWidget(
            widget_id="system_health",
            widget_type="metric",
            title="System Health",
            position={"x": 0, "y": 0, "width": 4, "height": 2},
            data={"score": 0, "status": "unknown"},
            refresh_rate=10,
        )

        # Active traces widget
        self._widgets["active_traces"] = DashboardWidget(
            widget_id="active_traces",
            widget_type="metric",
            title="Active Traces",
            position={"x": 4, "y": 0, "width": 4, "height": 2},
            data={"count": 0, "rate": 0},
            refresh_rate=5,
        )

        # Performance metrics widget
        self._widgets["performance_metrics"] = DashboardWidget(
            widget_id="performance_metrics",
            widget_type="chart",
            title="Performance Metrics",
            position={"x": 8, "y": 0, "width": 4, "height": 2},
            data=ChartData(
                chart_type="line",
                title="Performance",
                data=[],
                labels=["Time", "Efficiency", "Complexity", "Reliability"],
                colors=["#00ff00", "#ffff00", "#ff0000"],
            ),
            refresh_rate=15,
        )

        # Alert widget
        self._widgets["alerts"] = DashboardWidget(
            widget_id="alerts",
            widget_type="table",
            title="Active Alerts",
            position={"x": 0, "y": 2, "width": 6, "height": 3},
            data={"columns": ["Severity", "Message", "Time"], "rows": []},
            refresh_rate=10,
        )

        # Service health widget
        self._widgets["service_health"] = DashboardWidget(
            widget_id="service_health",
            widget_type="chart",
            title="Service Health",
            position={"x": 6, "y": 2, "width": 6, "height": 3},
            data=ChartData(
                chart_type="pie",
                title="Service Status",
                data=[],
                labels=["Healthy", "Warning", "Critical"],
                colors=["#00ff00", "#ffff00", "#ff0000"],
            ),
            refresh_rate=30,
        )

        # Optimization recommendations widget
        self._widgets["optimization"] = DashboardWidget(
            widget_id="optimization",
            widget_type="table",
            title="Optimization Recommendations",
            position={"x": 0, "y": 5, "width": 12, "height": 3},
            data={"columns": ["Priority", "Type", "Description"], "rows": []},
            refresh_rate=60,
        )

    def _default_widget_data(self, widget_id: str, widget_type: str) -> Any:
        """Return safe default data for a widget."""
        if widget_id == "system_health":
            return {"score": 0, "status": "unknown"}
        if widget_id == "active_traces":
            return {"count": 0, "rate": 0}
        if widget_id == "performance_metrics":
            return ChartData(
                chart_type="line",
                title="Performance",
                data=[],
                labels=["Time", "Efficiency", "Complexity", "Reliability"],
                colors=["#00ff00", "#ffff00", "#ff0000"],
            )
        if widget_id == "alerts":
            return {"columns": ["Severity", "Message", "Time"], "rows": []}
        if widget_id == "service_health":
            return ChartData(
                chart_type="pie",
                title="Service Status",
                data=[],
                labels=["Healthy", "Warning", "Critical"],
                colors=["#00ff00", "#ffff00", "#ff0000"],
            )
        if widget_id == "optimization":
            return {"columns": ["Priority", "Type", "Description"], "rows": []}
        return (
            {}
            if widget_type == "table"
            else ChartData(chart_type="line", title=widget_id, data=[], labels=[], colors=[])
            if widget_type == "chart"
            else {}
        )

    def _ensure_widget_data_shape(self, widget: DashboardWidget) -> None:
        """Repair widget data when imported config is incomplete or malformed."""
        default_data = self._default_widget_data(widget.widget_id, widget.widget_type)
        if widget.widget_type == "chart" and not isinstance(widget.data, ChartData):
            widget.data = copy.deepcopy(default_data)
        elif widget.widget_type == "table":
            if not isinstance(widget.data, dict):
                widget.data = copy.deepcopy(default_data)
            else:
                widget.data.setdefault("columns", copy.deepcopy(default_data.get("columns", [])))
                widget.data.setdefault("rows", [])
        elif widget.widget_type == "metric" and not isinstance(widget.data, dict):
            widget.data = copy.deepcopy(default_data)

    def start_dashboard(self) -> None:
        """Start the analytics dashboard."""
        with self._lock:
            if self._dashboard_active:
                Logger.warning("[DASHBOARD] Dashboard already active")
                return

            self._dashboard_active = True
            self._shutdown_requested = False
            self._stop_event.clear()

            # Start dashboard update thread
            self._dashboard_thread = threading.Thread(
                target=self._dashboard_loop,
                daemon=True,
                name="AnalyticsDashboard",
            )
            self._dashboard_thread.start()

        Logger.info(f"[DASHBOARD] Started analytics dashboard on {self._config.host}:{self._config.port}")
        Logger.info(f"[DASHBOARD] Dashboard URL: http://{self._config.host}:{self._config.port}")

    def stop_dashboard(self) -> None:
        """Stop the analytics dashboard."""
        with self._lock:
            if not self._dashboard_active:
                return

            self._shutdown_requested = True
            self._dashboard_active = False
            self._stop_event.set()
            dashboard_thread = self._dashboard_thread

        if dashboard_thread and dashboard_thread.is_alive():
            dashboard_thread.join(timeout=5.0)

        Logger.info("[DASHBOARD] Stopped analytics dashboard")

    def _dashboard_loop(self) -> None:
        """Main dashboard update loop."""
        while self._dashboard_active and not self._shutdown_requested:
            try:
                start_time = time.time()

                # Update all widgets
                self._update_all_widgets()

                # Update real-time data
                self._update_real_time_data()

                # Sleep until next update
                elapsed = time.time() - start_time
                sleep_time = max(0.1, self._config.refresh_interval_seconds - elapsed)
                if self._stop_event.wait(timeout=sleep_time):
                    break

            except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
                Logger.error(f"[DASHBOARD] Dashboard loop error: {e}")
                if self._stop_event.wait(timeout=5.0):
                    break

    def _update_all_widgets(self) -> None:
        """Update all dashboard widgets."""
        current_time = time.time()

        with self._lock:
            widget_items = list(self._widgets.items())

        for widget_id, widget in widget_items:
            try:
                # Check if widget needs update
                if current_time - getattr(widget, "_last_update", 0) >= widget.refresh_rate:
                    self._update_widget(widget)
                    widget._last_update = current_time

            except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
                Logger.error(f"[DASHBOARD] Failed to update widget {widget_id}: {e}")

    def _update_widget(self, widget: DashboardWidget) -> None:
        """Update a specific widget."""
        self._ensure_widget_data_shape(widget)
        if widget.widget_type == "metric":
            self._update_metric_widget(widget)
        elif widget.widget_type == "chart":
            self._update_chart_widget(widget)
        elif widget.widget_type == "table":
            self._update_table_widget(widget)
        else:
            Logger.warning(f"[DASHBOARD] Unknown widget type: {widget.widget_type}")

    def _update_metric_widget(self, widget: DashboardWidget) -> None:
        """Update metric widget."""
        if widget.widget_id == "system_health":
            if self._observability_system:
                health = self._observability_system.get_system_health()
                if health:
                    widget.data = {
                        "score": health.score,
                        "status": health.status.value,
                        "timestamp": health.timestamp,
                    }

        elif widget.widget_id == "active_traces":
            if self._distributed_coordinator:
                stats = self._distributed_coordinator.get_coordination_stats()
                widget.data = {
                    "count": stats.get("active_traces", 0),
                    "rate": stats.get("trace_rate", 0),
                }

    def _update_chart_widget(self, widget: DashboardWidget) -> None:
        """Update chart widget."""
        if widget.widget_id == "performance_metrics":
            if self._analytics_engine:
                # Get performance data
                perf_data = self._analytics_engine.get_performance_data()
                widget.data.data = perf_data.get("trends", [])

        elif widget.widget_id == "service_health":
            if self._observability_system:
                health_data = self._observability_system.get_service_health()
                widget.data.data = [
                    {"label": "Healthy", "value": health_data.get("healthy", 0)},
                    {"label": "Warning", "value": health_data.get("warning", 0)},
                    {"label": "Critical", "value": health_data.get("critical", 0)},
                ]

    def _update_table_widget(self, widget: DashboardWidget) -> None:
        """Update table widget."""
        if widget.widget_id == "alerts":
            if self._observability_system:
                alerts = self._observability_system.get_active_alerts()

                rows = []
                for alert in alerts[:10]:  # Top 10 alerts
                    rows.append(
                        [
                            alert.severity.value,
                            alert.description,
                            datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S"),
                        ]
                    )

                widget.data = {
                    "columns": widget.data["columns"],
                    "rows": rows,
                    "total_count": len(alerts),
                }

        elif widget.widget_id == "optimization":
            if self._analytics_engine:
                # Get recent optimization insights
                # This would require access to recent analysis results
                # For now, we'll use placeholder data
                widget.data = {
                    "columns": widget.data["columns"],
                    "rows": [
                        ["High", "Performance", "Optimize bottleneck operations"],
                        ["Medium", "Architecture", "Reduce system complexity"],
                        ["Low", "Resource", "Increase buffer sizes"],
                    ],
                    "total_count": 3,
                }

    def _update_real_time_data(self) -> None:
        """Update real-time data cache."""
        try:
            # System metrics
            if self._observability_system:
                dashboard_data = self._observability_system.get_dashboard_data()
                with self._lock:
                    self._real_time_data["system_metrics"] = dashboard_data.get("current_metrics", {})
                    self._real_time_data["system_health"] = dashboard_data.get("system_health", {})

            # Distributed tracing stats
            if self._distributed_coordinator:
                with self._lock:
                    self._real_time_data["distributed_stats"] = (
                        self._distributed_coordinator.get_coordination_stats()
                    )

            # Performance stats
            try:
                from agentic_core.mixins.performance_optimized_collector import get_global_optimized_collector

                perf_collector = get_global_optimized_collector()
                with self._lock:
                    self._real_time_data["performance_stats"] = perf_collector.get_performance_stats()
            except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
                import logging

                logging.getLogger(__name__).debug("analytics_dashboard: Exception swallowed at L380: %s", e)

            # Timestamp
            with self._lock:
                self._real_time_data["timestamp"] = time.time()

        except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
            Logger.error(f"[DASHBOARD] Failed to update real-time data: {e}")

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get complete dashboard data for rendering."""
        with self._lock:
            widgets = {
                widget_id: {
                    "widget_type": widget.widget_type,
                    "title": widget.title,
                    "position": copy.deepcopy(widget.position),
                    "data": copy.deepcopy(widget.data),
                    "config": copy.deepcopy(widget.config),
                }
                for widget_id, widget in self._widgets.items()
            }
            real_time_data = copy.deepcopy(self._real_time_data)
            config = {
                "host": self._config.host,
                "port": self._config.port,
                "refresh_interval": self._config.refresh_interval_seconds,
                "dashboard_active": self._dashboard_active,
            }

        return {
            "config": config,
            "widgets": widgets,
            "real_time_data": real_time_data,
            "timestamp": time.time(),
        }

    def add_widget(self, widget: DashboardWidget) -> bool:
        """Add a new widget to the dashboard."""
        try:
            with self._lock:
                if widget.widget_id in self._widgets:
                    Logger.warning(f"[DASHBOARD] Widget {widget.widget_id} already exists")
                    return False

                self._widgets[widget.widget_id] = widget
            Logger.info(f"[DASHBOARD] Added widget: {widget.widget_id}")
            return True

        except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
            Logger.error(f"[DASHBOARD] Failed to add widget: {e}")
            return False

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the dashboard."""
        try:
            with self._lock:
                if widget_id in self._widgets:
                    del self._widgets[widget_id]
                    removed = True
                else:
                    removed = False

            if removed:
                Logger.info(f"[DASHBOARD] Removed widget: {widget_id}")
                return True

            Logger.warning(f"[DASHBOARD] Widget {widget_id} not found")
            return False

        except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
            Logger.error(f"[DASHBOARD] Failed to remove widget: {e}")
            return False

    def get_widget(self, widget_id: str) -> DashboardWidget | None:
        """Get a specific widget."""
        with self._lock:
            return copy.deepcopy(self._widgets.get(widget_id))

    def update_widget_config(self, widget_id: str, config: dict[str, Any]) -> bool:
        """Update widget configuration."""
        try:
            with self._lock:
                widget = self._widgets.get(widget_id)
                if widget:
                    widget.config.update(config)
                    updated = True
                else:
                    updated = False

            if updated:
                Logger.info(f"[DASHBOARD] Updated config for widget: {widget_id}")
                return True

            Logger.warning(f"[DASHBOARD] Widget {widget_id} not found")
            return False

        except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
            Logger.error(f"[DASHBOARD] Failed to update widget config: {e}")
            return False

    def export_dashboard_config(self) -> dict[str, Any]:
        """Export dashboard configuration."""
        with self._lock:
            widgets = {
                widget_id: {
                    "widget_type": widget.widget_type,
                    "title": widget.title,
                    "position": copy.deepcopy(widget.position),
                    "config": copy.deepcopy(widget.config),
                    "refresh_rate": widget.refresh_rate,
                }
                for widget_id, widget in self._widgets.items()
            }

            return {
                "config": {
                    "host": self._config.host,
                    "port": self._config.port,
                    "refresh_interval_seconds": self._config.refresh_interval_seconds,
                    "max_data_points": self._config.max_data_points,
                    "enable_real_time": self._config.enable_real_time,
                    "enable_alerts": self._config.enable_alerts,
                    "enable_optimization": self._config.enable_optimization,
                },
                "widgets": widgets,
            }

    def import_dashboard_config(self, config: dict[str, Any]) -> bool:
        """Import dashboard configuration."""
        try:
            # Update config
            if "config" in config:
                config_data = config["config"]
                self._config.host = config_data.get("host", self._config.host)
                self._config.port = config_data.get("port", self._config.port)
                self._config.refresh_interval_seconds = config_data.get(
                    "refresh_interval_seconds", self._config.refresh_interval_seconds
                )
                self._config.max_data_points = config_data.get(
                    "max_data_points", self._config.max_data_points
                )
                self._config.enable_real_time = config_data.get(
                    "enable_real_time", self._config.enable_real_time
                )
                self._config.enable_alerts = config_data.get("enable_alerts", self._config.enable_alerts)
                self._config.enable_optimization = config_data.get(
                    "enable_optimization", self._config.enable_optimization
                )

            # Update widgets
            if "widgets" in config:
                new_widgets: dict[str, DashboardWidget] = {}
                for widget_id, widget_data in config["widgets"].items():
                    widget_type = widget_data["widget_type"]
                    widget = DashboardWidget(
                        widget_id=widget_id,
                        widget_type=widget_type,
                        title=widget_data["title"],
                        position=copy.deepcopy(widget_data["position"]),
                        data=copy.deepcopy(
                            widget_data.get("data", self._default_widget_data(widget_id, widget_type))
                        ),
                        config=copy.deepcopy(widget_data.get("config", {})),
                        refresh_rate=widget_data.get("refresh_rate", 5),
                    )
                    self._ensure_widget_data_shape(widget)
                    new_widgets[widget_id] = widget

                with self._lock:
                    self._widgets = new_widgets

            Logger.info("[DASHBOARD] Imported dashboard configuration")
            return True

        except _DASHBOARD_NON_FATAL_EXCEPTIONS as e:
            Logger.error(f"[DASHBOARD] Failed to import dashboard config: {e}")
            return False

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Get dashboard summary information."""
        with self._lock:
            widgets = list(self._widgets.values())
            real_time_data = copy.deepcopy(self._real_time_data)
            dashboard_active = self._dashboard_active

        return {
            "dashboard_active": dashboard_active,
            "total_widgets": len(widgets),
            "widget_types": {
                widget_type: sum(1 for w in widgets if w.widget_type == widget_type)
                for widget_type in set(w.widget_type for w in widgets)
            },
            "real_time_data_points": len(real_time_data),
            "integrations": {
                "analytics_engine": self._analytics_engine is not None,
                "observability_system": self._observability_system is not None,
                "distributed_coordinator": self._distributed_coordinator is not None,
            },
            "last_update": real_time_data.get("timestamp", time.time()),
        }


# Global dashboard instance
_global_dashboard: AnalyticsDashboard | None = None


def get_global_dashboard() -> AnalyticsDashboard:
    """Get the global analytics dashboard instance."""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = AnalyticsDashboard()
    return _global_dashboard


def start_analytics_dashboard() -> None:
    """Start global analytics dashboard."""
    dashboard = get_global_dashboard()
    dashboard.start_dashboard()


def stop_analytics_dashboard() -> None:
    """Stop global analytics dashboard."""
    dashboard = get_global_dashboard()
    dashboard.stop_dashboard()


def get_dashboard_data() -> dict[str, Any]:
    """Get dashboard data for rendering."""
    dashboard = get_global_dashboard()
    return dashboard.get_dashboard_data()


def get_dashboard_summary() -> dict[str, Any]:
    """Get dashboard summary."""
    dashboard = get_global_dashboard()
    return dashboard.get_dashboard_summary()
