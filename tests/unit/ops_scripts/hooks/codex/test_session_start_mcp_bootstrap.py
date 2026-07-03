"""Tests for the Codex SessionStart MCP bootstrap hook."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
BOOTSTRAP = REPO_ROOT / ".codex" / "hooks" / "session_start_mcp_bootstrap.py"

_spec = importlib.util.spec_from_file_location("_session_start_mcp_bootstrap_under_test", BOOTSTRAP)
assert _spec is not None and _spec.loader is not None
bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bootstrap)


def test_prepare_env_sets_mcp_defaults(monkeypatch) -> None:
    monkeypatch.delenv("AGENTIC_REPO_ROOT", raising=False)
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)
    monkeypatch.delenv("MEMORY_DB", raising=False)

    env = bootstrap._prepare_env()

    assert env["AGENTIC_REPO_ROOT"].endswith("Agentic-Workflow-FRESH")
    assert env["ADG_REDIS_URL"] == "redis://localhost:6379/0"
    assert env["MEMORY_DB"] == "artifacts/memory/knowledge_graph.sqlite"
    assert "Agentic-Workflow-FRESH" in env["PYTHONPATH"]


def test_main_skips_detached_backstop_by_default(monkeypatch, tmp_path: Path, capsys) -> None:
    calls: list[tuple[str, list[str]]] = []

    def fake_run(label: str, argv: list[str], *, env: dict[str, str], timeout: int) -> dict[str, Any]:
        calls.append((label, argv))
        return {"label": label, "status": "PASS", "returncode": 0}

    records: list[dict[str, Any]] = []
    epochs: list[dict[str, Any]] = []
    monkeypatch.delenv("CODEX_SESSION_START_DETACHED_MCP_BACKSTOP", raising=False)
    monkeypatch.setattr(bootstrap, "LOG_PATH", tmp_path / "bootstrap.jsonl")
    monkeypatch.setattr(bootstrap, "_drain_stdin", lambda: None)
    monkeypatch.setattr(bootstrap, "_run_step", fake_run)
    monkeypatch.setattr(bootstrap, "_append_log", lambda record: records.append(record))
    monkeypatch.setattr(
        bootstrap,
        "write_restart_epoch",
        lambda **kwargs: epochs.append(kwargs)
        or {"epoch_id": "epoch-1", "session_id": kwargs.get("session_id", "")},
    )

    assert bootstrap.main() == 0

    labels = [label for label, _argv in calls]
    assert "sync_user_config" in labels
    assert "detached_mcp_process_backstop" not in labels
    assert records[0]["steps"][-1]["status"] == "SKIP"
    assert records[0]["mcp_callability_epoch"]["epoch_id"] == "epoch-1"
    assert epochs[0]["source"] == "SessionStart"
    assert "MCP bootstrap complete" in capsys.readouterr().out


def test_main_passes_session_id_to_epoch_writer(monkeypatch, tmp_path: Path) -> None:
    epochs: list[dict[str, Any]] = []
    monkeypatch.setattr(bootstrap, "LOG_PATH", tmp_path / "bootstrap.jsonl")
    monkeypatch.setattr(bootstrap, "_drain_stdin", lambda: '{"sessionId":"session-abc"}')
    monkeypatch.setattr(
        bootstrap,
        "_run_step",
        lambda label, argv, *, env, timeout: {"label": label, "status": "PASS", "returncode": 0},
    )
    monkeypatch.setattr(bootstrap, "_append_log", lambda record: None)
    monkeypatch.setattr(
        bootstrap,
        "write_restart_epoch",
        lambda **kwargs: epochs.append(kwargs)
        or {"epoch_id": "epoch-session", "session_id": kwargs.get("session_id", "")},
    )

    assert bootstrap.main() == 0

    assert epochs[0]["session_id"] == "session-abc"
