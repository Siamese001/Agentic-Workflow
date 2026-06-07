#!/usr/bin/env python3
"""Register exec-summary-waves-abcd-e8f1a3 plan in Notion Plans DB (Completed)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-waves-abcd-e8f1a3"
PLAN_PATH = ".claude/plans/exec-summary-waves-abcd-e8f1a3.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): Executive summary Waves A–D — PUA splitter tokens, X2 display "
    "roundtrip + metric dedup gates, graph-only covered_bases dedup, opener-only repair, "
    "composition-before-repair, strategic closer, judge regen opt-in, APPS_RG_VLLM_AUTO_START. "
    "Brown exec_summary_20260523_213853: X2 PASS, ChatGPT 4.1, X3_REVIEW."
)

AI_SUMMARY = """- STATUS: Completed (Waves A–D + verify)
- A: PUA abbrev tokens; x2 display roundtrip + cross-sentence metric dedup; graph-only covered_bases
- B: opener_normalize_only repair; composition plan before graph repair; join_executive_summary_sentences
- C: composition_plan + strategic closer; RELEASE_JUDGE_REGENERATION + APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1 opt-in
- D: APPS_RG_VLLM_AUTO_START preflight; qwen-vllm-topology doc
- Proof: exec_summary_20260523_213853 — Basel III intact, no 8→28 dup, 23 pytest passed
- Deferred: X3 ALLOW (Gemini/Claude below 4.0; judge regen env or C0.3 plan)
- Disk SSOT: .claude/plans/exec-summary-waves-abcd-e8f1a3.md"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {"property": "Slug", "title": {"equals": SLUG}},
        "page_size": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query",
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
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return None
    rows = data.get("results") or []
    return str(rows[0].get("id") or "") if rows else None


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
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    page_id = _query_page_id()
    if page_id and _patch_page(page_id):
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
                    "status": "Completed",
                    "slug": SLUG,
                    "plan_path": PLAN_PATH,
                }
            )
        )
        print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
        return 0

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
            force_status="Completed",
        )
    except PlanCreationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "status": "Completed",
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={result.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
