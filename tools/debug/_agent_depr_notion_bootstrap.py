"""Notion bootstrap for agent-deprecation-migration-d7a3f2 plan.

Posts Plans row (Status=Active) + single W0 Wave row (Status=Done) + 6
remaining wave rows (Status=Todo) awaiting per-wave Author-Gate.
"""

from __future__ import annotations

import json
import os
import sys

import requests

PLAN_SLUG = "agent-deprecation-migration-d7a3f2"
PLAN_FILENAME = f"{PLAN_SLUG}.md"

PLANS_DB = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DS = "ac53d31b-3068-4039-9ebe-856c12caab32"
WAVE_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"
WAVE_DS = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

PARENT_SUMMARY = (
    "Agent deprecation migration. Exhaustive ADG-backed assessment of 141 "
    "*Agent.py files found 0 SAFE_TO_ARCHIVE, 31 RISKY_DEPRECATED with 2-265 "
    "consumers each, 6 SHIM_UNUSED all registered ACTIVE in taxonomy, 4 "
    "validators/-directory duplicates. Per-wave Author-Gate required before "
    "any file move. Constitutional §3 compliance enforced."
)

WAVES = [
    {
        "status": "Done",
        "phase_title": "[P2] W0 P0.1 — Agent deprecation assessment (ADG + registry + test probe)",
        "wave": "W0",
        "phase": "P0.1",
        "sub_wave": "W0-P2-CORE",
        "files": "tools/debug/_agent_deprecation_assessment.py, artifacts/windsurf/agent_deprecation_assessment.txt",
        "success": "141 agents scanned, classified into 5 buckets, zero SAFE_TO_ARCHIVE — proves no blind move possible",
        "deps": "Fresh ADG snapshot adg_indexed_04242026_0721.sqlite",
        "est_tokens": 4000,
        "blocking": "None; W0 is read-only assessment",
    },
    {
        "status": "Todo",
        "phase_title": "[P3] W1 P1.1 — Registry-duplicate resolution (IntelligenceLibrarianAgent 2-path)",
        "wave": "W1",
        "phase": "P1.1",
        "sub_wave": "W1-P3-CORE",
        "files": "agentic_core/L2_execution/types/agent_taxonomy_registry.py, apps_lic/reasoning/IntelligenceLibrarianAgent.py, agentic_core/L4_state/engines/IntelligenceLibrarianAgent.py",
        "success": "Single canonical IntelligenceLibrarianAgent path; non-canonical version either renamed or marked @deprecated",
        "deps": "W0",
        "est_tokens": 5000,
        "blocking": "Author-Gate required: decide which path is canonical (apps_lic vs L4_state/engines)",
    },
    {
        "status": "Todo",
        "phase_title": "[P2] W2 P2.1 — validators/ directory dedup (3 duplicated adapters)",
        "wave": "W2",
        "phase": "P2.1",
        "sub_wave": "W2-P2-CORE",
        "files": "agentic_core/L5_safety/validators/{CodeJanitorAgent,GovernanceAgent,PascalSovereigntyAgent}.py",
        "success": "3 v_p2_duplicated_adapters violations resolved; single canonical path per agent",
        "deps": "W0",
        "est_tokens": 8000,
        "blocking": "Author-Gate required: decide which directory (validators/ vs reasoning/) wins per agent",
    },
    {
        "status": "Todo",
        "phase_title": "[P2] W3 P3.1 — Low-fan-in DEPRECATED migration (21 agents, ~760 consumers)",
        "wave": "W3",
        "phase": "P3.1",
        "sub_wave": "W3-P2-CORE",
        "files": "21 DEPRECATED agents with fan-in ≤ 8 — see plan §ADG_HOTSPOT_REPORT Low-fan-in table",
        "success": "21 agents have 0 consumers, AGENT-DELETION-AUTHORIZED markers added, 90-day cooling timers started",
        "deps": "W0; may proceed in parallel with W1/W2",
        "est_tokens": 18000,
        "blocking": "Per-agent Author-Gate. Wave may further decompose into sub-waves by layer.",
    },
    {
        "status": "Todo",
        "phase_title": "[P2] W4 P4.1 — Medium-fan-in DEPRECATED migration (7 agents, ~200 consumers)",
        "wave": "W4",
        "phase": "P4.1",
        "sub_wave": "W4-P2-CORE",
        "files": "RootCustomsAgent, StructureHealerAgent, AutonomyGuardianAgent, SubAtomicRegistryAgent, StructuralValidatorAgent, RedSentinelAgent, CognitiveDispositionAgent",
        "success": "7 agents at 0 consumers; each carries AGENT-DELETION-AUTHORIZED marker",
        "deps": "W3 complete",
        "est_tokens": 15000,
        "blocking": "Per-agent Author-Gate",
    },
    {
        "status": "Todo",
        "phase_title": "[P1] W5 P5.1 — High-fan-in DEPRECATED migration (3 agents, ~560 consumers)",
        "wave": "W5",
        "phase": "P5.1",
        "sub_wave": "W5-P1-CORE",
        "files": "FileClassificationAgent (5688 lines, 265 consumers), LocationHealerAgent (3212 lines, 224 consumers), GovernanceAgent (1263 lines, 70 consumers)",
        "success": "3 agents at 0 consumers; likely requires sub-wave split per constitutional cap (30k token ceiling)",
        "deps": "W3+W4 complete",
        "est_tokens": 30000,
        "blocking": "P1 — highest risk in plan. Per-agent sub-waves required.",
    },
    {
        "status": "Todo",
        "phase_title": "[P3] W6 P6.1 — 90-day cooling archive sweep",
        "wave": "W6",
        "phase": "P6.1",
        "sub_wave": "W6-P3-CORE",
        "files": "archives/agents/<YYYY-MM-DD>/*.py, agent_taxonomy_registry.py",
        "success": "All agents that completed 90-day cooling moved; registry updated; full test suite green",
        "deps": "W3+W4+W5 complete AND 90 days elapsed per agent",
        "est_tokens": 8000,
        "blocking": "Requires elapsed-time trigger + Author-Gate per batch",
    },
]


