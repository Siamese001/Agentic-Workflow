"""
Refreshes the local legacy editor documentation mirror to ensure high-quality context retrieval.

Usage:
    python scripts/refresh_legacy_docs.py
"""

import os
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.join("docs", "windsurf")

PAGES = {
    "llms-full.txt": "https://docs.windsurf.com/llms-full.txt",
    "context-awareness-overview.html": "https://docs.windsurf.com/context-awareness/overview",
    "advanced-configuration.html": "https://docs.windsurf.com/windsurf/advanced",
    "memories-rules.html": "https://docs.windsurf.com/windsurf/cascade/memories",
    "agents-md.html": "https://docs.windsurf.com/windsurf/cascade/agents-md",
    "skills.html": "https://docs.windsurf.com/windsurf/cascade/skills",
    "workflows.html": "https://docs.windsurf.com/windsurf/cascade/workflows",
    "hooks.html": "https://docs.windsurf.com/windsurf/cascade/hooks",
    "mcp.html": "https://docs.windsurf.com/windsurf/cascade/mcp",
    "web-search.html": "https://docs.windsurf.com/windsurf/cascade/web-search",
    "prompt-engineering.html": "https://docs.windsurf.com/best-practices/prompt-engineering",
    "changelog.html": "https://windsurf.com/changelog",
}


def main() -> None:
    os.makedirs(ROOT, exist_ok=True)

    for filename, url in PAGES.items():
        dest = os.path.join(ROOT, filename)
        print(f"Fetching {filename} ...")
        urllib.request.urlretrieve(url, dest)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")
    with open(os.path.join(ROOT, "FETCHED_AT.txt"), "w", encoding="utf-8") as fh:
        fh.write(timestamp + "\n")

    print(f"\nSuccess: legacy editor documentation mirror updated at {timestamp}.")


if __name__ == "__main__":
    main()
