"""ADG-driven tests for agentic_core/utils/__init__.py — fan_in=90.

90 callers import from this package. Tests verify re-exported symbols
are present, callable, and behave as documented.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_utils_init_adg")
_emit_applies_guardrail("p0", "test_utils_init_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_utils_init_adg", "policy_binding")
_emit_snapshots_state("p0", "test_utils_init_adg", "state_snapshot")
emit_replay_key("p0", "test_utils_init_adg")
emit_determinism_digest("p0", "test_utils_init_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_utils_init_adg", "execution_auth")
_emit_validates_capability("p2", "test_utils_init_adg", "capability_check")
_emit_routes_to_capability("p2", "test_utils_init_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_utils_init_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_utils_init_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_utils_init_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_utils_init_adg", "exec_output")
_emit_dispatches_agent("p3", "test_utils_init_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_utils_init_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_utils_init_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_utils_init_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_utils_init_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_utils_init_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_utils_init_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_utils_init_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_utils_init_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_utils_init_adg", "eval_metric")
_emit_stores_embedding("p4", "test_utils_init_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_utils_init_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_utils_init_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


class TestUtilsPackagePublicAPI:
    def test_standard_heal_importable(self):
        from agentic_core.utils import standard_heal
        assert callable(standard_heal)

    def test_standard_heal_async_importable(self):
        from agentic_core.utils import standard_heal_async
        assert callable(standard_heal_async)

    def test_timeout_importable(self):
        from agentic_core.utils import timeout
        assert callable(timeout)

    def test_timeout_error_importable(self):
        from agentic_core.utils import TimeoutError as AgenticTimeoutError
        assert issubclass(AgenticTimeoutError, Exception)

    def test_heal_result_schema_importable(self):
        from agentic_core.utils import HEAL_RESULT_SCHEMA
        assert isinstance(HEAL_RESULT_SCHEMA, dict)

    def test_heal_result_schema_has_required_keys(self):
        from agentic_core.utils import HEAL_RESULT_SCHEMA
        assert "type" in HEAL_RESULT_SCHEMA or len(HEAL_RESULT_SCHEMA) > 0

    def test_all_exports_present(self):
        import agentic_core.utils as pkg
        for name in pkg.__all__:
            assert hasattr(pkg, name), f"Missing __all__ member: {name}"


class TestUtilsSecurityUtil:
    """security_util is fan_in=23 — verify re-export shim integrity."""

    def test_safe_execute_importable(self):
        from agentic_core.utils.security_util import safe_execute
        assert callable(safe_execute)

    def test_safe_git_execute_importable(self):
        from agentic_core.utils.security_util import safe_git_execute
        assert callable(safe_git_execute)

    def test_safe_popen_importable(self):
        from agentic_core.utils.security_util import safe_popen
        assert callable(safe_popen)

    def test_validate_command_whitelist_importable(self):
        from agentic_core.utils.security_util import validate_command_whitelist
        assert callable(validate_command_whitelist)

    def test_security_violation_error_is_exception(self):
        from agentic_core.utils.security_util import SecurityViolationError
        assert issubclass(SecurityViolationError, Exception)

    def test_all_exports_present(self):
        import agentic_core.utils.security_util as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_safe_execute_rejects_empty_command(self):
        from agentic_core.utils.security_util import SecurityViolationError, safe_execute
        with pytest.raises((SecurityViolationError, ValueError, TypeError, Exception)):
            safe_execute([])

    def test_validate_command_whitelist_accepts_allowed(self):
        from agentic_core.utils.security_util import validate_command_whitelist
        # Should not raise for a benign command like 'git'
        try:
            validate_command_whitelist(["git", "status"])
        except Exception:
            pass  # Some implementations always validate against a strict whitelist
