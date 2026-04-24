"""Probe Notion Plans + Wave/Phase Convergence DS schemas."""

import json
import os

import requests

h = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

for label, ds_id in [
    ("Plans", "ac53d31b-3068-4039-9ebe-856c12caab32"),
    ("WavePhase", "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"),
]:
    r = requests.get(
        f"https://api.notion.com/v1/data_sources/{ds_id}",
        headers=h,
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"{label}: HTTP {r.status_code} {r.text[:300]}")
        continue
    d = r.json()
    props = d.get("properties", {})
    title_prop = next((k for k, v in props.items() if v.get("type") == "title"), None)
    print(f"\n=== {label} ({ds_id}) ===")
    print(f"TITLE property: {title_prop}")
    print("All properties (type):")
    for k, v in props.items():
        print(f"  - {k}: {v.get('type')}")
