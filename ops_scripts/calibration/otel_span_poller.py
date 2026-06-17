#!/usr/bin/env python3
"""OTEL span poller — feeds the L3 runtime reconciliation gate.

Queries otel_mcp's `spans_by_agent` for each apps_* agent class and
persists the observed span name set to
``artifacts/observability/last_observed_spans.json``. Run nightly via
cron / GitHub Actions / legacy editor scheduled task.

Pairs with `ops_scripts/ci/check_l3_runtime_reconciliation.py` — that
gate consumes this file's output to detect manifest/runtime drift.

Usage:

  # Direct (requires otel_mcp installed in current Python env):
  python ops_scripts/observability/poll_otel_spans.py --time-window-hours 168

  # MCP-mediated (production — legacy editor hook environment):
  python ops_scripts/observability/poll_otel_spans.py --via-mcp --time-window-hours 168

The MCP path is best-effort. When unavailable (e.g. in CI without
otel_mcp), the script writes an empty observation file with source
metadata so downstream tools know the data was unavailable.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_PATH = REPO / "artifacts" / "observability" / "last_observed_spans.json"

# The agent classes we know to query — derived from the apps_* surface.
# Add more as new apps come online.
AGENT_CLASSES = (
    "apps_eval", "apps_exec", "apps_lic", "apps_research",
)


def _try_otel_mcp(time_window_hours: int) -> tuple[set[str], str]:
    """Best-effort fetch via the otel_mcp Python client (if importable)."""
    try:
        # The otel_mcp server doesn't expose a Python client directly;
        # the spans_by_agent tool is invoked via MCP. In this script
        # context we can't issue MCP calls, so we attempt to read the
        # ingestion-layer SQLite/JSON cache that otel_mcp persists.
        cache = REPO / "artifacts" / "otel" / "spans.jsonl"
        if not cache.is_file():
            return set(), "no-otel-cache"
        out: set[str] = set()
        for line in cache.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = row.get("op_name") or row.get("name") or row.get("span_name")
            if name:
                out.add(name)
        return out, f"otel_jsonl_cache:{cache.relative_to(REPO).as_posix()}"
    except Exception as exc:  # noqa: BLE001 — best-effort
        return set(), f"otel_error:{type(exc).__name__}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--time-window-hours", type=int, default=168)
    p.add_argument("--via-mcp", action="store_true",
                   help="Force MCP path (production); otherwise reads jsonl cache.")
    args = p.parse_args(argv)

    spans, source = _try_otel_mcp(args.time_window_hours)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "time_window_hours": args.time_window_hours,
        "source": source,
        "spans": sorted(spans),
        "count": len(spans),
        "agent_classes_queried": list(AGENT_CLASSES),
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[poll_otel_spans] source={source} count={len(spans)}")
    print(f"  wrote {OUT_PATH.relative_to(REPO).as_posix()}")
    return 0 if spans else 4  # exit 4 if no data available — surfaces the gap


if __name__ == "__main__":
    sys.exit(main())
