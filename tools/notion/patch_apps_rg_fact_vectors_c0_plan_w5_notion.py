#!/usr/bin/env python3
"""One-shot: PATCH Notion Plans row for apps-rg-fact-vectors-c0-notion-d4e8c2 (W5 complete).

Run from repo root with NOTION_TOKEN (or NOTION_API_KEY) set.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

PAGE_ID = "36127693-f55c-8153-9859-f4eeccdf1846"
TIMEOUT = 30.0

SUMMARY = (
    "W5 done: run_contract_gates runs SEED-RG-FV before CHECK-RG-FACT-VECTORS; "
    "idempotent smoke ingest at default Chroma path. W1–W4 unchanged. Readiness gate "
    "stays advisory unless APPS_RG_FACT_VECTORS_FAIL_CLOSED=1."
)

AI_SUMMARY = (
    "- W5: ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py (fixture: "
    "tests/fixtures/apps_rg/fact_vectors_c0_smoke.chroma_input)\n"
    "- run_contract_gates: SEED-RG-FV gate + 900s timeout; --gate CHECK-RG-FACT-VECTORS "
    "runs seed prerequisite\n"
    "- Bypass seed: APPS_RG_SEED_FACT_VECTORS_BYPASS=1\n"
    "- Disk SSOT: .claude/plans/apps-rg-fact-vectors-c0-notion-d4e8c2.md"
)


def _patch() -> None:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN (or NOTION_API_KEY) not set", file=sys.stderr)
        sys.exit(2)

    url = f"{NOTION_BASE}/pages/{PAGE_ID}"
    payload = {
        "properties": {
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:1990]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:1990]}}]},
        }
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8", errors="replace")[:500], file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"Patched Notion page {PAGE_ID} Summary + AI Summary.")


if __name__ == "__main__":
    _patch()
