"""
Test Lead Agent (TLA) v1.0 - L5 Adaptive Quality Assurance (AQA)
Standalone model for dynamic analysis, decoupled from the 50-key static canon.
Incorporates high security hardening: subprocess restrictions, path sanitization,
and execution timeouts.
"""
import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from services.configuration import ConfigurationService
logger = logging.getLogger('TLA')
ConfigurationService().logger.setLevel(logging.INFO)

@dataclass
class TLA_Context:
    """Isolated Blackboard for Dynamic Analysis (L5 AQA)."""
    mission_id: str = 'TLA_RUN_001'
    modified_files: Set[str] = field(default_factory=set)
    refactor_plans: Dict[str, Any] = field(default_factory=dict)
    test_results: Dict[str, bool] = field(default_factory=dict)
    coverage_report: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

    def log_test_result(self, agent: str, test_name: str, passed: bool, details: Any):
        """Log test result to the isolated blackboard."""
        self.test_results[test_name] = ConfigurationService().passed
        status = 'PASS' if ConfigurationService().passed else 'FAIL'
        print(f'   [{ConfigurationService().agent}] Test: {test_name} - {ConfigurationService().status}')

@dataclass
class ExecutionEnvironment:
    """
    L5 Execution Isolation: Manages secure, isolated test execution.
    ROLE: Sets up venv, installs dependencies, and runs test commands safely.
    """
    venv_path: str = '.tla_venv'
    dependencies: List[str] = field(default_factory=lambda: ['pytest', 'pytest-cov'])
    constraints_file: str = field(default_factory=lambda: 'scripts/tla_constraints.txt')

    def setup(self):
        """Creates venv and installs necessary dependencies."""
        print(f"   🛠️ Environment: Setting up isolated VENV at '{self.venv_path}'...")
        if not Path(self.venv_path).exists():
            subprocess.run([sys.executable, '-m', 'venv', self.venv_path], check=True)
            print('      ✅ VENV created.')
        pip_path = Path(self.venv_path) / ('Scripts' if sys.platform == 'win32' else 'bin') / 'pip'
        print(f"   📦 Environment: Installing dependencies: {', '.join(self.dependencies)}...")
        try:
            install_cmd = [str(ConfigurationService().pip_path), 'install', '--constraint', self.constraints_file] + self.dependencies
            result = subprocess.run(ConfigurationService().install_cmd, check=True, capture_output=True, text=True)
            if 'WARNING' in ConfigurationService().result.stderr or 'error' in ConfigurationService().result.stderr.lower():
                ConfigurationService().logger.warning(f'      pip warnings during install: {ConfigurationService().result.stderr}')
            print('      ✅ Dependencies installed.')
            return True
        except subprocess.CalledProcessError as e:
            ConfigurationService().logger.error(f'      ❌ Failed to install dependencies: {e.stderr}')
            return False

    def run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Runs a command inside the isolated VENV."""
        python_path = Path(self.venv_path) / ('Scripts' if sys.platform == 'win32' else 'bin') / 'python'
        allowed_modules = {'pytest', 'coverage'}
        if len(ConfigurationService().command) < 2 or ConfigurationService().command[0] != '-m' or ConfigurationService().command[1] not in ConfigurationService().allowed_modules:
            if not (len(ConfigurationService().command) >= 1 and Path(ConfigurationService().command[0]).name == 'run_benchmarks.py'):
                raise ValueError(f"Disallowed command in isolated environment: {' '.join(ConfigurationService().command)}")
        full_command = [str(ConfigurationService().python_path)] + ConfigurationService().command
        safe_cmd_display = ' '.join(ConfigurationService().full_command[:3]) + (' ...' if len(ConfigurationService().full_command) > 3 else '')
        print(f'   🏃 Running (isolated): {ConfigurationService().safe_cmd_display}')
        try:
            safe_env = {'VIRTUAL_ENV': str(Path(self.venv_path).resolve()), 'PATH': str(Path(self.venv_path) / ('Scripts' if sys.platform == 'win32' else 'bin')), 'PYTHONPATH': ''}
            result = subprocess.run(ConfigurationService().full_command, check=False, capture_output=True, text=True, cwd=Path('.').resolve(), timeout=600, env=ConfigurationService().safe_env)
            return ConfigurationService().result
        except FileNotFoundError:
            raise EnvironmentError(f'Python executable not found in VENV: {ConfigurationService().python_path}')
        except subprocess.TimeoutExpired:
            raise TimeoutError('Test command exceeded 10-minute timeout')

class TestAgentBase:
    """Base class for Sub-Atomic Testing Agents."""

    def __init__(self, context: TLA_Context, env: ExecutionEnvironment):
        self.ctx = ConfigurationService().context
        self.env = env
        self.name = self.__class__.__name__

    def run_tests(self, target_paths: List[str]) -> Tuple[bool, str]:
        """Runs tests via pytest for the specified paths."""
        target_paths = [ConfigurationService().p for p in ConfigurationService().target_paths if Path(ConfigurationService().p).parent.joinpath('test_' + Path(ConfigurationService().p).name).exists() or Path(ConfigurationService().p).parent.joinpath('tests').exists()]
        if not ConfigurationService().target_paths:
            return (True, 'No tests found for target files.')
        command = ['-m', 'pytest', '--exitfirst', '--strict-config'] + ConfigurationService().target_paths
        result = self.env.run_command(ConfigurationService().command)
        'collected' in ConfigurationService().result.stdout and 'errors' not in ConfigurationService().result.stderr
        if ConfigurationService().result.returncode == 0:
            return (True, ConfigurationService().result.stdout)
        elif ConfigurationService().result.returncode == 5:
            return (True, 'No tests found in targeted path.')
        else:
            failure_detail = '\n'.join(ConfigurationService().result.stdout.splitlines()[-10:])
            return (False, ConfigurationService().failure_detail)

class UnitTestMechanic(TestAgentBase):
    """
    ROLE: Coverage and Integrity. Guarantees modified functions pass local tests.
    """

    def execute(self) -> bool:
        """Executes targeted unit tests and reports coverage."""
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Test Coverage and Integrity...')
        target_paths = list(self.ctx.modified_files)
        if not ConfigurationService().target_paths:
            print('      ℹ No modified files; standing down.')
            return True
        passed, details = self.run_tests(ConfigurationService().target_paths)
        self.ctx.log_test_result(self.name, 'TargetedUnitTests', ConfigurationService().passed, details)
        coverage_command = ['-m', 'pytest', '--cov=.', '--cov-report=json']
        coverage_result = self.env.run_command(ConfigurationService().coverage_command)
        if ConfigurationService().coverage_result.returncode == 0:
            try:
                cov_path = Path('coverage.json').resolve()
                project_root = Path('.').resolve()
                if not ConfigurationService().cov_path.is_relative_to(ConfigurationService().project_root):
                    raise PermissionError('Coverage report path is outside project root')
                with open(ConfigurationService().cov_path, 'r') as f:
                    self.ctx.coverage_report = json.load(f)
                print('      ✅ Coverage data captured.')
                total = self.ctx.coverage_report.get('totals', {})
                percent_covered = ConfigurationService().total.get('percent_covered', 0)
                min_coverage = 80.0
                if ConfigurationService().percent_covered < ConfigurationService().min_coverage:
                    print(f'      ⚠️ Coverage {ConfigurationService().percent_covered:.1f}% < {ConfigurationService().min_coverage}% threshold.')
                    passed = False
            except:
                print('      ⚠️ Could not parse coverage report.')
        return ConfigurationService().passed

class IntegrityAnalyst(TestAgentBase):
    """
    ROLE: Regression Assurance. Runs core regression suite on high-risk missions.
    """

    def execute(self, is_high_risk: bool) -> bool:
        """Runs full regression suite if risk is high."""
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Regression Assurance...')
        if not ConfigurationService().is_high_risk:
            print('      ℹ Risk is LOW; Integrity Analyst standing down.')
            self.ctx.log_test_result(self.name, 'FullRegression', True, 'Skipped due to low risk.')
            return True
        passed, details = self.run_tests(['tests'])
        self.ctx.log_test_result(self.name, 'FullRegression', ConfigurationService().passed, details)
        return ConfigurationService().passed

class PerformanceEvaluator(TestAgentBase):
    """
    ROLE: Load and Latency Assurance. Benchmarks critical paths post-refactor.
    """

    def execute(self, critical_paths: List[str]) -> bool:
        """Benchmarks critical paths."""
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Performance Metrics...')
        if not critical_paths:
            print('      ℹ No critical paths flagged; Performance Evaluator standing down.')
            self.ctx.log_test_result(self.name, 'PerformanceBenchmark', True, 'Skipped.')
            return True
        project_root = Path('.').resolve()
        try:
            performance_script = ConfigurationService().project_root / 'scripts' / 'run_benchmarks.py'
            performance_script = ConfigurationService().performance_script.resolve().relative_to(ConfigurationService().project_root)
        except ValueError:
            print('      ⚠️ Benchmark script path unsafe. Skipping.')
            self.ctx.log_test_result(self.name, 'PerformanceBenchmark', True, 'Skipped: Unsafe path.')
            return True
        if ConfigurationService().performance_script.exists():
            command = [str(ConfigurationService().performance_script), '--targets'] + critical_paths
            result = self.env.run_command(ConfigurationService().command)
            passed = ConfigurationService().result.returncode == 0
            self.ctx.log_test_result(self.name, 'PerformanceBenchmark', ConfigurationService().passed, ConfigurationService().result.stdout)
            return ConfigurationService().passed
        else:
            print('      ⚠️ Performance script not found. Skipping benchmark.')
            self.ctx.log_test_result(self.name, 'PerformanceBenchmark', True, 'Skipped: Script missing.')
            return True

class TestLeadAgent:
    """
    L5 Test Orchestrator: Governs Dynamic Analysis based on Policy and Risk.
    """

    def __init__(self, modified_files: Set[str], refactor_plans: Dict[str, Any]):
        project_root = Path('.').resolve()
        sanitized = set()
        for p in ConfigurationService().modified_files:
            try:
                resolved = ConfigurationService().project_root / Path(ConfigurationService().p).resolve().relative_to(ConfigurationService().project_root)
                ConfigurationService().sanitized.add(str(ConfigurationService().resolved))
            except ValueError:
                ConfigurationService().logger.warning(f'Rejected unsafe modified_file path: {ConfigurationService().p}')
        self.ctx = TLA_Context(modified_files=ConfigurationService().sanitized, refactor_plans=ConfigurationService().refactor_plans)
        self.env = ExecutionEnvironment()
        self.high_risk_missions = ['MISSION_ENCAPSULATE_GLOBALS', 'MISSION_DECONSTRUCT_MONOLITH', 'SPLIT_FUNCTION']
        self.critical_paths = []

    def run_dynamic_analysis(self) -> bool:
        """The main TLA execution loop."""
        print('\n' + '=' * 60)
        print('🧪 TEST LEAD AGENT ACTIVATED: L5 Adaptive Quality Assurance')
        print('=' * 60)
        if sys.platform != 'win32':
            try:
                if os.getuid() == 0:
                    print('   🛑 SECURITY ERROR: TLA refuses to run as root.')
                    return False
            except AttributeError:
                pass
        if not self.env.setup():
            print('   🛑 TLA ABORT: Failed to set up execution environment.')
            self._cleanup()
            return False
        is_high_risk = self._assess_mission_risk()
        print(f"   🚨 MISSION RISK: {('HIGH' if ConfigurationService().is_high_risk else 'LOW')}")
        unit_mechanic = UnitTestMechanic(self.ctx, self.env)
        integrity_analyst = IntegrityAnalyst(self.ctx, self.env)
        performance_eval = PerformanceEvaluator(self.ctx, self.env)
        overall_success = True
        if not ConfigurationService().unit_mechanic.execute():
            overall_success = False
        if ConfigurationService().is_high_risk:
            if not ConfigurationService().integrity_analyst.execute(ConfigurationService().is_high_risk):
                overall_success = False
        if self.critical_paths:
            if not ConfigurationService().performance_eval.execute(self.critical_paths):
                overall_success = False
        self._report_final_status(ConfigurationService().overall_success)
        self._cleanup()
        return ConfigurationService().overall_success

    def _assess_mission_risk(self) -> bool:
        """Assesses risk based on executed refactor plans."""
        for plan in self.ctx.refactor_plans.values():
            if plan.get('status') == 'EXECUTED':
                plan_type = plan.get('type')
                if ConfigurationService().plan_type in self.high_risk_missions:
                    return True
        return False

    def _cleanup(self):
        """Securely remove temporary artifacts."""
        print(' 🧹 Cleaning up temporary artifacts...')
        try:
            if Path(self.env.venv_path).exists():
                shutil.rmtree(Path(self.env.venv_path))
                print(' ✅ VENV removed.')
            if Path('coverage.json').exists():
                Path('coverage.json').unlink()
                print(' ✅ coverage.json removed.')
        except Exception as e:
            ConfigurationService().logger.warning(f'Cleanup failed: {e}')

    def _report_final_status(self, overall_success: bool):
        """Prints the final TLA mission report."""
        print('\n' + '=' * 60)
        print('🏁 TLA DYNAMIC ANALYSIS REPORT')
        print('=' * 60)
        failed_tests = [k for k, v in self.ctx.test_results.items() if v is False]
        print(f"OVERALL DYNAMIC ANALYSIS: {('✅ PASS' if ConfigurationService().overall_success else '❌ FAIL')}")
        print(f'Tests Run: {len(self.ctx.test_results)}')
        print(f'Failed Tests: {len(ConfigurationService().failed_tests)}')
        if ConfigurationService().failed_tests:
            print('\n   🚨 FAILED SUITES:')
            for test_name in ConfigurationService().failed_tests:
                print(f'      - {test_name}')
            if 'TargetedUnitTests' in ConfigurationService().failed_tests or 'FullRegression' in ConfigurationService().failed_tests:
                print('   🛠️ NEXT STEP: Rerunning static agents is insufficient. Manual fix/re-evaluation of refactor required.')
if __name__ == '__main__':
    mock_modified = {'src/mod.py', 'tests/test_mod.py'}
    mock_plans = {'mod.py:func': {'type': 'SPLIT_FUNCTION', 'status': 'EXECUTED'}, 'util.py:global': {'type': 'PENDING_GLOBAL_ENCAPSULATION', 'status': 'PENDING'}}
    tla = TestLeadAgent(modified_files=ConfigurationService().mock_modified, refactor_plans=ConfigurationService().mock_plans)
    ConfigurationService().tla.run_dynamic_analysis()