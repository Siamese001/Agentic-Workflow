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


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


# Patch W3 row: 15/21 done
w3_note = (
    "W3.1 (13) + W3.2 (2) complete 2026-04-24 (commits bd2e0a3d01, 2814c674a6): "
    "15 of 21 low-fan-in DEPRECATED agents authorized. W3.2 analysis revealed "
    "classifier miscategorization: SubAtomicAgent had class inheritance (not "
    "typehint), CodeEnforcerAgent/CodeDetectorAgent appeared in registry dispatch "
    "dicts (not typehint). Only CostGovernorAgent + GravityStateAgent qualified "
    "for mechanical migration - both had their sole 'consumer' (a dead compat "
    "re-export file with zero external importers) entry-removed, dropping them "
    "to zero. Archive-eligible 2026-07-23. Deferred to W3.3: 6 agents with "
    "genuine architectural consumers (AgentFactory, HealingStrategy, runner, "
    "inheritance)."
)
body1 = {"properties": {"Blocking Items": {"rich_text": rt(w3_note)}}}
r1 = requests.patch(
    f"https://api.notion.com/v1/pages/{W3_PAGE}",
    headers=h,
    data=json.dumps(body1),
    timeout=30,
)
print(r1.status_code, "W3 updated" if r1.ok else r1.text[:300])

# Create W3.3 row for 6 remaining
w3_3 = {
    "parent": {"type": "database_id", "database_id": WAVE_DB},
    "properties": {
        "Phase Title": {
            "title": rt(
                "[P2] W3.3 P3.3 — Infrastructure refactor for 6 DEPRECATED agents with active-usage consumers"
            )
        },
        "Phase ID": {"rich_text": rt("P3.3")},
        "Wave ID": {"rich_text": rt("W3.3")},
        "Sub-Wave": {"rich_text": rt("W3-P3-INFRASTRUCTURE-REFACTOR")},
        "Dependencies": {
            "rich_text": rt(
                "W3.2 complete. These 6 agents have active-usage consumers that "
                "require refactoring touching AgentFactory type contracts, "
                "HealingStrategy string-dispatch, a subprocess runner, and "
                "base-class inheritance chains."
            )
        },
        "Success Criteria": {
            "rich_text": rt(
                "All 6 agents at zero live consumers; AGENT-DELETION-AUTHORIZED "
                "markers + cooling artifacts added; full L3+L5 test suite green."
            )
        },
        "Files In Scope": {
            "rich_text": rt(
                "DEPRECATED agents: SubAtomicAgent (inheritance by DocumentationAgent + TypeMechanicAgent), "
                "CodeJanitorAgent L5 (HealingStrategy dispatch + validators self-ref), "
                "CodeDetectorAgent (SubAtomicRegistryAgent dispatch dict), "
                "CodeValidatorAgent (HealingStrategy + code_validator_runner), "
                "CodeEnforcerAgent (HealingStrategy + AgentFactory), "
                "SSOTFolderCleanupAgent (ArchitectureGovernorAgent). "
                "Consumer details in artifacts/agent_deprecation/w3_2_consumer_usage.json"
            )
        },
        "Parent Plan Summary": {
            "rich_text": rt(
                "Agent deprecation migration. Tail 6 W3 agents need real "
                "architectural refactor rather than shim-removal."
            )
        },
        "Plan File": {"rich_text": rt("agent-deprecation-migration-d7a3f2.md")},
        "Status": {"select": {"name": "Todo"}},
        "Est Tokens": {"number": 18000},
        "Blocking Items": {
            "rich_text": rt(
                "Per-agent Author-Gate. Each of the 6 touches architectural "
                "contracts and needs test verification."
            )
        },
    },
}
r2 = requests.post(
    "https://api.notion.com/v1/pages",
    headers=h,
    data=json.dumps(w3_3),
    timeout=30,
)
print(r2.status_code, "W3.3 created" if r2.ok else r2.text[:300])
