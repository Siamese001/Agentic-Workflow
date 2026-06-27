from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import time

from tools.adg.mcp import supervisor
from tools.mcp import mcp_heartbeat

REPO_ROOT = Path(__file__).resolve().parents[4]


def _write_snapshot(adg_dir: Path, name: str = "adg_indexed_06012026_1200.sqlite") -> Path:
    adg_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = adg_dir / name
    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO nodes VALUES ('n1')")
        conn.execute("INSERT INTO edges VALUES ('e1')")
        conn.commit()
    finally:
        conn.close()
    return sqlite_path


def test_normalize_optional_env_value_rejects_placeholders() -> None:
    assert supervisor.normalize_optional_env_value("${ADG_REDIS_URL}") is None
    assert supervisor.normalize_optional_env_value("{ADG_REPO_ROOT}") is None
    assert supervisor.normalize_optional_env_value(" redis://127.0.0.1:6379/0 ") == (
        "redis://127.0.0.1:6379/0"
    )


def test_configure_process_environment_sets_root_and_cleans_redis_placeholder(tmp_path: Path) -> None:
    env = {
        "ADG_REDIS_URL": "${ADG_REDIS_URL}",
        "PYTHONPATH": "C:\\existing",
    }

    before = supervisor.configure_process_environment(tmp_path, env)

    assert before["ADG_REDIS_URL"] == "${ADG_REDIS_URL}"
    assert env["ADG_REPO_ROOT"] == str(tmp_path)
    assert env["AGENTIC_REPO_ROOT"] == str(tmp_path)
    assert "ADG_REDIS_URL" not in env
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(tmp_path)


def test_preflight_ok_with_valid_sqlite_and_no_redis(
    monkeypatch,
    tmp_path: Path,
) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    sqlite_path = _write_snapshot(adg_dir)
    monkeypatch.setenv("ADG_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)

    result = supervisor.preflight_status()

    assert result["status"] == "ok"
    assert result["sqlite"]["sqlite_path"] == str(sqlite_path.resolve())
    assert result["sqlite"]["node_count"] == 1
    assert result["redis"] == {"status": "disabled", "configured": False}


def test_preflight_critical_without_valid_sqlite(monkeypatch, tmp_path: Path) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    monkeypatch.setenv("ADG_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")

    result = supervisor.preflight_status()

    assert result["status"] == "critical"
    assert result["sqlite"]["available"] is False
    assert result["issues"]


def test_write_and_read_launcher_state(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"

    written = supervisor.write_launcher_state(
        {"status": "running", "pid": 123},
        state_path=state_path,
        repo_root=tmp_path,
    )
    loaded = supervisor.read_launcher_state(state_path=state_path, repo_root=tmp_path)

    assert written == state_path
    assert loaded == {"status": "running", "pid": 123}
    assert json.loads(state_path.read_text(encoding="utf-8"))["status"] == "running"


def test_transport_status_closed_when_backend_ok_but_no_heartbeat(
    monkeypatch,
    tmp_path: Path,
) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    _write_snapshot(adg_dir)
    monkeypatch.setenv("ADG_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)
    monkeypatch.setattr(mcp_heartbeat, "_HEARTBEAT_DIR", tmp_path / "hb")

    result = supervisor.transport_status(state_path=tmp_path / "missing.json")

    assert result["status"] == "closed"
    assert result["preflight"]["status"] == "ok"
    assert result["open"] is False


def test_transport_status_heartbeat_without_callable_proof_is_not_open(
    monkeypatch,
    tmp_path: Path,
) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    _write_snapshot(adg_dir)
    heartbeat_dir = tmp_path / "hb"
    heartbeat_dir.mkdir()
    monkeypatch.setenv("ADG_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)
    monkeypatch.delenv(supervisor.CALLABLE_PROOF_ENV, raising=False)
    monkeypatch.setattr(mcp_heartbeat, "_HEARTBEAT_DIR", heartbeat_dir)
    marker_path = mcp_heartbeat._heartbeat_path(supervisor.ADG_SERVER_MARKERS[0])
    marker_path.write_text(f"{time.time():.3f}:{os.getpid()}\n", encoding="utf-8")

    result = supervisor.transport_status(state_path=tmp_path / "missing.json")

    assert result["status"] == "callability_unproven"
    assert result["heartbeat_authoritative"] is True
    assert result["callable_proof"]["callable"] is False
    assert result["open"] is False


def test_transport_status_open_requires_authoritative_heartbeat_and_callable_proof(
    monkeypatch,
    tmp_path: Path,
) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    _write_snapshot(adg_dir)
    heartbeat_dir = tmp_path / "hb"
    heartbeat_dir.mkdir()
    monkeypatch.setenv("ADG_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)
    monkeypatch.setenv(supervisor.CALLABLE_PROOF_ENV, "healthy")
    monkeypatch.setattr(mcp_heartbeat, "_HEARTBEAT_DIR", heartbeat_dir)
    marker_path = mcp_heartbeat._heartbeat_path(supervisor.ADG_SERVER_MARKERS[0])
    marker_path.write_text(f"{time.time():.3f}:{os.getpid()}\n", encoding="utf-8")

    result = supervisor.transport_status(state_path=tmp_path / "missing.json")

    assert result["status"] == "open"
    assert result["callable_proof"]["callable"] is True
    assert result["open"] is True


def test_guard_markers_include_supervised_launcher() -> None:
    assert supervisor.LAUNCHER_MARKER in supervisor.ADG_SERVER_MARKERS


def test_root_mcp_config_uses_supervised_launcher() -> None:
    config = json.loads((REPO_ROOT / ".mcp.json").read_text(encoding="utf-8"))
    adg_sqlite = config["mcpServers"]["adg_sqlite"]

    assert adg_sqlite["command"] == "python"
    assert adg_sqlite["args"] == ["-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"]
