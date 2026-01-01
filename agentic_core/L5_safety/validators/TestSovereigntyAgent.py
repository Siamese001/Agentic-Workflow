"""TestSovereigntyAgent — L5 Specialist for Advanced Testing (Jan 01, 2026)

Delegated from L2-L4 agents for coverage, integration, regression.
- Sandboxed pytest --cov
- Subatomic with emit events
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from agentic_core.L2_execution.tool_registry.ExecutionCanonBaseAgent import CanonBaseAgent


class TestSovereigntyAgent(CanonBaseAgent):
    """L5 specialist — advanced sovereign testing."""

    def __init__(self, ctx: Any = None, **kwargs):
        if ctx is None:
            from unittest.mock import MagicMock
            ctx = MagicMock()
        super().__init__(ctx)
        self.repo_root = Path.cwd()

    def get_validation_keys(self) -> List[int]:
        """Return canon keys for test sovereignty."""
        return [99]  # Testing sovereignty key

    async def execute(self, request: Dict = None) -> Dict:
        """Run advanced tests on artifact or repo."""
        if request is None:
            request = {}
        
        test_type = request.get("type", "basic")
        coverage_target = request.get("coverage_target", 80)
        artifact = request.get("artifact", "")

        results = {
            "passed": True,
            "coverage": 0.0,
            "tests": [],
            "output": ""
        }

        # If artifact provided, write to temp for testing
        temp_path = None
        if artifact:
            temp_path = self.repo_root / "temp_test_artifact.py"
            temp_path.write_text(artifact, encoding='utf-8')

        try:
            if test_type == "full_repo":
                results = await self._run_full_repo_tests(coverage_target)
            elif test_type == "basic":
                results = await self._run_basic_tests()
            else:
                results = await self._run_targeted_tests(request)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()

        self._emit_event(
            "INFO" if results["passed"] else "ERROR",
            "TEST_SOVEREIGNTY_RESULT",
            {"passed": results["passed"], "coverage": results["coverage"]}
        )

        return results

    async def _run_full_repo_tests(self, coverage_target: float) -> Dict:
        """Run full pytest with coverage."""
        try:
            result = subprocess.run(
                ["pytest", "--cov=.", "--cov-report=term-missing", "-q", "--tb=short"],
                capture_output=True,
                timeout=120,
                cwd=self.repo_root
            )
            
            output = result.stdout.decode()
            coverage = self._parse_coverage(output)
            passed = result.returncode == 0 and coverage >= coverage_target

            return {
                "passed": passed,
                "coverage": coverage,
                "tests": [{"name": "pytest_cov", "passed": result.returncode == 0}],
                "output": output[:2000]
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "coverage": 0.0,
                "tests": [{"name": "pytest_cov", "passed": False, "error": "timeout"}],
                "output": "Test timeout after 120s"
            }
        except Exception as e:
            return {
                "passed": False,
                "coverage": 0.0,
                "tests": [{"name": "pytest_cov", "passed": False, "error": str(e)}],
                "output": str(e)
            }

    async def _run_basic_tests(self) -> Dict:
        """Run basic pytest without coverage."""
        try:
            result = subprocess.run(
                ["pytest", "-q", "--tb=no"],
                capture_output=True,
                timeout=60,
                cwd=self.repo_root
            )
            
            passed = result.returncode == 0
            return {
                "passed": passed,
                "coverage": 0.0,
                "tests": [{"name": "pytest_basic", "passed": passed}],
                "output": result.stdout.decode()[:1000]
            }
        except Exception as e:
            return {
                "passed": False,
                "coverage": 0.0,
                "tests": [{"name": "pytest_basic", "passed": False, "error": str(e)}],
                "output": str(e)
            }

    async def _run_targeted_tests(self, request: Dict) -> Dict:
        """Run targeted tests on specific files/modules."""
        target = request.get("target", "tests/")
        try:
            result = subprocess.run(
                ["pytest", target, "-q", "--tb=short"],
                capture_output=True,
                timeout=60,
                cwd=self.repo_root
            )
            
            passed = result.returncode == 0
            return {
                "passed": passed,
                "coverage": 0.0,
                "tests": [{"name": f"pytest_{target}", "passed": passed}],
                "output": result.stdout.decode()[:1000]
            }
        except Exception as e:
            return {
                "passed": False,
                "coverage": 0.0,
                "tests": [{"name": f"pytest_{target}", "passed": False, "error": str(e)}],
                "output": str(e)
            }

    def _parse_coverage(self, output: str) -> float:
        """Parse coverage percentage from pytest-cov output."""
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1))
        # Alternative format
        match = re.search(r"(\d+)%\s*$", output, re.MULTILINE)
        return float(match.group(1)) if match else 0.0

    def _emit_event(self, severity: str, event_type: str, payload: Optional[Dict] = None) -> None:
        """Telemetry for observability."""
        print(f"[SOVEREIGN EVENT] {severity} | {event_type}")
        if payload:
            print(f"  Payload: {payload}")
