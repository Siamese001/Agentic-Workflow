#!/usr/bin/env python3
"""Close out l0-routing-v15-only-cutover-c9e2f1 in Notion (W4 final wave)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "l0-routing-v15-only-cutover-c9e2f1"
PLAN_PATH = ".claude/plans/l0-routing-v15-only-cutover-c9e2f1.md"
PAGE_ID = "36727693-f55c-81e9-b053-ef58e79f02fb"

SUMMARY = (
    "COMPLETE W1–W4 (final wave W4 2026-05-24): v15-only L0 cutover. v12 archived; "
    "e2e harness 67/67; proof bundles l0_v15_e2e_proof_bundle_20260525 + route_coverage. "
    "Receipt: docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md. "
    "No further waves in plan."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETE — all waves W1–W4 done (W4 = last wave)
- W4: Fixed test_runtime_proof_harness REPO_ROOT + PYTHONPATH; 67/67 pytest; CLI bundles PASS
- Scenarios: RC-HITL (HITL_POSTURE), managed workflow, UWG — acceptance_status PASS
- Gates: check_l0_v15_no_v12_hotpath, check_l0_parent_invariants, check_replay_proof PASS
- PARTIAL: full run_contract_gates (6 unrelated plan plan_type rows — not L0)
- W3 receipt: l0_v12_retirement_w3_receipt_20260525.md
- W4 receipt: l0_v15_only_cutover_w4_receipt_20260525.md
- DEFERRED_SCOPE: none"""

W4_COMMENT = """W4 closeout (final wave) — 2026-05-24

This plan has no W5. W4 closed the deferred e2e/replay proof seam after W3 v12 hot-path retirement.

Delivered:
• E2E harness: 67/67 (fixed REPO_ROOT parents[3] + PYTHONPATH for 99.8 CLI subprocesses)
• Proof bundles on disk: l0_v15_e2e_proof_bundle_20260525, l0_v15_route_coverage_proof_20260525 (acceptance_status PASS; RC-HITL / HITL_POSTURE included)
• L0 CI: check_l0_v15_no_v12_hotpath, check_l0_parent_invariants (8/8), check_replay_proof PASS
• Wireup + v15 unit tests green

Out of scope / honest partial:
• Full-repo run_contract_gates still fails on check_graph_layer_evidence (6 exec-summary/L5 plan_type taxonomy rows) — not L0 routing

Receipts:
• W3: docs/reports/agentic_core/l0_v12_retirement_w3_receipt_20260525.md
• W4: docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md

Plan file: .claude/plans/l0-routing-v15-only-cutover-c9e2f1.md — PLAN_STATUS COMPLETE, DEFERRED_SCOPE none."""


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
            "Waiting For": {"rich_text": []},
        }
    }
    body = json.dumps(payload).encode("utf-8")
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "patch_error": str(exc)}), file=sys.stderr)
        return False


def _post_comment(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    # Notion comments API: chunk if needed (2000 char rich_text limit per block)
    chunks = [W4_COMMENT[i : i + 1900] for i in range(0, len(W4_COMMENT), 1900)]
    rich_text = [{"type": "text", "text": {"content": c}} for c in chunks]
    payload = {
        "parent": {"page_id": page_id},
        "rich_text": rich_text,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.notion.com/v1/comments",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "comment_error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    patched = _patch_page(PAGE_ID)
    commented = _post_comment(PAGE_ID)
    notion_url = f"https://www.notion.so/{PAGE_ID.replace('-', '')}"
    out = {
        "ok": patched,
        "patched": patched,
        "comment_posted": commented,
        "page_id": PAGE_ID,
        "notion_url": notion_url,
        "slug": SLUG,
        "status": "Completed",
        "last_wave": "W4",
    }
    print(json.dumps(out, indent=2))
    print(f"PLAN_COMPLETED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={PAGE_ID}")
    return 0 if patched else 1


if __name__ == "__main__":
    raise SystemExit(main())
