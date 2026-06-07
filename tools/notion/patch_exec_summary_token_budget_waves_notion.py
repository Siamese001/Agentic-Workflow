#!/usr/bin/env python3
"""Register exec-summary-token-budget-a8f3c2 on disk + Notion; post W1–W4 as Done.

Disk SSOT:
  .claude/plans/exec-summary-token-budget-a8f3c2.md
  docs/reports/apps_rg/executive_summary_token_budget_waves_manifest.json

Run from repo root with NOTION_TOKEN (or NOTION_API_KEY).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

from tools.notion._wave_lifecycle_helpers import (  # noqa: E402
    PROP_AI_SUMMARY,
    PROP_STATUS,
    PROP_SUMMARY,
    NotionPatchSpec,
    STATUS_COMPLETED,
)
from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402
from tools.notion.plan_creation_helper import create_plan_in_notion  # noqa: E402
from tools.notion.wave_lifecycle_writer import apply_spec, find_plan_page  # noqa: E402

SLUG = "exec-summary-token-budget-a8f3c2"
PLAN_FILE = ".claude/plans/exec-summary-token-budget-a8f3c2.md"
WAVE_PLAN_ID = "EXEC-SUM-TOKEN-BUDGET"
WPC_DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
WAVE_STATUS_DONE = "Completed"
TIMEOUT = 30.0

SUMMARY = (
    "COMPLETED. apps_rg executive_summary token budget W1–W4: v2 fail-closed policy, "
    "Brown LIVE_BLOCK, evidence capsule, targeting cap LIVE_RUNTIME (exec_summary_20260520_144839). "
    "Manifest: docs/reports/apps_rg/executive_summary_token_budget_waves_manifest.json. "
    "Not RELEASE_ELIGIBLE (X3 judge BLOCK)."
)

AI_SUMMARY = (
    "- W1: executive_summary_optional_trim_only_v2 + pytest PASS\n"
    "- W2: LIVE_BLOCK exec_summary_20260520_142647 TOKEN_BUDGET_EXCEEDED_AFTER_TRIM\n"
    "- W3: capsule LIVE_BLOCK exec_summary_20260520_144110\n"
    "- W4: targeting cap LIVE_RUNTIME exec_summary_20260520_144839 X2 PASS X3 BLOCK\n"
    "- Disk: docs/reports/apps_rg/executive_summary_token_budget_waves_closeout_receipt.md"
)

WAVES: tuple[tuple[str, str, str, int], ...] = (
    (
        "1",
        "EXEC-TB-W1",
        "v2 optional-only policy + contract/unit tests. Receipt: executive_summary_token_budget_policy_closeout_receipt.md",
        4000,
    ),
    (
        "2",
        "EXEC-TB-W2",
        "Brown LIVE_BLOCK fail-closed. Run: exec_summary_20260520_142647. TOKEN_BUDGET_EXCEEDED_AFTER_TRIM; provider_attempted=false.",
        3000,
    ),
    (
        "3",
        "EXEC-TB-W3",
        "Evidence capsule + Brown LIVE_BLOCK. Run: exec_summary_20260520_144110. after_capsule~17519 still blocked.",
        5000,
    ),
    (
        "4",
        "EXEC-TB-W4",
        "Targeting cap + LIVE_RUNTIME. Run: exec_summary_20260520_144839. targeting 4708→943; prompt 13753/14848; X2 PASS X3 BLOCK.",
        6000,
    ),
)


def _http(
    method: str,
    url: str,
    token: str,
    body: dict | None = None,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _rt(text: str) -> dict:
    return {"rich_text": [{"text": {"content": text[:1990]}}]}


def _title(text: str) -> dict:
    return {"title": [{"text": {"content": text[:1990]}}]}


def _query_wpc_by_phase_id(token: str, phase_id: str) -> str | None:
    url = f"{NOTION_BASE}/data_sources/{WPC_DATA_SOURCE_ID}/query"
    body = {
        "filter": {
            "and": [
                {"property": "Phase ID", "rich_text": {"equals": phase_id}},
                {"property": "Wave ID", "rich_text": {"equals": WAVE_PLAN_ID}},
            ]
        },
        "page_size": 1,
    }
    try:
        data = _http("POST", url, token, body)
    except urllib.error.HTTPError:
        return None
    results = data.get("results") or []
    if not results:
        return None
    return results[0].get("id")


def _patch_wpc_done(token: str, page_id: str, evidence: str) -> None:
    payload = {
        "properties": {
            "Status": {"select": {"name": WAVE_STATUS_DONE}},
            "Evidence": _rt(evidence),
        }
    }
    _http("PATCH", f"{NOTION_BASE}/pages/{page_id}", token, payload)


def _post_wpc_wave(
    token: str,
    plan_page_id: str,
    wave_num: str,
    phase_id: str,
    label: str,
    evidence: str,
    est_tokens: int,
) -> str:
    phase_title = f"[EXEC-TB] W{wave_num} — {label}"
    body = {
        "parent": {"type": "data_source_id", "data_source_id": WPC_DATA_SOURCE_ID},
        "properties": {
            "Phase Title": _title(phase_title),
            "Phase ID": _rt(phase_id),
            "Wave ID": _rt(WAVE_PLAN_ID),
            "Plan File": _rt(PLAN_FILE),
            "Plan": {"relation": [{"id": plan_page_id}]},
            "Evidence": _rt(evidence),
            "Status": {"select": {"name": WAVE_STATUS_DONE}},
            "Est Tokens": {"number": est_tokens},
        },
    }
    r = _http("POST", f"{NOTION_BASE}/pages", token, body)
    return r["id"]


def _ensure_plan_row(token: str) -> str | None:
    existing, _props, _msg = find_plan_page(SLUG, token)
    if existing:
        spec = NotionPatchSpec(
            slug=SLUG,
            properties={
                PROP_STATUS: {"select": {"name": STATUS_COMPLETED}},
                PROP_SUMMARY: {"rich_text": [{"text": {"content": SUMMARY[:1990]}}]},
                PROP_AI_SUMMARY: {"rich_text": [{"text": {"content": AI_SUMMARY[:1990]}}]},
            },
            summary_append=(
                "[Wave-Log 2026-05-20T00:00:00Z] W1 DONE — v2 policy + tests\n"
                "[Wave-Log 2026-05-20T00:00:00Z] W2 DONE — LIVE_BLOCK 142647\n"
                "[Wave-Log 2026-05-20T00:00:00Z] W3 DONE — capsule LIVE_BLOCK 144110\n"
                "[Wave-Log 2026-05-20T00:00:00Z] W4 DONE — targeting cap LIVE_RUNTIME 144839\n"
                "[Wave-Log 2026-05-20T00:00:00Z] PLAN_COMPLETE — token budget waves closed"
            ),
            reason="exec_summary_token_budget_waves_closeout",
        )
        ok, msg = apply_spec(spec, dry_run=False)
        if not ok:
            print(f"Plan patch failed: {msg}", file=sys.stderr)
            return None
        print(f"Plan patched Completed: {existing} ({msg})")
        return existing

    result = create_plan_in_notion(
        slug=SLUG,
        summary=SUMMARY,
        ai_summary=AI_SUMMARY,
        plan_file_path=PLAN_FILE,
        force_status="Completed",
    )
    if not result.ok:
        print(f"Plan create failed: {result.error}", file=sys.stderr)
        return None
    print(f"Plan created Completed: {result.page_id}")
    return result.page_id


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN not set", file=sys.stderr)
        return 2

    plan_id = _ensure_plan_row(token)
    if not plan_id:
        return 1

    wave_ok = 0
    for wave_num, phase_id, label, est_tokens in WAVES:
        existing = _query_wpc_by_phase_id(token, phase_id)
        evidence = label
        try:
            if existing:
                _patch_wpc_done(token, existing, evidence)
                print(f"W{wave_num} patched Completed: {existing} ({phase_id})")
            else:
                pid = _post_wpc_wave(
                    token, plan_id, wave_num, phase_id, label, evidence, est_tokens
                )
                print(f"W{wave_num} posted Completed: {pid} ({phase_id})")
            wave_ok += 1
        except urllib.error.HTTPError as exc:
            print(
                f"W{wave_num} failed: {exc.read().decode('utf-8', errors='replace')[:500]}",
                file=sys.stderr,
            )

    print(f"Done: plan={plan_id} waves={wave_ok}/{len(WAVES)}")
    return 0 if wave_ok == len(WAVES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
