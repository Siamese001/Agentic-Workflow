"""W3 Notion update: mark W3 In Progress (13/21 done); create W3.2 Todo row for remaining 8."""

import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

W3_PAGE = "34c27693-f55c-81ab-bf27-d6a34a2a1dc4"
WAVE_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"


def rt(text):
    return [{"type": "text", "text": {"content": text}}]


# Patch existing W3 row to In Progress with progress narrative
w3_note = (
    "W3.1 complete 2026-04-24 (commit bd2e0a3d01): 13 of 21 agents authorized "
    "after live-consumer grep showed zero external imports (ADG resolves_callsite "
    "counts of 2-8 were intra-class self-resolution). All 13 carry "
    "AGENT-DELETION-AUTHORIZED markers + cooling artifacts, archive-eligible "
    "2026-07-23. Deferred to W3.2: 8 agents with 1-4 live consumers each: "
    "SSOTFolderCleanupAgent, CostGovernorAgent, GravityStateAgent, CodeJanitorAgent "
    "(L5), CodeDetectorAgent, SubAtomicAgent, CodeValidatorAgent, CodeEnforcerAgent."
)
body1 = {
    "properties": {
        "Status": {"select": {"name": "In Progress"}},
        "Blocking Items": {"rich_text": rt(w3_note)},
    }
}
r1 = requests.patch(
    f"https://api.notion.com/v1/pages/{W3_PAGE}",
    headers=h,
    data=json.dumps(body1),
    timeout=30,
)
print(r1.status_code, "W3 -> In Progress" if r1.ok else r1.text[:400])

# Create W3.2 row
w3_2 = {
    "parent": {"type": "database_id", "database_id": WAVE_DB},
    "properties": {
        "Phase Title": {
            "title": rt("[P2] W3.2 P3.2 — Consumer migration for 8 low-fan-in DEPRECATED agents")
        },
        "Phase ID": {"rich_text": rt("P3.2")},
        "Wave ID": {"rich_text": rt("W3.2")},
        "Sub-Wave": {"rich_text": rt("W3-P2-CONSUMER-MIGRATION")},
        "Dependencies": {
            "rich_text": rt(
                "W3.1 complete. Each agent in this wave has 1-4 live consumers "
                "that must be migrated to the canonical *_util replacement before "
                "AGENT-DELETION-AUTHORIZED can be issued."
            )
        },
        "Success Criteria": {
            "rich_text": rt(
                "All 8 agents at zero live consumers; AGENT-DELETION-AUTHORIZED "
                "markers + cooling artifacts added; full test suite green."
            )
        },
        "Files In Scope": {
            "rich_text": rt(
                "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py (1), "
                "agentic_core/L5_safety/reasoning/CostGovernorAgent.py (1), "
                "agentic_core/L3_orchestration/reasoning/GravityStateAgent.py (1), "
                "agentic_core/L5_safety/reasoning/CodeJanitorAgent.py (2), "
                "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py (2), "
                "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py (3), "
                "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py (3), "
                "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py (4). "
                "Consumer list per agent in artifacts/agent_deprecation/w3_live_consumers.json"
            )
        },
        "Parent Plan Summary": {
            "rich_text": rt(
                "Agent deprecation migration. 13/21 low-fan-in DEPRECATED agents "
                "authorized in W3.1 (zero-consumer proven). 8 remaining require "
                "per-consumer refactor to the *_util replacement module."
            )
        },
        "Plan File": {"rich_text": rt("agent-deprecation-migration-d7a3f2.md")},
        "Status": {"select": {"name": "Todo"}},
        "Est Tokens": {"number": 12000},
        "Blocking Items": {
            "rich_text": rt(
                "Per-agent Author-Gate. Each consumer refactor requires py_compile "
                "+ targeted test run. Total 17 consumer files to touch."
            )
        },
    },
}
r2 = requests.post(
    "https://api.notion.com/v1/pages",
    headers=h,
    data=json.dumps(w3_2),
    timeout=30,
)
print(r2.status_code, "W3.2 created" if r2.ok else r2.text[:400])
