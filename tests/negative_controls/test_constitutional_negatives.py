"""Constitutional negative-control suite.

Each case feeds a gate a known-bad input and asserts the gate fails closed.
This is the assurance dimension #5 (fail-closed verification) — proves
gates are not vacuous.

Covers W2.2 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from tests.negative_controls.conftest import run_gate


@dataclass(frozen=True)
class NegativeCase:
    """One negative control: feed gate this bad input, expect non-zero exit."""

    case_id: str
    gate: str
    stdin_payload: dict | str | None = None
    args: list[str] | None = None
    expect_substring_in_stderr: str = ""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return self.case_id


# -------------------------------------------------------------------------
# pre_run_gate.py negatives — constitutional §0 (no PowerShell), §26 (no
# interactive pagers), python-dash-c-quote-hazard rule.
# -------------------------------------------------------------------------

PRE_RUN_GATE = ".claude/governance/scripts/_legacy_windsurf/pre_run_gate.py"

PRE_RUN_NEGATIVES: list[NegativeCase] = [
    NegativeCase(
        case_id="powershell_explicit",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "powershell -Command Get-Process"},
    ),
    NegativeCase(
        case_id="pwsh_explicit",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "pwsh -c 'echo hi'"},
    ),
    NegativeCase(
        case_id="powershell_exe_with_path",
        gate=PRE_RUN_GATE,
        stdin_payload={
            "command_line": ("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile")
        },
    ),
    NegativeCase(
        case_id="python_dash_c_escaped_triple_quote",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": ('python -c "import re; pat=r\\"\\"\\"x\\"\\"\\"; print(pat)"')},
    ),
    NegativeCase(
        case_id="python_dash_c_escaped_dquote",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": 'python -c "print(\\"hi\\")"'},
    ),
    NegativeCase(
        case_id="pipe_to_more",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "type big_file.txt | more"},
    ),
    NegativeCase(
        case_id="pipe_to_less",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "cat /etc/hosts | less"},
    ),
    NegativeCase(
        case_id="bare_more_with_file",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "more big_file.txt"},
    ),
    NegativeCase(
        case_id="bare_less_with_file",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "less big_file.txt"},
    ),
    NegativeCase(
        case_id="malformed_json_payload",
        gate=PRE_RUN_GATE,
        stdin_payload="{this is not valid json",
    ),
    NegativeCase(
        case_id="vim_editor",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "vim file.txt"},
    ),
    NegativeCase(
        case_id="top_watcher",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "top"},
    ),
    NegativeCase(
        case_id="tail_follow",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "tail -f /var/log/system.log"},
    ),
    NegativeCase(
        case_id="bare_python_repl",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "python"},
    ),
    NegativeCase(
        case_id="python_interactive_flag",
        gate=PRE_RUN_GATE,
        stdin_payload={"command_line": "python -i script.py"},
    ),
]


# -------------------------------------------------------------------------
# Runtime trace contract gate negatives (W1.3 — proves the gate fails when
# its inputs are wrong, completing the W2 fail-closed coverage for the new
# W1 gate).
# -------------------------------------------------------------------------

RUNTIME_TRACE_NEGATIVES: list[NegativeCase] = [
    NegativeCase(
        case_id="runtime_trace_unknown_contract",
        gate="ops_scripts/ci/check_runtime_trace_contract.py",
        args=["--contract", "no.such.contract.v999"],
    ),
    NegativeCase(
        case_id="runtime_trace_empty_contract_id",
        gate="ops_scripts/ci/check_runtime_trace_contract.py",
        args=["--contract", ""],
    ),
]


# -------------------------------------------------------------------------
# Constitutional CI check negatives (Author-Gate decision capture, plan-file
# discipline, MCP serialization).
# -------------------------------------------------------------------------

# These gates run against the live repo; we pick ones whose fail-closed
# behavior is exercisable via CLI args (no fixture file needed).

LIVE_REPO_NEGATIVES: list[NegativeCase] = [
    # check_runtime_trace_contract with a contract path that does not exist
    # exercises the script-missing infrastructure-error path.
    NegativeCase(
        case_id="runtime_trace_unknown_via_main",
        gate="ops_scripts/ci/check_runtime_trace_contract.py",
        args=["--contract", "another.fake.canary.v1"],
    ),
]


# -------------------------------------------------------------------------
# Combined suite — pytest parametrization.
# -------------------------------------------------------------------------

ALL_NEGATIVES: list[NegativeCase] = PRE_RUN_NEGATIVES + RUNTIME_TRACE_NEGATIVES + LIVE_REPO_NEGATIVES


@pytest.mark.parametrize("case", ALL_NEGATIVES, ids=lambda c: c.case_id)
def test_gate_blocks_bad_input(case: NegativeCase) -> None:
    """Each negative-control case must produce a non-zero exit code."""
    result = run_gate(
        case.gate,
        args=case.args,
        stdin_payload=case.stdin_payload,
    )
    assert result.blocked, (
        f"gate {case.gate} did NOT fail-close on case {case.case_id!r}; "
        f"exit={result.returncode}, stdout={result.stdout[:200]!r}, "
        f"stderr={result.stderr[:200]!r}"
    )
    if case.expect_substring_in_stderr:
        assert case.expect_substring_in_stderr in result.stderr, (
            f"case {case.case_id}: stderr did not contain "
            f"{case.expect_substring_in_stderr!r}; got {result.stderr[:300]!r}"
        )


def test_negative_control_count_meets_minimum() -> None:
    """Constitutional W2 success criterion: ≥15 negative-control tests."""
    assert len(ALL_NEGATIVES) >= 15, (
        f"only {len(ALL_NEGATIVES)} negative controls registered; "
        f"plan assurance-p1-gates-ab4758 W2 requires ≥15"
    )
