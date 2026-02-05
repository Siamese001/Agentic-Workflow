#!/usr/bin/env python3
"""
Consolidated Dashboard Verification Script
==========================================

Single entry point for all dashboard verification tasks.

Usage:
    python scripts/verify_dashboard.py --quick       # Fast checks (no browser)
    python scripts/verify_dashboard.py --full        # All checks including data validation
    python scripts/verify_dashboard.py --deployment  # Pre-deployment validation with Playwright

This script consolidates:
- verify_dashboard_simple.py (--quick)
- verify_dashboard_state.py (--quick)
- verify_dashboard_columns.py (--full)
- verify_dashboard_updates.py (--full)
- verify_dashboard_deployment.py (--deployment)
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

# Setup project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    DASHBOARD_DIR,
    get_validated_project_root,
)


class DashboardVerifier:
    """Consolidated dashboard verification class."""

    def __init__(self):
        self.project_root = get_validated_project_root()
        self.dashboard_dir = self.project_root / DASHBOARD_DIR
        self.html_file = self.dashboard_dir / "autonomy_dashboard.html"
        self.data_dir = self.dashboard_dir / "data"
        self.js_dir = self.dashboard_dir / "js"
        self.css_dir = self.dashboard_dir / "css"
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed: int = 0
        self.failed: int = 0

    def _check(self, condition: bool, success_msg: str, failure_msg: str) -> bool:
        """Record a check result."""
        if condition:
            print(f"   ✅ {success_msg}")
            self.passed += 1
            return True
        else:
            print(f"   ❌ {failure_msg}")
            self.errors.append(failure_msg)
            self.failed += 1
            return False

    def _warn(self, msg: str):
        """Record a warning."""
        print(f"   ⚠️  {msg}")
        self.warnings.append(msg)

    def verify_html_exists(self) -> tuple[bool, str]:
        """Verify dashboard HTML file exists."""
        print("\n1. Checking HTML file existence...")
        if not self.html_file.exists():
            self._check(False, "", f"HTML file not found: {self.html_file}")
            return False, ""

        size_kb = self.html_file.stat().st_size / 1024
        self._check(True, f"HTML file exists ({size_kb:.1f}KB)", "")
        return True, self.html_file.read_text(encoding="utf-8")

    def verify_phase5_sections(self, html: str) -> bool:
        """Verify Phase 5 sections exist in HTML."""
        print("\n2. Checking Phase 5 sections...")
        sections = [
            ("Meta-Learning Activity", "🧠 Meta-Learning Activity"),
            ("Redis cache Activity", "💾 Redis cache Activity"),
            ("Pinecone Vector Operations", "🔍 Pinecone Vector Operations"),
            ("Agent Execution Flow", "⚡ Agent Execution Flow"),
        ]

        all_found = True
        for _section_id, section_text in sections:
            found = section_text in html
            self._check(found, f"Found: {section_text}", f"Missing: {section_text}")
            all_found = all_found and found

        return all_found

    def verify_container_elements(self, html: str) -> bool:
        """Verify container elements exist in HTML."""
        print("\n3. Checking container elements...")
        containers = [
            "meta-stats",
            "strategy-weights",
            "experience-stream",
            "pattern-timeline",
            "redis-stats",
            "redis-log",
            "pinecone-stats",
            "pinecone-queries",
            "layer-flow",
            "execution-summary",
            "execution-timeline",
        ]

        all_found = True
        for container in containers:
            found = f'id="{container}"' in html
            self._check(found, f"Found: #{container}", f"Missing: #{container}")
            all_found = all_found and found

        return all_found

    def verify_js_includes(self, html: str) -> bool:
        """Verify JavaScript includes in HTML."""
        print("\n4. Checking JavaScript includes...")
        js_includes = [
            "meta-learning-panel.js",
            "redis-monitor.js",
            "pinecone-monitor.js",
            "execution-flow.js",
            "meta-learning-controller.js",
        ]

        all_found = True
        for js_file in js_includes:
            found = js_file in html
            self._check(found, f"Included: {js_file}", f"Missing: {js_file}")
            all_found = all_found and found

        return all_found

    def verify_js_files_exist(self) -> bool:
        """Verify JavaScript files exist on disk."""
        print("\n5. Checking JavaScript files exist...")
        js_files = [
            self.js_dir / "components" / "meta-learning-panel.js",
            self.js_dir / "components" / "redis-monitor.js",
            self.js_dir / "components" / "pinecone-monitor.js",
            self.js_dir / "components" / "execution-flow.js",
            self.js_dir / "controllers" / "meta-learning-controller.js",
        ]

        all_found = True
        for js_file in js_files:
            if js_file.exists():
                size = js_file.stat().st_size
                self._check(True, f"Exists: {js_file.name} ({size:,} bytes)", "")
            else:
                self._check(False, "", f"Missing: {js_file}")
                all_found = False

        return all_found

    def verify_css_files_exist(self) -> bool:
        """Verify CSS files exist."""
        print("\n6. Checking CSS files...")
        css_file = self.css_dir / "meta-learning.css"
        if css_file.exists():
            size = css_file.stat().st_size
            return self._check(True, f"Exists: meta-learning.css ({size:,} bytes)", "")
        else:
            return self._check(False, "", "Missing: meta-learning.css")

    def verify_data_injection(self, html: str) -> bool:
        """Verify data is injected into HTML."""
        print("\n7. Checking data injection...")

        has_dashboard_data = (
            "const dashboardData = [" in html and "const dashboardData = [];" not in html
        )
        has_recommendations = (
            "const recommendationsData = [" in html
            and "const recommendationsData = [];" not in html
        )

        self._check(has_dashboard_data, "dashboardData populated", "dashboardData empty or missing")
        self._check(
            has_recommendations,
            "recommendationsData populated",
            "recommendationsData empty or missing",
        )

        if has_dashboard_data:
            territory_count = html.count('"Territory"')
            print(f"      Territories found: {territory_count}")

        return has_dashboard_data

    def verify_plotly(self, html: str) -> bool:
        """Verify Plotly configuration."""
        print("\n8. Checking Plotly configuration...")

        plotly_file = self.dashboard_dir / "plotly.min.js"
        if plotly_file.exists():
            size_mb = plotly_file.stat().st_size / 1024 / 1024
            if size_mb >= 3.0:
                self._check(True, f"plotly.min.js exists ({size_mb:.1f}MB)", "")
            else:
                self._warn(f"plotly.min.js is too small ({size_mb:.1f}MB) - may be corrupted")
        else:
            self._warn("plotly.min.js not found locally - will use CDN fallback")

        # Check for CDN fallback
        cdn_match = re.search(r"https://[^'\"]+plotly[^'\"]+\.js", html)
        if cdn_match:
            print(f"      CDN fallback: {cdn_match.group(0)}")

        return True

    def verify_dashboard_data_file(self) -> bool:
        """Verify dashboard_data.js file."""
        print("\n9. Checking dashboard_data.js...")

        data_file = self.data_dir / "dashboard_data.js"
        if not data_file.exists():
            return self._check(False, "", f"Missing: {data_file}")

        content = data_file.read_text(encoding="utf-8")
        lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
        content_clean = "\n".join(lines).replace("window.dashboardData = ", "").strip().rstrip(";")

        try:
            data = json.loads(content_clean)
            total_row = next((r for r in data if r.get("Territory") == "TOTAL"), None)

            if total_row:
                self._check(True, f"TOTAL row found with {len(total_row)} columns", "")
                print(f"      Health: {total_row.get('Health', 'N/A')}")
                print(f"      Code Quality: {total_row.get('Code Quality Score', 'N/A')}")
                return True
            else:
                return self._check(False, "", "TOTAL row not found in dashboard_data.js")
        except json.JSONDecodeError as e:
            return self._check(False, "", f"Invalid JSON in dashboard_data.js: {e}")

    def verify_kpi_elements(self, html: str) -> bool:
        """Verify KPI elements exist."""
        print("\n10. Checking KPI elements...")

        elements = [
            ("healthScoreBox", "Health Score box"),
            ("codeQualityBox", "Code Quality box"),
            ("baseInheritanceBox", "Base Inheritance box"),
        ]

        all_found = True
        for element_id, desc in elements:
            found = f'id="{element_id}"' in html
            self._check(found, f"Found: {desc}", f"Missing: {desc}")
            all_found = all_found and found

        return all_found

    def run_quick(self) -> int:
        """Run quick verification (no browser)."""
        print("=" * 70)
        print("DASHBOARD QUICK VERIFICATION")
        print("=" * 70)

        exists, html = self.verify_html_exists()
        if not exists:
            return 1

        self.verify_phase5_sections(html)
        self.verify_container_elements(html)
        self.verify_js_includes(html)
        self.verify_js_files_exist()
        self.verify_css_files_exist()
        self.verify_data_injection(html)
        self.verify_plotly(html)

        return self._print_summary()

    def run_full(self) -> int:
        """Run full verification (no browser)."""
        print("=" * 70)
        print("DASHBOARD FULL VERIFICATION")
        print("=" * 70)

        exists, html = self.verify_html_exists()
        if not exists:
            return 1

        self.verify_phase5_sections(html)
        self.verify_container_elements(html)
        self.verify_js_includes(html)
        self.verify_js_files_exist()
        self.verify_css_files_exist()
        self.verify_data_injection(html)
        self.verify_plotly(html)
        self.verify_dashboard_data_file()
        self.verify_kpi_elements(html)

        return self._print_summary()

    def run_deployment(self) -> int:
        """Run deployment verification with Playwright."""
        print("=" * 70)
        print("DASHBOARD DEPLOYMENT VERIFICATION (Playwright)")
        print("=" * 70)

        # First run full verification
        exists, html = self.verify_html_exists()
        if not exists:
            return 1

        self.verify_phase5_sections(html)
        self.verify_container_elements(html)
        self.verify_js_files_exist()
        self.verify_dashboard_data_file()

        # Check if Playwright is available
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("\n❌ Playwright not installed!")
            print("\nInstall with:")
            print("  pip install playwright")
            print("  playwright install chromium")
            return 1

        # Start dashboard server
        print("\n11. Starting dashboard server on port 8765...")
        from agentic_core.utils.security import safe_popen

        server_process = safe_popen(
            [sys.executable, "-m", "http.server", "8765"],
            cwd=str(self.dashboard_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        time.sleep(2)
        print("   ✅ Server started")

        try:
            with sync_playwright() as p:
                print("\n12. Launching browser...")
                browser = p.chromium.launch(
                    headless=True, args=["--disable-cache", "--disable-application-cache"]
                )

                context = browser.new_context(viewport={"width": 1920, "height": 1080})
                page = context.new_page()

                # Track JavaScript errors
                js_errors = []
                page.on("pageerror", lambda exc: js_errors.append(str(exc)))

                print("\n13. Navigating to dashboard...")
                page.goto("http://localhost:8765/autonomy_dashboard.html", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                time.sleep(3)

                # Check for JavaScript errors
                if js_errors:
                    for err in js_errors[:5]:
                        self._check(False, "", f"JavaScript error: {err}")
                else:
                    self._check(True, "No JavaScript errors", "")

                # Check tables rendered
                print("\n14. Checking table rendering...")
                table_rows = page.locator("#kpiGrid table tbody tr").count()
                self._check(
                    table_rows > 0,
                    f"Table 1 rendered with {table_rows} rows",
                    "Table 1 not rendered",
                )

                # Check TOTAL row position
                if table_rows > 0:
                    first_row_text = page.locator("#kpiGrid table tbody tr").first.text_content()
                    self._check(
                        "TOTAL" in first_row_text,
                        "TOTAL row at top of Table 1",
                        "TOTAL row not at top",
                    )

                # Take screenshot
                screenshot_path = self.dashboard_dir / "verification_screenshot.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"\n   📸 Screenshot saved: {screenshot_path}")

                browser.close()

        finally:
            server_process.terminate()
            print("\n   Server stopped")

        return self._print_summary()

    def _print_summary(self) -> int:
        """Print verification summary and return exit code."""
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"\n   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n   Errors:")
            for err in self.errors:
                print(f"      - {err}")

        if self.warnings:
            print("\n   Warnings:")
            for warn in self.warnings:
                print(f"      - {warn}")

        print("\n" + "=" * 70)

        if self.failed == 0:
            print("✅ VERIFICATION PASSED")
            return 0
        else:
            print("❌ VERIFICATION FAILED")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="Consolidated Dashboard Verification Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/verify_dashboard.py --quick       # Fast checks (no browser)
  python scripts/verify_dashboard.py --full        # All checks including data validation
  python scripts/verify_dashboard.py --deployment  # Pre-deployment validation with Playwright
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--quick", action="store_true", help="Run quick verification (no browser)")
    group.add_argument("--full", action="store_true", help="Run full verification (no browser)")
    group.add_argument(
        "--deployment", action="store_true", help="Run deployment verification with Playwright"
    )

    args = parser.parse_args()

    verifier = DashboardVerifier()

    if args.quick:
        return verifier.run_quick()
    elif args.full:
        return verifier.run_full()
    elif args.deployment:
        return verifier.run_deployment()


if __name__ == "__main__":
    sys.exit(main())
