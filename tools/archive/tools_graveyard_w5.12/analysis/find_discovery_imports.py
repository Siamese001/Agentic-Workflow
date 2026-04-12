import json

with open("artifacts/collection_safety_phase1.json") as f:
    d = json.load(f)

# Find files importing agentic_core.discovery
for f in d["files"]:
    for issue in f["issues"]:
        if "agentic_core.discovery" in issue:
            print(f"{f['file']}: {issue}")
