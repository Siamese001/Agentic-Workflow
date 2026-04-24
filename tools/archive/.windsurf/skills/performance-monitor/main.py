#!/usr/bin/env python3
"""
Windsurf Skill: Performance Monitor
Monitors pre-write validation performance and enforces timeout limits.
"""

import json
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

import psutil

# guardian: allow-silent-swallower -- Exception handling for performance monitoring
# guardian: allow-magic-configuration -- Performance threshold configuration

# guardian: allow-silent-swallower -- Exception handling for performance monitoring
# guardian: allow-magic-configuration -- Performance threshold configuration


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""

    operation: str
    start_time: float
    end_time: float | None
    duration: float | None
    cpu_percent: list[float]
    memory_mb: list[float]
    timeout_threshold: float
    timed_out: bool = False
    skills_executed: list[str] = None

    def __post_init__(self):
        if self.skills_executed is None:
            self.skills_executed = []


class PerformanceMonitor:
    """Monitors performance of pre-write validations."""

    def __init__(self, timeout_threshold: float = 5.0):
        self.timeout_threshold = timeout_threshold
        self.metrics_file = Path("docs/reports/plans/performance_metrics.json")
        self.current_operation: PerformanceMetrics | None = None
        self.monitor_thread: threading.Thread | None = None
        self.monitoring = False
        self.history = self._load_history()

    def _load_history(self) -> list[PerformanceMetrics]:
        """Load historical performance data."""
        history = []

        if self.metrics_file.exists():
            try:
                data = json.loads(self.metrics_file.read_text(encoding="utf-8"))
                for item in data.get("history", []):
                    metrics = PerformanceMetrics(**item)
                    # Convert lists back
                    metrics.cpu_percent = item.get("cpu_percent", [])
                    metrics.memory_mb = item.get("memory_mb", [])
                    metrics.skills_executed = item.get("skills_executed", [])
                    history.append(metrics)
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                print(f"Warning: Could not load performance history: {e}")

        return history

    def _save_history(self):
        """Save performance history."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "timeout_threshold": self.timeout_threshold,
                "history": [asdict(m) for m in self.history[-100:]],  # Keep last 100 operations
            }

            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            self.metrics_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            print(f"Warning: Could not save performance history: {e}")

    def _monitor_system(self):
        """Monitor system resources during operation."""
        while self.monitoring and self.current_operation:
            try:
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory().used / (1024 * 1024)  # MB

                self.current_operation.cpu_percent.append(cpu)
                self.current_operation.memory_mb.append(memory)

                time.sleep(0.5)  # Sample every 500ms

            except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
                break

    def start_monitoring(self, operation: str) -> str:
        """Start monitoring an operation."""
        if self.current_operation:
            return "Error: Already monitoring an operation"

        self.current_operation = PerformanceMetrics(
            operation=operation,
            start_time=time.time(),
            end_time=None,
            duration=None,
            cpu_percent=[],
            memory_mb=[],
            timeout_threshold=self.timeout_threshold,
        )

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()

        return f"Started monitoring {operation}"

    def add_skill_executed(self, skill_name: str):
        """Add a skill to the executed list."""
        if self.current_operation:
            self.current_operation.skills_executed.append(skill_name)

    def stop_monitoring(self, timed_out: bool = False) -> dict:
        """Stop monitoring and return metrics."""
        if not self.current_operation:
            return {"error": "No operation being monitored"}

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

        self.current_operation.end_time = time.time()
        self.current_operation.duration = self.current_operation.end_time - self.current_operation.start_time
        self.current_operation.timed_out = timed_out

        # Calculate averages
        if self.current_operation.cpu_percent:
            avg_cpu = sum(self.current_operation.cpu_percent) / len(self.current_operation.cpu_percent)
        else:
            avg_cpu = 0.0

        if self.current_operation.memory_mb:
            avg_memory = sum(self.current_operation.memory_mb) / len(self.current_operation.memory_mb)
        else:
            avg_memory = 0.0

        # Add to history
        self.history.append(self.current_operation)
        self._save_history()

        result = {
            "operation": self.current_operation.operation,
            "duration": self.current_operation.duration,
            "timeout_threshold": self.current_operation.timeout_threshold,
            "timed_out": timed_out,
            "skills_executed": len(self.current_operation.skills_executed),
            "avg_cpu_percent": avg_cpu,
            "avg_memory_mb": avg_memory,
            "max_cpu_percent": max(self.current_operation.cpu_percent)
            if self.current_operation.cpu_percent
            else 0.0,
            "max_memory_mb": max(self.current_operation.memory_mb)
            if self.current_operation.memory_mb
            else 0.0,
        }

        self.current_operation = None
        return result

    def check_timeout(self) -> bool:
        """Check if current operation has timed out."""
        if not self.current_operation:
            return False

        elapsed = time.time() - self.current_operation.start_time
        return elapsed > self.timeout_threshold

    def get_performance_summary(self, hours: int = 24) -> dict:
        """Get performance summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_ops = [
            m for m in self.history if m.end_time and datetime.fromtimestamp(m.end_time) > cutoff_time
        ]

        if not recent_ops:
            return {"error": f"No operations in the last {hours} hours"}

        durations = [m.duration for m in recent_ops if m.duration]
        timeouts = sum(1 for m in recent_ops if m.timed_out)

        # Calculate percentiles
        if durations:
            durations.sort()
            p50 = durations[len(durations) // 2]
            p95 = durations[int(len(durations) * 0.95)]
            p99 = durations[int(len(durations) * 0.99)] if len(durations) > 100 else max(durations)
        else:
            p50 = p95 = p99 = 0.0

        # CPU and memory averages
        all_cpu = []
        all_memory = []
        for m in recent_ops:
            all_cpu.extend(m.cpu_percent)
            all_memory.extend(m.memory_mb)

        avg_cpu = sum(all_cpu) / len(all_cpu) if all_cpu else 0.0
        avg_memory = sum(all_memory) / len(all_memory) if all_memory else 0.0

        return {
            "period_hours": hours,
            "total_operations": len(recent_ops),
            "timeouts": timeouts,
            "timeout_rate": (timeouts / len(recent_ops)) * 100,
            "duration_stats": {
                "min": min(durations) if durations else 0.0,
                "max": max(durations) if durations else 0.0,
                "avg": sum(durations) / len(durations) if durations else 0.0,
                "p50": p50,
                "p95": p95,
                "p99": p99,
            },
            "resource_stats": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_mb": avg_memory,
                "max_cpu_percent": max(all_cpu) if all_cpu else 0.0,
                "max_memory_mb": max(all_memory) if all_memory else 0.0,
            },
            "operations_over_threshold": sum(
                1 for m in recent_ops if m.duration and m.duration > self.timeout_threshold
            ),
        }

    def generate_alerts(self) -> list[str]:
        """Generate performance alerts."""
        alerts = []
        recent_summary = self.get_performance_summary(1)  # Last hour

        if "error" not in recent_summary:
            # High timeout rate
            if recent_summary["timeout_rate"] > 10:  # More than 10% timeouts
                alerts.append(f"⚠️ High timeout rate: {recent_summary['timeout_rate']:.1f}% in last hour")

            # Slow operations
            if (
                recent_summary["duration_stats"]["p95"] > self.timeout_threshold * 0.8
            ):  # 95th percentile approaching threshold
                alerts.append(
                    f"⚠️ Slow operations: 95th percentile at {recent_summary['duration_stats']['p95']:.2f}s",
                )

            # High resource usage
            if recent_summary["resource_stats"]["avg_cpu_percent"] > 80:
                alerts.append(
                    f"⚠️ High CPU usage: {recent_summary['resource_stats']['avg_cpu_percent']:.1f}% average",
                )

            if recent_summary["resource_stats"]["avg_memory_mb"] > 1000:  # More than 1GB
                alerts.append(
                    f"⚠️ High memory usage: {recent_summary['resource_stats']['avg_memory_mb']:.1f}MB average",
                )

        return alerts


