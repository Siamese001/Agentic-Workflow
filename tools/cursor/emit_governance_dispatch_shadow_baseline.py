#!/usr/bin/env python3
"""Emit W0 governance dispatch shadow baseline (one jsonl row)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SLUG = "governance-dedup-closeout-e8a4c2"
OUT = REPO / "artifacts" / "cursor" / "governance_dispatch_shadow.jsonl"
MATRIX = REPO / "docs/reports/cursor/governance_w3_hook_audit_matrix.json"
DISPATCH_HOOK = REPO / ".cursor/hooks/after_agent_governance_dispatch.py"
DISPATCH_PY = REPO / ".claude/governance/scripts/post_agent_dispatch.py"


def _extract_ag_chain(text: str) -> list[str]:
    in_chain = False
    names: list[str] = []
    for line in text.splitlines():
        if "_AG_CHAIN" in line and "tuple" in line:
            in_chain = True
            continue
        if in_chain:
            if line.strip() == ")":
                break
            m = re.search(r"(post_agent_[\w]+\.py)", line)
            if m:
                names.append(m.group(1))
    return names


def _extract_legacy(text: str) -> list[str]:
    names: list[str] = []
    in_legacy = False
    for line in text.splitlines():
        if line.strip().startswith("LEGACY_SCRIPTS"):
            in_legacy = True
            continue
        if in_legacy:
            if line.strip() == "]":
                break
            m = re.search(r"(post_agent_[\w]+\.py)", line)
            if m:
                names.append(m.group(1))
    return names


def main() -> int:
    started = datetime.now(timezone.utc)
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    record = {
        "event": "shadow_period_started",
        "plan_id": SLUG,
        "wave": "W0",
        "started_at": started.isoformat(),
        "eligible_for_w1_script_archive_at": (started + timedelta(days=7)).isoformat(),
        "shadow_days_required": 7,
        "post_agent_dispatcher_env": "POST_AGENT_DISPATCHER=1",
        "hooks_json_after_agent_response": ["after_agent_governance_dispatch.py"],
        "matrix_generated_at": matrix.get("generated_at"),
        "matrix_counts": matrix.get("counts"),
        "post_agent_scripts_total": matrix.get("post_agent_scripts_total"),
        "ag_chain_scripts": _extract_ag_chain(DISPATCH_HOOK.read_text(encoding="utf-8")),
        "dispatch_legacy_scripts": _extract_legacy(DISPATCH_PY.read_text(encoding="utf-8")),
        "invocation_count": 0,
        "error_count": 0,
        "notes": "W0 baseline; W1 may add per-invocation append rows",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "path": str(OUT.relative_to(REPO)).replace("\\", "/")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
