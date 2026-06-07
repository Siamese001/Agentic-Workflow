#!/usr/bin/env python3
"""
check_ledger_freshness.py — W3.1 per-ledger freshness SLO gate.

Reads `config/ledger_freshness_slo.yaml` and fires when a ledger's most-recent
`events.ts_utc` is older than its configured `silent_alarm_hours`.

Exit 0 — all within SLO (or allow_empty=true for empty ledgers)
Exit 1 — one or more ledgers stale
Exit 2 — script error

Bypass: LEDGER_FRESHNESS_BYPASS=1
"""

from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "ledger_freshness_slo.yaml"
LEDGER_GLOB = str(REPO_ROOT / "artifacts" / "ledgers" / "*.sqlite")
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "ledger_freshness_violations.jsonl"
REPORT_PATH = REPO_ROOT / "artifacts" / "ledgers" / "freshness_report.json"
BYPASS_LOG = REPO_ROOT / "artifacts" / "governance" / "ledger_freshness_bypass.jsonl"


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


def _load_yaml_minimal(path: Path) -> dict:
    """Tiny YAML reader that handles this file's structure (no PyYAML dep).

    Supports: scalar key:value, nested blocks via indent, inline comments.
    """
    if not path.exists():
        return {"defaults": {"silent_alarm_hours": 168, "allow_empty": True}, "ledgers": {}}
    out: dict = {}
    stack: list[tuple[int, dict]] = [(-1, out)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key_val = line.strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else out
        if key_val.endswith(":"):
            k = key_val[:-1].strip()
            new: dict = {}
            parent[k] = new
            stack.append((indent, new))
        elif ":" in key_val:
            k, v = key_val.split(":", 1)
            v = v.strip().strip('"').strip("'")
            try:
                if v.lower() in ("true", "false"):
                    parent[k.strip()] = v.lower() == "true"
                else:
                    parent[k.strip()] = int(v)
            except ValueError:
                parent[k.strip()] = v
    return out


def _last_event_age_hours(path: str) -> tuple[int, str] | None:
    """Return (age_hours, latest_ts_str) or None if ledger is empty/missing events."""
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return None
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(events)")}
        if "ts_utc" not in cols:
            return None
        row = conn.execute(
            "SELECT ts_utc FROM events WHERE ts_utc IS NOT NULL AND ts_utc != '' ORDER BY ts_utc DESC LIMIT 1"
        ).fetchone()
        if row is None or not row[0]:
            return None
        ts_str = row[0]
        try:
            ts = ts_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
        age_s = (datetime.now(timezone.utc) - dt).total_seconds()
        return int(age_s // 3600), ts_str
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def main() -> int:
    if os.environ.get("LEDGER_FRESHNESS_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_ledger_freshness] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    cfg = _load_yaml_minimal(CONFIG_PATH)
    defaults = cfg.get("defaults", {}) or {}
    default_alarm = int(defaults.get("silent_alarm_hours", 168))
    allow_empty = bool(defaults.get("allow_empty", True))
    per_ledger = cfg.get("ledgers", {}) or {}

    ledgers = sorted(glob.glob(LEDGER_GLOB))
    if not ledgers:
        print("[check_ledger_freshness] OK — no ledgers present (skipped)", file=sys.stderr)
        return 0

    stale: list[dict] = []
    report_rows: list[dict] = []
    for path in ledgers:
        name = os.path.basename(path).replace(".sqlite", "")
        ledger_cfg = per_ledger.get(name, {}) or {}
        alarm_h = int(ledger_cfg.get("silent_alarm_hours", default_alarm))

        result = _last_event_age_hours(path)
        if result is None:
            # empty ledger
            status = "EMPTY"
            age_h: int | None = None
            ts: str | None = None
            if not allow_empty:
                stale.append({"ledger": name, "reason": "empty", "alarm_hours": alarm_h})
        else:
            age_h, ts = result
            if age_h > alarm_h:
                status = "STALE"
                stale.append(
                    {
                        "ledger": name,
                        "age_hours": age_h,
                        "alarm_hours": alarm_h,
                        "last_ts": ts,
                    }
                )
            else:
                status = "FRESH"

        report_rows.append(
            {
                "ledger": name,
                "status": status,
                "age_hours": age_h,
                "alarm_hours": alarm_h,
                "last_ts": ts,
            }
        )
        print(f"  {status:6s} {name:35s} age={age_h}h alarm={alarm_h}h", file=sys.stderr)

    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "ledgers": report_rows,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        # guardian: allow-silent-swallow -- report write: non-fatal observability
        pass

    if stale:
        print(f"[check_ledger_freshness] FAIL — {len(stale)} stale ledger(s)", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"stale": stale})
        return 1

    print(f"[check_ledger_freshness] PASS — {len(ledgers)} ledger(s) within SLO", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_ledger_freshness] script error: {exc}", file=sys.stderr)
        sys.exit(2)