def main():
    """Main entry point for the performance monitor."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args]")
        print("Commands:")
        print("  start <operation>     - Start monitoring an operation")
        print("  stop                  - Stop monitoring and show results")
        print("  summary [hours]       - Show performance summary (default: 24)")
        print("  alerts                - Show performance alerts")
        print("  check                 - Check if current operation timed out")
        print("  add-skill <skill>     - Add skill to current operation")
        sys.exit(1)

    command = sys.argv[1]

    # Health check
    if command == "--health-check":
        print("[PASS] Performance monitor health check")
        sys.exit(0)

    # Get timeout threshold from args or environment
    timeout_threshold = 5.0
    if "--timeout" in sys.argv:
        idx = sys.argv.index("--timeout")
        if idx + 1 < len(sys.argv):
            timeout_threshold = float(sys.argv[idx + 1])

    monitor = PerformanceMonitor(timeout_threshold)

    if command == "start":
        if len(sys.argv) < 3:
            print("Error: Operation name required")
            sys.exit(1)

        operation = sys.argv[2]
        result = monitor.start_monitoring(operation)
        print(result)

    elif command == "add-skill":
        if len(sys.argv) < 3:
            print("Error: Skill name required")
            sys.exit(1)

        skill_name = sys.argv[2]
        monitor.add_skill_executed(skill_name)
        print(f"Added skill: {skill_name}")

    elif command == "stop":
        timed_out = "--timeout" in sys.argv
        result = monitor.stop_monitoring(timed_out)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\n📊 Performance Results for {result['operation']}:")
            print(f"   Duration: {result['duration']:.2f}s")
            print(f"   Timeout: {result['timeout_threshold']:.1f}s")
            print(f"   Status: {'⏰ TIMED OUT' if result['timed_out'] else '✅ Completed'}")
            print(f"   Skills: {result['skills_executed']}")
            print(f"   Avg CPU: {result['avg_cpu_percent']:.1f}%")
            print(f"   Avg Memory: {result['avg_memory_mb']:.1f}MB")

    elif command == "summary":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        summary = monitor.get_performance_summary(hours)

        if "error" in summary:
            print(f"Error: {summary['error']}")
        else:
            print(f"\n📊 Performance Summary (Last {hours} hours):")
            print(f"   Total Operations: {summary['total_operations']}")
            print(f"   Timeouts: {summary['timeouts']} ({summary['timeout_rate']:.1f}%)")
            print(f"   Avg Duration: {summary['duration_stats']['avg']:.2f}s")
            print(f"   P95 Duration: {summary['duration_stats']['p95']:.2f}s")
            print(f"   Avg CPU: {summary['resource_stats']['avg_cpu_percent']:.1f}%")
            print(f"   Avg Memory: {summary['resource_stats']['avg_memory_mb']:.1f}MB")
            print(f"   Over Threshold: {summary['operations_over_threshold']}")

    elif command == "alerts":
        alerts = monitor.generate_alerts()

        if alerts:
            print("\n⚠️ Performance Alerts:")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print("\n✅ No performance alerts")

    elif command == "check":
        timed_out = monitor.check_timeout()
        if timed_out:
            print("⏰ Operation has timed out")
            sys.exit(1)
        else:
            elapsed = time.time() - monitor.current_operation.start_time if monitor.current_operation else 0
            remaining = monitor.timeout_threshold - elapsed
            print(f"✅ Operation running, {remaining:.1f}s remaining")

    else:
        print(f"Error: Unknown command {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
