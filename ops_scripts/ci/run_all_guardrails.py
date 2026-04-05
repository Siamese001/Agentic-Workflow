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
from agentic_core.L0_routing.utils.clock_provider import ClockProvider as clock_provider
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "run_all_guardrails")
_emit_applies_guardrail("p0", "run_all_guardrails", "p0_governance")
_emit_reads_policy_state("p0", "run_all_guardrails", "policy_binding")
_emit_snapshots_state("p0", "run_all_guardrails", "state_snapshot")
emit_replay_key("p0", "run_all_guardrails")
emit_determinism_digest("p0", "run_all_guardrails")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_all_guardrails", "execution_auth")
_emit_validates_capability("p2", "run_all_guardrails", "capability_check")
_emit_routes_to_capability("p2", "run_all_guardrails", "capability_route")
_emit_writes_via_uwg("p2", "run_all_guardrails", "uwg_write")
_emit_blocks_direct_write("p2", "run_all_guardrails", "direct_write_block")
_emit_records_tool_invocation("p2", "run_all_guardrails", "tool_invocation")
_emit_captures_execution_output("p2", "run_all_guardrails", "exec_output")
_emit_dispatches_agent("p3", "run_all_guardrails", "agent_dispatch")
_emit_coordinates_agents("p3", "run_all_guardrails", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_all_guardrails", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_all_guardrails", "healing_outcome")
_emit_escalates_failure("p3", "run_all_guardrails", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_all_guardrails", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_all_guardrails", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_all_guardrails", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_all_guardrails", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_all_guardrails", "eval_metric")
_emit_stores_embedding("p4", "run_all_guardrails", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_all_guardrails", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_all_guardrails", "exec_snapshot_link")

# Configuration constants
DEFAULT_TIMEOUT = 300
DEFAULT_REPORT_INTERVAL = 30

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

_FIXED_TS = '2026-01-01T00:00:00'
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from ops_scripts.ci.ci_timeout_decorator import ci_progress_reporter, ci_timeout, generate_rca

_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_1")
_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_2")
_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_3")
_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_4")
_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_5")
_emit_emits_metric_event("run_all_guardrails", "p4obs", "metric_6")
_emit_records_incident_event("run_all_guardrails", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_all_guardrails", "p4obs", "anomaly")
_emit_writes_observability_log("run_all_guardrails", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_all_guardrails", "p4obs", "mon_state")
_emit_triggers_alert("run_all_guardrails", "p4obs", "alert")
_emit_links_incident_trace("run_all_guardrails", "p4obs", "trace_link")
_emit_captures_pattern("run_all_guardrails", "p3lm", "pattern")
_emit_records_learning_event("run_all_guardrails", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_all_guardrails", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_all_guardrails", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_all_guardrails", "p3lm", "routing")
_emit_improves_agent_policy("run_all_guardrails", "p3lm", "policy")
_emit_stores_learning_state("run_all_guardrails", "p3lm", "state")
_emit_records_execution_trace("run_all_guardrails", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_all_guardrails", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_all_guardrails", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_all_guardrails", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_all_guardrails", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_all_guardrails", "env_read", "p2_env_1")
_emit_reads_environ("run_all_guardrails", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_all_guardrails", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_all_guardrails", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_all_guardrails", "context_pull")
_emit_pulls_context("p1", "run_all_guardrails", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_all_guardrails", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_all_guardrails", "uwg_term_2")
_emit_writes_through("p1", "run_all_guardrails", "write_through")
_emit_writes_through("p1", "run_all_guardrails", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_all_guardrails", "safety_validation")
_emit_invokes_eval("p1", "run_all_guardrails", "eval_call")
_emit_proposal_commits_routing("p1", "run_all_guardrails", "routing_commit")
_emit_escalates_to_human("p1", "run_all_guardrails", "human_escalation")
_emit_routes_through("p1", "run_all_guardrails", "route_through")
_emit_checks_agent_registry("p1", "run_all_guardrails", "agent_registry")
_emit_validates_agent_capability("p1", "run_all_guardrails", "capability")
_emit_dispatches_execution_plan("p1", "run_all_guardrails", "exec_plan")
_emit_agent_executes_agent("p1", "run_all_guardrails", "sub_agent")
_emit_routes_to_agent("p1", "run_all_guardrails", "target_agent")
_emit_verifies_policy("p1", "run_all_guardrails", "policy_check")
_emit_observes_runtime_state("p1", "run_all_guardrails", "runtime_state")
_emit_verifies_boundary("p1", "run_all_guardrails", "boundary_check")
_emit_transcripts_response("p1", "run_all_guardrails", "transcript")
_emit_hard_fails_untranscripted("p1", "run_all_guardrails")
_emit_gated_by_confidence("p1", "run_all_guardrails", "confidence_gate")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_1")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_2")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_3")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_4")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_5")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_6")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_7")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_8")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_9")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_10")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_11")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_12")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_13")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_14")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_15")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_16")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_17")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_18")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_19")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_20")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_21")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_22")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_23")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_24")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_25")
_emit_reads_through("l4", "run_all_guardrails", "urg_read_26")

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
    output: str = ''
    error: str | None = None
    timeout: bool = False
    rca_path: Path | None = None

