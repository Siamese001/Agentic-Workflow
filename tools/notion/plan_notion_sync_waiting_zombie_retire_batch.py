#!/usr/bin/env python3
"""Retire Windsurf-era Waiting zombie plans; narrow apps-test-surface to W1 soak only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RETIRE: list[tuple[str, str, str, str]] = [
    (
        "runtime-cert-e-ci-gate-e7b3f1",
        "35c27693-f55c-810e-8fc8-e0ac2db108bd",
        "RETIRED 2026-05-24: Superseded — check_runtime_certification.py (T8r advisory) + "
        "runtime-cert-e1w2/e1-fail-closed child plans COMPLETE; fortknox dual-track COMPLETE.",
        "Superseded by shipped Phase E.1 gate and child plans. Notion row retired; "
        "strict promotion tracked separately if needed.",
    ),
    (
        "author-gate-pipeline-hardening-deferred-b3e1d7",
        "35b27693-f55c-818a-9bad-f0237cb136a1",
        "RETIRED 2026-05-24: DS-1–DS-4 DONE on disk; AGP1 fail-closed default; "
        "HITL_PACKET alias retired. DS-5 optional — no violation jsonl yet.",
        "Parent hardening complete. Remaining regex tune is optional T1 when "
        "artifacts/cursor/author_gate_pipeline_violations.jsonl has 14d data.",
    ),
    (
        "notion-plan-identity-deferred-scope-a3b7e2",
        "35c27693-f55c-8105-acc7-c121fe6860e4",
        "RETIRED 2026-05-24: Volume below webhook threshold; NP8 + plan_identity "
        "audits already in CI. DS-1/DS-2 premature until scale or incident.",
        "Reactivate as new plan if plan count >500 or bulk-status incident recurs.",
    ),
    (
        "apps-embedding-deferred-scope-f9a3b2",
        "35c27693-f55c-8112-b14f-cecde0a8a9c4",
        "RETIRED 2026-05-24: Not blocking apps_rg/exec-summary. Research has BGE-M3 "
        "Chroma path; semantic-cache fingerprint plan COMPLETE. Fleet review deferred.",
        "Per-app embedding work opens when that app spine is in scope — not this tracker.",
    ),
    (
        "l5-cert-ref-deferred-scope-f3a1b8",
        "35b27693-f55c-810c-a40f-e7cde42b0da2",
        "RETIRED 2026-05-24: apps_rg/lic/underwriting wired; qna/rfp/eval have zero "
        "l5_certification_ref. Use per-app plans when activating those apps.",
        "Tracker superseded by spine-unification + l5-pa-orchestrator-ref-forward closeout.",
    ),
]

TSP1_SLUG = "apps-test-surface-deferred-f3c8b2"
TSP1_PAGE = "35c27693-f55c-818f-855b-eeadfa81fc03"
TSP1_SUMMARY = (
    "WAITING W1 only (2/30 TSP1 soak): flip APPS_TEST_SURFACE_FAIL_CLOSED=1 after "
    "30 consecutive exit-0 runs in artifacts/ci/check_apps_test_surface_parity_*.json. "
    "GHA: apps-test-surface-tsp1-soak-nightly.yml. W2–W5 DONE."
)
TSP1_AI = """- W1 only: TSP1 fail-closed promotion (soak 2/30 as of 2026-05-25)
- Parent consolidation COMPLETE; do not re-run W2–W5
- Retired sibling zombies 2026-05-24 batch (runtime-cert-e, author-gate, notion-identity, embedding, l5 tracker)"""

TSP1_COMMENT = """Waiting narrowed 2026-05-24

Only W1 remains: promote TSP1 to fail-closed after 30 consecutive green soak runs (nightly GHA). W2–W5 already DONE on disk. Not a full program — calendar/data gate only."""


def _patch(page_id: str, status: str, summary: str, ai: str, waiting: bool = False) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    props: dict = {
        "Status": {"select": {"name": status}},
        "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
        "AI Summary ": {"rich_text": [{"text": {"content": ai[:2000]}}]},
    }
    if not waiting:
        props["Waiting For"] = {"rich_text": []}
    body = json.dumps({"properties": props}).encode("utf-8")
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
        print(json.dumps({"page_id": page_id, "error": str(exc)}), file=sys.stderr)
        return False


def _comment(page_id: str, text: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    chunks = [text[i : i + 1900] for i in range(0, len(text), 1900)]
    payload = {
        "parent": {"page_id": page_id},
        "rich_text": [{"type": "text", "text": {"content": c}} for c in chunks],
    }
    req = urllib.request.Request(
        "https://api.notion.com/v1/comments",
        data=json.dumps(payload).encode("utf-8"),
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
        print(json.dumps({"page_id": page_id, "comment_error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    results: list[dict] = []
    ok_all = True

    for slug, page_id, summary, ai in RETIRE:
        patched = _patch(page_id, "Retired", summary, ai, waiting=False)
        commented = _comment(
            page_id,
            f"Retired 2026-05-24 (repo supersession audit).\n\n{summary}\n\n{ai}",
        )
        ok = patched and commented
        ok_all = ok_all and ok
        results.append(
            {
                "slug": slug,
                "page_id": page_id,
                "action": "retired",
                "patched": patched,
                "comment_posted": commented,
                "notion_url": f"https://www.notion.so/{page_id.replace('-', '')}",
            }
        )
        print(f"PLAN_RETIRED: slug={slug} notion_page={page_id}")

    patched = _patch(TSP1_PAGE, "Waiting", TSP1_SUMMARY, TSP1_AI, waiting=False)
    commented = _comment(TSP1_PAGE, TSP1_COMMENT)
    ok_all = ok_all and patched and commented
    results.append(
        {
            "slug": TSP1_SLUG,
            "page_id": TSP1_PAGE,
            "action": "waiting_w1_only",
            "patched": patched,
            "comment_posted": commented,
            "notion_url": f"https://www.notion.so/{TSP1_PAGE.replace('-', '')}",
        }
    )
    print(f"PLAN_UPDATED: slug={TSP1_SLUG} status=Waiting notion_page={TSP1_PAGE}")

    print(json.dumps({"ok": ok_all, "results": results}, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
