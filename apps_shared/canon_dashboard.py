"""
Canon Validator Dashboard - Best-in-Class Monitoring UI
Real-time metrics, interactive tables, and comprehensive analytics
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import queue

try:
    from rich.console import Console
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich.align import Align
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Install with: pip install rich")


@dataclass
class KeyMetrics:
    """Metrics for a single canon key"""
    key_id: int
    key_name: str
    files_checked: int = 0
    files_passed: int = 0
    files_failed: int = 0
    violations_found: int = 0
    violations_healed: int = 0
    healing_attempts: int = 0
    avg_healing_time: float = 0.0
    status: str = "pending"  # pending, running, passed, failed
    
    @property
    def pass_rate(self) -> float:
        if self.files_checked == 0:
            return 0.0
        return (self.files_passed / self.files_checked) * 100
    
    @property
    def healing_success_rate(self) -> float:
        if self.violations_found == 0:
            return 0.0
        return (self.violations_healed / self.violations_found) * 100


@dataclass
class FileMetrics:
    """Metrics for a single file"""
    file_path: str
    loc: int
    keys_checked: List[int]
    keys_passed: List[int]
    keys_failed: List[int]
    violations: Dict[int, int]  # key_id -> violation_count
    healing_rounds: int = 0
    processing_time: float = 0.0
    status: str = "pending"  # pending, processing, passed, failed, healing


@dataclass
class ValidationSession:
    """Overall validation session metrics"""
    session_id: str
    target_directory: str
    start_time: datetime
    total_files: int
    files_processed: int = 0
    files_passed: int = 0
    files_failed: int = 0
    total_violations: int = 0
    total_healed: int = 0
    total_healing_attempts: int = 0
    current_file: Optional[str] = None
    status: str = "running"  # running, completed, failed
    
    @property
    def progress_pct(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.files_processed / self.total_files) * 100
    
    @property
    def elapsed_time(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def files_per_minute(self) -> float:
        if self.elapsed_time == 0:
            return 0.0
        return (self.files_processed / self.elapsed_time) * 60
    
    @property
    def eta_minutes(self) -> float:
        if self.files_per_minute == 0:
            return 0.0
        remaining = self.total_files - self.files_processed
        return remaining / self.files_per_minute


class DashboardMetrics:
    """Central metrics collection and aggregation"""
    
    def __init__(self):
        self.session: Optional[ValidationSession] = None
        self.key_metrics: Dict[int, KeyMetrics] = {}
        self.file_metrics: Dict[str, FileMetrics] = {}
        self.violation_timeline: List[Dict[str, Any]] = []
        self.healing_timeline: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # Initialize all 50 keys
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Initialize metrics for all 50 canon keys"""
        key_names = {
            0: "Void Compliance", 1: "No Hardcoded Paths", 2: "No Secrets",
            3: "No Dead Code", 4: "No Magic Numbers", 5: "Type Hints",
            6: "Docstrings", 7: "Error Handling", 8: "Logging",
            9: "Testing", 10: "No Global State", 11: "Immutability",
            12: "Single Responsibility", 13: "DRY", 14: "KISS",
            15: "YAGNI", 16: "Composition over Inheritance", 17: "Dependency Injection",
            18: "Interface Segregation", 19: "Liskov Substitution", 20: "Open/Closed",
            21: "Async/Await", 22: "Context Managers", 23: "Generators",
            24: "Decorators", 25: "Property Methods", 26: "Class Methods",
            27: "Static Methods", 28: "Abstract Base Classes", 29: "Protocols",
            30: "Dataclasses", 31: "Enums", 32: "Named Tuples",
            33: "Type Aliases", 34: "Generic Types", 35: "Union Types",
            36: "Optional Types", 37: "Literal Types", 38: "Final Types",
            39: "ClassVar Types", 40: "Import Waterfall", 41: "Deep Nesting",
            42: "Line Length", 43: "Function Complexity", 44: "Class Size",
            45: "Parameter Count", 46: "Return Complexity", 47: "Cognitive Load",
            48: "RESERVED", 49: "Universal Depth Law"
        }
        
        for key_id, key_name in key_names.items():
            self.key_metrics[key_id] = KeyMetrics(key_id=key_id, key_name=key_name)
    
    def start_session(self, target_dir: str, total_files: int):
        """Start a new validation session"""
        with self.lock:
            self.session = ValidationSession(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                target_directory=target_dir,
                start_time=datetime.now(),
                total_files=total_files
            )
    
    def update_file_progress(self, file_path: str, status: str):
        """Update file processing status"""
        with self.lock:
            if self.session:
                self.session.current_file = file_path
                if status == "passed":
                    self.session.files_passed += 1
                    self.session.files_processed += 1
                elif status == "failed":
                    self.session.files_failed += 1
                    self.session.files_processed += 1
    
    def record_violation(self, file_path: str, key_id: int, violation_count: int):
        """Record violations found"""
        with self.lock:
            if key_id in self.key_metrics:
                self.key_metrics[key_id].violations_found += violation_count
                self.key_metrics[key_id].files_failed += 1
                self.session.total_violations += violation_count
            
            self.violation_timeline.append({
                "timestamp": datetime.now(),
                "file": file_path,
                "key_id": key_id,
                "count": violation_count
            })
    
    def record_healing(self, file_path: str, key_id: int, healed_count: int, duration: float):
        """Record healing attempt"""
        with self.lock:
            if key_id in self.key_metrics:
                self.key_metrics[key_id].violations_healed += healed_count
                self.key_metrics[key_id].healing_attempts += 1
                self.session.total_healed += healed_count
                self.session.total_healing_attempts += 1
            
            self.healing_timeline.append({
                "timestamp": datetime.now(),
                "file": file_path,
                "key_id": key_id,
                "healed": healed_count,
                "duration": duration
            })
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get files with most violations"""
        file_violations = defaultdict(int)
        for entry in self.violation_timeline:
            file_violations[entry["file"]] += entry["count"]
        
        sorted_files = sorted(file_violations.items(), key=lambda x: x[1], reverse=True)
        return [{"file": f, "violations": v} for f, v in sorted_files[:limit]]
    
    def get_key_summary(self) -> Dict[str, Any]:
        """Get summary of key performance"""
        with self.lock:
            passed = sum(1 for k in self.key_metrics.values() if k.status == "passed")
            failed = sum(1 for k in self.key_metrics.values() if k.status == "failed")
            running = sum(1 for k in self.key_metrics.values() if k.status == "running")
            
            return {
                "total_keys": 50,
                "passed": passed,
                "failed": failed,
                "running": running,
                "pending": 50 - passed - failed - running
            }


class CanonDashboard:
    """Best-in-class dashboard UI for canon validator"""
    
    def __init__(self, metrics: DashboardMetrics):
        self.metrics = metrics
        self.console = Console() if RICH_AVAILABLE else None
        self.update_interval = 0.5  # seconds
        
    def create_header_panel(self) -> Panel:
        """Create header with session info"""
        if not self.metrics.session:
            return Panel("No active session", title="Canon Validator Dashboard", border_style="red")
        
        session = self.metrics.session
        
        header_text = Text()
        header_text.append("🎯 Target: ", style="bold cyan")
        header_text.append(f"{session.target_directory}\n", style="white")
        header_text.append("📊 Progress: ", style="bold cyan")
        header_text.append(f"{session.files_processed}/{session.total_files} ", style="white")
        header_text.append(f"({session.progress_pct:.1f}%)\n", style="green")
        header_text.append("⏱️  Elapsed: ", style="bold cyan")
        header_text.append(f"{session.elapsed_time:.0f}s ", style="white")
        header_text.append(f"| ETA: {session.eta_minutes:.1f}m ", style="yellow")
        header_text.append(f"| Speed: {session.files_per_minute:.1f} files/min\n", style="yellow")
        header_text.append("📝 Current: ", style="bold cyan")
        header_text.append(f"{session.current_file or 'Initializing...'}", style="white")
        
        return Panel(
            Align.center(header_text),
            title=f"[bold white]Canon Validator Dashboard[/bold white] [dim]Session: {session.session_id}[/dim]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
    
    def create_summary_table(self) -> Table:
        """Create summary statistics table"""
        table = Table(title="📈 Validation Summary", box=box.ROUNDED, border_style="cyan")
        
        table.add_column("Metric", style="bold cyan", width=25)
        table.add_column("Value", justify="right", style="white", width=15)
        table.add_column("Status", justify="center", width=20)
        
        session = self.metrics.session
        if not session:
            return table
        
        # Files
        table.add_row(
            "Files Processed",
            f"{session.files_processed}/{session.total_files}",
            self._get_progress_bar(session.progress_pct)
        )
        table.add_row(
            "Files Passed",
            str(session.files_passed),
            f"[green]✓ {session.files_passed}[/green]"
        )
        table.add_row(
            "Files Failed",
            str(session.files_failed),
            f"[red]✗ {session.files_failed}[/red]"
        )
        
        table.add_section()
        
        # Violations
        table.add_row(
            "Total Violations",
            str(session.total_violations),
            f"[red]⚠ {session.total_violations}[/red]"
        )
        table.add_row(
            "Violations Healed",
            str(session.total_healed),
            f"[green]✓ {session.total_healed}[/green]"
        )
        
        healing_rate = 0.0
        if session.total_violations > 0:
            healing_rate = (session.total_healed / session.total_violations) * 100
        
        table.add_row(
            "Healing Success Rate",
            f"{healing_rate:.1f}%",
            self._get_status_indicator(healing_rate, 80, 50)
        )
        
        table.add_section()
        
        # Keys
        key_summary = self.metrics.get_key_summary()
        table.add_row(
            "Keys Passed",
            f"{key_summary['passed']}/50",
            f"[green]✓ {key_summary['passed']}[/green]"
        )
        table.add_row(
            "Keys Failed",
            f"{key_summary['failed']}/50",
            f"[red]✗ {key_summary['failed']}[/red]"
        )
        table.add_row(
            "Keys Running",
            f"{key_summary['running']}/50",
            f"[yellow]⟳ {key_summary['running']}[/yellow]"
        )
        
        return table
    
    def create_key_metrics_table(self, limit: int = 15) -> Table:
        """Create detailed key metrics table"""
        table = Table(title="🔑 Key Performance Metrics", box=box.ROUNDED, border_style="magenta")
        
        table.add_column("Key", style="bold", width=4)
        table.add_column("Name", style="cyan", width=25)
        table.add_column("Files", justify="right", width=8)
        table.add_column("Pass Rate", justify="right", width=10)
        table.add_column("Violations", justify="right", width=12)
        table.add_column("Healed", justify="right", width=10)
        table.add_column("Status", justify="center", width=12)
        
        # Sort by violations (most problematic first)
        sorted_keys = sorted(
            self.metrics.key_metrics.values(),
            key=lambda k: k.violations_found,
            reverse=True
        )
        
        for key in sorted_keys[:limit]:
            if key.files_checked == 0 and key.violations_found == 0:
                continue
            
            status_icon = {
                "passed": "[green]✓[/green]",
                "failed": "[red]✗[/red]",
                "running": "[yellow]⟳[/yellow]",
                "pending": "[dim]○[/dim]"
            }.get(key.status, "○")
            
            pass_rate_color = "green" if key.pass_rate >= 90 else "yellow" if key.pass_rate >= 70 else "red"
            healing_color = "green" if key.healing_success_rate >= 80 else "yellow" if key.healing_success_rate >= 50 else "red"
            
            table.add_row(
                str(key.key_id),
                key.key_name[:25],
                str(key.files_checked),
                f"[{pass_rate_color}]{key.pass_rate:.1f}%[/{pass_rate_color}]",
                f"[red]{key.violations_found}[/red]",
                f"[{healing_color}]{key.violations_healed}[/{healing_color}]",
                status_icon
            )
        
        return table
    
    def create_top_violators_table(self, limit: int = 10) -> Table:
        """Create table of files with most violations"""
        table = Table(title="⚠️  Top Violators", box=box.ROUNDED, border_style="red")
        
        table.add_column("Rank", style="bold", width=6, justify="center")
        table.add_column("File", style="cyan", width=50)
        table.add_column("Violations", justify="right", style="red bold", width=12)
        table.add_column("Severity", justify="center", width=15)
        
        top_violators = self.metrics.get_top_violators(limit)
        
        for idx, violator in enumerate(top_violators, 1):
            severity = "🔥 CRITICAL" if violator["violations"] > 50 else "⚠️  HIGH" if violator["violations"] > 20 else "⚡ MEDIUM"
            severity_color = "red" if violator["violations"] > 50 else "yellow" if violator["violations"] > 20 else "white"
            
            file_name = Path(violator["file"]).name
            
            table.add_row(
                f"#{idx}",
                file_name,
                str(violator["violations"]),
                f"[{severity_color}]{severity}[/{severity_color}]"
            )
        
        return table
    
    def create_healing_activity_table(self, limit: int = 8) -> Table:
        """Create table of recent healing activity"""
        table = Table(title="🏥 Recent Healing Activity", box=box.ROUNDED, border_style="green")
        
        table.add_column("Time", style="dim", width=10)
        table.add_column("File", style="cyan", width=35)
        table.add_column("Key", justify="center", width=8)
        table.add_column("Healed", justify="right", style="green", width=10)
        table.add_column("Duration", justify="right", width=12)
        
        recent_healing = sorted(
            self.metrics.healing_timeline[-limit:],
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        for entry in recent_healing:
            time_str = entry["timestamp"].strftime("%H:%M:%S")
            file_name = Path(entry["file"]).name[:35]
            
            table.add_row(
                time_str,
                file_name,
                f"K{entry['key_id']}",
                f"+{entry['healed']}",
                f"{entry['duration']:.2f}s"
            )
        
        return table
    
    def _get_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text-based progress bar"""
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        color = "green" if percentage >= 80 else "yellow" if percentage >= 50 else "red"
        return f"[{color}]{bar}[/{color}] {percentage:.1f}%"
    
    def _get_status_indicator(self, value: float, good_threshold: float, ok_threshold: float) -> str:
        """Get colored status indicator"""
        if value >= good_threshold:
            return f"[green]✓ Excellent[/green]"
        elif value >= ok_threshold:
            return f"[yellow]⚠ Fair[/yellow]"
        else:
            return f"[red]✗ Poor[/red]"
    
    def create_layout(self) -> Layout:
        """Create the complete dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=7),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="summary", size=18),
            Layout(name="keys")
        )
        
        layout["right"].split_column(
            Layout(name="violators", size=15),
            Layout(name="healing")
        )
        
        # Populate layout
        layout["header"].update(self.create_header_panel())
        layout["summary"].update(self.create_summary_table())
        layout["keys"].update(self.create_key_metrics_table())
        layout["violators"].update(self.create_top_violators_table())
        layout["healing"].update(self.create_healing_activity_table())
        
        # Footer
        footer_text = Text()
        footer_text.append("Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold red")
        footer_text.append(" to stop monitoring | Updates every ", style="dim")
        footer_text.append(f"{self.update_interval}s", style="bold yellow")
        
        layout["footer"].update(Panel(Align.center(footer_text), border_style="dim"))
        
        return layout
    
    def run_live(self):
        """Run the dashboard with live updates"""
        if not RICH_AVAILABLE:
            print("Rich library not available. Install with: pip install rich")
            return
        
        try:
            with Live(self.create_layout(), refresh_per_second=2, console=self.console) as live:
                while True:
                    time.sleep(self.update_interval)
                    live.update(self.create_layout())
                    
                    # Check if session is complete
                    if self.metrics.session and self.metrics.session.status == "completed":
                        break
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard monitoring stopped by user[/yellow]")
    
    def export_report(self, output_path: str):
        """Export metrics to JSON report"""
        report = {
            "session": asdict(self.metrics.session) if self.metrics.session else None,
            "key_metrics": {k: asdict(v) for k, v in self.metrics.key_metrics.items()},
            "top_violators": self.metrics.get_top_violators(20),
            "key_summary": self.metrics.get_key_summary(),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report exported to: {output_path}")


# Example usage and testing
if __name__ == "__main__":
    # Create mock metrics for demonstration
    metrics = DashboardMetrics()
    metrics.start_session("agentic_core", 238)
    
    # Simulate some activity
    metrics.record_violation("agentic_core/canon_agents_core.py", 40, 5)
    metrics.record_violation("agentic_core/canon_orchestrator.py", 40, 3)
    metrics.record_violation("agentic_core/action_node.py", 41, 99)
    
    metrics.record_healing("agentic_core/canon_agents_core.py", 40, 3, 2.5)
    metrics.record_healing("agentic_core/action_node.py", 41, 50, 5.2)
    
    metrics.update_file_progress("agentic_core/canon_agents_core.py", "passed")
    metrics.update_file_progress("agentic_core/action_node.py", "failed")
    
    # Update some key statuses
    metrics.key_metrics[40].status = "failed"
    metrics.key_metrics[41].status = "running"
    metrics.key_metrics[0].status = "passed"
    
    # Create and run dashboard
    dashboard = CanonDashboard(metrics)
    
    if RICH_AVAILABLE:
        print("Starting dashboard in 3 seconds...")
        time.sleep(3)
        dashboard.run_live()
    else:
        print("Rich library not available. Exporting report instead...")
        dashboard.export_report("canon_validation_report.json")
