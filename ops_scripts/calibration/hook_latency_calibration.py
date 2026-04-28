#!/usr/bin/env python3
"""
hook_latency_calibration.py — Weekly post-cascade hook chain latency report (P5).

Reads ``artifacts/windsurf/post_cascade_heartbeat.jsonl`` and emits a
markdown report to ``docs/reports/calibration/hook_latency/<YYYY-Www>.md``
summarizing the last 7 days of chain latency measurements.

Metrics:
    - n samples in the window
    - min / p50 / p95 / max latency (ms)
    - samples exceeding the 500 ms budget (Kumar best practice)
    - samples exceeding the 2000 ms "user-visible lag" threshold

Exit 0 always — advisory report, never blocks.

Run manually:
    python ops_scripts/calibration/hook_latency_calibration.py
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HEARTBEAT_PATH = _ROOT / "artifacts" / "windsurf" / "post_cascade_heartbeat.jsonl"
_REPORT_DIR = _ROOT / "docs" / "reports" / "calibration" / "hook_latency"

_BUDGET_MS = 500.0  # Kumar best-practice ceiling for hook execution
_UX_LAG_MS = 2000.0  # user-visibly slow


def _load_samples(since_unix: float) -> list[dict]:
    if not _HEARTBEAT_PATH.exists():
        return []
    out: list[dict] = []
    try:
        for line in _HEARTBEAT_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            ts = obj.get("timestamp_unix")
            lat = obj.get("chain_latency_ms")
            if not isinstance(ts, (int, float)) or not isinstance(lat, (int, float)):
                continue
            if ts < since_unix:
                continue
            out.append(obj)
    except OSError:
        return []
    return out


def _iso_week_label(when: datetime) -> str:
    y, w, _ = when.isocalendar()
    return f"{y:04d}-W{w:02d}"


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def _render(samples: list[dict], window_days: int) -> str:
    if not samples:
        return (
            "# Hook Chain Latency — no samples\n\n"
            f"No heartbeat samples with chain_latency_ms found in the last {window_days} days.\n"
            "First run must populate at least 2 heartbeats before a latency can be computed.\n"
        )

    lats = [float(s["chain_latency_ms"]) for s in samples]
    n = len(lats)
    mn = min(lats)
    mx = max(lats)
    mean = statistics.fmean(lats)
    p50 = _percentile(lats, 50)
    p95 = _percentile(lats, 95)
    over_budget = sum(1 for v in lats if v > _BUDGET_MS)
    over_ux = sum(1 for v in lats if v > _UX_LAG_MS)

    status = "🟢 OK" if p95 <= _BUDGET_MS else ("🟡 WATCH" if p95 <= _UX_LAG_MS else "🔴 REGRESSION")

    return (
        f"# Hook Chain Latency — last {window_days} days\n\n"
        f"**Status**: {status}\n\n"
        f"| Metric | Value |\n"
        f"|---|---:|\n"
        f"| n samples | {n} |\n"
        f"| min | {mn:.1f} ms |\n"
        f"| mean | {mean:.1f} ms |\n"
        f"| p50 | {p50:.1f} ms |\n"
        f"| p95 | {p95:.1f} ms |\n"
        f"| max | {mx:.1f} ms |\n"
        f"| > 500 ms budget (Kumar) | {over_budget} ({100.0 * over_budget / n:.1f}%) |\n"
        f"| > 2000 ms user-lag | {over_ux} ({100.0 * over_ux / n:.1f}%) |\n\n"
        "## Interpretation\n\n"
        "- **< 500 ms**: healthy — hook chain inside industry best-practice budget.\n"
        "- **500–2000 ms**: hook chain is adding detectable latency; profile and trim.\n"
        "- **> 2000 ms**: user-visibly slow; a hook has regressed and needs immediate attention.\n\n"
        "## Raw samples (tail-10)\n\n"
        + "\n".join(f"- {s.get('timestamp_iso', '?')}: {s['chain_latency_ms']:.1f} ms" for s in samples[-10:])
        + "\n"
    )


def main() -> int:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=7)
    samples = _load_samples(since.timestamp())
    body = _render(samples, window_days=7)

    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _REPORT_DIR / f"{_iso_week_label(now)}.md"
    out_path.write_text(body, encoding="utf-8")
    print(f"[hook_latency_calibration] wrote {out_path.relative_to(_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
