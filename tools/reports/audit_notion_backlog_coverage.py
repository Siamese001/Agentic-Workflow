#!/usr/bin/env python3
"""Audit Notion Wave/Phase Convergence coverage vs .windsurf/plans/ on disk.

Deterministic, re-runnable. Writes a markdown audit report to
docs/reports/plans/notion_backlog_audit_<YYYYMMDD>.md.

Surfaces:
  - Plans on disk with ZERO Notion rows (possible missed writebacks)
  - Notion rows pointing to non-existent plan files (renames/deletes)
  - Status breakdown per plan (Todo/In-Progress/Done/Blocked/Descoped/Ready)
  - Rows missing the 5 enriched-schema fields added 2026-04-22

Usage:
    python tools/reports/audit_notion_backlog_coverage.py

Requires: NOTION_TOKEN in env or .env.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "plans"

ENRICHED_FIELDS = (
    "sub_wave",
    "dependencies",
    "success_criteria",
    "files_in_scope",
    "parent_plan_summary",
)


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if not tok:
        env_file = REPO_ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("NOTION_TOKEN="):
                    tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not tok:
        raise SystemExit("NOTION_TOKEN not set and not found in .env")
    return tok


def _query_all_rows() -> list[dict[str, Any]]:
    token = _token()
    results: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"{NOTION_API}/data_sources/{DATA_SOURCE_ID}/query",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise SystemExit(f"Notion API HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
        except urllib.error.URLError as exc:
            raise SystemExit(f"Notion API network error: {exc.reason}") from exc
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return results


def _plain(rich: list[dict[str, Any]]) -> str:
    return "".join(r.get("plain_text", "") for r in rich)


def _extract(row: dict[str, Any]) -> dict[str, str]:
    p = row.get("properties", {})

    def rich(key: str) -> str:
        return _plain(p.get(key, {}).get("rich_text", []))

    def title(key: str) -> str:
        return _plain(p.get(key, {}).get("title", []))

    def select(key: str) -> str:
        sel = p.get(key, {}).get("select")
        return sel.get("name", "") if sel else ""

    return {
        "id": row.get("id", ""),
        "url": row.get("url", ""),
        "title": title("Phase Title"),
        "phase_id": rich("Phase ID"),
        "wave_id": rich("Wave ID"),
        "status": select("Status"),
        "plan_file": (
            rich("Plan File")
            .strip()
            .removeprefix(".windsurf/plans/")
            .removeprefix("windsurf/plans/")
            .removesuffix(".md")
            .strip()
        ),
        "sub_wave": rich("Sub-Wave"),
        "dependencies": rich("Dependencies"),
        "success_criteria": rich("Success Criteria"),
        "files_in_scope": rich("Files In Scope"),
        "parent_plan_summary": rich("Parent Plan Summary"),
    }


def _is_enriched(row: dict[str, str]) -> bool:
    return all(row[f] for f in ENRICHED_FIELDS)


def audit() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    plan_files = sorted(p.name for p in PLANS_DIR.glob("*.md"))
    plan_stems = {p.replace(".md", "") for p in plan_files}

    print(f"Scanning {len(plan_files)} plan files on disk...")
    print("Querying Notion Wave/Phase Convergence DB (paginated)...")
    rows = _query_all_rows()
    extracted = [_extract(r) for r in rows]
    print(f"  Retrieved {len(extracted)} Notion rows")

    by_plan: dict[str, list[dict[str, str]]] = {}
    for row in extracted:
        key = row["plan_file"]
        by_plan.setdefault(key, []).append(row)

    plans_with_rows = set(by_plan.keys()) & plan_stems
    plans_without_rows = plan_stems - set(by_plan.keys())
    notion_orphans = set(by_plan.keys()) - plan_stems - {""}
    rows_missing_enrichment = [r for r in extracted if not _is_enriched(r)]

    today = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
    report_path = REPORT_DIR / f"notion_backlog_audit_{today}.md"

    lines: list[str] = [
        f"# Notion Backlog Audit — {today}",
        "",
        "Deterministic reconciliation of `.windsurf/plans/*.md` vs Notion Wave/Phase Convergence DB.",
        "",
        "## Headline Numbers",
        "",
        f"- Total disk plans: **{len(plan_files)}**",
        f"- Total Notion rows: **{len(extracted)}**",
        f"- Plans with >=1 Notion row: **{len(plans_with_rows)}**",
        f"- Plans WITHOUT Notion rows: **{len(plans_without_rows)}**",
        f"- Notion rows pointing to missing plans: **{len(notion_orphans)}**",
        f"- Rows missing >=1 enriched field: **{len(rows_missing_enrichment)}**/{len(extracted)}",
        "",
        "## 1. Plans WITHOUT Notion Coverage",
        "",
        "Plan files exist on disk but have ZERO rows in Wave/Phase Convergence.",
        "Each needs review: was Notion tracking requested, or is the plan self-contained?",
        "",
    ]
    for p in sorted(plans_without_rows):
        lines.append(f"- `.windsurf/plans/{p}.md`")

    lines += [
        "",
        "## 2. Notion Rows Pointing to Non-Existent Plans",
        "",
        "Plan File values don't match any current `.md`. Plan renamed, deleted, or mistyped.",
        "",
    ]
    if not notion_orphans:
        lines.append("_None._")
    else:
        for p in sorted(notion_orphans):
            count = len(by_plan[p])
            lines.append(f"- `{p}` -- {count} row(s) in Notion")

    lines += [
        "",
        "## 3. Coverage Per Plan With Notion Rows",
        "",
        "| Plan | Rows | Todo | Ready | In-Prog | Done | Blocked | Descoped | Enriched |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in sorted(plans_with_rows):
        rs = by_plan[p]
        counts = {
            "Todo": 0,
            "Ready": 0,
            "In Progress": 0,
            "Done": 0,
            "Blocked": 0,
            "Descoped": 0,
        }
        enriched_count = sum(1 for r in rs if _is_enriched(r))
        for r in rs:
            if r["status"] in counts:
                counts[r["status"]] += 1
        lines.append(
            f"| `{p}` | {len(rs)} | {counts['Todo']} | {counts['Ready']} | "
            f"{counts['In Progress']} | {counts['Done']} | {counts['Blocked']} | "
            f"{counts['Descoped']} | {enriched_count}/{len(rs)} |"
        )

    lines += [
        "",
        "## 4. Rows Missing Enriched Schema Fields",
        "",
        "Created before 2026-04-22 19:31 schema enrichment, or created without populating the 5 fields.",
        "",
        "| Plan | Phase | Wave | Status | Title | Missing Fields |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(rows_missing_enrichment, key=lambda x: (x["plan_file"], x["phase_id"])):
        missing = [f for f in ENRICHED_FIELDS if not r[f]]
        title_esc = r["title"].replace("|", "\\|")[:80]
        lines.append(
            f"| `{r['plan_file']}` | {r['phase_id']} | {r['wave_id']} | "
            f"{r['status']} | {title_esc} | {', '.join(missing)} |"
        )

    lines += [
        "",
        "---",
        f"Generated by `tools/reports/audit_notion_backlog_coverage.py` at "
        f"{datetime.now(tz=timezone.utc).isoformat()}.",
        "Re-run: `python tools/reports/audit_notion_backlog_coverage.py`",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written: {report_path}")
    print(f"  Plans without Notion coverage: {len(plans_without_rows)}")
    print(f"  Notion orphan rows (missing plans): {len(notion_orphans)}")
    print(f"  Rows missing enrichment: {len(rows_missing_enrichment)}/{len(extracted)}")
    return 0


if __name__ == "__main__":
    sys.exit(audit())
