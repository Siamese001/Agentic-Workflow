#!/usr/bin/env python3
"""Patch five active-backlog plans Completed in Notion Plans DB (2026-05-25 closeout)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

PLANS: list[tuple[str, str, str, str]] = [
    (
        "l5-fanin-architecture-reduction-e7c4a2",
        ".cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md",
        "36227693-f55c-81fc-a35b-dea4f39b11d8",
        "COMPLETED (2026-05-25): L5 fan-in W3 + ratchet PASS on adg_indexed_05242026_2005.sqlite "
        "(4 improvements, 0 regressions). W4 baseline not required.",
    ),
    (
        "apps-rg-spine-only-unification-d8f4a2",
        ".cursor/plans/apps-rg-spine-only-unification-d8f4a2.md",
        "36927693-f55c-8190-b30b-de1f6534e2a7",
        "COMPLETED phase-1 (2026-05-25): W1–W4+W6 single spine; bridges deleted; ExitEvalPipeline; "
        "0 single-spine gate findings. DEFERRED: W5 L3+assembly in spine; W7 core migration.",
    ),
    (
        "apps-rg-proof-pool-c0-ssot-a7f3e2",
        ".cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md",
        "36927693-f55c-8173-99c1-c25da5321677",
        "COMPLETED Track B+C containment (2026-05-25): W23 RCAs; Track C synthesis gates; "
        "targeting parity exec_summary_20260524_233409. DEFERRED: X3_ALLOW; W0–W4 FEC waves.",
    ),
    (
        "apps-rg-resume-assembly-debt-burndown-56c022",
        ".cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md",
        "36827693-f55c-811f-9cae-c14d491432c4",
        "COMPLETED W0–W3 (2026-05-25): JSON SSOT, lane→rg_output merge, fail-closed assembly. "
        "DEFERRED: W4 offline demotion; W5 engines/reasoning boundary.",
    ),
    (
        "apps-rg-legacy-dependency-burndown-b7e4a2",
        ".cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md",
        "36527693-f55c-8178-8c13-f1c889dccaf1",
        "COMPLETED phases A–C (2026-05-25): competencies contract, PA parity, Rg migration. "
        "DEFERRED: D3 stub/repair hardening; Phase E archive when fan-in zero.",
    ),
]


def _patch(page_id: str, plan_path: str, summary: str, ai_summary: str) -> bool:
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
            "Plan File Path": {"rich_text": [{"text": {"content": plan_path}}]},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": ai_summary[:2000]}}]},
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
    results: list[dict[str, object]] = []
    ok_all = True
    for slug, plan_path, page_id, summary in PLANS:
        ai = (
            f"- PLAN_STATUS: COMPLETE (2026-05-25)\n"
            f"- Receipt: docs/reports/plans/active_backlog_closeout_receipt_20260525.md\n"
            f"- Disk: {plan_path}\n"
            f"- {summary}"
        )
        ok = _patch(page_id, plan_path, summary, ai)
        results.append({"slug": slug, "page_id": page_id, "ok": ok})
        ok_all = ok_all and ok
        print(f"PLAN_COMPLETE: slug={slug} path={plan_path} status=Completed notion_page={page_id}")
    print(json.dumps({"ok": ok_all, "results": results}, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
