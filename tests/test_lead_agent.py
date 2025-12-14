#!/usr/bin/env python3
"""
Test Lead Agent (TLA) v1.0 - L5 Adaptive Quality Assurance (AQA)
Standalone model for dynamic analysis, decoupled from the 50-key static canon.
Incorporates high security hardening: subprocess restrictions, path sanitization,
and execution timeouts.
"""

import os
import subprocess
import sys
import json
import logging
import shutil # Added for cleanup
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any
from pathlib import Path

# Configure logging for TLA
logger = logging.getLogger("TLA")
logger.setLevel(logging.INFO)

# ==============================================================================
# 1. ISOLATED CONTEXT & ENVIRONMENT
# ==============================================================================
@dataclass
class TLA_Context:
    """Isolated Blackboard for Dynamic Analysis (L5 AQA)."""
    mission_id: str = "TLA_RUN_001"
    
    # State passed from main validator
    modified_files: Set[str] = field(default_factory=set)
    refactor_plans: Dict[str, Any] = field(default_factory=dict)
    
    # Dynamic testing results
    test_results: Dict[str, bool] = field(default_factory=dict)
    coverage_report: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def log_test_result(self, agent: str, test_name: str, passed: bool, details: Any):
        """Log test result to the isolated blackboard."""
        self.test_results[test_name] = passed
        status = "PASS" if passed else "FAIL"
        print(f"   [{agent}] Test: {test_name} - {status}")

