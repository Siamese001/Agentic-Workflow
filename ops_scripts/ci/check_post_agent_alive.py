#!/usr/bin/env python3
"""
check_post_agent_alive.py — W5.6 post_cascade hook heartbeat gate.

Windsurf 2.0.67 has a documented bug where post_agent_response hooks
silently stop firing mid-session. The post-hook chain writes a heartbeat
row to `artifacts/cursor/post_agent_heartbeat.jsonl` on every fire.
When the heartbeat goes stale during an active git session, log the
manual-replay instructions and fail CI.

"Active git session" heuristic: any commit in the last --grace-hours
(default 6). If no recent commits, we treat the repo as idle and don't
enforce.

Exit 0 — heartbeat fresh OR repo idle
Exit 1 — heartbeat stale AND recent commits present
Exit 2 — script error

Bypass: POST_AGENT_ALIVE_BYPASS=1
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HEARTBEAT = REPO_ROOT / "artifacts" / "windsurf" / "post_agent_heartbeat.jsonl"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "post_agent_alive_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "post_agent_alive_bypass.jsonl"


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def _parse_iso(ts: str) -> datetime | None:
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _last_heartbeat() -> datetime | None:
    if not HEARTBEAT.exists():
        return None
    # Read last non-empty line efficiently for bounded-size log
    last_line = ""
    try:
        with HEARTBEAT.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.strip():
                    last_line = line.strip()
    except OSError:
        return None
    try:
        obj = json.loads(last_line)
    except (json.JSONDecodeError, ValueError):
        return None
    return _parse_iso(obj.get("timestamp", "") or obj.get("ts", ""))


def _has_recent_commits(grace_hours: int) -> bool:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
            cwd=str(REPO_ROOT),
            check=False,
        )
        if r.returncode != 0:
            return False
    except (subprocess.TimeoutExpired, OSError):
        return False
    last = _parse_iso(r.stdout.strip())
    if last is None:
        return False
    age = (datetime.now(timezone.utc) - last).total_seconds()
    return age <= grace_hours * 3600


def main() -> int:
    ap = argparse.ArgumentParser(description="post_cascade heartbeat (W5.6)")
    ap.add_argument("--max-age-hours", type=int, default=6)
    ap.add_argument(
        "--grace-hours", type=int, default=6, help="Consider repo idle if no commits in this many hours"
    )
    args = ap.parse_args()

    if os.environ.get("POST_AGENT_ALIVE_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_post_agent_alive] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    last = _last_heartbeat()
    active = _has_recent_commits(args.grace_hours)
    now = datetime.now(timezone.utc)

    if not active:
        print(
            "[check_post_agent_alive] OK — repo idle (no commits in "
            f"{args.grace_hours}h); heartbeat check skipped",
            file=sys.stderr,
        )
        return 0

    if last is None:
        print(
            "[check_post_agent_alive] FAIL — repo active but no heartbeat "
            "found. Windsurf post_agent_response hook may be dark; "
            "see memory MEMORY[876ef21d] for bypass workaround.",
            file=sys.stderr,
        )
        _log(VIOLATIONS_LOG, {"reason": "no_heartbeat", "active": True})
        return 1

    age_h = (now - last).total_seconds() / 3600.0
    if age_h > args.max_age_hours:
        print(
            f"[check_post_agent_alive] FAIL — heartbeat stale ({age_h:.1f}h > "
            f"{args.max_age_hours}h). Windsurf 2.0.67 hook-dispatcher regression "
            f"suspected. Manual replay: "
            f"python .claude/governance/scripts/manual_post_agent_replay.py --clipboard",
            file=sys.stderr,
        )
        _log(
            VIOLATIONS_LOG,
            {
                "reason": "stale_heartbeat",
                "age_hours": age_h,
                "max_age_hours": args.max_age_hours,
                "last_heartbeat": last.isoformat(timespec="seconds"),
            },
        )
        return 1

    print(f"[check_post_agent_alive] PASS — heartbeat age {age_h:.1f}h", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError,) as exc:
        print(f"[check_post_agent_alive] script error: {exc}", file=sys.stderr)
        sys.exit(2)
