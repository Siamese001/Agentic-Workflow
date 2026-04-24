import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

W4_PAGE = "34c27693-f55c-8172-8eb6-f9d9fc3f46e8"
W5_PAGE = "34c27693-f55c-81c0-be0a-eda35e4d8a55"
WAVE_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


# Update W4 row: 3/7 done, 4 deferred
w4_note = (
    "W4.1 complete 2026-04-24 (commit ca3acd9124): 3 of 7 medium-fan-in DEPRECATED "
    "agents authorized. StructureHealerAgent (facade shell, zero consumers). "
    "RedSentinelAgent + AutonomyGuardianAgent: only consumer was the dead "
    "l5_safety_aliases.py compat shim; removed entries, authorized. "
    "CognitiveDispositionAgent: self-declared KEEP in docstring (removed from "
    "W4 list). Deferred to W4.2 (3 agents): StructuralValidatorAgent (3 real "
    "consumers), SubAtomicRegistryAgent (consumer chain via l2_agent_wrappers), "
    "RootCustomsAgent (its replacement util imports constants FROM the agent - "
    "needs constant-move refactor)."
)
body4 = {
    "properties": {
        "Status": {"select": {"name": "In Progress"}},
        "Blocking Items": {"rich_text": rt(w4_note)},
    }
}
r4 = requests.patch(
    f"https://api.notion.com/v1/pages/{W4_PAGE}",
    headers=h,
    data=json.dumps(body4),
    timeout=30,
)
print(r4.status_code, "W4 updated" if r4.ok else r4.text[:300])

# Update W5 row: 0/3 done, all deferred with analysis
w5_note = (
    "W5 analysis complete 2026-04-24: all 3 top-fan-in DEPRECATED agents blocked "
    "by real consumer dependencies requiring dedicated architectural refactor. "
    "GovernanceAgent L5 (2 consumers - mission_runner.py imports "
    "GovernanceAgent as ArchitectureGovernor; validators/GovernanceAgent.py "
    "W2-archive-bound, self-resolves at W6). LocationHealerAgent (7 consumers - "
    "hierarchy_healer, location_path_util, runners, test, ops_scripts). "
    "FileClassificationAgent (14 consumers - foundational L5 infrastructure "
    "used by ArchitectureGovernor, hierarchy_healer, location_validator, "
    "file_classification/*, runners, tests). W5 requires per-agent focused "
    "refactor waves in future sessions. Consumer list at "
    "artifacts/agent_deprecation/w5_live_consumers.json."
)
body5 = {
    "properties": {
        "Status": {"select": {"name": "Blocked"}},
        "Blocking Items": {"rich_text": rt(w5_note)},
    }
}
r5 = requests.patch(
    f"https://api.notion.com/v1/pages/{W5_PAGE}",
    headers=h,
    data=json.dumps(body5),
    timeout=30,
)
print(r5.status_code, "W5 updated" if r5.ok else r5.text[:300])
