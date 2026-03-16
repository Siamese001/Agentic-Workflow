"""ADG-driven tests for agentic_core/L5_safety/static_checks/system_invariant_scanner.py — fan_in=2.

Contract tests: BypassViolation, SystemInvariantScanner constants and importability.
"""
from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_system_invariant_scanner_adg")
_emit_applies_guardrail("p0", "test_system_invariant_scanner_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_system_invariant_scanner_adg", "policy_binding")
_emit_snapshots_state("p0", "test_system_invariant_scanner_adg", "state_snapshot")
emit_replay_key("p0", "test_system_invariant_scanner_adg")
emit_determinism_digest("p0", "test_system_invariant_scanner_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_system_invariant_scanner_adg", "execution_auth")
_emit_validates_capability("p2", "test_system_invariant_scanner_adg", "capability_check")
_emit_routes_to_capability("p2", "test_system_invariant_scanner_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_system_invariant_scanner_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_system_invariant_scanner_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_system_invariant_scanner_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_system_invariant_scanner_adg", "exec_output")
_emit_dispatches_agent("p3", "test_system_invariant_scanner_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_system_invariant_scanner_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_system_invariant_scanner_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_system_invariant_scanner_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_system_invariant_scanner_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_system_invariant_scanner_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_system_invariant_scanner_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_system_invariant_scanner_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_system_invariant_scanner_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_system_invariant_scanner_adg", "eval_metric")
_emit_stores_embedding("p4", "test_system_invariant_scanner_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_system_invariant_scanner_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_system_invariant_scanner_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.static_checks.system_invariant_scanner import (
    BypassViolation,
    SystemInvariantScanner,
)


class TestBypassViolation:
    def test_importable(self):
        assert callable(BypassViolation)

    def test_attributes_stored(self):
        v = BypassViolation(
            file_path="foo/bar.py",
            line=42,
            rule_id="GATEWAY_BYPASS",
            snippet="open('file.txt')",
            description="Direct file write",
        )
        assert v.file_path == "foo/bar.py"
        assert v.line == 42
        assert v.rule_id == "GATEWAY_BYPASS"
        assert v.snippet == "open('file.txt')"
        assert v.description == "Direct file write"

    def test_str_contains_rule_id(self):
        v = BypassViolation("f.py", 1, "RULE_X", "code", "desc")
        assert "RULE_X" in str(v)

    def test_to_dict_has_required_keys(self):
        v = BypassViolation("f.py", 1, "R", "s", "d")
        d = v.to_dict()
        for key in ("file_path", "line", "rule_id", "snippet", "description"):
            assert key in d


class TestSystemInvariantScannerConstants:
    def test_allowlisted_modules_nonempty(self):
        assert len(SystemInvariantScanner.ALLOWLISTED_MODULES) > 0

    def test_restricted_providers_nonempty(self):
        assert "openai" in SystemInvariantScanner.RESTRICTED_PROVIDERS
        assert "anthropic" in SystemInvariantScanner.RESTRICTED_PROVIDERS

    def test_restricted_file_ops_nonempty(self):
        assert "open" in SystemInvariantScanner.RESTRICTED_FILE_OPS

    def test_restricted_embedding_nonempty(self):
        assert len(SystemInvariantScanner.RESTRICTED_EMBEDDING) > 0


class TestSystemInvariantScannerDetection:
    def _scan_source(self, source: str) -> list[BypassViolation]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source)
            tmp = Path(f.name)
        try:
            scanner = SystemInvariantScanner(tmp)
            tree = ast.parse(source)
            scanner.visit(tree)
            return scanner.violations
        finally:
            tmp.unlink(missing_ok=True)

    def test_clean_source_no_violations(self):
        source = "x = 1\ny = x + 2\n"
        violations = self._scan_source(source)
        assert violations == []

    def test_direct_open_call_detected(self):
        source = "open('secret.txt', 'w')\n"
        violations = self._scan_source(source)
        assert any(v.rule_id == "GATEWAY_BYPASS" for v in violations)

    def test_restricted_provider_import_detected(self):
        source = "import openai\n"
        violations = self._scan_source(source)
        assert any(v.rule_id == "PROVIDER_BYPASS" for v in violations)

    def test_violations_list_empty_on_init(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("")
            tmp = Path(f.name)
        try:
            scanner = SystemInvariantScanner(tmp)
            assert scanner.violations == []
        finally:
            tmp.unlink(missing_ok=True)
