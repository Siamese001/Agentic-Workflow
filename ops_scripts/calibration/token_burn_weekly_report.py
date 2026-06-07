"""token_burn_weekly_report.py - weekly aggregate of per-turn token telemetry.

Reads `artifacts/cursor/turn_budget.jsonl` (produced by
`post_agent_token_telemetry.py`) and emits a markdown report at
`docs/reports/token-burn/<YYYY-Www>.md` with:

  - Total turns observed
  - Aggregate approx tokens (response + payload)
  - Top-10 highest-burn turns with timestamps
  - Tool-call frequency table (which tools dominate burn)
  - Marker frequency (DECISION_CAPTURED, NEXT_STEP, etc.)
  - Read-budget violation cross-reference (count over-cap turns from
    `read_budget_violations.jsonl`)

Usage:
  python ops_scripts/calibration/token_burn_weekly_report.py [--week YYYY-Www]
  python ops_scripts/calibration/token_burn_weekly_report.py --tail-only

Without --week, defaults to current ISO week.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_LOG = REPO_ROOT / "artifacts" / "windsurf" / "turn_budget.jsonl"
READ_BUDGET_LOG = REPO_ROOT / "artifacts" / "windsurf" / "read_budget_violations.jsonl"
GREP_BUDGET_LOG = REPO_ROOT / "artifacts" / "windsurf" / "grep_budget_violations.jsonl"
REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "token-burn"


def _iso_week_bounds(year: int, week: int) -> tuple[datetime, datetime]:
    """Return [start, end) of an ISO week as UTC datetimes."""
    monday = datetime.fromisocalendar(year, week, 1).replace(tzinfo=timezone.utc)
    return (monday, monday + timedelta(days=7))


def _parse_week_arg(week: str) -> tuple[int, int]:
    """Parse 'YYYY-Www' format, e.g. '2026-W18'."""
    try:
        year_str, week_str = week.split("-W")
        return (int(year_str), int(week_str))
    except (ValueError, IndexError) as exc:
        raise SystemExit(f"--week must be 'YYYY-Www', got '{week}': {exc}")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except (ValueError, TypeError):
                continue
    return rows


def _filter_week(
    rows: list[dict[str, Any]], start: datetime, end: datetime
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        ts_str = row.get("timestamp")
        if not isinstance(ts_str, str):
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if start <= ts < end:
            out.append(row)
    return out


def _render_report(
    week_label: str,
    turns: list[dict[str, Any]],
    read_violations: list[dict[str, Any]],
    grep_violations: list[dict[str, Any]],
) -> str:
    n_turns = len(turns)
    if n_turns == 0:
        return f"# Token-Burn Report - {week_label}\n\nNo turns recorded this week.\n"

    total_response_tokens = sum(t.get("approx_response_tokens", 0) for t in turns)
    total_payload_tokens = sum(t.get("approx_payload_tokens", 0) for t in turns)
    total_tool_calls = sum(t.get("tool_call_total", 0) for t in turns)
    avg_response = total_response_tokens // n_turns if n_turns else 0
    avg_payload = total_payload_tokens // n_turns if n_turns else 0

    # Top-10 by approx_payload_tokens.
    top = sorted(turns, key=lambda t: t.get("approx_payload_tokens", 0), reverse=True)[:10]

    # Tool-call frequency.
    tool_counter: Counter[str] = Counter()
    for t in turns:
        for name, n in (t.get("tool_call_counts") or {}).items():
            tool_counter[name] += n

    # Marker frequency.
    marker_counter: Counter[str] = Counter()
    for t in turns:
        for name, n in (t.get("marker_counts") or {}).items():
            marker_counter[name] += n

    lines: list[str] = []
    lines.append(f"# Token-Burn Report - {week_label}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Turns observed:** {n_turns}")
    lines.append(f"- **Total approx response tokens:** {total_response_tokens:,}")
    lines.append(f"- **Total approx payload tokens:** {total_payload_tokens:,}")
    lines.append(f"- **Total tool calls:** {total_tool_calls}")
    lines.append(f"- **Avg response tokens/turn:** {avg_response:,}")
    lines.append(f"- **Avg payload tokens/turn:** {avg_payload:,}")
    lines.append(f"- **Read-budget violations:** {len(read_violations)}")
    lines.append(f"- **Grep-budget violations:** {len(grep_violations)}")
    lines.append("")
    lines.append("> Approximation: tokens = bytes/4 (Claude tokenizer ratio 3-5x).")
    lines.append("")
    lines.append("## Top 10 Highest-Burn Turns")
    lines.append("")
    lines.append("| Rank | Timestamp | Response Tokens | Payload Tokens | Tool Calls |")
    lines.append("|------|-----------|----------------:|---------------:|-----------:|")
    for i, t in enumerate(top, 1):
        ts = t.get("timestamp", "?")
        resp = t.get("approx_response_tokens", 0)
        payload = t.get("approx_payload_tokens", 0)
        calls = t.get("tool_call_total", 0)
        lines.append(f"| {i} | `{ts}` | {resp:,} | {payload:,} | {calls} |")
    lines.append("")
    lines.append("## Tool-Call Frequency")
    lines.append("")
    lines.append("| Tool | Calls |")
    lines.append("|------|------:|")
    for name, count in tool_counter.most_common(20):
        lines.append(f"| `{name}` | {count} |")
    lines.append("")
    lines.append("## Marker Frequency")
    lines.append("")
    if not marker_counter:
        lines.append("_No markers observed this week._")
    else:
        lines.append("| Marker | Occurrences |")
        lines.append("|--------|-----------:|")
        for name, count in marker_counter.most_common():
            lines.append(f"| `{name}` | {count} |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Source: `artifacts/cursor/turn_budget.jsonl`")
    lines.append("- Generator: `ops_scripts/calibration/token_burn_weekly_report.py`")
    lines.append("- Plan reference: `docs/archive/windsurf/legacy-tree/plans/windsurf-token-burn-augmentation-b7a3f1.md` W2/P3")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Weekly token-burn report")
    ap.add_argument(
        "--week",
        default=None,
        help="ISO week label like '2026-W18'. Defaults to current week.",
    )
    ap.add_argument(
        "--tail-only",
        action="store_true",
        help="Print summary to stdout; do not write report file.",
    )
    args = ap.parse_args(argv)

    if args.week:
        year, week = _parse_week_arg(args.week)
        week_label = args.week
    else:
        now = datetime.now(timezone.utc)
        year, week, _ = now.isocalendar()
        week_label = f"{year}-W{week:02d}"

    start, end = _iso_week_bounds(year, week)
    turns = _filter_week(_load_jsonl(TELEMETRY_LOG), start, end)
    reads = _filter_week(_load_jsonl(READ_BUDGET_LOG), start, end)
    greps = _filter_week(_load_jsonl(GREP_BUDGET_LOG), start, end)

    report = _render_report(week_label, turns, reads, greps)

    if args.tail_only:
        sys.stdout.write(report)
        return 0

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{week_label}.md"
    out.write_text(report, encoding="utf-8")
    sys.stdout.write(f"Wrote {out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