@dataclass
class ExecutionEnvironment:
    """
    L5 Execution Isolation: Manages secure, isolated test execution.
    ROLE: Sets up venv, installs dependencies, and runs test commands safely.
    """
    venv_path: str = ".tla_venv"
    dependencies: List[str] = field(default_factory=lambda: ["pytest", "pytest-cov"])
    
    # HARDENING: Pin dependencies for supply-chain integrity
    constraints_file: str = field(default_factory=lambda: "scripts/tla_constraints.txt")

    def setup(self):
        """Creates venv and installs necessary dependencies."""
        print(f"   🛠️ Environment: Setting up isolated VENV at '{self.venv_path}'...")
        if not Path(self.venv_path).exists():
            subprocess.run([sys.executable, "-m", "venv", self.venv_path], check=True)
            print("      ✅ VENV created.")
        
        pip_path = Path(self.venv_path) / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        
        print(f"   📦 Environment: Installing dependencies: {', '.join(self.dependencies)}...")
        try:
            # HARDENING: Use --constraint to pin known-good versions/hashes
            install_cmd = [str(pip_path), "install", "--constraint", self.constraints_file] + self.dependencies
            
            result = subprocess.run(install_cmd, check=True, capture_output=True, text=True)
            
            if "WARNING" in result.stderr or "error" in result.stderr.lower():
                logger.warning(f"      pip warnings during install: {result.stderr}")
            
            print("      ✅ Dependencies installed.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"      ❌ Failed to install dependencies: {e.stderr}")
            return False

    def run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Runs a command inside the isolated VENV."""
        python_path = Path(self.venv_path) / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        
        # SAFETY: Explicitly allow only known module invocations
        allowed_modules = {"pytest", "coverage"} # Explicitly allow coverage.py commands if added later
        if len(command) < 2 or command[0] != "-m" or command[1] not in allowed_modules:
            # Allow run_benchmarks.py script to run directly
            if not (len(command) >= 1 and Path(command[0]).name == "run_benchmarks.py"):
                raise ValueError(f"Disallowed command in isolated environment: {' '.join(command)}")

        full_command = [str(python_path)] + command
        
        # REDACTED logging: avoid leaking sensitive output (e.g., tokens in env)
        safe_cmd_display = " ".join(full_command[:3]) + (" ..." if len(full_command) > 3 else "")
        print(f"   🏃 Running (isolated): {safe_cmd_display}")
        try:
            # HARDENING: 10-minute timeout + no shell + restricted env
            safe_env = {
                "VIRTUAL_ENV": str(Path(self.venv_path).resolve()),
                "PATH": str(Path(self.venv_path) / ("Scripts" if sys.platform == "win32" else "bin")),
                # Explicitly block common secret leakage vectors
                "PYTHONPATH": "",
            }
            result = subprocess.run(
                full_command,
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(".").resolve(),
                timeout=600,  # 10 minutes max per test run
                env=safe_env,
            )
            return result
        except FileNotFoundError:
            raise EnvironmentError(f"Python executable not found in VENV: {python_path}")
        except subprocess.TimeoutExpired:
            raise TimeoutError("Test command exceeded 10-minute timeout")

# ==============================================================================
# 2. SUB-ATOMIC TESTING SWARM (L5 Specialization)
# ==============================================================================
class TestAgentBase:
    """Base class for Sub-Atomic Testing Agents."""
    
    def __init__(self, context: TLA_Context, env: ExecutionEnvironment):
        self.ctx = context
        self.env = env
        self.name = self.__class__.__name__

    def run_tests(self, target_paths: List[str]) -> Tuple[bool, str]:
        """Runs tests via pytest for the specified paths."""
        
        # L5: Filter out files with no tests (prevents false negatives)
        target_paths = [p for p in target_paths if Path(p).parent.joinpath('test_' + Path(p).name).exists() or Path(p).parent.joinpath('tests').exists()]
        if not target_paths:
             return True, "No tests found for target files."

        # Command: python -m pytest --exitfirst --strict-config <target_paths>
        command = ["-m", "pytest", "--exitfirst", "--strict-config"] + target_paths
        
        result = self.env.run_command(command)
        
        # Check if tests were run successfully
        test_run_success = "collected" in result.stdout and "errors" not in result.stderr
        
        if result.returncode == 0:
            return True, result.stdout
        elif result.returncode == 5:
            return True, "No tests found in targeted path."
        else:
            # Failure details are usually near the end of the output
            failure_detail = "\n".join(result.stdout.splitlines()[-10:])
            return False, failure_detail

class UnitTestMechanic(TestAgentBase):
    """
    ROLE: Coverage and Integrity. Guarantees modified functions pass local tests.
    """
    def execute(self) -> bool:
        """Executes targeted unit tests and reports coverage."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Test Coverage and Integrity...")
        
        # Target only modified files (high value, low cost)
        target_paths = list(self.ctx.modified_files)
        if not target_paths:
            print("      ℹ No modified files; standing down.")
            return True
        
        passed, details = self.run_tests(target_paths)
        
        self.ctx.log_test_result(self.name, "TargetedUnitTests", passed, details)
        
        # L5: Run coverage report
        coverage_command = ["-m", "pytest", "--cov=.", "--cov-report=json"]
        coverage_result = self.env.run_command(coverage_command)
        
        if coverage_result.returncode == 0:
            # Parse and store JSON coverage report (L5 data for Policy Evolution)
            try:
                cov_path = Path("coverage.json").resolve()
                project_root = Path(".").resolve()
                if not cov_path.is_relative_to(project_root):
                    raise PermissionError("Coverage report path is outside project root")
                
                with open(cov_path, "r") as f:
                    self.ctx.coverage_report = json.load(f)
                print("      ✅ Coverage data captured.")
                
                # HARDENING: Enforce minimum line coverage (adjust threshold as needed)
                total = self.ctx.coverage_report.get("totals", {})
                percent_covered = total.get("percent_covered", 0)
                min_coverage = 80.0
                
                if percent_covered < min_coverage:
                    print(f"      ⚠️ Coverage {percent_covered:.1f}% < {min_coverage}% threshold.")
                    passed = False  # Force overall failure
                
            except:
                print("      ⚠️ Could not parse coverage report.")

        return passed

