"""Register notion-backlog-human-scoring-e7a941 plan in Notion.

1. POST plan row to Plans DB
2. POST 5 wave summary rows to Wave/Phase Convergence DB (one per wave, Status=Todo)
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2025-09-03"

PLANS_DB = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
WPC_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"
RECEIPTS = ROOT / "artifacts" / "notion" / "_writeback_receipts.jsonl"

PLAN_SLUG = "notion-backlog-human-scoring-e7a941"
PLAN_FILE = "docs/archive/windsurf/legacy-tree/plans/notion-backlog-human-scoring-e7a941.md"
PLAN_SUMMARY = (
    "Human-driven scoring pass for 63 UNSCORED Wave/Phase Convergence rows that no automated "
    "pass could score. Output: worksheet filled by human -> applier script PATCHes Notion. "
    "5 waves by category: graph-edge (4), governance (22), baseline-burndown (8), singleton (22), "
    "apply (Codex runs script)."
)


def http(method, url, body=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _rt(s, max_len=2000):
    return {"rich_text": [{"type": "text", "text": {"content": s[:max_len]}}]}


def _title(s, max_len=200):
    return {"title": [{"type": "text", "text": {"content": s[:max_len]}}]}


def receipt(op, page_id, ok, **extra):
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "op": op,
        "page_id": page_id,
        "ok": ok,
        **extra,
    }
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


WAVES = [
    (
        "1",
        "Score 4 graph-edge rows (W9/W11/W12/W13)",
        "Human reviews W9 (OTel span->ADG edge), W11 (watchdog + secret telemetry), W12 (HITL decision log edges), W13 (profiler calls). Assigns band based on ADR completeness priority.",
        2000,
        4,
    ),
    (
        "2",
        "Score 22 governance rows (W1.x / W2.x / W2-P1.x)",
        "Human audits each governance row against .codex/rules/ and .codex/hooks.json. Rows that are already landed -> DESCOPE. Rows still real get P-band.",
        5000,
        22,
    ),
    (
        "3",
        "Score 8 baseline-burndown rows (GAP/W1-P0/W3-P2/W4-P3)",
        "Human spot-checks baseline counts (153 env flags, 142 legacy leaks, 1051 uncovered modules) for freshness, then scores.",
        3000,
        8,
    ),
    (
        "4",
        "Score 22 singleton rows (H/B/EQ/ENH/misc)",
        "Human reviews remaining H-series (H3/H6-H10 not in prior Wave D), B-series (B1-B5), EQ-series (EQ-8b/11b/12b/15/16), ENH-series (ENH1-ENH6), and misc singletons (W0/W4/W1-W5/RT3/M/S/TechDebt/INDEX).",
        5000,
        22,
    ),
    (
        "5",
        "Apply filled worksheet to Notion",
        "Codex runs tools/debug/_apply_human_scoring.py once human finishes waves 1-4. Script PATCHes every row with BAND filled, descopes rows marked DESCOPE, skips rows marked SKIP/empty.",
        2000,
        63,
    ),
]


def register_plan():
    body = {
        "parent": {"type": "database_id", "database_id": PLANS_DB},
        "properties": {
            "Slug": _title(PLAN_SLUG),
            "Plan File Path": _rt(PLAN_FILE),
            "Summary": _rt(PLAN_SUMMARY),
            "Status": {"select": {"name": "Not Started"}},
            "Exists On Disk": {"checkbox": True},
        },
    }
    try:
        r = http("POST", "https://api.notion.com/v1/pages", body)
        receipt("POST-plan-register", r["id"], True, slug=PLAN_SLUG)
        print(f"[plan] REGISTERED: {r['id']}")
        return r["id"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        receipt("POST-plan-register", None, False, detail=detail[:500])
        print(f"[plan] FAILED: {detail[:400]}", file=sys.stderr)
        return ""


def post_wave(wave_num: str, label: str, summary: str, tokens: int, row_count: int):
    phase_title = f"Wave {wave_num} — {label}"
    success_crit = (
        f"{row_count} rows processed with BAND assigned (P1..P5, DESCOPE, or SKIP). "
        f"Worksheet path: artifacts/notion/human_scoring_worksheet.json."
    )
    body = {
        "parent": {"type": "database_id", "database_id": WPC_DB},
        "properties": {
            "Phase Title": _title(f"[SCORING] {phase_title}"),
            "Phase ID": _rt(f"Wave-{wave_num}"),
            "Wave ID": _rt("HUMAN-SCORING"),
            "Sub-Wave": _rt(f"HUMAN-SCORING-W{wave_num}-CORE"),
            "Plan File": _rt(PLAN_FILE),
            "Parent Plan Summary": _rt(PLAN_SUMMARY),
            "Success Criteria": _rt(success_crit),
            "Files In Scope": _rt(
                "artifacts/notion/human_scoring_worksheet.json, artifacts/notion/human_scoring_worksheet.md, tools/debug/_apply_human_scoring.py"
            ),
            "Dependencies": _rt(
                "Pass 1/Pass 2 dry-run output from prior plan notion-backlog-residual-cleanup-c3d8f2. "
                + (
                    "Depends on completion of Waves 1-4 (human-filled worksheet)."
                    if wave_num == "5"
                    else "No upstream deps within this plan."
                )
            ),
            "Blocking Items": _rt(summary),
            "Status": {"select": {"name": "Todo"}},
            "Est Tokens": {"number": tokens},
        },
    }
    try:
        r = http("POST", "https://api.notion.com/v1/pages", body)
        receipt("POST-human-scoring-wave", r["id"], True, wave=wave_num, label=label)
        print(f"[wave {wave_num}] POSTED: {r['id']}")
        return r["id"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        receipt("POST-human-scoring-wave", None, False, detail=detail[:500])
        print(f"[wave {wave_num}] FAILED: {detail[:400]}", file=sys.stderr)
        return ""


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1

    print("=" * 70)
    print("Registering notion-backlog-human-scoring-e7a941")
    print("=" * 70)

    plan_id = register_plan()

    print("\nPosting 5 wave summary rows to Wave/Phase Convergence...")
    success = 0
    for wave_num, label, summary, tokens, row_count in WAVES:
        if post_wave(wave_num, label, summary, tokens, row_count):
            success += 1

    print()
    print("=" * 70)
    print("REGISTRATION COMPLETE")
    print("=" * 70)
    print(f"Plan registered: {'YES' if plan_id else 'NO'}")
    print(f"Wave rows: {success}/5")
    return 0 if plan_id and success == 5 else 2


if __name__ == "__main__":
    sys.exit(main())