def _headers():
    return {
        "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }


def _rt(text: str):
    return [{"type": "text", "text": {"content": text}}]


def _find(ds_id: str, prop: str, value: str, h, title: bool = False):
    body = {
        "filter": {
            "property": prop,
            ("title" if title else "rich_text"): {"equals": value},
        },
        "page_size": 1,
    }
    r = requests.post(
        f"https://api.notion.com/v1/data_sources/{ds_id}/query",
        headers=h,
        data=json.dumps(body),
        timeout=30,
    )
    r.raise_for_status()
    rs = r.json().get("results", [])
    return rs[0]["id"] if rs else None


def main() -> int:
    h = _headers()
    # Plans row
    existing = _find(PLANS_DS, "Slug", PLAN_SLUG, h, title=True)
    if existing:
        print(f"[plans] exists {PLAN_SLUG} page_id={existing}")
    else:
        payload = {
            "parent": {"type": "database_id", "database_id": PLANS_DB},
            "properties": {
                "Slug": {"title": _rt(PLAN_SLUG)},
                "Status": {"select": {"name": "Active"}},
                "Plan File Path": {"rich_text": _rt(f".windsurf/plans/{PLAN_FILENAME}")},
                "Exists On Disk": {"checkbox": True},
                "Summary": {"rich_text": _rt(PARENT_SUMMARY)},
            },
        }
        r = requests.post(
            "https://api.notion.com/v1/pages",
            headers=h,
            data=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        print(f"[plans] created {PLAN_SLUG} page_id={r.json()['id']}")

    # Wave rows
    for w in WAVES:
        # Dedup by title
        dedup_body = {
            "filter": {"property": "Phase Title", "title": {"equals": w["phase_title"]}},
            "page_size": 1,
        }
        rq = requests.post(
            f"https://api.notion.com/v1/data_sources/{WAVE_DS}/query",
            headers=h,
            data=json.dumps(dedup_body),
            timeout=30,
        )
        rq.raise_for_status()
        if rq.json().get("results"):
            print(f"  [wave] exists {w['wave']}")
            continue
        payload = {
            "parent": {"type": "database_id", "database_id": WAVE_DB},
            "properties": {
                "Phase Title": {"title": _rt(w["phase_title"])},
                "Phase ID": {"rich_text": _rt(w["phase"])},
                "Wave ID": {"rich_text": _rt(w["wave"])},
                "Sub-Wave": {"rich_text": _rt(w["sub_wave"])},
                "Dependencies": {"rich_text": _rt(w["deps"])},
                "Success Criteria": {"rich_text": _rt(w["success"])},
                "Files In Scope": {"rich_text": _rt(w["files"])},
                "Parent Plan Summary": {"rich_text": _rt(PARENT_SUMMARY)},
                "Plan File": {"rich_text": _rt(PLAN_FILENAME)},
                "Status": {"select": {"name": w["status"]}},
                "Est Tokens": {"number": w["est_tokens"]},
                "Blocking Items": {"rich_text": _rt(w["blocking"])},
            },
        }
        r = requests.post(
            "https://api.notion.com/v1/pages",
            headers=h,
            data=json.dumps(payload),
            timeout=30,
        )
        if r.status_code >= 400:
            sys.stderr.write(f"  [wave] FAIL {w['wave']}: {r.status_code} {r.text[:300]}\n")
            continue
        print(f"  [wave] created {w['wave']} status={w['status']} page_id={r.json()['id']}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
