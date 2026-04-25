import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}
pid = "34c27693-f55c-81b3-b6d0-fec799d1179b"
note = (
    "Completed 2026-04-24 (commit d8ccca7391). 3 validators/ re-export shims "
    "(CodeJanitorAgent, GovernanceAgent, PascalSovereigntyAgent) authorized "
    "with AGENT-DELETION-AUTHORIZED markers + zero-consumer evidence. Archive "
    "scheduled 2026-07-23 (90-day cooling). 3 cooling-timer artifacts created "
    "under artifacts/agent_deprecation/. 3 v_p2_duplicated_adapters ADG "
    "violations will resolve on W6 archive sweep."
)
body = {
    "properties": {
        "Status": {"select": {"name": "Done"}},
        "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": note}}]},
    }
}
r = requests.patch(
    f"https://api.notion.com/v1/pages/{pid}",
    headers=h,
    data=json.dumps(body),
    timeout=30,
)
print(r.status_code, "W2 -> Done" if r.ok else r.text[:400])
