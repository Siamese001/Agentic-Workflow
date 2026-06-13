#!/usr/bin/env python3
"""Create visible Notion child page for windsurf-gha metadata reconcile receipt."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PLAN_PAGE_ID = "36927693-f55c-81eb-a9a1-d9955c280b83"
CHILD_TITLE = "Windsurf GHA Metadata Reconcile Receipt (2026-05-25)"
DISK_RECEIPT = "docs/reports/cursor/windsurf_gha_metadata_reconcile_20260525_receipt.md"


def _rt(text: str) -> dict:
    return {"type": "text", "text": {"content": text[:2000]}}


def _paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [_rt(text)]}}


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [_rt(text)]},
    }


def _create_child_page(token: str) -> str:
    import urllib.error
    import urllib.request

    children = [
        _paragraph(
            "Auditor-safe metadata reconcile for plan windsurf-gha-cutover-d9f2a7. "
            "Migration scope COMPLETE; global contract gate PARTIAL (external graph_layer)."
        ),
        _paragraph("Disk SSOT: docs/reports/cursor/windsurf_gha_metadata_reconcile_20260525_receipt.md"),
        _bullet("MIGRATION_SCOPE_STATUS: COMPLETE (W0–W5 + W5.D1–D4)"),
        _bullet("GLOBAL_CONTRACT_GATE_STATUS: PARTIAL_EXTERNAL_BLOCKER (6 plan_type violations)"),
        _bullet("GOVERNANCE_CERTIFICATION_STATUS: PARTIAL — not full repo green"),
        _bullet("W1.D1 full docs/archive/windsurf/legacy-tree/ deletion: OUT_OF_BAND (separate plan)"),
        _paragraph("Proof artifacts (repo paths):"),
        _bullet("docs/reports/cursor/windsurf_gha_inventory.json"),
        _bullet("docs/reports/cursor/windsurf_gha_cutover_closeout.md"),
        _bullet("docs/reports/cursor/windsurf_gha_deferred_scope_closeout.md"),
        _bullet("artifacts/governance/windsurf_deletion_readiness.json"),
        _paragraph("DoD-4: python ops_scripts/ci/run_contract_gates.py -> exit 1"),
        _bullet("exec-summary-l2-x1d-input-parity-c4f8e1.md (unknown plan_type remediation)"),
        _bullet("exec-summary-operator-ship-a3f7c2.md (unknown plan_type product)"),
        _bullet("exec-summary-targeting-ingress-u0-b8e4f1.md (unknown plan_type feature)"),
        _bullet("exec-summary-targeting-wiring-closeout-b9e2a4.md (unknown plan_type bugfix)"),
        _bullet("exec-summary-x1d-dimension-verdicts-e8f4a2.md (unknown plan_type product)"),
        _bullet("l5-pa-orchestrator-ref-forward-c7e4a1.md (unknown plan_type bugfix)"),
        _paragraph("Plans DB parent: windsurf-gha-cutover-d9f2a7 (Status Completed). Open this page from the parent row."),
    ]
    payload = {
        "parent": {"page_id": PLAN_PAGE_ID},
        "properties": {"title": {"title": [_rt(CHILD_TITLE)]}},
        "children": children,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["id"])


def _patch_plan_row(token: str, child_url: str, child_id: str) -> None:
    import urllib.error
    import urllib.request

    summary = (
        "COMPLETED + metadata reconcile 2026-05-25. "
        f"OPEN NOTION RECEIPT: {CHILD_TITLE} (child page under this row). "
        "DoD-4 PARTIAL graph_layer external. Disk: "
        + DISK_RECEIPT
    )
    ai = (
        "NOTION RECEIPT PAGE (open this plan row → subpage): "
        + CHILD_TITLE
        + "\n- Metadata reconcile 2026-05-25: phase ledger DONE\n"
        "- MIGRATION_SCOPE_STATUS=COMPLETE\n"
        "- GLOBAL_CONTRACT_GATE_STATUS=PARTIAL_EXTERNAL_BLOCKER\n"
        "- W1.D1 tree deletion OUT_OF_BAND\n"
        "- Disk: docs/reports/cursor/windsurf_gha_metadata_reconcile_20260525_receipt.md"
    )
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": ai[:2000]}}]},
            "Waiting For": {
                "rich_text": [{"text": {"content": f"Receipt subpage: {child_url}"}}],
            },
        }
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{PLAN_PAGE_ID}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        json.loads(resp.read().decode("utf-8"))
    print(json.dumps({"ok": True, "child_page_id": child_id, "child_url": child_url, "parent": PLAN_PAGE_ID}))


def main() -> int:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none

    token = get_notion_bearer_token_or_none()
    if not token:
        print("BLOCKED: NOTION_TOKEN missing", file=sys.stderr)
        return 1
    child_id = _create_child_page(token)
    child_url = f"https://www.notion.so/{child_id.replace('-', '')}"
    _patch_plan_row(token, child_url, child_id)
    print(f"NOTION_RECEIPT_PAGE: {child_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
