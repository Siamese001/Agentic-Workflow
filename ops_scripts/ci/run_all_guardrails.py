#!/usr/bin/env python3
"""
CI Guardrail Orchestrator with Timeout Protection and RCA

Runs all CI guardrails with timeout protection, progress reporting, and automatic
RCA generation on failures. Prevents CI hangs and provides comprehensive diagnostics.

Usage:
    python ops_scripts/ci/run_all_guardrails.py [--timeout SECONDS] [--verbose]

Exit codes:
    0 - All guardrails passed
    1 - One or more guardrails failed
    2 - Timeout or critical error
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Force UTF-8 encoding for Windows compatibility
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ops_scripts.ci.ci_timeout_decorator import ci_timeout, generate_rca, ci_progress_reporter

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class GuardrailResult:
    """Result of a guardrail execution."""
    name: str
    script: str
    passed: bool
    exit_code: int
    elapsed_time: float
    violations: int = 0
    output: str = ""
    error: Optional[str] = None
    timeout: bool = False
    rca_path: Optional[Path] = None


@dataclass
class GuardrailSuite:
    """Configuration for CI guardrail suite."""

    guardrails: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "Anti-Pattern Scanner",
            "script": "ops_scripts/ci/check_anti_patterns.py",
            "timeout": 120,
            "critical": True,
            "description": "Detects 6 categories of anti-patterns"
        },
        {
            "name": "Utility Silent Swallower Detection",
            "script": "ops_scripts/ci/check_utility_silent_swallowers.py",
            "timeout": 180,
            "critical": True,
            "description": "Prevents hidden failures in governance scripts"
        },
        {
            "name": "Plan Location Compliance",
            "script": "ops_scripts/ci/check_plan_location_compliance.py",
            "timeout": 30,
            "critical": True,
            "description": "Enforces Constitutional Rule #0"
        },
        {
            "name": "PowerShell Usage Ban",
            "script": "ops_scripts/ci/check_powershell_ban.py",
            "timeout": 300,
            "critical": False,
            "description": "Enforces Python-only subprocess operations"
        }
    ])


class GuardrailOrchestrator:
    """Orchestrates CI guardrail execution with timeout and RCA."""

    # guardian: allow-magic-config
    def __init__(self, default_timeout: int = 300, verbose: bool = False):
        self.default_timeout = default_timeout
        self.verbose = verbose
        self.results: List[GuardrailResult] = []
        self.start_time = time.time()

    def run_all_guardrails(self, suite: GuardrailSuite) -> bool:
        """
        Run all guardrails in the suite with timeout protection.

        Returns:
            True if all guardrails passed, False otherwise
        """
        print("=" * 80)
        print("CI GUARDRAIL SUITE - TIMEOUT PROTECTED")
        print("=" * 80)
        print(f"Total Guardrails: {len(suite.guardrails)}")
        print(f"Default Timeout: {self.default_timeout}s")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        print()

        all_passed = True

        with ci_progress_reporter(len(suite.guardrails), "Running Guardrails") as reporter:
            for i, guardrail_config in enumerate(suite.guardrails):
                reporter.update(i)

                result = self._run_single_guardrail(guardrail_config)
                self.results.append(result)

                if not result.passed:
                    all_passed = False
                    if guardrail_config.get("critical", True):
                        print(f"🚨 CRITICAL GUARDRAIL FAILED: {result.name}")

        self._print_summary()

        return all_passed

    def _run_single_guardrail(self, config: Dict[str, Any]) -> GuardrailResult:
        """Run a single guardrail with timeout protection."""
        name = config["name"]
        script = config["script"]
        timeout = config.get("timeout", self.default_timeout)

        print(f"\n{'=' * 80}")
        print(f"🔍 Running: {name}")
        print(f"📜 Script: {script}")
        print(f"⏱️  Timeout: {timeout}s")
        print(f"{'=' * 80}")

        start_time = time.time()
        script_path = PROJECT_ROOT / script

        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            print(f"❌ {error_msg}")

            rca_path = generate_rca(
                operation_name=name,
                error_type="SCRIPT_NOT_FOUND",
                error_message=error_msg,
                elapsed_time=0,
                context={"script": str(script_path)}
            )

            return GuardrailResult(
                name=name,
                script=script,
                passed=False,
                exit_code=127,
                elapsed_time=0,
                error=error_msg,
                rca_path=rca_path
            )

        try:
            # Run with timeout
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=PROJECT_ROOT
            )

            elapsed = time.time() - start_time
            passed = result.returncode == 0

            # Parse violations from output if available
            violations = self._parse_violations(result.stdout + result.stderr)

            if self.verbose or not passed:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            if passed:
                print(f"✅ {name} PASSED in {elapsed:.2f}s")
            else:
                print(f"❌ {name} FAILED in {elapsed:.2f}s (exit code: {result.returncode})")

                # Generate RCA for failure
                rca_path = generate_rca(
                    operation_name=name,
                    error_type="GUARDRAIL_FAILURE",
                    error_message=f"Exit code: {result.returncode}, Violations: {violations}",
                    elapsed_time=elapsed,
                    context={
                        "script": script,
                        "violations": violations,
                        "stdout": result.stdout[:500],
                        "stderr": result.stderr[:500]
                    }
                )

                return GuardrailResult(
                    name=name,
                    script=script,
                    passed=False,
                    exit_code=result.returncode,
                    elapsed_time=elapsed,
                    violations=violations,
                    output=result.stdout,
                    error=result.stderr,
                    rca_path=rca_path
                )

            return GuardrailResult(
                name=name,
                script=script,
                passed=True,
                exit_code=0,
                elapsed_time=elapsed,
                violations=violations,
                output=result.stdout
            )

        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            print(f"⏱️  {name} TIMEOUT after {elapsed:.2f}s")

            # Generate RCA for timeout
            rca_path = generate_rca(
                operation_name=name,
                error_type="TIMEOUT",
                error_message=f"Guardrail exceeded {timeout}s timeout limit",
                elapsed_time=elapsed,
                context={
                    "script": script,
                    "timeout_limit": timeout,
                    "stdout": e.stdout[:500] if e.stdout else "N/A",
                    "stderr": e.stderr[:500] if e.stderr else "N/A"
                }
            )

            return GuardrailResult(
                name=name,
                script=script,
                passed=False,
                exit_code=124,  # Standard timeout exit code
                elapsed_time=elapsed,
                timeout=True,
                error=f"Timeout after {timeout}s",
                rca_path=rca_path
            )

        except Exception as e:
            raise
            elapsed = time.time() - start_time
            print(f"💥 {name} EXCEPTION: {e}")

            # Generate RCA for exception
            rca_path = generate_rca(
                operation_name=name,
                error_type=type(e).__name__,
                error_message=str(e),
                elapsed_time=elapsed,
                context={"script": script}
            )

            return GuardrailResult(
                name=name,
                script=script,
                passed=False,
                exit_code=1,
                elapsed_time=elapsed,
                error=str(e),
                rca_path=rca_path
            )

    def _parse_violations(self, output: str) -> int:
        """Parse violation count from output."""
        import re

        # Look for common violation patterns
        patterns = [
            r'(\d+)\s+violations?\s+found',
            r'violations?:\s*(\d+)',
            r'total:\s*(\d+)',
            r'FAILED.*?(\d+)\s+violations?'
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 0

    def _print_summary(self):
        """Print comprehensive summary of all guardrail results."""
        total_elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("CI GUARDRAIL SUITE - SUMMARY")
        print("=" * 80)

        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        timeout_count = sum(1 for r in self.results if r.timeout)
        total_violations = sum(r.violations for r in self.results)

        print(f"Total Guardrails: {len(self.results)}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"⏱️  Timeouts: {timeout_count}")
        print(f"🚨 Total Violations: {total_violations}")
        print(f"⏱️  Total Time: {total_elapsed:.2f}s")
        print()

        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 80)

        for result in self.results:
            status_icon = "✅" if result.passed else "⏱️" if result.timeout else "❌"
            print(f"{status_icon} {result.name}")
            print(f"   Time: {result.elapsed_time:.2f}s")

            if result.violations > 0:
                print(f"   Violations: {result.violations}")

            if result.error:
                print(f"   Error: {result.error}")

            if result.rca_path:
                print(f"   RCA: {result.rca_path.relative_to(PROJECT_ROOT)}")

            print()

        # RCA summary
        rca_files = [r.rca_path for r in self.results if r.rca_path]
        if rca_files:
            print("📄 RCA FILES GENERATED:")
            for rca_path in rca_files:
                print(f"   - {rca_path.relative_to(PROJECT_ROOT)}")
            print()

        print("=" * 80)

        if passed_count == len(self.results):
            print("🎉 ALL GUARDRAILS PASSED")
        else:
            print(f"⚠️  {failed_count} GUARDRAIL(S) FAILED")

        print("=" * 80)

    def save_report(self, output_path: Path):
        """Save detailed JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_elapsed": time.time() - self.start_time,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "timeouts": sum(1 for r in self.results if r.timeout),
                "total_violations": sum(r.violations for r in self.results)
            },
            "results": [
                {
                    "name": r.name,
                    "script": r.script,
                    "passed": r.passed,
                    "exit_code": r.exit_code,
                    "elapsed_time": r.elapsed_time,
                    "violations": r.violations,
                    "timeout": r.timeout,
                    "error": r.error,
                    "rca_path": str(r.rca_path) if r.rca_path else None
                }
                for r in self.results
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f"📊 Report saved: {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run all CI guardrails with timeout protection")
    parser.add_argument("--timeout", type=int, default=300, help="Default timeout in seconds")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--report", type=str, help="Save JSON report to file")

    args = parser.parse_args()

    suite = GuardrailSuite()
    orchestrator = GuardrailOrchestrator(
        default_timeout=args.timeout,
        verbose=args.verbose
    )

    all_passed = orchestrator.run_all_guardrails(suite)

    if args.report:
        orchestrator.save_report(Path(args.report))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
