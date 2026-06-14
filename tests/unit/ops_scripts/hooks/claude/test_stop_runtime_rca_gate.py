"""Tests for the runtime-RCA Stop gate (plan rca-depth-enforcement-83e392 W2).

The gate is a live Stop hook under .claude/hooks/. It imports lib.claude_hook_common
(so .claude/hooks must be on sys.path) and reuses detect() from the advisory audit.
``block()`` prints {"decision":"block",...} to stdout and main() returns exit code 2;
``allow()``/``warn()`` return 0.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
GATE = HOOKS_DIR / "stop_runtime_rca_gate.py"

# A refactor turn with NO Outcome frame (no "Verdict source:") -> missing_refactor_outcome.
_FRAMELESS_REFACTOR = (
    "STATUS: FAIL\nFILES_CHANGED:\n- [foo.py](foo.py)\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n"
)
# Same refactor turn WITH the Outcome frame -> no missing_refactor_outcome.
_FRAMED_REFACTOR = (
    "**Outcome**\nDid it run? Yes.\nVerdict source: pytest -> exit 0, 5 passed\n"
    "STATUS: PASS\nFILES_CHANGED:\n- [foo.py](foo.py)\n"
)
# Not a refactor turn (no code file changed) -> the gate's block kind never fires.
_NON_REFACTOR = "STATUS: PASS\nCOMMANDS_RUN:\n- pytest -> 5 passed\n"


@pytest.fixture()
def gate_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # .claude/hooks must be importable for `from lib.claude_hook_common import ...`.
    monkeypatch.syspath_prepend(str(HOOKS_DIR))
    name = "_stop_runtime_rca_gate_test"
    spec = importlib.util.spec_from_file_location(name, GATE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "_STATE_FILE", tmp_path / "runtime_rca_gate_state.json")
    monkeypatch.delenv("RUNTIME_RCA_AUDIT_BYPASS", raising=False)
    monkeypatch.delenv("RUNTIME_RCA_ENFORCE", raising=False)
    monkeypatch.delenv("RUNTIME_RCA_GATE_MAX_BLOCKS", raising=False)
    return mod


def _run(mod, response_text: str, monkeypatch: pytest.MonkeyPatch, session: str = "s1") -> int:
    payload = json.dumps({"session_id": session, "tool_info": {"response": response_text}})
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


class TestRuntimeRcaGate:
    def test_warn_default_never_blocks(self, gate_mod, monkeypatch, capsys) -> None:
        # Default mode is warn (shadow): a frameless refactor turn is logged, not blocked.
        rc = _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch)
        assert rc == 0
        assert "decision" not in capsys.readouterr().out  # no block JSON on stdout

    def test_off_allows(self, gate_mod, monkeypatch, capsys) -> None:
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "off")
        assert _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch) == 0
        assert capsys.readouterr().out.strip() == ""

    def test_block_mode_blocks_frameless_refactor(self, gate_mod, monkeypatch, capsys) -> None:
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        rc = _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch)
        assert rc == 2
        out = capsys.readouterr().out
        decision = json.loads(out.strip().splitlines()[-1])
        assert decision["decision"] == "block"
        assert "Outcome frame" in decision["reason"]

    def test_block_mode_allows_framed_refactor(self, gate_mod, monkeypatch, capsys) -> None:
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        assert _run(gate_mod, _FRAMED_REFACTOR, monkeypatch) == 0
        assert "decision" not in capsys.readouterr().out

    def test_block_mode_allows_non_refactor(self, gate_mod, monkeypatch, capsys) -> None:
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        assert _run(gate_mod, _NON_REFACTOR, monkeypatch) == 0
        assert "decision" not in capsys.readouterr().out

    def test_bypass_allows(self, gate_mod, monkeypatch, capsys) -> None:
        # Bypass wins even in block mode over a frameless refactor turn that would block.
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        monkeypatch.setenv("RUNTIME_RCA_AUDIT_BYPASS", "1")
        assert _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch) == 0
        assert "decision" not in capsys.readouterr().out

    def test_loop_guard_stops_after_max(self, gate_mod, monkeypatch, capsys) -> None:
        # Default MAX_BLOCKS=1: first frameless turn blocks, the second (same session)
        # allows with block_limit_reached so the turn is never trapped.
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        rc1 = _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch, session="loop")
        capsys.readouterr()
        rc2 = _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch, session="loop")
        assert rc1 == 2
        assert rc2 == 0  # block_limit_reached
        assert "decision" not in capsys.readouterr().out

    def test_compliant_turn_resets_counter(self, gate_mod, monkeypatch, capsys) -> None:
        # A block increments the session counter; a later compliant turn clears it so a
        # subsequent violation blocks again (the guard is consecutive, not lifetime).
        monkeypatch.setenv("RUNTIME_RCA_ENFORCE", "block")
        assert _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch, session="reset") == 2
        capsys.readouterr()
        assert _run(gate_mod, _FRAMED_REFACTOR, monkeypatch, session="reset") == 0  # resets
        capsys.readouterr()
        assert _run(gate_mod, _FRAMELESS_REFACTOR, monkeypatch, session="reset") == 2  # blocks again


class TestStopChainRegistration:
    def test_gate_registered_in_settings_stop(self) -> None:
        settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [
            h["command"]
            for group in settings["hooks"]["Stop"]
            for h in group["hooks"]
        ]
        assert any("stop_runtime_rca_gate.py" in c for c in cmds), cmds
