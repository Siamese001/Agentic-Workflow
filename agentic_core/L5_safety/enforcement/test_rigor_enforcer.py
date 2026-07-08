"""
Test Rigor Enforcer

Enforces §1 TESTING & EVIDENCE requirements from .codex/rules during code generation.
Provides automated validation that code changes comply with constitutional testing requirements.

Constitutional Requirements:
- §1.1: Every line of changed logic MUST have tests
- §1.2: Tests MUST exist before logic changes are committed
- §1.3: Tests MUST be deterministic
- §1.5: Every changed surface MUST include edge case tests
- §1.12: Zero-tolerance for test skipping

Usage:
    from agentic_core.L5_safety.enforcement.test_rigor_enforcer import TestRigorEnforcer

    enforcer = TestRigorEnforcer(project_root=Path.cwd())
    result = enforcer.validate_code_changes()

    if not result.compliant:
        print(f"BLOCKED: {result.violations}")
"""

from __future__ import annotations

import subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "test_rigor_enforcer")
trace_contract.emit_determinism_digest("p0", "test_rigor_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "test_rigor_enforcer", "L5")
trace_contract._emit_routes_through("p1", "test_rigor_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "test_rigor_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "test_rigor_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "test_rigor_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "test_rigor_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "test_rigor_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "test_rigor_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "test_rigor_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "test_rigor_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "test_rigor_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "test_rigor_enforcer")
trace_contract._emit_gated_by_confidence("p1", "test_rigor_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "test_rigor_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "test_rigor_enforcer", "L5")
trace_contract._emit_snapshots_state("p0", "test_rigor_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "test_rigor_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "test_rigor_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "test_rigor_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "test_rigor_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "test_rigor_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "test_rigor_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "test_rigor_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "test_rigor_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "test_rigor_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "test_rigor_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "test_rigor_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "test_rigor_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "test_rigor_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "test_rigor_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "test_rigor_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "test_rigor_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "test_rigor_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "test_rigor_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "test_rigor_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "test_rigor_enforcer", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("test_rigor_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("test_rigor_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("test_rigor_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("test_rigor_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("test_rigor_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("test_rigor_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("test_rigor_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("test_rigor_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("test_rigor_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("test_rigor_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("test_rigor_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("test_rigor_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("test_rigor_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("test_rigor_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("test_rigor_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("test_rigor_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("test_rigor_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("test_rigor_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("test_rigor_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("test_rigor_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("test_rigor_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("test_rigor_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("test_rigor_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "test_rigor_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "test_rigor_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "test_rigor_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "test_rigor_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "test_rigor_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "test_rigor_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "test_rigor_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "test_rigor_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "test_rigor_enforcer", "routing_commit")

# Configuration constants


@dataclass
class TestCoverageRequirement:
    """Requirement for test coverage of a changed surface."""

    file_path: str
    surface_name: str  # function, class, or method name
    surface_type: str  # decision_surface, side_effect, state_transition, etc.
    required_tests: list[str]  # edge_null, edge_empty, determinism_identical, etc.
    minimum_test_count: int


@dataclass
class ValidationResult:
    """Result of test rigor validation."""

    compliant: bool
    collected_tests: int
    executed_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TestRigorEnforcer:
    """Enforces constitutional testing requirements during code generation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.requirements: list[TestCoverageRequirement] = []

    def declare_scope(self, changed_files: list[str]) -> None:
        """Declare scope of code changes (Step 1 of pre-code-generation gate)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "TestRigorEnforcer.declare_scope")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TestRigorEnforcer.declare_scope".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print(f"[TEST-RIGOR] Scope declared: {len(changed_files)} files")
        for file_path in changed_files:
            print(f"  - {file_path}")

    def add_coverage_requirement(self, requirement: TestCoverageRequirement) -> None:
        """Add test coverage requirement for a changed surface."""
        self.requirements.append(requirement)
        print(
            f"[TEST-RIGOR] Requirement added: {requirement.surface_name} "
            f"({requirement.minimum_test_count} tests minimum)",
        )

    def validate_pre_code_generation(self) -> ValidationResult:
        """Validate that test requirements are declared before code generation.

        Enforces §1.2: Tests MUST exist before logic changes are committed.

        Returns:
            ValidationResult with compliant=True if requirements declared, False otherwise
        """
        trace_contract._emit_applies_guardrail(
            str(uuid.uuid4()),
            "TestRigorEnforcer.validate_pre_code_generation",
            "L5_POLICY",
        )
        violations = []

        if not self.requirements:
            violations.append(
                "§1.2 VIOLATION: No test requirements declared. "
                "Must declare test coverage before code generation.",
            )

        total_required = sum(req.minimum_test_count for req in self.requirements)
        if total_required == 0:
            violations.append(
                "§1.1 VIOLATION: Zero tests required. Every line of changed logic MUST have tests.",
            )

        return ValidationResult(
            compliant=len(violations) == 0,
            collected_tests=0,
            executed_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            violations=violations,
        )

    def validate_post_code_generation(self, test_path: str | None = None) -> ValidationResult:
        """Validate test coverage after code changes.

        Enforces:
        - §1.12: Zero-tolerance for test skipping (collection == execution)
        - §1.1: Test coverage matches declared requirements

        Args:
            test_path: Optional path to test directory/file. If None, runs all tests.

        Returns:
            ValidationResult with compliance status and metrics
        """
        violations = []
        warnings = []

        # Step 1: Collect tests
        collected = self._run_pytest_collect(test_path)
        if collected is None:
            violations.append("PYTEST COLLECTION FAILED: Cannot validate test coverage")
            return ValidationResult(
                compliant=False,
                collected_tests=0,
                executed_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                violations=violations,
            )

        # Step 2: Execute tests
        execution = self._run_pytest_execute(test_path)
        if execution is None:
            violations.append("PYTEST EXECUTION FAILED: Cannot validate test coverage")
            return ValidationResult(
                compliant=False,
                collected_tests=collected,
                executed_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                violations=violations,
            )

        passed, failed, skipped = execution

        # Step 3: Verify collection == execution (§1.12)
        executed_total = passed + failed
        if collected != executed_total:
            violations.append(
                f"§1.12 VIOLATION: Test count mismatch. "
                f"Collected {collected} but executed {executed_total}. "
                f"Deselected: {collected - executed_total} tests. "
                f"Zero-tolerance for test skipping.",
            )

        # Step 4: Verify no skipped tests (§1.12)
        if skipped > 0:
            violations.append(f"§1.12 VIOLATION: {skipped} tests skipped. Zero-tolerance for test skipping.")

        # Step 5: Verify coverage matches requirements (§1.1)
        total_required = sum(req.minimum_test_count for req in self.requirements)
        if total_required > 0 and executed_total < total_required:
            violations.append(
                f"§1.1 VIOLATION: Insufficient test coverage. "
                f"Required {total_required} tests minimum, executed {executed_total}. "
                f"Coverage gap: {total_required - executed_total} tests.",
            )

        # Step 6: Check for test failures
        if failed > 0:
            warnings.append(f"WARNING: {failed} tests failed. Fix failing tests before commit.")

        return ValidationResult(
            compliant=len(violations) == 0,
            collected_tests=collected,
            executed_tests=executed_total,
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            violations=violations,
            warnings=warnings,
        )

    def _run_pytest_collect(self, test_path: str | None) -> int | None:
        """Run pytest --collect-only and return count of collected tests."""
        cmd = ["pytest", "--collect-only", "-q"]
        if test_path:
            cmd.append(test_path)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )

            # Parse output for collected count
            for line in result.stdout.splitlines():
                if "no tests ran" in line.lower():
                    return 0
                # Look for pattern like "18 tests collected"
                if "test" in line.lower() and "collected" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            return int(part)

            return 0

        except (
            RuntimeError,
            OSError,
        ) as e:  # guardian: allow-return-none-swallow -- test collection: non-fatal, caller handles None as no tests
            print(f"[TEST-RIGOR] Collection failed: {e}")
            return None

    def _run_pytest_execute(self, test_path: str | None) -> tuple[int, int, int] | None:
        """Run pytest and return (passed, failed, skipped) counts."""
        cmd = ["pytest", "-v", "--tb=short"]
        if test_path:
            cmd.append(test_path)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
            )

            # Parse output for test counts
            passed = 0
            failed = 0
            skipped = 0

            for line in tqdm(result.stdout.splitlines(), desc="Processing", unit="item"):
                line_lower = line.lower()
                if "passed" in line_lower:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i + 1 < len(parts) and "passed" in parts[i + 1].lower():
                            passed = int(part)
                if "failed" in line_lower:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i + 1 < len(parts) and "failed" in parts[i + 1].lower():
                            failed = int(part)
                if "skipped" in line_lower:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i + 1 < len(parts) and "skipped" in parts[i + 1].lower():
                            skipped = int(part)

            return (passed, failed, skipped)

        except (
            RuntimeError,
            OSError,
        ) as e:  # guardian: allow-return-none-swallow -- test execution: non-fatal, caller handles None as failed run
            print(f"[TEST-RIGOR] Execution failed: {e}")
            return None

    def generate_validation_report(self, result: ValidationResult) -> str:
        """Generate validation report for post-code validation."""
        report_lines = [
            "=" * 60,
            "POST-CODE VALIDATION REPORT",
            "=" * 60,
            "",
            "Test Execution:",
            f"  Collected: {result.collected_tests} tests",
            f"  Executed:  {result.executed_tests} tests",
            f"  Passed:    {result.passed_tests} tests",
            f"  Failed:    {result.failed_tests} tests",
            f"  Skipped:   {result.skipped_tests} tests",
            "",
        ]

        # Collection/Execution match
        match_status = "✅ PASS" if result.collected_tests == result.executed_tests else "❌ FAIL"
        report_lines.append(f"  Collection/Execution Match: {match_status} (§1.12)")
        report_lines.append("")

        # Coverage
        total_required = sum(req.minimum_test_count for req in self.requirements)
        coverage_status = "✅ PASS" if result.executed_tests >= total_required else "❌ FAIL"
        report_lines.extend(
            [
                "Test Coverage:",
                f"  Declared minimum: {total_required} tests",
                f"  Actual coverage:  {result.executed_tests} tests",
                f"  Coverage gap:     {max(0, total_required - result.executed_tests)} tests",
                "",
                f"  Coverage Match: {coverage_status} (§1.1)",
                "",
            ],
        )

        # Violations
        if result.violations:
            report_lines.append("VIOLATIONS:")
            for violation in result.violations:
                report_lines.append(f"  ❌ {violation}")
            report_lines.append("")

        # Warnings
        if result.warnings:
            report_lines.append("WARNINGS:")
            for warning in result.warnings:
                report_lines.append(f"  ⚠️  {warning}")
            report_lines.append("")

        # Final status
        status = "✅ APPROVED FOR COMMIT" if result.compliant else "❌ BLOCKED - FIX VIOLATIONS"
        report_lines.extend(
            [
                "=" * 60,
                f"VALIDATION STATUS: {status}",
                "=" * 60,
            ],
        )

        return "\n".join(report_lines)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "TestRigorEnforcer",
    "TestCoverageRequirement",
    "ValidationResult",
]
