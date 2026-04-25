#!/usr/bin/env python3
"""
plan_driven_closer.py — reconcile Notion Wave/Phase Convergence Status against
the status declared in .windsurf/plans/*.md files.

This is the structured complement to post_commit_phase_closer.py. Rather than
guessing completion from commit messages, it parses each plan's Wave and
Phase-Level Summary markdown tables to extract the authoritative status per
(Wave ID, Phase ID) and patches Notion rows that disagree.

Three-way drift detection (surface these as warnings, don't auto-close):
  1. Plan header says "COMPLETE" but phase tables still say "Todo" → stale plan
  2. Plan table says "Done" but Notion says "Todo" → auto-close candidate
  3. Plan table says "Todo" but Notion says "Done" → possible regression

CLI:
    python plan_driven_closer.py                        # dry-run, summary only
    python plan_driven_closer.py --execute              # patch Notion
    python plan_driven_closer.py --show-drift           # dump full drift report
    python plan_driven_closer.py --plan <slug>          # target one plan

Audit log: artifacts/windsurf/plan_driven_close_audit.jsonl
Fail policy: OPEN — errors logged, exit 0.
Bypass:     PLAN_DRIVEN_CLOSE_BYPASS=1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "plan_driven_close_audit.jsonl"

# SSOT: see .windsurf/scripts/_notion_constants.py
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)

# Status vocabulary — case-insensitive substring match
DONE_STATUSES = {
    "done",
    "complete",
    "completed",
    "shipped",
    "closed",
    "landed",
    "✅",
    "ship",
    "merged",
    "all phases complete",
}
OPEN_STATUSES = {
    "todo",
    "to do",
    "in progress",
    "wip",
    "pending",
    "blocked",
    "deferred",
    "ready",
    "planned",
    "not started",
    "on hold",
}


@dataclass
class PlanStatus:
    plan_slug: str
    plan_file: str
    header_status: str | None = None  # top-level "Status:" line
    wave_status: dict[str, str] = field(default_factory=dict)  # wave_id → status
    phase_status: dict[str, str] = field(default_factory=dict)  # phase_id → status


# ---------------------------------------------------------------------------
# Plan-file parsing
# ---------------------------------------------------------------------------


def _normalize_status(raw: str) -> str:
    """Return 'done', 'open', or 'unknown'."""
    s = raw.strip().lower().strip("*`_ ")
    if not s:
        return "unknown"
    if s in DONE_STATUSES or any(
        d in s for d in ("✅", "complete", "done", "shipped", "closed", "landed", "merged")
    ):
        return "done"
    if s in OPEN_STATUSES or any(
        o in s for o in ("todo", "in progress", "wip", "pending", "blocked", "deferred", "planned", "on hold")
    ):
        return "open"
    return "unknown"


HEADER_STATUS_RE = re.compile(
    r"^(?:-\s+)?\*?\*?Status\*?\*?\s*:\s*(.+?)$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_plan_file(path: Path) -> PlanStatus:
    text = path.read_text(encoding="utf-8", errors="replace")
    status = PlanStatus(plan_slug=path.stem, plan_file=path.name)

    # 1. Top-level Status: header (only take the FIRST occurrence in first 50 lines)
    head = "\n".join(text.splitlines()[:50])
    m = HEADER_STATUS_RE.search(head)
    if m:
        status.header_status = m.group(1).strip()

    # 2. Markdown tables — find any table with a header row containing "Status"
    #    and a left column containing "Phase ID" or "Wave"
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect header row
        if not (line.lstrip().startswith("|") and "|" in line[1:] and "status" in line.lower()):
            i += 1
            continue
        # Next line must be separator (|---|---|)
        if i + 1 >= len(lines) or not re.match(r"^\s*\|[\s\-:|]+\|?\s*$", lines[i + 1]):
            i += 1
            continue
        headers = [h.strip().lower().strip("*") for h in line.strip().strip("|").split("|")]

        # Map column indices
        def find_col(*names: str) -> int:
            for idx, h in enumerate(headers):
                if any(n == h or n in h for n in names):
                    return idx
            return -1

        status_col = find_col("status")
        phase_col = find_col("phase id", "phase")
        wave_col = find_col("wave id", "wave")
        phases_col = find_col("phases")  # "Phases" column lists range like "LJH1.1 – LJH1.3"

        if status_col < 0:
            i += 2
            continue

        # Parse data rows until next non-table line
        j = i + 2
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            cells = [c.strip().strip("*") for c in lines[j].strip().strip("|").split("|")]
            if len(cells) > status_col:
                raw_status = cells[status_col]
                norm = _normalize_status(raw_status)

                # Phase-level table row
                if phase_col >= 0 and phase_col < len(cells):
                    pid = cells[phase_col].strip().strip("`*")
                    if pid and re.match(r"^[A-Za-z][\w\.\-]+$", pid):
                        status.phase_status[pid] = norm

                # Wave-level table row
                if wave_col >= 0 and wave_col < len(cells):
                    wid = cells[wave_col].strip().strip("`*")
                    if wid and re.match(r"^[A-Za-z][\w\.\-]+$", wid):
                        status.wave_status[wid] = norm

                # "Phases" column like "LJH1.1 – LJH1.3" — expand range
                if phases_col >= 0 and phases_col < len(cells):
                    pr = cells[phases_col].strip()
                    # Match "X.a – X.b" or "X.a - X.b" or "X.a, X.b, X.c"
                    range_m = re.match(r"^([A-Za-z][\w]*\.)(\d+)\s*[–\-]\s*(?:[A-Za-z][\w]*\.)?(\d+)$", pr)
                    if range_m:
                        base, start, end = range_m.group(1), int(range_m.group(2)), int(range_m.group(3))
                        for n in range(start, end + 1):
                            status.phase_status.setdefault(f"{base}{n}", norm)
                    else:
                        for p in re.split(r"[,;]", pr):
                            p = p.strip().strip("`*")
                            if p and re.match(r"^[A-Za-z][\w\.\-]+$", p):
                                status.phase_status.setdefault(p, norm)
            j += 1
        i = j

    return status


def parse_all_plans() -> dict[str, PlanStatus]:
    """Return {plan_filename: PlanStatus}."""
    out: dict[str, PlanStatus] = {}
    for path in sorted(PLANS_DIR.glob("*.md")):
        try:
            out[path.name] = parse_plan_file(path)
        except (OSError, UnicodeDecodeError) as exc:
            _log({"event": "plan_parse_error", "path": str(path), "error": str(exc)})
    return out


# ---------------------------------------------------------------------------
# Notion access
# ---------------------------------------------------------------------------


def _notion_request(method: str, path: str, token: str, body: dict | None = None) -> dict | None:
    url = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            parsed: Any = json.loads(resp.read().decode("utf-8"))
            return parsed if isinstance(parsed, dict) else None
    except urllib.error.HTTPError as exc:
        _log(
            {
                "event": "notion_http_error",
                "method": method,
                "path": path,
                "status": exc.code,
                "body": exc.read().decode("utf-8", errors="replace")[:500],
            }
        )
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        _log({"event": "notion_net_error", "method": method, "path": path, "error": str(exc)})
        return None


def fetch_all_open_rows(token: str) -> list[dict]:
    """Page through Wave/Phase Convergence, collecting all rows not Done."""
    out: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = _notion_request("POST", f"/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query", token, body)
        if resp is None:
            break
        for row in resp.get("results", []):
            if not isinstance(row, dict):
                continue
            status_sel = row.get("properties", {}).get("Status", {}).get("select") or {}
            if status_sel.get("name") == "Done":
                continue
            out.append(row)
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
        if not cursor:
            break
    return out


def _rich_text(row: dict, prop: str) -> str:
    rt = row.get("properties", {}).get(prop, {}).get("rich_text") or []
    return "".join(t.get("plain_text", "") for t in rt)


def patch_row_done(page_id: str, reason: str, token: str, existing_blocking: str = "") -> bool:
    evidence = f"\n[PLAN-DRIVEN-CLOSE {datetime.now(timezone.utc).strftime('%Y-%m-%d')}] {reason}"
    new_blocking = (existing_blocking + evidence).strip()[:2000]
    body = {
        "properties": {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": new_blocking}}]},
        }
    }
    resp = _notion_request("PATCH", f"/pages/{page_id}", token, body)
    return resp is not None


# ---------------------------------------------------------------------------
# Log + CLI
# ---------------------------------------------------------------------------


def _log(record: dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


@dataclass
class Candidate:
    page_id: str
    notion_phase_id: str
    notion_wave_id: str
    plan_file: str
    source: str  # "phase_match" | "wave_match" | "header_complete"
    plan_status: str  # the raw plan cell value


def reconcile(
    plans: dict[str, PlanStatus],
    open_rows: list[dict],
) -> tuple[list[Candidate], list[dict[str, Any]]]:
    """Return (close_candidates, warnings)."""
    candidates: list[Candidate] = []
    warnings: list[dict[str, Any]] = []

    for row in open_rows:
        props = row.get("properties", {})
        plan_file = _rich_text(row, "Plan File").strip()
        notion_phase = _rich_text(row, "Phase ID").strip()
        notion_wave = _rich_text(row, "Wave ID").strip()
        page_id = row["id"]

        if not plan_file or plan_file not in plans:
            continue

        plan = plans[plan_file]
        verdict: str | None = None
        source = ""
        plan_status_cell = ""

        # Priority 1: exact phase match
        if notion_phase and notion_phase in plan.phase_status:
            ps = plan.phase_status[notion_phase]
            if ps == "done":
                verdict = "close"
                source = "phase_match"
                plan_status_cell = notion_phase
        # Priority 2: wave match (only if phase unknown)
        if verdict is None and notion_wave and notion_wave in plan.wave_status:
            ws = plan.wave_status[notion_wave]
            if ws == "done":
                # Only trust wave if phase column in plan didn't say something else
                phase_says = plan.phase_status.get(notion_phase) if notion_phase else None
                if phase_says != "open":
                    verdict = "close"
                    source = "wave_match"
                    plan_status_cell = notion_wave
        # Priority 3: header says complete AND plan doesn't contradict via open tables
        if verdict is None and plan.header_status:
            hs = _normalize_status(plan.header_status)
            has_open_rows = any(v == "open" for v in plan.phase_status.values())
            has_open_waves = any(v == "open" for v in plan.wave_status.values())
            if hs == "done":
                if has_open_rows or has_open_waves:
                    # Three-way drift: header says done, tables say open
                    warnings.append(
                        {
                            "kind": "plan_header_table_drift",
                            "plan_file": plan_file,
                            "header": plan.header_status,
                            "open_phases": [k for k, v in plan.phase_status.items() if v == "open"],
                            "open_waves": [k for k, v in plan.wave_status.items() if v == "open"],
                        }
                    )
                else:
                    verdict = "close"
                    source = "header_complete"
                    plan_status_cell = plan.header_status or ""

        if verdict == "close":
            candidates.append(
                Candidate(
                    page_id=page_id,
                    notion_phase_id=notion_phase,
                    notion_wave_id=notion_wave,
                    plan_file=plan_file,
                    source=source,
                    plan_status=plan_status_cell,
                )
            )

    return candidates, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--execute", action="store_true", help="Actually patch (default: dry-run)")
    parser.add_argument("--show-drift", action="store_true", help="Show plan-header-vs-table drift warnings")
    parser.add_argument("--plan", type=str, default=None, help="Only process this plan file name")
    args = parser.parse_args()

    if os.environ.get("PLAN_DRIVEN_CLOSE_BYPASS") == "1":
        _log({"event": "bypass"})
        return 0

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        print("NOTION_TOKEN not set", file=sys.stderr)
        return 1

    print(f"Parsing {len(list(PLANS_DIR.glob('*.md')))} plan files…", file=sys.stderr)
    plans = parse_all_plans()
    if args.plan:
        plans = {k: v for k, v in plans.items() if k == args.plan or v.plan_slug == args.plan}
        if not plans:
            print(f"No plan matches {args.plan!r}", file=sys.stderr)
            return 1

    total_phase_entries = sum(len(p.phase_status) for p in plans.values())
    total_wave_entries = sum(len(p.wave_status) for p in plans.values())
    print(
        f"  Parsed {len(plans)} plans — {total_phase_entries} phase rows, {total_wave_entries} wave rows",
        file=sys.stderr,
    )

    print("Fetching open Notion rows…", file=sys.stderr)
    open_rows = fetch_all_open_rows(token)
    print(f"  {len(open_rows)} open rows", file=sys.stderr)

    candidates, warnings = reconcile(plans, open_rows)
    print(f"\nClose candidates: {len(candidates)}")
    by_source: dict[str, int] = {}
    for c in candidates:
        by_source[c.source] = by_source.get(c.source, 0) + 1
    for src, n in sorted(by_source.items()):
        print(f"  {src}: {n}")

    if args.show_drift and warnings:
        print(f"\nPlan-header-vs-table drift ({len(warnings)} plans):")
        for w in warnings[:20]:
            print(f"  {w['plan_file']}")
            print(f"    header says: {w['header']!r}")
            print(f"    open phases: {w['open_phases'][:5]}{' ...' if len(w['open_phases']) > 5 else ''}")

    if candidates:
        print(f"\nFirst 20 close candidates:")
        for c in candidates[:20]:
            print(
                f"  {c.plan_file} {c.notion_phase_id or c.notion_wave_id} via={c.source} plan_says={c.plan_status!r}"
            )

    if not args.execute:
        print(f"\nDRY RUN — use --execute to apply.")
        _log(
            {
                "event": "dry_run_summary",
                "plans_parsed": len(plans),
                "open_rows": len(open_rows),
                "close_candidates": len(candidates),
                "drift_warnings": len(warnings),
            }
        )
        return 0

    # Execute
    ok = 0
    for c in candidates:
        # Re-fetch blocking items to avoid clobbering
        page = _notion_request("GET", f"/pages/{c.page_id}", token)
        existing = ""
        if page:
            existing = _rich_text(page, "Blocking Items")
        reason = f"source={c.source} plan={c.plan_file} ref={c.plan_status}"
        if patch_row_done(c.page_id, reason, token, existing):
            ok += 1
            _log({"event": "plan_driven_close", "ok": True, **c.__dict__})
        else:
            _log({"event": "plan_driven_close", "ok": False, **c.__dict__})

    print(f"\nPatched: {ok}/{len(candidates)}")
    _log(
        {
            "event": "execute_summary",
            "patched": ok,
            "total_candidates": len(candidates),
            "drift_warnings": len(warnings),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
