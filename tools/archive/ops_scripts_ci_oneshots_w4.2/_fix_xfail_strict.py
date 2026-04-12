"""One-shot script: replace strict=False with strict=True in xfail decorators."""

import pathlib
import re
import sys

FILES = [
    "tests/system_learning/test_activation_gate_w4f.py",
    "tests/system_learning/test_policy_recommendation_w4d.py",
    "tests/system_learning/test_retrieval_profile_proposal_w4e.py",
    "tests/system_learning/test_shadow_drift_w4c.py",
    "tests/system_learning/test_shadow_embedder_w4b.py",
    "tests/system_learning/test_w5_replay_engine.py",
]
ROOT = pathlib.Path(__file__).resolve().parents[2]
changed = 0
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        print(f"MISSING: {rel}")
        continue
    src = p.read_text(encoding="utf-8")
    fixed = re.sub(
        "(@pytest\\.mark\\.xfail\\([^)]*?)strict\\s*=\\s*False([^)]*\\))", "\\1strict=True\\2", src
    )
    if fixed != src:
        p.write_text(fixed, encoding="utf-8")
        print(f"Fixed: {rel}")
        changed += 1
    else:
        print(f"No change: {rel}")
print(f"\n{changed} file(s) updated.")
sys.exit(0)
