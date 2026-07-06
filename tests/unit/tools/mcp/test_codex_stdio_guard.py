from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import textwrap


GUARD = Path(__file__).resolve().parents[4] / "tools" / "mcp" / "codex_stdio_guard.py"


def _write_child(tmp_path: Path, body: str) -> Path:
    child = tmp_path / "child.py"
    child.write_text(textwrap.dedent(body), encoding="utf-8")
    return child


def _run_guard(tmp_path: Path, child: Path, payload: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--server",
            "unit_mcp",
            "--artifact-dir",
            str(tmp_path / "artifacts"),
            "--",
            sys.executable,
            str(child),
        ],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        check=False,
    )


def _receipt_rows(tmp_path: Path) -> list[dict]:
    path = tmp_path / "artifacts" / "unit_mcp_stdio_guard.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_guard_forwards_stdin_stdout_byte_for_byte(tmp_path: Path) -> None:
    child = _write_child(
        tmp_path,
        """
        import sys
        data = sys.stdin.buffer.read()
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        """,
    )
    payload = b'{"method":"initialize"}\n{"method":"tools/list"}\nraw:\x00:\xff\n'

    result = _run_guard(tmp_path, child, payload)

    assert result.returncode == 0
    assert result.stdout == payload
    assert result.stderr == b""
    rows = _receipt_rows(tmp_path)
    assert rows[-1]["event"] == "child_exit"
    assert rows[-1]["early_exit_before_initialize_tools_list"] is False


def test_guard_drains_heavy_stderr_without_stdout_corruption(tmp_path: Path) -> None:
    child = _write_child(
        tmp_path,
        """
        import sys
        data = sys.stdin.buffer.read()
        for i in range(200):
            sys.stderr.buffer.write((f"err-{i}-" + "x" * 200 + "\\n").encode())
        sys.stderr.buffer.flush()
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        """,
    )
    payload = b'{"method":"initialize"}\n{"method":"tools/list"}\n'

    result = _run_guard(tmp_path, child, payload)

    assert result.returncode == 0
    assert result.stdout == payload
    assert result.stderr == b""
    stderr_log = tmp_path / "artifacts" / "unit_mcp.stderr.log"
    assert b"err-199-" in stderr_log.read_bytes()


def test_partial_stderr_line_does_not_hang_guard(tmp_path: Path) -> None:
    child = _write_child(
        tmp_path,
        """
        import sys
        data = sys.stdin.buffer.read()
        sys.stderr.buffer.write(b"partial-without-newline")
        sys.stderr.buffer.flush()
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        """,
    )
    payload = b'{"method":"initialize"}\n{"method":"tools/list"}\n'

    result = _run_guard(tmp_path, child, payload)

    assert result.returncode == 0
    assert result.stdout == payload
    assert (tmp_path / "artifacts" / "unit_mcp.stderr.log").read_bytes() == b"partial-without-newline"


def test_child_exit_before_initialize_tools_list_writes_receipt_and_nonzero(tmp_path: Path) -> None:
    child = _write_child(tmp_path, "raise SystemExit(0)")

    result = _run_guard(tmp_path, child)

    assert result.returncode != 0
    rows = _receipt_rows(tmp_path)
    assert rows[-1]["event"] == "child_exit"
    assert rows[-1]["early_exit_before_initialize_tools_list"] is True
    assert rows[-1]["exit_code"] != 0
