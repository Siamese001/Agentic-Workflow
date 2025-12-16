#!/usr/bin/env python
"""
Test Dashboard for Agentic Workflow

Provides a comprehensive UI to view, run, and analyze all tests in the tests/ directory.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestDashboard:
    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).parent
        self.tests_dir = self.root_dir / "tests"
        self.report_dir = self.root_dir / "test_reports"
        self.report_dir.mkdir(exist_ok=True)

    def discover_tests(self) -> Dict[str, Any]:
        """Discover all tests in the tests/ directory"""
        # print(f"\n{Colors.HEADER}🔍 Discovering Tests{Colors.ENDC}")  # [Security Fix]
        # print(f"Scanning: {self.tests_dir}")  # [Security Fix]

        # Collect all tests
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(self.tests_dir), "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=self.root_dir
        )

        if result.returncode != 0:
            # print(f"{Colors.FAIL}❌ Error collecting tests:{Colors.ENDC}")  # [Security Fix]
            # print(result.stderr)  # [Security Fix]
            return {"status": "error", "message": result.stderr}

        # Parse the output
        lines = result.stdout.split('\n')
        test_files = []
        test_count = 0

        for line in lines:
            if '.py::' in line:
                test_files.append(line.strip())
                test_count += 1

        return {
            "status": "success",
            "test_count": test_count,
            "test_files": test_files
        }

    def run_tests(self, test_pattern: str = None, generate_report: bool = True) -> Dict[str, Any]:
        """Run tests and generate reports"""
        # print(f"\n{Colors.HEADER}🚀 Running Tests{Colors.ENDC}")  # [Security Fix]

        # Determine which tests to run
        if test_pattern:
            test_path = self.tests_dir / test_pattern
        else:
            test_path = self.tests_dir

        # Prepare report filenames with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.report_dir / f"test_report_{timestamp}.html"
        json_report = self.report_dir / f"test_report_{timestamp}.json"

        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "--html", str(html_report),
            "--self-contained-html",
            "-v",
            "--tb=short"
        ]

        # Run tests
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root_dir)
        duration = time.time() - start_time

        # Parse results
        output_lines = result.stdout.split('\n')
        summary = {}
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed " in line:
                passed = int(line.split(" passed ")[0].split()[-1])
            elif " failed " in line:
                failed = int(line.split(" failed ")[0].split()[-1])
            elif " skipped " in line:
                skipped = int(line.split(" skipped ")[0].split()[-1])
            elif " error " in line:
                errors = int(line.split(" error ")[0].split()[-1])

        summary = {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total": passed + failed + skipped + errors,
            "duration": duration,
            "exit_code": result.returncode
        }

        # Print summary
        # print(f"\n{Colors.BOLD}Test Results Summary:{Colors.ENDC}")  # [Security Fix]
        # print(f"  Total: {summary['total']}")  # [Security Fix]
        # print(f"  {Colors.GREEN}✅ Passed: {summary['passed']}{Colors.ENDC}")  # [Security Fix]
        if failed > 0:
            # print(f"  {Colors.FAIL}❌ Failed: {failed}{Colors.ENDC}")  # [Security Fix]
        if skipped > 0:
            # print(f"  {Colors.WARNING}⏭️  Skipped: {skipped}{Colors.ENDC}")  # [Security Fix]
        if errors > 0:
            # print(f"  {Colors.FAIL}🚨 Errors: {errors}{Colors.ENDC}")  # [Security Fix]
        # print(f"  Duration: {duration:.2f}s")  # [Security Fix]

        # Save report
        report_data = {
            "timestamp": timestamp,
            "summary": summary,
            "html_report": str(html_report),
            "command": " ".join(cmd)
        }

        with open(json_report, 'w') as f:
            json.dump(report_data, f, indent=2)

        # print(f"\n{Colors.CYAN}📊 Reports generated:{Colors.ENDC}")  # [Security Fix]
        # print(f"  HTML: {html_report}")  # [Security Fix]
        # print(f"  JSON: {json_report}")  # [Security Fix]

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "summary": summary,
            "reports": {
                "html": str(html_report),
                "json": str(json_report)
            }
        }

    def show_test_categories(self):
        """Show different test categories available"""
        # print(f"\n{Colors.HEADER}📁 Test Categories{Colors.ENDC}")  # [Security Fix]

        categories = {
            "Core Implementation": [
                "test_zlm.py - ZLM (Zero-Latency Mode) tests",
                "test_outreach_zse.py - Outreach Engine ZSE tests",
                "master_integration_suite_fixed.py - Master integration suite"
            ],
            "Unit Tests": [
                "unit/ - Unit tests for individual components",
                "unit/agentic_core/ - Core agentic framework",
                "unit/engine/ - Engine operations",
                "unit/runtime/ - Runtime components"
            ],
            "Integration Tests": [
                "integration/ - Cross-component integration",
                "integration/api/ - API integration",
                "integration/core_plus_runtime/ - Core runtime integration"
            ],
            "Performance Tests": [
                "perf/ - Performance and load tests",
                "perf/latency/ - Latency measurements",
                "perf/throughput/ - Throughput tests"
            ],
            "End-to-End Tests": [
                "e2e/ - Full workflow tests",
                "e2e/admin_flows/ - Admin workflows",
                "e2e/outreach_flows/ - Outreach workflows"
            ],
            "Golden Tests": [
                "golden/ - Golden path tests",
                "golden/prompts/ - Prompt validation",
                "golden/safety/ - Safety property tests"
            ]
        }

        for category, tests in categories.items():
            # print(f"\n{Colors.BLUE}{category}:{Colors.ENDC}")  # [Security Fix]
            for test in tests:
                # print(f"  • {test}")  # [Security Fix]

    def run_category(self, category: str):
        """Run tests for a specific category"""
        category_map = {
            "core": "test_zlm.py test_outreach_zse.py master_integration_suite_fixed.py",
            "unit": "unit/",
            "integration": "integration/",
            "perf": "perf/",
            "e2e": "e2e/",
            "golden": "golden/"
        }

        if category not in category_map:
            # print(f"{Colors.FAIL}❌ Unknown category: {category}{Colors.ENDC}")  # [Security Fix]
            # print(f"Available categories: {', '.join(category_map.keys())}")  # [Security Fix]
            return

        # print(f"\n{Colors.HEADER}Running {category.upper()} tests{Colors.ENDC}")  # [Security Fix]
        return self.run_tests(category_map[category])

    def interactive_mode(self):
        """Run in interactive mode"""
        # print(f"\n{Colors.BOLD}{Colors.HEADER}🎛️  Agentic Workflow Test Dashboard{Colors.ENDC}")  # [Security Fix]
        # print(f"Root Directory: {self.root_dir}")  # [Security Fix]
        # print(f"Tests Directory: {self.tests_dir}")  # [Security Fix]

        while True:
            # print(f"\n{Colors.CYAN}Options:{Colors.ENDC}")  # [Security Fix]
            # print("  1. Discover all tests")  # [Security Fix]
            # print("  2. Run core implementation tests")  # [Security Fix]
            # print("  3. Run all tests (may have errors)")  # [Security Fix]
            # print("  4. Show test categories")  # [Security Fix]
            # print("  5. Run specific category")  # [Security Fix]
            # print("  6. View latest report")  # [Security Fix]
            # print("  7. Exit")  # [Security Fix]

            choice = input(f"\n{Colors.BOLD}Select option (1-7): {Colors.ENDC}").strip()

            if choice == "1":
                self.discover_tests()
            elif choice == "2":
                self.run_tests("test_zlm.py test_outreach_zse.py master_integration_suite_fixed.py")
            elif choice == "3":
                self.run_tests()
            elif choice == "4":
                self.show_test_categories()
            elif choice == "5":
                category = input("Enter category (core/unit/integration/perf/e2e/golden): ").strip()
                self.run_category(category)
            elif choice == "6":
                self.view_latest_report()
            elif choice == "7":
                # print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.ENDC}")  # [Security Fix]
                break
            else:
                # print(f"{Colors.FAIL}❌ Invalid option. Please try again.{Colors.ENDC}")  # [Security Fix]

    def view_latest_report(self):
        """View the latest test report"""
        html_reports = list(self.report_dir.glob("test_report_*.html"))
        if not html_reports:
            # print(f"{Colors.WARNING}⚠️  No test reports found.{Colors.ENDC}")  # [Security Fix]
            return

        latest = max(html_reports, key=lambda p: p.stat().st_mtime)
        # print(f"\n{Colors.CYAN}📊 Latest Report: {Colors.ENDC}{latest}")  # [Security Fix]

        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f"file://{latest.absolute()}")
            # print(f"Opened in default browser.")  # [Security Fix]
except Exception:
    pass
pass
# print(f"Open manually: file://{latest.absolute()}")  # [Security Fix]

def main():
    parser = argparse.ArgumentParser(description="Agentic Workflow Test Dashboard")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    parser.add_argument("--discover", action="store_true", help="Discover all tests")
    parser.add_argument("--run", help="Run specific test pattern")
    parser.add_argument("--category", choices=["core", "unit", "integration", "perf", "e2e", "golden"],
                       help="Run tests for specific category")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")

    args = parser.parse_args()

    dashboard = TestDashboard(args.root)

    if args.interactive:
        dashboard.interactive_mode()
    elif args.discover:
        dashboard.discover_tests()
    elif args.category:
        dashboard.run_category(args.category)
    elif args.run:
        dashboard.run_tests(args.run)
    else:
        # Default: run core tests
        dashboard.run_tests("test_zlm.py test_outreach_zse.py master_integration_suite_fixed.py")

if __name__ == "__main__":
    main()

