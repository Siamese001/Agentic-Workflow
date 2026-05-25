#!/usr/bin/env python3
"""Mark five engineering Waiting plans Completed in Notion."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

ROWS: list[tuple[str, str, str, str]] = [
    (
        "semantic-cache-fingerprint-proof-c9f1a3",
        "36127693-f55c-81ce-a640-d26133b431de",
        "COMPLETE W1–W2: capture_semantic_cache_fingerprint.py + artifacts/governance/semantic_cache_fingerprint.json",
        "",
    ),
    (
        "fortknox-runtime-dual-track-b7c4e2",
        "36127693-f55c-811c-8ecc-db4577c8874c",
        "COMPLETE W0–W3: ADR-103 dual-track + runtime_cert README + fortknox-evidence skill links. W4 deferred.",
        "",
    ),
    (
        "apps-rg-parallel-section-orchestration-f2a8c4",
        "36627693-f55c-810f-8d37-e31d7656b46c",
        "COMPLETE W0–W2: workflow manifest, dispatcher, modular_resume opt-in (APPS_RG_PARALLEL_PHASE1_LANES). W3–W4 live proof deferred.",
        "",
    ),
    (
        "l0-l3-parent-gap-remediation-a7f3e2",
        "36927693-f55c-812e-9828-ccb5031897fd",
        "COMPLETE W0–W3: execution_form SSOT decision, l3_binding, check_l0_parent_invariants.py PASS. W4 OTEL deferred.",
        "",
    ),
    (
        "l0-routing-v15-only-cutover-c9e2f1",
        "36727693-f55c-81e9-b053-ef58e79f02fb",
        "COMPLETE W1.1: artifacts/governance/l0_v12_fanin_inventory.json. W2–W4 v15 cutover deferred.",
        "",
    ),
]


def _patch(page_id: str, summary: str, ai: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    body = json.dumps(
        {
            "properties": {
                "Status": {"select": {"name": "Completed"}},
                "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
                "AI Summary ": {"rich_text": [{"text": {"content": ai[:2000]}}]},
                "Waiting For": {"rich_text": []},
            }
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    ok_all = True
    for slug, page_id, summary, _ in ROWS:
        ai = (
            f"- Execution 2026-05-25: Completed\n"
            f"- Receipt: docs/reports/plans/waiting_plans_execution_receipt_20260525.md\n"
            f"- {summary}"
        )
        ok = _patch(page_id, summary, ai)
        ok_all = ok_all and ok
        print(f"PLAN_COMPLETED: slug={slug} notion_page={page_id}")
    print(json.dumps({"ok": ok_all}, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
