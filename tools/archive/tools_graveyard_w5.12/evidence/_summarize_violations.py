"""Summarize scanner violations by file and edge."""

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

result = subprocess.run(
    [sys.executable, "ops_scripts/ci/validate_layer_violations.py", "agentic_core"],
    capture_output=True,
    text=True,
    cwd=Path(__file__).parents[2],
)
data = json.loads(result.stdout)
violations = data["violations"]

by_file = defaultdict(list)
for v in violations:
    by_file[v["file"]].append(v)

print(f"Total: {len(violations)} violations across {len(by_file)} files\n")
for fpath in sorted(by_file):
    vs = by_file[fpath]
    print(fpath)
    for v in vs:
        print(f"  line {v['line']}: {v['edge']}  --  {v['import']}")
