"""Flip 15 codebase-validated Retired Plans rows to Completed.

12 Tier 1 (CI gate exists OR successor delivered) + 3 Tier 2 (specific
codebase artifacts confirmed). 5 originally proposed Tier 2 candidates
held back: 2 confirmed truly abandoned (llm-judge-hardening-followups
and anthropic-alignment-followups), 3 promoted on evidence.

Resolves real page_ids from the Notion dump file -- no fabricated ids.
Patches Status -> Completed AND rewrites AI Summary to reflect delivery.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DUMP = Path("C:/Users/amita/AppData/Local/Temp/windsurf/mcp_output_4570bbeb1534c8d5.txt")
_NOTION_VERSION = "2025-09-03"

# slug -> new AI Summary (<= 14 words, scope + delivery proof)
FLIPS: dict[str, str] = {
    # --- Tier 1: 12 high-confidence ---
    "d-bucket-burndown-e4f2c9":
        "Decomposed: 3 per-wave child plans live (w2/w3/w4-burndown).",
    "adg-ci-gate-hardening-deferred-b4e3c9":
        "Folded into adg-three-bucket-unified W3-W6; CI gates shipped.",
    "adg-ci-spine-delegation-gate-438b16":
        "Shipped: check_apps_spine_delegation.py strict, violations=0 verified.",
    "three-bucket-otel-view-5db409":
        "Folded into adg-three-bucket-unified W2; OTel-view SSOT shipped.",
    "three-bucket-gap-remediation-069806":
        "Registry resolver shipped; residue folded into adg-three-bucket-unified.",
    "adg-three-bucket-authority-model-7e2a91":
        "Authority model carried into adg-three-bucket-unified W1.",
    "query-progress-bar-backlog":
        "check_query_progress_bar.py CI gate enforces invariant permanently.",
    "test-coverage-backlog-f8f5a7":
        "check_test_harness_coverage.py ratcheting gate owns no-regression.",
    "terminal-cleanup-burndown-a7f2d1":
        "check_terminal_cleanup.py CI gate owns no-regression invariant.",
    "p2-burndown-wave-9e4c17":
        "P2 ratchet verified MEDIUM=0 at ceiling=0; gate owns invariant.",
    "p2-antipattern-burndown-ae0549":
        "P2 ratchet verified MEDIUM=0 at ceiling=0; gate owns invariant.",
    "p1-antipattern-burndown-8a3f2b":
        "P1 anti-pattern ratcheting gate owns no-regression invariant.",
    # --- Tier 2: 3 promoted on codebase evidence ---
    "prompt-reception-followups-a7b3c4":
        "Delivered: tests/golden/prompt_reception + core_synthesis_executor.py shipped.",
    "l0-prompt-retrieval-deferred-triage-d3e8f1":
        "Delivered: guardian exemptions on named catches + test imports fixed.",
    "cache-r1ab-residuals-8c4e2a":
        "Delivered: corpus_version plumbed in SQLite; BGE-M3 model active.",
}


def _token() -> str | None:
    return os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def _patch(token: str, page_id: str, status: str, ai_summary: str) -> None:
    payload = {
        "properties": {
            "Status": {"select": {"name": status}},
            "AI Summary ": {
                "rich_text": [{"type": "text", "text": {"content": ai_summary}}]
            },
        }
    }
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def main() -> int:
    token = _token()
    if not token:
        print("ERROR: NOTION_API_KEY / NOTION_TOKEN not set")
        return 2

    data = json.loads(DUMP.read_text(encoding="utf-8"))
    by_slug: dict[str, str] = {}
    for r in data["results"]:
        title = r["properties"]["Slug"]["title"]
        slug = title[0]["plain_text"] if title else ""
        if slug:
            by_slug[slug] = r["id"]

    ok = failed = missing = 0
    for slug, ai in FLIPS.items():
        page_id = by_slug.get(slug)
        if not page_id:
            print(f"MISS  {slug}: not in dump")
            missing += 1
            continue
        try:
            _patch(token, page_id, "Completed", ai)
            print(f"OK    {slug}: {ai}")
            ok += 1
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:200]
            print(f"FAIL  {slug}: HTTP {exc.code} {body}")
            failed += 1
        except urllib.error.URLError as exc:
            print(f"FAIL  {slug}: {exc.reason}")
            failed += 1
        time.sleep(0.12)

    print()
    print(f"Done: ok={ok} missing={missing} failed={failed} (of {len(FLIPS)} planned)")
    return 0 if failed == 0 and missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
