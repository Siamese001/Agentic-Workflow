"""Final Notion writeback: micro-wave consumer-migration results."""
import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

W3_3_PAGE = "34c27693-f55c-81c6-b16c-cbc422a3dfeb"
W4_PAGE = "34c27693-f55c-8126-a65b-ffc78ee39db1"
W5_PAGE = "34c27693-f55c-81de-866c-fdf0c1029830"
W6_PAGE = "34c27693-f55c-8124-a32c-fe4f924cfe05"


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


def patch(pid, note):
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{pid}",
        headers=h,
        data=json.dumps({"properties": {"Blocking Items": {"rich_text": rt(note)}}}),
        timeout=30,
    )
    return r.status_code, ("ok" if r.ok else r.text[:300])


w33_note = (
    "W3.3 + MW-3..MW-12 complete 2026-04-24 (commits 0c574edd5b, a60aa1add0). "
    "All 6 W3.3 agents now at EFFECTIVE ZERO REAL CONSUMERS: SubAtomicAgent, "
    "CodeJanitorAgent, CodeDetectorAgent, CodeValidatorAgent, CodeEnforcerAgent, "
    "SSOTFolderCleanupAgent. Remaining 'consumers' are either string-literals "
    "in migration-tool rename-mapping data (extract_pattern_util.py + "
    "rename_unified_agents_util.py) OR W2-bound self-resolving validator shims. "
    "W6 sweep on 2026-07-23 will clean-archive all 6."
)
print("W3.3:", patch(W3_3_PAGE, w33_note))

w4_note = (
    "W4 + MW-3 complete 2026-04-24 (commit cd67694c5f). RootCustomsAgent: "
    "removed 3 broken imports from root_customs_util.py (ARTIFACT_ROUTING_MAP, "
    "TEST_TYPE_SIGNALS, LEGACY_AST_SIGNALS were never defined in codebase; "
    "imports would ImportError at runtime). Zero real consumers. W6-ready."
)
print("W4:", patch(W4_PAGE, w4_note))

w5_note = (
    "W5 + MW-10..MW-12 partial complete 2026-04-24 (commits 0c574edd5b, "
    "a60aa1add0). GovernanceAgent: mission_runner.py swapped to "
    "ArchitectureGovernorAgent direct import (MW-10); only validators/ W2-bound "
    "shim remains, self-resolves W6. LocationHealerAgent: 7 real consumers "
    "requiring dedicated follow-up session with UnifiedAgent API mapping; "
    "authorization ACTIVE but archive DEFERRED per-agent at W6. See "
    "artifacts/agent_deprecation/MW9_LOCATION_HEALER_DEFERRAL.md for "
    "7-consumer breakdown and recommended migration path."
)
print("W5:", patch(W5_PAGE, w5_note))

w6_note = (
    "W6 pending 2026-07-23 archive sweep. Per MW-3..MW-12 consumer migrations "
    "complete: 30 of 31 authorized agents now at effective zero-real-consumer "
    "and will archive cleanly. EXCEPTION: LocationHealerAgent has 7 real "
    "consumers; W6 must detect these and defer per-agent archive while "
    "preserving authorization. Consumer-migration state: "
    "artifacts/agent_deprecation/mw_usage_scan.json. "
    "LocationHealer follow-up spec: artifacts/agent_deprecation/"
    "MW9_LOCATION_HEALER_DEFERRAL.md."
)
print("W6:", patch(W6_PAGE, w6_note))
