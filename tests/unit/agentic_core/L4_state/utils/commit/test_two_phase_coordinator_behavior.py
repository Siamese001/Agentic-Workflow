"""Behavioral tests for ``agentic_core.L4_state.utils.commit.two_phase_coordinator``.

Covers Addendum 2.3 Two-Phase Commit semantics:
- execute_commit: both phases succeed → returns (resource_result, ledger_result).
- Phase 1 failure → MutationCommitFailure with "Phase 1" marker; ledger never invoked.
- Phase 2 failure → MutationCommitFailure with "Phase 2" marker and manual-rollback note.
- safe_commit wraps raise → returns structured dict.
- Context is included in error message for diagnosability.
- Only the documented exception types (AttributeError/RuntimeError/TypeError/ValueError)
  are trapped into MutationCommitFailure; other exceptions propagate.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L4_state.utils.commit.two_phase_coordinator import TwoPhaseCoordinator
from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure


class TestExecuteCommitSuccess:
    def test_returns_both_results(self) -> None:
        c = TwoPhaseCoordinator()
        resource_calls: list[str] = []
        ledger_calls: list[str] = []

        def resource() -> str:
            resource_calls.append("r")
            return "RESOURCE_OK"

        def ledger() -> str:
            ledger_calls.append("l")
            return "LEDGER_OK"

        r, l = c.execute_commit(resource, ledger, context={"file": "f"})
        assert r == "RESOURCE_OK"
        assert l == "LEDGER_OK"
        assert resource_calls == ["r"]
        assert ledger_calls == ["l"]

    def test_context_none_ok(self) -> None:
        c = TwoPhaseCoordinator()
        r, l = c.execute_commit(lambda: 1, lambda: 2)
        assert (r, l) == (1, 2)


class TestExecuteCommitPhase1Failure:
    @pytest.mark.parametrize(
        "exc",
        [ValueError("bad"), RuntimeError("boom"), TypeError("nope"), AttributeError("x")],
    )
    def test_phase_1_error_raises_mutation_commit_failure(
        self,
        exc: Exception,
    ) -> None:
        c = TwoPhaseCoordinator()
        ledger_calls: list[Any] = []

        def resource() -> Any:
            raise exc

        def ledger() -> Any:
            ledger_calls.append("l")  # pragma: no cover
            return "LEDGER_OK"

        with pytest.raises(MutationCommitFailure) as info:
            c.execute_commit(resource, ledger)
        assert "Phase 1" in str(info.value)
        assert ledger_calls == []  # ledger never invoked

    def test_phase_1_non_trapped_exc_propagates(self) -> None:
        c = TwoPhaseCoordinator()

        def resource() -> Any:
            raise KeyError("not-trapped")

        with pytest.raises(KeyError, match="not-trapped"):
            c.execute_commit(resource, lambda: None)

    def test_phase_1_error_chains_original(self) -> None:
        c = TwoPhaseCoordinator()
        orig = ValueError("orig")

        def resource() -> Any:
            raise orig

        with pytest.raises(MutationCommitFailure) as info:
            c.execute_commit(resource, lambda: None)
        assert info.value.__cause__ is orig


class TestExecuteCommitPhase2Failure:
    def test_phase_2_error_raises_mutation_commit_failure(self) -> None:
        c = TwoPhaseCoordinator()
        resource_calls: list[str] = []

        def resource() -> str:
            resource_calls.append("r")
            return "RESOURCE_OK"

        def ledger() -> Any:
            raise RuntimeError("ledger-down")

        with pytest.raises(MutationCommitFailure) as info:
            c.execute_commit(resource, ledger)
        msg = str(info.value)
        assert "Phase 2" in msg
        assert "manual rollback required" in msg
        assert resource_calls == ["r"]  # resource DID commit

    def test_phase_2_non_trapped_exc_propagates(self) -> None:
        c = TwoPhaseCoordinator()
        with pytest.raises(KeyError, match="prop"):
            c.execute_commit(lambda: "ok", lambda: (_ for _ in ()).throw(KeyError("prop")))


class TestContextInErrors:
    def test_context_included_in_phase_1_error(self) -> None:
        c = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure) as info:
            c.execute_commit(
                lambda: (_ for _ in ()).throw(ValueError("boom")),
                lambda: None,
                context={"file": "/tmp/x.py"},
            )
        assert "/tmp/x.py" in str(info.value)

    def test_context_included_in_phase_2_error(self) -> None:
        c = TwoPhaseCoordinator()
        with pytest.raises(MutationCommitFailure) as info:
            c.execute_commit(
                lambda: "ok",
                lambda: (_ for _ in ()).throw(RuntimeError("down")),
                context={"run": "abc123"},
            )
        assert "abc123" in str(info.value)


class TestSafeCommit:
    def test_success_returns_structured_dict(self) -> None:
        c = TwoPhaseCoordinator()
        out = c.safe_commit(lambda: "R", lambda: "L")
        assert out == {"success": True, "resource_result": "R", "ledger_result": "L"}

    def test_failure_returns_false_with_error(self) -> None:
        c = TwoPhaseCoordinator()
        out = c.safe_commit(
            lambda: (_ for _ in ()).throw(ValueError("bad")),
            lambda: None,
        )
        assert out["success"] is False
        assert "Phase 1" in out["error"]

    def test_phase_2_failure_also_returns_false(self) -> None:
        c = TwoPhaseCoordinator()
        out = c.safe_commit(
            lambda: "R",
            lambda: (_ for _ in ()).throw(RuntimeError("ledger")),
        )
        assert out["success"] is False
        assert "Phase 2" in out["error"]

    def test_non_trapped_exception_still_propagates(self) -> None:
        """safe_commit only wraps MutationCommitFailure — untrapped errors still raise."""
        c = TwoPhaseCoordinator()
        with pytest.raises(KeyError):
            c.safe_commit(
                lambda: (_ for _ in ()).throw(KeyError("prop")),
                lambda: None,
            )
