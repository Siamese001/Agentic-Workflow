"""Pre-user-prompt hook-health check (W7.1 session-start recovery).

Reads the latest heartbeat written by
``_post_handlers/heartbeat`` (in-process dispatch) / legacy ``_legacy_cursor/post_cursor_agent_heartbeat.py`` — warns when
the prior session's post_cursor_agent_response chain did not fire.

Detection logic:

  * No heartbeat file          -> first-run or corruption; emit banner.
  * Heartbeat older than the
    stale threshold (default
    30 minutes)                -> previous session's hooks likely
                                  skipped; emit banner.
  * Heartbeat within threshold -> silent.

Fail-soft: any inspection error is logged to stderr and exits 0 so we
never block session start on observability plumbing.

Known limitation (W10.1, RCA 2026-04-23): this check itself runs via
the ``pre_user_prompt`` hook. When Cursor's hook dispatcher is dead
(HOOK_OUTAGE), this watchdog never fires either. A truly independent
fallback (cron / systemd timer / OS-level scheduler) is deferred —
tracked under plan ``post-cursor_agent-watchdog-hardening.md``. Threshold
was tightened from 6h to 30min 2026-04-24 so that when the hook chain
IS alive, even sub-hour gaps surface the drift window.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HEARTBEAT_PATH = _ROOT / "artifacts" / "cursor" / "post_cursor_agent_heartbeat.jsonl"

# Default stale threshold: 30 minutes. Override with
# POST_CURSOR_AGENT_HEARTBEAT_STALE_SECONDS env var.
# W10.1 (RCA 2026-04-23): tightened from 6h → 30min so that the 1h34m
# hook-silence window that triggered the HOOK_OUTAGE RCA would have
# surfaced the banner instead of hiding behind a stale 6h threshold.
_DEFAULT_STALE_SECONDS = 30 * 60


def _stale_threshold() -> int:
    raw = os.getenv("POST_CURSOR_AGENT_HEARTBEAT_STALE_SECONDS")
    if not raw:
        return _DEFAULT_STALE_SECONDS
    try:
        return max(60, int(raw))
    except (TypeError, ValueError):
        return _DEFAULT_STALE_SECONDS


def _read_last_heartbeat(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return None
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return None


def _banner(msg: str) -> None:
    print("", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print("WINDSURF HOOK-CHAIN HEALTH CHECK (W7.1)", file=sys.stderr)
    print("-" * 72, file=sys.stderr)
    print(msg, file=sys.stderr)
    print("=" * 72, file=sys.stderr)


def check_heartbeat_health(
    path: Path = _HEARTBEAT_PATH,
    now: float | None = None,
    stale_seconds: int | None = None,
) -> dict[str, object]:
    """Inspect heartbeat status.

    Returns a dict with:
      status:         one of {"ok", "missing", "stale"}
      last_timestamp: last heartbeat unix timestamp, or None
      age_seconds:    age of last heartbeat, or None
      threshold:      stale threshold in seconds
    """
    now_unix = now if now is not None else time.time()
    threshold = stale_seconds if stale_seconds is not None else _stale_threshold()
    last = _read_last_heartbeat(path)
    if last is None:
        return {
            "status": "missing",
            "last_timestamp": None,
            "age_seconds": None,
            "threshold": threshold,
        }
    ts = last.get("timestamp_unix")
    if not isinstance(ts, (int, float)):
        return {
            "status": "missing",
            "last_timestamp": None,
            "age_seconds": None,
            "threshold": threshold,
        }
    age = now_unix - float(ts)
    status = "stale" if age > threshold else "ok"
    return {
        "status": status,
        "last_timestamp": float(ts),
        "age_seconds": age,
        "threshold": threshold,
    }


def main() -> int:
    if os.getenv("POST_CURSOR_AGENT_HEARTBEAT_HEALTH_DISABLE") == "1":
        return 0
    try:
        result = check_heartbeat_health()
    except (OSError, ValueError) as exc:
        print(
            f"[hook_health_check] WARN: inspection failed: {exc}",
            file=sys.stderr,
        )
        return 0

    status = result["status"]
    threshold = int(result["threshold"])  # type: ignore[arg-type]
    if status == "missing":
        _banner(
            "No post_cursor_agent heartbeat found at:\n"
            f"  {_HEARTBEAT_PATH}\n"
            "This is normal for a brand-new clone. If you have used this\n"
            "repo before, Cursor may have skipped the post_cursor_agent_response\n"
            "hook chain in prior sessions. Run any Cursor Agent response to\n"
            "reseed the heartbeat."
        )
    elif status == "stale":
        age = int(result["age_seconds"] or 0)  # type: ignore[arg-type]
        _banner(
            f"Last post_cursor_agent heartbeat is {age}s old\n"
            f"(threshold: {threshold}s). Cursor may have skipped the\n"
            "post_cursor_agent_response hook chain in the previous session —\n"
            "audit writebacks, author-gate captures, and deferred-scope\n"
            "captures may be missing. Review artifacts/cursor/*.jsonl\n"
            "for gaps before relying on hook-captured state.\n"
            "\n"
            "WORKAROUND (Cursor 2.0.67 bug): Cursor Agent should invoke\n"
            ".claude/governance/scripts/defer.py directly in the same response\n"
            "that emits DEFERRED_SCOPE markers, and use\n"
            "manual_post_cursor_agent_replay.py --file/--clipboard for the\n"
            "full post_cursor_agent chain. See docs in those scripts."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
