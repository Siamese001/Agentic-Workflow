"""Pre-user-prompt hook-health check (W7.1 session-start recovery).

Reads the latest heartbeat written by
``.windsurf/scripts/post_cascade_heartbeat.py`` and warns the user when
the prior session's post_cascade_response chain did not fire.

Detection logic:

  * No heartbeat file          -> first-run or corruption; emit banner.
  * Heartbeat older than the
    stale threshold (default
    6 hours)                   -> previous session's hooks likely
                                  skipped; emit banner.
  * Heartbeat within threshold -> silent.

Fail-soft: any inspection error is logged to stderr and exits 0 so we
never block session start on observability plumbing.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HEARTBEAT_PATH = _ROOT / "artifacts" / "windsurf" / "post_cascade_heartbeat.jsonl"

# Default stale threshold: 6 hours. Override with
# POST_CASCADE_HEARTBEAT_STALE_SECONDS env var.
_DEFAULT_STALE_SECONDS = 6 * 60 * 60


def _stale_threshold() -> int:
    raw = os.getenv("POST_CASCADE_HEARTBEAT_STALE_SECONDS")
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
    if os.getenv("POST_CASCADE_HEARTBEAT_HEALTH_DISABLE") == "1":
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
            "No post_cascade heartbeat found at:\n"
            f"  {_HEARTBEAT_PATH}\n"
            "This is normal for a brand-new clone. If you have used this\n"
            "repo before, Windsurf may have skipped the post_cascade_response\n"
            "hook chain in prior sessions. Run any Cascade response to\n"
            "reseed the heartbeat."
        )
    elif status == "stale":
        age = int(result["age_seconds"] or 0)  # type: ignore[arg-type]
        _banner(
            f"Last post_cascade heartbeat is {age}s old\n"
            f"(threshold: {threshold}s). Windsurf may have skipped the\n"
            "post_cascade_response hook chain in the previous session —\n"
            "audit writebacks, author-gate captures, and deferred-scope\n"
            "captures may be missing. Review artifacts/windsurf/*.jsonl\n"
            "for gaps before relying on hook-captured state.\n"
            "\n"
            "WORKAROUND (Windsurf 2.0.67 bug): Cascade should invoke\n"
            ".windsurf/scripts/defer.py directly in the same response\n"
            "that emits DEFERRED_SCOPE markers, and use\n"
            "manual_post_cascade_replay.py --file/--clipboard for the\n"
            "full post_cascade chain. See docs in those scripts."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
