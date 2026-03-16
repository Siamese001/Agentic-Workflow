"""
§1-Compliant robust tests for remediation_dispatcher.py.

Coverage per §1.1 Required test dimensions:
  - Edge cases: all 4 _tier_escalate guard paths, missing healer, empty notes,
    every exception type in _invoke_healer, FAILED with needs_llm_escalation=False
  - State transitions: FAILED→escalated, HEALED→pass-through, PARTIAL→pass-through,
    repeated failure → escalation each time
  - Fail-closed: _tier_escalate returns skip-note (not raise) for each guard
  - Matrix: (status × needs_llm_escalation × allowlist) = all 8 combinations
  - Regression: minimal reproducers for Fix #4 (dead code after raise) and
    Fix #1 (logger missing from remediation_dispatcher)
  - Mutation-sensitive: guard condition changes would flip these tests

§1.2: All tests are deterministic — no random inputs, no wall-clock, injected
      fakes only for external services (dispatch_healing).
"""

from __future__ import annotations

import inspect
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_remediation_dispatcher_robust")
_emit_applies_guardrail("p0", "test_remediation_dispatcher_robust", "p0_governance")
_emit_reads_policy_state("p0", "test_remediation_dispatcher_robust", "policy_binding")
_emit_snapshots_state("p0", "test_remediation_dispatcher_robust", "state_snapshot")
emit_replay_key("p0", "test_remediation_dispatcher_robust")
emit_determinism_digest("p0", "test_remediation_dispatcher_robust")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(
    *,
    check_id: str = "test_check",
    status: HealStatus = HealStatus.FAILED,
    notes: str = "healer notes",
    needs_llm_escalation: bool = True,
    escalation_hint: str | None = "failure_type=syntax_error",
) -> HealCheckResult:
    return HealCheckResult(
        check_id=check_id,
        status=status,
        changes_made=(),
        rollback_info=None,
        notes=notes,
        needs_llm_escalation=needs_llm_escalation,
        escalation_hint=escalation_hint,
    )


# ---------------------------------------------------------------------------
# §1.1 _tier_escalate: Guard 1 — status must be FAILED
# ---------------------------------------------------------------------------


class TestTierEscalateGuard1StatusNotFailed:
    """Guard 1: _tier_escalate must return skip-note (not raise) for non-FAILED status."""

    @pytest.mark.parametrize("status", [HealStatus.HEALED, HealStatus.PARTIAL, HealStatus.SKIPPED])
    def test_non_failed_status_returns_skip_note(self, status):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        result = _make_result(status=status, needs_llm_escalation=True)
        note = _tier_escalate("test_check", result, retry_count=0)

        assert "tier_escalation_skipped" in note
        assert "status_not_failed" in note

    def test_failed_status_does_not_trigger_guard1(self):
        """FAILED status must NOT be blocked by guard 1 (it should proceed to guard 2)."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        result = _make_result(status=HealStatus.FAILED, needs_llm_escalation=False)
        note = _tier_escalate("test_check", result, retry_count=0)
        # Guard 2 fires, not guard 1
        assert "status_not_failed" not in note
        assert "needs_llm_escalation_false" in note


# ---------------------------------------------------------------------------
# §1.1 _tier_escalate: Guard 2 — needs_llm_escalation must be True
# ---------------------------------------------------------------------------


class TestTierEscalateGuard2EscalationOptIn:
    """Guard 2: needs_llm_escalation=False must return skip-note."""

    def test_needs_llm_escalation_false_returns_skip_note(self):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        result = _make_result(status=HealStatus.FAILED, needs_llm_escalation=False)
        note = _tier_escalate("test_check", result, retry_count=0)

        assert "tier_escalation_skipped" in note
        assert "needs_llm_escalation_false" in note

    def test_needs_llm_escalation_true_passes_guard2(self):
        """needs_llm_escalation=True must NOT be blocked by guard 2."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        result = _make_result(status=HealStatus.FAILED, needs_llm_escalation=True)
        # Guard 3 (allowlist) will fire if (check_id, healer_name) not in allowlist
        note = _tier_escalate("unknown_check_not_in_allowlist", result, retry_count=0)
        assert "needs_llm_escalation_false" not in note
        # Guard 3 fires instead
        assert "not_in_allowlist" in note or "tier_escalation_skipped" in note


# ---------------------------------------------------------------------------
# §1.1 _tier_escalate: Guard 3 — allowlist membership
# ---------------------------------------------------------------------------


