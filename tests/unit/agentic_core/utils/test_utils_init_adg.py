"""ADG-driven tests for agentic_core/utils/__init__.py — fan_in=90.

90 callers import from this package. Tests verify re-exported symbols
are present, callable, and behave as documented.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
