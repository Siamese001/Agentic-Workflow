import json
import os
import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}
pid = "34c27693-f55c-81e9-bfcb-e60d28a1ee95"
note = (
    "Completed 2026-04-24 (commit 1a3640ca16). Phantom registry path fixed, status "
    "flipped to OBSOLETE, AGENT-DELETION-AUTHORIZED marker added with 0-consumer "
    "evidence, cooling-timer artifact created at "
    "artifacts/agent_deprecation/IntelligenceLibrarianAgent.json. Physical archive "
    "scheduled for W6 on/after 2026-05-09."
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
print(r.status_code, "W1 -> Done" if r.ok else r.text[:400])
