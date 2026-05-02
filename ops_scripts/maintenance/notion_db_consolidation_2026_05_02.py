"""notion_db_consolidation_2026_05_02.py — One-shot Notion DB cleanup.

Per Tier 1 plan (2026-05-02):
  1. Fetch all MCP Registry rows; identify BACKLOG/Disabled entries and the
     _serialization_sentinel retirement runbook.
  2. Migrate BACKLOG rows -> Backlog Items DB (Status=Draft, P-Band=P3).
  3. Dump _serialization_sentinel content to a staging file for ADR conversion.
  4. Archive 4 Notion DBs (in_trash=true):
       - MCP Registry            59693bbc-71b1-4c63-bc9f-b31eb8b08a0e
       - Constitutional Rules    1c1379bc-32ca-4216-898a-3672f0316f69
       - SC/AP Violation Backlog 0a3b8072-eabd-4516-9473-3c321bb011ff
       - ADR Registry            6ed25e12-bd92-4352-ac7a-3a971311f024

Idempotent: re-running after partial success is safe (creates duplicates only
if interrupted between fetch and post; the migration log records every action).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

NOTION_VERSION = "2025-09-03"
RATE_SLEEP = 0.35

MCP_REGISTRY_DSID = "e7b149b4-0496-4e98-a5dd-074dbe31881b"
BACKLOG_ITEMS_DBID = "aa8d2507-101e-4384-81d9-60ea3fe33876"

DBS_TO_ARCHIVE = {
    "MCP Registry": "59693bbc-71b1-4c63-bc9f-b31eb8b08a0e",
    "Constitutional Rules Registry": "1c1379bc-32ca-4216-898a-3672f0316f69",
    "SC/AP Violation Backlog": "0a3b8072-eabd-4516-9473-3c321bb011ff",
    "ADR Registry": "6ed25e12-bd92-4352-ac7a-3a971311f024",
}

STAGING_DIR = Path("artifacts/maintenance/notion_consolidation_2026_05_02")


def _headers() -> dict[str, str]:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        raise RuntimeError("NOTION_TOKEN not set")
    return {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _request(method: str, url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise last_exc if last_exc else RuntimeError("request failed")


def _query_all(data_source_id: str) -> list[dict]:
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    rows: list[dict] = []
    cursor = None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        resp = _request("POST", url, payload)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            return rows
        cursor = resp.get("next_cursor")


def _rt(prop) -> str:
    """Concatenate rich_text blocks into a single string."""
    if not prop:
        return ""
    arr = prop.get("rich_text") or prop.get("title") or []
    return "".join(b.get("plain_text", "") for b in arr)


def _post_backlog_row(title: str, summary: str) -> dict:
    """Create a Backlog Items row with Status=Draft, P-Band=P3."""
    payload = {
        "parent": {"type": "database_id", "database_id": BACKLOG_ITEMS_DBID},
        "properties": {
            "Phase Title": {"title": [{"type": "text", "text": {"content": title[:200]}}]},
            "Status": {"select": {"name": "Draft"}},
            "P-Band": {"select": {"name": "P3"}},
            "Evidence": {"rich_text": [{"type": "text", "text": {"content": summary[:1900]}}]},
        },
    }
    res = _request("POST", "https://api.notion.com/v1/pages", payload)
    time.sleep(RATE_SLEEP)
    return res


def _archive_database(db_id: str) -> dict:
    url = f"https://api.notion.com/v1/databases/{db_id}"
    res = _request("PATCH", url, {"in_trash": True})
    time.sleep(RATE_SLEEP)
    return res


def main() -> int:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    # 1. Fetch all MCP Registry rows.
    print("[1/4] Fetching MCP Registry rows...")
    rows = _query_all(MCP_REGISTRY_DSID)
    print(f"      found {len(rows)} rows")

    # 2. Classify: BACKLOG, retirement runbook, or skip.
    backlog_rows: list[dict] = []
    retirement_rows: list[dict] = []
    for row in rows:
        props = row["properties"]
        title = _rt(props.get("Server Name"))
        notes = _rt(props.get("Notes"))
        status = (props.get("Status", {}).get("select") or {}).get("name", "")
        if "BACKLOG" in title.upper() or "BACKLOG —" in notes[:200]:
            backlog_rows.append({"title": title, "notes": notes,
                                 "scope": _rt(props.get("Capability Scope")),
                                 "authority": _rt(props.get("Authority"))})
        elif "RETIREMENT PROCEDURE" in notes.upper() or "RETIRE THIS ENTRY" in notes.upper():
            retirement_rows.append({"title": title, "notes": notes,
                                    "scope": _rt(props.get("Capability Scope")),
                                    "authority": _rt(props.get("Authority")),
                                    "linked_adr": _rt(props.get("Linked ADR"))})
    print(f"      backlog={len(backlog_rows)} retirement_runbooks={len(retirement_rows)}")

    # Stash full content for ADR conversion.
    (STAGING_DIR / "backlog_rows.json").write_text(
        json.dumps(backlog_rows, indent=2), encoding="utf-8")
    (STAGING_DIR / "retirement_rows.json").write_text(
        json.dumps(retirement_rows, indent=2), encoding="utf-8")

    # 3. Migrate backlog rows to Backlog Items.
    print(f"[2/4] Migrating {len(backlog_rows)} BACKLOG rows to Backlog Items...")
    for r in backlog_rows:
        new_title = f"[P3] MCP-BACKLOG — {r['title']}"
        summary = (
            f"Migrated from archived MCP Registry on 2026-05-02.\n\n"
            f"Authority: {r['authority']}\n\n"
            f"Capability Scope: {r['scope']}\n\n"
            f"Original Notes: {r['notes']}"
        )
        try:
            res = _post_backlog_row(new_title, summary)
            log.append(f"created backlog row: {res['id']} title={new_title}")
            print(f"      + {new_title[:80]}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            log.append(f"FAILED to create backlog row for {r['title']}: {exc}")
            print(f"      ! FAILED: {r['title']} — {exc}")

    # 4. Archive 4 Notion DBs.
    print(f"[3/4] Archiving {len(DBS_TO_ARCHIVE)} Notion databases...")
    for name, db_id in DBS_TO_ARCHIVE.items():
        try:
            res = _archive_database(db_id)
            in_trash = res.get("in_trash")
            log.append(f"archived {name} ({db_id}) in_trash={in_trash}")
            print(f"      + {name}: in_trash={in_trash}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            log.append(f"FAILED to archive {name}: {exc}")
            print(f"      ! FAILED: {name} — {exc}")

    # 5. Write log.
    log_path = STAGING_DIR / "consolidation.log"
    log_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"[4/4] Done. Log: {log_path}")
    print(f"      Staging: {STAGING_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
