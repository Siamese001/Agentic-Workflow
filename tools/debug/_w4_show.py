import json
import pathlib

d = json.loads(pathlib.Path("artifacts/agent_deprecation/w4_live_consumers.json").read_text(encoding="utf-8"))
for e in sorted(d["entries"], key=lambda x: x["live_consumer_count"]):
    print(f"=== {e['class_name']} ({e['live_consumer_count']} consumers) ===")
    doc = (e["docstring_head"] or "").replace("\n", " | ")[:250]
    print(f"  doc: {doc}")
    for c in e["live_consumer_files"]:
        print(f"  consumer: {c}")
    print()