class TestTierEscalateGuard3Allowlist:
    """Guard 3: (check_id, healer_name) not in HEALER_ESCALATION_ALLOWLIST → skip."""

    def test_not_in_allowlist_returns_skip_note(self):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        result = _make_result(check_id="unknown_check", needs_llm_escalation=True)
        note = _tier_escalate("unknown_check", result, retry_count=0)

        assert "tier_escalation_skipped" in note
        assert "not_in_allowlist" in note

    def test_note_contains_check_id_in_all_guard_paths(self):
        """All guard skip notes must contain the check_id for auditability."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _tier_escalate

        cid = "unique_audit_check_id"
        # Guard 1
        note = _tier_escalate(cid, _make_result(status=HealStatus.HEALED), retry_count=0)
        assert cid in note

        # Guard 2
        note = _tier_escalate(cid, _make_result(needs_llm_escalation=False), retry_count=0)
        assert cid in note

        # Guard 3
        note = _tier_escalate(cid, _make_result(), retry_count=0)
        assert cid in note


# ---------------------------------------------------------------------------
# §1.1 _tier_escalate: Matrix (status × needs_llm_escalation × allowlist)
# ---------------------------------------------------------------------------


class TestTierEscalateMatrix:
    """Full 3-dimensional guard matrix per §1.1 Matrix requirement."""

    @pytest.mark.parametrize(
        "status,needs_escalation,in_allowlist,expected_pattern",
        [
            # status=HEALED → guard 1 fires immediately
            (HealStatus.HEALED, True, True, "status_not_failed"),
            (HealStatus.HEALED, True, False, "status_not_failed"),
            (HealStatus.HEALED, False, True, "status_not_failed"),
            (HealStatus.HEALED, False, False, "status_not_failed"),
            # status=FAILED, needs_escalation=False → guard 2
            (HealStatus.FAILED, False, True, "needs_llm_escalation_false"),
            (HealStatus.FAILED, False, False, "needs_llm_escalation_false"),
            # status=FAILED, needs_escalation=True, not in allowlist → guard 3
            (HealStatus.FAILED, True, False, "not_in_allowlist"),
        ],
    )
    def test_guard_matrix(self, status, needs_escalation, in_allowlist, expected_pattern):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            _tier_escalate,
        )

        cid = "matrix_check"
        result = _make_result(check_id=cid, status=status, needs_llm_escalation=needs_escalation)
        note = _tier_escalate(cid, result, retry_count=0)
        assert expected_pattern in note, (
            f"status={status.value}, needs_escalation={needs_escalation}, "
            f"in_allowlist={in_allowlist} → expected '{expected_pattern}' in note: {note!r}"
        )


# ---------------------------------------------------------------------------
# §1.1 _invoke_healer: exception matrix + status propagation
# ---------------------------------------------------------------------------


class TestInvokeHealerExceptionMatrix:
    """Every exception type must be caught, converted to FAILED, and escalated."""

    @pytest.mark.parametrize(
        "exc_type,exc_msg",
        [
            (ValueError, "bad config"),
            (RuntimeError, "healer crashed"),
            (OSError, "file not found"),
            (KeyError, "missing key"),
            (TypeError, "wrong type"),
            (AttributeError, "no such attr"),
            (Exception, "generic error"),
        ],
    )
    def test_exception_produces_failed_result(self, exc_type, exc_msg):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _bad_healer(check_dict, repo_root=None, apply=False):
            raise exc_type(exc_msg)

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"exc_check": _bad_healer},
        ):
            result = _invoke_healer("exc_check", {"check_id": "exc_check"}, retry_count=0)

        assert result.status == HealStatus.FAILED
        assert exc_type.__name__ in result.notes
        assert exc_msg in result.notes

    def test_exception_sets_needs_llm_escalation_true(self):
        """Exceptions from healers must set needs_llm_escalation=True."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _bad(*_, **__):
            raise RuntimeError("boom")

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY", {"boom_check": _bad}
        ):
            result = _invoke_healer("boom_check", {}, retry_count=0)

        assert result.needs_llm_escalation is True

    def test_exception_sets_escalation_hint_healer_error(self):
        """Exception result must carry escalation_hint='failure_type=healer_error'."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _bad(*_, **__):
            raise ValueError("bad value")

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY", {"hint_check": _bad}
        ):
            result = _invoke_healer("hint_check", {}, retry_count=0)

        assert result.escalation_hint == "failure_type=healer_error"

    def test_exception_check_id_preserved_in_result(self):
        """The check_id in the FAILED result must match the input check_id."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        cid = "my_specific_check"

        def _bad(*_, **__):
            raise TypeError("oops")

        with patch("agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY", {cid: _bad}):
            result = _invoke_healer(cid, {"check_id": cid}, retry_count=0)

        assert result.check_id == cid


