"""Break down authority_boundary violations by file and breach_class."""
import json
from collections import Counter
from pathlib import Path

artifacts = sorted(Path("artifacts/ci_gates").glob("p0_runner_full_*.json"),
                   key=lambda p: p.stat().st_mtime)
d = json.loads(artifacts[-1].read_text(encoding="utf-8"))
for r in d["results"]:
    if r["gate_family"] == "authority_boundary":
        by_file = Counter()
        by_class = Counter()
        by_pair = Counter()
        for v in r["violations"]:
            by_file[v.get("file") or "?"] += 1
            extra = v.get("extra") or {}
            by_class[extra.get("breach_class", "?")] += 1
            pair = f"{v.get('layer_src','?')} -> {v.get('layer_dst','?')}"
            by_pair[pair] += 1
        print("=== by breach_class ===")
        for k, n in by_class.most_common():
            print(f"  {n:4d}  {k}")
        print("\n=== by layer pair ===")
        for k, n in by_pair.most_common():
            print(f"  {n:4d}  {k}")
        print("\n=== top 15 files ===")
        for f, n in by_file.most_common(15):
            print(f"  {n:4d}  {f}")
        break
