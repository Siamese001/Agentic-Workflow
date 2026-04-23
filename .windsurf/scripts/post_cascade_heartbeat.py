"""Post-cascade heartbeat writer (W7.1 observability gap).

Writes a single heartbeat record per Cascade response to
``artifacts/windsurf/post_cascade_heartbeat.jsonl``.

The companion session-start script
``.windsurf/scripts/pre_user_prompt_hook_health_check.py`` inspects the
latest heartbeat and warns the user when the prior session's
post_cascade_response chain did not fire (indicating Windsurf skipped
the hook chain — a known silent-failure mode).

Fail-soft: any write failure is logged to stderr and swallowed so we
never block the response pipeline on observability plumbing.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACTS_DIR = _ROOT / "artifacts" / "windsurf"
_HEARTBEAT_PATH = _ARTIFACTS_DIR / "post_cascade_heartbeat.jsonl"

# Keep the log bounded so it does not grow unboundedly across hundreds of
# sessions. Keep the most recent N lines after appending.
_MAX_LINES = 500


def _record() -> dict[str, object]:
    return {
        "timestamp_unix": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "hook": "post_cascade_heartbeat",
        "script": str(Path(__file__).name),
    }


def _append_and_truncate(path: Path, line: str, max_lines: int = _MAX_LINES) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    try:
        existing = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if len(existing) <= max_lines:
        return
    trimmed = existing[-max_lines:]
    path.write_text("\n".join(trimmed) + "\n", encoding="utf-8")


def main() -> int:
    if os.getenv("POST_CASCADE_HEARTBEAT_DISABLE") == "1":
        return 0
    try:
        line = json.dumps(_record(), ensure_ascii=False)
        _append_and_truncate(_HEARTBEAT_PATH, line)
    except (OSError, TypeError, ValueError) as exc:
        print(
            f"[post_cascade_heartbeat] WARN: could not write heartbeat: {exc}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
