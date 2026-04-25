"""MW-9 completion Notion update."""

import json, os, requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

W5 = "34c27693-f55c-81de-866c-fdf0c1029830"
W6 = "34c27693-f55c-8124-a32c-fe4f924cfe05"


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


def patch(pid, note):
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{pid}",
        headers=h,
        data=json.dumps({"properties": {"Blocking Items": {"rich_text": rt(note)}}}),
        timeout=30,
    )
    return r.status_code


w5 = (
    "W5 + MW-9 COMPLETE 2026-04-24 (commit ab970aff17). LocationHealerAgent: "
    "class body (3212 lines, facade over UnifiedAgent+LocationHealingStrategy) "
    "mechanically relocated via git mv to agentic_core/L5_safety/utils/"
    "location_healer_util.py. Reasoning path now a deprecation re-export shim. "
    "All 7 consumers swapped: hierarchy_healer, location_path_util (2 sites), "
    "agent_roster_runner, orchestrator_runner, sovereign_healing_mission, "
    "test_depth_violation_no_archive_invariant, territory_healer_adapters. "
    "Consumer scan: 7 -> 0. py_compile clean. harden harness 23/33 identical "
    "(all failures pre-existing, structure_blueprint archived W7.5). "
    "W6 2026-07-23 can now archive LocationHealerAgent cleanly."
)
w6 = (
    "W6 READY 2026-04-24 (commit ab970aff17). ALL 9 REMAINING AUTHORIZED "
    "AGENTS now at effective zero-real-consumer after micro-waves MW-3..MW-12: "
    "RootCustomsAgent, SSOTFolderCleanupAgent, LocationHealerAgent, "
    "CodeJanitorAgent, CodeDetectorAgent, CodeEnforcerAgent, CodeValidatorAgent, "
    "SubAtomicAgent, GovernanceAgent. W6 sweep on 2026-07-23 can execute a "
    "single clean pass with no per-agent deferrals. Remaining 'consumers' are "
    "exclusively migration-tool string-literal rename-map data + W2-bound "
    "validator re-export shims that self-resolve at same W6 pass. Agent-"
    "deprecation-migration-d7a3f2 plan ready for final closure at W6."
)

print("W5:", patch(W5, w5))
print("W6:", patch(W6, w6))
