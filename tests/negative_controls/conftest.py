"""Shared harness for negative-control tests.

Each test invokes a gate script as a real subprocess against a fixture
designed to be rejected by the gate. The helpers here keep tests terse.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GateResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def blocked(self) -> bool:
        """A gate is considered to have blocked when it exits non-zero."""
        return self.returncode != 0


def run_gate(
    gate_rel_path: str,
    *,
    args: list[str] | None = None,
    stdin_payload: dict | str | None = None,
    cwd: Path | None = None,
    timeout: int = 30,
    env_overrides: dict[str, str] | None = None,
) -> GateResult:
    """Invoke a gate script as a subprocess and capture its result.

    Args:
        gate_rel_path: repo-relative path to the gate script.
        args: extra CLI args.
        stdin_payload: dict (JSON-encoded) or raw string to send on stdin;
            None means inherit the empty stdin (some gates short-circuit).
        cwd: working directory; defaults to repo root.
        timeout: subprocess timeout in seconds.
        env_overrides: extra env vars (merged into os.environ).

    Returns:
        :class:`GateResult` capturing the exit code and outputs.
    """
    import os

    gate_path = REPO_ROOT / gate_rel_path
    if not gate_path.is_file():
        raise FileNotFoundError(f"gate script missing: {gate_path}")

    cmd = [sys.executable, str(gate_path), *(args or [])]
    stdin_text: str | None
    if stdin_payload is None:
        stdin_text = ""
    elif isinstance(stdin_payload, str):
        stdin_text = stdin_payload
    else:
        stdin_text = json.dumps(stdin_payload)

    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, shell=False
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=str(cwd or REPO_ROOT),
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return GateResult(
            returncode=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
        )

    return GateResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def materialize_files(root: Path, files: dict[str, str]) -> None:
    """Write ``files`` (path -> content) under ``root``."""
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
