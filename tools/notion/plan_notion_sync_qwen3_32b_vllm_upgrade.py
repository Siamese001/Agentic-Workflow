#!/usr/bin/env python3
"""Register qwen3-32b-vllm-upgrade-d7a3f1 in Notion Plans DB as Lower Priority."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "qwen3-32b-vllm-upgrade-d7a3f1"
PLAN_PATH = ".cursor/plans/qwen3-32b-vllm-upgrade-d7a3f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
STATUS = "Lower Priority"

SUMMARY = (
    "Lower Priority: Upgrade local-qwen-vllm from Qwen2.5-32B-Instruct-AWQ to "
    "Qwen3-32B-Instruct-AWQ (dense AWQ) on RTX 5090 — preflight vLLM pin, container "
    "recreate, SSOT docs, exec_summary regression. Resume when vLLM maintenance or "
    "regen quality triggers. Chroma/BGE retrieval out of scope."
)

AI_SUMMARY = """- Plan: qwen3-32b-vllm-upgrade-d7a3f1 (Lower Priority)
- Target: Qwen/Qwen3-32B-Instruct-AWQ @ max-model-len 24576, awq_marlin
- W0: HF id + trial container on Blackwell
- W1: local-qwen-vllm cutover + rollback
- W2: qwen-vllm-topology + local-llm-wsl2-gpu.mdc
- W3: pytest + exec_summary REAL_LLM proof
- W4: optional lane sweep (deferred)
- NOT retrieval: BGE-M3 + Chroma unchanged
- Resume: vLLM rebuild scheduled OR exec regen pain post c4e8a1"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {"filter": {"property": "Slug", "title": {"equals": SLUG}}, "page_size": 1}
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
            "Status": {"select": {"name": STATUS}},
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1

    page_id = _query_page_id()
    if page_id:
        ok = _patch_page(page_id)
        print(
            json.dumps(
                {
                    "ok": ok,
                    "action": "patched",
                    "page_id": page_id,
                    "slug": SLUG,
                    "status": STATUS,
                },
                indent=2,
            )
        )
        if ok:
            print(f"PLAN_EXISTS: slug={SLUG} notion_page={page_id} status={STATUS}")
        return 0 if ok else 1

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    page_id = result.page_id or ""
    if not page_id:
        print("FAIL: created but no page_id", file=sys.stderr)
        return 1

    ok = _patch_page(page_id)
    print(
        json.dumps(
            {
                "ok": ok,
                "action": "created_then_patched",
                "page_id": page_id,
                "slug": SLUG,
                "status": STATUS,
                "plan_path": PLAN_PATH,
            },
            indent=2,
        )
    )
    if ok:
        print(
            f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status={STATUS} "
            f"notion_page={page_id}"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
