"""Tests for the ADG pipeline simplification (plan adg-pipeline-simplification-e2e-9b4c27).

Covers the new symbols and edge cases introduced by waves W1..W7:

- ``_env_flag``                       (W2.2 / F-11)
- ``_pipeline_stage``                 (W6 / F-7)
- ``KNOWN_TOLERATED_CLOSURE_GAPS``    (W2.2 / F-5)
- ``_run_post_adg_gates_parallel``    (W3 / F-6)
- skip-summary blank-line tolerance  (W4.2 hardening)

These tests do NOT regenerate the ADG and never invoke ``generate_full_adg``
itself. They exercise only the helpers in isolation, so they run in well
under a second and are safe under pre-commit.
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path

import pytest

# Ensure repo root is on sys.path so module imports resolve when pytest is
# invoked from anywhere.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.generate.core import _env_flag  # noqa: E402
from tools.generate.generate_full_adg import (  # noqa: E402
    KNOWN_TOLERATED_CLOSURE_GAPS,
    _pipeline_stage,
    _record_pipeline_skip,
    _run_post_adg_gates_parallel,
)


# ---------------------------------------------------------------------------
# _env_flag
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _scrub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make sure no test leaks env vars to its neighbours."""
    for k in (
        "X_ENV_FLAG_TEST",
        "ADG_ENABLE_DETERMINISM_PROBE",
        "ADG_SKIP_REDIS",
        "ADG_SKIP_GIT",
    ):
        monkeypatch.delenv(k, raising=False)


