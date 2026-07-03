#!/usr/bin/env python3
"""SessionStart MCP bootstrap for Codex Desktop.

This hook prepares the local dependency surface and keeps the Codex Desktop
MCP config projection in sync with root `.mcp.json`. Actual stdio MCP ownership
belongs to the Codex host: the generated config marks servers `required = true`
so new chats fail startup/resume when a server cannot initialize.

The hook is fail-open and advisory after startup. It must not claim detached
manual stdio processes as callable MCP parity.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(os.environ.get("AGENTIC_REPO_ROOT") or Path(__file__).resolve().parents[2])
LOG_PATH = REPO_ROOT / "artifacts" / "mcp" / "session_start_mcp_bootstrap.jsonl"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
GOVERNANCE_SCRIPTS = REPO_ROOT / ".codex" / "governance" / "scripts"
if str(GOVERNANCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_SCRIPTS))

from mcp_callability_epoch import write_restart_epoch


def _drain_stdin() -> str:
    try:
        if not sys.stdin.closed:
            return sys.stdin.read()
    except OSError:
        return ""
    return ""


def _session_id_from_raw(raw: str) -> str:
    if not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    for key in ("session_id", "sessionId"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _repo_posix() -> str:
    return str(REPO_ROOT.resolve()).replace("\\", "/")


def _find_gitkraken() -> str | None:
    candidates = [
        os.environ.get("GITKRAKEN_GK_PATH", ""),
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "GitKrakenCLI" / "gk.exe"),
        str(Path.home() / "AppData" / "Local" / "GitKrakenCLI" / "gk.exe"),
        "gk",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if candidate == "gk":
            return candidate
        if Path(candidate).exists():
            return candidate
    return None


def _prepare_env() -> dict[str, str]:
    env = dict(os.environ)
    repo = _repo_posix()
    env.setdefault("AGENTIC_REPO_ROOT", repo)
    env.setdefault("ADG_REDIS_URL", DEFAULT_REDIS_URL)
    env.setdefault("MEMORY_DB", "artifacts/memory/knowledge_graph.sqlite")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = repo if not existing_pythonpath else f"{repo}{os.pathsep}{existing_pythonpath}"
    if "GITKRAKEN_GK_PATH" not in env:
        gk = _find_gitkraken()
        if gk:
            env["GITKRAKEN_GK_PATH"] = gk
    return env


def _run_step(label: str, argv: list[str], *, env: dict[str, str], timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
            env=env,
        )
        return {
            "label": label,
            "status": "PASS" if proc.returncode == 0 else "WARN",
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout.strip()[-2000:],
            "stderr_tail": proc.stderr.strip()[-2000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "label": label,
            "status": "WARN",
            "reason": "timeout",
            "timeout": timeout,
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "label": label,
            "status": "WARN",
            "reason": f"{type(exc).__name__}: {exc}",
        }


def _append_log(record: dict[str, Any]) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        return


def main() -> int:
    raw_stdin = _drain_stdin() or ""
    env = _prepare_env()
    epoch = write_restart_epoch(
        repo_root=REPO_ROOT,
        session_id=_session_id_from_raw(raw_stdin),
        source="SessionStart",
    )
    python = sys.executable
    steps = [
        _run_step(
            "sync_user_config",
            [
                python,
                ".codex/governance/scripts/sync_mcp_config.py",
                "--sync-user-config",
                "--json",
            ],
            env=env,
            timeout=30,
        ),
        _run_step(
            "mcp_tool_exposure_audit",
            [
                python,
                ".codex/governance/scripts/mcp_tool_exposure_audit.py",
                "--advisory",
                "--json",
            ],
            env=env,
            timeout=30,
        ),
        _run_step(
            "mcp_python_heartbeat",
            [
                python,
                ".codex/governance/scripts/mcp_python_heartbeat.py",
                "--json",
            ],
            env=env,
            timeout=30,
        ),
        _run_step(
            "searxng_readiness",
            [
                python,
                "scripts/governance/ensure_searxng_readiness.py",
                "--restart",
                "--set-restart-policy",
                "--json",
            ],
            env=env,
            timeout=120,
        ),
    ]

    if env.get("CODEX_SESSION_START_DETACHED_MCP_BACKSTOP") == "1":
        supervisor_env = dict(env)
        supervisor_env["MCP_SUPERVISOR_ENABLED"] = "1"
        steps.append(
            _run_step(
                "detached_mcp_process_backstop",
                [
                    python,
                    ".codex/governance/scripts/mcp_python_supervisor.py",
                    "--json",
                ],
                env=supervisor_env,
                timeout=30,
            )
        )
    else:
        steps.append(
            {
                "label": "detached_mcp_process_backstop",
                "status": "SKIP",
                "reason": "host-owned Codex MCP config is authoritative; detached stdio backstop disabled",
            }
        )

    record = {
        "schema_version": "session-start-mcp-bootstrap/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_root": str(REPO_ROOT),
        "mcp_callability_epoch": {
            "epoch_id": epoch.get("epoch_id"),
            "session_id": epoch.get("session_id"),
        },
        "steps": steps,
    }
    _append_log(record)

    warn_count = sum(1 for step in steps if step.get("status") == "WARN")
    print(
        "[session-start] MCP bootstrap complete "
        f"(warn={warn_count}; log={LOG_PATH})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
