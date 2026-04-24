"""One-shot Notion bootstrap for plan l2-execute-v2-agent-conformance-c8e4f1.

Posts a parent row to Plans DB + 7 child rows to Wave/Phase Convergence DB.
Uses direct HTTP (not MCP) to avoid §26 serialization race on 8 sequential posts.
Idempotent: skips creation if a row with the same Phase Title already exists.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

PLAN_SLUG = "l2-execute-v2-agent-conformance-c8e4f1"
PLAN_FILENAME = f"{PLAN_SLUG}.md"

PLANS_DB = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DS = "ac53d31b-3068-4039-9ebe-856c12caab32"
WAVE_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"
WAVE_DS = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

WAVES: list[dict[str, Any]] = [
    {
        "phase_title": "[P2] W0 P0.1 — ADG hotspot probe + graph-layer evidence",
        "wave": "W0",
        "phase": "P0.1",
        "sub_wave": "W0-P2-CORE",
        "files": "tools/debug/_l2v2_w0_probe.py (new)",
        "success": "ADG_HOTSPOT_REPORT + ADG_GRAPH_LAYER_EVIDENCE populated with fan-in ranks, 3+ MVs, P-view matches",
        "deps": "Requires fresh ADG snapshot adg_indexed_04242026_0721.sqlite",
        "est_tokens": 4000,
        "blocking": "Fan-in map drives W6 exemplar selection. Cannot skip per constitutional §22/§23.",
    },
    {
        "phase_title": "[P2] W1 P1.1 — Split base classes (additive) SovereignValidatorBase + SovereignHealerBase",
        "wave": "W1",
        "phase": "P1.1",
        "sub_wave": "W1-P2-CORE",
        "files": "agentic_core/base_agents/SovereignValidatorBase.py (new), SovereignHealerBase.py (new), tests/unit/agentic_core/base_agents/test_split_bases.py (new)",
        "success": "Two new base classes import cleanly, instantiate, validator surface has no heal methods, healer surface has no validate methods",
        "deps": "None — SovereignBaseAgent remains untouched",
        "est_tokens": 8000,
        "blocking": "Foundation for W6 exemplar migration. Additive-only; legacy agents unaffected.",
    },
    {
        "phase_title": "[P2] W2 P2.1 — HealResult return contract + HealOutcome enum",
        "wave": "W2",
        "phase": "P2.1",
        "sub_wave": "W2-P2-CORE",
        "files": "agentic_core/L5_safety/types/heal_request_types.py (edit — additive), tests/unit/agentic_core/L5_safety/test_heal_result.py (new)",
        "success": "HealResult frozen dataclass with outcome/reason_code/parent_packet_id/repair_count/policy_hash/blueprint_hash fields + to_dict serialization; HealOutcome enum with SUCCESS/SOFT_REPAIRABLE/FAIL_TERMINAL/NEEDS_HELP",
        "deps": "HealRequest fields reused",
        "est_tokens": 5000,
        "blocking": "Required by W3 stub fixes. Additive to existing HealRequest.",
    },
    {
        "phase_title": "[P1] W3 P3.1 — Fix 4 stub heal implementations to return HealResult",
        "wave": "W3",
        "phase": "P3.1",
        "sub_wave": "W3-P1-CORE",
        "files": "agentic_core/L2_execution/reasoning/StructuredEngineAgent.py, apps_rg/reasoning/ResumeAssemblyAgent.py, apps_shared/reasoning/BaseProactiveAgent.py, apps_shared/reasoning/BaseReflectionAgent.py, tests/unit/integration/test_heal_stubs_replaced.py (new)",
        "success": "All 4 agents return valid HealResult; ResumeAssemblyAgent no longer raises NotImplementedError; returned dict round-trips through HealResult.to_dict()",
        "deps": "W2 HealResult",
        "est_tokens": 6000,
        "blocking": "P1 priority — current NotImplementedError is a hard contract violation.",
    },
    {
        "phase_title": "[P2] W4 P4.1 — e2_agent_gate decorator (additive)",
        "wave": "W4",
        "phase": "P4.1",
        "sub_wave": "W4-P2-CORE",
        "files": "agentic_core/L2_execution/enforcement/e2_agent_gate.py (new), tests/unit/agentic_core/L2_execution/test_e2_agent_gate.py (new)",
        "success": "Decorator wraps agent methods, runs evaluate_work_order (yesterday's primitive), short-circuits with E2RejectedBeforeExecute or ConfirmBeforeExecute without swallowing",
        "deps": "Yesterday's e2_validate_before_execute.py",
        "est_tokens": 6000,
        "blocking": "Additive wrapper — no call-site migration in this plan.",
    },
    {
        "phase_title": "[P2] W5 P5.1 — SealedL2Artifact helper + opt-in CI gate",
        "wave": "W5",
        "phase": "P5.1",
        "sub_wave": "W5-P2-CORE",
        "files": "agentic_core/L2_execution/enforcement/agent_seal_helper.py (new), ops_scripts/ci/check_agent_sealed_return.py (new), tests/unit/agentic_core/L2_execution/test_agent_seal_helper.py (new)",
        "success": "Helper constructs SealedL2Artifact from agent output; CI gate scans classes marked @requires_sealed_return and fails if return type annotation is not SealedL2Artifact",
        "deps": "sealed_l2_artifact.py (exists)",
        "est_tokens": 7000,
        "blocking": "Opt-in marker avoids retroactive failure on 88 agents.",
    },
    {
        "phase_title": "[P3] W6 P6.1 — Exemplar migration (2 agents) as template",
        "wave": "W6",
        "phase": "P6.1",
        "sub_wave": "W6-P3-CORE",
        "files": "TBD — lowest fan-in co-located agents selected from W0 probe",
        "success": "2 agents migrated onto split bases, return HealResult, marked @requires_sealed_return, pass CI gate; migration pattern documented in plan",
        "deps": "W1, W2, W3, W4, W5",
        "est_tokens": 6000,
        "blocking": "Template for future rollout. Does not migrate all 88 agents.",
    },
]


def _headers() -> dict[str, str]:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.stderr.write("ERROR: NOTION_TOKEN not set\n")
        sys.exit(2)
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }


def _rt(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}}]


def _title(text: str) -> list[dict[str, Any]]:
    return _rt(text)


def _find_existing(ds_id: str, title_prop: str, title_value: str, headers: dict[str, str]) -> str | None:
    url = f"https://api.notion.com/v1/data_sources/{ds_id}/query"
    payload = {
        "filter": {"property": title_prop, "title": {"equals": title_value}},
        "page_size": 1,
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0]["id"] if results else None


def create_plans_row(headers: dict[str, str]) -> str:
    existing = _find_existing(PLANS_DS, "Slug", PLAN_SLUG, headers)
    if existing:
        print(f"[plans] exists plan_slug={PLAN_SLUG} page_id={existing}")
        return existing
    payload = {
        "parent": {"type": "database_id", "database_id": PLANS_DB},
        "properties": {
            "Slug": {"title": _title(PLAN_SLUG)},
            "Status": {"select": {"name": "Active"}},
            "Plan File Path": {"rich_text": _rt(f".windsurf/plans/{PLAN_FILENAME}")},
            "Exists On Disk": {"checkbox": True},
            "Summary": {
                "rich_text": _rt(
                    "L2 Execute v2 — thread E1–E5 stage contract through 88 Agent files. Consumes primitives from plan b7c4e2 (2026-04-23) without reinventing them. 7 waves: W0 ADG evidence, W1 split bases, W2 HealResult contract, W3 fix 4 stub heals, W4 E2 agent gate, W5 seal helper+CI, W6 2-agent exemplar migration."
                )
            },
        },
    }
    r = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        data=json.dumps(payload),
        timeout=30,
    )
    if r.status_code >= 400:
        sys.stderr.write(f"[plans] FAIL {r.status_code}: {r.text[:500]}\n")
        r.raise_for_status()
    page_id = r.json()["id"]
    print(f"[plans] created page_id={page_id}")
    return page_id


def create_wave_row(wave: dict[str, Any], headers: dict[str, str]) -> str | None:
    existing = _find_existing(WAVE_DS, "Phase Title", wave["phase_title"], headers)
    if existing:
        print(f"  [wave] exists {wave['wave']} page_id={existing}")
        return existing
    props = {
        "Phase Title": {"title": _title(wave["phase_title"])},
        "Phase ID": {"rich_text": _rt(wave["phase"])},
        "Wave ID": {"rich_text": _rt(wave["wave"])},
        "Sub-Wave": {"rich_text": _rt(wave["sub_wave"])},
        "Dependencies": {"rich_text": _rt(wave["deps"])},
        "Success Criteria": {"rich_text": _rt(wave["success"])},
        "Files In Scope": {"rich_text": _rt(wave["files"])},
        "Parent Plan Summary": {
            "rich_text": _rt(
                "L2 Execute v2 — agent conformance. Thread the E1–E5 stage contract through the 88 Agent files; consume the 14 primitives landed by plan b7c4e2 without reinventing them."
            )
        },
        "Plan File": {"rich_text": _rt(PLAN_FILENAME)},
        "Status": {"select": {"name": "Todo"}},
        "Est Tokens": {"number": wave["est_tokens"]},
        "Blocking Items": {"rich_text": _rt(wave["blocking"])},
    }
    payload = {
        "parent": {"type": "database_id", "database_id": WAVE_DB},
        "properties": props,
    }
    r = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        data=json.dumps(payload),
        timeout=30,
    )
    if r.status_code >= 400:
        sys.stderr.write(f"  [wave] FAIL {wave['wave']} {r.status_code}: {r.text[:500]}\n")
        return None
    pid = r.json()["id"]
    print(f"  [wave] created {wave['wave']} page_id={pid}")
    return pid


def main() -> int:
    h = _headers()
    create_plans_row(h)
    for w in WAVES:
        create_wave_row(w, h)
    print("[done] bootstrap complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
