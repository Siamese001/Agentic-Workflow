#!/usr/bin/env python3
"""Post ADR-078 + ADR-079 rows to the Notion ADR Registry.

W3 P3.5 of ``adg-three-bucket-unified-c4f8e2``. Idempotent — checks for an
existing row by ADR ID before posting.

NOTION_TOKEN resolved from env or .env per snapshot_renderer pattern.

Usage:
    python tools/notion/post_adrs_078_079.py --dry-run
    python tools/notion/post_adrs_078_079.py --execute
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"

ADR_REGISTRY_DS_ID = "e59d7640-dc09-48f9-8bdc-b0c94bf98c2a"
ADR_REGISTRY_DB_ID = "6ed25e12-bd92-4352-ac7a-3a971311f024"

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "post_adrs_078_079_audit.jsonl"

ADR_PAYLOADS: list[dict[str, Any]] = [
    {
        "adr_id": "ADR-078",
        "title": "apps_* Spine Delegation Invariant",
        "filename": "ADR-078-apps-spine-delegation.md",
        "status": "Accepted",
        "decision_date": "2026-04-30",
        "impact_layers": ["L_OPS"],
        "summary": (
            "Every apps_*/ top-level package MUST have ≥1 import edge into the "
            "agentic_core spine (L0_routing | L1_cognition | L2_execution). "
            "Catches the forbidden 'apps_* standalone mini-runtime' mode via "
            "direct ADG SQLite query (§28). Default advisory; W5 P5.4 flips "
            "strict. Live evidence: apps_underwriting_ai flagged (0/693 "
            "imports into spine). Allowlist with per-package reason + ISO "
            "expires; bypass via APPS_SPINE_DELEGATION_GATE_BYPASS=1."
        ),
        "deciders": ["Cursor Agent", "operator"],
    },
    {
        "adr_id": "ADR-079",
        "title": "L2 Agent ↔ ADG Graph-Layer Integration Contract",
        "filename": "ADR-079-l2-agent-graph-layer-contract.md",
        "status": "Accepted",
        "decision_date": "2026-04-30",
        "impact_layers": ["L2", "L3", "L6"],
        "summary": (
            "Sanctioned consumption contract for L2 runtime agents reading the "
            "ADG graph layer (mv_*, semantic edges, P-views) via the W3 P3.3 "
            "MCP tools or the in-process ADGService. Forbidden: direct "
            "sqlite3.connect(), writes, ADGResponse-envelope bypass. Latency "
            "contract: warm <50ms / cold <500ms. Three-bucket "
            "__adg_consumer_mode__ declaration mandatory. Feature-flag "
            "fallback pattern for graceful degradation. Layer-gravity rule: "
            "L2→L6 downward consumption allowed; reverse forbidden. Pilot "
            "consumer: ExecutionOrchestrator._populate_d2_cache (W5 P5.3). "
            "Pairs with ADR-074 + ADR-078."
        ),
        "deciders": ["Cursor Agent", "operator"],
    },
]


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set (env or .env)")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 2:
                time.sleep(int(err.headers.get("Retry-After", "2")))
                continue
            body_txt = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_txt}") from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _query_existing(tok: str, adr_id: str) -> str | None:
    """Return existing page_id if a row with this ADR ID already exists."""
    body = {
        "filter": {
            "or": [
                {"property": "ADR ID", "rich_text": {"equals": adr_id}},
                {"property": "ADR ID", "title": {"equals": adr_id}},
            ]
        },
        "page_size": 5,
    }
    # Try with each filter shape — schemas vary.
    for shape in (
        {"property": "ADR ID", "rich_text": {"equals": adr_id}},
        {"property": "ADR ID", "title": {"equals": adr_id}},
        {"property": "Name", "title": {"contains": adr_id}},
    ):
        try:
            resp = _http(
                "POST",
                f"{NOTION_API}/data_sources/{ADR_REGISTRY_DS_ID}/query",
                tok,
                {"filter": shape, "page_size": 5},
            )
            results = resp.get("results", [])
            if results:
                return str(results[0]["id"])
        except RuntimeError:
            continue
    return None


def _discover_schema(tok: str) -> dict[str, str]:
    """Return {property_name: type} from the ADR Registry data source."""
    resp = _http("GET", f"{NOTION_API}/data_sources/{ADR_REGISTRY_DS_ID}", tok)
    return {name: spec.get("type", "?") for name, spec in resp.get("properties", {}).items()}


def _build_properties(adr: dict[str, Any], schema: dict[str, str]) -> dict[str, Any]:
    """Construct properties payload matching whatever the live schema accepts.

    The ADR Registry's exact column shape varies; we map best-effort using
    common property names (ADR ID, Title/Name, Status, Decision Date,
    Filename, Summary, Impact Layers, Deciders) and fall through to whatever
    title property exists.
    """
    props: dict[str, Any] = {}

    # Find the title property (always exactly one per Notion DB).
    title_prop = next((n for n, t in schema.items() if t == "title"), None)
    if title_prop is None:
        raise RuntimeError(f"ADR Registry has no title property; schema={schema}")
    title_text = f"{adr['adr_id']} — {adr['title']}"
    props[title_prop] = {"title": [{"type": "text", "text": {"content": title_text}}]}

    # Optional rich_text fields by common name.
    optional_rich_text = {
        "ADR ID": adr["adr_id"],
        "Filename": adr["filename"],
        "Summary": adr["summary"],
    }
    for name, value in optional_rich_text.items():
        if schema.get(name) == "rich_text":
            props[name] = {"rich_text": [{"type": "text", "text": {"content": value[:1900]}}]}

    # Status select.
    if schema.get("Status") == "select":
        props["Status"] = {"select": {"name": adr["status"]}}

    # Decision Date.
    if schema.get("Decision Date") == "date":
        props["Decision Date"] = {"date": {"start": adr["decision_date"]}}

    # Impact Layers — multi_select if present.
    if schema.get("Impact Layers") == "multi_select":
        props["Impact Layers"] = {
            "multi_select": [{"name": layer} for layer in adr["impact_layers"]]
        }
    elif schema.get("Impact Layers") == "rich_text":
        props["Impact Layers"] = {
            "rich_text": [{"type": "text", "text": {"content": ", ".join(adr["impact_layers"])}}]
        }

    # Deciders — multi_select or rich_text.
    if schema.get("Deciders") == "multi_select":
        props["Deciders"] = {
            "multi_select": [{"name": d} for d in adr["deciders"]]
        }
    elif schema.get("Deciders") == "rich_text":
        props["Deciders"] = {
            "rich_text": [{"type": "text", "text": {"content": ", ".join(adr["deciders"])}}]
        }

    return props


def post_adr(tok: str, adr: dict[str, Any], schema: dict[str, str], dry_run: bool) -> dict:
    existing = _query_existing(tok, adr["adr_id"])
    if existing:
        print(f"[{adr['adr_id']}] already exists at {existing} — skipping POST")
        _audit({"adr": adr["adr_id"], "action": "skip_existing", "page_id": existing})
        return {"action": "skip", "page_id": existing}

    body = {
        "parent": {"type": "database_id", "database_id": ADR_REGISTRY_DB_ID},
        "properties": _build_properties(adr, schema),
    }

    if dry_run:
        print(f"[{adr['adr_id']}] DRY-RUN — would POST {len(body['properties'])} properties")
        for k in body["properties"]:
            print(f"     - {k}")
        _audit({"adr": adr["adr_id"], "action": "dry_run_post"})
        return {"action": "dry_run"}

    resp = _http("POST", f"{NOTION_API}/pages", tok, body)
    page_id = resp["id"]
    print(f"[{adr['adr_id']}] posted: {page_id}")
    _audit({"adr": adr["adr_id"], "action": "created", "page_id": page_id})
    return {"action": "created", "page_id": page_id}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    dry_run = args.dry_run

    tok = _token()
    print(f"=== Posting ADR-078 + ADR-079 to ADR Registry ({'DRY-RUN' if dry_run else 'EXECUTE'}) ===")

    schema = _discover_schema(tok)
    print(f"Discovered schema: {sorted(schema.keys())}")

    results = []
    for adr in ADR_PAYLOADS:
        results.append(post_adr(tok, adr, schema, dry_run))
        time.sleep(0.5)

    print()
    print("=== Summary ===")
    for adr, res in zip(ADR_PAYLOADS, results):
        print(f"  {adr['adr_id']}: {res}")
    print(f"  Audit log: {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
