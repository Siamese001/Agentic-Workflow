"""One-shot RCA probe for the dead post_cascade hook chain.

Collects four signals:
1. Last heartbeat timestamp vs now → time since hook chain last fired.
2. Last deferred_scope_capture timestamp → confirms the capture-specific
   hook is also dead, not just heartbeat.
3. Current hooks.json config for post_cursor_agent_response → what SHOULD be firing.
4. Any error rows recorded anywhere under artifacts/cursor/ today.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HB = ROOT / "artifacts" / "windsurf" / "post_cursor_agent_heartbeat.jsonl"
DSC = ROOT / "artifacts" / "windsurf" / "deferred_scope_capture.jsonl"
HOOKS = ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
WSDIR = ROOT / "artifacts" / "windsurf"


def _last_iso(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return None
    rec = json.loads(lines[-1])
    val = rec.get(key)
    if isinstance(val, str):
        return val
    if key == "timestamp" and isinstance(val, str):
        return val
    return rec.get("timestamp") or rec.get("timestamp_iso")


def _gap(iso: str) -> str:
    now = datetime.now(timezone.utc)
    when = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return str(now - when)


def main() -> None:
    print("=" * 72)
    print("POST_CASCADE HOOK CHAIN RCA")
    print("=" * 72)

    hb_last = _last_iso(HB, "timestamp_iso")
    print(f"\n[1] Heartbeat log: {HB.name}")
    print(f"    Last entry:    {hb_last}")
    if hb_last:
        print(f"    Gap from now:  {_gap(hb_last)}")
    if HB.exists():
        lines = HB.read_text(encoding="utf-8").strip().splitlines()
        print(f"    Total entries: {len(lines)}")

    dsc_last = _last_iso(DSC, "timestamp")
    print(f"\n[2] Deferred-scope capture log: {DSC.name}")
    print(f"    Last entry:    {dsc_last}")
    if dsc_last:
        print(f"    Gap from now:  {_gap(dsc_last)}")
    if DSC.exists():
        lines = DSC.read_text(encoding="utf-8").strip().splitlines()
        print(f"    Total entries: {len(lines)}")

    print(f"\n[3] hooks.json post_cursor_agent_response config:")
    if HOOKS.exists():
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        post = data.get("hooks", {}).get("post_cursor_agent_response")
        if isinstance(post, list):
            for i, h in enumerate(post):
                flags = ", ".join(f"{k}={v}" for k, v in h.items() if k not in ("description",))
                print(f"    [{i}] {flags}")
        else:
            print(f"    (unexpected shape: {type(post).__name__})")
    else:
        print("    MISSING")

    print(f"\n[4] Error artifacts in {WSDIR.name}/ since 2026-04-23 17:00Z:")
    cutoff = datetime(2026, 4, 23, 17, 0, tzinfo=timezone.utc).timestamp()
    error_hits: list[tuple[str, str]] = []
    for p in sorted(WSDIR.glob("*.jsonl")):
        if p.stat().st_mtime < cutoff:
            continue
        # Look for error rows
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                status = str(rec.get("status") or rec.get("kind") or "").lower()
                if "error" in status or "fail" in status or rec.get("error") or rec.get("exception"):
                    ts = rec.get("timestamp") or rec.get("timestamp_iso") or ""
                    error_hits.append((p.name, f"{ts}: {str(rec)[:160]}"))
        except (OSError, UnicodeDecodeError):
            continue
    if error_hits:
        for name, detail in error_hits[-10:]:
            print(f"    [{name}] {detail}")
    else:
        print("    (none found)")

    print(f"\n[5] Hook log artifacts modified today:")
    today = datetime(2026, 4, 23, tzinfo=timezone.utc).timestamp()
    for p in sorted(WSDIR.glob("*.jsonl")):
        if p.stat().st_mtime < today:
            continue
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        size_kb = p.stat().st_size / 1024
        print(f"    {mtime}  {size_kb:8.2f} KB  {p.name}")


if __name__ == "__main__":
    main()
