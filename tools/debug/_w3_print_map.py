import json
import pathlib

d = json.loads(
    pathlib.Path("artifacts/agent_deprecation/w3_replacement_map.json").read_text(encoding="utf-8")
)
for e in sorted(d["entries"], key=lambda x: x["consumer_fanin"]):
    name = e["agent_path"].split("/")[-1]
    repl = e["inferred_replacement"]
    print(f"{e['consumer_fanin']:3d} {name:50s} -> {repl}")
