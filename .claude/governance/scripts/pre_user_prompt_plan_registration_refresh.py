#!/usr/bin/env python3
"""pre_user_prompt_plan_registration_refresh.py — async cache refresh.

Runs at the start of every Cursor Agent prompt. When
``.claude/state/plan_registration_cache.json`` is older than
``CACHE_TTL_SECONDS`` (1h), spawns a detached background subprocess to
refresh it via ``ops_scripts/ci/check_plan_registration_freshness.py
--refresh``. Returns immediately so prompt latency is <100ms typical.

Why: RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause C — the cache TTL was
declared 1h but no scheduled refresh existed. Operator UI edits made
between snapshots were invisible to recovery and dedup tooling.

Bypass: ``PLAN_CACHE_REFRESH_BYPASS=1``.

Plan: notion-plans-status-rca-followups-b8e3f2 (W2.P2).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Reuse the canonical TTL from _plan_registration. We avoid pulling in
# read_cache/cache_is_fresh because they reference _plan_registration's
# own CACHE_PATH constant — making this module's CACHE_PATH unmockable
# for tests. We re-implement the same logic locally and key off our own
# CACHE_PATH constant.
from _plan_registration import CACHE_TTL_SECONDS  # noqa: E402

CACHE_PATH = REPO_ROOT / ".claude" / "state" / "plan_registration_cache.json"
REFRESH_SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_plan_registration_freshness.py"
LOG_PATH = REPO_ROOT / "artifacts" / "governance" / "plan_cache_refresh.jsonl"


def _read_cache_local() -> dict | None:
    """Read the cache from this module's CACHE_PATH. Returns None on
    missing / malformed input. Mirrors _plan_registration.read_cache so
    tests can monkeypatch CACHE_PATH on this module.
    """
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or "plans" not in data:
        return None
    return data


def _cache_is_fresh_local(cache: dict | None) -> bool:
    if not cache:
        return False
    fetched = cache.get("fetched_at_epoch")
    if not isinstance(fetched, (int, float)):
        return False
    return (time.time() - float(fetched)) <= CACHE_TTL_SECONDS


def _is_bypass() -> bool:
    return os.environ.get("PLAN_CACHE_REFRESH_BYPASS", "").strip() == "1"


def _has_token() -> bool:
    return bool(
        os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    )


def _log(event: dict) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def cache_age_seconds() -> float | None:
    """Return age in seconds or None when cache missing/malformed."""
    cache = _read_cache_local()
    if not cache:
        return None
    fetched = cache.get("fetched_at_epoch")
    if not isinstance(fetched, (int, float)):
        return None
    return time.time() - float(fetched)


def should_refresh() -> tuple[bool, str]:
    """Decide whether to spawn a refresh. Returns (decision, reason)."""
    if _is_bypass():
        return False, "bypass_env_set"
    if not _has_token():
        return False, "no_notion_token"
    cache = _read_cache_local()
    if cache is None:
        return True, "cache_missing"
    if not _cache_is_fresh_local(cache):
        return True, "cache_stale"
    return False, "cache_fresh"


def spawn_refresh() -> tuple[bool, str]:
    """Launch the refresh script detached. Never blocks; never raises."""
    if not REFRESH_SCRIPT.exists():
        return False, f"refresh_script_missing:{REFRESH_SCRIPT}"

    cmd = [sys.executable, str(REFRESH_SCRIPT), "--refresh"]
    try:
        # Detached on Windows; new process group elsewhere. Don't capture
        # stdout/stderr — let the script log to its own files.
        creationflags = 0
        if sys.platform == "win32":
            DETACHED_PROCESS = 0x00000008  # noqa: N806
            creationflags = DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

        subprocess.Popen(  # noqa: S603 — argv list, shell=False
            cmd,
            cwd=str(REPO_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=(sys.platform != "win32"),
            creationflags=creationflags,
        )
        return True, "spawned"
    except (OSError, ValueError) as exc:
        return False, f"spawn_failed:{exc!r}"


def main() -> int:
    decision, reason = should_refresh()
    if not decision:
        # Quiet success — only log when something actually changed.
        return 0

    age = cache_age_seconds()
    spawned, msg = spawn_refresh()
    _log({
        "event": "refresh_decision",
        "decision": decision,
        "reason": reason,
        "spawned": spawned,
        "spawn_msg": msg,
        "cache_age_seconds": age,
        "ttl_seconds": CACHE_TTL_SECONDS,
    })

    # Whisper to stderr so the operator sees the refresh fired.
    if spawned:
        if age is None:
            age_str = "missing"
        else:
            age_str = f"{int(age)}s"
        print(
            f"[plan_cache_refresh] cache age={age_str} ttl={CACHE_TTL_SECONDS}s "
            "— spawning background refresh",
            file=sys.stderr,
        )
    else:
        print(
            f"[plan_cache_refresh] needed but spawn failed: {msg}",
            file=sys.stderr,
        )

    return 0  # never block the prompt


if __name__ == "__main__":
    sys.exit(main())
