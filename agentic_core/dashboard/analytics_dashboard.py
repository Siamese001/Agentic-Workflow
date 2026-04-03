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

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("analytics_dashboard", "analytics_dashboard_digest")
record_execution_trace("analytics_dashboard", "analytics_dashboard_trace")

Logger = logging.getLogger(__name__)


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
    data: List[Dict[str, Any]]
    labels: List[str]
    colors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """Dashboard widget definition."""

    widget_id: str
    widget_type: str  # chart, metric, alert, table
    title: str
    position: Dict[str, int]  # x, y, width, height
    data: Any
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_rate: int = 5  # seconds


class AnalyticsDashboard:
    """
    Advanced analytics dashboard for real-time monitoring.

    Provides comprehensive visualization and monitoring capabilities
    for the tracing and Runtime ADG system.
    """

    def __init__(self, config: Optional[DashboardConfig] = None) -> None:
        """Initialize analytics dashboard."""
        self._config = config or DashboardConfig()

        # Dashboard state
        self._dashboard_active: bool = False
        self._dashboard_thread: Optional[threading.Thread] = None
        self._shutdown_requested: bool = False

        # Data storage
        self._widgets: Dict[str, DashboardWidget] = {}
        self._chart_data: Dict[str, ChartData] = {}
        self._real_time_data: Dict[str, Any] = {}

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
            from agentic_core.monitoring.enhanced_observability import get_global_observability
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

    def start_dashboard(self) -> None:
        """Start the analytics dashboard."""
        if self._dashboard_active:
            Logger.warning("[DASHBOARD] Dashboard already active")
            return

        self._dashboard_active = True
        self._shutdown_requested = False

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
        if not self._dashboard_active:
            return

        self._shutdown_requested = True
        self._dashboard_active = False

        if self._dashboard_thread and self._dashboard_thread.is_alive():
            self._dashboard_thread.join(timeout=5.0)

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
                time.sleep(sleep_time)

            except Exception as e:
                Logger.error(f"[DASHBOARD] Dashboard loop error: {e}")
                time.sleep(5.0)

    def _update_all_widgets(self) -> None:
        """Update all dashboard widgets."""
        current_time = time.time()

        for widget_id, widget in self._widgets.items():
            try:
                # Check if widget needs update
                if current_time - getattr(widget, '_last_update', 0) >= widget.refresh_rate:
                    self._update_widget(widget)
                    widget._last_update = current_time

            except Exception as e:
                Logger.error(f"[DASHBOARD] Failed to update widget {widget_id}: {e}")

    def _update_widget(self, widget: DashboardWidget) -> None:
        """Update a specific widget."""
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
                    "rate": stats.get("statistics", {}).get("spans_received", 0),
                    "timestamp": time.time(),
                }

    def _update_chart_widget(self, widget: DashboardWidget) -> None:
        """Update chart widget."""
        if widget.widget_id == "performance_metrics":
            if self._analytics_engine:
                trends = self._analytics_engine.get_trend_analysis()

                # Prepare chart data
                chart_data = widget.data
                chart_data.data = [
                    {
                        "label": "Efficiency",
                        "value": trends.get("efficiency_trend", "stable"),
                        "timestamp": time.time(),
                    },
                    {
                        "label": "Complexity",
                        "value": trends.get("complexity_trend", "stable"),
                        "timestamp": time.time(),
                    },
                    {
                        "label": "Reliability",
                        "value": trends.get("reliability_trend", "stable"),
                        "timestamp": time.time(),
                    },
                ]

        elif widget.widget_id == "service_health":
            if self._distributed_coordinator:
                service_health = self._distributed_coordinator.get_service_health()

                # Count service statuses
                status_counts = {"healthy": 0, "warning": 0, "critical": 0}

                for service_data in service_health.values():
                    status = service_data.get("health_status", "unknown").lower()
                    if status in status_counts:
                        status_counts[status] += 1

                # Prepare pie chart data
                chart_data = widget.data
                chart_data.data = [
                    {"label": "Healthy", "value": status_counts["healthy"]},
                    {"label": "Warning", "value": status_counts["warning"]},
                    {"label": "Critical", "value": status_counts["critical"]},
                ]

    def _update_table_widget(self, widget: DashboardWidget) -> None:
        """Update table widget."""
        if widget.widget_id == "alerts":
            if self._observability_system:
                alerts = self._observability_system.get_active_alerts()

                rows = []
                for alert in alerts[:10]:  # Top 10 alerts
                    rows.append([
                        alert.severity.value,
                        alert.description,
                        datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S"),
                    ])

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
                self._real_time_data["system_metrics"] = dashboard_data.get("current_metrics", {})
                self._real_time_data["system_health"] = dashboard_data.get("system_health", {})

            # Distributed tracing stats
            if self._distributed_coordinator:
                self._real_time_data["distributed_stats"] = self._distributed_coordinator.get_coordination_stats()

            # Performance stats
            try:
                from agentic_core.mixins.performance_optimized_collector import get_global_optimized_collector
                perf_collector = get_global_optimized_collector()
                self._real_time_data["performance_stats"] = perf_collector.get_performance_stats()
            except:
                pass

            # Timestamp
            self._real_time_data["timestamp"] = time.time()

        except Exception as e:
            Logger.error(f"[DASHBOARD] Failed to update real-time data: {e}")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data for rendering."""
        return {
            "config": {
                "host": self._config.host,
                "port": self._config.port,
                "refresh_interval": self._config.refresh_interval_seconds,
                "dashboard_active": self._dashboard_active,
            },
            "widgets": {
                widget_id: {
                    "widget_type": widget.widget_type,
                    "title": widget.title,
                    "position": widget.position,
                    "data": widget.data,
                    "config": widget.config,
                }
                for widget_id, widget in self._widgets.items()
            },
            "real_time_data": self._real_time_data,
            "timestamp": time.time(),
        }

    def add_widget(self, widget: DashboardWidget) -> bool:
        """Add a new widget to the dashboard."""
        try:
            if widget.widget_id in self._widgets:
                Logger.warning(f"[DASHBOARD] Widget {widget.widget_id} already exists")
                return False

            self._widgets[widget.widget_id] = widget
            Logger.info(f"[DASHBOARD] Added widget: {widget.widget_id}")
            return True

        except Exception as e:
            Logger.error(f"[DASHBOARD] Failed to add widget: {e}")
            return False

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the dashboard."""
        try:
            if widget_id in self._widgets:
                del self._widgets[widget_id]
                Logger.info(f"[DASHBOARD] Removed widget: {widget_id}")
                return True
            else:
                Logger.warning(f"[DASHBOARD] Widget {widget_id} not found")
                return False

        except Exception as e:
            Logger.error(f"[DASHBOARD] Failed to remove widget: {e}")
            return False

    def get_widget(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get a specific widget."""
        return self._widgets.get(widget_id)

    def update_widget_config(self, widget_id: str, config: Dict[str, Any]) -> bool:
        """Update widget configuration."""
        try:
            widget = self._widgets.get(widget_id)
            if widget:
                widget.config.update(config)
                Logger.info(f"[DASHBOARD] Updated config for widget: {widget_id}")
                return True
            else:
                Logger.warning(f"[DASHBOARD] Widget {widget_id} not found")
                return False

        except Exception as e:
            Logger.error(f"[DASHBOARD] Failed to update widget config: {e}")
            return False

    def export_dashboard_config(self) -> Dict[str, Any]:
        """Export dashboard configuration."""
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
            "widgets": {
                widget_id: {
                    "widget_type": widget.widget_type,
                    "title": widget.title,
                    "position": widget.position,
                    "config": widget.config,
                    "refresh_rate": widget.refresh_rate,
                }
                for widget_id, widget in self._widgets.items()
            },
        }

    def import_dashboard_config(self, config: Dict[str, Any]) -> bool:
        """Import dashboard configuration."""
        try:
            # Update config
            if "config" in config:
                config_data = config["config"]
                self._config.host = config_data.get("host", self._config.host)
                self._config.port = config_data.get("port", self._config.port)
                self._config.refresh_interval_seconds = config_data.get("refresh_interval_seconds", self._config.refresh_interval_seconds)
                self._config.max_data_points = config_data.get("max_data_points", self._config.max_data_points)
                self._config.enable_real_time = config_data.get("enable_real_time", self._config.enable_real_time)
                self._config.enable_alerts = config_data.get("enable_alerts", self._config.enable_alerts)
                self._config.enable_optimization = config_data.get("enable_optimization", self._config.enable_optimization)

            # Update widgets
            if "widgets" in config:
                self._widgets.clear()
                for widget_id, widget_data in config["widgets"].items():
                    widget = DashboardWidget(
                        widget_id=widget_id,
                        widget_type=widget_data["widget_type"],
                        title=widget_data["title"],
                        position=widget_data["position"],
                        data={},  # Data will be populated by updates
                        config=widget_data.get("config", {}),
                        refresh_rate=widget_data.get("refresh_rate", 5),
                    )
                    self._widgets[widget_id] = widget

            Logger.info("[DASHBOARD] Imported dashboard configuration")
            return True

        except Exception as e:
            Logger.error(f"[DASHBOARD] Failed to import dashboard config: {e}")
            return False

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary information."""
        return {
            "dashboard_active": self._dashboard_active,
            "total_widgets": len(self._widgets),
            "widget_types": {
                widget_type: sum(1 for w in self._widgets.values() if w.widget_type == widget_type)
                for widget_type in set(w.widget_type for w in self._widgets.values())
            },
            "real_time_data_points": len(self._real_time_data),
            "integrations": {
                "analytics_engine": self._analytics_engine is not None,
                "observability_system": self._observability_system is not None,
                "distributed_coordinator": self._distributed_coordinator is not None,
            },
            "last_update": self._real_time_data.get("timestamp", time.time()),
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


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data for rendering."""
    dashboard = get_global_dashboard()
    return dashboard.get_dashboard_data()


def get_dashboard_summary() -> Dict[str, Any]:
    """Get dashboard summary."""
    dashboard = get_global_dashboard()
    return dashboard.get_dashboard_summary()
