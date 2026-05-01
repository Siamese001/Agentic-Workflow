"""W2 — Terminal cache reuse never executes L2 / L4."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"

import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (LATEST / "integrated_runtime_artifact_manifest.json").exists(),
    reason=(
        "W2b honest non-green: latest/ empty without approved live provider. "
        "Run probe_integrated_runtime_safe_reuse.py with local_qwen reachable "
        "or ANTHROPIC_API_KEY set."
    ),
)


class TestTerminalNoL2NoL4:
    def test_terminal_packet_no_l2_assertion(self):
        env = json.loads((LATEST / "terminal_ret_packet.json").read_text(encoding="utf-8"))
        assert env["payload"]["no_l2_execution_assertion"] is True

    def test_terminal_packet_no_l4_write_assertion(self):
        env = json.loads((LATEST / "terminal_ret_packet.json").read_text(encoding="utf-8"))
        assert env["payload"]["no_l4_write_assertion"] is True

    def test_exit_review_exec_trace_has_no_tool_or_model_calls(self):
        env = json.loads((LATEST / "exit_review_packet.json").read_text(encoding="utf-8"))
        exec_trace = env["payload"].get("exec_trace", {})
        assert exec_trace.get("tool_calls") in (None, [], ())
        assert exec_trace.get("model_calls") in (None, [], ())

    def test_exit_review_state_diff_empty(self):
        """No L4 mutation without UWG receipt — state_diff must be empty."""
        env = json.loads((LATEST / "exit_review_packet.json").read_text(encoding="utf-8"))
        sd = env["payload"].get("state_diff", {})
        assert sd in ({}, None)
