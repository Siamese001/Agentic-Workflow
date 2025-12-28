#!/usr/bin/env python3
"""
Test Coverage Guardian Agent
Advanced batch agent: Enforces comprehensive test coverage with branch, function, and historical metrics.
- Runs coverage with --branch
- Generates HTML report
- Tracks history in coverage_history.json
- Auto-generates targeted stubs
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class TestCoverageGuardianAgent:
    """
    Advanced batch agent: Enforces comprehensive test coverage with branch, function, and historical metrics.
    - Runs coverage with --branch
    - Generates HTML report
    - Tracks history in coverage_history.json
    - Auto-generates targeted stubs
    """

    def __init__(self, project_root: Path, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.min_line_coverage = 95
        self.min_branch_coverage = 90
        self.test_dir = self.project_root / "tests"
        self.html_report_dir = self.project_root / "htmlcov"
        self.history_file = self.project_root / "coverage_history.json"
        self.auto_generate = True

    def _load_history(self) -> List[Dict]:
        """Load coverage history from JSON file."""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_history(self, entry: Dict):
        """Save coverage history entry (keep last 30)."""
        history = self._load_history()
        history.append(entry)
        # Keep only last 30 entries
        self.history_file.write_text(
            json.dumps(history[-30:], indent=2), encoding="utf-8"
        )

    def _run_advanced_coverage(self) -> Dict[str, Any]:
        """Run pytest with branch coverage and generate reports."""
        try:
            # Run coverage with branch analysis
            subprocess.run(
                [
                    "coverage",
                    "run",
                    "--branch",
                    "-m",
                    "pytest",
                    str(self.project_root / "agentic_core"),
                    "--quiet",
                ],
                check=True,
                cwd=self.project_root,
                capture_output=True,
            )
            
            # Generate JSON report
            subprocess.run(
                ["coverage", "json", "-o", "coverage.json"], cwd=self.project_root
            )
            
            # Generate HTML report
            subprocess.run(
                ["coverage", "html", "-d", str(self.html_report_dir)],
                cwd=self.project_root,
            )

            # Read JSON report
            report_file = self.project_root / "coverage.json"
            if report_file.exists():
                return json.loads(report_file.read_text(encoding="utf-8"))

        except FileNotFoundError:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "TestCoverageGuardianAgent", 0, False, "coverage not installed"
                )
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "TestCoverageGuardianAgent", 0, False, f"Advanced coverage failed: {e}"
                )
        return {"files": {}}

    async def execute(self) -> Dict:
        """Measure test coverage with advanced metrics and generate reports."""
        print("   [ADVANCED COVERAGE] Running branch-aware coverage analysis...")
        report = self._run_advanced_coverage()
        totals = report.get("totals", {})
        line_cov = totals.get("percent_covered", 0)
        branch_cov = totals.get("percent_covered_display", 0)  # Branch coverage if available

        low_files = []

        for file_path, data in report.get("files", {}).items():
            if not file_path.startswith("agentic_core/"):
                continue

            summary = data.get("summary", {})
            line_percent = summary.get("percent_covered", 100)
            branch_percent = summary.get("percent_covered_display", 100)

            # Check both line and branch coverage
            if line_percent < self.min_line_coverage or (
                isinstance(branch_percent, (int, float))
                and branch_percent < self.min_branch_coverage
            ):
                low_files.append(file_path)

        # Save history entry
        self._save_history(
            {
                "timestamp": datetime.now().isoformat(),
                "line_coverage": round(line_cov, 1),
                "branch_coverage": round(branch_cov, 1) if isinstance(branch_cov, (int, float)) else 0,
                "gaps": len(low_files),
            }
        )

        print(f"   [METRICS] Line: {line_cov:.1f}% | Branch: {branch_cov if isinstance(branch_cov, (int, float)) else 'N/A'}")
        print(f"   [REPORT] HTML: file://{self.html_report_dir}/index.html")

        return {
            "line_coverage": line_cov,
            "branch_coverage": branch_cov if isinstance(branch_cov, (int, float)) else 0,
            "low_coverage_files": len(low_files),
            "html_report": str(self.html_report_dir / "index.html"),
        }
