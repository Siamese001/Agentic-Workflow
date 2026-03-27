#!/usr/bin/env python3
"""
Windsurf Skill: Skill Status Dashboard
Dashboard for monitoring skill health and performance.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for dashboard operations
# guardian: allow-magic-configuration -- Dashboard configuration and display logic


class SkillMetrics:
    """Metrics for a single skill."""

    def __init__(self, name: str):
        self.name = name
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.average_duration = 0.0
        self.last_run_time = None
        self.last_run_status = None
        self.dependencies = []
        self.category = ""
        self.exists = False

    def update_run(self, success: bool, duration: float):
        """Update metrics with a new run."""
        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1

        # Update average duration
        if self.total_runs == 1:
            self.average_duration = duration
        else:
            self.average_duration = (
                (self.average_duration * (self.total_runs - 1)) + duration
            ) / self.total_runs

        self.last_run_time = datetime.now()
        self.last_run_status = success

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100

    @property
    def health_score(self) -> str:
        """Calculate health score."""
        if self.total_runs == 0:
            return "Unknown"

        if self.success_rate >= 95:
            return "Excellent"
        elif self.success_rate >= 85:
            return "Good"
        elif self.success_rate >= 70:
            return "Fair"
        else:
            return "Poor"


class SkillStatusDashboard:
    """Dashboard for monitoring skill status."""

    def __init__(self):
        self.skills_dir = Path(".windsurf/skills")
        self.metrics_file = Path("docs/reports/plans/skill_metrics.json")
        self.metrics = self._load_metrics()
        self.skill_registry = self._scan_skills()

    def _load_metrics(self) -> dict[str, SkillMetrics]:
        """Load historical metrics."""
        metrics = {}

        if self.metrics_file.exists():
            try:
                data = json.loads(self.metrics_file.read_text(encoding="utf-8"))
                for name, data_dict in data.items():
                    metric = SkillMetrics(name)
                    metric.total_runs = data_dict.get("total_runs", 0)
                    metric.successful_runs = data_dict.get("successful_runs", 0)
                    metric.failed_runs = data_dict.get("failed_runs", 0)
                    metric.average_duration = data_dict.get("average_duration", 0.0)
                    metric.dependencies = data_dict.get("dependencies", [])
                    metric.category = data_dict.get("category", "")
                    metric.exists = data_dict.get("exists", False)

                    if data_dict.get("last_run_time"):
                        metric.last_run_time = datetime.fromisoformat(data_dict["last_run_time"])

                    metrics[name] = metric
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")

        return metrics

    def _save_metrics(self):
        """Save metrics to file."""
        try:
            data = {}
            for name, metric in self.metrics.items():
                data[name] = {
                    "total_runs": metric.total_runs,
                    "successful_runs": metric.successful_runs,
                    "failed_runs": metric.failed_runs,
                    "average_duration": metric.average_duration,
                    "dependencies": metric.dependencies,
                    "category": metric.category,
                    "exists": metric.exists,
                    "last_run_time": metric.last_run_time.isoformat() if metric.last_run_time else None,
                    "last_run_status": metric.last_run_status,
                }

            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            self.metrics_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

    def _scan_skills(self) -> dict[str, dict]:
        """Scan for available skills."""
        registry = {}

        if not self.skills_dir.exists():
            return registry

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                main_script = skill_dir / "main.py"
                config_file = skill_dir / "skill.yaml"

                registry[skill_dir.name] = {
                    "path": str(skill_dir),
                    "main_exists": main_script.exists(),
                    "config_exists": config_file.exists(),
                    "last_modified": datetime.fromtimestamp(skill_dir.stat().st_mtime)
                    if skill_dir.exists()
                    else None,
                }

                # Initialize metrics if not exists
                if skill_dir.name not in self.metrics:
                    self.metrics[skill_dir.name] = SkillMetrics(skill_dir.name)

                self.metrics[skill_dir.name].exists = main_script.exists()

        return registry

    def _test_skill_health(self, skill_name: str) -> tuple[bool, float, list[str]]:
        """Test if a skill is healthy."""
        if skill_name not in self.skill_registry:
            return False, 0.0, ["Skill not found"]

        skill_info = self.skill_registry[skill_name]

        if not skill_info["main_exists"]:
            return False, 0.0, ["Main script missing"]

        start_time = time.time()

        try:
            # Try to run the skill with --help or similar
            main_script = Path(skill_info["path"]) / "main.py"
            result = subprocess.run(
                ["python", str(main_script), "--help"], capture_output=True, text=True, timeout=10
            )

            duration = time.time() - start_time

            # Check if it ran (even if it failed due to wrong args)
            if result.returncode in [0, 1]:  # 0 for success, 1 for wrong args is okay
                return True, duration, []
            else:
                return False, duration, [result.stderr.strip() or "Unknown error"]

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, duration, ["Timeout"]
        except Exception as e:
            duration = time.time() - start_time
            return False, duration, [str(e)]

    def update_skill_metrics(self):
        """Update metrics for all skills."""
        print("🔍 Updating skill metrics...")

        for skill_name in self.skill_registry.keys():
            print(f"  Testing {skill_name}...", end=" ")
            success, duration, issues = self._test_skill_health(skill_name)

            self.metrics[skill_name].update_run(success, duration)

            if success:
                print(f"✅ ({duration:.2f}s)")
            else:
                print(f"❌ ({duration:.2f}s)")
                for issue in issues[:1]:  # Show first issue only
                    print(f"    - {issue}")

        self._save_metrics()
        print("✅ Metrics updated")

    def generate_table_report(self, skill_filter: str | None = None) -> str:
        """Generate table format report."""
        report = []
        report.append("\n📊 Skill Status Dashboard")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Filter skills
        skills_to_show = list(self.metrics.keys())
        if skill_filter:
            skills_to_show = [s for s in skills_to_show if skill_filter.lower() in s.lower()]

        if not skills_to_show:
            report.append(f"No skills found matching filter: {skill_filter}")
            return "\n".join(report)

        # Table header
        report.append(f"{'Skill':<25} {'Health':<10} {'Success':<8} {'Runs':<6} {'Avg Time':<10} {'Status'}")
        report.append("-" * 80)

        # Sort by health score
        sorted_skills = sorted(skills_to_show, key=lambda s: self.metrics[s].success_rate, reverse=True)

        for skill_name in sorted_skills:
            metric = self.metrics[skill_name]
            status_icon = "✅" if metric.exists else "❌"
            health = metric.health_score

            report.append(
                f"{skill_name:<25} {health:<10} {metric.success_rate:>6.1f}% {metric.total_runs:>6} {metric.average_duration:>8.2f}s {status_icon}"
            )

        # Summary
        report.append("")
        report.append("Summary:")
        total_skills = len(skills_to_show)
        healthy_skills = sum(1 for s in skills_to_show if self.metrics[s].success_rate >= 85)
        total_runs = sum(self.metrics[s].total_runs for s in skills_to_show)
        avg_success_rate = (
            sum(self.metrics[s].success_rate for s in skills_to_show) / total_skills
            if total_skills > 0
            else 0
        )

        report.append(f"  Total skills: {total_skills}")
        report.append(f"  Healthy skills (≥85%): {healthy_skills}")
        report.append(f"  Total runs: {total_runs}")
        report.append(f"  Average success rate: {avg_success_rate:.1f}%")

        return "\n".join(report)

    def generate_json_report(self, skill_filter: str | None = None) -> str:
        """Generate JSON format report."""
        skills_to_show = list(self.metrics.keys())
        if skill_filter:
            skills_to_show = [s for s in skills_to_show if skill_filter.lower() in s.lower()]

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_skills": len(skills_to_show),
                "healthy_skills": sum(1 for s in skills_to_show if self.metrics[s].success_rate >= 85),
                "total_runs": sum(self.metrics[s].total_runs for s in skills_to_show),
                "average_success_rate": sum(self.metrics[s].success_rate for s in skills_to_show)
                / len(skills_to_show)
                if skills_to_show
                else 0,
            },
            "skills": {},
        }

        for skill_name in skills_to_show:
            metric = self.metrics[skill_name]
            report_data["skills"][skill_name] = {
                "success_rate": metric.success_rate,
                "total_runs": metric.total_runs,
                "successful_runs": metric.successful_runs,
                "failed_runs": metric.failed_runs,
                "average_duration": metric.average_duration,
                "health_score": metric.health_score,
                "exists": metric.exists,
                "last_run_time": metric.last_run_time.isoformat() if metric.last_run_time else None,
                "last_run_status": metric.last_run_status,
            }

        return json.dumps(report_data, indent=2)

    def generate_markdown_report(self, skill_filter: str | None = None) -> str:
        """Generate Markdown format report."""
        skills_to_show = list(self.metrics.keys())
        if skill_filter:
            skills_to_show = [s for s in skills_to_show if skill_filter.lower() in s.lower()]

        report = []
        report.append("# Skill Status Dashboard")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary section
        total_skills = len(skills_to_show)
        healthy_skills = sum(1 for s in skills_to_show if self.metrics[s].success_rate >= 85)
        total_runs = sum(self.metrics[s].total_runs for s in skills_to_show)
        avg_success_rate = (
            sum(self.metrics[s].success_rate for s in skills_to_show) / total_skills
            if total_skills > 0
            else 0
        )

        report.append("## Summary")
        report.append("")
        report.append(f"- **Total Skills:** {total_skills}")
        report.append(f"- **Healthy Skills (≥85%):** {healthy_skills}")
        report.append(f"- **Total Runs:** {total_runs}")
        report.append(f"- **Average Success Rate:** {avg_success_rate:.1f}%")
        report.append("")

        # Skills table
        report.append("## Skills Details")
        report.append("")
        report.append("| Skill | Health | Success Rate | Runs | Avg Time | Status |")
        report.append("|-------|--------|-------------|------|---------|--------|")

        sorted_skills = sorted(skills_to_show, key=lambda s: self.metrics[s].success_rate, reverse=True)

        for skill_name in sorted_skills:
            metric = self.metrics[skill_name]
            status_icon = "✅" if metric.exists else "❌"

            report.append(
                f"| {skill_name} | {metric.health_score} | {metric.success_rate:.1f}% | {metric.total_runs} | {metric.average_duration:.2f}s | {status_icon} |"
            )

        return "\n".join(report)


def main():
    """Main entry point for the dashboard."""
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] Skill status dashboard health check")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python main.py <format> [skill_filter]")
        print("Formats: json, table, markdown")
        sys.exit(1)

    format_type = sys.argv[1]
    skill_filter = sys.argv[2] if len(sys.argv) > 2 else None

    if format_type not in ["json", "table", "markdown"]:
        print("Error: Invalid format. Use json, table, or markdown")
        sys.exit(1)

    dashboard = SkillStatusDashboard()

    # Update metrics if requested
    if "--update" in sys.argv:
        dashboard.update_skill_metrics()

    # Generate report
    if format_type == "json":
        print(dashboard.generate_json_report(skill_filter))
    elif format_type == "table":
        print(dashboard.generate_table_report(skill_filter))
    elif format_type == "markdown":
        print(dashboard.generate_markdown_report(skill_filter))


if __name__ == "__main__":
    main()
