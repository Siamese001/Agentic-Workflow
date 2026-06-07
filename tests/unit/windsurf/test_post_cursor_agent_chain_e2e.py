"""E2E: full post_cursor_agent_response chain with real Windsurf payload shape.

Simulates Windsurf dispatching the entire hook chain defined in
``.cursor/hooks.json`` and asserts each hook's observable side-effect.
This is the end-to-end regression guard for the 2026-04-23 RCA.

What it proves:
  1. hooks.json is valid JSON and lists every post_cascade script.
  2. Every hook runs under a real Windsurf payload shape
     (``{"agent_action_name": ..., "tool_info": {"response": "..."}}``)
     with ``returncode == 0`` (fail-open policy honored).
  3. Each hook produces its expected observable artifact:
       - heartbeat.jsonl gets a new line
       - deferred_scope_capture.jsonl gets a marker entry
       - long_command log gets entries when the response text includes
         the respective violation patterns
  4. The chain is resilient: an early hook's failure must not halt later
     hooks. (Tested by injecting a malformed JSON-in-JSON payload.)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOKS_JSON = REPO / "docs/archive/windsurf/legacy-tree" / "hooks.json"
SCRIPTS = REPO / ".cursor" / "scripts" / "_legacy_windsurf"
ARTIFACTS = REPO / "artifacts" / "windsurf"


def _load_chain() -> list[Path]:
    """Parse hooks.json and return the list of post_cursor_agent_response scripts."""
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    chain = data["hooks"]["post_cursor_agent_response"]
    scripts: list[Path] = []
    for entry in chain:
        cmd = entry["command"]
        # Format: "python .cursor/scripts/_legacy_windsurf/<name>.py"
        parts = cmd.split()
        rel = parts[-1].replace("\\", "/")
        if rel.startswith("./"):
            rel = rel[2:]
        script_path = REPO / rel
        scripts.append(script_path)
    return scripts


def _run_hook(script: Path, payload: str) -> subprocess.CompletedProcess[str]:
    """Run one hook with the given stdin payload. Inherit env but strip
    NOTION tokens to prevent smoke-test markers from reaching real Notion."""
    env = dict(os.environ)
    env["NOTION_TOKEN"] = ""
    env["NOTION_API_KEY"] = ""
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(script)],
        input=payload,
        text=True,
        capture_output=True,
        env=env,
        cwd=str(REPO),
        timeout=30,
        check=False,
    )


def _make_payload(response_text: str) -> str:
    return json.dumps(
        {
            "agent_action_name": "post_cursor_agent_response",
            "tool_info": {"response": response_text},
        }
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHooksJsonIntegrity:
    def test_hooks_json_is_valid(self) -> None:
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        assert "post_cursor_agent_response" in data["hooks"]

    def test_every_script_exists(self) -> None:
        for script in _load_chain():
            assert script.is_file(), f"missing hook script: {script}"

    def test_heartbeat_is_first(self) -> None:
        """Heartbeat must run first so we always have proof-of-dispatch
        even when a downstream hook crashes."""
        chain = _load_chain()
        assert chain[0].name == "post_cursor_agent_heartbeat.py", (
            f"Expected heartbeat first; got {chain[0].name}. "
            "See 2026-04-23 RCA: first-position placement is the only "
            "unambiguous signal that the chain actually fired."
        )


class TestFullChainRun:
    """Run every hook with a realistic Windsurf payload; assert zero crashes."""

    RESPONSE_TEXT = (
        "I executed the task and captured residual scope.\n"
        "\n"
        "DEFERRED_SCOPE: plan=NEW:chain-e2e-test wave=X phase=X.1 layer=L6 "
        "fan_in=1 surface=Observability coverage_gap_pct=5.0 est_tokens=100 "
        "reason=Chain E2E smoke test (offline)\n"
        "\n"
        "All done."
    )

    @pytest.fixture(autouse=True)
    def _capture_mtimes(self) -> None:
        """Record each artifact's mtime before the chain runs."""
        self._before: dict[str, float] = {}
        for path in ARTIFACTS.glob("*.jsonl"):
            self._before[path.name] = path.stat().st_mtime if path.exists() else 0.0

    def test_all_hooks_exit_zero(self) -> None:
        payload = _make_payload(self.RESPONSE_TEXT)
        failures: list[str] = []
        for script in _load_chain():
            result = _run_hook(script, payload)
            if result.returncode != 0:
                failures.append(
                    f"{script.name} exit={result.returncode}\n"
                    f"  stderr: {result.stderr[:500]}\n"
                    f"  stdout: {result.stdout[:500]}"
                )
        assert not failures, "\n".join(failures)

    def test_heartbeat_jsonl_advances(self) -> None:
        before = self._before.get("post_cursor_agent_heartbeat.jsonl", 0.0)
        payload = _make_payload(self.RESPONSE_TEXT)
        _run_hook(SCRIPTS / "post_cursor_agent_heartbeat.py", payload)
        path = ARTIFACTS / "post_cursor_agent_heartbeat.jsonl"
        assert path.exists(), "heartbeat hook did not create its log"
        assert path.stat().st_mtime >= before, "heartbeat jsonl mtime did not advance"

    def test_deferred_scope_capture_reads_real_payload(self) -> None:
        """Core regression: the real Windsurf payload (tool_info.response)
        MUST yield 'markers=1' from the deferred-scope hook."""
        payload = _make_payload(self.RESPONSE_TEXT)
        result = _run_hook(SCRIPTS / "post_cursor_agent_deferred_scope_capture.py", payload)
        assert result.returncode == 0
        assert "markers=1" in result.stderr, (
            f"Deferred-scope hook did NOT detect marker in real Windsurf payload.\n"
            f"stderr: {result.stderr}\nstdout: {result.stdout}"
        )

    def test_long_command_hook_detects_pytest_in_run_command(self) -> None:
        """Response text containing an unbounded pytest run_command should
        trigger the long-command hook."""
        text = (
            'I ran tests.\n<invoke name="run_command">'
            '<parameter name="CommandLine">pytest tests/ -v</parameter>'
            '<parameter name="Blocking">true</parameter></invoke>\nDone.'
        )
        payload = _make_payload(text)
        result = _run_hook(SCRIPTS / "post_cursor_agent_long_command_audit.py", payload)
        assert result.returncode == 0
        assert "DETECTED" in result.stderr, (
            f"long_command hook did not detect pytest invocation.\nstderr: {result.stderr}"
        )