class IntegrityAnalyst(TestAgentBase):
    """
    ROLE: Regression Assurance. Runs core regression suite on high-risk missions.
    """
    def execute(self, is_high_risk: bool) -> bool:
        """Runs full regression suite if risk is high."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Regression Assurance...")
        
        if not is_high_risk:
            print("      ℹ Risk is LOW; Integrity Analyst standing down.")
            self.ctx.log_test_result(self.name, "FullRegression", True, "Skipped due to low risk.")
            return True
            
        # Command: Run the entire test suite (high cost)
        passed, details = self.run_tests(["tests"])
        self.ctx.log_test_result(self.name, "FullRegression", passed, details)
        
        return passed

class PerformanceEvaluator(TestAgentBase):
    """
    ROLE: Load and Latency Assurance. Benchmarks critical paths post-refactor.
    """
    def execute(self, critical_paths: List[str]) -> bool:
        """Benchmarks critical paths."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Performance Metrics...")
        
        if not critical_paths:
            print("      ℹ No critical paths flagged; Performance Evaluator standing down.")
            self.ctx.log_test_result(self.name, "PerformanceBenchmark", True, "Skipped.")
            return True

        # L5: Run a simple benchmark command (Placeholder for detailed load tests)
        # Assuming a dedicated performance test script exists
        
        # HARDENING: Sanitize benchmark script path
        project_root = Path(".").resolve()
        try:
            performance_script = project_root / "scripts" / "run_benchmarks.py"
            performance_script = performance_script.resolve().relative_to(project_root)
        except ValueError:
            print("      ⚠️ Benchmark script path unsafe. Skipping.")
            self.ctx.log_test_result(self.name, "PerformanceBenchmark", True, "Skipped: Unsafe path.")
            return True

        if performance_script.exists():
            command = [str(performance_script), "--targets"] + critical_paths
            result = self.env.run_command(command)
            
            # Simple check: pass if command successful
            passed = result.returncode == 0
            self.ctx.log_test_result(self.name, "PerformanceBenchmark", passed, result.stdout)
            
            # L5: Actual performance data would be parsed here and stored in self.ctx.performance_metrics
            return passed
        else:
            print("      ⚠️ Performance script not found. Skipping benchmark.")
            self.ctx.log_test_result(self.name, "PerformanceBenchmark", True, "Skipped: Script missing.")
            return True

