"""Find or create W4/W5 rows in Wave/Phase Convergence DB; update statuses."""

import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

WAVE_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"
WAVE_DS = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


def rt(t):
    return [{"type": "text", "text": {"content": t}}]


# Query for W4 and W5 rows linked to agent-deprecation-migration plan
q = {
    "filter": {
        "and": [
            {
                "property": "Plan File",
                "rich_text": {"contains": "agent-deprecation-migration"},
            },
        ]
    },
    "page_size": 50,
}
r = requests.post(
    f"https://api.notion.com/v1/data_sources/{WAVE_DS}/query",
    headers=h,
    data=json.dumps(q),
    timeout=30,
)
rows = r.json().get("results", []) if r.ok else []
print(f"found {len(rows)} agent-deprecation rows")
w4_page = None
w5_page = None
for row in rows:
    title_parts = row.get("properties", {}).get("Phase Title", {}).get("title", [])
    title = "".join(p.get("plain_text", "") for p in title_parts)
    wave_id_parts = row.get("properties", {}).get("Wave ID", {}).get("rich_text", [])
    wave_id = "".join(p.get("plain_text", "") for p in wave_id_parts)
    pid = row["id"]
    print(f"  {pid}  wave={wave_id!r}  title={title[:80]!r}")
    if wave_id.strip() == "W4" and w4_page is None:
        w4_page = pid
    elif wave_id.strip() == "W5" and w5_page is None:
        w5_page = pid

print(f"\nW4 page: {w4_page}")
print(f"W5 page: {w5_page}")


def patch(pid, status, note):
    body = {
        "properties": {
            "Status": {"select": {"name": status}},
            "Blocking Items": {"rich_text": rt(note)},
        }
    }
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{pid}",
        headers=h,
        data=json.dumps(body),
        timeout=30,
    )
    return r.status_code, r.text[:300] if not r.ok else "ok"


def create(wave_id, phase_id, title, status, note):
    body = {
        "parent": {"type": "database_id", "database_id": WAVE_DB},
        "properties": {
            "Phase Title": {"title": rt(title)},
            "Phase ID": {"rich_text": rt(phase_id)},
            "Wave ID": {"rich_text": rt(wave_id)},
            "Plan File": {"rich_text": rt("agent-deprecation-migration-d7a3f2.md")},
            "Status": {"select": {"name": status}},
            "Blocking Items": {"rich_text": rt(note)},
            "Est Tokens": {"number": 15000},
        },
    }
    r = requests.post(
        "https://api.notion.com/v1/pages",
        headers=h,
        data=json.dumps(body),
        timeout=30,
    )
    return r.status_code, r.text[:300] if not r.ok else "ok"


w4_note = (
    "W4.1 complete 2026-04-24 (commit ca3acd9124): 3 of 7 medium-fan-in authorized "
    "(StructureHealerAgent, RedSentinelAgent, AutonomyGuardianAgent). "
    "CognitiveDispositionAgent self-declared KEEP and was removed from list. "
    "Deferred to W4.2: StructuralValidatorAgent (3 consumers), "
    "SubAtomicRegistryAgent (l2_agent_wrappers chain), RootCustomsAgent "
    "(needs constant-move refactor — util imports constants from agent)."
)
w5_note = (
    "W5 analysis complete 2026-04-24: all 3 top-fan-in DEPRECATED agents blocked "
    "by real consumer dependencies. GovernanceAgent L5 (1 real + 1 self-resolving "
    "via W6), LocationHealerAgent (7 consumers), FileClassificationAgent "
    "(14 consumers, foundational). All 3 need per-agent focused refactor waves. "
    "Consumer lists at artifacts/agent_deprecation/w5_live_consumers.json."
)

if w4_page:
    print("W4 patch:", patch(w4_page, "In Progress", w4_note))
else:
    print(
        "W4 create:",
        create(
            "W4",
            "P4",
            "[P2] W4 P4 — Medium-fan-in DEPRECATED migration (7 agents, 3 authorized)",
            "In Progress",
            w4_note,
        ),
    )

if w5_page:
    print("W5 patch:", patch(w5_page, "Blocked", w5_note))
else:
    print(
        "W5 create:",
        create(
            "W5",
            "P5",
            "[P1] W5 P5 — High-fan-in DEPRECATED (3 agents, blocked on consumer-refactor)",
            "Blocked",
            w5_note,
        ),
    )
