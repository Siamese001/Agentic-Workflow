#!/usr/bin/env python3
"""Sync W8A/W8B/W8C chat-session waves to Notion Plans + Backlog (Completed).

Disk SSOT:
  docs/reports/apps_rg/apps_rg_chat_session_w8_waves_closeout_manifest.json
  docs/reports/apps_rg/w8b_integrated_lane_evidence_runtime_validation_closeout_receipt.md
  docs/reports/apps_rg/fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md

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
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402
from tools.notion.wave_lifecycle_writer import apply_spec, find_plan_page  # noqa: E402
from tools.notion._wave_lifecycle_helpers import (  # noqa: E402
    PROP_AI_SUMMARY,
    PROP_STATUS,
    PROP_SUMMARY,
    NotionPatchSpec,
    STATUS_COMPLETED,
)

EXEC_SLUG = "fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2"
EXEC_PLAN_FILE = ".claude/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md"
WAVE_PLAN_ID = "APPS-RG-CHAT-W8"
WPC_DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
WAVE_STATUS_DONE = "Completed"
TIMEOUT = 30.0

EXEC_SUMMARY = (
    "COMPLETED (2026-05-20). Whole-run executive_summary materializes under "
    "modular_r4/sections/executive_summary/real/; RUN_LINKS EXECUTED (not PHASE1_NO_RUN_DIR). "
    "Proof run cli_22cf55c9fd58. Whole-run exit 1 aggregation preflight — out of scope."
)

EXEC_AI_SUMMARY = (
    "- STATUS: PASS materialization (2026-05-20)\n"
    "- PROOF: cli_22cf55c9fd58 exec_summary_20260520_201036 under integrated tree\n"
    "- FIX: file-ref briefing dispatch; sections root re-assert; canonical_dispatch brief resolver\n"
    "- RECEIPT: docs/reports/apps_rg/fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md\n"
    "- NON-CLAIM: product proof / aggregation preflight PASS"
)

WAVES: tuple[tuple[str, str, str, str], ...] = (
    (
        "8A",
        "W8A",
        "Integrated R4 live product proof inspection — product BLOCKED truthfully.",
        "docs/reports/apps_rg/integrated_r4_live_product_proof_attempt_receipt.md",
    ),
    (
        "8B",
        "W8B",
        "Integrated lane evidence packaging — 7 lane_bundle_refs on cli_93046aa0c06e fresh whole-run.",
        "docs/reports/apps_rg/w8b_integrated_lane_evidence_runtime_validation_closeout_receipt.md",
    ),
    (
        "8C",
        "W8C",
        "Whole-run executive_summary materialization PASS cli_22cf55c9fd58; X3_BLOCK aggregation out of scope.",
        "docs/reports/apps_rg/fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md",
    ),
)


def _http(method: str, url: str, token: str, body: dict | None = None) -> dict:
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
) -> str:
    phase_title = f"[W8] W{wave_num} — {label}"
    payload = {
        "parent": {"database_id": "aa8d2507-101e-4384-81d9-60ea3fe33876"},
        "properties": {
            "Phase Title": _title(phase_title),
            "Phase ID": _rt(phase_id),
            "Wave ID": _rt(WAVE_PLAN_ID),
            "Plan File": _rt(EXEC_PLAN_FILE),
            "Plan": {"relation": [{"id": plan_page_id}]},
            "Status": {"select": {"name": WAVE_STATUS_DONE}},
            "Evidence": _rt(evidence),
            "Est Tokens": {"number": 2000},
        },
    }
    data = _http("POST", f"{NOTION_BASE}/pages", token, payload)
    return str(data.get("id") or "")


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print(json.dumps({"ok": False, "error": "no_notion_token"}), file=sys.stderr)
        return 1

    page_id_tuple = find_plan_page(EXEC_SLUG, token)
    plan_page_id = page_id_tuple[0] if page_id_tuple else None
    if not plan_page_id:
        print(json.dumps({"ok": False, "error": "plan_not_found", "slug": EXEC_SLUG}), file=sys.stderr)
        return 1

    spec = NotionPatchSpec(
        slug=EXEC_SLUG,
        summary_append="[Wave-Log 2026-05-20T20:30:00Z] W8C PASS — cli_22cf55c9fd58 materialization",
        properties={
            PROP_STATUS: {"select": {"name": STATUS_COMPLETED}},
            PROP_SUMMARY: {"rich_text": [{"text": {"content": EXEC_SUMMARY[:1990]}}]},
            PROP_AI_SUMMARY: {"rich_text": [{"text": {"content": EXEC_AI_SUMMARY[:1990]}}]},
        },
        reason="chat_w8_waves_closeout",
    )
    apply_spec(spec)

    wave_results: list[dict[str, str]] = []
    for wave_num, phase_id, label, receipt in WAVES:
        evidence = f"PASS. Receipt: {receipt}"
        existing = _query_wpc_by_phase_id(token, phase_id)
        if existing:
            _patch_wpc_done(token, existing, evidence)
            wave_results.append({"phase_id": phase_id, "action": "patched", "page_id": existing})
        else:
            page_id = _post_wpc_wave(token, plan_page_id, wave_num, phase_id, label, evidence)
            wave_results.append({"phase_id": phase_id, "action": "created", "page_id": page_id})

    print(
        json.dumps(
            {
                "ok": True,
                "plan_slug": EXEC_SLUG,
                "plan_page_id": plan_page_id,
                "waves": wave_results,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
