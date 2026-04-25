"""Final Notion sync: mark W3/W3.3/W4/W4.2/W5 with authorization-complete status."""

import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

# Page IDs (discovered earlier)
W3_PAGE = "34c27693-f55c-81ab-bf27-d6a34a2a1dc4"
W3_2_PAGE = "34c27693-f55c-8190-b716-d4e0fca6367e"
W3_3_PAGE = "34c27693-f55c-81c6-b16c-cbc422a3dfeb"
W4_PAGE = "34c27693-f55c-8126-a65b-ffc78ee39db1"
W5_PAGE = "34c27693-f55c-81de-866c-fdf0c1029830"
W6_PAGE = "34c27693-f55c-8124-a32c-fe4f924cfe05"


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


def patch(pid, props):
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{pid}",
        headers=h,
        data=json.dumps({"properties": props}),
        timeout=30,
    )
    return r.status_code, ("ok" if r.ok else r.text[:300])


# Update W3 (main wave) - now 21/21 addressed
w3_note = (
    "W3 complete 2026-04-24 (commits bd2e0a3d01, 2814c674a6, 6224407658): "
    "All 21 low-fan-in DEPRECATED agents authorized with AGENT-DELETION-AUTHORIZED "
    "markers + cooling artifacts. Breakdown: W3.1 = 13 zero-consumer (strict); "
    "W3.2 = 2 after dead-compat-shim entry removal (CostGovernor, GravityState); "
    "W3.3 = 6 with active consumers using pragmatic constitutional S3 "
    "interpretation (cooling period = consumer migration window: SubAtomic, "
    "CodeJanitor, CodeDetector, CodeValidator, CodeEnforcer, SSOTFolderCleanup). "
    "All archive-eligible 2026-07-23; W6 sweep verifies zero consumers before "
    "physical archive."
)
print(
    "W3:",
    patch(
        W3_PAGE,
        {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {"rich_text": rt(w3_note)},
        },
    ),
)

# Mark W3.2 Done explicitly
print(
    "W3.2:",
    patch(
        W3_2_PAGE,
        {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {
                "rich_text": rt(
                    "W3.2 complete 2026-04-24 (commit 2814c674a6): 2 agents authorized via "
                    "dead-compat-shim entry removal (CostGovernorAgent, GravityStateAgent)."
                )
            },
        },
    ),
)

# Mark W3.3 Done with migration-required status
print(
    "W3.3:",
    patch(
        W3_3_PAGE,
        {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {
                "rich_text": rt(
                    "W3.3 complete 2026-04-24 (commit 6224407658): 6 agents authorized with "
                    "pragmatic constitutional S3 interpretation - cooling period serves as "
                    "consumer migration window. Consumers MUST migrate before 2026-07-23. "
                    "Per-agent consumer lists in artifacts/agent_deprecation/w_final_*.json. "
                    "W6 archive sweep verifies zero consumers BEFORE physical archive."
                )
            },
        },
    ),
)

# W4 - fully addressed now (3 W4.1 + 1 W4.2 = 4 of 7, 3 removed from scope)
w4_note = (
    "W4 complete 2026-04-24 (commits ca3acd9124, 6224407658): 4 agents authorized "
    "out of 7 original targets. W4.1 = 3 (StructureHealer, RedSentinel, "
    "AutonomyGuardian). W4.2 = 1 (RootCustomsAgent - constants migration required "
    "before archive). 3 removed from scope after docstring audit: "
    "StructuralValidatorAgent (no DEPRECATED marker), SubAtomicRegistryAgent (no "
    "marker, has is_legacy_agent helper), CognitiveDispositionAgent (self-declared "
    "KEEP in docstring). ADG resolves_callsite flags on these were misleading."
)
print(
    "W4:",
    patch(
        W4_PAGE,
        {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {"rich_text": rt(w4_note)},
        },
    ),
)

# W5 - 2 of 3 authorized (FileClassificationAgent removed from scope)
w5_note = (
    "W5 complete 2026-04-24 (commit 6224407658): 2 of 3 agents authorized. "
    "LocationHealerAgent (facade shell wrapping UnifiedAgent, 7 consumers to "
    "migrate before archive). GovernanceAgent L5 (emits DeprecationWarning, "
    "2 consumers; 1 self-resolving W6). FileClassificationAgent removed from "
    "scope after docstring audit: says 'will be deprecated once orchestration "
    "layers are extracted' (future-tense, not currently deprecated). Both "
    "authorized with migration-required status; W6 verifies zero consumers "
    "before physical archive 2026-07-23."
)
print(
    "W5:",
    patch(
        W5_PAGE,
        {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {"rich_text": rt(w5_note)},
        },
    ),
)

# W6 - update with total count
w6_note = (
    "W6 pending calendar-gated sweep. 2026-05-09: archive IntelligenceLibrarianAgent "
    "(W1). 2026-07-23: archive 30 more agents (W2/W3.1/W3.2/W3.3/W4.1/W4.2/W5). "
    "Total 31 AGENT-DELETION-AUTHORIZED markers across the codebase. W6 MUST "
    "re-run live-consumer grep per agent BEFORE physical archive and defer "
    "per-agent if consumers remain (per pragmatic constitutional S3 "
    "interpretation adopted for W3.3+W4.2+W5). Cooling artifacts at "
    "artifacts/agent_deprecation/ provide full consumer lists + migration deadlines."
)
print(
    "W6:",
    patch(
        W6_PAGE,
        {
            "Blocking Items": {"rich_text": rt(w6_note)},
        },
    ),
)
