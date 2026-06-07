"""mcp_30day_retirement_review.py — 30-day shadow-disabled MCP retirement diagnostic.

Per ADR-095 (plan token-burn-followup-f8c2d1 W3/F4), the `filesystem` and
`task_manager` MCPs are shadow-disabled (`disabled: true` in mcp_config.json).
After 30 calendar days (target 2026-06-01), this script provides the operator
with the data needed to make the retirement vs. re-enablement decision.

Methodology
-----------
Disabled MCPs do not appear in Cursor Agent's tool list, so direct tool-call counts
in `turn_budget.jsonl` will always be 0 for the disabled prefixes. This is
expected and not, on its own, evidence of unneed.

The actionable signals are:
  1. Confirm the MCP is still disabled (config sanity)
  2. Count the days the shadow-disable has been in effect
  3. Surface ANY usage rows that DID hit the disabled prefixes (would indicate
     model attempted a call against a phantom tool — should never happen but
     paranoid check)
  4. Print a turn-count baseline so the operator knows how much usage occurred
     during the window
  5. Print the exact ADR-095 review checklist for human judgment

Usage
-----
  python tools/diagnostics/mcp_30day_retirement_review.py
  python tools/diagnostics/mcp_30day_retirement_review.py --since 2026-05-02
  python tools/diagnostics/mcp_30day_retirement_review.py --servers filesystem,task_manager
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
TURN_BUDGET = REPO_ROOT / "artifacts" / "governance" / "turn_budget.jsonl"

# Default review targets — the two shadow-disabled MCPs from ADR-095.
DEFAULT_REVIEW_SERVERS = ["filesystem", "task_manager"]
DEFAULT_SINCE = "2026-05-02"  # ADR-095 decision date


def _load_mcp_config() -> dict[str, dict[str, Any]]:
    raw = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    return raw.get("mcpServers", {})


def _server_status(spec: dict[str, Any]) -> str:
    return "DISABLED" if spec.get("disabled") else "ACTIVE"


def _shadow_disable_note(spec: dict[str, Any]) -> str:
    return spec.get("_shadow_disable", "")


def _iter_turn_budget(since_iso: str) -> list[dict[str, Any]]:
    """Yield rows from turn_budget.jsonl with timestamp >= since_iso."""
    if not TURN_BUDGET.exists():
        return []
    rows: list[dict[str, Any]] = []
    with TURN_BUDGET.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = row.get("timestamp", "")
            if ts >= since_iso:
                rows.append(row)
    return rows


def _count_mcp_calls(rows: list[dict[str, Any]], server_name: str) -> dict[str, int]:
    """Aggregate tool_call_counts by tool-name prefix for the given server.

    MCP tool prefixes shift with mcp_config.json ordering, so we match on the
    suffix pattern: any tool whose name contains the server's distinctive token
    suffix counts. For filesystem: read_text_file, read_multiple_files,
    directory_tree, write_file, etc. For task_manager: create_task,
    decompose_task, update_task, task_info.
    """
    suffix_patterns = {
        "filesystem": (
            "read_text_file", "read_multiple_files", "directory_tree",
            "write_file", "create_directory", "list_directory", "move_file",
            "search_files", "get_file_info", "edit_file",
        ),
        "task_manager": (
            "create_task", "decompose_task", "update_task", "task_info",
        ),
    }
    patterns = suffix_patterns.get(server_name, ())
    counts: dict[str, int] = {}
    for row in rows:
        for tool, n in (row.get("tool_call_counts") or {}).items():
            for pat in patterns:
                if pat in tool:
                    counts[tool] = counts.get(tool, 0) + int(n)
                    break
    return counts


def _days_since(since_iso: str) -> int:
    try:
        since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
        if since_dt.tzinfo is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return -1
    now = datetime.now(timezone.utc)
    return (now - since_dt).days


def _review_one(server_name: str, spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "server": server_name,
        "status": _server_status(spec),
        "shadow_disable_note": _shadow_disable_note(spec),
        "tool_call_counts": _count_mcp_calls(rows, server_name),
        "tool_call_total": sum(_count_mcp_calls(rows, server_name).values()),
    }


def _print_human_report(reviews: list[dict[str, Any]], since_iso: str, total_rows: int) -> None:
    days = _days_since(since_iso)
    print()
    print("=" * 72)
    print("30-Day Shadow-Disabled MCP Retirement Review (ADR-095)")
    print("=" * 72)
    print(f"Decision date:  {since_iso}")
    print(f"Days elapsed:   {days}")
    print(f"Telemetry rows: {total_rows} (in turn_budget.jsonl since decision date)")
    print()

    for r in reviews:
        print(f"### {r['server']} — status={r['status']}")
        if r["shadow_disable_note"]:
            print(f"   Shadow-disable note: {r['shadow_disable_note'][:120]}...")
        if r["tool_call_total"] == 0:
            print(f"   Tool calls observed: 0 (expected — MCP is disabled)")
        else:
            print(f"   Tool calls observed: {r['tool_call_total']} ⚠️  ANOMALY")
            for tool, n in sorted(r["tool_call_counts"].items()):
                print(f"     - {tool}: {n}")
        print()

    print("=" * 72)
    print("Operator Decision Checklist (ADR-095 §Re-Enablement / Retirement)")
    print("=" * 72)
    print("For EACH disabled MCP, ask yourself:")
    print("  [ ] During the last 30 days, did any task feel harder due to its absence?")
    print("  [ ] Were there cases where native tools (read_file, write_to_file,")
    print("      edit, list_dir, find_by_name, structured-reasoning skill) felt")
    print("      strictly worse than the disabled MCP would have been?")
    print("  [ ] Are there pending workflows that NEED the MCP within the next 30 days?")
    print()
    print("If ALL three answers are 'no' for an MCP -> RETIRE (write follow-up ADR;")
    print("  remove from mcp_config.json; AGENTS.md regenerates automatically).")
    print("If ANY answer is 'yes' -> RE-ENABLE (set disabled=false; document the")
    print("  substitute-insufficiency case in a follow-up ADR for future reference).")
    print()
    print(f"After 30 calendar days the recommendation is overdue.")
    if days < 30:
        print(f"NOTE: Only {days}/30 days elapsed — re-run on or after 2026-06-01.")
    print("=" * 72)


def main() -> int:
    p = argparse.ArgumentParser(description="30-day MCP retirement review (ADR-095)")
    p.add_argument("--since", default=DEFAULT_SINCE, help="ISO date the disable took effect")
    p.add_argument(
        "--servers",
        default=",".join(DEFAULT_REVIEW_SERVERS),
        help="Comma-separated server names to review",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human report")
    args = p.parse_args()

    config = _load_mcp_config()
    target_servers = [s.strip() for s in args.servers.split(",") if s.strip()]
    rows = _iter_turn_budget(args.since)

    reviews: list[dict[str, Any]] = []
    for name in target_servers:
        if name not in config:
            print(f"[mcp_30day_review] WARN: server {name!r} not in mcp_config.json", file=sys.stderr)
            continue
        reviews.append(_review_one(name, config[name], rows))

    if args.json:
        print(json.dumps({
            "since": args.since,
            "days_elapsed": _days_since(args.since),
            "telemetry_rows": len(rows),
            "reviews": reviews,
        }, indent=2))
    else:
        _print_human_report(reviews, args.since, len(rows))

    return 0


if __name__ == "__main__":
    sys.exit(main())
