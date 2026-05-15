#!/usr/bin/env python3
"""
infer_and_score_unscored.py — One-shot helper to infer Layer / Surface / Fan-In
for Notion backlog rows whose P-Band is empty AND whose required scorer inputs
are not populated. Uses direct ADG SQLite (no MCP dependency) to compute fan-in
from Files In Scope, infers Layer from file paths, and infers Surface from
title/evidence keywords. Then runs the deterministic deferred-scope scorer and
patches Notion in-place.

Coverage gap % is set to 100 for every row (these are deferred items with no
coverage by definition — matches what post_cursor_agent_deferred_scope_capture does).

Dry-run by default; pass --apply to patch Notion.

Usage:
    python tools/priority/infer_and_score_unscored.py           # dry-run
    python tools/priority/infer_and_score_unscored.py --apply   # patch
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.priority.deferred_scope_scorer import score_deferred_scope  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_infer_and_score_audit.jsonl"

LAYER_PATH_RE = re.compile(r"agentic_core/(L[0-6])_\w+/")
# Priority order — smaller layer number = more critical (higher multiplier).
LAYER_PRIORITY = {"L0": 0, "L5": 1, "L3": 2, "L4": 3, "L1": 4, "L2": 5, "L6": 6}

# Surface inference — keyword-based on title + Files In Scope + Success Criteria.
# Blocking Items field is intentionally excluded — it carries Author-Gate
# boilerplate ("Author-Gate", "safety", "rollback") that over-matches Security.
# Order matters: first match wins; most specific surfaces listed first.
SURFACE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Security", [
        "thought redactor", "rationale publication", "guardrail", "policy",
        "threat model", "secret", "credential", "oidc", "cosign", "signing",
    ]),
    ("Write", [
        "uwg", "write-", "write_", "mutation", "commit ", "apply-patch",
        "evidence-resolver", "payload-emit",
    ]),
    ("State", [
        "cache", "memory tree", "hot store", "sqlite", "redis", "threshold",
        "key harden", "semantic cache", "cache-prefix",
    ]),
    ("Observability", [
        "metric", "otel", "telemetry", "dashboard", "grafana", "billing",
        "observab", "registry sync", "doc + registry", "overhead metric",
    ]),
    ("Execution", [
        "adapter", "gateway", "dispatch", "orchestrat", "router", "routing-meta",
        "compressor", "summariz", "validator", "fence", "slot", "assembly",
        "mixin", "planner", "prompt envelope", "agentspec",
    ]),
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
    raise RuntimeError("NOTION_TOKEN not set")


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
                result: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
                return result
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


def _latest_adg_sqlite() -> Path:
    candidates = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    if not candidates:
        raise RuntimeError("No ADG snapshot found under artifacts/adg/")
    return candidates[-1]


def _plain_text(prop: dict) -> str:
    return "".join(p.get("plain_text", "") for p in prop.get("rich_text", [])).strip()


def fetch_unscored_triage(tok: str) -> list[dict]:
    """Rows where P-Band is empty AND Layer is empty (needs inference)."""
    body: dict = {
        "page_size": 100,
        "filter": {
            "and": [
                {"property": "P-Band", "select": {"is_empty": True}},
                {"property": "Layer", "select": {"is_empty": True}},
            ]
        },
    }
    resp = _http("POST", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query", tok, body)
    return resp.get("results", [])


def infer_layer(files_in_scope: str) -> str:
    matches = LAYER_PATH_RE.findall(files_in_scope)
    if not matches:
        return "L2"  # default: execution / app surface
    # Pick the most critical layer (lowest LAYER_PRIORITY rank).
    return min(matches, key=lambda layer: LAYER_PRIORITY.get(layer, 99))


def infer_surface(haystack: str) -> str:
    lc = haystack.lower()
    for surface, keywords in SURFACE_KEYWORDS:
        if any(kw in lc for kw in keywords):
            return surface
    return "Execution"


def infer_fan_in(files_in_scope: str, sqlite_path: Path) -> int:
    """Sum of incoming 'imports' edges for every file path mentioned in scope."""
    if not files_in_scope.strip():
        return 0
    # Extract file paths — tolerate prose like "foo.py (new), bar.py (wire-in)".
    paths = re.findall(r"[A-Za-z0-9_./\\-]+\.py", files_in_scope)
    if not paths:
        return 0
    con = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        total = 0
        for raw in paths:
            # Normalize separators — ADG stores forward-slashed rel paths.
            path = raw.replace("\\", "/").lstrip("./")
            cur.execute(
                """
                SELECT COUNT(*) FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                WHERE n.resolved_path = ? AND e.relation_type = 'imports'
                """,
                (path,),
            )
            row = cur.fetchone()
            total += int(row[0]) if row else 0
        return total
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer + score unscored Notion rows")
    parser.add_argument("--apply", action="store_true", help="Patch Notion (default: dry-run)")
    args = parser.parse_args()
    dry_run = not args.apply

    tok = _token()
    sqlite_path = _latest_adg_sqlite()
    rows = fetch_unscored_triage(tok)

    patched: list[dict] = []
    skipped: list[dict] = []

    for row in rows:
        props = row["properties"]
        page_id = row["id"]
        title_parts = props.get("Phase Title", {}).get("title", [])
        title = "".join(p.get("plain_text", "") for p in title_parts).strip()
        files_in_scope = _plain_text(props.get("Files In Scope", {}))
        blocking = _plain_text(props.get("Blocking Items", {}))
        parent_summary = _plain_text(props.get("Parent Plan Summary", {}))
        success = _plain_text(props.get("Success Criteria", {}))

        if not files_in_scope:
            skipped.append({"page_id": page_id, "title": title, "reason": "no_files_in_scope"})
            continue

        # Blocking Items deliberately excluded — see SURFACE_KEYWORDS comment.
        _ = blocking  # retained for potential audit / future use
        haystack = " ".join([title, files_in_scope, success, parent_summary])
        layer = infer_layer(files_in_scope)
        surface = infer_surface(haystack)
        fan_in = infer_fan_in(files_in_scope, sqlite_path)
        coverage_gap_pct = 100.0

        try:
            result = score_deferred_scope(
                layer=layer,
                fan_in=fan_in,
                surface=surface,
                coverage_gap_pct=coverage_gap_pct,
            )
        except (ValueError, KeyError) as exc:
            skipped.append({"page_id": page_id, "title": title, "reason": f"scorer_error: {exc}"})
            continue

        patched.append({
            "page_id": page_id,
            "title": title,
            "layer": layer,
            "surface": surface,
            "fan_in": fan_in,
            "coverage_gap_pct": coverage_gap_pct,
            "impact": result.impact_score,
            "band": result.band,
        })

        if not dry_run:
            patch_props = {
                "P-Band": {"select": {"name": result.band}},
                "Layer": {"select": {"name": layer}},
                "Surface": {"select": {"name": surface}},
                "Fan-In": {"number": fan_in},
                "Coverage Gap %": {"number": coverage_gap_pct},
                "Impact Score": {"number": round(result.impact_score, 2)},
                "Last Scored": {"date": {"start": datetime.now(timezone.utc).date().isoformat()}},
            }
            _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, {"properties": patch_props})

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run" if dry_run else "apply",
        "adg_snapshot": sqlite_path.name,
        "rows_inspected": len(rows),
        "patched": len(patched),
        "skipped": len(skipped),
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print(json.dumps(summary, indent=2))
    print()
    print(f"{'TITLE':<60} {'LAYER':<6} {'SURFACE':<14} {'FAN_IN':>7} {'IMPACT':>8} {'BAND':>5}")
    print("-" * 105)
    for p in patched:
        short = (p["title"][:57] + "...") if len(p["title"]) > 60 else p["title"]
        print(f"{short:<60} {p['layer']:<6} {p['surface']:<14} {p['fan_in']:>7} {p['impact']:>8.2f} {p['band']:>5}")
    if skipped:
        print()
        print("SKIPPED:")
        for s in skipped:
            print(f"  {s['title']}  ({s['reason']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