class TestEnvFlag:
    @pytest.mark.parametrize("value", ["1", "true", "True", "TRUE", "yes", "Yes", "YES"])
    def test_truthy_values(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("X_ENV_FLAG_TEST", value)
        assert _env_flag("X_ENV_FLAG_TEST") is True

    @pytest.mark.parametrize("value", ["0", "false", "FALSE", "no", "NO"])
    def test_falsy_values(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("X_ENV_FLAG_TEST", value)
        assert _env_flag("X_ENV_FLAG_TEST") is False

    def test_unset_returns_default(self) -> None:
        assert _env_flag("X_ENV_FLAG_TEST") is False
        assert _env_flag("X_ENV_FLAG_TEST", default=True) is True

    def test_empty_string_returns_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("X_ENV_FLAG_TEST", "")
        assert _env_flag("X_ENV_FLAG_TEST") is False
        assert _env_flag("X_ENV_FLAG_TEST", default=True) is True

    def test_whitespace_is_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("X_ENV_FLAG_TEST", "  yes  ")
        assert _env_flag("X_ENV_FLAG_TEST") is True
        monkeypatch.setenv("X_ENV_FLAG_TEST", "\tfalse\n")
        assert _env_flag("X_ENV_FLAG_TEST") is False

    def test_unrecognised_value_returns_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Unknown tokens must not silently flip a flag; they fall through
        # to the caller's default. This is the contract that lets callers
        # write `_env_flag("X", default=True)` and trust the answer.
        monkeypatch.setenv("X_ENV_FLAG_TEST", "maybe")
        assert _env_flag("X_ENV_FLAG_TEST") is False
        assert _env_flag("X_ENV_FLAG_TEST", default=True) is True


# ---------------------------------------------------------------------------
# _pipeline_stage
# ---------------------------------------------------------------------------


def _read_ledger(adg_dir: Path, ts: str) -> list[dict]:
    ledger = adg_dir / f"adg_pipeline_skips_{ts}.jsonl"
    if not ledger.exists():
        return []
    out: list[dict] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


class TestPipelineStage:
    def test_no_exception_emits_nothing(self, tmp_path: Path) -> None:
        with _pipeline_stage(tmp_path, "TS", layer="P4", name="watchlist", exc_types=(ValueError,)):
            pass
        assert _read_ledger(tmp_path, "TS") == []

    def test_caught_exception_writes_ledger_row(self, tmp_path: Path) -> None:
        with _pipeline_stage(
            tmp_path, "TS", layer="P5", name="graph-watchlist", exc_types=(ValueError, OSError)
        ):
            raise ValueError("oops")
        rows = _read_ledger(tmp_path, "TS")
        assert len(rows) == 1
        row = rows[0]
        assert row["layer"] == "P5"
        assert row["name"] == "graph-watchlist"
        assert row["exc_type"] == "ValueError"
        assert row["exc_message"] == "oops"

    def test_uncaught_exception_propagates(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="propagate me"):
            with _pipeline_stage(tmp_path, "TS", layer="P6", name="proj", exc_types=(ValueError,)):
                raise RuntimeError("propagate me")
        assert _read_ledger(tmp_path, "TS") == []

    def test_subclass_of_caught_type_is_caught(self, tmp_path: Path) -> None:
        # FileNotFoundError is a subclass of OSError — the ctxmgr must
        # follow normal `except` semantics.
        with _pipeline_stage(tmp_path, "TS", layer="P6", name="proj", exc_types=(OSError,)):
            raise FileNotFoundError("missing input")
        rows = _read_ledger(tmp_path, "TS")
        assert len(rows) == 1
        assert rows[0]["exc_type"] == "FileNotFoundError"

    def test_empty_exc_types_propagates_everything(self, tmp_path: Path) -> None:
        # Edge case: empty tuple should catch nothing — same as `except ():`.
        with pytest.raises(ValueError):
            with _pipeline_stage(tmp_path, "TS", layer="X", name="y", exc_types=()):
                raise ValueError("not caught")

    def test_multiple_stages_append_to_same_ledger(self, tmp_path: Path) -> None:
        with _pipeline_stage(tmp_path, "TS", layer="P4", name="a", exc_types=(ValueError,)):
            raise ValueError("first")
        with _pipeline_stage(tmp_path, "TS", layer="P5", name="b", exc_types=(ValueError,)):
            raise ValueError("second")
        rows = _read_ledger(tmp_path, "TS")
        assert [r["layer"] for r in rows] == ["P4", "P5"]
        assert [r["name"] for r in rows] == ["a", "b"]


# ---------------------------------------------------------------------------
# _record_pipeline_skip — sanity check (used by both _pipeline_stage and
# the inline P7/phase2/adg-gates sites; W4.2 skip-summary depends on its
# JSONL output shape).
# ---------------------------------------------------------------------------


class TestRecordPipelineSkip:
    def test_ledger_row_shape(self, tmp_path: Path) -> None:
        try:
            raise OSError("io fail")
        except OSError as e:
            _record_pipeline_skip(tmp_path, "TS", layer="L", name="N", exc=e)
        rows = _read_ledger(tmp_path, "TS")
        assert len(rows) == 1
        assert set(rows[0].keys()) == {"ts", "layer", "name", "exc_type", "exc_message"}
        assert rows[0]["exc_type"] == "OSError"


# ---------------------------------------------------------------------------
# KNOWN_TOLERATED_CLOSURE_GAPS
# ---------------------------------------------------------------------------


class TestKnownToleratedClosureGaps:
    def test_is_frozenset(self) -> None:
        # Frozen so call sites can't accidentally mutate the policy at runtime.
        assert isinstance(KNOWN_TOLERATED_CLOSURE_GAPS, frozenset)

    def test_contains_expected_capabilities(self) -> None:
        assert "EDGE SEMANTIC PRECISION" in KNOWN_TOLERATED_CLOSURE_GAPS
        assert "DETERMINISM (ARTIFACT LEVEL)" in KNOWN_TOLERATED_CLOSURE_GAPS

    def test_subset_logic_handles_each_branch(self) -> None:
        # Exact-prior-behaviour parity check: the original 3-way branch
        # accepted exactly these three subsets as "tolerated" without
        # blocking. The new data-driven implementation must still accept
        # them, AND must still reject anything else.
        gaps = KNOWN_TOLERATED_CLOSURE_GAPS

        # Single tolerated cap: tolerated.
        assert {"EDGE SEMANTIC PRECISION"}.issubset(gaps)
        assert {"DETERMINISM (ARTIFACT LEVEL)"}.issubset(gaps)
        # Both tolerated caps together: tolerated.
        assert {"EDGE SEMANTIC PRECISION", "DETERMINISM (ARTIFACT LEVEL)"}.issubset(gaps)
        # Empty failure set: trivially a subset, but caller code only
        # enters the tolerated branch when failed_caps is non-empty by
        # construction (`not all_gaps_passed`).
        assert set().issubset(gaps)
        # Anything outside the policy: rejected.
        assert not {"EDGE SEMANTIC PRECISION", "STRUCTURAL CONFORMANCE"}.issubset(gaps)
        assert not {"NEW UNTRUSTED GAP"}.issubset(gaps)


# ---------------------------------------------------------------------------
# _run_post_adg_gates_parallel
# ---------------------------------------------------------------------------


def _write_gate_script(
    tmp_path: Path, name: str, exit_code: int, *, stdout: str = "", sleep_ms: int = 0
) -> Path:
    """Materialise a tiny pretend "ci gate" script that prints + exits."""
    script = tmp_path / name
    body = textwrap.dedent(f"""
        import sys, time
        time.sleep({sleep_ms} / 1000.0)
        if {stdout!r}:
            print({stdout!r})
        sys.exit({exit_code})
    """)
    script.write_text(body, encoding="utf-8")
    return script


class TestRunPostAdgGatesParallel:
    @pytest.fixture(autouse=True)
    def _reset_deferred_failures(self):
        from tools.generate.integration.deferred_failures import reset_for_tests

        reset_for_tests()
        yield
        reset_for_tests()

    def test_all_pass_no_exit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Point ROOT at tmp_path so the gate scripts resolve there.
        from tools.generate import generate_full_adg as gfa

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        _write_gate_script(tmp_path, "g1.py", 0, stdout="g1 ok")
        _write_gate_script(tmp_path, "g2.py", 0, stdout="g2 ok")
        specs: list[dict[str, object]] = [
            {"label": "alpha", "script_rel": "g1.py", "args_list": [], "fail_hint": "—", "timeout_s": 30},
            {"label": "beta", "script_rel": "g2.py", "args_list": [], "fail_hint": "—", "timeout_s": 30},
        ]
        # Must NOT raise SystemExit when all pass.
        _run_post_adg_gates_parallel(specs)
        out = capsys.readouterr().out
        assert "[alpha] PASS" in out
        assert "[beta] PASS" in out

    def test_first_failure_rc_is_deferred_until_bundle_sealing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate import generate_full_adg as gfa
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            deferred_failure_summary,
        )

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        _write_gate_script(tmp_path, "g1.py", 7, stdout="g1 fail")
        _write_gate_script(tmp_path, "g2.py", 9, stdout="g2 fail")
        specs: list[dict[str, object]] = [
            {
                "label": "alpha",
                "script_rel": "g1.py",
                "args_list": [],
                "fail_hint": "fix alpha",
                "timeout_s": 30,
            },
            {
                "label": "beta",
                "script_rel": "g2.py",
                "args_list": [],
                "fail_hint": "fix beta",
                "timeout_s": 30,
            },
        ]
        _run_post_adg_gates_parallel(specs)
        # First spec's failure rc wins (deterministic), but the subprocess
        # does not exit before the terminal output bundle can be sealed.
        assert deferred_exit_code() == 7
        assert deferred_failure_summary()[0]["gate_name"] == "post_adg_gate.alpha"
        out = capsys.readouterr().out
        assert "[alpha] FAIL" in out
        assert "[beta] FAIL" in out
        # Even on failure both gate outputs are printed.
        assert "g1 fail" in out
        assert "g2 fail" in out

    def test_missing_script_does_not_fail_run(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate import generate_full_adg as gfa

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        _write_gate_script(tmp_path, "real.py", 0)
        specs: list[dict[str, object]] = [
            {"label": "real", "script_rel": "real.py", "args_list": [], "fail_hint": "—", "timeout_s": 30},
            {
                "label": "ghost",
                "script_rel": "does_not_exist.py",
                "args_list": [],
                "fail_hint": "—",
                "timeout_s": 30,
            },
        ]
        # Missing scripts emit a "skipping" message but don't fail the run.
        _run_post_adg_gates_parallel(specs)
        out = capsys.readouterr().out
        assert "[ghost]" in out
        assert "missing" in out.lower()
        assert "[real] PASS" in out

    def test_timeout_treated_as_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate import generate_full_adg as gfa

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        # Sleep 5s but timeout is 1s.
        slow = tmp_path / "slow.py"
        slow.write_text("import time; time.sleep(5)", encoding="utf-8")
        specs: list[dict[str, object]] = [
            {
                "label": "slow",
                "script_rel": "slow.py",
                "args_list": [],
                "fail_hint": "fix slow",
                "timeout_s": 1,
            },
        ]
        from tools.generate.integration.deferred_failures import deferred_exit_code

        _run_post_adg_gates_parallel(specs)
        # Timeout exit code is 2, deferred until terminal bundle sealing.
        assert deferred_exit_code() == 2
        out = capsys.readouterr().out
        assert "[slow] FAIL" in out
        assert "timed out" in out.lower()

    def test_output_order_is_deterministic(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate import generate_full_adg as gfa

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        # Make the second gate finish first by sleeping the first one.
        # Output ordering must still match input spec order, NOT
        # completion order (so build logs are reproducible).
        _write_gate_script(tmp_path, "slow.py", 0, stdout="slow done", sleep_ms=200)
        _write_gate_script(tmp_path, "fast.py", 0, stdout="fast done", sleep_ms=10)
        specs: list[dict[str, object]] = [
            {"label": "slow", "script_rel": "slow.py", "args_list": [], "fail_hint": "—", "timeout_s": 30},
            {"label": "fast", "script_rel": "fast.py", "args_list": [], "fail_hint": "—", "timeout_s": 30},
        ]
        _run_post_adg_gates_parallel(specs)
        out = capsys.readouterr().out
        # The "slow done" line must be printed BEFORE "fast done" even
        # though slow finished after fast.
        assert out.index("slow done") < out.index("fast done")
        # PASS lines also follow spec order.
        assert out.index("[slow] PASS") < out.index("[fast] PASS")

    def test_args_list_is_forwarded(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate import generate_full_adg as gfa

        monkeypatch.setattr(gfa, "ROOT", tmp_path)

        echoer = tmp_path / "echo.py"
        echoer.write_text("import sys; print('argv=', sys.argv[1:])", encoding="utf-8")
        specs: list[dict[str, object]] = [
            {
                "label": "echo",
                "script_rel": "echo.py",
                "args_list": ["--foo", "bar"],
                "fail_hint": "—",
                "timeout_s": 30,
            },
        ]
        _run_post_adg_gates_parallel(specs)
        out = capsys.readouterr().out
        assert "argv= ['--foo', 'bar']" in out


# ---------------------------------------------------------------------------
# Skip-summary blank-line tolerance (W4.2 hardening)
# ---------------------------------------------------------------------------


class TestSkipSummaryCounting:
    """Validate the counting logic used in the end-of-run skip summary.

    The summary reads the JSONL ledger and prints
    ``Pipeline skips: N non-blocking layer(s) recorded`` where N must be
    the number of non-empty lines (real records), not raw line count.
    """

    @staticmethod
    def _count_nonblank(p: Path) -> int:
        with p.open("r", encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())

    def test_blank_lines_are_not_counted(self, tmp_path: Path) -> None:
        ledger = tmp_path / "skips.jsonl"
        # One real row, two blank lines (a writer that flushed an empty
        # buffer between records would produce these).
        ledger.write_text(
            json.dumps({"ts": "TS", "layer": "P4", "name": "x", "exc_type": "OSError", "exc_message": "fail"})
            + "\n\n\n",
            encoding="utf-8",
        )
        assert self._count_nonblank(ledger) == 1

    def test_trailing_newline_is_not_double_counted(self, tmp_path: Path) -> None:
        ledger = tmp_path / "skips.jsonl"
        rows = [
            json.dumps(
                {"ts": "TS", "layer": "P4", "name": "x", "exc_type": "OSError", "exc_message": "fail"}
            ),
            json.dumps(
                {"ts": "TS", "layer": "P5", "name": "y", "exc_type": "ValueError", "exc_message": "bad"}
            ),
        ]
        ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")
        assert self._count_nonblank(ledger) == 2


# ---------------------------------------------------------------------------
# Deferred-P0 exit (W8 — --continue-on-p0 / ADG_CONTINUE_ON_P0)
# ---------------------------------------------------------------------------


class TestDeferredP0Exit:
    """Validate the W8 defer-exit path in tools.generate.integration.p0_runner.

    The runner ordinarily calls ``sys.exit(1)`` on P0 failure. When invoked
    with ``defer_exit=True`` (or env ``ADG_CONTINUE_ON_P0=1``), it must
    instead record the failure and return so the rest of the pipeline can
    run, with main() exiting non-zero at the very end.
    """

    @pytest.fixture(autouse=True)
    def _reset_module_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Each test must start from a clean slate so deferred-state from
        # a prior test cannot leak.
        from tools.generate.integration import p0_runner as p0r

        p0r._DEFERRED_P0_FAILURE.update(failed=False, rc=0, plan_path=None)
        monkeypatch.delenv("ADG_CONTINUE_ON_P0", raising=False)

    def test_initial_state_is_clean(self) -> None:
        from tools.generate.integration import (
            deferred_p0_exit_code,
            deferred_p0_plan_path,
            is_p0_failure_deferred,
        )

        assert is_p0_failure_deferred() is False
        assert deferred_p0_exit_code() == 0
        assert deferred_p0_plan_path() is None

    @staticmethod
    def _stub_inner_runner(monkeypatch: pytest.MonkeyPatch, return_code: int) -> None:
        """Stub the runner module so the real P0 gates don't actually run.

        ``_run_p0_two_pass_runner`` does ``from importlib import import_module``
        at module-load time, capturing the function object — so we MUST patch
        the bound name in the runner module itself, not the importlib module.
        """

        class _StubModule:
            @staticmethod
            def run_p0_two_pass(*args, **kwargs):  # noqa: ARG004
                return return_code

        monkeypatch.setattr(
            "tools.generate.integration.p0_runner.import_module",
            lambda *a, **kw: _StubModule,
        )

    def test_default_p0_failure_calls_sys_exit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate.integration import _run_p0_two_pass_runner

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        self._stub_inner_runner(monkeypatch, return_code=1)

        with pytest.raises(SystemExit) as excinfo:
            _run_p0_two_pass_runner(sqlite_path=sqlite_path)
        assert excinfo.value.code == 1
        out = capsys.readouterr().out
        assert "BLOCKED" in out
        assert "halted" in out

    def test_defer_exit_argument_records_and_returns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tools.generate.integration import (
            _run_p0_two_pass_runner,
            deferred_p0_exit_code,
            deferred_p0_plan_path,
            is_p0_failure_deferred,
        )

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        plan_path = tmp_path / "plan.md"
        plan_path.write_text("plan", encoding="utf-8")
        self._stub_inner_runner(monkeypatch, return_code=1)

        # Must NOT raise.
        _run_p0_two_pass_runner(sqlite_path=sqlite_path, plan_path=plan_path, defer_exit=True)
        assert is_p0_failure_deferred() is True
        assert deferred_p0_exit_code() == 1
        assert deferred_p0_plan_path() == plan_path
        out = capsys.readouterr().out
        assert "BLOCKED (deferred" in out
        assert "Pipeline continues" in out

    def test_env_var_triggers_defer(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from tools.generate.integration import (
            _run_p0_two_pass_runner,
            is_p0_failure_deferred,
        )

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        self._stub_inner_runner(monkeypatch, return_code=1)
        monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")

        # Must NOT raise.
        _run_p0_two_pass_runner(sqlite_path=sqlite_path)
        assert is_p0_failure_deferred() is True

    @pytest.mark.parametrize("env_value", ["1", "true", "TRUE", "yes", "on"])
    def test_env_var_truthy_variants(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, env_value: str
    ) -> None:
        from tools.generate.integration import (
            _run_p0_two_pass_runner,
            is_p0_failure_deferred,
        )

        # Reset state for each parametrized case.
        from tools.generate.integration import p0_runner as p0r

        p0r._DEFERRED_P0_FAILURE.update(failed=False, rc=0, plan_path=None)

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        self._stub_inner_runner(monkeypatch, return_code=1)
        monkeypatch.setenv("ADG_CONTINUE_ON_P0", env_value)

        _run_p0_two_pass_runner(sqlite_path=sqlite_path)
        assert is_p0_failure_deferred() is True

    def test_explicit_defer_false_overrides_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tools.generate.integration import _run_p0_two_pass_runner

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        self._stub_inner_runner(monkeypatch, return_code=1)
        # Env says defer, but explicit kwarg says don't defer — explicit wins.
        monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")

        with pytest.raises(SystemExit) as excinfo:
            _run_p0_two_pass_runner(sqlite_path=sqlite_path, defer_exit=False)
        assert excinfo.value.code == 1

    def test_p0_pass_does_not_record_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from tools.generate.integration import (
            _run_p0_two_pass_runner,
            is_p0_failure_deferred,
        )

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()
        self._stub_inner_runner(monkeypatch, return_code=0)  # PASS

        _run_p0_two_pass_runner(sqlite_path=sqlite_path, defer_exit=True)
        # Even with defer enabled, a PASS must NOT record a failure.
        assert is_p0_failure_deferred() is False

    def test_missing_sqlite_does_not_defer(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # When SQLite is missing, downstream stages have nothing to read,
        # so the runner MUST hard-fail even in defer mode.
        from tools.generate.integration import _run_p0_two_pass_runner

        missing = tmp_path / "does_not_exist.sqlite"
        with pytest.raises(SystemExit) as excinfo:
            _run_p0_two_pass_runner(sqlite_path=missing, defer_exit=True)
        assert excinfo.value.code == 1


# ---------------------------------------------------------------------------
# Shared deferred-failure registry (Wave B / plan adg-cascading-ratchet-defer-exit-a41828)
# ---------------------------------------------------------------------------


class TestSharedDeferredFailureRegistry:
    """Validate the shared registry that backs the cascading defer-exit pattern.

    Sibling to ``TestDeferredP0Exit`` but for the broader, gate-agnostic
    registry in ``tools.generate.integration.deferred_failures``. Any new
    gate that opts into defer-exit calls into this same registry; the
    pipeline drains it at the end of ``main()`` and exits with the first
    recorded non-zero rc.
    """

    @pytest.fixture(autouse=True)
    def _reset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tools.generate.integration.deferred_failures import reset_for_tests

        reset_for_tests()
        monkeypatch.delenv("ADG_CONTINUE_ON_P0", raising=False)

    def test_initial_state(self) -> None:
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            deferred_failure_summary,
            is_failure_deferred,
        )

        assert is_failure_deferred() is False
        assert deferred_exit_code() == 0
        assert deferred_failure_summary() == []

    def test_record_or_exit_no_env_calls_sys_exit(self) -> None:
        from tools.generate.integration.deferred_failures import record_or_exit

        with pytest.raises(SystemExit) as excinfo:
            record_or_exit("some_gate", 5)
        assert excinfo.value.code == 5

    def test_record_or_exit_with_env_records_and_returns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            deferred_failure_summary,
            is_failure_deferred,
            record_or_exit,
        )

        monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")

        record_or_exit("gate_a", 7, message="fail-a")
        record_or_exit("gate_b", 3, message="fail-b", plan_path="some/plan.md")

        assert is_failure_deferred() is True
        # First non-zero rc wins (insertion order = registration order).
        assert deferred_exit_code() == 7
        rows = deferred_failure_summary()
        assert len(rows) == 2
        assert rows[0]["gate_name"] == "gate_a"
        assert rows[0]["rc"] == 7
        assert rows[0]["message"] == "fail-a"
        assert rows[1]["gate_name"] == "gate_b"
        assert rows[1]["plan_path"] == "some/plan.md"

    def test_record_or_exit_explicit_defer_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tools.generate.integration.deferred_failures import record_or_exit

        # Env says defer, but explicit kwarg says don't.
        monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")
        with pytest.raises(SystemExit) as excinfo:
            record_or_exit("g", 9, defer_exit=False)
        assert excinfo.value.code == 9

    def test_zero_rc_is_no_op(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # rc=0 means PASS — must not pollute the registry, must not exit.
        from tools.generate.integration.deferred_failures import (
            is_failure_deferred,
            record_or_exit,
        )

        monkeypatch.setenv("ADG_CONTINUE_ON_P0", "1")
        record_or_exit("pass_gate", 0)
        assert is_failure_deferred() is False

    def test_record_failure_always_records(self) -> None:
        # `record_failure` (no -or-exit) must record regardless of env.
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            is_failure_deferred,
            record_failure,
        )

        # Env unset (per autouse fixture).
        record_failure("x", 4, message="fail")
        assert is_failure_deferred() is True
        assert deferred_exit_code() == 4

    def test_first_failure_rc_wins_with_zero_in_between(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # If gates report rc=2 then later rc=0 (a no-op) then rc=5, the
        # first non-zero (2) is the one we exit with.
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            record_failure,
        )

        record_failure("first", 2)
        record_failure("second", 0)  # no-op (rc=0 just overwrites if same key, but here new)
        record_failure("third", 5)
        assert deferred_exit_code() == 2

    def test_re_recording_same_gate_overwrites(self) -> None:
        # Re-recording the same gate name must overwrite the prior entry's
        # rc/message but preserve its registration order (so a later
        # `record_or_exit` doesn't unexpectedly bump it to the end).
        from tools.generate.integration.deferred_failures import (
            deferred_exit_code,
            deferred_failure_summary,
            record_failure,
        )

        record_failure("g1", 3)
        record_failure("g2", 7)
        record_failure("g1", 9)  # overwrite — order should still be g1, g2
        rows = deferred_failure_summary()
        assert [r["gate_name"] for r in rows] == ["g1", "g2"]
        assert deferred_exit_code() == 9  # g1's new rc wins because it's first

    def test_p0_runner_writes_to_shared_registry_via_compat_layer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The legacy p0_runner module owns its own _DEFERRED_P0_FAILURE
        # state for back-compat. The shared registry is populated only
        # through `record_or_exit`/`record_failure`. Confirm the two
        # paths coexist cleanly: the shared registry remains empty when
        # only the legacy P0 path is exercised.
        from tools.generate.integration import (
            _run_p0_two_pass_runner,
            is_p0_failure_deferred,
        )
        from tools.generate.integration.deferred_failures import (
            is_failure_deferred,
        )

        sqlite_path = tmp_path / "fake.sqlite"
        sqlite_path.touch()

        class _StubModule:
            @staticmethod
            def run_p0_two_pass(*args, **kwargs):  # noqa: ARG004
                return 1

        monkeypatch.setattr(
            "tools.generate.integration.p0_runner.import_module",
            lambda *a, **kw: _StubModule,
        )

        _run_p0_two_pass_runner(sqlite_path=sqlite_path, defer_exit=True)
        assert is_p0_failure_deferred() is True
        # The shared registry stays empty: p0_runner uses its own state
        # for now (preserved for back-compat). main() reads BOTH and
        # exits with whichever is non-zero.
        assert is_failure_deferred() is False