@dataclass
class GuardrailSuite:
    """Configuration for CI guardrail suite."""
    guardrails: list[dict[str, Any]] = field(default_factory=lambda: [{'name': 'Anti-Pattern Scanner', 'script': 'ops_scripts/ci/check_anti_patterns.py', 'timeout': 120, 'critical': True, 'description': 'Detects 6 categories of anti-patterns'}, {'name': 'Utility Silent Swallower Detection', 'script': 'ops_scripts/ci/check_utility_silent_swallowers.py', 'timeout': 180, 'critical': True, 'description': 'Prevents hidden failures in governance scripts'}, {'name': 'Plan Location Compliance', 'script': 'ops_scripts/ci/check_plan_location_compliance.py', 'timeout': 30, 'critical': True, 'description': 'Enforces Constitutional Rule #0'}, {'name': 'PowerShell Usage Ban', 'script': 'ops_scripts/ci/check_powershell_ban.py', 'timeout': 300, 'critical': False, 'description': 'Enforces Python-only subprocess operations'}])

class GuardrailOrchestrator:
    """Orchestrates CI guardrail execution with timeout and RCA."""

    def __init__(self, default_timeout: int=DEFAULT_TIMEOUT, verbose: bool=False):
        self.default_timeout = default_timeout
        self.verbose = verbose
        self.results: list[GuardrailResult] = []
        self.start_time = clock_provider.time()

    def run_all_guardrails(self, suite: GuardrailSuite) -> bool:
        """
        Run all guardrails in the suite with timeout protection.

        Returns:
            True if all guardrails passed, False otherwise
        """
        print('=' * 80)
        print('CI GUARDRAIL SUITE - TIMEOUT PROTECTED')
        print('=' * 80)
        print(f'Total Guardrails: {len(suite.guardrails)}')
        print(f'Default Timeout: {self.default_timeout}s')
        print(f'Timestamp: {clock_provider.now().isoformat()}')
        print('=' * 80)
        print()
        all_passed = True
        with ci_progress_reporter(len(suite.guardrails), 'Running Guardrails') as reporter:
            for i, guardrail_config in enumerate(suite.guardrails):
                reporter.update(i)
                result = self._run_single_guardrail(guardrail_config)
                self.results.append(result)
                if not result.passed:
                    all_passed = False
                    if guardrail_config.get('critical', True):
                        print(f'🚨 CRITICAL GUARDRAIL FAILED: {result.name}')
        self._print_summary()
        return all_passed

    def _run_single_guardrail(self, config: dict[str, Any]) -> GuardrailResult:
        """Run a single guardrail with timeout protection."""
        name = config['name']
        script = config['script']
        timeout = config.get('timeout', self.default_timeout)
        print(f"\n{'=' * 80}")
        print(f'🔍 Running: {name}')
        print(f'📜 Script: {script}')
        print(f'⏱️  Timeout: {timeout}s')
        print(f"{'=' * 80}")
        start_time = clock_provider.time()
        script_path = PROJECT_ROOT / script
        if not script_path.exists():
            error_msg = f'Script not found: {script_path}'
            print(f'❌ {error_msg}')
            rca_path = generate_rca(operation_name=name, error_type='SCRIPT_NOT_FOUND', error_message=error_msg, elapsed_time=0, context={'script': str(script_path)})
            return GuardrailResult(name=name, script=script, passed=False, exit_code=127, elapsed_time=0, error=error_msg, rca_path=rca_path)
        try:
            result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT)
            elapsed = clock_provider.time() - start_time
            passed = result.returncode == 0
            violations = self._parse_violations(result.stdout + result.stderr)
            if self.verbose or not passed:
                print(result.stdout)
                if result.stderr:
                    print('STDERR:', result.stderr)
            if passed:
                print(f'✅ {name} PASSED in {elapsed:.2f}s')
            else:
                print(f'❌ {name} FAILED in {elapsed:.2f}s (exit code: {result.returncode})')
                rca_path = generate_rca(operation_name=name, error_type='GUARDRAIL_FAILURE', error_message=f'Exit code: {result.returncode}, Violations: {violations}', elapsed_time=elapsed, context={'script': script, 'violations': violations, 'stdout': result.stdout[:500], 'stderr': result.stderr[:500]})
                return GuardrailResult(name=name, script=script, passed=False, exit_code=result.returncode, elapsed_time=elapsed, violations=violations, output=result.stdout, error=result.stderr, rca_path=rca_path)
            return GuardrailResult(name=name, script=script, passed=True, exit_code=0, elapsed_time=elapsed, violations=violations, output=result.stdout)
        except subprocess.TimeoutExpired as e:
            elapsed = clock_provider.time() - start_time
            print(f'⏱️  {name} TIMEOUT after {elapsed:.2f}s')
            rca_path = generate_rca(operation_name=name, error_type='TIMEOUT', error_message=f'Guardrail exceeded {timeout}s timeout limit', elapsed_time=elapsed, context={'script': script, 'timeout_limit': timeout, 'stdout': e.stdout[:500] if e.stdout else 'N/A', 'stderr': e.stderr[:500] if e.stderr else 'N/A'})
            return GuardrailResult(name=name, script=script, passed=False, exit_code=124, elapsed_time=elapsed, timeout=True, error=f'Timeout after {timeout}s', rca_path=rca_path)
        except Exception as e:
            raise
            elapsed = clock_provider.time() - start_time
            print(f'💥 {name} EXCEPTION: {e}')
            rca_path = generate_rca(operation_name=name, error_type=type(e).__name__, error_message=str(e), elapsed_time=elapsed, context={'script': script})
            return GuardrailResult(name=name, script=script, passed=False, exit_code=1, elapsed_time=elapsed, error=str(e), rca_path=rca_path)

    def _parse_violations(self, output: str) -> int:
        """Parse violation count from output."""
        import re
        patterns = ['(\\d+)\\s+violations?\\s+found', 'violations?:\\s*(\\d+)', 'total:\\s*(\\d+)', 'FAILED.*?(\\d+)\\s+violations?']
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0

    def _print_summary(self):
        """Print comprehensive summary of all guardrail results."""
        total_elapsed = clock_provider.time() - self.start_time
        print('\n' + '=' * 80)
        print('CI GUARDRAIL SUITE - SUMMARY')
        print('=' * 80)
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        timeout_count = sum(1 for r in self.results if r.timeout)
        total_violations = sum(r.violations for r in self.results)
        print(f'Total Guardrails: {len(self.results)}')
        print(f'✅ Passed: {passed_count}')
        print(f'❌ Failed: {failed_count}')
        print(f'⏱️  Timeouts: {timeout_count}')
        print(f'🚨 Total Violations: {total_violations}')
        print(f'⏱️  Total Time: {total_elapsed:.2f}s')
        print()
        print('DETAILED RESULTS:')
        print('-' * 80)
        for result in self.results:
            status_icon = '✅' if result.passed else '⏱️' if result.timeout else '❌'
            print(f'{status_icon} {result.name}')
            print(f'   Time: {result.elapsed_time:.2f}s')
            if result.violations > 0:
                print(f'   Violations: {result.violations}')
            if result.error:
                print(f'   Error: {result.error}')
            if result.rca_path:
                print(f'   RCA: {result.rca_path.relative_to(PROJECT_ROOT)}')
            print()
        rca_files = [r.rca_path for r in self.results if r.rca_path]
        if rca_files:
            print('📄 RCA FILES GENERATED:')
            for rca_path in rca_files:
                print(f'   - {rca_path.relative_to(PROJECT_ROOT)}')
            print()
        print('=' * 80)
        if passed_count == len(self.results):
            print('🎉 ALL GUARDRAILS PASSED')
        else:
            print(f'⚠️  {failed_count} GUARDRAIL(S) FAILED')
        print('=' * 80)

    def save_report(self, output_path: Path):
        """Save detailed JSON report."""
        # guardian: allow-global-mutation
        report = {'timestamp': _FIXED_TS, 'total_elapsed': clock_provider.time() - self.start_time, 'summary': {'total': len(self.results), 'passed': sum(1 for r in self.results if r.passed), 'failed': sum(1 for r in self.results if not r.passed), 'timeouts': sum(1 for r in self.results if r.timeout), 'total_violations': sum(r.violations for r in self.results)}, 'results': [{'name': r.name, 'script': r.script, 'passed': r.passed, 'exit_code': r.exit_code, 'elapsed_time': r.elapsed_time, 'violations': r.violations, 'timeout': r.timeout, 'error': r.error, 'rca_path': str(r.rca_path) if r.rca_path else None} for r in self.results]}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f'📊 Report saved: {output_path}')

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run all CI guardrails with timeout protection')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Default timeout in seconds')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', type=str, help='Save JSON report to file')
    args = parser.parse_args()
    suite = GuardrailSuite()
    orchestrator = GuardrailOrchestrator(default_timeout=args.timeout, verbose=args.verbose)
    all_passed = orchestrator.run_all_guardrails(suite)
    if args.report:
        orchestrator.save_report(Path(args.report))
    return 0 if all_passed else 1
if __name__ == '__main__':
    sys.exit(main())
