#!/usr/bin/env python3
"""Build W3 hook audit matrix for post_agent_* scripts."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".codex" / "governance/scripts"
HOOKS_JSON = REPO / ".codex" / "hooks.json"
GOVERNANCE_DISPATCH = REPO / ".codex" / "hooks" / "after_agent_governance_dispatch.py"
DISPATCH_LEGACY = REPO / ".codex" / "governance/scripts" / "post_agent_dispatch.py"
OUT_JSON = REPO / "docs/reports/cursor/governance_w3_hook_audit_matrix.json"
OUT_MD = REPO / "docs/reports/cursor/governance_w3_hook_audit_matrix.md"

HOOK_REQUIRED = {
    "post_agent_adg_audit.py",
    # Author-Gate audits + AG-queue scripts retired + archived (teardown, ADR-093):
    # capture / miss_detector / ui_audit / schema_audit / ask_user_question_packet_audit /
    # pipeline_audit / ag_queue_drain / ag_queue_seed -> archives/claude_native_supersession_2026-06-07/.
    # S4 deferred-scope/next-step capture unwired from the per-Stop chain (W6
    # enforcement-surface-consolidation-d8b3f6; §24/ADR-096) -> moved to OBSOLETE_CANDIDATE below.
    "post_agent_mcp_hygiene_audit.py",
    "post_agent_long_command_audit.py",
    # [notion-wave-enforcement-removal] post_agent_wave_lifecycle_capture + post_agent_writeback_audit
    # DELETED (Notion wave enforcement + writeback-discipline advisory retired).
    "post_agent_scope_drift_detector.py",
}

CI_REQUIRED = {
    # Author-Gate audits retired + archived (teardown, ADR-093).
    "post_agent_adg_audit.py",
}

MANUAL_ONLY = {
    "manual_post_agent_replay.py",
}

OBSOLETE_CANDIDATE = {
    # S4 deferred-scope/next-step capture hooks deleted in W7 (enforcement-surface-consolidation-d8b3f6).
    "post_agent_author_gate_audit.py": "superseded by capture + miss_detector + schema/ui audits",
    "post_agent_author_gate_suite.py": "orchestration duplicate of individual AG audits",
    "post_agent_adr_registry_capture.py": "Notion ADR registry archived 2026-05-02; capture optional",
    "post_agent_notion_plans_status_audit.py": "superseded by unified_notion_status_auditor in governance hook",
    "post_agent_plan_creation_audit.py": "overlap plan_registration_capture + CI plan gates",
    "post_agent_plan_complete_audit.py": "CI + lifecycle capture cover completion",
    "post_agent_plans_dup_audit.py": "advisory; manual or periodic CI",
    "post_agent_heartbeat.py": "native handler in dispatch; not standalone hook",
    "post_agent_cleanup.py": "native handler in dispatch",
    "post_agent_grep_budget_audit.py": "native handler in dispatch",
    "post_agent_read_budget_audit.py": "native handler in dispatch",
    "post_agent_token_telemetry.py": "native handler in dispatch",
}

DUPLICATE_CANDIDATE = {
    "post_agent_notion_plans_status_audit.py": ["tools/notion/unified_notion_status_auditor.py"],
    "post_agent_notion_plan_identity_audit.py": ["post_agent_notion_plans_status_audit.py"],
}


def _hook_wired() -> set[str]:
    wired: set[str] = set()
    if GOVERNANCE_DISPATCH.is_file():
        text = GOVERNANCE_DISPATCH.read_text(encoding="utf-8")
        for name in HOOK_REQUIRED:
            if name in text:
                wired.add(name)
    if DISPATCH_LEGACY.is_file():
        text = DISPATCH_LEGACY.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "post_agent_" in line and ".py" in line:
                m = re.search(r"(post_agent_[\w]+\.py)", line)
                if m:
                    wired.add(m.group(1))
    return wired


def _disposition(name: str) -> str:
    if name == "post_agent_dispatch.py":
        return "hook_required"
    if name in MANUAL_ONLY:
        return "manual_only"
    if name in OBSOLETE_CANDIDATE:
        return "obsolete_candidate"
    if name in HOOK_REQUIRED:
        return "hook_required"
    if name in CI_REQUIRED:
        return "ci_required"
    return "manual_only"


def main() -> int:
    scripts = sorted(SCRIPTS.glob("post_agent_*.py"))
    wired = _hook_wired()
    rows = []
    counts = {
        "hook_required": 0,
        "ci_required": 0,
        "manual_only": 0,
        "obsolete_candidate": 0,
        "duplicate_candidate": 0,
    }

    for path in scripts:
        name = path.name
        disp = _disposition(name)
        counts[disp] = counts.get(disp, 0) + 1
        is_dup = name in DUPLICATE_CANDIDATE
        if is_dup:
            counts["duplicate_candidate"] += 1

        row = {
            "script_path": f".codex/governance/scripts/{name}",
            "current_hook_status": "wired_via_governance_dispatch" if name in wired else "not_in_after_agent_chain",
            "recommended_disposition": disp,
            "reason": OBSOLETE_CANDIDATE.get(name, "governance W3 matrix classification"),
            "duplicate_overlap_refs": DUPLICATE_CANDIDATE.get(name, []),
            "required_trigger": "afterAgentResponse" if disp == "hook_required" else None,
            "ci_command": "ops_scripts/ci/run_contract_gates.py (AG/ADG artifact gates)" if name in CI_REQUIRED else None,
            "deletion_status": "not_deleted_w3",
            "non_claim": None if name not in OBSOLETE_CANDIDATE else "retained_unreachable_ok_w3",
        }
        rows.append(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_id": "cursor-governance-two-tier-b4e8f2",
        "wave": "W3A",
        "hook_strategy": "dispatcher",
        "hooks_json_after_agent_response": ["after_agent_governance_dispatch.py"],
        "post_agent_scripts_total": len(scripts),
        "counts": counts,
        "matrix": rows,
        "explicit_non_claims": [
            "no post_agent scripts deleted in W3",
            "legacy after_agent_* hook files retained but unwired from hooks.json",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = [
        "# W3 Hook audit matrix",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        f"**Strategy:** {payload['hook_strategy']} (`after_agent_governance_dispatch.py`)",
        f"**Scripts inventoried:** {payload['post_agent_scripts_total']}",
        "",
        "| Disposition | Count |",
        "|-------------|-------|",
    ]
    for k, v in counts.items():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Matrix (summary)")
    md.append("")
    for row in rows:
        md.append(f"- `{row['script_path']}` → **{row['recommended_disposition']}** ({row['current_hook_status']})")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[w3-hook-audit] wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