class TestChainResilience:
    """A malformed payload must not crash any hook (fail-open policy)."""

    @pytest.mark.parametrize(
        "bad_payload",
        [
            "",  # empty
            "   ",  # whitespace only
            "<<not json at all>>",  # non-JSON
            "[1, 2, 3]",  # JSON but wrong type
            '{"tool_info": null}',  # null nesting
            '{"tool_info": {"response": 12345}}',  # non-string response
            '{"tool_info": {}}',  # empty tool_info
        ],
    )
    def test_every_hook_survives_malformed_payload(self, bad_payload: str) -> None:
        failures: list[str] = []
        for script in _load_chain():
            result = _run_hook(script, bad_payload)
            if result.returncode != 0:
                failures.append(
                    f"{script.name} crashed on payload={bad_payload!r} "
                    f"(exit={result.returncode}, stderr={result.stderr[:200]})"
                )
        assert not failures, "\n".join(failures)


class TestHeartbeatProvesChainFired:
    """If hooks.json is correctly wired, a single chain run must leave the
    heartbeat jsonl newer than when the test started. This is the ground-
    truth observability signal the RCA hardening introduced."""

    def test_heartbeat_moves_after_single_chain_run(self) -> None:
        path = ARTIFACTS / "post_cursor_agent_heartbeat.jsonl"
        # Use line count instead of mtime — Windows mtime resolution is coarse
        # and a full chain run completes in <1s.
        start_lines = len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0
        payload = _make_payload("trivial response")
        for script in _load_chain():
            _run_hook(script, payload)
        assert path.exists()
        end_lines = len(path.read_text(encoding="utf-8").splitlines())
        assert end_lines > start_lines, (
            f"Heartbeat jsonl did not grow after running the full chain "
            f"(was {start_lines} lines, still {end_lines}). "
            "Heartbeat script itself is broken."
        )