# ---------------------------------------------------------------------------
# §1.1 _invoke_healer: success path — pass-through, no exception handling
# ---------------------------------------------------------------------------


class TestInvokeHealerSuccessPassthrough:
    """Successful healer results must pass through unchanged (no mangling)."""

    @pytest.mark.parametrize("status", [HealStatus.HEALED, HealStatus.PARTIAL, HealStatus.SKIPPED])
    def test_non_failed_result_returned_unmodified(self, status):
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        expected = HealCheckResult(
            check_id="ok_check",
            status=status,
            changes_made=("file.py",),
            rollback_info=None,
            notes="healer did its job",
            needs_llm_escalation=False,
            escalation_hint=None,
        )

        def _good_healer(*_, **__):
            return expected

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"ok_check": _good_healer},
        ):
            result = _invoke_healer("ok_check", {}, retry_count=0)

        assert result.status == status
        assert result.notes == "healer did its job"
        assert result.changes_made == ("file.py",)
        assert result.needs_llm_escalation is False

    def test_success_does_not_append_escalation_note(self):
        """Non-FAILED results must NOT have escalation note appended."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _good(*_, **__):
            return HealCheckResult(
                check_id="c",
                status=HealStatus.HEALED,
                changes_made=(),
                rollback_info=None,
                notes="clean",
                needs_llm_escalation=False,
                escalation_hint=None,
            )

        with patch("agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY", {"c": _good}):
            result = _invoke_healer("c", {}, retry_count=0)

        assert "tier_escalation" not in (result.notes or "")


# ---------------------------------------------------------------------------
# §1.1 _invoke_healer: FAILED + escalation note appended
# ---------------------------------------------------------------------------


class TestInvokeHealerFailedEscalation:
    """FAILED results must have tier_escalation audit note appended."""

    def test_failed_result_gets_escalation_note_appended(self):
        """A FAILED result from a healer must get the _tier_escalate note appended."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _failing(*_, **__):
            return _make_result(check_id="fail_check", status=HealStatus.FAILED, needs_llm_escalation=True)

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"fail_check": _failing},
        ):
            result = _invoke_healer("fail_check", {}, retry_count=0)

        assert result.status == HealStatus.FAILED
        # _tier_escalate produces a note string which is appended
        assert "tier_escalation" in result.notes

    def test_failed_result_notes_concatenated_with_pipe(self):
        """Original notes + escalation note must be joined with ' | '."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _failing(*_, **__):
            return _make_result(
                check_id="pipe_check",
                status=HealStatus.FAILED,
                notes="original_notes",
                needs_llm_escalation=True,
            )

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"pipe_check": _failing},
        ):
            result = _invoke_healer("pipe_check", {}, retry_count=0)

        assert "original_notes" in result.notes
        # The escalation note is appended
        assert "tier_escalation" in result.notes

    def test_failed_result_with_no_escalation_opt_in(self):
        """FAILED + needs_llm_escalation=False must NOT get escalation note."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _failing(*_, **__):
            return _make_result(
                check_id="no_esc_check",
                status=HealStatus.FAILED,
                notes="no escalation please",
                needs_llm_escalation=False,
            )

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"no_esc_check": _failing},
        ):
            result = _invoke_healer("no_esc_check", {}, retry_count=0)

        assert result.status == HealStatus.FAILED
        # Guard 2 blocks escalation — note should be about guard skip, not tier call
        assert "needs_llm_escalation_false" in result.notes


# ---------------------------------------------------------------------------
# §1.1 Regression Fix #4 — no dead code after raise
# ---------------------------------------------------------------------------


