"""Tests for `tools.ledgers.hook_helpers`.

Covers the Execution + Write + Observability surface intersections
(per hardened concentration analysis 2026-04-28). This module is the
single convenience surface every Windsurf post-hook uses to write router-
decision rows; the fail-soft contract is constitutional (§29) — the helper
MUST swallow every exception so that ledger failures cannot crash hook
chains.

Tested invariants:
    1. emit_ledger_event returns "" on missing ledger writer (fail-soft)
    2. emit_ledger_event returns "" on writer.append exception (fail-soft)
    3. emit_ledger_event returns event_id on success path
    4. bind_ledger_outcome returns False on empty event_id (no-op)
    5. bind_ledger_outcome returns False on writer exception (fail-soft)
    6. bind_ledger_outcome returns True on success path
    7. emit_ledger_event passes all kwargs through to writer.append
    8. broad-exception swallow does NOT eat KeyboardInterrupt or SystemExit
       (catching `Exception` excludes BaseException subclasses by design).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.ledgers.hook_helpers import bind_ledger_outcome, emit_ledger_event  # noqa: E402


class TestEmitLedgerEventFailSoft:
    """emit_ledger_event MUST never raise — hook fail-soft contract."""

    def test_returns_empty_when_writer_for_raises(self):
        with mock.patch(
            "tools.ledgers.writer_for",
            side_effect=ImportError("no module"),
        ):
            result = emit_ledger_event(ledger="missing_ledger", event_kind="x")
            assert result == ""

    def test_returns_empty_when_append_raises(self):
        mock_writer = mock.MagicMock()
        mock_writer.append.side_effect = RuntimeError("disk full")
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            result = emit_ledger_event(ledger="any", event_kind="x")
            assert result == ""

    def test_returns_empty_string_on_attribute_error(self):
        with mock.patch(
            "tools.ledgers.writer_for",
            side_effect=AttributeError("nope"),
        ):
            result = emit_ledger_event(ledger="any", event_kind="x")
            assert result == ""


class TestEmitLedgerEventSuccess:
    """Happy path returns the writer's event_id."""

    def test_returns_event_id_on_success(self):
        mock_writer = mock.MagicMock()
        mock_writer.append.return_value = "evt-12345"
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            result = emit_ledger_event(
                ledger="tool_routing",
                event_kind="retrieval_tool_choice",
            )
            assert result == "evt-12345"

    def test_passes_all_kwargs_to_append(self):
        mock_writer = mock.MagicMock()
        mock_writer.append.return_value = "evt-1"
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            emit_ledger_event(
                ledger="L1_c0",
                event_kind="retrieval_decision",
                prediction={"k": 3},
                outcome={"hits": 2},
                score_band="correct",
                score_numeric=0.95,
                repo_area="agentic_core/L1_cognition/foo.py",
                session_id="sess-1",
                branch="main",
                commit_sha="abc123",
                adg_snapshot_id="snap-1",
                latency_ms=42,
                metadata={"k1": "v1"},
            )
            kwargs = mock_writer.append.call_args.kwargs
            assert kwargs["event_kind"] == "retrieval_decision"
            assert kwargs["prediction"] == {"k": 3}
            assert kwargs["outcome"] == {"hits": 2}
            assert kwargs["score_band"] == "correct"
            assert kwargs["score_numeric"] == 0.95
            assert kwargs["repo_area"] == "agentic_core/L1_cognition/foo.py"
            assert kwargs["session_id"] == "sess-1"
            assert kwargs["branch"] == "main"
            assert kwargs["commit_sha"] == "abc123"
            assert kwargs["adg_snapshot_id"] == "snap-1"
            assert kwargs["latency_ms"] == 42
            assert kwargs["metadata"] == {"k1": "v1"}

    def test_routes_to_correct_writer_per_ledger_name(self):
        """Different ledger names → different writer_for calls."""
        with mock.patch("tools.ledgers.writer_for") as mock_factory:
            mock_factory.return_value = mock.MagicMock(append=mock.MagicMock(return_value="evt"))
            emit_ledger_event(ledger="router_l0_bandit", event_kind="x")
            emit_ledger_event(ledger="router_l6_promo", event_kind="y")
            calls = [c.args[0] for c in mock_factory.call_args_list]
            assert "router_l0_bandit" in calls
            assert "router_l6_promo" in calls


class TestBindLedgerOutcomeFailSoft:
    def test_returns_false_on_empty_event_id(self):
        # Short-circuit before any writer lookup
        assert bind_ledger_outcome(ledger="x", event_id="", outcome={}) is False

    def test_returns_false_when_writer_for_raises(self):
        with mock.patch(
            "tools.ledgers.writer_for",
            side_effect=ImportError,
        ):
            assert bind_ledger_outcome(ledger="x", event_id="evt-1", outcome={}) is False

    def test_returns_false_when_bind_outcome_raises(self):
        mock_writer = mock.MagicMock()
        mock_writer.bind_outcome.side_effect = RuntimeError("locked")
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            assert bind_ledger_outcome(ledger="x", event_id="evt-1", outcome={}) is False


class TestBindLedgerOutcomeSuccess:
    def test_returns_true_on_success(self):
        mock_writer = mock.MagicMock()
        mock_writer.bind_outcome.return_value = True
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            result = bind_ledger_outcome(
                ledger="L0_bandit",
                event_id="evt-42",
                outcome={"reward": 1.0},
                score_band="correct",
                score_numeric=1.0,
                latency_ms=15,
            )
            assert result is True

    def test_passes_kwargs_through_to_bind_outcome(self):
        mock_writer = mock.MagicMock()
        mock_writer.bind_outcome.return_value = True
        with mock.patch("tools.ledgers.writer_for", return_value=mock_writer):
            bind_ledger_outcome(
                ledger="x",
                event_id="evt-1",
                outcome={"r": 0.7},
                score_band="incorrect",
                score_numeric=0.3,
                latency_ms=99,
            )
            args, kwargs = mock_writer.bind_outcome.call_args
            assert args[0] == "evt-1"  # positional event_id
            assert kwargs["outcome"] == {"r": 0.7}
            assert kwargs["score_band"] == "incorrect"
            assert kwargs["score_numeric"] == 0.3
            assert kwargs["latency_ms"] == 99


class TestBaseExceptionsNotSwallowed:
    """The fail-soft `except Exception` MUST NOT swallow KeyboardInterrupt or
    SystemExit (those derive from BaseException, not Exception). This is the
    constitutional contract that prevents hooks from making the process
    unkillable."""

    def test_keyboard_interrupt_propagates(self):
        with mock.patch(
            "tools.ledgers.writer_for",
            side_effect=KeyboardInterrupt,
        ):
            try:
                emit_ledger_event(ledger="x", event_kind="y")
            except KeyboardInterrupt:
                # Expected — NOT swallowed
                return
            raise AssertionError("KeyboardInterrupt was swallowed")

    def test_system_exit_propagates(self):
        with mock.patch(
            "tools.ledgers.writer_for",
            side_effect=SystemExit(1),
        ):
            try:
                emit_ledger_event(ledger="x", event_kind="y")
            except SystemExit:
                # Expected — NOT swallowed
                return
            raise AssertionError("SystemExit was swallowed")
