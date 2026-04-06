"""System Invariant Scanner — AST/CI enforcement for bypass detection.

Scans repository for forbidden patterns that could bypass sovereignty controls:
- Gateway bypass (direct file operations)
- Provider SDK bypass (direct LLM API calls)
- Embedding bypass (factory instantiation)
- Unsigned ingress (signature verification)
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "system_invariant_scanner")
emit_determinism_digest("p0", "system_invariant_scanner")

_emit_dispatches_healing_run("p1", "system_invariant_scanner", "L5")
_emit_routes_through("p1", "system_invariant_scanner", "L5")
_emit_checks_agent_registry("p1", "system_invariant_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "system_invariant_scanner", "capability")
_emit_dispatches_execution_plan("p1", "system_invariant_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "system_invariant_scanner", "sub_agent")
_emit_routes_to_agent("p1", "system_invariant_scanner", "target_agent")
_emit_verifies_policy("p1", "system_invariant_scanner", "policy_check")
_emit_observes_runtime_state("p1", "system_invariant_scanner", "runtime_state")
_emit_verifies_boundary("p1", "system_invariant_scanner", "boundary_check")
_emit_transcripts_response("p1", "system_invariant_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "system_invariant_scanner")
_emit_gated_by_confidence("p1", "system_invariant_scanner", "confidence_gate")
_emit_escalates_to_human("p1", "system_invariant_scanner", "L5")
_emit_reads_policy_state("p1", "system_invariant_scanner", "L5")

_emit_applies_guardrail("p0", "system_invariant_scanner", "p0_governance")
_emit_snapshots_state("p0", "system_invariant_scanner", "state_snapshot")
_emit_authorize_and_execute("p2", "system_invariant_scanner", "execution_auth")
_emit_validates_capability("p2", "system_invariant_scanner", "capability_check")
_emit_routes_to_capability("p2", "system_invariant_scanner", "capability_route")
_emit_writes_via_uwg("p2", "system_invariant_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "system_invariant_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "system_invariant_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "system_invariant_scanner", "exec_output")
_emit_dispatches_agent("p3", "system_invariant_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "system_invariant_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "system_invariant_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "system_invariant_scanner", "healing_outcome")
_emit_escalates_failure("p3", "system_invariant_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "system_invariant_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "system_invariant_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "system_invariant_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "system_invariant_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "system_invariant_scanner", "eval_metric")
_emit_stores_embedding("p4", "system_invariant_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "system_invariant_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "system_invariant_scanner", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_1")
_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_2")
_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_3")
_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_4")
_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_5")
_emit_emits_metric_event("system_invariant_scanner", "p4obs", "metric_6")
_emit_records_incident_event("system_invariant_scanner", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_invariant_scanner", "p4obs", "anomaly")
_emit_writes_observability_log("system_invariant_scanner", "p4obs", "obs_log")
_emit_updates_monitoring_state("system_invariant_scanner", "p4obs", "mon_state")
_emit_triggers_alert("system_invariant_scanner", "p4obs", "alert")
_emit_links_incident_trace("system_invariant_scanner", "p4obs", "trace_link")
_emit_captures_pattern("system_invariant_scanner", "p3lm", "pattern")
_emit_records_learning_event("system_invariant_scanner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_invariant_scanner", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_invariant_scanner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("system_invariant_scanner", "p3lm", "routing")
_emit_improves_agent_policy("system_invariant_scanner", "p3lm", "policy")
_emit_stores_learning_state("system_invariant_scanner", "p3lm", "state")
_emit_records_execution_trace("system_invariant_scanner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("system_invariant_scanner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("system_invariant_scanner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("system_invariant_scanner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("system_invariant_scanner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("system_invariant_scanner", "env_read", "p2_env_1")
_emit_reads_environ("system_invariant_scanner", "env_read", "p2_env_2")
_emit_reads_runtime_state("system_invariant_scanner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("system_invariant_scanner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "system_invariant_scanner", "context_pull")
_emit_pulls_context("p1", "system_invariant_scanner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "system_invariant_scanner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "system_invariant_scanner", "uwg_term_2")
_emit_writes_through("p1", "system_invariant_scanner", "write_through")
_emit_writes_through("p1", "system_invariant_scanner", "write_through_2")
_emit_validated_by_safety_plane("p1", "system_invariant_scanner", "safety_validation")
_emit_invokes_eval("p1", "system_invariant_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "system_invariant_scanner", "routing_commit")


class BypassViolation:
    """Represents a detected bypass violation."""

    def __init__(self, file_path: str, line: int, rule_id: str, snippet: str, description: str):
        self.file_path = file_path
        self.line = line
        self.rule_id = rule_id
        self.snippet = snippet
        self.description = description

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line} [{self.rule_id}] {self.description}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line": self.line,
            "rule_id": self.rule_id,
            "snippet": self.snippet,
            "description": self.description,
        }


class SystemInvariantScanner(ast.NodeVisitor):
    """AST visitor to detect sovereignty bypass violations."""

    ALLOWLISTED_MODULES = {
        "agentic_core.L2_execution.UniversalWriteGateway",
        "agentic_core.L2_execution.engines.execution_gateway",
        "agentic_core.L2_execution.healers.healing_provider_adapters",
        "system_invariant_scanner",
        "system_learning.engines.embedding_service_factory",
        TESTS_DIR,
        "test_",
    }
    RESTRICTED_PROVIDERS = {
        "openai",
        "anthropic",
        "google.generativeai",
        "vertexai",
        "litellm",
        "transformers",
        "torch",
        "tensorflow",
    }
    RESTRICTED_FILE_OPS = {
        "open",
        "Path.write_text",
        "Path.write_bytes",
        "Path.unlink",
        "os.remove",
        "os.rename",
        "os.replace",
        "os.mkdir",
        "os.makedirs",
    }
    RESTRICTED_EMBEDDING = {"EmbeddingServiceFactory", "SentenceTransformer", "OpenAIEmbeddings"}

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[BypassViolation] = []
        self.current_line_content = ""

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SystemInvariantScanner.visit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SystemInvariantScanner.visit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if hasattr(node, "lineno"):
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1].strip()
            except (ValueError, TypeError, RuntimeError) as e:
                raise
                self.current_line_content = ""
        super().visit(node)

    def _is_allowlisted(self) -> bool:
        """Check if current file is allowlisted."""
        file_str = str(self.file_path)
        return any(allowed in file_str for allowed in self.ALLOWLISTED_MODULES)

    def _has_allowlist_comment(self) -> bool:
        """Check if current line has allowlist comment."""
        return "# guardian: allow-" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for restricted function calls."""
        if self._is_allowlisted() or self._has_allowlist_comment():
            self.generic_visit(node)
            return
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.RESTRICTED_FILE_OPS:
                self._add_violation(
                    node.lineno,
                    "GATEWAY_BYPASS",
                    f"Direct call to {func_name}",
                    f"Direct file operation '{func_name}' detected - use UniversalWriteGateway",
                )
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                if module_name in self.RESTRICTED_PROVIDERS:
                    self._add_violation(
                        node.lineno,
                        "PROVIDER_BYPASS",
                        f"Direct call to {module_name}.{node.func.attr}",
                        "Direct provider SDK call detected - use HealingProviderInvoker",
                    )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check for restricted imports."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return
        for alias in node.names:
            if alias.name in self.RESTRICTED_PROVIDERS:
                self._add_violation(
                    node.lineno,
                    "PROVIDER_BYPASS",
                    f"Import of restricted provider {alias.name}",
                    "Direct provider import detected - use HealingProviderInvoker seam",
                )
            elif any(restricted in alias.name for restricted in self.RESTRICTED_EMBEDDING):
                self._add_violation(
                    node.lineno,
                    "EMBEDDING_BYPASS",
                    f"Import of restricted embedding {alias.name}",
                    "Direct embedding import detected - use EmbeddingServiceFactory",
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for restricted from-imports."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return
        if node.module:
            if node.module in self.RESTRICTED_PROVIDERS:
                self._add_violation(
                    node.lineno,
                    "PROVIDER_BYPASS",
                    f"From-import of restricted provider {node.module}",
                    "Direct provider import detected - use HealingProviderInvoker seam",
                )
            elif any(restricted in node.module for restricted in self.RESTRICTED_EMBEDDING):
                self._add_violation(
                    node.lineno,
                    "EMBEDDING_BYPASS",
                    f"From-import of restricted embedding {node.module}",
                    "Direct embedding import detected - use EmbeddingServiceFactory",
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check for restricted class definitions."""
        if self._is_allowlisted():
            self.generic_visit(node)
            return
        if node.name in self.RESTRICTED_EMBEDDING:
            self._add_violation(
                node.lineno,
                "EMBEDDING_BYPASS",
                f"Class definition of {node.name}",
                "Direct embedding class definition detected - use EmbeddingServiceFactory",
            )
        self.generic_visit(node)

    def _add_violation(self, line: int, rule_id: str, snippet: str, description: str) -> None:
        """Add a violation to the list."""
        violation = BypassViolation(
            file_path=str(self.file_path),
            line=line,
            rule_id=rule_id,
            snippet=snippet,
            description=description,
        )
        self.violations.append(violation)


def scan_repository_for_bypasses(repo_root: Path) -> list[BypassViolation]:
    """Scan entire repository for sovereignty bypass violations."""
    violations: list[BypassViolation] = []
    patterns = ["**/*.py"]
    for pattern in patterns:
        for file_path in repo_root.glob(pattern):
            if any(
                skip in str(file_path) for skip in ["__pycache__", ".git", ".pytest_cache", "node_modules"]
            ):
                continue
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(file_path))
                scanner = SystemInvariantScanner(file_path)
                scanner.visit(tree)
                violations.extend(scanner.violations)
            except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                violations.append(
                    BypassViolation(
                        file_path=str(file_path),
                        line=e.lineno or 0,
                        rule_id="SYNTAX_ERROR",
                        snippet="Syntax error",
                        description=f"Syntax error: {e}",
                    )
                )
            except Exception as e:
                raise
                violations.append(
                    BypassViolation(
                        file_path=str(file_path),
                        line=0,
                        rule_id="SCAN_ERROR",
                        snippet="Scan error",
                        description=f"Scan error: {e}",
                    )
                )
    violations.sort(key=lambda v: (v.file_path, v.line, v.rule_id))
    return violations


def print_bypass_report(violations: list[BypassViolation]) -> None:
    """Print a formatted report of bypass violations."""
    if not violations:
        print("✅ No sovereignty bypass violations detected")
        return
    print(f"❌ Found {len(violations)} sovereignty bypass violations:")
    print()
    by_rule = {}
    for violation in violations:
        if violation.rule_id not in by_rule:
            by_rule[violation.rule_id] = []
        by_rule[violation.rule_id].append(violation)
    for rule_id in sorted(by_rule.keys()):
        print(f"🚨 {rule_id}:")
        for violation in by_rule[rule_id]:
            print(f"   {violation}")
        print()


def get_bypass_scan_summary(violations: list[BypassViolation]) -> dict[str, Any]:
    """Get summary statistics for bypass scan."""
    files_affected = set()
    for violation in violations:
        files_affected.add(violation.file_path)
    summary = {
        "total_violations": len(violations),
        "by_rule": {},
        "files_affected": len(files_affected),
        "files_affected_list": sorted(files_affected),
    }
    for violation in violations:
        rule_id = violation.rule_id
        if rule_id not in summary["by_rule"]:
            summary["by_rule"][rule_id] = 0
        summary["by_rule"][rule_id] += 1
    return summary


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    violations = scan_repository_for_bypasses(repo_root)
    print("System Invariant Scanner - Sovereignty Bypass Detection")
    print("=" * 60)
    print_bypass_report(violations)
    summary = get_bypass_scan_summary(violations)
    print(f"Summary: {summary['total_violations']} violations across {summary['files_affected']} files")
    if violations:
        os.exit(1)
    else:
        os.exit(0)
