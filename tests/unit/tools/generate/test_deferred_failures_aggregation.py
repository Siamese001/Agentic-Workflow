"""Tests for fail-aggregating gate chain (plan adg-fail-aggregating-gate-chain-9d4e1f W2.4 + W3).

Covers:
  - record_or_exit fail-fast (no env var) → SystemExit
  - record_or_exit defer mode (legacy ADG_CONTINUE_ON_P0=1) → records, returns
  - record_or_exit defer mode (canonical ADG_CONTINUE_ON_GATE_FAILURE=1) → records, returns
  - record_or_exit explicit defer_exit=True overrides env
  - record_or_exit explicit defer_exit=False overrides env
  - format_summary_table renders all recorded gates with rc + message
  - format_summary_table returns empty string when registry is empty
  - deferred_exit_code returns first non-zero rc; 0 when empty
"""
from __future__ import annotations

import os

import pytest

from tools.generate.integration import deferred_failures as df


@pytest.fixture(autouse=True)
def _reset_registry_and_env(monkeypatch):
    df.reset_for_tests()
    monkeypatch.delenv("ADG_CONTINUE_ON_P0", raising=False)
    monkeypatch.delenv("ADG_CONTINUE_ON_GATE_FAILURE", raising=False)
    yield
    df.reset_for_tests()


# ---- record_or_exit semantics --------------------------------------------------


def test_record_or_exit_fail_fast_when_no_env_var():
    with pytest.raises(SystemExit) as exc:
        df.record_or_exit("Test_gate", 7, message="hard fail")
    assert exc.value.code == 7
    # No registry pollution on fail-fast (since process would have exited).
    assert df.deferred_failure_summary() == []


def test_record_or_exit_defers_with_legacy_env_var(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")
    df.record_or_exit("P0_layer_violations", 1, message="10 violations")
    rows = df.deferred_failure_summary()
    assert len(rows) == 1
    assert rows[0]["gate_name"] == "P0_layer_violations"
    assert rows[0]["rc"] == 1
    assert rows[0]["message"] == "10 violations"


def test_record_or_exit_defers_with_canonical_env_var(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    df.record_or_exit("P1_ratchet", 1, message="155 > 80")
    assert df.is_failure_deferred()
    assert df.deferred_exit_code() == 1


def test_record_or_exit_explicit_defer_overrides_env(monkeypatch):
    # Env var off, but explicit defer_exit=True takes precedence.
    monkeypatch.delenv("ADG_CONTINUE_ON_P0", raising=False)
    df.record_or_exit("Forced_defer", 2, message="forced", defer_exit=True)
    rows = df.deferred_failure_summary()
    assert len(rows) == 1
    assert rows[0]["gate_name"] == "Forced_defer"


def test_record_or_exit_explicit_no_defer_overrides_env(monkeypatch):
    # Env var on, but explicit defer_exit=False forces fail-fast.
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    with pytest.raises(SystemExit) as exc:
        df.record_or_exit("Forced_exit", 3, message="forced exit", defer_exit=False)
    assert exc.value.code == 3


def test_record_or_exit_rc_zero_is_noop():
    # Passing rc=0 should never pollute the registry.
    df.record_or_exit("Pass_gate", 0, message="passed")
    assert df.deferred_failure_summary() == []
    assert df.deferred_exit_code() == 0


# ---- multi-gate accumulation ---------------------------------------------------


def test_multiple_gates_accumulate_in_order(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    df.record_or_exit("Gate_A", 1, message="A failed")
    df.record_or_exit("Gate_B", 2, message="B failed")
    df.record_or_exit("Gate_C", 0, message="C passed")  # rc=0 ignored
    df.record_or_exit("Gate_D", 5, message="D failed")
    rows = df.deferred_failure_summary()
    assert [r["gate_name"] for r in rows] == ["Gate_A", "Gate_B", "Gate_D"]
    # First non-zero rc wins.
    assert df.deferred_exit_code() == 1


def test_re_recording_same_gate_overwrites_rc_message(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    df.record_or_exit("Gate_X", 1, message="first")
    df.record_or_exit("Gate_X", 7, message="second")
    rows = df.deferred_failure_summary()
    assert len(rows) == 1
    assert rows[0]["rc"] == 7
    assert rows[0]["message"] == "second"


# ---- format_summary_table ------------------------------------------------------


def test_format_summary_table_empty_registry():
    assert df.format_summary_table() == ""


def test_format_summary_table_renders_all_rows(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    df.record_or_exit("P0_layer_violations", 1, message="10 violations", plan_path="plans/p0.md")
    df.record_or_exit("P1_ratchet", 1, message="155 > 80")
    df.record_or_exit("Witness_classB", 2, message="2 breaches")
    table = df.format_summary_table()
    # Every gate appears.
    for name in ("P0_layer_violations", "P1_ratchet", "Witness_classB"):
        assert name in table, f"gate {name} not in table:\n{table}"
    # Messages appear (truncation aware).
    assert "10 violations" in table
    assert "155 > 80" in table
    assert "2 breaches" in table
    # Plan path surfaced.
    assert "plans/p0.md" in table
    # Header + footer present.
    assert "DEFERRED FAILURE SUMMARY" in table
    assert "Total deferred failures: 3" in table
    assert "Final exit code: 1" in table


def test_format_summary_table_truncates_overlong_message(monkeypatch):
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")
    long_msg = "x" * 500
    df.record_or_exit("Verbose_gate", 1, message=long_msg)
    table = df.format_summary_table()
    # The message column is capped at 80 chars; full 500-char string must NOT appear.
    assert long_msg not in table
    assert "Verbose_gate" in table
