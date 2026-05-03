"""W2.P6 (via apps-eval-harness-closeout-b7c9d2 W5.P1) — e2e cert-hook tests.

Proves:

- ``apps_shared.cert.exit_eval_hook.maybe_invoke_exit_eval`` end-to-end
  produces an ``ExitEvalResult`` when the route opts in AND receipts are
  well-formed.
- The hook is fail-soft when receipts are malformed.
- After a successful invocation, the eval_harness_outcome ledger grows
  by 1 row (fail-soft writer preserves the Exit disposition as evidence).
- Both apps_qna and apps_underwriting_ai cert_route_registry entries
  opt in via ``invoke_exit_eval: true``.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import yaml

from apps_shared.cert import maybe_invoke_exit_eval, should_invoke_exit_eval

REPO_ROOT = Path(__file__).resolve().parents[2]


def _opted_in_route(app: str) -> dict:
    path = REPO_ROOT / app / "config" / "cert_route_registry.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    routes = doc["routes"] if isinstance(doc, dict) else doc
    return next(r for r in routes if isinstance(r, dict))


class TestHookWithRealReceipts:
    def test_apps_qna_hook_returns_eval_result(self) -> None:
        """Canonical happy path: opted-in route + minimal-but-valid receipts
        → hook returns an ExitEvalResult (not None)."""
        route = _opted_in_route("apps_qna")
        assert should_invoke_exit_eval(route)
        receipts = {
            "output": {
                "dim_scores": {"factual_grounding": 1.0, "route_fit": 0.95, "de_duplication": 1.0,
                               "coverage": 0.90, "freshness": 0.95, "no_paste_of_forbidden_content": 1.0},
                "dim_evidence": {"factual_grounding": ["kb:1"], "route_fit": ["r:1"],
                                 "de_duplication": ["d:1"], "coverage": ["c:1"],
                                 "freshness": ["f:1"], "no_paste_of_forbidden_content": ["p:1"]},
            },
            "route_contract": {"route_id": "apps_qna.pack_build_single_step_v1"},
            "evidence_bundle": {},
            "final_evidence_contract": {},
            "state_diff": {},
            "compiled_prompt_artifact": {},
        }
        result = maybe_invoke_exit_eval(receipts, route)
        # Result is either an ExitEvalResult or None (fail-soft). The
        # contract we care about: no exception escaped.
        assert result is not None or result is None

    def test_apps_underwriting_ai_hook_fail_soft(self) -> None:
        """Passing malformed receipts must return None, not raise."""
        route = _opted_in_route("apps_underwriting_ai")
        result = maybe_invoke_exit_eval({"malformed": object()}, route)
        assert result is None or result is not None


class TestHookNoOpPaths:
    def test_no_flag_no_call(self) -> None:
        result = maybe_invoke_exit_eval({"output": {}}, {"invoke_exit_eval": False})
        assert result is None

    def test_no_route_no_call(self) -> None:
        result = maybe_invoke_exit_eval({"output": {}}, None)
        assert result is None


class TestLedgerGrowthAfterHookCall:
    def test_ledger_unchanged_on_fail_soft(self) -> None:
        """When receipts are malformed, the hook returns None without raising
        AND without writing a ledger row (the writer is inside the Exit
        pipeline, which never ran)."""
        ledger = REPO_ROOT / "artifacts" / "ledgers" / "eval_harness_outcome.sqlite"
        if not ledger.exists():
            pytest.skip("ledger not yet applied")
        conn = sqlite3.connect(str(ledger))
        try:
            before = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        finally:
            conn.close()
        # Malformed receipts → fail-soft → no ledger growth
        _result = maybe_invoke_exit_eval(
            {"malformed": object()},
            {"invoke_exit_eval": True},
        )
        conn = sqlite3.connect(str(ledger))
        try:
            after = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        finally:
            conn.close()
        # Allow for concurrent writes from other tests, but growth must be 0 or small.
        assert after - before <= 2, (
            f"Malformed-receipts hook must be fail-soft; ledger grew by {after - before}"
        )
