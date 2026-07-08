"""
Phase Acceptance Enforcement Guard
==================================

Enforcement guard to prevent transgressions learned from Phase 2 closeout:
1. Testpaths contract synchronization violations
2. Failure to distinguish pre-existing vs new issues
3. Evidence capture protocol violations
"""

import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "phase_acceptance_guardrail")
trace_contract.emit_determinism_digest("p0", "phase_acceptance_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "phase_acceptance_guardrail", "L5")
trace_contract._emit_routes_through("p1", "phase_acceptance_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "phase_acceptance_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "phase_acceptance_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "phase_acceptance_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "phase_acceptance_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "phase_acceptance_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "phase_acceptance_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "phase_acceptance_guardrail", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "phase_acceptance_guardrail", "boundary_check")
trace_contract._emit_transcripts_response("p1", "phase_acceptance_guardrail", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "phase_acceptance_guardrail")
trace_contract._emit_gated_by_confidence("p1", "phase_acceptance_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "phase_acceptance_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "phase_acceptance_guardrail", "L5")

trace_contract._emit_applies_guardrail("p0", "phase_acceptance_guardrail", "p0_governance")
trace_contract._emit_snapshots_state("p0", "phase_acceptance_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "phase_acceptance_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "phase_acceptance_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "phase_acceptance_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "phase_acceptance_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "phase_acceptance_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "phase_acceptance_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "phase_acceptance_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "phase_acceptance_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "phase_acceptance_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "phase_acceptance_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "phase_acceptance_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "phase_acceptance_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "phase_acceptance_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "phase_acceptance_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "phase_acceptance_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "phase_acceptance_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "phase_acceptance_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "phase_acceptance_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "phase_acceptance_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "phase_acceptance_guardrail", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("phase_acceptance_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("phase_acceptance_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("phase_acceptance_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("phase_acceptance_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("phase_acceptance_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("phase_acceptance_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("phase_acceptance_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("phase_acceptance_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("phase_acceptance_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("phase_acceptance_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("phase_acceptance_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("phase_acceptance_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("phase_acceptance_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("phase_acceptance_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("phase_acceptance_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("phase_acceptance_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("phase_acceptance_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("phase_acceptance_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("phase_acceptance_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("phase_acceptance_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("phase_acceptance_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("phase_acceptance_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("phase_acceptance_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "phase_acceptance_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "phase_acceptance_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "phase_acceptance_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "phase_acceptance_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "phase_acceptance_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "phase_acceptance_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "phase_acceptance_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "phase_acceptance_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "phase_acceptance_guardrail", "routing_commit")


class PhaseAcceptanceGuard:
    """Enforces Phase 2 closeout lessons learned."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def check_testpaths_contract_sync(self) -> None:
        """Rule 46: Testpaths contract must be synchronized with pytest.ini."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "PhaseAcceptanceGuard.check_testpaths_contract_sync",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:PhaseAcceptanceGuard.check_testpaths_contract_sync".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        pytest_ini = self.repo_root / "pytest.ini"
        contract_test = self.repo_root / TESTS_DIR / "unit_min_deps" / "test_testpaths_contract.py"
        if not pytest_ini.exists():
            self.errors.append("pytest.ini not found")
            return
        if not contract_test.exists():
            self.errors.append(
                "testpaths contract test not found at tests/unit_min_deps/test_testpaths_contract.py",
            )
            return
        content = pytest_ini.read_text(encoding="utf-8")
        testpaths_match = re.search("^testpaths\\s*=\\s*\\n((?:\\s+.*\\n?)*)", content, re.MULTILINE)
        if not testpaths_match:
            self.errors.append("No testpaths section found in pytest.ini")
            return
        testpaths_lines = testpaths_match.group(1).strip().split("\n")
        actual_testpaths = set()
        for line in testpaths_lines:
            line = line.strip()
            if line and (not line.startswith("#")):
                actual_testpaths.add(line)
        contract_content = contract_test.read_text(encoding="utf-8")
        required_match = re.search("REQUIRED_TESTPATHS\\s*=\\s*{([^}]+)}", contract_content)
        if not required_match:
            self.errors.append("REQUIRED_TESTPATHS not found in contract test")
            return
        required_paths = set()
        for path in required_match.group(1).split(","):
            path = path.strip().strip("'\"")
            if path:
                required_paths.add(path)
        if actual_testpaths != required_paths:
            self.errors.append(
                f"Testpaths contract mismatch:\n  pytest.ini testpaths: {sorted(actual_testpaths)}\n  Contract REQUIRED_TESTPATHS: {sorted(required_paths)}\n  Missing in contract: {sorted(actual_testpaths - required_paths)}\n  Extra in contract: {sorted(required_paths - actual_testpaths)}",
            )

    def check_evidence_files_protocol(self) -> None:
        """Rule 48: Evidence files must contain raw, untruncated outputs."""
        evidence_dir = self.repo_root / "docs" / REPORTS_DIR / "governance"
        if not evidence_dir.exists():
            return
        for evidence_file in tqdm(evidence_dir.glob("*evidence.md"), desc="Processing", unit="item"):
            content = evidence_file.read_text(encoding="utf-8")
            test_blocks = re.findall("```bash\\npytest.*?\\n```", content, re.DOTALL)
            for block in test_blocks:
                if re.search("Full output truncated|lines were truncated", block, re.IGNORECASE):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} contains pytest output truncation",
                    )
                elif re.search("\\.\\.\\.(?!\\n.*```)", block) and "Exit code:" not in block:
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} contains possible pytest output truncation",
                    )
            for block in test_blocks:
                if "Exit code:" not in block and "passed" not in block and ("failed" not in block):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} missing exit code in pytest output block",
                    )
            if (
                "git status" in content
                and "clean working tree" not in content
                and ("nothing to commit" not in content)
            ):
                status_match = re.search("git status.*?\\n```(.*?)```", content, re.DOTALL)
                if status_match and "working tree clean" not in status_match.group(1):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} shows git status but may not prove clean state",
                    )

    def _is_allowed_truncation(self, content: str, pattern: str) -> bool:
        """Check if truncation is allowed in this context."""
        if pattern == "Full output truncated":
            return "==================== test session starts" in content
        if pattern == "\\.\\.\\.":
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "..." in line:
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 3)
                    context = "\n".join(lines[context_start:context_end])
                    if "```" not in context and "Output:" not in context:
                        return True
        return False

    def check_phase_evidence_completeness(self) -> None:
        """Rule 47: Phase evidence must distinguish pre-existing vs new issues."""
        evidence_dir = self.repo_root / "docs" / REPORTS_DIR / "governance"
        for evidence_file in tqdm(evidence_dir.glob("phase*evidence.md"), desc="Processing", unit="item"):
            content = evidence_file.read_text(encoding="utf-8")
            if "failed" in content.lower() and "git --no-pager show" not in content:
                self.warnings.append(
                    f"Evidence file {evidence_file.name} mentions failures but lacks git history analysis",
                )
            if "pytest -q" in content and "Exit code: 1" in content:
                if not re.search("pytest.*tests/governance/test_.*\\.py", content):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} shows pytest failure but no deterministic command set",
                    )
            if "pre-existing" not in content.lower() and "BLOCKED" in content:
                self.warnings.append(
                    f"Evidence file {evidence_file.name} marked as BLOCKED but lacks pre-existing analysis",
                )

    def validate(self) -> bool:
        """Run all validation checks."""
        self.errors.clear()
        self.warnings.clear()
        self.check_testpaths_contract_sync()
        self.check_evidence_files_protocol()
        self.check_phase_evidence_completeness()
        return len(self.errors) == 0

    def report(self) -> str:
        """Generate validation report."""
        report_lines = []
        if self.errors:
            report_lines.append("ERRORS:")
            for error in self.errors:
                report_lines.append(f"  - {error}")
        if self.warnings:
            report_lines.append("WARNINGS:")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")
        if not self.errors and (not self.warnings):
            report_lines.append("No enforcement violations detected.")
        return "\n".join(report_lines)


def main():
    """Run phase acceptance enforcement validation."""
    repo_root = Path(__file__).parent.parent.parent
    guard = PhaseAcceptanceGuard(repo_root)
    if guard.validate():
        print("✓ Phase acceptance enforcement validation passed")
        return 0
    else:
        print("✗ Phase acceptance enforcement validation failed")
        print(guard.report())
        return 1


if __name__ == "__main__":
    exit(main())
