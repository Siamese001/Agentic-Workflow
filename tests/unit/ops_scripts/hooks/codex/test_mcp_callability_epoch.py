"""Tests for current-epoch MCP callability proof ledger."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "mcp_callability_epoch.py"

_spec = importlib.util.spec_from_file_location("mcp_callability_epoch_under_test", SCRIPT_PATH)
assert _spec and _spec.loader
epoch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(epoch)


def test_session_restart_clears_previous_callability_proof(tmp_path: Path) -> None:
    epoch.write_restart_epoch(
        repo_root=tmp_path,
        session_id="s1",
        epoch_id="epoch-1",
        now=datetime(2026, 7, 3, tzinfo=UTC),
    )
    epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        now=datetime(2026, 7, 3, 0, 1, tzinfo=UTC),
    )

    assert (
        epoch.proof_status(
            "memory",
            repo_root=tmp_path,
            now=datetime(2026, 7, 3, 0, 1, tzinfo=UTC),
        )["status"]
        == "healthy"
    )

    epoch.write_restart_epoch(
        repo_root=tmp_path,
        session_id="s2",
        epoch_id="epoch-2",
        now=datetime(2026, 7, 3, 0, 2, tzinfo=UTC),
    )

    status = epoch.proof_status("memory", repo_root=tmp_path)

    assert status["status"] == "absent"
    assert status["epoch_id"] == "epoch-2"


def test_stale_ledger_epoch_is_not_callable(tmp_path: Path) -> None:
    epoch.write_restart_epoch(
        repo_root=tmp_path,
        session_id="s1",
        epoch_id="epoch-1",
        now=datetime(2026, 7, 3, tzinfo=UTC),
    )
    epoch.write_callability_proof(
        server_id="vector_db",
        tool="health_snapshot",
        evidence='{"semantic_ready":true}',
        repo_root=tmp_path,
        now=datetime(2026, 7, 3, 0, 1, tzinfo=UTC),
    )
    epoch.epoch_path(tmp_path).write_text(
        '{"schema_version":"codex-mcp-session-epoch/v1","epoch_id":"epoch-2"}',
        encoding="utf-8",
    )

    status = epoch.proof_status("vector_db", repo_root=tmp_path)

    assert status["status"] == "stale_epoch"
    assert status["proof_epoch_id"] == "epoch-1"


def test_proof_age_expires_with_env_limit(tmp_path: Path) -> None:
    epoch.write_restart_epoch(
        repo_root=tmp_path,
        epoch_id="epoch-1",
        now=datetime(2026, 7, 3, tzinfo=UTC),
    )
    epoch.write_callability_proof(
        server_id="GitKraken",
        tool="git_status",
        evidence='{"ok":true}',
        repo_root=tmp_path,
        now=datetime(2026, 7, 3, tzinfo=UTC),
    )

    status = epoch.proof_status(
        "GitKraken",
        repo_root=tmp_path,
        env={epoch.PROOF_MAX_AGE_ENV: "5"},
        now=datetime(2026, 7, 3, tzinfo=UTC) + timedelta(seconds=6),
    )

    assert status["status"] == "stale_age"


def test_http_route_metadata_is_returned_with_healthy_proof(tmp_path: Path) -> None:
    epoch.write_restart_epoch(repo_root=tmp_path, epoch_id="epoch-1")
    epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        route_kind="http",
        endpoint="http://127.0.0.1:8766/mcp",
    )

    status = epoch.proof_status("memory", repo_root=tmp_path)

    assert status["status"] == "healthy"
    assert status["route_kind"] == "http"
    assert status["endpoint"] == "http://127.0.0.1:8766/mcp"
