"""Live Claude X1D judge is ON by default when ANTHROPIC_API_KEY is present.

Regression guard: previously the live judge required APPS_LIC_RUN_LIVE_CLAUDE_X1D=1,
so production runs silently shipped with the required X1D judges missing -> Exit
fail-closed to blocked. It is now default-on (key present, outside pytest), with
an explicit opt-out, and stays off under pytest unless explicitly enabled.
"""

from __future__ import annotations

import pytest

from apps_lic.runtime.dispatch import canonical_dispatch as cd

FLAG = "APPS_LIC_RUN_LIVE_CLAUDE_X1D"


def test_default_on_when_key_present_outside_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)  # simulate production
    monkeypatch.delenv(FLAG, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-used")
    assert cd._live_x1d_judge_runner() is not None  # judges run by default


def test_explicit_off_suppresses_even_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-used")
    for off in ("0", "false", "no", "off"):
        monkeypatch.setenv(FLAG, off)
        assert cd._live_x1d_judge_runner() is None


def test_no_key_never_runs_live(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv(FLAG, raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert cd._live_x1d_judge_runner() is None


def test_under_pytest_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "yes")  # the test suite must not call live
    monkeypatch.delenv(FLAG, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-used")
    assert cd._live_x1d_judge_runner() is None


def test_under_pytest_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "yes")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-used")
    monkeypatch.setenv(FLAG, "1")
    assert cd._live_x1d_judge_runner() is not None
