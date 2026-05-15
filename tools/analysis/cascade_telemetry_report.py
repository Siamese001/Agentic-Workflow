"""CLI: aggregate cascade telemetry from a JSONL file or in-memory buffer.

Closes the operator-facing half of G7 from
``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md``.

Reads dispatch result records (one JSON object per line) of the shape
emitted by ``HealingRouter._dispatch_qwen`` /
``ConfidenceAwareExecutor.execute`` and prints:

  - cascade rate (MEDIUM->LOW demotions)
  - top fallback_reason buckets
  - per-app cascade counts

Usage::

    python tools/analysis/cascade_telemetry_report.py path/to/events.jsonl

The tool intentionally does not require any prod dependency; it just
reads JSONL.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"telemetry file not found: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except (
                json.JSONDecodeError
            ) as exc:  # guardian: allow-broad-narrow -- specific JSON error type, still narrow
                print(f"warning: skipping malformed line: {exc}", file=sys.stderr)
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if total == 0:
        return {
            "total": 0,
            "cascade_rate": 0.0,
            "by_fallback_reason": {},
            "by_app": {},
            "successes": 0,
            "failures": 0,
        }
    cascades = sum(
        1
        for r in rows
        if r.get("tier_attempted") and r.get("tier_used") and r["tier_attempted"] != r["tier_used"]
    )
    reasons = Counter(r.get("fallback_reason") for r in rows if r.get("fallback_reason"))
    apps = Counter(r.get("app_name", "unknown") for r in rows)
    successes = sum(1 for r in rows if r.get("success"))
    return {
        "total": total,
        "cascade_rate": cascades / total,
        "successes": successes,
        "failures": total - successes,
        "by_fallback_reason": dict(reasons.most_common()),
        "by_app": dict(apps.most_common()),
    }


def render_text(stats: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("=== Cursor Agent Telemetry Report ===")
    lines.append(f"total events       : {stats['total']}")
    lines.append(f"successes          : {stats['successes']}")
    lines.append(f"failures           : {stats['failures']}")
    lines.append(f"cascade rate       : {stats['cascade_rate']:.2%}")
    lines.append("")
    lines.append("Top fallback reasons:")
    for reason, count in stats["by_fallback_reason"].items():
        lines.append(f"  {count:>5}  {reason}")
    if not stats["by_fallback_reason"]:
        lines.append("  (none)")
    lines.append("")
    lines.append("Per-app event counts:")
    for app, count in stats["by_app"].items():
        lines.append(f"  {count:>5}  {app}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a JSONL file of dispatch result records.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable text.",
    )
    args = parser.parse_args(argv)

    rows = _load_jsonl(args.path)
    stats = summarize(rows)
    if args.json:
        print(json.dumps(stats, indent=2, sort_keys=True))
    else:
        print(render_text(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