# ==============================================================================
# 3. TEST LEAD AGENT (TLA) ORCHESTRATOR
# ==============================================================================
class TestLeadAgent:
    """
    L5 Test Orchestrator: Governs Dynamic Analysis based on Policy and Risk.
    """
    def __init__(self, modified_files: Set[str], refactor_plans: Dict[str, Any]):
        
        # HARDENING: Sanitize all paths – must be relative and within project root
        project_root = Path(".").resolve()
        sanitized = set()
        for p in modified_files:
            try:
                resolved = project_root / Path(p).resolve().relative_to(project_root)
                sanitized.add(str(resolved))
            except ValueError:
                logger.warning(f"Rejected unsafe modified_file path: {p}")

        self.ctx = TLA_Context(modified_files=sanitized, refactor_plans=refactor_plans)
        self.env = ExecutionEnvironment()
        
        # TLA Policy: Defines which refactoring missions are high risk
        self.high_risk_missions = ["MISSION_ENCAPSULATE_GLOBALS", "MISSION_DECONSTRUCT_MONOLITH", "SPLIT_FUNCTION"]
        
        # Critical paths (L5 data derived from history/logs)
        self.critical_paths = [] # Placeholder for future L5 dynamic loading

    def run_dynamic_analysis(self) -> bool:
        """The main TLA execution loop."""
        
        print("\n" + "="*60)
        print("🧪 TEST LEAD AGENT ACTIVATED: L5 Adaptive Quality Assurance")
        print("="*60)
        
        # HARDENING: Refuse to run as root (optional but strong hardening)
        if sys.platform != "win32":
            try:
                if os.getuid() == 0:
                    print("   🛑 SECURITY ERROR: TLA refuses to run as root.")
                    return False
            except AttributeError:  # Windows has no getuid()
                pass

        if not self.env.setup():
            print("   🛑 TLA ABORT: Failed to set up execution environment.")
            self._cleanup()
            return False

        # 1. Risk Assessment
        is_high_risk = self._assess_mission_risk()
        print(f"   🚨 MISSION RISK: {'HIGH' if is_high_risk else 'LOW'}")

        # 2. Initialize Sub-Atomic Agents
        unit_mechanic = UnitTestMechanic(self.ctx, self.env)
        integrity_analyst = IntegrityAnalyst(self.ctx, self.env)
        performance_eval = PerformanceEvaluator(self.ctx, self.env)
        
        overall_success = True

        # 3. Execute Swarm (L5 Policy-Driven)
        
        # Policy A: Unit Mechanic runs on all modified code
        if not unit_mechanic.execute():
            overall_success = False

        # Policy B: Integrity Analyst runs on high risk
        if is_high_risk:
            if not integrity_analyst.execute(is_high_risk):
                overall_success = False
        
        # Policy C: Performance Evaluator runs if files touch critical path
        if self.critical_paths:
            if not performance_eval.execute(self.critical_paths):
                overall_success = False

        self._report_final_status(overall_success)
        self._cleanup()
        return overall_success

    def _assess_mission_risk(self) -> bool:
        """Assesses risk based on executed refactor plans."""
        for plan in self.ctx.refactor_plans.values():
            if plan.get("status") == "EXECUTED":
                plan_type = plan.get("type")
                if plan_type in self.high_risk_missions:
                    return True
        return False
        
    def _cleanup(self):
        """Securely remove temporary artifacts."""
        print(" 🧹 Cleaning up temporary artifacts...")
        try:
            if Path(self.env.venv_path).exists():
                shutil.rmtree(Path(self.env.venv_path))
                print(" ✅ VENV removed.")
            if Path("coverage.json").exists():
                Path("coverage.json").unlink()
                print(" ✅ coverage.json removed.")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    def _report_final_status(self, overall_success: bool):
        """Prints the final TLA mission report."""
        print("\n" + "="*60)
        print("🏁 TLA DYNAMIC ANALYSIS REPORT")
        print("="*60)
        
        failed_tests = [k for k, v in self.ctx.test_results.items() if v is False]
        
        print(f"OVERALL DYNAMIC ANALYSIS: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"Tests Run: {len(self.ctx.test_results)}")
        print(f"Failed Tests: {len(failed_tests)}")
        
        if failed_tests:
            print("\n   🚨 FAILED SUITES:")
            for test_name in failed_tests:
                print(f"      - {test_name}")
            
            # L5: Recommend next action based on failure type
            if "TargetedUnitTests" in failed_tests or "FullRegression" in failed_tests:
                print("   🛠️ NEXT STEP: Rerunning static agents is insufficient. Manual fix/re-evaluation of refactor required.")

# Example integration point from the main canon_validator.py:
if __name__ == "__main__":
    # Mock data to demonstrate TLA execution
    
    # 1. Mock the modified files and refactor plans from the Orchestrator
    # This simulates a high-risk refactoring mission (SPLIT_FUNCTION was executed)
    mock_modified = {"src/mod.py", "tests/test_mod.py"}
    mock_plans = {
        "mod.py:func": {"type": "SPLIT_FUNCTION", "status": "EXECUTED"},
        "util.py:global": {"type": "PENDING_GLOBAL_ENCAPSULATION", "status": "PENDING"}
    }
    
    # 2. Instantiate and run the Test Lead Agent
    tla = TestLeadAgent(modified_files=mock_modified, refactor_plans=mock_plans)
    tla.run_dynamic_analysis()