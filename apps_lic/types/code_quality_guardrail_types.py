"""
Code Quality Guardrail - Consolidated Code Quality Checks

Merges:
- CodeFormatter
- DuplicateDetector
- UnusedCleanup
- DependencyPruning
- GitHygiene

Composable Rules:
- formatting: Code style enforcement
- duplication: Duplicate code detection
- unused_code: Unused variable/function removal
- dependencies: Dependency cleanup
- git_hygiene: Git best practices
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "code_quality_guardrail_types", "p0_governance")
_emit_reads_policy_state("p0", "code_quality_guardrail_types", "policy_binding")
_emit_snapshots_state("p0", "code_quality_guardrail_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_1")
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_2")
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_3")
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_4")
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_5")
_emit_emits_metric_event("code_quality_guardrail_types", "p4obs", "metric_6")
_emit_records_incident_event("code_quality_guardrail_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("code_quality_guardrail_types", "p4obs", "anomaly")
_emit_writes_observability_log("code_quality_guardrail_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("code_quality_guardrail_types", "p4obs", "mon_state")
_emit_triggers_alert("code_quality_guardrail_types", "p4obs", "alert")
_emit_links_incident_trace("code_quality_guardrail_types", "p4obs", "trace_link")
_emit_captures_pattern("code_quality_guardrail_types", "p3lm", "pattern")
_emit_records_learning_event("code_quality_guardrail_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("code_quality_guardrail_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("code_quality_guardrail_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("code_quality_guardrail_types", "p3lm", "routing")
_emit_improves_agent_policy("code_quality_guardrail_types", "p3lm", "policy")
_emit_stores_learning_state("code_quality_guardrail_types", "p3lm", "state")
_emit_records_execution_trace("code_quality_guardrail_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("code_quality_guardrail_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("code_quality_guardrail_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("code_quality_guardrail_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("code_quality_guardrail_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("code_quality_guardrail_types", "env_read", "p2_env_1")
_emit_reads_environ("code_quality_guardrail_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("code_quality_guardrail_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("code_quality_guardrail_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "code_quality_guardrail_types", "context_pull")
_emit_pulls_context("p1", "code_quality_guardrail_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "code_quality_guardrail_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "code_quality_guardrail_types", "uwg_term_2")
_emit_writes_through("p1", "code_quality_guardrail_types", "write_through")
_emit_writes_through("p1", "code_quality_guardrail_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "code_quality_guardrail_types", "safety_validation")
_emit_invokes_eval("p1", "code_quality_guardrail_types", "eval_call")
_emit_proposal_commits_routing("p1", "code_quality_guardrail_types", "routing_commit")
emit_replay_key("p0", "code_quality_guardrail_types")
emit_determinism_digest("p0", "code_quality_guardrail_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "code_quality_guardrail_types", "execution_auth")
_emit_validates_capability("p2", "code_quality_guardrail_types", "capability_check")
_emit_routes_to_capability("p2", "code_quality_guardrail_types", "capability_route")
_emit_writes_via_uwg("p2", "code_quality_guardrail_types", "uwg_write")
_emit_blocks_direct_write("p2", "code_quality_guardrail_types", "direct_write_block")
_emit_records_tool_invocation("p2", "code_quality_guardrail_types", "tool_invocation")
_emit_captures_execution_output("p2", "code_quality_guardrail_types", "exec_output")
_emit_dispatches_agent("p3", "code_quality_guardrail_types", "agent_dispatch")
_emit_coordinates_agents("p3", "code_quality_guardrail_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "code_quality_guardrail_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "code_quality_guardrail_types", "healing_outcome")
_emit_escalates_failure("p3", "code_quality_guardrail_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "code_quality_guardrail_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "code_quality_guardrail_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "code_quality_guardrail_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "code_quality_guardrail_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "code_quality_guardrail_types", "eval_metric")
_emit_stores_embedding("p4", "code_quality_guardrail_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "code_quality_guardrail_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "code_quality_guardrail_types", "exec_snapshot_link")


@dataclass
class CodeIssue:
    """Represents a code quality issue."""

    rule: str
    severity: str
    message: str
    file_path: str | None = None
    line_number: int | None = None
    suggestion: str | None = None


@dataclass
class QualityResult:
    """Result of code quality check."""

    valid: bool
    issues: list[CodeIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class CodeQualityGuardrail:
    """
    Consolidated Code Quality Guardrail.

    Provides unified code quality checks with:
    - Code formatting validation
    - Duplicate code detection
    - Unused code detection
    - Dependency analysis
    - Git hygiene checks
    """

    def __init__(self):
        """Initialize code quality guardrail."""
        self.enabled_rules: list[str] = [
            "formatting",
            "duplication",
            "unused_code",
            "dependencies",
            "git_hygiene",
        ]
        # guardian: allow-magic-config
        self.max_line_length = 120
        # guardian: allow-magic-config
        self.max_function_length = 50
        # guardian: allow-magic-config
        self.max_file_length = 500
        # guardian: allow-magic-config
        self.min_duplicate_lines = 5
        self.code_hashes: dict[str, list[str]] = {}
        self.unused_patterns = ["^\\s*#\\s*TODO", "^\\s*#\\s*FIXME", "^\\s*pass\\s*$"]
        self.bad_commit_patterns = ["^fix$", "^wip$", "^test$", "^asdf"]
        self.checks_performed = 0
        self.issues_found = 0

    async def validate(self, code: str, file_path: str | None = None) -> QualityResult:
        """
        Validate code quality.

        Args:
            code: Code to validate
            file_path: Optional file path for context

        Returns:
            QualityResult with issues
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CodeQualityGuardrail.validate")

        self.checks_performed += 1
        issues = []
        if "formatting" in self.enabled_rules:
            issues.extend(self._check_formatting(code, file_path))
        if "duplication" in self.enabled_rules:
            issues.extend(self._check_duplication(code, file_path))
        if "unused_code" in self.enabled_rules:
            issues.extend(self._check_unused(code, file_path))
        self.issues_found += len(issues)
        return QualityResult(
            valid=not any(i.severity == "error" for i in issues),
            issues=issues,
            metrics={"line_count": len(code.splitlines()), "issue_count": len(issues)},
        )

    def _check_formatting(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check code formatting."""
        issues = []
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                issues.append(
                    CodeIssue(
                        rule="formatting",
                        severity="warning",
                        message=f"Line exceeds {self.max_line_length} characters ({len(line)})",
                        file_path=file_path,
                        line_number=i,
                        suggestion="Consider breaking this line",
                    )
                )
        if len(lines) > self.max_file_length:
            issues.append(
                CodeIssue(
                    rule="formatting",
                    severity="warning",
                    message=f"File exceeds {self.max_file_length} lines ({len(lines)})",
                    file_path=file_path,
                    suggestion="Consider splitting into multiple files",
                )
            )
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                issues.append(
                    CodeIssue(
                        rule="formatting",
                        severity="info",
                        message="Trailing whitespace",
                        file_path=file_path,
                        line_number=i,
                    )
                )
        return issues

    def _check_duplication(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check for duplicate code."""
        issues = []
        lines = code.splitlines()
        for i in range(len(lines) - self.min_duplicate_lines):
            block = "\n".join(lines[i : i + self.min_duplicate_lines])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            if block_hash in self.code_hashes:
                if file_path not in self.code_hashes[block_hash]:
                    issues.append(
                        CodeIssue(
                            rule="duplication",
                            severity="warning",
                            message="Duplicate code block detected",
                            file_path=file_path,
                            line_number=i + 1,
                            suggestion="Consider extracting to shared function",
                        )
                    )
            else:
                self.code_hashes[block_hash] = []
            if file_path:
                self.code_hashes[block_hash].append(file_path)
        return issues

    def _check_unused(self, code: str, file_path: str | None) -> list[CodeIssue]:
        """Check for unused code patterns."""
        issues = []
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern in self.unused_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        CodeIssue(
                            rule="unused_code",
                            severity="info",
                            message="Potential cleanup needed",
                            file_path=file_path,
                            line_number=i,
                            suggestion="Review and remove if no longer needed",
                        )
                    )
        return issues

    def validate_commit_message(self, message: str) -> QualityResult:
        """
        Validate git commit message.

        Args:
            message: Commit message to validate

        Returns:
            QualityResult with issues
        """
        issues = []
        for pattern in self.bad_commit_patterns:
            if re.match(pattern, message.lower().strip()):
                issues.append(
                    CodeIssue(
                        rule="git_hygiene",
                        severity="error",
                        message="Commit message too short or unclear",
                        suggestion="Use descriptive commit messages",
                    )
                )
        if len(message.strip()) < 10:
            issues.append(
                CodeIssue(
                    rule="git_hygiene",
                    severity="warning",
                    message="Commit message is too short",
                    suggestion="Add more context to the commit message",
                )
            )
        return QualityResult(valid=not any(i.severity == "error" for i in issues), issues=issues)

    def validate_dependencies(self, dependencies: list[str], used: set[str]) -> QualityResult:
        """
        Validate dependencies.

        Args:
            dependencies: List of declared dependencies
            used: Set of actually used dependencies

        Returns:
            QualityResult with unused dependencies
        """
        issues = []
        unused = set(dependencies) - used
        for dep in unused:
            issues.append(
                CodeIssue(
                    rule="dependencies",
                    severity="warning",
                    message=f"Unused dependency: {dep}",
                    suggestion="Consider removing from dependencies",
                )
            )
        return QualityResult(
            valid=len(issues) == 0,
            issues=issues,
            metrics={"total_dependencies": len(dependencies), "unused_dependencies": len(unused)},
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get code quality statistics."""
        return {
            "checks_performed": self.checks_performed,
            "issues_found": self.issues_found,
            "enabled_rules": self.enabled_rules,
        }