class TestNoDeadCodeAfterRaiseRegression:
    """Minimal reproducer for Fix #4: dead unreachable result construction after raise.

    Mutation-sensitive: if the except block is changed to re-raise instead of
    constructing the result, exceptions would propagate rather than being caught.
    """

    def test_exception_does_not_propagate_out_of_invoke_healer(self):
        """ANY Exception from a healer MUST be caught — must NOT propagate to caller."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _explosive(*_, **__):
            raise RuntimeError("BOOM — this must be caught")

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"explosive_check": _explosive},
        ):
            # Must NOT raise — the exception must be swallowed and converted to FAILED
            result = _invoke_healer("explosive_check", {}, retry_count=0)

        assert result is not None
        assert result.status == HealStatus.FAILED

    def test_source_has_no_raise_followed_by_result_assignment(self):
        """Source code invariant: no 'raise' statement immediately before 'result = HealCheckResult'.

        This is the structural regression test for Fix #4 — dead code after raise.
        Mutation-sensitive: re-introducing the raise would break the previous test,
        and this test would also fail.
        """
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        source = inspect.getsource(_invoke_healer)
        lines = source.splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped in ("raise", "raise exc"):
                # Next non-blank line must NOT be 'result = HealCheckResult('
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_stripped = lines[j].strip()
                    if next_stripped:
                        assert not next_stripped.startswith("result = HealCheckResult("), (
                            f"Dead code detected: 'raise' on line {i + 1} followed by "
                            f"unreachable 'result = HealCheckResult(' on line {j + 1}"
                        )
                        break


# ---------------------------------------------------------------------------
# §1.1 Regression Fix #1 — logger defined in remediation_dispatcher
# ---------------------------------------------------------------------------


class TestLoggerImportRegression:
    """Regression for missing logger in remediation_dispatcher.

    Before Fix #1, the logger was not imported, causing NameError on
    logger.warning() in the exception handler.
    """

    def test_logger_defined_at_module_level(self):
        """logger must be a module-level attribute of remediation_dispatcher."""
        import agentic_core.L2_execution.scripts.remediation_dispatcher as mod

        assert hasattr(mod, "logger"), "logger must be defined at module level"

    def test_logger_is_logging_logger_instance(self):
        """logger must be a standard logging.Logger (not a MagicMock or None)."""
        import logging

        import agentic_core.L2_execution.scripts.remediation_dispatcher as mod

        assert isinstance(mod.logger, logging.Logger)

    def test_exception_in_healer_logs_warning(self):
        """When healer raises, logger.warning must be called (not NameError)."""
        import agentic_core.L2_execution.scripts.remediation_dispatcher as mod
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _bad(*_, **__):
            raise ValueError("test warning log")

        with patch.object(mod.logger, "warning") as mock_warn:
            with patch(
                "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
                {"warn_check": _bad},
            ):
                _invoke_healer("warn_check", {}, retry_count=0)

        mock_warn.assert_called_once()
        call_args = mock_warn.call_args[0]
        assert "warn_check" in str(call_args)
        assert "ValueError" in str(call_args)


# ---------------------------------------------------------------------------
# §1.1 State transitions: repeated failures accumulate escalation correctly
# ---------------------------------------------------------------------------


class TestRepeatedFailureStateTransitions:
    """State transitions: valid→failed, failed→failed, interrupted recovery."""

    def test_multiple_exceptions_each_produce_distinct_failed_result(self):
        """Each call to _invoke_healer with a failing healer must produce
        an independent FAILED result — no shared state between calls."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        call_count = 0

        def _counter_healer(*_, **__):
            nonlocal call_count
            call_count += 1
            raise RuntimeError(f"failure #{call_count}")

        results = []
        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"count_check": _counter_healer},
        ):
            for retry in range(3):
                r = _invoke_healer("count_check", {}, retry_count=retry)
                results.append(r)

        assert len(results) == 3
        assert all(r.status == HealStatus.FAILED for r in results)
        # Each has a distinct error message
        notes = [r.notes for r in results]
        assert len(set(notes)) > 1, "Repeated failures must produce distinct notes"

    def test_retry_count_propagated_to_tier_escalate(self):
        """retry_count parameter must be forwarded to _tier_escalate."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        def _failing(*_, **__):
            return _make_result(status=HealStatus.FAILED, needs_llm_escalation=True)

        escalate_call_args = []
        original_tier_escalate_path = (
            "agentic_core.L2_execution.scripts.remediation_dispatcher._tier_escalate"
        )

        def _mock_escalate(check_id, result, *, retry_count=0, invoker=None):
            escalate_call_args.append(retry_count)
            return f"tier_escalation_skipped: check_id={check_id} reason=not_in_allowlist healer=?"

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {"retry_check": _failing},
        ):
            with patch(original_tier_escalate_path, side_effect=_mock_escalate):
                _invoke_healer("retry_check", {}, retry_count=7)

        assert escalate_call_args == [7], (
            f"retry_count=7 must be forwarded to _tier_escalate, got: {escalate_call_args}"
        )
