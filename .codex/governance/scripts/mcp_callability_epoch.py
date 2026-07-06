#!/usr/bin/env python3
"""Current-session MCP callability proof ledger.

SessionStart writes a restart epoch and clears the proof ledger. PostToolUse
records proof only after a real Codex MCP tool succeeds. Gates may then accept
that proof only when its epoch matches the current SessionStart epoch.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4


DEFAULT_EPOCH_RELATIVE_PATH = Path("artifacts/mcp/codex_mcp_session_epoch.json")
DEFAULT_LEDGER_RELATIVE_PATH = Path("artifacts/mcp/codex_mcp_callability_proofs.json")
DEFAULT_PROOF_MAX_AGE_SECONDS = 24 * 60 * 60
PROOF_MAX_AGE_ENV = "CODEX_MCP_CALLABLE_PROOF_MAX_AGE_SECONDS"

HEALTHY_STATUS = "healthy"
_CANONICAL_SERVER_IDS = {
    "adg_sqlite": "adg_sqlite",
    "gitkraken": "GitKraken",
    "memory": "memory",
    "vector_db": "vector_db",
}


def canonical_server_id(server_id: str) -> str:
    stripped = str(server_id or "").strip()
    return _CANONICAL_SERVER_IDS.get(stripped.lower(), stripped)


def _repo_root(repo_root: Path | None = None) -> Path:
    return repo_root or Path(__file__).resolve().parents[3]


def epoch_path(repo_root: Path | None = None) -> Path:
    return _repo_root(repo_root) / DEFAULT_EPOCH_RELATIVE_PATH


def ledger_path(repo_root: Path | None = None) -> Path:
    return _repo_root(repo_root) / DEFAULT_LEDGER_RELATIVE_PATH


def _now(now: datetime | None = None) -> datetime:
    resolved = now or datetime.now(UTC)
    if resolved.tzinfo is None:
        return resolved.replace(tzinfo=UTC)
    return resolved.astimezone(UTC)


def _iso(now: datetime | None = None) -> str:
    return _now(now).isoformat()


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _max_age_seconds(env: dict[str, str] | None = None) -> float:
    raw = (env or os.environ).get(PROOF_MAX_AGE_ENV, "").strip()
    if not raw:
        return float(DEFAULT_PROOF_MAX_AGE_SECONDS)
    try:
        value = float(raw)
    except ValueError:
        return float(DEFAULT_PROOF_MAX_AGE_SECONDS)
    return value if value > 0 else float(DEFAULT_PROOF_MAX_AGE_SECONDS)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def read_epoch(repo_root: Path | None = None) -> dict[str, Any]:
    return _read_json(epoch_path(repo_root))


def read_ledger(repo_root: Path | None = None) -> dict[str, Any]:
    return _read_json(ledger_path(repo_root))


def write_restart_epoch(
    *,
    repo_root: Path | None = None,
    session_id: str = "",
    source: str = "SessionStart",
    epoch_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    generated_at = _iso(now)
    resolved_epoch_id = epoch_id or f"{session_id or 'sessionless'}:{generated_at}:{uuid4().hex}"
    record = {
        "schema_version": "codex-mcp-session-epoch/v1",
        "epoch_id": resolved_epoch_id,
        "session_id": session_id,
        "source": source,
        "generated_at": generated_at,
        "repo_root": str(root),
    }
    path = epoch_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    reset_callability_ledger(repo_root=root, epoch=record, now=now)
    return record


def reset_callability_ledger(
    *,
    repo_root: Path | None = None,
    epoch: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    resolved_epoch = epoch or read_epoch(root)
    record = {
        "schema_version": "codex-mcp-callability-proofs/v1",
        "epoch_id": str(resolved_epoch.get("epoch_id") or ""),
        "session_id": str(resolved_epoch.get("session_id") or ""),
        "reset_at": _iso(now),
        "servers": {},
    }
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return record


def write_callability_proof(
    *,
    server_id: str,
    tool: str,
    evidence: str,
    repo_root: Path | None = None,
    session_id: str = "",
    pid: int | None = None,
    route_kind: str = "",
    endpoint: str = "",
    now: datetime | None = None,
) -> Path | None:
    root = _repo_root(repo_root)
    epoch = read_epoch(root)
    epoch_id = str(epoch.get("epoch_id") or "")
    if not epoch_id:
        return None

    ledger = read_ledger(root)
    if str(ledger.get("epoch_id") or "") != epoch_id:
        ledger = reset_callability_ledger(repo_root=root, epoch=epoch, now=now)

    canonical = canonical_server_id(server_id)
    proof: dict[str, Any] = {
        "status": HEALTHY_STATUS,
        "server_id": canonical,
        "tool": str(tool),
        "evidence": str(evidence)[:4000],
        "epoch_id": epoch_id,
        "session_id": session_id or str(epoch.get("session_id") or ""),
        "proved_at": _iso(now),
    }
    if isinstance(pid, int) and pid > 0:
        proof["pid"] = pid
    resolved_route_kind = str(route_kind or "").strip().lower()
    if resolved_route_kind:
        proof["route_kind"] = resolved_route_kind
    resolved_endpoint = str(endpoint or "").strip()
    if resolved_endpoint:
        proof["endpoint"] = resolved_endpoint

    servers = ledger.get("servers")
    if not isinstance(servers, dict):
        servers = {}
    servers[canonical] = proof
    ledger["servers"] = servers
    ledger["epoch_id"] = epoch_id
    ledger["session_id"] = str(epoch.get("session_id") or "")

    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    return path


def proof_status(
    server_id: str,
    *,
    repo_root: Path | None = None,
    env: dict[str, str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    canonical = canonical_server_id(server_id)
    epoch = read_epoch(root)
    epoch_id = str(epoch.get("epoch_id") or "")
    if not epoch_id:
        return {"server_id": canonical, "status": "absent", "reason": "no_session_epoch"}

    ledger = read_ledger(root)
    ledger_epoch = str(ledger.get("epoch_id") or "")
    if ledger_epoch != epoch_id:
        return {
            "server_id": canonical,
            "status": "stale_epoch",
            "epoch_id": epoch_id,
            "proof_epoch_id": ledger_epoch,
        }

    servers = ledger.get("servers")
    proof = servers.get(canonical) if isinstance(servers, dict) else None
    if not isinstance(proof, dict):
        return {"server_id": canonical, "status": "absent", "epoch_id": epoch_id}

    proved_at = _parse_iso(proof.get("proved_at"))
    max_age_s = _max_age_seconds(env)
    age_s = None
    if proved_at is not None:
        age_s = max(0.0, (_now(now) - proved_at).total_seconds())
    if proved_at is None:
        status = "malformed_proof"
    elif age_s is not None and age_s > max_age_s:
        status = "stale_age"
    else:
        status = str(proof.get("status") or "absent").strip().lower()

    callable_ok = status == HEALTHY_STATUS
    return {
        "server_id": canonical,
        "status": status,
        "callable": callable_ok,
        "epoch_id": epoch_id,
        "session_id": proof.get("session_id") or "",
        "tool": proof.get("tool") or "",
        "proved_at": proof.get("proved_at") or "",
        "age_s": age_s,
        "max_age_s": max_age_s,
        "pid": proof.get("pid"),
        "route_kind": proof.get("route_kind") or "",
        "endpoint": proof.get("endpoint") or "",
    }
