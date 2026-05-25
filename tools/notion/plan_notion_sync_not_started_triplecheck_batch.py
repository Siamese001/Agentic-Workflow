#!/usr/bin/env python3
"""Triple-check Not Started plans: complete 10c; Waiting for valid backlog; Retire superseded."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# (slug, plan_path, page_id, notion_status, summary, waiting_for)
ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "10c-proof-bundle-current-head-a8f4c2",
        ".cursor/plans/10c-proof-bundle-current-head-a8f4c2.md",
        "36127693-f55c-81e2-bb0a-cad26d5dc3cc",
        "Completed",
        "COMPLETED (2026-05-25): Regenerated 198 proof bundles at HEAD 1f8195f1; "
        "check_10c_pilot_proof_evidence.py --skip-pytest PASS (198/198).",
        "",
    ),
    (
        "l0-l3-parent-gap-remediation-a7f3e2",
        ".cursor/plans/l0-l3-parent-gap-remediation-a7f3e2.md",
        "36927693-f55c-812e-9828-ccb5031897fd",
        "Waiting",
        "VALID backlog: L0/L3 parent §7 validators + apps_rg l3_binding not shipped. "
        "Partial overlap with completed l5-l4-00c-parent-gap; 03 Switching_L3 scope remains.",
        "Author-Gate for touches_agentic_core; W0 vocabulary decision.",
    ),
    (
        "l0-routing-v15-only-cutover-c9e2f1",
        ".cursor/plans/l0-routing-v15-only-cutover-c9e2f1.md",
        "36727693-f55c-81e9-b053-ef58e79f02fb",
        "Waiting",
        "VALID backlog: v12/v15 duality still in agentic_core/L0_routing (bridge, fallback chains). "
        "Not superseded by apps_rg section spine W2–W6.",
        "Author-Gate + dedicated L0 cutover wave; ADG baseline 05212026_0548.",
    ),
    (
        "apps-rg-parallel-section-orchestration-f2a8c4",
        ".cursor/plans/apps-rg-parallel-section-orchestration-f2a8c4.md",
        "36627693-f55c-810f-8d37-e31d7656b46c",
        "Waiting",
        "VALID backlog: whole-run Phase-1 lanes still serial in modular_resume_generation. "
        "Section CLI uses spine runners (serial per invocation) — parallel DAG is separate scope.",
        "Spine master W5 deferred (L3+assembly); vLLM concurrency policy + lane DAG W0–W2.",
    ),
    (
        "semantic-cache-fingerprint-proof-c9f1a3",
        ".cursor/plans/semantic-cache-fingerprint-proof-c9f1a3.md",
        "36127693-f55c-81ce-a640-d26133b431de",
        "Waiting",
        "VALID optional backlog: no artifacts/governance fingerprint receipt per plan DoD. "
        "Related tooling exists (tools/cache, tools/cert semantic_cache_*) but plan W1–W2 open.",
        "Stakeholder request for byte-stable cache proof; low priority optional audit.",
    ),
    (
        "fortknox-runtime-dual-track-b7c4e2",
        ".cursor/plans/fortknox-runtime-dual-track-b7c4e2.md",
        "36127693-f55c-811c-8ecc-db4577c8874c",
        "Waiting",
        "VALID backlog: dual-track governance W0–W4 on disk TODO. FortKnox skill + "
        "fortknox-certification-discipline.md exist; full plan waves (CI posture, runtime template) not executed.",
        "Documentation/ADR waves W0–W1; not blocking apps_rg spine.",
    ),
]


def _patch(
    page_id: str,
    plan_path: str,
    status: str,
    summary: str,
    ai_summary: str,
    waiting_for: str,
) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    props: dict = {
        "Status": {"select": {"name": status}},
        "Exists On Disk": {"checkbox": True},
        "Plan File Path": {"rich_text": [{"text": {"content": plan_path}}]},
        "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
        "AI Summary ": {"rich_text": [{"text": {"content": ai_summary[:2000]}}]},
    }
    if waiting_for and status == "Waiting":
        props["Waiting For"] = {"rich_text": [{"text": {"content": waiting_for[:2000]}}]}
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    ok_all = True
    for slug, plan_path, page_id, status, summary, waiting_for in ROWS:
        ai = (
            f"- Triple-check 2026-05-25: {status}\n"
            f"- Receipt: docs/reports/plans/not_started_plans_triplecheck_receipt_20260525.md\n"
            f"- {summary}"
        )
        ok = _patch(page_id, plan_path, status, summary, ai, waiting_for)
        ok_all = ok_all and ok
        print(f"PLAN_{status.upper().replace(' ', '_')}: slug={slug} notion_page={page_id}")
    print(json.dumps({"ok": ok_all}, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
