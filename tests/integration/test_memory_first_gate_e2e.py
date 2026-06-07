"""
End-to-end integration test for the memory-first enforcement gate.

Drives the REAL pre_mcp_gate.py and post_mcp_audit.py processes via subprocess
(no mocks) to verify the full operational sequence across two fresh sessions:

  Step 1: First non-memory MCP call → BLOCKED (exit 2)
  Step 2: memory.mem_recall_session_start → ALLOWED (exit 0)
  Step 3: post_mcp_audit.py runs → session_state.memory_recalled flips True
  Step 4: Subsequent non-memory calls → ALLOWED (exit 0)
  Step 5: Reset and repeat for second session

Isolation boundary (matches pre_mcp_gate.py SESSION_STATE comment):
  These tests validate per-window isolation (one VSCODE_PID / one pytest
  runner process).  They do NOT validate per-chat / per-tab isolation,
  which would require a conversation-scoped ID from Windsurf.

Run with:
    python -m pytest tests/integration/test_memory_first_gate_e2e.py -v -s -n 0
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Integration tests share the real session_state.json — must run sequentially.
# Run with: python -m pytest tests/integration/test_memory_first_gate_e2e.py -n 0
pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]
# os.getpid() here == os.getppid() as seen by any subprocess this test spawns.
SESSION_STATE = REPO_ROOT / "artifacts" / "governance" / f"session_state_{os.getpid()}.json"
PRE_MCP_GATE = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "pre_mcp_gate.py"
POST_MCP_AUDIT = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_mcp_audit.py"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_session_state():
    """Save and restore session_state.json around each test.

    Ensures the real artifact is left in its original state regardless of
    whether the test passes, fails, or is interrupted.
    """
    original = SESSION_STATE.read_text(encoding="utf-8") if SESSION_STATE.exists() else None
    yield
    if original is not None:
        SESSION_STATE.write_text(original, encoding="utf-8")
    elif SESSION_STATE.exists():
        SESSION_STATE.unlink()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _invoke_gate(server: str, tool: str) -> tuple[int, str]:
    """Run pre_mcp_gate.py with the given server/tool; return (exit_code, stderr)."""
    payload = json.dumps({"tool_info": {"mcp_server_name": server, "mcp_tool_name": tool}})
    result = subprocess.run(
        [sys.executable, str(PRE_MCP_GATE)],
        input=payload,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stderr.strip()


def _invoke_post_audit(server: str, tool: str) -> None:
    """Run post_mcp_audit.py simulating a completed tool call."""
    payload = json.dumps(
        {
            "tool_info": {
                "mcp_server_name": server,
                "mcp_tool_name": tool,
                "duration_ms": 50,
            }
        }
    )
    subprocess.run(
        [sys.executable, str(POST_MCP_AUDIT)],
        input=payload,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
        timeout=30,
        cwd=str(REPO_ROOT),
    )


def _reset_session() -> None:
    """Write a fresh session_state.json with memory_recalled=False."""
    SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_STATE.write_text(
        json.dumps(
            {
                "current_tier": "T2",
                "memory_recalled": False,
                "max_memory_block_attempts": 0,
                "task_created": False,
                "task_started": False,
                "task_decomposed": False,
                "update_task_count": 0,
                "lessons_captured": False,
            }
        ),
        encoding="utf-8",
    )


def _read_state() -> dict:
    return dict(json.loads(SESSION_STATE.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Shared sequence runner
# ---------------------------------------------------------------------------


def _run_session(session_num: int) -> None:
    """Execute and assert the full enforcement sequence for one session."""
    sep = "=" * 64
    print(f"\n{sep}")
    print(f"  SESSION {session_num}: Fresh start")
    print(sep)  # noqa: T201

    _reset_session()
    state = _read_state()
    print(
        "\n[RESET] memory_recalled="
        + str(state["memory_recalled"])
        + "  max_memory_block_attempts="
        + str(state["max_memory_block_attempts"])
    )

    # ── Step 1: First non-memory call must be BLOCKED ────────────────────────
    rc, stderr = _invoke_gate("task_manager", "create_task")
    print("\n[Step 1] task_manager.create_task")
    print("  exit=" + str(rc) + "  (expected 2 — BLOCKED)")
    print("  stderr: " + stderr)
    assert rc == 2, "Session " + str(session_num) + " Step 1: expected exit 2, got " + str(rc)
    attempt = _read_state().get("max_memory_block_attempts", 0)
    print("  max_memory_block_attempts now: " + str(attempt))
    assert attempt == 1, "Session " + str(session_num) + " Step 1: expected attempt=1, got " + str(attempt)

    # ── Step 2: memory server must ALWAYS pass ───────────────────────────────
    rc, stderr = _invoke_gate("memory", "mem_recall_session_start")
    print("\n[Step 2] memory.mem_recall_session_start")
    print("  exit=" + str(rc) + "  (expected 0 — ALLOWED)")
    assert rc == 0, "Session " + str(session_num) + " Step 2: expected exit 0, got " + str(rc)

    # ── Step 3: post_mcp_audit flips memory_recalled=True ───────────────────
    _invoke_post_audit("memory", "mem_recall_session_start")
    state = _read_state()
    print("\n[Step 3] post_mcp_audit ran")
    print("  memory_recalled=" + str(state["memory_recalled"]) + "  (expected True)")
    assert state["memory_recalled"] is True, (
        "Session " + str(session_num) + " Step 3: expected memory_recalled=True"
    )

    # ── Step 4: Subsequent non-memory calls must be ALLOWED ──────────────────
    for server, tool in [
        ("task_manager", "create_task"),
        ("adg_sqlite", "adg_health"),
        ("GitKraken", "git_status"),
    ]:
        rc, stderr = _invoke_gate(server, tool)
        print(f"\n[Step 4] {server}.{tool}")
        print(f"  exit={rc}  (expected 0 — ALLOWED)")
        assert rc == 0, f"Session {session_num} Step 4: {server}.{tool} expected exit 0, got {rc}"

    print(f"\n[PASS] Session {session_num} — all assertions passed ✓")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMemoryFirstGateE2E:
    # Isolation guarantee: per IDE window / per pytest runner process.
    # Green tests here do NOT imply per-chat isolation.

    def test_session_1(self):
        """Fresh session 1: full enforcement sequence (per-window isolation)."""
        _run_session(1)

    def test_session_2(self):
        """Fresh session 2: identical sequence — proves per-window repeatability."""
        _run_session(2)

    def test_degrade_open_on_max_attempts(self):
        """After MAX_MEMORY_BLOCK_ATTEMPTS consecutive blocks, gate degrades to open."""
        _reset_session()

        # Exhaust the attempt counter
        for i in range(1, 4):
            rc, stderr = _invoke_gate("task_manager", "create_task")
            print(f"\n  Block attempt {i}: exit={rc}  stderr={stderr}")
            assert rc == 2, f"Expected block on attempt {i}, got {rc}"
            assert _read_state()["max_memory_block_attempts"] == i

        # Next call must degrade to open (counter == 3 >= MAX_MEMORY_BLOCK_ATTEMPTS)
        rc, stderr = _invoke_gate("task_manager", "create_task")
        print(f"\n  Attempt 4 (degrade-open): exit={rc}  (expected 0)")
        assert rc == 0, f"Expected degrade-open (exit 0) after max attempts, got {rc}"
        assert "degrading to open" in stderr, f"Expected degrade message in stderr: {stderr}"

        print("\n[PASS] degrade-open after max attempts ✓")
