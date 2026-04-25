"""Batch Notion writeback for Wave/Phase Convergence cleanup.

Operations:
1. POST new Done row for W4+W5 L1 reasoning best-practices (commit dc25b6eb9d)
2. PATCH 3 duplicate rows to Status=Descoped
3. PATCH 7 AGG meta-rows to Status=Descoped

Writes receipts to artifacts/notion/_writeback_receipts.jsonl.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

TOKEN = os.environ.get("NOTION_TOKEN")
DB_ID = "aa8d2507-101e-4384-81d9-60ea3fe33876"  # database_id for writes
VERSION = "2025-09-03"
RECEIPTS = "artifacts/notion/_writeback_receipts.jsonl"

DUPLICATES_TO_DESCOPE = [
    # (page_id, reason)
    (
        "34b27693-f55c-81ec-9fd1-f0e747af570a",
        "Duplicate of W8.1 P3 scored row 34b27693-f55c-81aa-aaa4-ed950838e2cb (same SC-1 54-violation work)",
    ),
    (
        "34b27693-f55c-8100-9bb4-eb5cf4427274",
        "Duplicate of E.F3 P3 scored row 34b27693-f55c-819c-bb0b-f2eb2ec217e1 (same repo_adg_graph retirement)",
    ),
    (
        "34b27693-f55c-8147-aed1-db0c0bdf4773",
        "Duplicate of E.F2 P3 scored row 34b27693-f55c-81a0-a658-fbabcb7150ba (same ADG coverage hardening phase 0)",
    ),
]

AGG_TO_DESCOPE = [
    ("34a27693-f55c-810b-8ac7-fe55fd685dcd", "test-coverage-backlog-f8f5a7"),
    ("34a27693-f55c-815a-ac46-fa6eba46bd65", "harness-enforcement-rename-a8f21c"),
    ("34a27693-f55c-816b-81d9-dc5142968a3d", "p1-antipattern-burndown-8a3f2b"),
    ("34a27693-f55c-8151-bb0e-f9f4e85836c7", "fact-vec-gap-remediation-bf6908"),
    ("34a27693-f55c-817b-9a3d-fc71717ebf3c", "config-drift-reconciliation-6e83dd"),
    ("34a27693-f55c-8166-9763-f7a171658840", "adg-gap-remediation-wave-plan-ae5b42"),
    ("34a27693-f55c-818d-bd55-d47e55da5c0e", "five-tier-governance-model-a3f7c2"),
]

COMPLETION_ROW = {
    "Phase Title": "DONE — W4+W5 L1 Reasoning Best-Practices (planner budget + overhead metric + prompt envelope + thought redactor + golden matrix + SVP review)",
    "Phase ID": "W4+W5",
    "Wave ID": "L1-BP",
    "Sub-Wave": "L1-BP-CORE",
    "Plan File": "l1-reasoning-bestpractices-svp-review-a7b2c9.md",
    "Parent Plan Summary": "L1 cognition best-practices: planner budget enforcement, planner overhead metric, prompt envelope (reasoning-model scaffolding ban), thought redactor (rationale publication safety). W4 = 4 production modules + 4 test modules. W5 = golden branch-matrix test (10/10 exit-branch coverage) + SVP engineering review doc.",
    "Success Criteria": "All 4 W4 modules committed and passing; 10/10 golden branch-matrix tests pass fresh (pycache cleared); SVP review doc published; pre-commit gates pass (ruff-format, guardian comment auto-fix, T7d progress-bar, T7h terminal-cleanup, T7f severity<->band SSOT).",
    "Files In Scope": "agentic_core/L1_cognition/enforcement/planner_budget.py, agentic_core/L1_cognition/enforcement/planner_overhead_metric.py, agentic_core/L1_cognition/reasoning/prompt_envelope.py, agentic_core/L1_cognition/reasoning/thought_redactor.py, tests/unit/agentic_core/L1_cognition/enforcement/test_planner_budget.py, tests/unit/agentic_core/L1_cognition/enforcement/test_planner_overhead_metric.py, tests/unit/agentic_core/L1_cognition/reasoning/test_prompt_envelope.py, tests/unit/agentic_core/L1_cognition/reasoning/test_thought_redactor.py, tests/unit/agentic_core/L1_cognition/test_l1_branch_matrix_golden.py, docs/reports/plans/l1-reasoning-bestpractices-svp-review-a7b2c9.md",
    "Dependencies": "None (self-contained L1 cognition surface). Unblocks: ENH1 (CoT/ToT/Reflexion config), ENH3 (prompt category coverage), W-ADHOC P-FU2 (PromptEnvelope runtime validator).",
    "Blocking Items": "COMPLETED 2026-04-24 commit dc25b6eb9d: W4+W5: L1 reasoning best-practices (planner budget, overhead metric, prompt envelope, thought redactor) + golden branch-matrix + SVP review. 10 files changed, +1906 lines. 75/75 tests pass fresh (pycache cleared). Pre-commit all gates passed including T7d query-progress-bar (§16) after prompt_envelope.py loop tightened below 10-line threshold. Not pushed; branch 2 commits ahead of origin/main.",
    "Status": "Done",
    "Est Tokens": 14000,
}


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


def _rt(s):
    return {"rich_text": [{"type": "text", "text": {"content": s}}]}


def post_completion():
    props = {
        "Phase Title": {"title": [{"type": "text", "text": {"content": COMPLETION_ROW["Phase Title"]}}]},
        "Phase ID": _rt(COMPLETION_ROW["Phase ID"]),
        "Wave ID": _rt(COMPLETION_ROW["Wave ID"]),
        "Sub-Wave": _rt(COMPLETION_ROW["Sub-Wave"]),
        "Plan File": _rt(COMPLETION_ROW["Plan File"]),
        "Parent Plan Summary": _rt(COMPLETION_ROW["Parent Plan Summary"]),
        "Success Criteria": _rt(COMPLETION_ROW["Success Criteria"]),
        "Files In Scope": _rt(COMPLETION_ROW["Files In Scope"]),
        "Dependencies": _rt(COMPLETION_ROW["Dependencies"]),
        "Blocking Items": _rt(COMPLETION_ROW["Blocking Items"]),
        "Status": {"select": {"name": COMPLETION_ROW["Status"]}},
        "Est Tokens": {"number": COMPLETION_ROW["Est Tokens"]},
    }
    body = {
        "parent": {"type": "database_id", "database_id": DB_ID},
        "properties": props,
    }
    return http("POST", "https://api.notion.com/v1/pages", body)


def patch_descope(page_id, note):
    body = {
        "properties": {
            "Status": {"select": {"name": "Descoped"}},
            "Blocking Items": _rt(f"DESCOPED 2026-04-24: {note}"),
        }
    }
    return http("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)


def log_receipt(op, page_id, ok, detail):
    os.makedirs(os.path.dirname(RECEIPTS), exist_ok=True)
    with open(RECEIPTS, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "op": op,
                    "page_id": page_id,
                    "ok": ok,
                    "detail": detail,
                }
            )
            + "\n"
        )


def main():
    if not TOKEN:
        print("NOTION_TOKEN not set", file=sys.stderr)
        return 1

    total_ops = 1 + len(DUPLICATES_TO_DESCOPE) + len(AGG_TO_DESCOPE)
    done = 0

    print(f"Starting Notion writeback: {total_ops} operations")

    # 1. POST completion row
    try:
        r = post_completion()
        new_id = r["id"]
        log_receipt("POST-completion", new_id, True, r["url"])
        done += 1
        print(f"[{done}/{total_ops}] POSTED completion row: {new_id}")
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        detail = getattr(e, "read", lambda: b"")().decode() if hasattr(e, "read") else str(e)
        log_receipt("POST-completion", None, False, detail[:500])
        print(f"[FAIL] POST completion: {e}\n{detail[:500]}", file=sys.stderr)
        return 2

    # 2. PATCH duplicates
    for page_id, reason in DUPLICATES_TO_DESCOPE:
        try:
            http(
                "PATCH",
                f"https://api.notion.com/v1/pages/{page_id}",
                {
                    "properties": {
                        "Status": {"select": {"name": "Descoped"}},
                        "Blocking Items": _rt(f"DESCOPED 2026-04-24 (duplicate): {reason}"),
                    }
                },
            )
            log_receipt("PATCH-descope-dup", page_id, True, reason[:120])
            done += 1
            print(f"[{done}/{total_ops}] DESCOPED dup {page_id}")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            detail = getattr(e, "read", lambda: b"")().decode() if hasattr(e, "read") else str(e)
            log_receipt("PATCH-descope-dup", page_id, False, detail[:500])
            print(f"[WARN] Patch dup {page_id} failed: {e}", file=sys.stderr)

    # 3. PATCH AGG meta-rows
    for page_id, plan_slug in AGG_TO_DESCOPE:
        note = f"AGG meta-row — real items tracked under their own Wave IDs. Parent plan: {plan_slug}."
        try:
            http(
                "PATCH",
                f"https://api.notion.com/v1/pages/{page_id}",
                {
                    "properties": {
                        "Status": {"select": {"name": "Descoped"}},
                        "Blocking Items": _rt(f"DESCOPED 2026-04-24 (AGG meta-row): {note}"),
                    }
                },
            )
            log_receipt("PATCH-descope-agg", page_id, True, plan_slug)
            done += 1
            print(f"[{done}/{total_ops}] DESCOPED AGG {page_id} ({plan_slug})")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            detail = getattr(e, "read", lambda: b"")().decode() if hasattr(e, "read") else str(e)
            log_receipt("PATCH-descope-agg", page_id, False, detail[:500])
            print(f"[WARN] Patch AGG {page_id} failed: {e}", file=sys.stderr)

    print(f"\nDone: {done}/{total_ops} operations completed")
    print(f"Receipts: {RECEIPTS}")
    return 0 if done == total_ops else 3


if __name__ == "__main__":
    sys.exit(main())
